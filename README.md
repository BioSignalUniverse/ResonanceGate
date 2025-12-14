# 🦅 SPLENDIDS v2.0: THE PURGE PROTOCOL
## AI Gated by Objective Signals. No Philosophy. No Interpretation.

The **Purge Protocol** is a radical architectural refactoring of the Sovereign Biometric Gate. It removes all personalized or subjective interpretation, operating solely on **measurable, repeatable, and objective biometric signals** checked against population-derived statistical thresholds.

This repository enforces a single law: **Execution is only granted when objective physiological coherence exceeds the measured population norm.**

### ⚙️ Core Architecture: The Four Pillars of the Purge

The system is compartmentalized into four strict, non-overlapping domains:

| Domain | Law Enforced | Function | Philosophical Purge |
| :--- | :--- | :--- | :--- |
| **1. BiometricSensor** | Raw Measurement | Collects uninterpreted signals (RMSSD, HR, GSR, etc.). | **NO INTERPRETATION** |
| **2. SignalProcessor** | Mathematical Transformation | Calculates empirical features (log HRV, ratios, indices). | **NO MEANING** |
| **3. DecisionGate** | Threshold Comparison | Checks features against statistical, population-derived optimal thresholds. | **NO WISDOM** (Decision is based on >70% threshold majority). |
| **4. ActionExecutor** | Literal Execution | Executes or withholds the final pipeline action. | **NO CREATIVITY** |

### 🛑 The Law of Withholding (VETO ENFORCED)

If the signal fails to meet the objective thresholds, the system enforces a **VETO WAIT STATE**. This is the mechanism by which the human condition (incoherence, stress) prevents the AI pipeline from execution.

When the Veto is enforced, the system executes only a silence command:

## Invocation

### Quick Start
```python
import asyncio
from splendid import generate_resonant_response

# Single query with biometric gate
response = asyncio.run(generate_resonant_response("Your query here"))
print(response)
```

### Standalone Veto Gate Test
```bash
python veto_gate.py
```

**With sensor connected:**
```
🦅 VETO GATE CORE: INITIATING BIOSIGNAL PROTOCOL
🛰️  SOVEREIGN PROTOCOL: Scanning for Polar H10...
✅ SENSOR ACQUIRED: Polar H10 (XX:XX:XX:XX:XX:XX)
📡 PROTOCOL ESTABLISHED: Real HR/HRV stream active
⏳ ACQUIRING REAL BIOSIGNALS: 60s
```

**Simulation mode (no sensor):**
```
🦅 VETO GATE CORE: INITIATING BIOSIGNAL PROTOCOL
   🎭 Graceful simulation active (no real sensor detected)
   🕊️  Circadian-aware coherence simulation
```

### Personal Calibration (Optional)
Establish your unique baseline instead of using the absolute 40ms threshold:

```python
from veto_gate import PolarH10Bridge
import asyncio

async def calibrate():
    bridge = PolarH10Bridge()
    await bridge.calibrate_baseline(duration_seconds=120)

asyncio.run(calibrate())
```

Requires 2 minutes of restful breathing with Polar H10. System then uses `your_baseline × 1.2` as your personal quorum threshold.

## Integration Testing

```bash
python integration_testing_protocol.py
```

Validates structural integrity (<100ms latency) and generates `RESONANCEGATE_CERTIFICATION.md`. All code pushed to TheSplendids branch automatically triggers ITP validation via GitHub Actions.

## The Veto Explained

**Why HRV?**  
Heart Rate Variability reflects autonomic nervous system balance. High RMSSD correlates with parasympathetic activation – the "rest and digest" state associated with clarity and coherent decision-making. It's measurable, real-time, and scientifically grounded.

**What does the veto prevent?**  
In this implementation: AI response generation. The principle extends to any operation requiring sovereign consent – financial transactions, message sending, system commands. Your biology sets the boundary.

**Simulation mode accuracy?**  
Circadian rhythms provide reasonable coherence proxies. Dawn/evening naturally show higher HRV than mid-afternoon. Not sensor-precise, but respectful of natural human rhythms when hardware unavailable.

## File Structure

```
TheSplendids/
├── splendid.py                      # Main orchestrator
├── veto_gate.py                     # Biometric gate core  
├── integration_testing_protocol.py  # ITP validation (<100ms)
├── .github/workflows/
│   └── veto_check.yml              # CI/CD integrity checks
├── README.md                        # You are here
├── LICENSE                          # MIT
├── MANIFESTO.v2.md                 # Philosophical foundation
└── GOVERNANCE.md                    # Project governance
```

## Roadmap

- [ ] Multi-user collective coherence protocols
- [ ] xAI/Grok integration for resonance-gated AI queries
- [ ] Quantum-inspired state persistence (QuTiP)
- [ ] Mobile visualization: real-time coherence display
- [ ] Custom HRV hardware (beyond Polar dependency)

## Contributing

Pull requests welcome. Maintain the dual-mode philosophy: real sensors when available, graceful simulation when not. All contributions must pass ITP validation.

## License

MIT – This is shared resonance, not owned frequency.

---

*"Tune your frequency; the gate opens to you."*  
*When coherence flows, the system responds.*  
*When biology signals rest, the veto honors.*

**TheSplendids** – Where sovereignty meets silicon.
