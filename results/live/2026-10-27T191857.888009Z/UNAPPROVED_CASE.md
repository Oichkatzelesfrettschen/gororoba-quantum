# Unapproved QPU case: state-prep-control

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-32768` at 32768 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-27T191857.888009Z`.
- [record.json](record.json) SHA-256: `914a19475d3304e7851ea3a3347c93a84088d34862e8f8f2fcb96797eb305bc7`.
- [isa.qpy](isa.qpy) SHA-256: `02d1024437e8f45ee4cf4d1280ed65df05cea51f13dcde4f8ed5834f79be7543`.
- Experiment source digest: `3bd68dc850d6458c7259e46acfc70511b2af8089c937009a821f78122c08e118`.
- Source commit: `b7ee3e4cb9bc5651ea069d471d39253ff20cc28f`; sources_modified=`true`.
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

The state-prep-control family measures, on 6 qubits of ibm_kingston (the declared layout: 147, 148, 149, 141, 142, 143), the excited fraction each qubit carries after the Sampler's implicit initialization at a requested repetition delay of 20 us (`--rep-delay 2e-05`). Three PUBs measure every qubit in each shot: A initializes and measures (residual excitation plus readout misassignment); XR applies an X and measures twice (the |1> column, read again by a second measurement); R initializes and measures twice, so the second read separates a population the first read found from a misassignment of the first read. A, XR and R share the static job in that row order. The run selects the arms prep0, x_remeasure, remeasure (`--state-prep-arms prep0,x_remeasure,remeasure`).

Under the readout channel e10 = prob_meas1_prep0, e01 = prob_meas0_prep1, A reads (1 - eps) e10 + eps (1 - e01), so the initial excitation is eps = (A - e10) / (1 - e01 - e10) (diagnostic_experiments.state_prep_excitation), the value dynamic_density's prep_excitation and live_run's --prep-excitation take. R reads each shot twice. A measurement projects the qubit onto the state it reads up to misassignment, so a population the first read found reads 1 again with probability 1 - e01 less the T1 decay over one measurement, while a misassigned first read is followed by a read of the prepared state; P(both reads 1) / P(first read 1) therefore separates a population from a misassignment. The service runs every circuit of shot s in row order before shot s + 1, so each R shot follows the row before it, an XR read of |1> when XR is selected. The calibration noise model starts every qubit in |0>, so it prices A at the readout error alone; the residual excitation is the device property this run measures, and only the device answers it.

Four two-sided precision contracts per qubit, 24 in all, split the family-wise alpha evenly and admit the design: half-width 0.025 on A, 0.025 on R's first read, 0.025 on R's both-reads-1 fraction, 0.025 on XR's first read, Hoeffding radii valid under arbitrary dependence between the qubits of one shot. They price resolution, not an effect. The comparison of A between two repetition delays spans two jobs, so it is outside these contracts; the written addendum states that comparison and its decision rule.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| spc_prep0_q147 | `[1.0, 0.0]` |
| spc_x_remeasure_q147 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q147 | `[1.0, 0.0, 0.0, 0.0]` |
| spc_prep0_q148 | `[1.0, 0.0]` |
| spc_x_remeasure_q148 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q148 | `[1.0, 0.0, 0.0, 0.0]` |
| spc_prep0_q149 | `[1.0, 0.0]` |
| spc_x_remeasure_q149 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q149 | `[1.0, 0.0, 0.0, 0.0]` |
| spc_prep0_q141 | `[1.0, 0.0]` |
| spc_x_remeasure_q141 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q141 | `[1.0, 0.0, 0.0, 0.0]` |
| spc_prep0_q142 | `[1.0, 0.0]` |
| spc_x_remeasure_q142 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q142 | `[1.0, 0.0, 0.0, 0.0]` |
| spc_prep0_q143 | `[1.0, 0.0]` |
| spc_x_remeasure_q143 | `[0.0, 0.0, 0.0, 1.0]` |
| spc_remeasure_q143 | `[1.0, 0.0, 0.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| state_prep_q147 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[147]` | `[[147]]` |
| state_prep_q148 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[148]` | `[[148]]` |
| state_prep_q149 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[149]` | `[[149]]` |
| state_prep_q141 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[141]` | `[[141]]` |
| state_prep_q142 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[142]` | `[[142]]` |
| state_prep_q143 | ibm_kingston | 2026-10-27T12:00:41-07:00 | 20261010 | `[143]` | `[[143]]` |

