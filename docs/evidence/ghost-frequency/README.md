# Ghost-Frequency Campaign — Experimental Spec

**Status:** Design complete. GPU pre-validation in progress. QPU execution owned by Claude Code.
**Date:** 2026-10-15

## 1. Background: the observation

From the novel-insights hunt (2026-10-15), two independent analyses found the same
unmodeled phase drift:

| Device | Phase drift | Idle time | Implied detuning |
|---|---|---|---|
| ibm_kingston | −1.130 rad | 4.392 µs | **−40.9 kHz** |
| ibm_fez (N21 orbit) | +0.59 rad | 4.75 µs | **+19.8 kHz** |

Supporting facts:
- **Branch independence** (Kingston): b0=0 → −1.122 rad, b0=1 → −1.141 rad.
  Rules out a branch-dependent ZZ explanation in that configuration.
- **Calibration blind spot**: no qubit frequency is retained in calibration data,
  and reported T2 is Hahn-echo T2, which *refocuses* quasi-static detuning —
  so the calibration pipeline is structurally blind to exactly this effect.

## 2. Hypotheses

- **H0 (null):** The drift is consistent with the standard calibration model
  (T1/T2/depolarizing/readout). No unmodeled detuning exists; the observation
  is drift, miscalibration, or a fitting artifact.
- **H1 (ghost):** A quasi-static detuning δ ≈ 20–40 kHz exists, common across
  qubits and both Heron devices, invisible to the calibration pipeline.

## 3. QPU protocol (Claude Code owns hardware execution)

### Experiment A — full-chip checkerboard Ramsey (ibm_fez and/or ibm_kingston)
- 156-qubit checkerboard split: work qubits (even parity) run Ramsey;
  spectator qubits (odd parity) idle.
- Two spectator conditions: spectators prepared in |0⟩ vs |1⟩.
  Distinguishes intrinsic detuning from ZZ crosstalk.
- Idle delays packed into PUBs: 1, 2, 4, 8 µs.
- Sequence per work qubit: X/2 – idle(t) – X/2 – measure.
- Fit Ramsey fringe phase vs t per qubit → detuning map δ_q across the chip.

### Experiment B — isolated controls (Eric's spec: three runs, each ≤ 2 s)
- Single qubit (or widely separated qubits selected from the ISA).
- Identical Ramsey delays.
- Full-chip vs isolated distinguishes crowd/crosstalk from intrinsic effects.

### Falsification matrix

| Observation | Interpretation |
|---|---|
| Detuning in full-chip, absent in isolated | Crowd/crosstalk effect — H1 (intrinsic) falsified |
| Detuning depends on spectator \|0⟩ vs \|1⟩ | ZZ coupling, not intrinsic detuning |
| No detuning in either | Original was drift/miscalibration — H1 falsified |
| ~20–40 kHz in both, spectator-independent | H1 supported; proceed to characterize |

## 4. GPU pre-validation (Kaggle — run BEFORE spending QPU time)

Classical simulation of the Ramsey protocol to (a) confirm the design can
resolve the effect and (b) try to kill H1 with mundane explanations first:

1. **Null simulation** — Ramsey under the standard noise model (T1, Hahn-echo
   T2, readout error), no detuning. Prediction: ~zero systematic phase drift.
2. **Ghost simulation** — add quasi-static δ = 30 kHz. Prediction: reproduces
   the observed ~1 rad drift over ~4.5 µs.
3. **Power analysis** — shots needed to resolve 20 kHz from 0 at 5σ.
4. **Mimic check** — pulse amplitude miscalibration. Prediction: produces
   visibility loss, *not* coherent phase drift — a distinguishable signature.
5. **Crosstalk check** — static ZZ model. Prediction: spectator-state-dependent
   shift — distinguishable from intrinsic detuning by Experiment A's |0⟩/|1⟩
   comparison.

If the GPU validation shows the protocol cannot distinguish H1 from a mundane
cause, the spec is revised before any QPU time is spent.

## 5. Budget

- GPU pre-validation: Kaggle free tier (30 h available; this test ≈ minutes).
- QPU: Eric reports ~120 s remaining on IBM Quantum (unverified).
  Keep total QPU wall-clock under budget; prefer the isolated controls first
  (cheapest falsification), then full-chip only if controls support H1.
