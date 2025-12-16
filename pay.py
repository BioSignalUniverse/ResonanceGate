# pay.py: Entry Point for Sovereign Logic (V1.1)
# Function: Orchestrates the Veto Sequence, bridging user input to the core modules.

import argparse
import sys
import os

# Ensure the V2.0 Shield is importable for core utilities (like RMSSD calculation)
try:
    from splendid_purge import (
        calculate_rmssd_mock,
        check_veto_condition,
        RMSSD_THRESHOLD_DEFAULT
    )
except ImportError:
    print("FATAL ERROR: splendid_purge.py (V2.0 Shield) not found or has errors.")
    sys.exit(1)

# --- Future V1.1 Imports (Placeholder) ---
# The sovereign logic lives here, replacing the simple check below.
# try:
#     from core.gate import SovereignGate
# except ImportError:
#     print("WARNING: core/gate.py not found. Running in V2.0 compatibility mode.")
#     SovereignGate = None
# ----------------------------------------


def run_veto_sequence(rmssd_value=None, threshold=RMSSD_THRESHOLD_DEFAULT):
    """
    Executes the Veto sequence based on provided RMSSD (or a simulated value).
    """
    print(f"\n--- RESONANCE GATE INITIATED ---")

    if rmssd_value is None:
        # Use V2.0 utility to simulate RMSSD if no real sensor data is available
        rmssd_value = calculate_rmssd_mock(simulate=True)
        print(f"MODE: Circadian Simulation Fallback (RMSSD: {rmssd_value:.2f}ms)")
    else:
        print(f"MODE: Direct Sensor Input (RMSSD: {rmssd_value:.2f}ms)")

    veto_enforced = check_veto_condition(rmssd_value, threshold)

    if not veto_enforced:
        print(f"✅ VETO CONDITION MET: RMSSD ({rmssd_value:.2f}ms) ≥ Threshold ({threshold}ms)")
        print("COHERENCE ACHIEVED. System grants access to higher purpose operation.")
        # Future V1.1 logic execution goes here (e.g., calling SovereignGate)
        # if SovereignGate:
        #    SovereignGate().execute_command()
    else:
        print(f"🛑 VETO ENFORCED: RMSSD ({rmssd_value:.2f}ms) < Threshold ({threshold}ms)")
        print("COHERENCE LOST. System honors biology and prohibits destructive operation.")
        sys.exit(0) # Exit cleanly, preventing further command execution


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
        help=f'Set a custom RMSSD threshold (default: {RMSSD_THRESHOLD_DEFAULT}ms).',
        default=RMSSD_THRESHOLD_DEFAULT
    )

    args = parser.parse_args()

    # If the user is running V1.1, they must have a V2.0 Shield present for core logic.
    if not os.path.exists("splendid_purge.py"):
        print("ERROR: Missing dependency. splendid_purge.py (V2.0 Shield) must be present.")
        sys.exit(1)

    run_veto_sequence(args.rmssd, args.threshold)
