import asyncio
import bleak
import numpy as np
from datetime import datetime
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# Polar H10 BLE Service UUIDs
POLAR_H10_HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
POLAR_H10_HRV_UUID = "00002a38-0000-1000-8000-00805f9b34fb" # Not used directly, but good reference
POLAR_H10_ECG_UUID = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8" # Not used in this Veto logic
POLAR_H10_DEVICE_INFO_UUID = "0000180a-0000-1000-8000-00805f9b34fb"

class PolarH10Bridge:
    """Sovereign Protocol: Polar H10 Sensor Bridge"""
    
    def __init__(self, timeout_seconds=30):
        self.client = None
        self.device = None
        self.timeout = timeout_seconds
        self.heart_rate = 0
        self.rr_intervals = [] # Stores RR intervals in milliseconds
        self.hrv_status = "INACTIVE"
        self.rmssd = 0.0
        self.last_update = None
        
    async def discover_device(self):
        """Protocol Phase 1: Sensor Discovery"""
        print("🛰️  SOVEREIGN PROTOCOL: Scanning for Polar H10...")
        # Add filtering for performance in real-world scenarios
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
        
        # Byte 0: Flags
        # Byte 1: Heart Rate Value (uint8)
        # Byte 2-3 onwards: RR Intervals (uint16, units of 1/1024 seconds)
        
        # 1. Extract Heart Rate
        if data[0] & 0x01:  # Heart rate in uint16 (usually not on H10)
            self.heart_rate = int.from_bytes(data[1:3], byteorder='little')
        else:  # Heart rate in uint8 (common on H10)
            self.heart_rate = data[1]
        
        # 2. Extract and Convert RR intervals (The Veto Signal)
        new_rr_intervals = []
        if len(data) > 3:
            offset = 3 if data[0] & 0x01 else 2
            while offset + 2 <= len(data):
                rr_val = int.from_bytes(data[offset:offset+2], byteorder='little')
                rr_ms = rr_val / 1024.0 * 1000.0  # Convert from 1/1024 seconds to milliseconds
                new_rr_intervals.append(rr_ms)
                offset += 2
        
        # Append new data and keep a rolling buffer (e.g., last 60 seconds of data)
        self.rr_intervals.extend(new_rr_intervals)
        # Simple rolling buffer to prevent memory overflow (e.g., max 100 RR-i)
        self.rr_intervals = self.rr_intervals[-100:] 

        self.last_update = datetime.now()
        
        # 3. Calculate HRV metrics immediately
        if len(self.rr_intervals) >= 5: # Need at least a few points for RMSSD
            self._calculate_hrv_metrics()
        
    def _calculate_hrv_metrics(self):
        """Protocol Phase 3: HRV Analysis (RMSSD for Coherence)"""
        rr_array = np.array(self.rr_intervals)
        
        # Calculate RMSSD (Root Mean Square of Successive Differences)
        if len(rr_array) > 1:
            differences = np.diff(rr_array)
            self.rmssd = np.sqrt(np.mean(differences ** 2))
        else:
            self.rmssd = 0.0
        
        # Veto Gate HRV Threshold Logic (The Law)
        if self.rmssd >= 40.0:  # The Veto Threshold: High Parasympathetic Tone
            self.hrv_status = "QUORUM_CALIBRATED"
        elif self.rmssd >= 20.0:
            self.hrv_status = "GATE_ACTIVE"
        else:
            self.hrv_status = "VETO_STANDBY"
        
        # Log metrics for protocol audit (Optional, can be commented out for performance)
        # print(f"📊 HRV PROTOCOL: HR={self.heart_rate}bpm | RMSSD={self.rmssd:.1f}ms | STATUS={self.hrv_status}")
    
    async def connect_and_subscribe(self):
        """Protocol Phase 4: Secure Connection and Subscription"""
        if not self.device:
            return False
        
        try:
            self.client = BleakClient(self.device.address, timeout=self.timeout)
            await self.client.connect()
            
            # Subscribe to heart rate notifications (which includes RR intervals)
            await self.client.start_notify(POLAR_H10_HR_UUID, self.hr_data_handler)
            print("📡 PROTOCOL ESTABLISHED: HR/HRV data stream active")
            
            return True
            
        except BleakError as e:
            print(f"❌ CONNECTION PROTOCOL VIOLATION: {str(e)}")
            return False
    
    async def read_hrv_data(self, duration_seconds=60):
        """Primary Interface: Sovereign HRV Data Acquisition"""
        
        # Step 1: Discover sensor
        if not await self.discover_device():
            return {"error": "SENSOR_NOT_FOUND"}
        
        # Step 2: Establish connection
        if not await self.connect_and_subscribe():
            return {"error": "CONNECTION_FAILED"}
        
        print(f"⏳ ACQUIRING SOVEREIGN BIOSIGNALS: {duration_seconds} seconds...")
        
        # Step 3: Collect data for the required duration
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < duration_seconds:
            # Sleep allows the asynchronous HR data handler to receive packets
            await asyncio.sleep(1) 
            
            # Print status periodically
            if self.last_update and (datetime.now() - self.last_update).seconds < 5:
                 print(f"❤️  REAL-TIME: {self.heart_rate} BPM | "
                       f"RMSSD: {self.rmssd:.1f}ms | Status: {self.hrv_status}")

        # Step 4: Clean shutdown
        try:
            await self.client.stop_notify(POLAR_H10_HR_UUID)
            await self.client.disconnect()
        except Exception:
            pass # Ignore errors on disconnect
        
        # Step 5: Compose Sovereign Data Packet
        sovereign_data = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate": self.heart_rate,
            "rr_intervals": self.rr_intervals,
            "hrv_status": self.hrv_status,
            "rmssd": self.rmssd,
            "data_quality": "SOVEREIGN_CALIBRATED" if len(self.rr_intervals) >= 10 else "INSUFFICIENT_DATA",
            "sensor_authenticated": True,
            "protocol_version": "VETO_GATE_1.0"
        }
        
        print("✅ SOVEREIGN BIOSIGNAL ACQUISITION COMPLETE")
        
        return sovereign_data

