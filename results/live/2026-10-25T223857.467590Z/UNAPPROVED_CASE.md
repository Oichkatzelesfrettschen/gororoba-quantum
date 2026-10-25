# Unapproved QPU case: latency-recovery

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-16384` at 16384 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-25T223857.467590Z`.
- [record.json](record.json) SHA-256: `5a82470b67ba357fd46542aaa82d4699334518edb709f3ee7408a43139edda96`.
- [isa.qpy](isa.qpy) SHA-256: `42212bc7551c4b149974dae2f17e33b728119367ff2a34bc53db7b510f2af0ab`.
- Experiment source digest: `4708338a25baa394f6292a782267427bfd5c7a75715d1c972e219b19a14ad537`.
- Source commit: `ea1d0e4aba2ba228ea2585a7f6377d263311fe73`; sources_modified=`true`.
- Simulator seed: `44016`; the source digest binds the simulator implementation.

The source flag records changes anywhere in the experiment directory, including documentation and unmanifested files. Reproduction requires verification of every declared source against the experiment digest; the broad flag alone does not establish which source bytes differ from the recorded commit. A separate source-closure audit can establish that comparison without altering the retained record.

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

The latency-recovery family measures on ibm_kingston how much entanglement fidelity a feed-forward bit-flip recovery loses to the controller's latency, against a Pauli-frame correction that applies the same syndrome in post-processing. A reference qubit holds a Bell pair with a three-qubit repetition code d0 d1 d2; two ancillas read the syndrome into a 2-bit register, and one conditional X on d0 corrects an X error on d0 when the syndrome is 0b01. Barriers bracket the two ancilla measurements in every member, so the data and reference qubits idle through the readout in every arm. The calibration noise model applies a conditional instantly and dephases an idle qubit at the calibrated T1 and T2 only, so it omits the controller window and any readout-induced dephasing; only the device measures them.

The arms are ff_0 (conditional correction), ff_w (an added idle of W = 2500 dt on the reference and data qubits before it), frame_0, frame_l and frame_lw (a Pauli frame after idles of 0, L = 215 dt and L + W), and ff_0_unencoded (the same circuit without the code). The frame arms flip the d0 outcome of the Z and Y bases when the syndrome is 0b01, and the no-correction null reads the same frame members without the flip. The 34 members are dynamic and run in one job. Readout correction is skipped, so each fidelity carries the same readout bias and arm differences cancel it to first order.

Seven contracts on differences of F = (1 + XX - YY + ZZ)/4 split the family alpha equally. recovery (ff_0 minus the null above 0.5) and code_property (ff_0 minus ff_0_unencoded above 0.25) are one-sided. The calibration model applies the conditional instantly and predicts no latency cost, so latency_cost (frame_0 minus ff_0), latency_is_idle (frame_l minus ff_0), the window costs window_cost_ff (ff_0 minus ff_w) and window_cost_frame (frame_l minus frame_lw), and window_slope (their difference) are two-sided precision endpoints of half-width 0.05, except 0.1 for window_slope; they price resolution, not an effect. The analysis then reads the retained intervals: latency_cost and each window cost resolve where the lower bound exceeds 0, and latency_is_idle and window_slope hold where their intervals lie inside +-0.01, a margin the Hoeffding radii at these shot tiers do not reach, so an unresolved equivalence remains an allowed outcome. The controller overlaps a requested delay with the broadcast, so the analysis reads each arm's executed exposure from the returned scheduler_timing (scripts/latency_recovery_exposure.py): a window cost over its executed increment is a finite-window fidelity-loss slope, and -ln(F(W)/F(0)) over that increment equals an exponential law's rate only if the decay is exponential. decay_not_phase is descriptive: it compares the coherence C and phase phi of ff_0 and frame_0 from the XY and YX members. A lower bound of latency_is_idle (frame_l minus ff_0) above 0 names a feed-forward cost beyond the idle itself, the device-specific part; an interval that includes 0 leaves that cost unresolved.

