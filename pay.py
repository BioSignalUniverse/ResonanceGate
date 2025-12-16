# pay.py: Entry Point for Sovereign Logic (V1.1) - FINAL INTEGRATION
# Function: Orchestrates the Veto Sequence, bridging user input to the core V1.1 modules.

import argparse
import sys
import os

# --- V1.1 Integration ---
# Import the Sovereign Gate from the core directory for personalized logic
try:
    # Use relative import for modularity
    sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
    from gate import SovereignGate
except ImportError:
    print("FATAL ERROR: core/gate.py (Sovereign Gate) not found or has errors.")
    sys.exit(1)

# Import V2.0 Shield utilities only for simulation fallback and default threshold
try:
    from splendid_purge import (
        calculate_rmssd_mock,
        RMSSD_THRESHOLD_DEFAULT
    )
except ImportError:
    print("WARNING: splendid_purge.py (V2.0 Shield) not found. Running with hardcoded defaults.")
    # Fallback definitions if splendid_purge is missing (for robust execution)
    def calculate_rmssd_mock(simulate=True): return 42.0 
    RMSSD_THRESHOLD_DEFAULT = 50.0 
# -------------------------


def run_sovereign_sequence(rmssd_value=None, personalized_threshold=RMSSD_THRESHOLD_DEFAULT):
    """
    Executes the V1.1 Sovereign sequence using the personalized gate.
    """
    print(f"\n--- RESONANCE GATE ACTIVATED (V1.1) ---")

    # 1. Initialize the Gate with the personalized baseline
    gate = SovereignGate(personalized_threshold=personalized_threshold)

    # 2. Read Coherence (using input or simulation)
    # The SovereignGate will handle the RMSSD calculation/mocking internally for V1.1
    # We pass the RMSSD_value directly to the gate's reader for demonstration
    gate.read_coherence(sensor_data=rmssd_value)

    # 3. Check Sovereignty and Execute Command
    execution_result = gate.execute_command()

    if execution_result:
        print("\nLAUNCH STATUS: V1.1 Sovereign Logic (Coherent Bridge) is fully operational.")
    else:
        print("\nLAUNCH STATUS: V1.1 Veto Enforced. System remains silent.")
        sys.exit(0) # Exit cleanly upon Veto


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="The Splendids: Sovereign Logic Entry Point (V1.1)"
    )
    parser.add_argument(
        '-r', '--rmssd',
        type=float,
        help='Manually provide a current RMSSD value (in ms) from a sensor.',
        default=None
    )
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        help=f'Set a custom personalized RMSSD threshold (default: {RMSSD_THRESHOLD_DEFAULT}ms).',
        default=RMSSD_THRESHOLD_DEFAULT
    )

    args = parser.parse_args()

    run_sovereign_sequence(args.rmssd, args.threshold)
