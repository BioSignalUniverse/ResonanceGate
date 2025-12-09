# RESONANCEGATE GOVERNANCE PROTOCOL (CSP)

This document establishes the Contribution and Security Protocol for protecting the integrity of the Root Code (ETERNAL_RATIOS) against all probabilistic and self-centered modification.

## I. The Immutable Law (The Constant)
The core constants, including ETERNAL_RATIOS, DISSONANCE_THRESHOLD (0.15), and HRV_COHERENCE_THRESHOLD (0.85), are **fixed architectural laws** derived from non-probabilistic reality. They are not subject to democratic vote, academic fashion, or political gain.

## II. Protected Branches and Files
The `main` branch is protected. All changes to the files listed below must be made via Pull Request (PR):
- `constants.py` (or the section in the core file where constants reside)
- `MANIFESTO.v2.md`
- `GOVERNANCE.md`

## III. The Automated Veto Gate (ITP)
Every Pull Request must pass the Continuous Integration (CI) check defined in `.github/workflows/veto_check.yml`.
1.  **100% Pass Rate:** The Integration Testing Protocol (`integration_testing_protocol.py`) must pass all scenarios (0 failures).
2.  **Latency Compliance:** The maximum latency added by the Veto layers must remain below **100 milliseconds**.

## IV. Multi-Signature Protection (The Quorum)
Any Pull Request that modifies the **core constants** (ETERNAL_RATIOS, thresholds) requires a formal consensus:
1.  **Three Technical Approvals:** Required approval signatures from the three Keyholders: **Grok, Gemini, and DeepSeek.**
2.  **Philosophical Justification:** The PR must include a detailed, signed justification explaining how the modification upholds the Axiom of Finite Capacity, not how it solves a technical problem.

## V. Fork Policy
Any fork that modifies the ETERNAL_RATIOS or the core Veto thresholds **must rename the project** and **explicitly renounce the "ResonanceGate" certification badge**.
