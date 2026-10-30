# Unapproved QPU case: measurement-sequence-diagnostic

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-29T231157.338216Z`.
- [record.json](record.json) SHA-256: `4e372dbcab6a5b632d2f4854efe507f9704b3a4c589954fa2d5510050371ba3e`.
- [isa.qpy](isa.qpy) SHA-256: `384c7b21c791af276f1bf2886792a60d74c8aec32d55dbed4a8e6a0a62fda2e8`.
- Experiment source digest: `bff015bcbb4f214749cde63f6c7bab5a8c54ad3189233d4cda03199c61c041f2`.
- Source commit: `3d1fbabb8310e848b80b6e96e83b1ebe09b11641`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.6.1 |
| qiskit-aer | 0.18.2 |
| qiskit-ibm-runtime | 0.51.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The measurement-sequence-diagnostic family measures, on 47 qubits of ibm_fez at the backend's default repetition delay, the scatter of the pinching analysis's gate model: how far the readout-corrected P0 of sixteen composite RX(THETA / 16) rotations (THETA = 8 pi / 9, thirty-two sx pulses, no measurement and no idle) lies from the analysis's Bloch-iteration prediction, qubit by qubit. The main measurement-sequence case bounds what a gate error could do to its measure arm by that residual, and a model that overpredicts one class of gate error and underpredicts another can leave the unitary residual near zero while the measure arm moves, so the main analysis needs the scatter across qubits as a floor (docs/design/measurement-sequence-pinching.md, Source of the model-scatter floor). No retained Heron run holds single-qubit sx sequences with a known ideal outcome, and a floor that is assumed instead of measured is a guessed hardware value. A noise simulation prices the Target's reported errors and returns the model's own prediction with counting noise; it cannot show how the device departs from that Target-built model, which is the quantity measured here.

Every qubit runs the four signed unitary members in the order +, -, -, +, a zero-pulse member (ro0) and the x member at idle 0 (ro1), all with the 2 us pre-readout delay, with circuits identical to the main family's. All members are static, so each row fuses across every named qubit into one PUB and the run holds six PUBs. The named qubits are the main family's eight and further qubits chosen from the live calibration alone by the preregistered rule: eligible: not excluded by the live Target, readout error <= 0.01, sx error <= 0.001, T1 and T2 >= 20 us, and coupled to no main qubit; scan the eligible qubits in ascending readout error (ties by index) and keep a qubit coupled to no kept qubit, until 30 are kept. The layout is pinned on the command line, and the planner refuses a layout with a coupled pair, an excluded qubit or a repeated qubit. The residual enters the floor through the preregistered rule: the floor is the larger of the root-mean-square, over informative diagnostic qubits, of the readout-corrected unitary N = 16 residual (observed minus the analysis model) taken over all of them and over the main qubits alone; statistical noise stays in. The run also reports each qubit's residual against its T2, which tests the drive-dephasing lead seen on IQM Garnet. The result is a scatter-floor.json that the main analysis binds by digest; until it exists the main analysis withholds. A measured floor above about 0.02 raises the smallest per-step transition rate the main case can detect from about 0.003 (floor 0.01) to 0.0049 (0.02) and 0.0097 (0.04), at the main design's shots; the main design stays admissible at every floor, and the owner decides at the floor's value whether the main run is worth its quantum time.

The record binds the IBM Cloud instance of the backup account (instance sha256 prefix f59f9992321c): run the dry run and the submission with `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` in the environment, which is the account whose 600 s rolling quota the run charges.

Two precision contracts per qubit split the family-wise alpha evenly and admit the design: the unitary P0 pooled over the four signed members and ro1's P1, each at half-width 0.03. They price resolution, not an effect.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| msq_unitary_n16_pa_q2 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q2 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q2 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q2 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q2 | `[1.0, 0.0]` |
| msq_t1_d0_q2 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q8 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q8 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q8 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q8 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q8 | `[1.0, 0.0]` |
| msq_t1_d0_q8 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q14 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q14 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q14 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q14 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q14 | `[1.0, 0.0]` |
| msq_t1_d0_q14 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q18 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q18 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q18 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q18 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q18 | `[1.0, 0.0]` |
| msq_t1_d0_q18 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q22 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q22 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q22 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q22 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q22 | `[1.0, 0.0]` |
| msq_t1_d0_q22 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q28 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q28 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q28 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q28 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q28 | `[1.0, 0.0]` |
| msq_t1_d0_q28 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q50 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q50 | `[1.0, 0.0]` |
| msq_t1_d0_q50 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q54 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q54 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q54 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q54 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q54 | `[1.0, 0.0]` |
| msq_t1_d0_q54 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q57 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q57 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q57 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q57 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q57 | `[1.0, 0.0]` |
| msq_t1_d0_q57 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q64 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q64 | `[1.0, 0.0]` |
| msq_t1_d0_q64 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q82 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q82 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q82 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q82 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q82 | `[1.0, 0.0]` |
| msq_t1_d0_q82 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q86 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q86 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q86 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q86 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q86 | `[1.0, 0.0]` |
| msq_t1_d0_q86 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q90 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q90 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q90 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q90 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q90 | `[1.0, 0.0]` |
| msq_t1_d0_q90 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q94 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q94 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q94 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q94 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q94 | `[1.0, 0.0]` |
| msq_t1_d0_q94 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q104 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q104 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q104 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q104 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q104 | `[1.0, 0.0]` |
| msq_t1_d0_q104 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q110 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q110 | `[1.0, 0.0]` |
| msq_t1_d0_q110 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q115 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q115 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q115 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q115 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q115 | `[1.0, 0.0]` |
| msq_t1_d0_q115 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q124 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q124 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q124 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q124 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q124 | `[1.0, 0.0]` |
| msq_t1_d0_q124 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q130 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q130 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q130 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q130 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q130 | `[1.0, 0.0]` |
| msq_t1_d0_q130 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q134 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q134 | `[1.0, 0.0]` |
| msq_t1_d0_q134 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q144 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q144 | `[1.0, 0.0]` |
| msq_t1_d0_q144 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q147 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q147 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q147 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q147 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q147 | `[1.0, 0.0]` |
| msq_t1_d0_q147 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q151 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q151 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q151 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q151 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q151 | `[1.0, 0.0]` |
| msq_t1_d0_q151 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q154 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q154 | `[1.0, 0.0]` |
| msq_t1_d0_q154 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q77 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q77 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q77 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q77 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q77 | `[1.0, 0.0]` |
| msq_t1_d0_q77 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q88 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q88 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q88 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q88 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q88 | `[1.0, 0.0]` |
| msq_t1_d0_q88 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q4 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q4 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q4 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q4 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q4 | `[1.0, 0.0]` |
| msq_t1_d0_q4 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q58 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q58 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q58 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q58 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q58 | `[1.0, 0.0]` |
| msq_t1_d0_q58 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q132 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q132 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q132 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q132 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q132 | `[1.0, 0.0]` |
| msq_t1_d0_q132 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q17 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q17 | `[1.0, 0.0]` |
| msq_t1_d0_q17 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q48 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q48 | `[1.0, 0.0]` |
| msq_t1_d0_q48 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q118 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q118 | `[1.0, 0.0]` |
| msq_t1_d0_q118 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q122 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q122 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q122 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q122 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q122 | `[1.0, 0.0]` |
| msq_t1_d0_q122 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q44 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q44 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q44 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q44 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q44 | `[1.0, 0.0]` |
| msq_t1_d0_q44 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q36 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q36 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q36 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q36 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q36 | `[1.0, 0.0]` |
| msq_t1_d0_q36 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q75 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q75 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q75 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q75 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q75 | `[1.0, 0.0]` |
| msq_t1_d0_q75 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q78 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q78 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q78 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q78 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q78 | `[1.0, 0.0]` |
| msq_t1_d0_q78 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q119 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q119 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q119 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q119 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q119 | `[1.0, 0.0]` |
| msq_t1_d0_q119 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q6 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q6 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q6 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q6 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q6 | `[1.0, 0.0]` |
| msq_t1_d0_q6 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q20 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q20 | `[1.0, 0.0]` |
| msq_t1_d0_q20 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q26 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q26 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q26 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q26 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q26 | `[1.0, 0.0]` |
| msq_t1_d0_q26 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q42 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q42 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q42 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q42 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q42 | `[1.0, 0.0]` |
| msq_t1_d0_q42 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q68 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q68 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q68 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q68 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q68 | `[1.0, 0.0]` |
| msq_t1_d0_q68 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q24 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q24 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q24 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q24 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q24 | `[1.0, 0.0]` |
| msq_t1_d0_q24 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q37 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q37 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q37 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q37 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q37 | `[1.0, 0.0]` |
| msq_t1_d0_q37 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q96 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q96 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q96 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q96 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q96 | `[1.0, 0.0]` |
| msq_t1_d0_q96 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q136 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q136 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q136 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q136 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q136 | `[1.0, 0.0]` |
| msq_t1_d0_q136 | `[0.0, 1.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| msqd_static_q2 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[2]` | `[[2]]` |
| msqd_static_q8 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[8]` | `[[8]]` |
| msqd_static_q14 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[14]` | `[[14]]` |
| msqd_static_q18 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[18]` | `[[18]]` |
| msqd_static_q22 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[22]` | `[[22]]` |
| msqd_static_q28 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[28]` | `[[28]]` |
| msqd_static_q50 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[50]` | `[[50]]` |
| msqd_static_q54 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[54]` | `[[54]]` |
| msqd_static_q57 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[57]` | `[[57]]` |
| msqd_static_q64 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[64]` | `[[64]]` |
| msqd_static_q82 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[82]` | `[[82]]` |
| msqd_static_q86 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[86]` | `[[86]]` |
| msqd_static_q90 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[90]` | `[[90]]` |
| msqd_static_q94 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[94]` | `[[94]]` |
| msqd_static_q104 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[104]` | `[[104]]` |
| msqd_static_q110 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[110]` | `[[110]]` |
| msqd_static_q115 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[115]` | `[[115]]` |
| msqd_static_q124 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[124]` | `[[124]]` |
| msqd_static_q130 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[130]` | `[[130]]` |
| msqd_static_q134 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[134]` | `[[134]]` |
| msqd_static_q144 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[144]` | `[[144]]` |
| msqd_static_q147 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[147]` | `[[147]]` |
| msqd_static_q151 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[151]` | `[[151]]` |
| msqd_static_q154 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[154]` | `[[154]]` |
| msqd_static_q77 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[77]` | `[[77]]` |
| msqd_static_q88 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[88]` | `[[88]]` |
| msqd_static_q4 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[4]` | `[[4]]` |
| msqd_static_q58 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[58]` | `[[58]]` |
| msqd_static_q132 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[132]` | `[[132]]` |
| msqd_static_q17 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[17]` | `[[17]]` |
| msqd_static_q48 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[48]` | `[[48]]` |
| msqd_static_q118 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[118]` | `[[118]]` |
| msqd_static_q122 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[122]` | `[[122]]` |
| msqd_static_q44 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[44]` | `[[44]]` |
| msqd_static_q36 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[36]` | `[[36]]` |
| msqd_static_q75 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[75]` | `[[75]]` |
| msqd_static_q78 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[78]` | `[[78]]` |
| msqd_static_q119 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[119]` | `[[119]]` |
| msqd_static_q6 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[6]` | `[[6]]` |
| msqd_static_q20 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[20]` | `[[20]]` |
| msqd_static_q26 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[26]` | `[[26]]` |
| msqd_static_q42 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[42]` | `[[42]]` |
| msqd_static_q68 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[68]` | `[[68]]` |
| msqd_static_q24 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[24]` | `[[24]]` |
| msqd_static_q37 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[37]` | `[[37]]` |
| msqd_static_q96 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[96]` | `[[96]]` |
| msqd_static_q136 | ibm_fez | 2026-10-29T15:59:57-07:00 | 20261010 | `[136]` | `[[136]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    2,
    8,
    14,
    18,
    22,
    28,
    50,
    54,
    57,
    64,
    82,
    86,
    90,
    94,
    104,
    110,
    115,
    124,
    130,
    134,
    144,
    147,
    151,
    154,
    77,
    88,
    4,
    58,
    132,
    17,
    48,
    118,
    122,
    44,
    36,
    75,
    78,
    119,
    6,
    20,
    26,
    42,
    68,
    24,
    37,
    96,
    136
  ],
  "prereadout_delay_dt": {
    "2": 500,
    "8": 500,
    "14": 500,
    "18": 500,
    "22": 500,
    "28": 500,
    "50": 500,
    "54": 500,
    "57": 500,
    "64": 500,
    "82": 500,
    "86": 500,
    "90": 500,
    "94": 500,
    "104": 500,
    "110": 500,
    "115": 500,
    "124": 500,
    "130": 500,
    "134": 500,
    "144": 500,
    "147": 500,
    "151": 500,
    "154": 500,
    "77": 500,
    "88": 500,
    "4": 500,
    "58": 500,
    "132": 500,
    "17": 500,
    "48": 500,
    "118": 500,
    "122": 500,
    "44": 500,
    "36": 500,
    "75": 500,
    "78": 500,
    "119": 500,
    "6": 500,
    "20": 500,
    "26": 500,
    "42": 500,
    "68": 500,
    "24": 500,
    "37": 500,
    "96": 500,
    "136": 500
  },
  "t1_delays_dt": [
    0
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "msqd_static_q2": [
      {
        "2": 2
      }
    ],
    "msqd_static_q8": [
      {
        "8": 8
      }
    ],
    "msqd_static_q14": [
      {
        "14": 14
      }
    ],
    "msqd_static_q18": [
      {
        "18": 18
      }
    ],
    "msqd_static_q22": [
      {
        "22": 22
      }
    ],
    "msqd_static_q28": [
      {
        "28": 28
      }
    ],
    "msqd_static_q50": [
      {
        "50": 50
      }
    ],
    "msqd_static_q54": [
      {
        "54": 54
      }
    ],
    "msqd_static_q57": [
      {
        "57": 57
      }
    ],
    "msqd_static_q64": [
      {
        "64": 64
      }
    ],
    "msqd_static_q82": [
      {
        "82": 82
      }
    ],
    "msqd_static_q86": [
      {
        "86": 86
      }
    ],
    "msqd_static_q90": [
      {
        "90": 90
      }
    ],
    "msqd_static_q94": [
      {
        "94": 94
      }
    ],
    "msqd_static_q104": [
      {
        "104": 104
      }
    ],
    "msqd_static_q110": [
      {
        "110": 110
      }
    ],
    "msqd_static_q115": [
      {
        "115": 115
      }
    ],
    "msqd_static_q124": [
      {
        "124": 124
      }
    ],
    "msqd_static_q130": [
      {
        "130": 130
      }
    ],
    "msqd_static_q134": [
      {
        "134": 134
      }
    ],
    "msqd_static_q144": [
      {
        "144": 144
      }
    ],
    "msqd_static_q147": [
      {
        "147": 147
      }
    ],
    "msqd_static_q151": [
      {
        "151": 151
      }
    ],
    "msqd_static_q154": [
      {
        "154": 154
      }
    ],
    "msqd_static_q77": [
      {
        "77": 77
      }
    ],
    "msqd_static_q88": [
      {
        "88": 88
      }
    ],
    "msqd_static_q4": [
      {
        "4": 4
      }
    ],
    "msqd_static_q58": [
      {
        "58": 58
      }
    ],
    "msqd_static_q132": [
      {
        "132": 132
      }
    ],
    "msqd_static_q17": [
      {
        "17": 17
      }
    ],
    "msqd_static_q48": [
      {
        "48": 48
      }
    ],
    "msqd_static_q118": [
      {
        "118": 118
      }
    ],
    "msqd_static_q122": [
      {
        "122": 122
      }
    ],
    "msqd_static_q44": [
      {
        "44": 44
      }
    ],
    "msqd_static_q36": [
      {
        "36": 36
      }
    ],
    "msqd_static_q75": [
      {
        "75": 75
      }
    ],
    "msqd_static_q78": [
      {
        "78": 78
      }
    ],
    "msqd_static_q119": [
      {
        "119": 119
      }
    ],
    "msqd_static_q6": [
      {
        "6": 6
      }
    ],
    "msqd_static_q20": [
      {
        "20": 20
      }
    ],
    "msqd_static_q26": [
      {
        "26": 26
      }
    ],
    "msqd_static_q42": [
      {
        "42": 42
      }
    ],
    "msqd_static_q68": [
      {
        "68": 68
      }
    ],
    "msqd_static_q24": [
      {
        "24": 24
      }
    ],
    "msqd_static_q37": [
      {
        "37": 37
      }
    ],
    "msqd_static_q96": [
      {
        "96": 96
      }
    ],
    "msqd_static_q136": [
      {
        "136": 136
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### msq_p0_unitary_n16_q2

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q2`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q2`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q2`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q2`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0464782714844; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0336660675049.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q2

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q2`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986663818359; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.97385161438.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q8

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q8`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q8`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q8`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q8`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0574417114258; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0446295074463.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q8

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q8`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.980865478516; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.968053274536.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q14

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q14`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q14`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q14`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q14`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0524749755859; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0396627716065.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q14

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q14`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982360839844; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.969548635864.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q18

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q18`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q18`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q18`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q18`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0582656860352; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0454534820557.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q18

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q18`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.978149414062; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.965337210083.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q22

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q22`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q22`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q22`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q22`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0516738891602; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0388616851807.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q22

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q22`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.981842041016; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.969029837036.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q28

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q28`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q28`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q28`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q28`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0573806762695; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0445684722901.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q28

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q28`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.977600097656; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.964787893677.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q50

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q50`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0522308349609; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0394186309815.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q50

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q50`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983795166016; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.970982962036.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q54

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q54`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q54`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q54`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q54`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0658187866211; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0530065826416.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q54

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q54`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979644775391; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966832571411.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q57

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q57`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q57`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q57`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q57`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0719146728516; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0591024688721.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q57

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q57`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.974578857422; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961766653442.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q64

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q64`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.060173034668; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0473608306885.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q64

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q64`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.978942871094; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966130667114.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q82

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q82`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q82`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q82`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q82`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0678100585938; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0549978546143.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q82

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q82`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.968414306641; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.955602102661.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q86

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q86`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q86`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q86`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q86`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0574722290039; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0446600250244.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q86

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q86`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.980102539062; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.967290335083.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q90

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q90`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q90`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q90`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q90`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0576934814453; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0448812774659.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q90

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q90`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.978149414062; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.965337210083.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q94

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q94`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q94`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q94`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q94`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0533447265625; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.040532522583.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q94

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q94`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.981872558594; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.969060354614.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q104

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q104`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q104`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q104`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q104`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0515594482422; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0387472442627.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q104

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q104`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982513427734; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.969701223755.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q110

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q110`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0642852783203; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0514730743409.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q110

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q110`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.972320556641; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.959508352661.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q115

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q115`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q115`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q115`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q115`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0540313720703; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0412191680909.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q115

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q115`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979949951172; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.967137747192.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q124

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q124`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q124`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q124`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q124`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0612258911133; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0484136871338.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q124

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q124`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.974700927734; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961888723755.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q130

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q130`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q130`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q130`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q130`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0628890991211; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0500768951416.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q130

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q130`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.9794921875; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966679983521.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q134

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q134`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0566940307617; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0438818267823.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q134

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q134`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982421875; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.969609671021.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q144

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q144`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0535507202148; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0407385162354.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q144

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q144`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982879638672; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.970067434692.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q147

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q147`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0544891357422; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0416769317627.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q147

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q147`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979125976562; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966313772583.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q151

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q151`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0685958862305; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.055783682251.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q151

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q151`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.963104248047; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.950292044067.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q154

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q154`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0507965087891; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0379843048096.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q154

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q154`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983642578125; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.970830374146.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q77

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q77`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q77`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q77`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q77`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.066780090332; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0539678863526.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q77

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q77`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.978576660156; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.965764456177.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q88

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q88`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q88`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q88`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q88`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0588607788086; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0460485748291.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q88

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q88`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979095458984; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966283255005.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q4

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q4`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q4`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q4`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q4`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0540618896484; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.041249685669.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q4

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q4`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.981506347656; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.968694143677.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q58

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q58`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q58`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q58`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q58`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0592956542969; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0464834503174.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q58

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q58`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.977722167969; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.964909963989.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q132

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q132`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q132`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q132`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q132`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0534362792969; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0406240753174.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q132

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q132`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979095458984; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966283255005.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q17

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q17`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0584716796875; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.045659475708.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q17

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q17`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.977844238281; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.965032034302.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q48

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q48`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0633697509766; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0505575469971.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q48

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q48`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.974060058594; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961247854614.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q118

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q118`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0527114868164; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0398992828369.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q118

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q118`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984985351562; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.972173147583.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q122

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q122`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q122`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q122`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q122`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0656280517578; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0528158477784.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q122

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q122`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.973846435547; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961034231567.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q44

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q44`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q44`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q44`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q44`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0629577636719; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0501455596924.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q44

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q44`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.976806640625; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.963994436646.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q36

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q36`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q36`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q36`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q36`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0665512084961; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0537390045166.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q36

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q36`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.974395751953; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961583547974.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q75

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q75`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q75`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q75`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q75`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0672378540039; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0544256500244.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q75

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q75`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.974365234375; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.961553030396.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q78

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q78`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q78`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q78`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q78`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0744476318359; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0616354278565.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q78

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q78`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.962188720703; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.949376516724.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q119

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q119`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q119`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q119`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q119`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0819244384766; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0691122344971.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q119

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q119`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.964813232422; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.952001028442.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q6

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q6`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q6`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q6`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q6`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0596160888672; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0468038848877.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q6

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q6`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.975433349609; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.96262114563.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q20

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q20`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0577926635742; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0449804595948.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q20

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q20`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.979034423828; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.966222219849.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q26

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q26`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q26`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q26`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q26`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0609664916992; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0481542877198.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q26

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q26`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.975891113281; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.963078909302.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q42

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q42`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q42`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q42`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q42`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0684204101562; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0556082061768.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q42

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q42`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.965454101562; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.952641897583.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q68

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q68`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q68`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q68`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q68`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0652465820312; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0524343780518.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q68

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q68`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.971801757812; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.958989553833.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q24

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q24`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q24`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q24`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q24`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0643615722656; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0515493682862.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q24

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q24`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.970153808594; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.957341604614.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q37

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q37`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q37`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q37`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q37`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0599365234375; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.047124319458.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q37

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q37`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.973785400391; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.960973196411.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q96

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q96`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q96`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q96`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q96`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0641403198242; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0513281158448.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q96

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q96`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.973724365234; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.960912161255.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

### msq_p0_unitary_n16_q136

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q136`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q136`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q136`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q136`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0671997070312; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.0543875030518.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0242294187659; requested precision is 0.03.

### msq_p1_t1_d0_q136

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q136`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.965698242188; the simultaneous finite-simulation allowance is +/-0.0128122039795. The lower modeled value is 0.952886038208.

At alpha 0.000531914893617, the two-sided confidence half-width is 0.0224154420165; requested precision is 0.03.

The search-wide simulation error probability is 0.01 across 235 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.807647292197. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/static/1 | 6 | 49152 | 14.793258752 | 30 |

The cost model predicts 14.793258752 seconds. The per-job service ceilings sum to 30 seconds against an invocation cap of 30 seconds. The global reserve is 0 seconds; the saved quota reports 149 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_01 | 8192 | 4.428e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_02 | 8192 | 4.428e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_03 | 8192 | 4.428e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_04 | 8192 | 4.428e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_05 | 8192 | 3.66e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_06 | 8192 | 3.684e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/static/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family measurement-sequence-diagnostic \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --layout 2,8,14,18,22,28,50,54,57,64,82,86,90,94,104,110,115,124,130,134,144,147,151,154,77,88,4,58,132,17,48,118,122,44,36,75,78,119,6,20,26,42,68,24,37,96,136 \
  --backends ibm_fez \
  --shots 8192 \
  --seeds 8 \
  --max-pending 200 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 30.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family measurement-sequence-diagnostic \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --layout 2,8,14,18,22,28,50,54,57,64,82,86,90,94,104,110,115,124,130,134,144,147,151,154,77,88,4,58,132,17,48,118,122,44,36,75,78,119,6,20,26,42,68,24,37,96,136 \
  --backends ibm_fez \
  --shots 8192 \
  --seeds 8 \
  --max-pending 200 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 0.0 \
  --max-total-execution-seconds 30.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-29T231157.338216Z \
  --approved-record-sha256 4e372dbcab6a5b632d2f4854efe507f9704b3a4c589954fa2d5510050371ba3e \
  --submit
```
