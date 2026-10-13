# Unapproved QPU case: patch-window

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-2048` at 2048 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-13T163154.032617Z`.
- [record.json](record.json) SHA-256: `a0ed332e83cd69c404be983b197d92e36bbd70aac3f96de9e8a4666b8b90c58e`.
- [isa.qpy](isa.qpy) SHA-256: `3d6f8162624df981b042244166e564407d2f7d58243587f6c7edc394a35d1965`.
- Experiment source digest: `12fe73bbfd6e5527fef9d140461cc5b7c978b1afff4462393e3028cce080d918`.
- Source commit: `af38c7a5f25bdfd2824a25516919fa7973a8a747`; sources_modified=`true`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

The source flag records changes anywhere in the experiment directory, including documentation and unmanifested files. Reproduction requires verification of every declared source against the experiment digest; the broad flag alone does not establish which source bytes differ from the recorded commit. A separate source-closure audit can establish that comparison without altering the retained record.

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

The N=21, base-4 family measures the change in the labeled two-phase-bit distribution when feed-forward is removed. Array labels are 00, 01, 10, 11 (index b0 + 2*b1). The preregistered score is P(01)-P(11) with feedback, minus the same score without feedback. Two phase bits provide a feedback diagnostic; they do not establish successful general order recovery, factoring advantage, or an asymptotic speedup.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| ramsey_plain_x_d900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d1400 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1400 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d1400 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d1400 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_plain_x_d1900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_plain_y_d1900 | `[0.25, 0.25, 0.25, 0.25]` |
| ramsey_echo_x_d1900 | `[1.0, 0.0, 0.0, 0.0]` |
| ramsey_echo_y_d1900 | `[0.25, 0.25, 0.25, 0.25]` |
| exchange_work_a_d900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_b_d900 | `[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_a_d1400 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_b_d1400 | `[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_a_d1900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| exchange_work_b_d1900 | `[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c0_x_d900 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c0_y_d900 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| readout_window_c1_x_d900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c1_y_d900 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| readout_window_c0_x_d1400 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c0_y_d1400 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| readout_window_c1_x_d1400 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c1_y_d1400 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| readout_window_c0_x_d1900 | `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c0_y_d1900 | `[0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0]` |
| readout_window_c1_x_d1900 | `[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]` |
| readout_window_c1_y_d1900 | `[0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]` |
| barrier_orbit_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| barrier_orbit_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| patch_static | ibm_fez | 2026-10-13T09:08:33-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |
| patch_dynamic | ibm_fez | 2026-10-13T09:08:33-07:00 | 20261010 | `[142, 136, 143, 144, 123, 145]` | `[[142, 136, 143, 144, 123, 145]]` |

Calibration-bound family and replica mapping:

```json
{
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

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### work_a_ramsey_visibility

Score terms (each member averages its recorded replicas):

- `ramsey_plain_x_d900`: sign +1, labeled score vector `[1.0, -1.0, 1.0, -1.0]`.

The noise model predicts 0.941040039062; the simultaneous finite-simulation allowance is +/-0.0270440372282. The lower modeled value is 0.913996001834.

At alpha 0.025, the two-sided confidence half-width is 0.0654165337313; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0600201744575 (null 0 plus one-sided radius 0.0600201744575). The admitted alternative effect is 0.913996001834, with conditional target power 0.8 and lower-tail radius 0.0396448825369. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### work_b_ramsey_visibility

Score terms (each member averages its recorded replicas):

- `ramsey_plain_x_d900`: sign +1, labeled score vector `[1.0, 1.0, -1.0, -1.0]`.

The noise model predicts 0.964233398438; the simultaneous finite-simulation allowance is +/-0.0270440372282. The lower modeled value is 0.937189361209.

At alpha 0.025, the two-sided confidence half-width is 0.0654165337313; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0600201744575 (null 0 plus one-sided radius 0.0600201744575). The admitted alternative effect is 0.937189361209, with conditional target power 0.8 and lower-tail radius 0.0396448825369. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 2 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 14 | 28672 | 9.725785856 | 20 |
| ibm_fez/static/1 | 18 | 36864 | 11.785697024 | 20 |

The cost model predicts 21.51148288 seconds. The per-job service ceilings sum to 40 seconds against an invocation cap of 40 seconds. The global reserve is 60 seconds; the saved quota reports 415 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_02 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_04 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_06 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_07 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_08 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_09 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_10 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_11 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_12 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_13 | 2048 | 9.088e-06 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_14 | 2048 | 9.088e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_01 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_02 | 2048 | 5.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_03 | 2048 | 5.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_04 | 2048 | 5.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_05 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_06 | 2048 | 7.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_07 | 2048 | 7.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_08 | 2048 | 7.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_09 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_10 | 2048 | 9.308e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_11 | 2048 | 9.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_12 | 2048 | 9.356e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_13 | 2048 | 5.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_14 | 2048 | 5.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_15 | 2048 | 7.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_16 | 2048 | 7.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_17 | 2048 | 9.284e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_18 | 2048 | 9.284e-06 | 0.00025 | 0 | 0 |

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
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez \
  --shots 2048 \
  --seeds 1 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 20 \
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
  --max-total-execution-seconds 40.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family patch-window \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez \
  --shots 2048 \
  --seeds 1 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 20 \
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
  --max-total-execution-seconds 40.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-13T163154.032617Z \
  --approved-record-sha256 a0ed332e83cd69c404be983b197d92e36bbd70aac3f96de9e8a4666b8b90c58e \
  --submit
```
