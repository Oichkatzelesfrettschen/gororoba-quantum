# Unapproved QPU case: measurement-sequence-diagnostic

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-26T025240.156256Z`.
- [record.json](record.json) SHA-256: `382063c2e0b888525b9f7bb7d940d056e55dfb6b2dca5143c172b9f598ef822e`.
- [isa.qpy](isa.qpy) SHA-256: `80353d6df7f1b83ceaa2c76fd7bf9c91d6414d939fcf795d719ab8e6a035c03f`.
- Experiment source digest: `e7a8829f997050ed3fe81722f0b5b1249d6ed5e9979fa41b778f5c9363624485`.
- Source commit: `ed3e3a9dbce3938ca7e6eeca07be0176dddf8835`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.6.0 |
| qiskit-aer | 0.17.2 |
| qiskit-ibm-runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The measurement-sequence-diagnostic family measures, on 38 qubits of ibm_kingston at the backend's default repetition delay, the scatter of the pinching analysis's gate model: how far the readout-corrected P0 of sixteen composite RX(THETA / 16) rotations (THETA = 8 pi / 9, thirty-two sx pulses, no measurement and no idle) lies from the analysis's Bloch-iteration prediction, qubit by qubit. The main measurement-sequence case bounds what a gate error could do to its measure arm by that residual, and a model that overpredicts one class of gate error and underpredicts another can leave the unitary residual near zero while the measure arm moves, so the main analysis needs the scatter across qubits as a floor (docs/design/measurement-sequence-pinching.md, Source of the model-scatter floor). No retained Heron run holds single-qubit sx sequences with a known ideal outcome, and a floor that is assumed instead of measured is a guessed hardware value. A noise simulation prices the Target's reported errors and returns the model's own prediction with counting noise; it cannot show how the device departs from that Target-built model, which is the quantity measured here.

Every qubit runs the four signed unitary members in the order +, -, -, +, a zero-pulse member (ro0) and the x member at idle 0 (ro1), all with the 2 us pre-readout delay, with circuits identical to the main family's. All members are static, so each row fuses across every named qubit into one PUB and the run holds six PUBs. The named qubits are the main family's eight and further qubits chosen from the live calibration alone by the preregistered rule: eligible: not excluded by the live Target, readout error <= 0.01, sx error <= 0.001, T1 and T2 >= 20 us, and coupled to no main qubit; scan the eligible qubits in ascending readout error (ties by index) and keep a qubit coupled to no kept qubit, until 30 are kept. The layout is pinned on the command line, and the planner refuses a layout with a coupled pair, an excluded qubit or a repeated qubit. The residual enters the floor through the preregistered rule: the floor is the larger of the root-mean-square, over informative diagnostic qubits, of the readout-corrected unitary N = 16 residual (observed minus the analysis model) taken over all of them and over the main qubits alone; statistical noise stays in. The run also reports each qubit's residual against its T2, which tests the drive-dephasing lead seen on IQM Garnet. The result is a scatter-floor.json that the main analysis binds by digest; until it exists the main analysis withholds. A measured floor above about 0.02 raises the smallest per-step transition rate the main case can detect from about 0.003 (floor 0.01) to 0.0049 (0.02) and 0.0097 (0.04), at the main design's shots; the main design stays admissible at every floor, and the owner decides at the floor's value whether the main run is worth its quantum time.

The record binds the IBM Cloud instance of the backup account (instance sha256 prefix f59f9992321c): run the dry run and the submission with `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` in the environment, which is the account whose 600 s rolling quota the run charges.

Two precision contracts per qubit split the family-wise alpha evenly and admit the design: the unitary P0 pooled over the four signed members and ro1's P1, each at half-width 0.03. They price resolution, not an effect.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| msq_unitary_n16_pa_q91 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q91 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q91 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q91 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q91 | `[1.0, 0.0]` |
| msq_t1_d0_q91 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q118 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q118 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q118 | `[1.0, 0.0]` |
| msq_t1_d0_q118 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q95 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q95 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q95 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q95 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q95 | `[1.0, 0.0]` |
| msq_t1_d0_q95 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q61 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q61 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q61 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q61 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q61 | `[1.0, 0.0]` |
| msq_t1_d0_q61 | `[0.0, 1.0]` |
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
| msq_unitary_n16_pa_q59 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q59 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q59 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q59 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q59 | `[1.0, 0.0]` |
| msq_t1_d0_q59 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q89 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q89 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q89 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q89 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q89 | `[1.0, 0.0]` |
| msq_t1_d0_q89 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q10 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q10 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q10 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q10 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q10 | `[1.0, 0.0]` |
| msq_t1_d0_q10 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q15 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q15 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q15 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q15 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q15 | `[1.0, 0.0]` |
| msq_t1_d0_q15 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q48 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q48 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q48 | `[1.0, 0.0]` |
| msq_t1_d0_q48 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q64 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q64 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q64 | `[1.0, 0.0]` |
| msq_t1_d0_q64 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q117 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q117 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q117 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q117 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q117 | `[1.0, 0.0]` |
| msq_t1_d0_q117 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q40 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q40 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q40 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q40 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q40 | `[1.0, 0.0]` |
| msq_t1_d0_q40 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q126 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q126 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q126 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q126 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q126 | `[1.0, 0.0]` |
| msq_t1_d0_q126 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q154 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q154 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q154 | `[1.0, 0.0]` |
| msq_t1_d0_q154 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q3 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q3 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q3 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q3 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q3 | `[1.0, 0.0]` |
| msq_t1_d0_q3 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q67 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q67 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q67 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q67 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q67 | `[1.0, 0.0]` |
| msq_t1_d0_q67 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q134 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q134 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q134 | `[1.0, 0.0]` |
| msq_t1_d0_q134 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q23 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q23 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q23 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q23 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q23 | `[1.0, 0.0]` |
| msq_t1_d0_q23 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q45 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q45 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q45 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q45 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q45 | `[1.0, 0.0]` |
| msq_t1_d0_q45 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q128 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q128 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q128 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q128 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q128 | `[1.0, 0.0]` |
| msq_t1_d0_q128 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q25 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q25 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q25 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q25 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q25 | `[1.0, 0.0]` |
| msq_t1_d0_q25 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q144 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q144 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q144 | `[1.0, 0.0]` |
| msq_t1_d0_q144 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q71 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q71 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q71 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q71 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q71 | `[1.0, 0.0]` |
| msq_t1_d0_q71 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q20 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q20 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q20 | `[1.0, 0.0]` |
| msq_t1_d0_q20 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q50 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q50 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q50 | `[1.0, 0.0]` |
| msq_t1_d0_q50 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q79 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q79 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q79 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q79 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q79 | `[1.0, 0.0]` |
| msq_t1_d0_q79 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q110 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q110 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q110 | `[1.0, 0.0]` |
| msq_t1_d0_q110 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q123 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q123 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q123 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q123 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q123 | `[1.0, 0.0]` |
| msq_t1_d0_q123 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q80 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q80 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q80 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q80 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q80 | `[1.0, 0.0]` |
| msq_t1_d0_q80 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q13 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q13 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q13 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q13 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q13 | `[1.0, 0.0]` |
| msq_t1_d0_q13 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q38 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q38 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q38 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q38 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q38 | `[1.0, 0.0]` |
| msq_t1_d0_q38 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q108 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q108 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q108 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q108 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q108 | `[1.0, 0.0]` |
| msq_t1_d0_q108 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q5 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q5 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q5 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q5 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q5 | `[1.0, 0.0]` |
| msq_t1_d0_q5 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q30 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q30 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q30 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q30 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q30 | `[1.0, 0.0]` |
| msq_t1_d0_q30 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q17 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q17 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q17 | `[1.0, 0.0]` |
| msq_t1_d0_q17 | `[0.0, 1.0]` |
| msq_unitary_n16_pa_q141 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_ma_q141 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_mb_q141 | `[0.030153689607, 0.969846310393]` |
| msq_unitary_n16_pb_q141 | `[0.030153689607, 0.969846310393]` |
| msq_ro0_q141 | `[1.0, 0.0]` |
| msq_t1_d0_q141 | `[0.0, 1.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| msqd_static_q91 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[91]` | `[[91]]` |
| msqd_static_q118 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[118]` | `[[118]]` |
| msqd_static_q95 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[95]` | `[[95]]` |
| msqd_static_q61 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[61]` | `[[61]]` |
| msqd_static_q147 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[147]` | `[[147]]` |
| msqd_static_q151 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[151]` | `[[151]]` |
| msqd_static_q59 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[59]` | `[[59]]` |
| msqd_static_q89 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[89]` | `[[89]]` |
| msqd_static_q10 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[10]` | `[[10]]` |
| msqd_static_q15 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[15]` | `[[15]]` |
| msqd_static_q48 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[48]` | `[[48]]` |
| msqd_static_q64 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[64]` | `[[64]]` |
| msqd_static_q117 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[117]` | `[[117]]` |
| msqd_static_q40 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[40]` | `[[40]]` |
| msqd_static_q126 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[126]` | `[[126]]` |
| msqd_static_q154 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[154]` | `[[154]]` |
| msqd_static_q3 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[3]` | `[[3]]` |
| msqd_static_q67 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[67]` | `[[67]]` |
| msqd_static_q134 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[134]` | `[[134]]` |
| msqd_static_q23 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[23]` | `[[23]]` |
| msqd_static_q45 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[45]` | `[[45]]` |
| msqd_static_q128 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[128]` | `[[128]]` |
| msqd_static_q25 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[25]` | `[[25]]` |
| msqd_static_q144 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[144]` | `[[144]]` |
| msqd_static_q71 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[71]` | `[[71]]` |
| msqd_static_q20 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[20]` | `[[20]]` |
| msqd_static_q50 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[50]` | `[[50]]` |
| msqd_static_q79 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[79]` | `[[79]]` |
| msqd_static_q110 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[110]` | `[[110]]` |
| msqd_static_q123 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[123]` | `[[123]]` |
| msqd_static_q80 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[80]` | `[[80]]` |
| msqd_static_q13 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[13]` | `[[13]]` |
| msqd_static_q38 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[38]` | `[[38]]` |
| msqd_static_q108 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[108]` | `[[108]]` |
| msqd_static_q5 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[5]` | `[[5]]` |
| msqd_static_q30 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[30]` | `[[30]]` |
| msqd_static_q17 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[17]` | `[[17]]` |
| msqd_static_q141 | ibm_kingston | 2026-10-25T19:36:09-07:00 | 20261010 | `[141]` | `[[141]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    91,
    118,
    95,
    61,
    147,
    151,
    59,
    89,
    10,
    15,
    48,
    64,
    117,
    40,
    126,
    154,
    3,
    67,
    134,
    23,
    45,
    128,
    25,
    144,
    71,
    20,
    50,
    79,
    110,
    123,
    80,
    13,
    38,
    108,
    5,
    30,
    17,
    141
  ],
  "prereadout_delay_dt": {
    "91": 500,
    "118": 500,
    "95": 500,
    "61": 500,
    "147": 500,
    "151": 500,
    "59": 500,
    "89": 500,
    "10": 500,
    "15": 500,
    "48": 500,
    "64": 500,
    "117": 500,
    "40": 500,
    "126": 500,
    "154": 500,
    "3": 500,
    "67": 500,
    "134": 500,
    "23": 500,
    "45": 500,
    "128": 500,
    "25": 500,
    "144": 500,
    "71": 500,
    "20": 500,
    "50": 500,
    "79": 500,
    "110": 500,
    "123": 500,
    "80": 500,
    "13": 500,
    "38": 500,
    "108": 500,
    "5": 500,
    "30": 500,
    "17": 500,
    "141": 500
  },
  "t1_delays_dt": [
    0
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "msqd_static_q91": [
      {
        "91": 91
      }
    ],
    "msqd_static_q118": [
      {
        "118": 118
      }
    ],
    "msqd_static_q95": [
      {
        "95": 95
      }
    ],
    "msqd_static_q61": [
      {
        "61": 61
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
    "msqd_static_q59": [
      {
        "59": 59
      }
    ],
    "msqd_static_q89": [
      {
        "89": 89
      }
    ],
    "msqd_static_q10": [
      {
        "10": 10
      }
    ],
    "msqd_static_q15": [
      {
        "15": 15
      }
    ],
    "msqd_static_q48": [
      {
        "48": 48
      }
    ],
    "msqd_static_q64": [
      {
        "64": 64
      }
    ],
    "msqd_static_q117": [
      {
        "117": 117
      }
    ],
    "msqd_static_q40": [
      {
        "40": 40
      }
    ],
    "msqd_static_q126": [
      {
        "126": 126
      }
    ],
    "msqd_static_q154": [
      {
        "154": 154
      }
    ],
    "msqd_static_q3": [
      {
        "3": 3
      }
    ],
    "msqd_static_q67": [
      {
        "67": 67
      }
    ],
    "msqd_static_q134": [
      {
        "134": 134
      }
    ],
    "msqd_static_q23": [
      {
        "23": 23
      }
    ],
    "msqd_static_q45": [
      {
        "45": 45
      }
    ],
    "msqd_static_q128": [
      {
        "128": 128
      }
    ],
    "msqd_static_q25": [
      {
        "25": 25
      }
    ],
    "msqd_static_q144": [
      {
        "144": 144
      }
    ],
    "msqd_static_q71": [
      {
        "71": 71
      }
    ],
    "msqd_static_q20": [
      {
        "20": 20
      }
    ],
    "msqd_static_q50": [
      {
        "50": 50
      }
    ],
    "msqd_static_q79": [
      {
        "79": 79
      }
    ],
    "msqd_static_q110": [
      {
        "110": 110
      }
    ],
    "msqd_static_q123": [
      {
        "123": 123
      }
    ],
    "msqd_static_q80": [
      {
        "80": 80
      }
    ],
    "msqd_static_q13": [
      {
        "13": 13
      }
    ],
    "msqd_static_q38": [
      {
        "38": 38
      }
    ],
    "msqd_static_q108": [
      {
        "108": 108
      }
    ],
    "msqd_static_q5": [
      {
        "5": 5
      }
    ],
    "msqd_static_q30": [
      {
        "30": 30
      }
    ],
    "msqd_static_q17": [
      {
        "17": 17
      }
    ],
    "msqd_static_q141": [
      {
        "141": 141
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### msq_p0_unitary_n16_q91

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q91`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q91`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q91`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q91`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0522766113281; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0269066179812.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q91

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q91`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984130859375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.958760866028.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q118

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q118`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q118`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0514526367188; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0260826433719.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q118

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q118`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983276367188; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957906373841.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q95

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q95`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q95`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q95`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q95`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0499267578125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0245567644656.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q95

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q95`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984619140625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959249147278.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q61

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q61`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q61`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q61`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q61`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0531311035156; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0277611101687.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q61

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q61`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98095703125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.955587037903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q147

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q147`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q147`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0741577148438; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0487877214969.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q147

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q147`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98095703125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.955587037903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q151

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q151`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q151`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.05029296875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0249229754031.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q151

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q151`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98388671875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.958516725403.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q59

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q59`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q59`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q59`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q59`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0505676269531; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0251976336062.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q59

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q59`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982299804688; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.956929811341.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q89

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q89`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q89`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q89`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q89`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0521850585938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0268150652469.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q89

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q89`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982666015625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957296022278.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q10

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q10`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q10`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q10`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q10`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.056884765625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0315147722781.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q10

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q10`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.988037109375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.962667116028.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q15

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q15`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q15`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q15`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q15`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0475769042969; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.02220691095.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q15

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q15`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986206054688; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.960836061341.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q48

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q48`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q48`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0582275390625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0328575457156.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q48

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q48`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984741210938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959371217591.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q64

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q64`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q64`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.05517578125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0298057879031.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q64

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q64`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983276367188; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957906373841.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q117

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q117`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q117`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q117`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q117`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0520935058594; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0267235125125.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q117

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q117`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984008789062; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.958638795716.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q40

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q40`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q40`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q40`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q40`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0520935058594; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0267235125125.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q40

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q40`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984497070312; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959127076966.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q126

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q126`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q126`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q126`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q126`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0560302734375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0306602800906.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q126

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.980834960938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.955464967591.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q154

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q154`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q154`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0502624511719; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.024892457825.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q154

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q154`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98583984375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.960469850403.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q3

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q3`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q3`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q3`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q3`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0598449707031; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0344749773562.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q3

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q3`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982421875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957051881653.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q67

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q67`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q67`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q67`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q67`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.05029296875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0249229754031.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q67

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q67`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98486328125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959493287903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q134

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q134`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q134`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0490112304688; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0236412371219.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q134

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q134`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.9853515625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959981569153.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q23

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q23`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q23`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q23`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q23`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0494995117188; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0241295183719.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q23

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q23`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.9853515625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959981569153.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q45

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q45`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q45`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q45`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q45`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0608825683594; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0355125750125.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q45

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q45`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.98095703125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.955587037903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q128

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q128`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q128`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q128`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q128`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0547180175781; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0293480242312.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q128

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q128`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.980102539062; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.954732545716.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q25

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q25`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q25`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q25`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q25`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0533142089844; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0279442156375.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q25

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q25`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.986328125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.960958131653.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q144

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q144`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q144`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0492858886719; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.023915895325.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q144

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q144`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.985107421875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959737428528.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q71

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q71`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q71`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q71`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q71`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0506286621094; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0252586687625.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q71

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q71`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984130859375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.958760866028.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q20

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q20`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q20`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0564880371094; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0311180437625.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q20

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q20`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.9853515625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959981569153.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q50

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q50`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q50`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0512084960938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0258385027469.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q50

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q50`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.981811523438; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.956441530091.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q79

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q79`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q79`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q79`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q79`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0498962402344; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0245262468875.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q79

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q79`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.984985351562; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959615358216.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q110

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q110`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q110`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0545959472656; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0292259539187.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q110

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q110`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982666015625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957296022278.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q123

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q123`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q123`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q123`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q123`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0599060058594; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0345360125125.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q123

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q123`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.985595703125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.960225709778.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q80

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q80`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q80`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q80`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q80`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0513305664062; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0259605730594.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q80

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q80`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.983154296875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.957784303528.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q13

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q13`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q13`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q13`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q13`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.055908203125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0305382097781.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q13

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q13`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.985107421875; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.959737428528.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q38

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q38`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q38`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q38`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q38`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0569152832031; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0315452898562.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q38

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q38`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.977172851562; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.951802858216.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q108

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q108`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q108`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q108`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q108`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0647277832031; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0393577898562.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q108

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q108`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.976928710938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.951558717591.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q5

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q5`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q5`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q5`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q5`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0689697265625; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0435997332156.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q5

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q5`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.97314453125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.947774537903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q30

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q30`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q30`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q30`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q30`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0553894042969; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.03001941095.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q30

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q30`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.980834960938; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.955464967591.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q17

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q17`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q17`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0525512695312; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.0271812761844.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q17

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q17`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.982177734375; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.956807741028.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

### msq_p0_unitary_n16_q141

Score terms (each member averages its recorded replicas):

- `msq_unitary_n16_pa_q141`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_ma_q141`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_mb_q141`: sign +1, labeled score vector `[0.25, 0.0]`.
- `msq_unitary_n16_pb_q141`: sign +1, labeled score vector `[0.25, 0.0]`.

The noise model predicts 0.0785827636719; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.053212770325.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0239601964289; requested precision is 0.03.

### msq_p1_t1_d0_q141

Score terms (each member averages its recorded replicas):

- `msq_t1_d0_q141`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.95751953125; the simultaneous finite-simulation allowance is +/-0.0253699933469. The lower modeled value is 0.932149537903.

At alpha 0.000657894736842, the two-sided confidence half-width is 0.0221241569324; requested precision is 0.03.

The search-wide simulation error probability is 0.01 across 190 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.798673214296. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 6 | 49152 | 14.827271936 | 20 |

The cost model predicts 14.827271936 seconds. The per-job service ceilings sum to 20 seconds against an invocation cap of 20 seconds. The global reserve is 60 seconds; the saved quota reports 450 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 8192 | 5.204e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_02 | 8192 | 5.204e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_03 | 8192 | 5.204e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_04 | 8192 | 5.204e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_05 | 8192 | 4.18e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_06 | 8192 | 4.212e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/1` adds 2.3 seconds of modeled overhead.

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
  --simulation-threads 3 \
  --simulation-memory-mb 2048 \
  --optimize \
  --layout 91,118,95,61,147,151,59,89,10,15,48,64,117,40,126,154,3,67,134,23,45,128,25,144,71,20,50,79,110,123,80,13,38,108,5,30,17,141 \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 20 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 8192 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 20.0 \
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
  --simulation-threads 3 \
  --simulation-memory-mb 2048 \
  --optimize \
  --layout 91,118,95,61,147,151,59,89,10,15,48,64,117,40,126,154,3,67,134,23,45,128,25,144,71,20,50,79,110,123,80,13,38,108,5,30,17,141 \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 20 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 8192 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 20.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-26T025240.156256Z \
  --approved-record-sha256 382063c2e0b888525b9f7bb7d940d056e55dfb6b2dca5143c172b9f598ef822e \
  --submit
```
