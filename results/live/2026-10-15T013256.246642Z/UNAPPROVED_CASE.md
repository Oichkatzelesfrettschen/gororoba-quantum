# Unapproved QPU case: coherence-window

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-2048-per-pub` with per-PUB shot allocation (used tiers: 2048; 2 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-15T013256.246642Z`.
- [record.json](record.json) SHA-256: `e0f9a714718630091fca5d6353df1497c6733e332d78a09de68aae945cd562be`.
- [isa.qpy](isa.qpy) SHA-256: `ef37df43ebacb574274d5313abc0b9ca15b75801944a5f3c7e5caedc41d21341`.
- Experiment source digest: `8d7979af7d277317c272e4bf5f5ae26302397bb15dac4c6e8a9f84d881042b98`.
- Source commit: `71decdf4b3b9ec6086e39370c0eec1664e3a77d1`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.5.2 |
| qiskit-aer | 0.17.2 |
| qiskit-ibm-runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The coherence-window family measures, on the initial layout control 92, work_a 98, spectator 91, work_b 90, neighbor_a 111, neighbor_b 89 on ibm_marrakesh, the best calibrated patch embedding the planner found on the eligible backends, the work coherence the first N=21 orbit round leaves between work_a and work_b, signed by the control's first bit b0. In each branch the work pair holds |10> + (-1)^b0 e^{i phi} |01>, so rho_{01,10} = <01|rho|10> changes sign with b0, its branch-unsigned average is zero on an ideal device, and the terminal four-outcome orbit law cannot see it. Each shot is weighted by (-1)^b0, and C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 is the branch-signed rho_{01,10}, with arg C = phi and |C| = 1/2 ideally; a Z rotation by delta on work_b turns C by +delta, on work_a by -delta.

Routing moves the logical work qubits during the prefix, so the compiled circuits read b0 from qubit 92, read_a from qubit 90, read_b from qubit 98, sector from qubit 91; no two-qubit gate follows the prefix, so per-qubit attribution of a window phase uses this executed map, not the initial roles.

