# Unapproved QPU case: patch-window

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096-per-pub` with per-PUB shot allocation (used tiers: 1024, 4096; 3 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-13T201228.119505Z`.
- [record.json](record.json) SHA-256: `425b426c5efd2c14450f850537aea1c97b1ac8ace9dbd45b3aae79300d21dc83`.
- [isa.qpy](isa.qpy) SHA-256: `cd45b6993fa4540ac75cc217a3685f07ff17af8fda34be630543cc6066911473`.
- Experiment source digest: `a8d281df7ce66ba7637f01f783346de8a5c8441622b74f4dd48f7201d404ed06`.
- Source commit: `4aaea17b6f36177274ca4ffce590e421c9e3f9a5`; sources_modified=`false`.
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

The patch-window family characterizes the pinned qubits the N=21 orbit runs used (control, two work qubits, spectator, two outer neighbors). Paired and single-qubit Ramsey, plain and echoed, measure work-qubit phase and visibility against executed idle; measure-and-reset and reset-only windows separate the explicit measurement; exchange circuits with zero-delay, unexcited and all-one references bound population transfer; and nominal, barrier and barrier-plus-echo orbit pairs compare scheduling contexts in one acquisition.

Ten two-sided precision contracts on member differences admit the design; the calibration noise model has no coherent window phase, so they price resolution, not an effect. The Y-only Ramsey endpoints resolve phase differences only at favorable orientation, the exchange and orbit endpoints are exploratory, and an unresolved or no-intervention outcome remains allowed. Physical detuning is withheld wherever executed timing, alias separation or visibility does not support it.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| ramsey_plain_x_d900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d1400 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1400 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d1900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d1400 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d1400 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d1900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d1900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d0 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d0 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d1900_only_work_a | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1900_only_work_a | `[0.5, 0.5, 0.0, 0.0]` |
| ramsey_plain_x_d1900_only_work_b | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1900_only_work_b | `[0.5, 0.0, 0.5, 0.0]` |
| exchange_work_a_d0 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_a_d1900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_b_d0 | `[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_b_d1900 | `[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_none_d1900 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_all_d0 | `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]` |
| window_measure_reset_c0_x_d900 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c0_y_d900 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| window_measure_reset_c1_x_d900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c1_y_d900 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| window_measure_reset_c0_x_d1400 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c0_y_d1400 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| window_measure_reset_c1_x_d1400 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c1_y_d1400 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| window_measure_reset_c0_x_d1900 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c0_y_d1900 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| window_measure_reset_c1_x_d1900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_measure_reset_c1_y_d1900 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| window_reset_only_c0_x_d1400 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_reset_only_c0_y_d1400 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| window_reset_only_c1_x_d1400 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| window_reset_only_c1_y_d1400 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| orbit_nominal_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| orbit_nominal_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |
| orbit_window_barrier_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| orbit_window_barrier_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |
| orbit_window_echo_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| orbit_window_echo_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| patch_static | ibm_fez | 2026-10-13T11:56:54-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |
| patch_dynamic | ibm_fez | 2026-10-13T11:56:54-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |

Calibration-bound family and replica mapping:

```json
{
  "measure_dt": 415,
  "echo_half_dt": 502,
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "patch_static": [
      {
        "123": 123,
        "136": 136,
        "142": 142,
        "143": 143,
        "144": 144,
        "145": 145
      }
    ],
    "patch_dynamic": [
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

### work_a_echo_minus_plain_y

Score terms (each member averages its recorded replicas):

- `ramsey_echo_y_d1900`: sign +1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.
- `ramsey_plain_y_d1900`: sign -1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.

The noise model predicts 0.0010986328125; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0632352861066.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_b_echo_minus_plain_y

Score terms (each member averages its recorded replicas):

- `ramsey_echo_y_d1900`: sign +1, labeled score vector `[1.0, 1.0, -1.0, -1.0]`.
- `ramsey_plain_y_d1900`: sign -1, labeled score vector `[1.0, 1.0, -1.0, -1.0]`.

The noise model predicts 0.0067138671875; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0576200517316.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_a_window_minus_plain_y

Score terms (each member averages its recorded replicas):

- `window_measure_reset_c1_y_d1400`: sign +1, labeled score vector `[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0]`.
- `ramsey_plain_y_d1400`: sign -1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.

The noise model predicts -0.0147705078125; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0791044267316.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_b_window_minus_plain_y

Score terms (each member averages its recorded replicas):

- `window_measure_reset_c1_y_d1400`: sign +1, labeled score vector `[1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0]`.
- `ramsey_plain_y_d1400`: sign -1, labeled score vector `[1.0, 1.0, -1.0, -1.0]`.

The noise model predicts -0.016357421875; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0806913407941.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_a_control_one_minus_zero_y

Score terms (each member averages its recorded replicas):

- `window_measure_reset_c1_y_d1400`: sign +1, labeled score vector `[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0]`.
- `window_measure_reset_c0_y_d1400`: sign -1, labeled score vector `[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0]`.

The noise model predicts 0.0040283203125; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0603055986066.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_a_measured_minus_reset_only_y

Score terms (each member averages its recorded replicas):

- `window_measure_reset_c1_y_d1400`: sign +1, labeled score vector `[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0]`.
- `window_reset_only_c1_y_d1400`: sign -1, labeled score vector `[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0]`.

The noise model predicts 0.0003662109375; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0639677079816.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### work_a_paired_minus_single_y

Score terms (each member averages its recorded replicas):

- `ramsey_plain_y_d1900`: sign +1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.
- `ramsey_plain_y_d1900_only_work_a`: sign -1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.

The noise model predicts 0.0064697265625; the simultaneous finite-simulation allowance is +/-0.0643339189191. The lower modeled value is -0.0578641923566.

At alpha 0.005, the two-sided confidence half-width is 0.22852467946; requested precision is 0.25.

### spectator_excess_from_work_a

Score terms (each member averages its recorded replicas):

- `exchange_work_a_d1900`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.
- `exchange_none_d1900`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]`.

The noise model predicts -6.103515625e-05; the simultaneous finite-simulation allowance is +/-0.0321669594595. The lower modeled value is -0.0322279946158.

At alpha 0.005, the two-sided confidence half-width is 0.11426233973; requested precision is 0.12.

### orbit_barrier_minus_nominal

Score terms (each member averages its recorded replicas):

- `orbit_window_barrier_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_window_barrier_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_nominal_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_nominal_no_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts -0.0272827148438; the simultaneous finite-simulation allowance is +/-0.128667837838. The lower modeled value is -0.155950552682.

At alpha 0.005, the two-sided confidence half-width is 0.24008069783; requested precision is 0.25.

### orbit_echo_minus_barrier

Score terms (each member averages its recorded replicas):

- `orbit_window_echo_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_window_echo_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_window_barrier_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `orbit_window_barrier_no_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.00689697265625; the simultaneous finite-simulation allowance is +/-0.128667837838. The lower modeled value is -0.121770865182.

At alpha 0.005, the two-sided confidence half-width is 0.24008069783; requested precision is 0.25.

The search-wide simulation error probability is 0.01 across 24 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.96032279132. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 16 | 16384 | 6.515734272 | 9 |
| ibm_fez/dynamic/2 | 6 | 24576 | 8.92716416 | 9 |
| ibm_fez/static/1 | 24 | 24576 | 8.609388288 | 9 |

The cost model predicts 24.05228672 seconds. The per-job service ceilings sum to 27 seconds against an invocation cap of 27 seconds. The global reserve is 60 seconds; the saved quota reports 415 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_02 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_04 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_06 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_07 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_08 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_09 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_10 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_11 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_12 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_13 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_14 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_15 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_16 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_17 | 4096 | 8.996e-06 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_18 | 4096 | 8.996e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_19 | 4096 | 9.968e-06 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_20 | 4096 | 9.968e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_21 | 4096 | 1.0016e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_22 | 4096 | 1.0016e-05 | 0.00025 | 0 | 0 |

Job `ibm_fez/dynamic/2` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_01 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_02 | 1024 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_03 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_04 | 1024 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_05 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_06 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_07 | 1024 | 5.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_08 | 1024 | 5.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_09 | 1024 | 7.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_10 | 1024 | 7.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_11 | 1024 | 9.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_12 | 1024 | 9.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_13 | 1024 | 1.708e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_14 | 1024 | 1.708e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_15 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_16 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_17 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_18 | 1024 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_19 | 1024 | 1.684e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_20 | 1024 | 9.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_21 | 1024 | 1.684e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_22 | 1024 | 9.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_23 | 1024 | 9.26e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_24 | 1024 | 1.684e-06 | 0.00025 | 0 | 0 |

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
  --family patch-window \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --patch-qubits 142,136,143,144,123,145 \
  --backends ibm_fez \
  --shots 4096 \
  --seeds 1 \
  --max-pending 50 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096 \
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
  --max-total-execution-seconds 27.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family patch-window \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --patch-qubits 142,136,143,144,123,145 \
  --backends ibm_fez \
  --shots 4096 \
  --seeds 1 \
  --max-pending 50 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 9 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096 \
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
  --max-total-execution-seconds 27.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-13T201228.119505Z \
  --approved-record-sha256 425b426c5efd2c14450f850537aea1c97b1ac8ace9dbd45b3aae79300d21dc83 \
  --submit
```
