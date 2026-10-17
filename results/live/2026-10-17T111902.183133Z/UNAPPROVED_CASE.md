# Unapproved QPU case: n21-feedback-encoded

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-001-shots-131072` at 131072 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-17T111902.183133Z`.
- [record.json](record.json) SHA-256: `adf5a64a11c7bec9fe5e2eafa7cd02eddf99d36eb32062f0b1b69de34c0f9227`.
- [isa.qpy](isa.qpy) SHA-256: `dc623fbc22466768f6e874d5a15e2604e0d5ccec782a18d84fa3c0402a8426a4`.
- Experiment source digest: `e83c4b0855f883fd69ecc6ab8cf4237eb6250eed603be9d61d6b4640ab5c3144`.
- Source commit: `d47c3e2f8c7aac4e1581922d4c113c939b622f83`; sources_modified=`false`.
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

The encoded family runs the complete multipliers on a work register encoded by one uncontrolled linear map B (columns 2, 4, 5, 10, 17; coset 15265 of GL(5,2)/S_5): it prepares B^-1 |1> and applies the target-flip network of B^-1 f B each round, which leaves the phase register's law exactly that of n21-feedback while routing about a third fewer CZ (docs/evidence/linear_conjugation/). It changes the circuit, not the question, and carries the same order-recovery boundary.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_encoded_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_encoded_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| n21_encoded_feedback | ibm_kingston | 2026-10-17T03:41:37-07:00 | 20261011 | `[83, 81, 103, 80, 96, 84, 82]` | `[[105, 125, 107, 126, 106, 104, 117], [67, 69, 65, 70, 66, 57, 68]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 2,
  "group_replica_mappings": {
    "n21_encoded_feedback": [
      {
        "80": 126,
        "81": 125,
        "82": 117,
        "83": 105,
        "84": 104,
        "96": 106,
        "103": 107
      },
      {
        "80": 70,
        "81": 69,
        "82": 68,
        "83": 67,
        "84": 57,
        "96": 66,
        "103": 65
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### n21_encoded_feedback_contrast

Score terms (each member averages its recorded replicas):

- `n21_encoded_feedback`: sign +1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.
- `n21_encoded_no_feedback`: sign -1, labeled score vector `[0.0, 1.0, 0.0, -1.0]`.

The noise model predicts 0.0242298518361 from the exact branch-resolved law (dynamic_density), so no finite-simulation allowance applies; each replica's exact law lies within 0.00434684899956 of its 65536-shot sampled marginal, inside the simultaneous radius 0.00784704573556. The endpoint's exact contrast 0.0242298518361 sits 0.00352588546858 from its sampled estimate 0.0277557373047, inside the contrast's own Hoeffding radius 0.0206710646148 at tail 0.00333333333333; that radius bounds a model bias no tighter than itself.

At alpha 0.05, the two-sided confidence half-width is 0.0163541334328; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0150050436144 (null 0 plus one-sided radius 0.0150050436144). The admitted alternative effect is 0.0242298518361, with conditional target power 0.8 and lower-tail radius 0.00869085760207. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

Additional covariance upper-bound assumptions appear in the selected endpoint's `covariance_assumptions` in record.json and form part of the conditional guarantee.

The search-wide simulation error probability is 0.01 across 0 scored finite-shot marginals. Each per-PUB radius is the smaller of the Hoeffding radius, valid under arbitrary same-shot replica dependence, and the Cantelli radius under the declared covariance bounds; the falsifier section below names which radius each endpoint takes. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

### Replica covariance falsifier

The power admission above rests on the declared covariance bounds. Collection tests them on the retained shot-ordered replica registers before it applies them (n21_exact_planning.covariance_falsifier, preregistered here and in record.json `covariance_falsifier`).

- Statistic: biased sample variance over shots of the weighted replica score sum Y = sum_k w_k s_k of one declared bound, w_k = term sign / replica count: the projection w' Sigma w the radius reads.
- Threshold: declared projection w' V w plus eps2 + D eps1, with D = sum_k |w_k| (max score - min score), s = sqrt(ln(4 / t) / (2 n)), eps1 = D s, eps2 = (D^2 / 4) s, n the PUB's shots and t = tail / number of declared bounds; total tail 0.001.
- Decision: every declared bound at or below its threshold applies the declared covariance to every endpoint; any bound above its threshold, or a bound whose shot-ordered registers are absent, analyzes every endpoint under the Hoeffding arbitrary-dependence radius.

| Endpoint | PUB | Weights | Shots | Declared projection | Allowance | Threshold |
|---|---|---|---:|---:|---:|---:|
| n21_encoded_feedback_contrast | ibm_kingston_dynamic_pub_01 | +0.5, +0.5 | 131072 | 0.275 | 0.029276 | 0.304276 |
| n21_encoded_feedback_contrast | ibm_kingston_dynamic_pub_02 | -0.5, -0.5 | 131072 | 0.275 | 0.029276 | 0.304276 |

Assumption in force for `n21_encoded_feedback_contrast`: the detection radius 0.0150050436144 equals the Hoeffding radius and needs no replica assumption; the power radius 0.00869085760207 rests on the declared bounds (Hoeffding alone gives 0.0118549). The declared bound reads: per-replica score variance at most 0.55; replicas independent: disjoint placements one CZ hop apart on the admitted graph and no inter-replica crosstalk in the noise model; collection tests the bound on the retained shot-ordered replica registers (n21_exact_planning.COVARIANCE_FALSIFIER) and analyzes under Hoeffding when it fails.

Under the Hoeffding fallback `n21_encoded_feedback_contrast` rejects its null only above 0.0150050436144; detection plus power radius 0.0268599 against the admitted effect 0.0242298518361 leaves the endpoint underpowered at these shots, and the collected analysis reports it so.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 2 | 262144 | 88.486131456 | 95 |

The cost model predicts 88.486131456 seconds. The per-job service ceilings sum to 95 seconds against an invocation cap of 120 seconds. The global reserve is 60 seconds; the saved quota reports 266 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 131072 | 6.8632e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_02 | 131072 | 6.8916e-05 | 0.00025 | 0 | 0 |

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
  --family n21-feedback-encoded \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 131072 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 95 \
  --replica-floor 0.55 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 110592,114688,118784,122880,131072,139264 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 2 \
  --model-shots 65536 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 120.0 \
  --model-method exact \
  --replica-variance-bound 0.55 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes. It plans only over the backends this record found eligible, so a backend whose queue or status changes after the dry run cannot enter the plan.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family n21-feedback-encoded \
  --shot-allocation uniform \
  --objective minimum_charge \
  --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 131072 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 95 \
  --replica-floor 0.55 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 110592,114688,118784,122880,131072,139264 \
  --replica-tiers 1,2,4 \
  --optimizer-candidates 2 \
  --model-shots 65536 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 120.0 \
  --model-method exact \
  --replica-variance-bound 0.55 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-17T111902.183133Z \
  --approved-record-sha256 adf5a64a11c7bec9fe5e2eafa7cd02eddf99d36eb32062f0b1b69de34c0f9227 \
  --submit
```
