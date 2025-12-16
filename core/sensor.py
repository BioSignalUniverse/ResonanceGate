# core/sensor.py: Simulates the HRV Data Acquisition Layer
# Function: Provides raw time-series data, either live (future) or mocked (present).

import random
import time

class HRVSensor:
    """
    Simulates a real-time sensor interface (e.g., connection to a Polar or Garmin API).
    """
    def __init__(self, data_points=300):
        self.data_points = data_points

    def read_raw_nn_intervals(self, simulation_mode=True, coherence_level='average'):
        """
        Reads or simulates 300 seconds of NN (R-R) intervals in milliseconds (ms).
        
        Args:
            simulation_mode (bool): If True, generates mock data.
            coherence_level (str): 'low', 'average', or 'high' to influence mock data quality.
            
        Returns:
            list[float]: A list of NN intervals in milliseconds.
        """
        print(f"SENSOR: Reading {self.data_points}s of raw NN intervals...")
        time.sleep(0.1) 
        
        if not simulation_mode:
            # Placeholder for future API/hardware integration (e.g., using BLE or vendor SDK)
            print("SENSOR: Attempting real-time hardware connection...")
            return [] # Returns empty list if real data fails

        # Mock Data Generation based on desired coherence (for robust testing)
        
        base_interval = 1000.0 / 60.0 # Approx 1000ms at 60BPM
        
        if coherence_level == 'high':
            # Low variability (High Coherence/Low Stress, good RMSSD)
            variability = 5.0 # Very stable NN intervals
        elif coherence_level == 'low':
            # High variability (Low Coherence/High Stress, poor RMSSD)
            variability = 30.0
        else:
            # Average/default
            variability = 15.0 

        data = [
            base_interval + random.uniform(-variability, variability)
            for _ in range(self.data_points)
        ]
        
        return data

# Example Usage:
# sensor = HRVSensor()
# intervals = sensor.read_raw_nn_intervals(coherence_level='high')