The run measures the fidelity cost of whatever the controller executes, not the latency's jitter. A bit-flip code protects no phase, so the run measures the idle cost of coherence, the quantity the latency-constrained recovery model needs, and says nothing about a code that also corrects phase. One layout and one calibration give one device's number.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| lr_ff_0_err_XX | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_ff_0_err_YY | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_ff_0_err_ZZ | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_ff_0_err_XY | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_ff_0_err_YX | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_ff_w_err_XX | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_ff_w_err_YY | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_ff_w_err_ZZ | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_ff_w_err_XY | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_ff_w_err_YX | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_0_err_XX | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_0_err_YY | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_0_err_ZZ | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_frame_0_err_XY | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_0_err_YX | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_l_err_XX | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_l_err_YY | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_l_err_ZZ | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_frame_l_err_XY | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_l_err_YX | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_lw_err_XX | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_lw_err_YY | `[0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0]` |
| lr_frame_lw_err_ZZ | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_frame_lw_err_XY | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_frame_lw_err_YX | `[0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0]` |
| lr_ff_0_ok_XX | `[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0]` |
| lr_ff_0_ok_YY | `[0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_ff_0_ok_ZZ | `[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0]` |
| lr_frame_0_ok_XX | `[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0]` |
| lr_frame_0_ok_YY | `[0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| lr_frame_0_ok_ZZ | `[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0]` |
| lr_ff_0_unencoded_err_XX | `[0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0]` |
| lr_ff_0_unencoded_err_YY | `[0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0, 0.125, 0.125, 0.0, 0.0]` |
| lr_ff_0_unencoded_err_ZZ | `[0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| latency_recovery | ibm_kingston | 2026-10-25T15:17:22-07:00 | 22269 | `[150, 151, 138, 152, 149, 153]` | `[[106, 105, 104, 117, 107, 125]]` |

Calibration-bound family and replica mapping:

```json
{
  "latency_dt": 215,
  "window_dt": 2500,
  "requested_latency_dt": 215,
  "requested_window_dt": 2500,
  "granularity_dt": 1,
  "dt_seconds": 4e-09,
  "replica_cap": 1,
  "group_replica_mappings": {
    "latency_recovery": [
      {
        "138": 104,
        "149": 107,
        "150": 106,
        "151": 105,
        "152": 117,
        "153": 125
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### lr_recovery

Score terms (each member averages its recorded replicas):

- `lr_ff_0_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign +1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_0_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_0_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_frame_0_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.

The noise model predicts 0.891098022461; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is 0.853546549.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.543004465635 (null 0.5 plus one-sided radius 0.0430044656348). The admitted alternative effect is 0.353546549, with conditional target power 0.8 and lower-tail radius 0.0305641417567. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### lr_code_property

Score terms (each member averages its recorded replicas):

- `lr_ff_0_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign +1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_unencoded_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_unencoded_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_unencoded_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.

The noise model predicts 0.657348632812; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is 0.619797159351.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.293004465635 (null 0.25 plus one-sided radius 0.0430044656348). The admitted alternative effect is 0.369797159351, with conditional target power 0.8 and lower-tail radius 0.0305641417567. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### lr_latency_cost

Score terms (each member averages its recorded replicas):

- `lr_frame_0_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_0_err_YY`: sign +1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_0_err_ZZ`: sign +1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.
- `lr_ff_0_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.

The noise model predicts 0.00254821777344; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is -0.0350032556877.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is 0.05.

### lr_latency_is_idle

Score terms (each member averages its recorded replicas):

- `lr_frame_l_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_l_err_YY`: sign +1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_l_err_ZZ`: sign +1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.
- `lr_ff_0_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.

The noise model predicts -0.00224304199219; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is -0.0397945154534.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is 0.05.

### lr_window_cost_ff

Score terms (each member averages its recorded replicas):

- `lr_ff_0_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign +1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_w_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_w_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_w_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.

The noise model predicts 0.0793914794922; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is 0.041840006031.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is 0.05.

### lr_window_cost_frame

Score terms (each member averages its recorded replicas):

- `lr_frame_l_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_l_err_YY`: sign +1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_l_err_ZZ`: sign +1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.
- `lr_frame_lw_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_lw_err_YY`: sign -1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_lw_err_ZZ`: sign -1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.

The noise model predicts 0.0776672363281; the simultaneous finite-simulation allowance is +/-0.0375514734612. The lower modeled value is 0.040115762867.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0451637312857; requested precision is 0.05.

### lr_window_slope

Score terms (each member averages its recorded replicas):

- `lr_ff_0_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_0_err_YY`: sign +1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_0_err_ZZ`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_w_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_ff_w_err_YY`: sign -1, labeled score vector `[-0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25]`.
- `lr_ff_w_err_ZZ`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_l_err_XX`: sign -1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_l_err_YY`: sign -1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_l_err_ZZ`: sign -1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.
- `lr_frame_lw_err_XX`: sign +1, labeled score vector `[0.25, 0.25, 0.25, 0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, -0.25, 0.25, 0.25, 0.25, 0.25]`.
- `lr_frame_lw_err_YY`: sign +1, labeled score vector `[-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25, 0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25]`.
- `lr_frame_lw_err_ZZ`: sign +1, labeled score vector `[0.25, -0.25, 0.25, 0.25, -0.25, 0.25, -0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25, 0.25]`.

The noise model predicts 0.00172424316406; the simultaneous finite-simulation allowance is +/-0.0751029469223. The lower modeled value is -0.0733787037583.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0944487412888; requested precision is 0.1.

The search-wide simulation error probability is 0.01 across 144 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 34 | 557056 | 40.442148608 | 90 |

The cost model predicts 40.442148608 seconds. The per-job service ceilings sum to 90 seconds against an invocation cap of 90 seconds. The global reserve is 0 seconds; the saved quota reports 517 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_02 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_03 | 16384 | 5.896e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_04 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_05 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_06 | 16384 | 1.5928e-05 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_07 | 16384 | 1.5928e-05 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_08 | 16384 | 1.5896e-05 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_09 | 16384 | 1.5928e-05 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_10 | 16384 | 1.5928e-05 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_11 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_12 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_13 | 16384 | 5.864e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_14 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_15 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_16 | 16384 | 6.756e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_17 | 16384 | 6.756e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_18 | 16384 | 6.724e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_19 | 16384 | 6.756e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_20 | 16384 | 6.756e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_21 | 16384 | 1.6756e-05 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_22 | 16384 | 1.6756e-05 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_23 | 16384 | 1.6724e-05 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_24 | 16384 | 1.6756e-05 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_25 | 16384 | 1.6756e-05 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_26 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_27 | 16384 | 5.928e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_28 | 16384 | 5.896e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_29 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_30 | 16384 | 5.896e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_31 | 16384 | 5.864e-06 | 5e-05 | 0 | 0 |
| ibm_kingston_dynamic_pub_32 | 16384 | 5.492e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_33 | 16384 | 5.492e-06 | 5e-05 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_34 | 16384 | 5.46e-06 | 5e-05 | 0 | 2e-05 |

Job `ibm_kingston/dynamic/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family latency-recovery \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --backends ibm_kingston \
  --shots 16384 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 90 \
  --rep-delay 5e-05 \
  --seed-transpiler 'qrng:docs/evidence/anu_qrng/draw-2026-10-25T223842Z.json#0' \
  --seed-simulator 'qrng:docs/evidence/anu_qrng/draw-2026-10-25T223842Z.json#1' \
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
  --max-total-execution-seconds 90.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family latency-recovery \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --backends ibm_kingston \
  --shots 16384 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 90 \
  --rep-delay 5e-05 \
  --seed-transpiler 'qrng:docs/evidence/anu_qrng/draw-2026-10-25T223842Z.json#0' \
  --seed-simulator 'qrng:docs/evidence/anu_qrng/draw-2026-10-25T223842Z.json#1' \
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
  --max-total-execution-seconds 90.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-25T223857.467590Z \
  --approved-record-sha256 5a82470b67ba357fd46542aaa82d4699334518edb709f3ee7408a43139edda96 \
  --submit
```