# ============================================================================
# VETO GATE INTEGRATION PROTOCOL (The Law Enforcement)
# ============================================================================

async def read_hrv_data():
    """
    SOVEREIGN PROTOCOL ENTRY POINT
    Executes the Polar H10 sensor bridge and returns veto-qualified HRV data.
    This function is called by Splendids.py.
    """
    print("=" * 60)
    print("🦅 VETO GATE CORE: INITIATING BIOSIGNAL PROTOCOL")
    print("=" * 60)
    
    bridge = PolarH10Bridge(timeout_seconds=30)
    
    try:
        # Execute 60-second biosignal acquisition protocol
        data = await bridge.read_hrv_data(duration_seconds=60)
        
        # Veto Gate Qualification Logic (The final decision)
        if "error" not in data:
            if data["hrv_status"] == "QUORUM_CALIBRATED":
                data["veto_eligible"] = True
                data["gate_status"] = "BIOMETRIC_VETO_ARMED"
                print("⚡ VETO GATE STATUS: BIOMETRIC VETO ARMED AND OPERATIONAL")
            else:
                data["veto_eligible"] = False
                data["gate_status"] = "BIOMETRIC_VETO_STANDBY"
                print("⏸️  VETO GATE STATUS: BIOSIGNALS INSUFFICIENT FOR VETO")
        else:
            data["veto_eligible"] = False
            data["gate_status"] = "SENSOR_PROTOCOL_FAILURE"
            print("❌ VETO GATE STATUS: SENSOR PROTOCOL FAILURE")
        
        # Append RMSSD to the final data packet for Splendids.py to see
        data["rmssd"] = bridge.rmssd 
        return data
        
    except Exception as e:
        # Catastrophic failure (e.g., missing bleak library, permissions)
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
    """
    Self-Test: Allows direct execution of this file to test sensor functionality.
    """
    print("🧪 INITIATING SOVEREIGN PROTOCOL SELF-TEST...")
    
    test_data = asyncio.run(read_hrv_data())
    
    print("\n" + "=" * 60)
    print("PROTOCOL SELF-TEST COMPLETE")
    print("=" * 60)
    print(f"VETO ELIGIBILITY: {test_data.get('veto_eligible', False)}")
    print(f"GATE STATUS: {test_data.get('gate_status', 'UNKNOWN')}")
    print(f"RMSSD SCORE: {test_data.get('rmssd', 0.0):.2f} ms")
    print("=" * 60)
