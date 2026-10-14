# Unapproved QPU case: coherence-window

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-2048-per-pub` with per-PUB shot allocation (used tiers: 2048; 2 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-14T041957.187831Z`.
- [record.json](record.json) SHA-256: `29ae86ae86327b155cf08dc41ba19ca2009598208c44d039609ba8fbce9f04fd`.
- [isa.qpy](isa.qpy) SHA-256: `141a7c34619d4b2af6dd328bb8585d7c84ec34667a6c442a79b5fc9fe792c6d0`.
- Experiment source digest: `879b50c1fd65b838b05ddfa73795d7e9261f3e8fe2e96d6620b6acbe76341231`.
- Source commit: `30909c194bd630dab43e694d7073932fabfe27df`; sources_modified=`false`.
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

The coherence-window family measures, on the physical qubits control 142, work_a 136, spectator 143, work_b 144, neighbor_a 123, neighbor_b 145 on ibm_fez, the work coherence the first N=21 orbit round leaves between work_a and work_b, signed by the control's first bit b0. That coherence changes sign with b0, so its branch-unsigned average is zero on an ideal device and the terminal four-outcome orbit law cannot see it. Each shot is weighted by (-1)^b0, and C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 has |C| = 1/2 ideally.

Three contexts follow the same round-1 prefix: immediate readout; a matched idle of 836 dt (the control's measure plus reset) with b0 read after it; and a mid-circuit measure and reset of the control before the work readout. A coherent window phase rotates C between contexts, dephasing or amplitude damping shrinks |C| without rotating it, and first-bit assignment error scales C by (1 - 2 epsilon), so rotation and shrinkage separate the explanations the terminal law left degenerate. The matched idle reads b0 after the window, so control relaxation there adds to epsilon and scales that context's C without rotating it. The branch-unsigned average is a negative control, the ZZ setting and the spectator readout give the work populations and the one-hot sector.

Five two-sided precision contracts admit the design: Re C in the immediate context and the Re C and Im C differences between adjacent contexts. They price resolution, not an effect; an unresolved rotation or a context-independent C remains an allowed outcome, and a phase is reported only where |C| supports it.

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
| coherence_static | ibm_fez | 2026-10-13T20:50:11-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |
| coherence_dynamic | ibm_fez | 2026-10-13T20:50:11-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |

Calibration-bound family and replica mapping:

```json
{
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "coherence_static": [
      {
        "123": 123,
        "136": 136,
        "142": 142,
        "143": 143,
        "144": 144,
        "145": 145
      }
    ],
    "coherence_dynamic": [
      {
        "123": 123,
        "136": 136,
        "142": 142,
        "143": 143,
        "144": 144,
        "145": 145
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

The noise model predicts 1.73706054688; the simultaneous finite-simulation allowance is +/-0.0632327712626. The lower modeled value is 1.67382777561.

At alpha 0.01, the two-sided confidence half-width is 0.152984176918; requested precision is 0.24.

### re_matched_idle_minus_immediate

Score terms (each member averages its recorded replicas):

- `coherence_matched_idle_xx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_xx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_yy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts -0.127807617188; the simultaneous finite-simulation allowance is +/-0.126465542525. The lower modeled value is -0.254273159713.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### im_matched_idle_minus_immediate

Score terms (each member averages its recorded replicas):

- `coherence_matched_idle_xy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_xy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_immediate_yx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 0.005859375; the simultaneous finite-simulation allowance is +/-0.126465542525. The lower modeled value is -0.120606167525.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### re_measure_reset_minus_matched_idle

Score terms (each member averages its recorded replicas):

- `coherence_measure_reset_xx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_measure_reset_yy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_xx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 0.125732421875; the simultaneous finite-simulation allowance is +/-0.126465542525. The lower modeled value is -0.000733120650148.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

### im_measure_reset_minus_matched_idle

Score terms (each member averages its recorded replicas):

- `coherence_measure_reset_xy`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_measure_reset_yx`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_xy`: sign -1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.
- `coherence_matched_idle_yx`: sign +1, labeled score vector `[1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.126465542525. The lower modeled value is -0.124512417525.

At alpha 0.01, the two-sided confidence half-width is 0.32318270103; requested precision is 0.33.

The search-wide simulation error probability is 0.01 across 18 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.979341518272. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 5 | 10240 | 4.934579968 | 9 |
| ibm_fez/static/1 | 10 | 20480 | 7.534917376 | 9 |

The cost model predicts 12.469497344 seconds. The per-job service ceilings sum to 18 seconds against an invocation cap of 18 seconds. The global reserve is 60 seconds; the saved quota reports 390 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_02 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_04 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 2048 | 7.264e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_01 | 2048 | 3.944e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_02 | 2048 | 3.944e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_03 | 2048 | 3.944e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_04 | 2048 | 3.944e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_05 | 2048 | 3.92e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_06 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_07 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_08 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_09 | 2048 | 7.288e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_10 | 2048 | 7.264e-06 | 0.00025 | 0 | 0 |

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
  --family coherence-window \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --patch-qubits 142,136,143,144,123,145 \
  --backends ibm_fez \
  --shots 2048 \
  --seeds 1 \
  --max-pending 50 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 16384 \
  --precision 0.08 \
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
  --patch-qubits 142,136,143,144,123,145 \
  --backends ibm_fez \
  --shots 2048 \
  --seeds 1 \
  --max-pending 50 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 16384 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 18.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-14T041957.187831Z \
  --approved-record-sha256 29ae86ae86327b155cf08dc41ba19ca2009598208c44d039609ba8fbce9f04fd \
  --submit
```
