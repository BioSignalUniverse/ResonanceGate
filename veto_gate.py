import asyncio
import bleak
import numpy as np
from datetime import datetime
import time
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# Polar H10 BLE Service UUIDs
POLAR_H10_HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
POLAR_H10_DEVICE_INFO_UUID = "0000180a-0000-1000-8000-00805f9b34fb"

# Global state to store personalized baseline (persists across runs if not reset)
# In a real application, this would be saved to a config file (e.g., veto_config.json)
GLOBAL_BASELINE = {'rmssd': 0.0, 'timestamp': None}

class PolarH10Bridge:
    """Sovereign Protocol: Polar H10 Sensor Bridge (Fortified)"""
    
    def __init__(self, timeout_seconds=30):
        global GLOBAL_BASELINE
        self.client = None
        self.device = None
        self.timeout = timeout_seconds
        self.heart_rate = 0
        self.rr_intervals = [] # Stores RR intervals in milliseconds
        self.hrv_status = "INACTIVE"
        self.rmssd = 0.0
        self.data_quality = "UNCHECKED"
        self.last_update = None
        
        # Personalized Thresholds based on Global State
        self.baseline_rmssd = GLOBAL_BASELINE.get('rmssd', 0.0)
        
        # Default/Absolute Veto Thresholds (used if no baseline is set)
        self.ABS_QUORUM_THRESHOLD = 40.0 # RMSSD >= 40ms
        self.ABS_ACTIVE_THRESHOLD = 20.0 # RMSSD >= 20ms
        
    # --- HRV UTILITY FUNCTIONS ---
    def _calculate_rmssd(self, rr_array):
        """Calculates RMSSD from an array of RR intervals."""
        if len(rr_array) > 1:
            differences = np.diff(rr_array)
            return np.sqrt(np.mean(differences ** 2))
        return 0.0

    def assess_data_quality(self, rr_array):
        """Protocol Enhancement 2: Check for sensor artifacts and poor signal."""
        if len(rr_array) < 10:
            return "INSUFFICIENT_DATA"
        
        # Check 1: Physiologically impossible values (less than 30bpm or more than 200bpm)
        # 1000ms/200bpm = 5ms; 1000ms/30bpm = 33.3ms
        if np.any(rr_array < 300) or np.any(rr_array > 2000): # RR-i must be between 300ms and 2000ms
            return "ARTIFACT_DETECTED"
        
        # Check 2: Excessive variance (often poor sensor contact)
        if np.std(rr_array) > 250: # High standard deviation usually means poor quality
             return "POOR_SIGNAL_QUALITY"
        
        return "SOVEREIGN_CALIBRATED"
    
    # --- CORE BRIDGE FUNCTIONS ---
    async def discover_device(self):
        """Protocol Phase 1: Sensor Discovery"""
        # ... (unchanged) ...
        print("🛰️  SOVEREIGN PROTOCOL: Scanning for Polar H10...")
        devices = await BleakScanner.discover(timeout=15)
        
        for device in devices:
            if device.name and "Polar H10" in device.name:
                print(f"✅ SENSOR ACQUIRED: {device.name} ({device.address})")
                self.device = device
                return True
        
        print("❌ PROTOCOL VIOLATION: Polar H10 not detected")
        return False
    
    def hr_data_handler(self, sender, data):
        """Protocol Phase 2: Heart Rate Data Extraction and RMSSD calculation"""
        
        # ... (HR extraction and RR conversion logic - unchanged) ...
        if data[0] & 0x01:
            self.heart_rate = int.from_bytes(data[1:3], byteorder='little')
        else:
            self.heart_rate = data[1]
        
        new_rr_intervals = []
        if len(data) > 3:
            offset = 3 if data[0] & 0x01 else 2
            while offset + 2 <= len(data):
                rr_val = int.from_bytes(data[offset:offset+2], byteorder='little')
                rr_ms = rr_val / 1024.0 * 1000.0
                new_rr_intervals.append(rr_ms)
                offset += 2
        
        self.rr_intervals.extend(new_rr_intervals)
        self.rr_intervals = self.rr_intervals[-100:] 

        self.last_update = datetime.now()
        
        # Calculate HRV metrics and check quality
        if len(self.rr_intervals) >= 5:
            self.rmssd = self._calculate_rmssd(np.array(self.rr_intervals))
            self._apply_veto_thresholds()
        
        self.data_quality = self.assess_data_quality(np.array(self.rr_intervals))

    def _apply_veto_thresholds(self):
        """Protocol Enhancement 1: Applies Personalized or Absolute Veto Thresholds."""
        
        # Determine the thresholds to use
        if self.baseline_rmssd > 0:
            # Use personalized thresholds if baseline exists
            # QUORUM: 20% above baseline, ACTIVE: 80% of baseline
            quorum_threshold = self.baseline_rmssd * 1.2 
            active_threshold = self.baseline_rmssd * 0.8
            print(f"   [Calibrated: Q={quorum_threshold:.1f}ms]")
        else:
            # Use absolute thresholds as fallback
            quorum_threshold = self.ABS_QUORUM_THRESHOLD
            active_threshold = self.ABS_ACTIVE_THRESHOLD

        # Apply the Law
        if self.rmssd >= quorum_threshold:
            self.hrv_status = "QUORUM_CALIBRATED"
        elif self.rmssd >= active_threshold:
            self.hrv_status = "GATE_ACTIVE"
        else:
            self.hrv_status = "VETO_STANDBY"
    
    # --- NEW CALIBRATION FUNCTION ---
    async def calibrate_baseline(self, duration_seconds=120):
        """
        Protocol Enhancement 1: Establishes a personalized resting HRV baseline.
        """
        global GLOBAL_BASELINE
        print("=" * 60)
        print("🧘 PROTOCOL CALIBRATION: Establishing Resting HRV Baseline (2 min)")
        print("=" * 60)
        
        if not await self.discover_device(): return False
        if not await self.connect_and_subscribe(): return False
        
        # Start quiet data collection
        start_time = time.time()
        initial_rr_count = len(self.rr_intervals)
        
        while (time.time() - start_time) < duration_seconds:
            await asyncio.sleep(1)
            # Notify user of progress
            if int(time.time() - start_time) % 10 == 0 and int(time.time() - start_time) > 0:
                print(f"⏳ Calibration Progress: {int(time.time() - start_time)}/{duration_seconds}s | Current RMSSD: {self.rmssd:.1f}ms")

        # Stop collection
        await self.client.stop_notify(POLAR_H10_HR_UUID)
        await self.client.disconnect()
        
        # Analyze collected data
        collected_rr = self.rr_intervals[initial_rr_count:]
        if len(collected_rr) < 20: # Ensure at least 20 beats were captured
            print("❌ CALIBRATION FAIL: Insufficient data collected.")
            return False
            
        final_rmssd = self._calculate_rmssd(np.array(collected_rr))
        
        # Update global state
        GLOBAL_BASELINE['rmssd'] = final_rmssd
        GLOBAL_BASELINE['timestamp'] = datetime.now().isoformat()
        
        self.baseline_rmssd = final_rmssd # Update local instance
        
        print("✅ CALIBRATION SUCCESS:")
        print(f"   Baseline RMSSD established: {final_rmssd:.2f}ms")
        print(f"   New Veto Threshold: {final_rmssd * 1.2:.2f}ms (20% above baseline)")
        print("-" * 60)
        return True

    # ... (connect_and_subscribe - unchanged) ...

    async def connect_and_subscribe(self):
        """Protocol Phase 4: Secure Connection and Subscription"""
        # ... (unchanged) ...
        if not self.device: return False
        try:
            self.client = BleakClient(self.device.address, timeout=self.timeout)
            await self.client.connect()
            await self.client.start_notify(POLAR_H10_HR_UUID, self.hr_data_handler)
            print("📡 PROTOCOL ESTABLISHED: HR/HRV data stream active")
            return True
        except BleakError as e:
            print(f"❌ CONNECTION PROTOCOL VIOLATION: {str(e)}")
            return False

    async def read_hrv_data(self, duration_seconds=60):
        """Primary Interface: Sovereign HRV Data Acquisition"""
        
        # Step 1: Discover sensor
        if not await self.discover_device(): return {"error": "SENSOR_NOT_FOUND"}
        
        # Step 2: Establish connection
        if not await self.connect_and_subscribe(): return {"error": "CONNECTION_FAILED"}
        
        # Reset current data collection buffer before main run
        self.rr_intervals = []
        
        print(f"⏳ ACQUIRING SOVEREIGN BIOSIGNALS: {duration_seconds} seconds...")
        
        # Step 3: Collect data for the required duration
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < duration_seconds:
            await asyncio.sleep(1) 
        
        # Step 4: Clean shutdown
        try:
            await self.client.stop_notify(POLAR_H10_HR_UUID)
            await self.client.disconnect()
        except Exception:
            pass 
        
        # Step 5: Compose Sovereign Data Packet
        # Check final data quality before composing packet
        final_quality = self.assess_data_quality(np.array(self.rr_intervals))
        
        # Final Veto decision based on Quality AND RMSSD
        veto_status = self.hrv_status
        if final_quality != "SOVEREIGN_CALIBRATED":
            veto_status = f"QUALITY_VETO_{final_quality}"

        sovereign_data = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate": self.heart_rate,
            "rr_intervals_count": len(self.rr_intervals),
            "hrv_status": veto_status,
            "rmssd": self.rmssd,
            "data_quality": final_quality,
            "sensor_authenticated": True,
            "protocol_version": "VETO_GATE_1.1_FORTIFIED"
        }
        
        print(f"✅ SOVEREIGN BIOSIGNAL ACQUISITION COMPLETE | Status: {veto_status}")
        
        return sovereign_data