Three contexts follow the same round-1 prefix: immediate readout; a matched idle of 1351 dt (the control's measure plus reset) with b0 read after it; and a mid-circuit measure and reset of the control before the work readout. A coherent window phase rotates C between contexts, dephasing or amplitude damping shrinks |C| without rotating it, and first-bit assignment error scales C by (1 - 2 epsilon), so rotation and shrinkage separate the explanations the terminal law left degenerate. The matched idle reads b0 after the window, so control relaxation there adds to epsilon and scales that context's C without rotating it. The branch-unsigned average is a negative control, the ZZ setting and the spectator readout give the work populations and the one-hot sector.

One idle length fixes a window phase only modulo 2 pi: a static detuning above 92.5 kHz aliases to a smaller rotation of the opposite sign, so a measured rotation converts to a frequency only below that bound. Readout assignment error scales C only for a symmetric, state-independent channel; correlated or asymmetric assignment error acts on raw counts whose pre-measurement state differs between contexts and Pauli settings, so it can move the modulus or the phase of C and remains a residual in every context. b0 and the work pair share one readout layer in the immediate and matched-idle contexts, while measure_reset reads b0 in its own mid-circuit layer. A control-work ZZ phase lam while the control holds b0 shrinks C by cos(lam) without rotating it, the same signature as dephasing; after the control's reset it rotates C instead, so measure_reset mixes both forms and a matched-idle shrink alone does not separate ZZ from dephasing. The calibration noise model omits measurement-induced dephasing of the work pair, so it prices the measure-and-reset contracts optimistically; a smaller hardware |C| there widens the reported intervals and remains an allowed outcome.

The immediate and matched-idle contexts run in the static job and the measure-and-reset context in the dynamic job; the idle-versus-immediate comparison shares one job, while drift between the jobs enters the measure-and-reset comparison as a rotation. The analysis reads each PUB's executed work exposure from the returned schedule and reports both jobs' execution times, so that comparison bounds a measurement-induced phase only together with them.

Five two-sided precision contracts admit the design, each with half-width 0.33 on 4 C: Re C in the immediate context and the Re C and Im C differences between adjacent contexts. That half-width resolves a rotation near 0.17 rad at |C| = 1/2 and 0.19 rad at |C| = 0.43. They price resolution, not an effect; an unresolved rotation or a context-independent C remains an allowed outcome, and a phase is reported only where |C| supports it.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| coherence_immediate_xx | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_immediate_xy | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_immediate_yx | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_immediate_yy | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_immediate_zz | `[0.0, 0.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_matched_idle_xx | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_matched_idle_xy | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_matched_idle_yx | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_matched_idle_yy | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_matched_idle_zz | `[0.0, 0.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_measure_reset_xx | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_measure_reset_xy | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_measure_reset_yx | `[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_measure_reset_yy | `[0.25, 0.0, 0.0, 0.25, 0.0, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| coherence_measure_reset_zz | `[0.0, 0.0, 0.25, 0.25, 0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| coherence_static | ibm_marrakesh | 2026-10-14T17:59:39-07:00 | 20261010 | `[92, 98, 91, 90, 111, 89]` | `[[92, 98, 91, 90, 111, 89]]` |
| coherence_dynamic | ibm_marrakesh | 2026-10-14T17:59:39-07:00 | 20261010 | `[92, 98, 91, 90, 111, 89]` | `[[92, 98, 91, 90, 111, 89]]` |

Calibration-bound family and replica mapping:

```json
{
  "window_dt": 1351,
  "readout_qubits": {
    "b0": 92,
    "read_a": 90,
    "read_b": 98,
    "sector": 91
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "coherence_static": [
      {
        "89": 89,
        "90": 90,
        "91": 91,
        "92": 92,
        "98": 98,
        "111": 111
      }
    ],
    "coherence_dynamic": [
      {
        "89": 89,
        "90": 90,
        "91": 91,
        "92": 92,
        "98": 98,
        "111": 111
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### re_immediate

Score terms (each member averages its recorded replicas):

- `coherence_immediate_xx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_yy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 1.72875213623; the simultaneous finite-simulation allowance is +/-0.0158081928156. The lower modeled value is 1.71294394341.

At alpha 0.01, the two-sided confidence half-width is 0.152984176918; requested precision is 0.33.

### re_matched_idle_minus_immediate

Score terms (each member averages its recorded replicas):

- `coherence_matched_idle_xx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_xx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_yy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts -0.27995300293; the simultaneous finite-simulation allowance is +/-0.0316163856313. The lower modeled value is -0.311569388561.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### im_matched_idle_minus_immediate

Score terms (each member averages its recorded replicas):

- `coherence_matched_idle_xy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_xy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_yx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 0.00757598876953; the simultaneous finite-simulation allowance is +/-0.0316163856313. The lower modeled value is -0.0240403968618.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### re_measure_reset_minus_matched_idle

Score terms (each member averages its recorded replicas):

- `coherence_measure_reset_xx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_measure_reset_yy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_xx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 0.282814025879; the simultaneous finite-simulation allowance is +/-0.0316163856313. The lower modeled value is 0.251197640248.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### im_measure_reset_minus_matched_idle

Score terms (each member averages its recorded replicas):

- `coherence_measure_reset_xy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_measure_reset_yx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_xy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts -0.000373840332031; the simultaneous finite-simulation allowance is +/-0.0316163856313. The lower modeled value is -0.0319902259633.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

The search-wide simulation error probability is 0.01 across 18 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.979341518272. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_marrakesh/dynamic/1 | 5 | 10240 | 4.970190592 | 9 |
| ibm_marrakesh/static/1 | 10 | 20480 | 7.585044224 | 9 |

The cost model predicts 12.555234816 seconds. The per-job service ceilings sum to 18 seconds against an invocation cap of 18 seconds. The global reserve is 60 seconds; the saved quota reports 390 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_marrakesh_dynamic_pub_01 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_dynamic_pub_02 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_dynamic_pub_03 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_dynamic_pub_04 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_dynamic_pub_05 | 2048 | 1.0732e-05 | 0.00025 | 0 | 0 |

Job `ibm_marrakesh/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_marrakesh_static_pub_01 | 2048 | 5.364e-06 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_02 | 2048 | 5.364e-06 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_03 | 2048 | 5.364e-06 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_04 | 2048 | 5.364e-06 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_05 | 2048 | 5.328e-06 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_06 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_07 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_08 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_09 | 2048 | 1.0768e-05 | 0.00025 | 0 | 0 |
| ibm_marrakesh_static_pub_10 | 2048 | 1.0732e-05 | 0.00025 | 0 | 0 |

Job `ibm_marrakesh/static/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family coherence-window \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 2048 \
  --seeds 1 \
  --max-pending 100 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 262144 \
  --precision 0.33 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 18.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family coherence-window \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 2048 \
  --seeds 1 \
  --max-pending 100 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 262144 \
  --precision 0.33 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 18.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-15T013256.246642Z \
  --approved-record-sha256 e0f9a714718630091fca5d6353df1497c6733e332d78a09de68aae945cd562be \
  --submit
```
