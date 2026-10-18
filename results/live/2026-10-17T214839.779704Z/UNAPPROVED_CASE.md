# Unapproved QPU case: n21-feedback-encoded

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-90112` at 90112 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-17T214839.779704Z`.
- [record.json](record.json) SHA-256: `d9cafa66bcdb83cc7e4e3f0bc78225a320042d75cd5706d93ccb7f15ab68f08c`.
- [isa.qpy](isa.qpy) SHA-256: `67d46b5a181f387e9b9a808add6144601594e8f3858db9fab7fb269ced399bfb`.
- Experiment source digest: `2ff9fe9c2eff72176e4df751ad195812b7c12414c261f48d93179be2d569e657`.
- Source commit: `5d1f58c11c102463d015cac8c58399fe7b69feeb`; sources_modified=`false`.
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

The model starts every active qubit with a declared excitation of 0.01 (`--prep-excitation`): the exact law and its sampled falsifier both apply that initial bit flip, a planning assumption until a state-prep-control run measures it at the run's repetition delay.

Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, replica correlations, and calibration drift can change the contrast. Calibration-based Aer simulation supplies a conditional model and power admission. Future hardware observations measure the actual contrast and model residual. A failed directional test leaves the stated hardware distinction unresolved; the case does not convert a simulated power calculation into a measured hardware guarantee.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| n21_encoded_feedback | `[0.375, 0.25, 0.125, 0.25]` |
| n21_encoded_no_feedback | `[0.375, 0.125, 0.125, 0.375]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| n21_encoded_feedback | ibm_kingston | 2026-10-17T14:35:51-07:00 | 20261011 | `[73, 71, 74, 70, 58, 79, 72]` | `[[105, 125, 104, 126, 124, 106, 117]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "group_replica_mappings": {
    "n21_encoded_feedback": [
      {
        "58": 124,
        "70": 126,
        "71": 125,
        "72": 117,
        "73": 105,
        "74": 104,
        "79": 106
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

The noise model predicts 0.0307314410552 from the exact branch-resolved law (dynamic_density), so no finite-simulation allowance applies; each replica's exact law lies within 0.00334115960818 of its 65536-shot sampled marginal, inside the simultaneous radius 0.00750252180719. The endpoint's exact contrast 0.0307314410552 sits 0.00337195249949 from its sampled estimate 0.0341033935547, inside the contrast's own Bernstein radius 0.0200443010341 at tail 0.00333333333333; a model bias smaller than that radius passes this check unseen.

At alpha 0.05, the two-sided confidence half-width is 0.0173105374424; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0162024578441 (null 0 plus one-sided radius 0.0162024578441). The admitted alternative effect is 0.0307314410552, with conditional target power 0.8 and lower-tail radius 0.0143131005321. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 0 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Confidence and detection radii also take the empirical-Bernstein radius at its share of alpha where smaller; the empirical-Bernstein section below states the split, the planned variances and the radius each PUB reads. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

### Empirical-Bernstein confidence and detection radii

Each opted-in endpoint reads, per PUB, the smaller of the data-free radius and the empirical-Bernstein radius, preregistered here and in record.json `empirical_bernstein`.

- Source: A. Maurer and M. Pontil, Empirical Bernstein Bounds and Sample Variance Penalization, COLT 2009, arXiv:0907.3740v1, Theorem 4 (i.i.d. scores in [0, 1], n >= 2) and Theorem 10 (4).
- Inequality: one-sided at tail d: mean - sample mean <= sqrt(2 V_n ln(2 / d) / n) + 7 R ln(2 / d) / (3 (n - 1)), V_n the sample variance with denominator n - 1 and R the per-shot score range; the two-sided radius takes d / 2 per side, ln(4 / d).
- Alpha split: each opted-in endpoint's confidence tail (alpha minus any covariance falsifier tails) splits equally: half to the data-free radius (Hoeffding, or the declared covariance radius where smaller), half to the empirical-Bernstein radius; each PUB reads the smaller, and the union bound over the two methods and over PUBs keeps coverage at alpha.
- Collection variance: each PUB score Y = sum_k w_k s_k reads V_n(Y) <= n / (n - 1) (sum_k |w_k| sigma_k)^2 with sigma_k the plug-in standard deviation of replica score s_k from its outcome frequencies: exact for one replica, valid for any within-shot dependence.
- Planning variance: each modeled replica standard deviation rises by Theorem 10 (4)'s allowance R_k sqrt(2 ln(K / t) / (n - 1)) at t = variance tail / PUBs, K replica scores per PUB; the plan spends the variance tail from its power miss probability, so a variance above plan costs power and never coverage.
- Scope: endpoints whose per-shot scores are bounded and i.i.d. over shots within a PUB, the conditions the Hoeffding radius already requires; power radii stay data-free.

| Endpoint | PUB | Shots | Score span | Planned variance | Detection: data-free | Detection: empirical Bernstein | Detection: read | Two-sided: read |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| n21_encoded_feedback_contrast | ibm_kingston_dynamic_pub_01 | 90112 | 2 | 0.545853 | 0.00986191 | 0.00810411 | 0.00810411 | 0.00865834 |
| n21_encoded_feedback_contrast | ibm_kingston_dynamic_pub_02 | 90112 | 2 | 0.54505 | 0.00986191 | 0.00809835 | 0.00809835 | 0.0086522 |

Alpha split for `n21_encoded_feedback_contrast`: 0.05 = falsifier tail 0 + data-free tail 0.025 + empirical-Bernstein tail 0.025. The planned two-sided half-width is 0.0173105 against 0.0197238 without the opt-in.

The planned detection radius is 0.0162025 against 0.0180968 under the data-free rule at the full alpha; the power radius 0.0143131 runs at tail 0.199, the miss probability 0.2 less the variance tail 0.001 (without the opt-in 0.0142975). The rejection threshold above reads the planned variances; collection recomputes each PUB's empirical-Bernstein radius from the measured frequencies and rejects only when the estimate exceeds the null plus the collected detection radius. A sample variance above its planned upper limit widens that radius and costs power, never coverage: the interval keeps its alpha whatever the variance.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/dynamic/1 | 2 | 180224 | 61.52521088 | 71 |

The cost model predicts 61.52521088 seconds. The per-job service ceilings sum to 71 seconds against an invocation cap of 120 seconds. The global reserve is 60 seconds; the saved quota reports 266 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 90112 | 6.8588e-05 | 0.00025 | 0 | 2e-05 |
| ibm_kingston_dynamic_pub_02 | 90112 | 6.8652e-05 | 0.00025 | 0 | 0 |

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
  --shots 90112 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 71 \
  --replica-floor 0.55 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 81920,90112,98304,106496,110592,114688,118784,122880,131072,139264 \
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
  --prep-excitation 0.01 \
  --empirical-bernstein \
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
  --shots 90112 \
  --seeds 8 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 71 \
  --replica-floor 0.55 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 81920,90112,98304,106496,110592,114688,118784,122880,131072,139264 \
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
  --prep-excitation 0.01 \
  --empirical-bernstein \
  --out ../results/live \
  --approved-record ../results/live/2026-10-17T214839.779704Z \
  --approved-record-sha256 d9cafa66bcdb83cc7e4e3f0bc78225a320042d75cd5706d93ccb7f15ab68f08c \
  --submit
```