Calibration-bound family and replica mapping:

```json
{
  "qubits": [
    147,
    148,
    149,
    141,
    142,
    143
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "state_prep_q147": [
      {
        "147": 147
      }
    ],
    "state_prep_q148": [
      {
        "148": 148
      }
    ],
    "state_prep_q149": [
      {
        "149": 149
      }
    ],
    "state_prep_q141": [
      {
        "141": 141
      }
    ],
    "state_prep_q142": [
      {
        "142": 142
      }
    ],
    "state_prep_q143": [
      {
        "143": 143
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### spc_excited_q147

Score terms (each member averages its recorded replicas):

- `spc_prep0_q147`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.002197265625; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00917547195699.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q147

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q147`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.00299072265625; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00838201492574.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q147

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q147`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 3.0517578125e-05; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0113422200039.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q147

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q147`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.989898681641; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.978525944059.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_excited_q148

Score terms (each member averages its recorded replicas):

- `spc_prep0_q148`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0103656575039.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q148

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q148`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.00143432617188; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00993841141012.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q148

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q148`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.011372737582.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q148

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q148`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.994323730469; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.982950992887.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_excited_q149

Score terms (each member averages its recorded replicas):

- `spc_prep0_q149`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0100299641445.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q149

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q149`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.00201416015625; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00935857742574.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q149

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q149`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.011372737582.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q149

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q149`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.994354248047; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.982981510465.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_excited_q141

Score terms (each member averages its recorded replicas):

- `spc_prep0_q141`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.00100708007812; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0103656575039.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q141

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q141`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.00143432617188; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00993841141012.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q141

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q141`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.011372737582.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q141

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q141`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.988494873047; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.977122135465.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_excited_q142

Score terms (each member averages its recorded replicas):

- `spc_prep0_q142`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0333862304688; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.0220134928868.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q142

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q142`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.0333862304688; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.0220134928868.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q142

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q142`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 0.00112915039062; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0102435871914.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q142

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q142`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.9755859375; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.964213199918.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_excited_q143

Score terms (each member averages its recorded replicas):

- `spc_prep0_q143`: sign +1, labeled score vector `[0.0, 1.0]`.

The noise model predicts 0.0101928710938; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.00117986648824.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_excited_q143

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q143`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.0113830566406; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 1.03190586315e-05.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_remeasure_persisting_q143

Score terms (each member averages its recorded replicas):

- `spc_remeasure_q143`: sign +1, labeled score vector `[0.0, 0.0, 0.0, 1.0]`.

The noise model predicts 0.000152587890625; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is -0.0112201496914.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

### spc_x_remeasure_one_column_q143

Score terms (each member averages its recorded replicas):

- `spc_x_remeasure_q143`: sign +1, labeled score vector `[0.0, 1.0, 0.0, 1.0]`.

The noise model predicts 0.985900878906; the simultaneous finite-simulation allowance is +/-0.011372737582. The lower modeled value is 0.974528141324.

At alpha 0.00208333333333, the two-sided confidence half-width is 0.0102362633072; requested precision is 0.025.

The search-wide simulation error probability is 0.01 across 24 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.409450532287. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 3 | 98304 | 4.624299776 | 12 |

The cost model predicts 4.624299776 seconds. The per-job service ceilings sum to 12 seconds against an invocation cap of 12 seconds. The global reserve is 0 seconds; the saved quota reports 197 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 32768 | 2.18e-06 | 2e-05 | 0 | 0 |
| ibm_kingston_static_pub_02 | 32768 | 4.392e-06 | 2e-05 | 0 | 0 |
| ibm_kingston_static_pub_03 | 32768 | 4.36e-06 | 2e-05 | 0 | 0 |

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
  --layout 147,148,149,141,142,143 \
  --state-prep-arms prep0,x_remeasure,remeasure \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 12 \
  --rep-delay 2e-05 \
  --max-replicas 1 \
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
  --max-total-execution-seconds 12.0 \
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
  --layout 147,148,149,141,142,143 \
  --state-prep-arms prep0,x_remeasure,remeasure \
  --backends ibm_kingston \
  --shots 32768 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 12 \
  --rep-delay 2e-05 \
  --max-replicas 1 \
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
  --max-total-execution-seconds 12.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-27T191857.888009Z \
  --approved-record-sha256 914a19475d3304e7851ea3a3347c93a84088d34862e8f8f2fcb96797eb305bc7 \
  --submit
```
