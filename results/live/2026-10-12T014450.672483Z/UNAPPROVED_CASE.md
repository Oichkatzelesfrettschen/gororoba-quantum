# Unapproved QPU case: folded-qpe

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-001-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-12T014450.672483Z`.
- [record.json](record.json) SHA-256: `e43c3e5bca12795a77d4148ff958735354271635430e2114f3b10233f9032d98`.
- [isa.qpy](isa.qpy) SHA-256: `661d5ba80e4cc0789a9526c548610bddfc86a299c5fa3f12f78fe6c19c68079d`.
- Experiment source digest: `bea51b497aaa1a7c43a9d40789648776352aae80571afe02e42632a410a8ae4b`.
- Source commit: `877f73c2bd15f242a8a5d54089347ab0bcf6d16d`; sources_modified=`true`.
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

## Scientific question and interpretation

The folded-QPE ladder measures terminal-bit contrasts for four supplied eigenstate labels. The archived arm, calibrated-delay arm, measurement-without-feedback arm, and coherent two-control arm expose distinct failures of the calibration-derived outcome model. The delay arm measures only its terminal bit; the supplied first-bit label is a preparation input. The other arms retain two measured bits with label index b0 + 2*b1.

The delay replaces the compiled first measurement's duration, rounded to device granularity, retains reset, and uses the supplied eigenstate label for its unconditional correction. The intervention changes measurement and correction behavior together. Removing feedback changes some ideal laws. The coherent arm adds a control qubit and runs in a separate static job. Shared initial placement preserves the initial register assignment; coherent routing and terminal readout sites can differ. The archived mapping below records those confounds. A contrast therefore does not establish a unique gate-level cause.

Noise simulation computes conditional predictions from Target/properties. The declared classical-latency allowance contributes to the cost estimate; scheduler-latency noise remains outside the Aer outcome model. Only future hardware observations measure scheduler residuals, correlated errors, readout disturbance, and drift omitted by that model. Raw outcomes, scheduler metadata, calibration windows, and charged usage support the comparison.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the feedback distinction.

| Member | Labeled ideal probabilities |
|---|---|
| qpe_coherent_s0 | `[1.0, 0.0, 0.0, 0.0]` |
| qpe_coherent_s1 | `[0.0, 1.0, 0.0, 0.0]` |
| qpe_coherent_s2 | `[0.0, 0.0, 1.0, 0.0]` |
| qpe_coherent_s3 | `[0.0, 0.0, 0.0, 1.0]` |
| qpe_archived_s0 | `[1.0, 0.0, 0.0, 0.0]` |
| qpe_archived_s1 | `[0.0, 1.0, 0.0, 0.0]` |
| qpe_archived_s2 | `[0.0, 0.0, 1.0, 0.0]` |
| qpe_archived_s3 | `[0.0, 0.0, 0.0, 1.0]` |
| qpe_delay_s0 | `[1.0, 0.0]` |
| qpe_delay_s1 | `[1.0, 0.0]` |
| qpe_delay_s2 | `[0.0, 1.0]` |
| qpe_delay_s3 | `[0.0, 1.0]` |
| qpe_no_feed_forward_s0 | `[1.0, 0.0, 0.0, 0.0]` |
| qpe_no_feed_forward_s1 | `[0.0, 0.5, 0.0, 0.5]` |
| qpe_no_feed_forward_s2 | `[0.0, 0.0, 1.0, 0.0]` |
| qpe_no_feed_forward_s3 | `[0.0, 0.5, 0.0, 0.5]` |

| Group | Backend | Calibration | Transpiler seed | Initial layout |
|---|---|---|---:|---|
| folded_qpe_ladder_static | ibm_kingston | 2026-10-11T18:14:09-07:00 | 20261010 | `[98, 92, 93, 94, 79, 91]` |
| folded_qpe_ladder_dynamic | ibm_kingston | 2026-10-11T18:14:09-07:00 | 20261010 | `[98, 92, 93, 94, 79]` |

Calibration-bound family and replica mapping:

```json
{
  "measurement_delay_dt": {
    "0": 545,
    "1": 545,
    "2": 545,
    "3": 545
  },
  "replaced_measurement_qubits": {
    "0": 92,
    "1": 92,
    "2": 92,
    "3": 92
  },
  "shared_initial_layout": [
    98,
    92,
    93,
    94,
    79
  ],
  "extra_control": 91,
  "measurement_seconds": {
    "0": 2.18e-06,
    "1": 2.18e-06,
    "2": 2.18e-06,
    "3": 2.18e-06
  },
  "measurement_sites": {
    "qpe_coherent_s0": [
      [
        98
      ],
      [
        91
      ]
    ],
    "qpe_coherent_s1": [
      [
        98
      ],
      [
        91
      ]
    ],
    "qpe_coherent_s2": [
      [
        98
      ],
      [
        91
      ]
    ],
    "qpe_coherent_s3": [
      [
        98
      ],
      [
        91
      ]
    ],
    "qpe_archived_s0": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_archived_s1": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_archived_s2": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_archived_s3": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_delay_s0": [
      [
        93
      ]
    ],
    "qpe_delay_s1": [
      [
        93
      ]
    ],
    "qpe_delay_s2": [
      [
        93
      ]
    ],
    "qpe_delay_s3": [
      [
        93
      ]
    ],
    "qpe_no_feed_forward_s0": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_no_feed_forward_s1": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_no_feed_forward_s2": [
      [
        92
      ],
      [
        93
      ]
    ],
    "qpe_no_feed_forward_s3": [
      [
        92
      ],
      [
        93
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "folded_qpe_ladder_static": [
      {
        "79": 79,
        "91": 91,
        "92": 92,
        "93": 93,
        "94": 94,
        "98": 98
      }
    ],
    "folded_qpe_ladder_dynamic": [
      {
        "79": 79,
        "91": 91,
        "92": 92,
        "93": 93,
        "94": 94,
        "98": 98
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

The saved endpoints preregister precision intervals.

### qpe_delay_minus_archived_s0

Score terms (each member averages its recorded replicas):

- `qpe_delay_s0`: sign +1, labeled score vector `[1.0, 0.0]`.
- `qpe_archived_s0`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts 0.020263671875; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.051529123298.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_delay_minus_archived_s1

Score terms (each member averages its recorded replicas):

- `qpe_delay_s1`: sign +1, labeled score vector `[1.0, 0.0]`.
- `qpe_archived_s1`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts 0.012939453125; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.058853342048.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_delay_minus_archived_s2

Score terms (each member averages its recorded replicas):

- `qpe_delay_s2`: sign +1, labeled score vector `[0.0, 1.0]`.
- `qpe_archived_s2`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.021484375; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.050308420173.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_delay_minus_archived_s3

Score terms (each member averages its recorded replicas):

- `qpe_delay_s3`: sign +1, labeled score vector `[0.0, 1.0]`.
- `qpe_archived_s3`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.00927734375; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.062515451423.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_no_feed_forward_minus_archived_s0

Score terms (each member averages its recorded replicas):

- `qpe_no_feed_forward_s0`: sign +1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.
- `qpe_archived_s0`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts 0.02001953125; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.051773263923.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_no_feed_forward_minus_archived_s1

Score terms (each member averages its recorded replicas):

- `qpe_no_feed_forward_s1`: sign +1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.
- `qpe_archived_s1`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts -0.410888671875; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.482681467048.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_no_feed_forward_minus_archived_s2

Score terms (each member averages its recorded replicas):

- `qpe_no_feed_forward_s2`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.
- `qpe_archived_s2`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.02587890625; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.045913888923.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_no_feed_forward_minus_archived_s3

Score terms (each member averages its recorded replicas):

- `qpe_no_feed_forward_s3`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.
- `qpe_archived_s3`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts -0.403076171875; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.474868967048.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_coherent_minus_archived_s0

Score terms (each member averages its recorded replicas):

- `qpe_coherent_s0`: sign +1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.
- `qpe_archived_s0`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts -0.005126953125; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.076919748298.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_coherent_minus_archived_s1

Score terms (each member averages its recorded replicas):

- `qpe_coherent_s1`: sign +1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.
- `qpe_archived_s1`: sign -1, labeled score vector `[1.0, 1.0, 0.0, 0.0]`.

The noise model predicts 0.00390625; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.067886545173.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_coherent_minus_archived_s2

Score terms (each member averages its recorded replicas):

- `qpe_coherent_s2`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.
- `qpe_archived_s2`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.004150390625; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.067642404548.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

### qpe_coherent_minus_archived_s3

Score terms (each member averages its recorded replicas):

- `qpe_coherent_s3`: sign +1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.
- `qpe_archived_s3`: sign -1, labeled score vector `[0.0, 0.0, 1.0, 1.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.071792795173. The lower modeled value is -0.071548654548.

At alpha 0.00416666666667, the two-sided confidence half-width is 0.0409450532287; requested precision is 0.08.

The search-wide simulation error probability is 0.01 across 192 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

## Selection objective and sensitivity assumptions

The objective is `precision_at_budget`. Selection compares the declared finite candidate set after statistical and cost admission.

The worst confidence half-width divided by its declared target is 0.511813165359. Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| latency_stress | 4.6 | 60 | 45.534993408 |

The largest nominal/scenario charge is 45.534993408 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 12 | 98304 | 28.82700672 | 60 |
| ibm_kingston/static/1 | 4 | 32768 | 10.797266688 | 60 |

The cost model predicts 39.624273408 seconds. The per-job service ceilings sum to 120 seconds against an invocation cap of 120 seconds. The global reserve is 60 seconds; the saved quota reports 591 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 8192 | 1.318e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_02 | 8192 | 1.318e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_03 | 8192 | 1.318e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_04 | 8192 | 1.318e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_05 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_06 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_07 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_08 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_09 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_10 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_11 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |
| ibm_kingston_dynamic_pub_12 | 8192 | 1.318e-05 | 0.00025 | 0 | 0 |

Job `ibm_kingston/dynamic/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 8192 | 9.316e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_02 | 8192 | 9.316e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_03 | 8192 | 9.316e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_04 | 8192 | 9.316e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/1` adds 2.3 seconds of modeled overhead.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family folded-qpe \
  --objective precision_at_budget \
  --cost-scenario latency_stress:4.6:60.0 \
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 60 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 4096 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 120.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family folded-qpe \
  --objective precision_at_budget \
  --cost-scenario latency_stress:4.6:60.0 \
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 8192 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 60 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192,16384 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 4096 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 120.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-12T014450.672483Z \
  --approved-record-sha256 e43c3e5bca12795a77d4148ff958735354271635430e2114f3b10233f9032d98 \
  --submit
```
