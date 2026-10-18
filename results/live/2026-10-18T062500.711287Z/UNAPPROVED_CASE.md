# Unapproved QPU case: n21-orbit-rca

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-003-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-18T062500.711287Z`.
- [record.json](record.json) SHA-256: `bee44f51e6eff892294bf9da2e0fafac3a2776fe0b58d923482cf626fa7d8a9e`.
- [isa.qpy](isa.qpy) SHA-256: `897138af577b87d29caf38ef96d33a999d1264183c4bfa8588b7dc46ed2bab5f`.
- Experiment source digest: `d3ec91a38f2c80312c721b0eec1ed4dbcde554bec853a4269d37086cb02a0a74`.
- Source commit: `656e944ddb81033932476b86855328468542e84c`; sources_modified=`false`.
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

The N=21, base-4 family measures the change in the labeled two-phase-bit distribution when feed-forward is removed. Array labels are 00, 01, 10, 11 (index b0 + 2*b1). The preregistered score is P(01)-P(11) with feedback, minus the same score without feedback. Two phase bits provide a feedback diagnostic; they do not establish successful general order recovery, factoring advantage, or an asymptotic speedup.

The orbit families compile each controlled multiplier only on the orbit 1, 4, 16 of the work register, which supplies the order 3 to the circuit. They measure feed-forward in a two-round semiclassical QPE and perform no order finding or factoring (Smolin, Smith and Vargo, Nature 499, 163 (2013)). The window arms of n21-orbit-rca idle the control, read it a second time, or echo the work qubits during the first measurement and reset; the family configuration records their durations in dt.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_orbit_nominal_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_orbit_nominal_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |
| n21_orbit_window_delay_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_orbit_window_delay_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |
| n21_orbit_extra_readout_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_orbit_extra_readout_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |
| n21_orbit_window_echo_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_orbit_window_echo_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| n21_orbit_rca | ibm_fez | 2026-10-17T23:10:01-07:00 | 20261014 | `[25, 23, 24, 22]` | `[[101, 121, 116, 120]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "window_delay_dt": 415,
  "echo_half_dt": 502,
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "n21_orbit_rca": [
      {
        "22": 120,
        "23": 121,
        "24": 116,
        "25": 101
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### n21_orbit_nominal_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_nominal_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_nominal_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.198669433594; the simultaneous finite-simulation allowance is +/-0.0507651723072. The lower modeled value is 0.147904261287.

At alpha 0.0125, the two-sided confidence half-width is 0.075054153599; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0704004575904 (null 0 plus one-sided radius 0.0704004575904). The admitted alternative effect is 0.147904261287, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_orbit_window_delay_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_window_delay_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_window_delay_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.199157714844; the simultaneous finite-simulation allowance is +/-0.0507651723072. The lower modeled value is 0.148392542537.

At alpha 0.0125, the two-sided confidence half-width is 0.075054153599; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0704004575904 (null 0 plus one-sided radius 0.0704004575904). The admitted alternative effect is 0.148392542537, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_orbit_extra_readout_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_extra_readout_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_extra_readout_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.190002441406; the simultaneous finite-simulation allowance is +/-0.0507651723072. The lower modeled value is 0.139237269099.

At alpha 0.0125, the two-sided confidence half-width is 0.075054153599; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0704004575904 (null 0 plus one-sided radius 0.0704004575904). The admitted alternative effect is 0.139237269099, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### n21_orbit_window_echo_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_window_echo_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_window_echo_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.181488037109; the simultaneous finite-simulation allowance is +/-0.0507651723072. The lower modeled value is 0.130722864802.

At alpha 0.0125, the two-sided confidence half-width is 0.075054153599; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0704004575904 (null 0 plus one-sided radius 0.0704004575904). The admitted alternative effect is 0.130722864802, with conditional target power 0.8 and lower-tail radius 0.0474195977933. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 192 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 8 | 65536 | 20.020541184 | 30 |

The cost model predicts 20.020541184 seconds. The per-job service ceilings sum to 30 seconds against an invocation cap of 30 seconds. The global reserve is 0 seconds; the saved quota reports 266 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 8192 | 9.384e-06 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_02 | 8192 | 9.384e-06 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_03 | 8192 | 1.1044e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_04 | 8192 | 1.1044e-05 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_05 | 8192 | 1.1044e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_06 | 8192 | 1.1044e-05 | 0.00025 | 0 | 0 |
| ibm_fez_dynamic_pub_07 | 8192 | 1.0104e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_08 | 8192 | 1.0104e-05 | 0.00025 | 0 | 0 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family n21-orbit-rca \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
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
  --family n21-orbit-rca \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
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
  --approved-record ../results/live/2026-10-18T062500.711287Z \
  --approved-record-sha256 bee44f51e6eff892294bf9da2e0fafac3a2776fe0b58d923482cf626fa7d8a9e \
  --submit
```
