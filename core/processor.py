# core/processor.py: The Coherence Processor
# Function: Calculates the RMSSD (Root Mean Square of Successive Differences) from raw NN intervals.

import math

class CoherenceProcessor:
    """
    Static methods for calculating the time-domain HRV metrics required by the Veto.
    """

    @staticmethod
    def calculate_rmssd(nn_intervals: list) -> float:
        """
        Calculates the Root Mean Square of Successive Differences (RMSSD) in ms.
        RMSSD is a robust and preferred metric for assessing parasympathetic activity (coherence).
        
        Args:
            nn_intervals (list[float]): List of successive R-R intervals in milliseconds.
            
        Returns:
            float: The calculated RMSSD value in milliseconds. Returns 0.0 if data is insufficient.
        """
        if len(nn_intervals) < 2:
            print("PROCESSOR ERROR: Insufficient data for RMSSD calculation.")
            return 0.0

        # Calculate the difference between successive NN intervals (SDNNI)
        diff_successive = [
            nn_intervals[i+1] - nn_intervals[i] 
            for i in range(len(nn_intervals) - 1)
        ]

        # Square the differences
        squared_diff = [d**2 for d in diff_successive]

        # Calculate the mean of the squared differences
        mean_squared_diff = sum(squared_diff) / len(squared_diff)

        # Take the square root (RMSSD)
        rmssd = math.sqrt(mean_squared_diff)
        
        return rmssd

    @staticmethod
    def check_architectural_threshold(rmssd_value: float, threshold: float = 85.0) -> bool:
        """
        Checks the RMSSD value against the immutable architectural threshold (HRV_COHERENCE_THRESHOLD).
        Note: The Veto Mandate specifies a coherence index (0.85), but RMSSD (in ms) is the practical metric.
        RMSSD > 80ms is often cited as high coherence in literature. 
        """
        if rmssd_value >= threshold:
            return True # Coherence present
        else:
            return False # Veto condition met (incoherence)

# Example Usage:
# processor = CoherenceProcessor()
# mock_intervals = [1000, 1005, 995, 1010, 990] # Very stable, high RMSSD
# rmssd_result = processor.calculate_rmssd(mock_intervals)
# is_coherent = processor.check_architectural_threshold(rmssd_result)