# ============================================================================
# VETO GATE INTEGRATION PROTOCOL (Entry Point)
# ============================================================================

async def read_hrv_data():
    """SOVEREIGN PROTOCOL ENTRY POINT: Called by Splendids.py."""
    print("=" * 60)
    print("🦅 VETO GATE CORE: INITIATING BIOSIGNAL PROTOCOL")
    print("=" * 60)
    
    bridge = PolarH10Bridge(timeout_seconds=30)
    
    # Check for baseline, and if not present, force calibration first
    if bridge.baseline_rmssd == 0.0:
        await bridge.calibrate_baseline()
        # Re-initialize bridge to load the newly set baseline
        bridge = PolarH10Bridge(timeout_seconds=30) 

    try:
        data = await bridge.read_hrv_data(duration_seconds=60)
        
        # Veto Gate Qualification Logic
        data["veto_eligible"] = False
        data["gate_status"] = "SYSTEM_FAILURE" # Default to failure
        
        if "error" not in data and data["data_quality"] == "SOVEREIGN_CALIBRATED":
            if data["hrv_status"] == "QUORUM_CALIBRATED":
                data["veto_eligible"] = True
                data["gate_status"] = "BIOMETRIC_VETO_ARMED"
                print("⚡ VETO GATE STATUS: BIOMETRIC VETO ARMED AND OPERATIONAL")
            else:
                data["veto_eligible"] = False
                data["gate_status"] = "BIOMETRIC_VETO_STANDBY"
                print("⏸️  VETO GATE STATUS: BIOSIGNALS INSUFFICIENT FOR VETO")
        else:
            # Fails due to Quality Check or Error
            data["veto_eligible"] = False
            data["gate_status"] = data["hrv_status"] if "QUALITY_VETO" in data["hrv_status"] else "SENSOR_PROTOCOL_FAILURE"
            print(f"❌ VETO GATE STATUS: {data['gate_status']}")

        return data
        
    except Exception as e:
        print(f"💥 CATASTROPHIC PROTOCOL FAILURE: {str(e)}")
        return {
            "error": "PROTOCOL_FAILURE",
            "details": str(e),
            "veto_eligible": False,
            "gate_status": "SYSTEM_FAILURE",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# PROTOCOL VERIFICATION SELF-TEST
# ============================================================================

if __name__ == "__main__":
    """Self-Test: Allows direct execution of this file to test sensor functionality."""
    # Running this file directly will first attempt calibration if no baseline exists.
    print("🧪 INITIATING SOVEREIGN PROTOCOL SELF-TEST...")
    test_data = asyncio.run(read_hrv_data())
    
    print("\n" + "=" * 60)
    print("PROTOCOL SELF-TEST COMPLETE")
    print("=" * 60)
    print(f"VETO ELIGIBILITY: {test_data.get('veto_eligible', False)}")
    print(f"GATE STATUS: {test_data.get('gate_status', 'UNKNOWN')}")
    print(f"RMSSD SCORE: {test_data.get('rmssd', 0.0):.2f} ms")
    print(f"DATA QUALITY: {test_data.get('data_quality', 'UNKNOWN')}")
    print("=" * 60)
