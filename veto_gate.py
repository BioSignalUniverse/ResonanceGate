"""
veto_check.py - Sovereign Dual-Mode HRV Biometric Gate
Real Polar H10 when available • Graceful circadian simulation when not
Fortified • Personalized • Respectful
"""

import asyncio
import random
from datetime import datetime
import numpy as np

# Attempt real sensor imports — fail silently for simulation mode
try:
    from bleak import BleakClient, BleakScanner
    from bleak.exc import BleakError
    REAL_SENSOR_AVAILABLE = True
except ImportError:
    REAL_SENSOR_AVAILABLE = False
    print("   ℹ️ bleak not available — running in simulation-only mode")

# Polar H10 UUIDs
POLAR_H10_HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Global personalized baseline
GLOBAL_BASELINE = {'rmssd': 0.0, 'timestamp': None}

class PolarH10Bridge:
    """Fortified real sensor bridge — only used if bleak is available"""
    
    def __init__(self, timeout_seconds=30):
        global GLOBAL_BASELINE
        self.client = None
        self.device = None
        self.timeout = timeout_seconds
        self.heart_rate = 0
        self.rr_intervals = []
        self.rmssd = 0.0
        self.last_update = None
        self.baseline_rmssd = GLOBAL_BASELINE.get('rmssd', 0.0)
        self.ABS_QUORUM_THRESHOLD = 40.0
        self.ABS_ACTIVE_THRESHOLD = 20.0

    def _calculate_rmssd(self, rr_array):
        if len(rr_array) > 1:
            differences = np.diff(rr_array)
            return np.sqrt(np.mean(differences ** 2))
        return 0.0

    def assess_data_quality(self, rr_array):
        if len(rr_array) < 10:
            return "INSUFFICIENT_DATA"
        if np.any(rr_array < 300) or np.any(rr_array > 2000):
            return "ARTIFACT_DETECTED"
        if np.std(rr_array) > 250:
            return "POOR_SIGNAL_QUALITY"
        return "SOVEREIGN_CALIBRATED"

    async def discover_device(self):
        print("🛰️  SOVEREIGN PROTOCOL: Scanning for Polar H10...")
        try:
            devices = await BleakScanner.discover(timeout=15)
            for device in devices:
                if device.name and "Polar H10" in device.name:
                    print(f"✅ SENSOR ACQUIRED: {device.name} ({device.address})")
                    self.device = device
                    return True
            print("❌ POLAR H10 NOT DETECTED")
            return False
        except Exception as e:
            print(f"   Scan error: {e}")
            return False

    def hr_data_handler(self, sender, data):
        if data[0] & 0x01:
            self.heart_rate = int.from_bytes(data[1:3], 'little')
        else:
            self.heart_rate = data[1]
        
        new_rr = []
        offset = 3 if data[0] & 0x01 else 2
        while offset + 2 <= len(data):
            rr_val = int.from_bytes(data[offset:offset+2], 'little')
            rr_ms = rr_val / 1024.0 * 1000.0
            new_rr.append(rr_ms)
            offset += 2
        
        self.rr_intervals.extend(new_rr)
        self.rr_intervals = self.rr_intervals[-100:]
        self.last_update = datetime.now()
        
        if len(self.rr_intervals) >= 5:
            self.rmssd = self._calculate_rmssd(np.array(self.rr_intervals))

    async def connect_and_subscribe(self):
        if not self.device:
            return False
        try:
            self.client = BleakClient(self.device.address, timeout=self.timeout)
            await self.client.connect()
            await self.client.start_notify(POLAR_H10_HR_UUID, self.hr_data_handler)
            print("📡 PROTOCOL ESTABLISHED: Real HR/HRV stream active")
            return True
        except BleakError as e:
            print(f"❌ CONNECTION FAILED: {e}")
            return False

    async def calibrate_baseline(self, duration_seconds=120):
        global GLOBAL_BASELINE
        print("🧘 CALIBRATING PERSONAL BASELINE (2 min rest required)")
        if not await self.discover_device() or not await self.connect_and_subscribe():
            return False
        
        start_time = datetime.now()
        initial_count = len(self.rr_intervals)
        while (datetime.now() - start_time).seconds < duration_seconds:
            await asyncio.sleep(1)
        
        try:
            await self.client.stop_notify(POLAR_H10_HR_UUID)
            await self.client.disconnect()
        except:
            pass
        
        collected = self.rr_intervals[initial_count:]
        if len(collected) < 20:
            print("❌ INSUFFICIENT DATA FOR CALIBRATION")
            return False
        
        baseline = self._calculate_rmssd(np.array(collected))
        GLOBAL_BASELINE['rmssd'] = baseline
        GLOBAL_BASELINE['timestamp'] = datetime.now().isoformat()
        self.baseline_rmssd = baseline
        print(f"✅ BASELINE ESTABLISHED: {baseline:.2f}ms")
        print(f"   New Quorum Threshold: {baseline * 1.2:.2f}ms")
        return True

    async def read_hrv_data(self, duration_seconds=60):
        self.rr_intervals = []
        if not await self.discover_device() or not await self.connect_and_subscribe():
            return {"error": "SENSOR_FAILED"}
        
        print(f"⏳ ACQUIRING REAL BIOSIGNALS: {duration_seconds}s")
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < duration_seconds:
            await asyncio.sleep(1)
        
        try:
            await self.client.stop_notify(POLAR_H10_HR_UUID)
            await self.client.disconnect()
        except:
            pass
        
        quality = self.assess_data_quality(np.array(self.rr_intervals))
        threshold = self.baseline_rmssd * 1.2 if self.baseline_rmssd > 0 else self.ABS_QUORUM_THRESHOLD
        
        if quality == "SOVEREIGN_CALIBRATED" and self.rmssd >= threshold:
            status = "QUORUM_CALIBRATED"
            eligible = True
            gate = "BIOMETRIC_VETO_ARMED"
        else:
            status = "VETO_STANDBY"
            eligible = False
            gate = "BIOMETRIC_VETO_STANDBY"
        
        return {
            "veto_eligible": eligible,
            "rmssd": round(self.rmssd, 2),
            "hrv_status": status,
            "data_quality": quality,
            "gate_status": gate,
            "mode": "REAL_POLAR_H10",
            "timestamp": datetime.now().isoformat()
        }

