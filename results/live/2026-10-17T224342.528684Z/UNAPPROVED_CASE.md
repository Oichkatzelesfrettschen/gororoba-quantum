# Unapproved QPU case: state-prep-control

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-17T224342.528684Z`.
- [record.json](record.json) SHA-256: `6b80ce043934f0571512735cb567240dc28ec6fc9932da8784d8170d958af91a`.
- [isa.qpy](isa.qpy) SHA-256: `89ad3d29ec9e0e63242f6b0364c29055b249d09e90a5928d0421a2b70fc5b9eb`.
- Experiment source digest: `a518f8495ebaa7d50d394ba38bd2c6b20034a4116d622875dc9ba85c3a29d217`.
- Source commit: `55d6b075cd8cdaf75e10f964683e4145ce80e1c5`; sources_modified=`false`.
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

The state-prep-control family measures, on 7 qubits of ibm_kingston (the declared layout: 104, 105, 106, 117, 124, 125, 126), the excited fraction each qubit carries after the Sampler's implicit initialization at a requested repetition delay of 250 us (`--rep-delay 0.00025`). Three PUBs measure every qubit in each shot: A initializes and measures (residual excitation plus readout misassignment), B adds an active reset before the measure, and C applies an X before the measure (the |1> column of the assignment matrix). A and C share the static job; B, which the reset makes dynamic, runs in its own job with twirling and dynamical decoupling off.

Under the readout channel e10 = prob_meas1_prep0, e01 = prob_meas0_prep1, A reads (1 - eps) e10 + eps (1 - e01), so the initial excitation is eps = (A - e10) / (1 - e01 - e10) (diagnostic_experiments.state_prep_excitation), the value dynamic_density's prep_excitation and live_run's --prep-excitation take. The reset benefit A - B is positive only where initialization leaves more excitation than the reset's own misassignment. The calibration noise model starts every qubit in |0>, so it prices A at the readout error alone; the residual excitation is the device property this run measures, and only the device answers it.

Three two-sided precision contracts per qubit, 21 in all, split the family-wise alpha evenly and admit the design: half-width 0.025 on A and on C, 0.05 on A - B, Hoeffding radii valid under arbitrary dependence between the qubits of one shot. They price resolution, not an effect. The comparison of A between two repetition delays spans two jobs, so it is outside these contracts; the written addendum states that comparison and its decision rule.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| spc_prep0_q104 | `[1.0, 0.0]` |
| spc_prep0_q105 | `[1.0, 0.0]` |
| spc_prep0_q106 | `[1.0, 0.0]` |
| spc_prep0_q117 | `[1.0, 0.0]` |
| spc_prep0_q124 | `[1.0, 0.0]` |
| spc_prep0_q125 | `[1.0, 0.0]` |
| spc_prep0_q126 | `[1.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| state_prep_q104 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[104]` | `[[104]]` |
| state_prep_q105 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[105]` | `[[105]]` |
| state_prep_q106 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[106]` | `[[106]]` |
| state_prep_q117 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[117]` | `[[117]]` |
| state_prep_q124 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[124]` | `[[124]]` |
| state_prep_q125 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[125]` | `[[125]]` |
| state_prep_q126 | ibm_kingston | 2026-10-17T15:07:14-07:00 | 20261010 | `[126]` | `[[126]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    104,
    105,
    106,
    117,
    124,
    125,
    126
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "state_prep_q104": [
      {
        "104": 104
      }
    ],
    "state_prep_q105": [
      {
        "105": 105
      }
    ],
    "state_prep_q106": [
      {
        "106": 106
      }
    ],
    "state_prep_q117": [
      {
        "117": 117
      }
    ],
    "state_prep_q124": [
      {
        "124": 124
      }
    ],
    "state_prep_q125": [
      {
        "125": 125
      }
    ],
    "state_prep_q126": [
      {
        "126": 126
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### spc_excited_q104

Score terms (each member averages its recorded replicas):

- `spc_prep0_q104`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00607299804688; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is -0.00520980447535.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q105

Score terms (each member averages its recorded replicas):

- `spc_prep0_q105`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.001953125; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is -0.00932967752223.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q106

Score terms (each member averages its recorded replicas):

- `spc_prep0_q106`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00677490234375; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is -0.00450790017848.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q117

Score terms (each member averages its recorded replicas):

- `spc_prep0_q117`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00119018554688; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is -0.0100926169754.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q124

Score terms (each member averages its recorded replicas):

- `spc_prep0_q124`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.013916015625; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is 0.00263321310277.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q125

Score terms (each member averages its recorded replicas):

- `spc_prep0_q125`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.049072265625; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is 0.0377894631028.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

### spc_excited_q126

Score terms (each member averages its recorded replicas):

- `spc_prep0_q126`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0112828025222. The lower modeled value is -0.00994002908473.

At alpha 0.00714285714286, the two-sided confidence half-width is 0.0185450873243; requested precision is 0.025.

The search-wide simulation error probability is 0.01 across 21 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.741803492971. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 1 | 8192 | 4.36585856 | 5 |

The cost model predicts 4.36585856 seconds. The per-job service ceilings sum to 5 seconds against an invocation cap of 5 seconds. The global reserve is 60 seconds; the saved quota reports 266 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 8192 | 2.18e-06 | 0.00025 | 0 | 0 |

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
  --family state-prep-control \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --layout 104,105,106,117,124,125,126 \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 5 \
  --rep-delay 0.00025 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 5.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family state-prep-control \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --layout 104,105,106,117,124,125,126 \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 5 \
  --rep-delay 0.00025 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 5.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-17T224342.528684Z \
  --approved-record-sha256 6b80ce043934f0571512735cb567240dc28ec6fc9932da8784d8170d958af91a \
  --submit
```
