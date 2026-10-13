# Unapproved QPU case: n21-orbit-feedback

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096` at 4096 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-13T074651.134471Z`.
- [record.json](record.json) SHA-256: `7282ba8b66a60741854a18e27b47f4fa308abd93cde5ba7333adad810b8456fe`.
- [isa.qpy](isa.qpy) SHA-256: `acf8774467585e2cd0346fa5c39f6c1e054d73af1994aa967877ac86dacbcea9`.
- Experiment source digest: `a8fca2f05f0439844d17e515e4f5362ad381cb157ba6d4d618c766284af9f685`.
- Source commit: `abd432b5f90a88e7703a0a057d87c6b51c7202a7`; sources_modified=`false`.
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

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_orbit_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_orbit_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Initial layout |
|---|---|---|---:|---|
| n21_orbit_feedback | ibm_fez | 2026-10-12T23:27:11-07:00 | 20261010 | `[2, 16, 3, 4]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "group_replica_mappings": {
    "n21_orbit_feedback": [
      {
        "2": 142,
        "3": 143,
        "4": 144,
        "16": 136
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### n21_orbit_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_orbit_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_orbit_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.21467590332; the simultaneous finite-simulation allowance is +/-0.0294191756341. The lower modeled value is 0.185256727686.

At alpha 0.05, the two-sided confidence half-width is 0.0925129492063; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0848813447338 (null 0 plus one-sided radius 0.0848813447338). The admitted alternative effect is 0.185256727686, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 6 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 2 | 8192 | 4.503713536 | 15 |

The cost model predicts 4.503713536 seconds. The per-job service ceilings sum to 15 seconds against an invocation cap of 15 seconds. The global reserve is 60 seconds; the saved quota reports 430 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 4096 | 9.02e-06 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_02 | 4096 | 8.996e-06 | 0.00025 | 0 | 0 |

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
  --family n21-orbit-feedback \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --simulation-threads 12 \
  --simulation-memory-mb 2048 \
  --optimize \
  --backends ibm_fez,ibm_kingston \
  --shots 4096 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 15 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 65536 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 15.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family n21-orbit-feedback \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --simulation-threads 12 \
  --simulation-memory-mb 2048 \
  --optimize \
  --backends ibm_fez,ibm_kingston \
  --shots 4096 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 15 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,8192 \
  --replica-tiers 1 \
  --optimizer-candidates 1 \
  --model-shots 65536 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 15.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-13T074651.134471Z \
  --approved-record-sha256 7282ba8b66a60741854a18e27b47f4fa308abd93cde5ba7333adad810b8456fe \
  --submit
```