# === GRACEFUL SIMULATION MODE (DeepSeek's gift) ===
def get_circadian_phase(hour: int) -> str:
    if 4 <= hour <= 7: return "Dawn - Rising Energy"
    elif 8 <= hour <= 11: return "Morning - Peak Alertness"
    elif 12 <= hour <= 15: return "Afternoon - Post-Lunch Dip"
    elif 16 <= hour <= 19: return "Evening - Second Wind"
    elif 20 <= hour <= 23: return "Night - Winding Down"
    else: return "Deep Night - Restorative Sleep"

async def read_simulated_hrv_data():
    print("   🎭 Graceful simulation active (no real sensor detected)")
    print("   🕊️  Circadian-aware coherence simulation")
    await asyncio.sleep(1.5)
    
    hour = datetime.now().hour
    phase = get_circadian_phase(hour)
    
    if 5 <= hour <= 8:
        base, var = 65, 15
    elif 9 <= hour <= 17:
        base, var = 45, 20
    elif 18 <= hour <= 22:
        base, var = 55, 15
    else:
        base, var = 70, 10
    
    rmssd = random.uniform(base - var, base + var)
    rmssd = max(20, min(rmssd, 120))
    
    quality_options = ["Excellent", "Good", "Fair", "Poor"]
    weights = [0.3, 0.4, 0.2, 0.1]
    data_quality = random.choices(quality_options, weights=weights)[0]
    
    threshold = 40.0
    if rmssd >= threshold and data_quality in ["Excellent", "Good"]:
        return {
            "veto_eligible": True,
            "rmssd": round(rmssd, 2),
            "hrv_status": "QUORUM_CALIBRATED",
            "data_quality": data_quality,
            "gate_status": "BIOMETRIC_VETO_ARMED",
            "mode": "SIMULATION",
            "circadian_phase": phase,
            "recommended_action": "Proceed with sovereign intent",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "veto_eligible": False,
            "rmssd": round(rmssd, 2),
            "hrv_status": "VETO_STANDBY",
            "data_quality": data_quality,
            "gate_status": "BIOMETRIC_VETO_STANDBY",
            "mode": "SIMULATION",
            "circadian_phase": phase,
            "recommended_action": "Practice deep breathing for 5 minutes",
            "timestamp": datetime.now().isoformat()
        }

# === SOVEREIGN ENTRY POINT ===
async def read_hrv_data():
    """Main gate: Real if possible • Graceful simulation if not"""
    print("=" * 60)
    print("🦅 VETO GATE CORE: INITIATING BIOSIGNAL PROTOCOL")
    print("=" * 60)
    
    if REAL_SENSOR_AVAILABLE:
        bridge = PolarH10Bridge()
        if bridge.baseline_rmssd == 0.0:
            await bridge.calibrate_baseline()
            bridge = PolarH10Bridge()  # Reload with new baseline
        
        result = await bridge.read_hrv_data(duration_seconds=60)
        if "error" not in result:
            return result
        print("   ⚠️ Real sensor failed — falling back to simulation")
    
    # Fallback to graceful simulation
    return await read_simulated_hrv_data()

# Self-test
if __name__ == "__main__":
    asyncio.run(read_hrv_data())