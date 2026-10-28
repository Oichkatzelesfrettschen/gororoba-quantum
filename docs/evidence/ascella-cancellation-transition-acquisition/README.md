# Ascella cancellation and dimension-six acquisition case

The acquisition measures realized cancellation, leakage, routing and transition distributions on
`qpu:ascella`. A local matrix calculation establishes the requested laws; hardware determines the
realized distributions, compiled meshes, repeatability and execution duration. The
[acquisition procedure](../../runbooks/quantum-experiment-acquisition.md) and
[conformance evidence](../quantum-experiment-conformance/README.md) supply the source operators.

## Frozen acquisitions

The [campaign](campaign.json) binds five separately timed cancellation jobs followed by one packed
dimension-six pilot. Every job uses the same twelve-mode, 342-operation template, one photon in input
mode zero, an explicit empty mitigation list and a minimum of one detected photon. Every setting
retains all twelve outputs. The original operator cases and their seed-allocation files retain their
bytes. The [request builder](../../../scripts/ascella_experiment_request.py) copies their full operators,
parameters and registered compilation seed identities into successor cases.

| Job | Settings in the job | Requested herald law | Accepted samples | Detected-shot cap | Credit ceiling |
|---|---|---|---|---|---|
| Dark cancellation | dark | 0 | 65,536 | 131,072 | 1.131072 |
| Bright control | bright | 1 | 65,536 | 131,072 | 1.131072 |
| Repeated bright control | bright-repeat | 1 | 65,536 | 131,072 | 1.131072 |
| Repeated dark cancellation | dark-repeat | 0 | 65,536 | 131,072 | 1.131072 |
| Mutation fixture | fixture | 1/2 | 65,536 | 131,072 | 1.131072 |
| Dimension-six pilot | six computational identity inputs, then six Fourier-to-chirped inputs | identity or 1/6 per logical port | 65,536 each | 131,072 each | 1.131072 |

Each cancellation job contains a one-entry `ComputationIterator`. Separate jobs permit their execution
envelopes to establish the requested `+, -, -, +` arm order. The twelve-setting pilot uses one iterator;
its returned ordinal identifies settings, while physical execution chronology remains unestablished.
Repeated seed identifiers request the same compilation. Matching returned `computed_circuit` and
`computed_input` records establish whether the repeated jobs actually used identical implementations.

The total target is 1,114,112 accepted events, with a summed detected-shot cap of 2,228,224.
The six-job ceiling is **6.786432 credits**. The arithmetic uses the user's stated one-credit base charge,
the [retained billing rule](../../runbooks/quandela-credit-optimization.md) and the current
`10^-6` credits per billed shot. Iterated jobs bill the largest iteration shot cap rather than their
sum; every setting still receives its own sample target and shot cap. A live tariff change above the
ceiling refuses submission. Additional independent meshes, cross-day repeats and the full campaign
require separately frozen successors; the screening cohort keeps a single analysis family.

## Readiness, account limits and duration qualification

The [initial observation](provider-observation.json) recorded calibration. The subsequent
[availability observation](available-observation.json) records `available` on the offer and processor,
zero running jobs and zero queued jobs. Every submission refreshes those observations through the
guarded runner. The runner admits `available` only. The account permits one running and one queued job;
the operator collects each cancellation job before submitting its successor.

The [account-access observation](account-access-observation.json) records HTTP 404 from the documented
account and offer routes, plus an empty connected-browser inventory. The job-token usage report measures
consumption, rather than remaining account credits. Remaining credits and exact expiry are therefore
unknown. The provider documentation describes a monthly allowance and calendar-month reset, with the
exact reset timezone unestablished; those statements establish neither a current balance nor a precise
expiry. The acquisition stays within the six-job ceiling even while account balance remains unreadable.

**The first dark-arm job is a duration and result-interface qualification.** Its duration is unknown
before execution. Perceval's detected-shot estimate supplies neither a compilation-time forecast nor
a detection-rate forecast. Retained successful jobs used a 34-operation template and do not establish
the duration of the larger 342-operation template. The verified provider limit is 300 seconds per job;
every case requests that stop limit. The legacy CLI argument `--expected-seconds 300` carries the
conservative planning limit for compatibility and is explicitly a ceiling, rather than a forecast.
The six requested stop limits sum to 1,800 seconds; queueing and collection add wall-clock time.

Collect the first dark result before continuing. Require a completed acquisition, 65,536 attributed
accepted events, echoed parameters and seed, returned mesh/input reconstruction, and a finite measured
duration within 300 seconds. An initialization failure, missing result or exceeded limit stops the
sequence for diagnosis. A failed optical-performance requirement remains useful diagnostic data and
retains the bright and mutation controls as the next acquisitions when the interface works.

The pilot also qualifies twelve-setting packing on the larger template. Its conservative sizing model
is twelve times the largest measured cancellation-job duration plus 60 seconds of reserve. Submit the
packed pilot only when that model is at most 300 seconds. The model is a prospective admission rule;
different phase settings can change runtime. A model above the limit requires a successor partitioned
case before acquisition, rather than silently changing the frozen iterator.

## Scientific decision rules

The digest-bound [qualification profile](qualification-profile.json) freezes one 95% simultaneous
Clopper-Pearson family with 243 endpoints: seventeen times twelve ports plus one combined invalid
photon-number category, seventeen nonlogical/invalid leakage aggregates, and five herald probabilities.
Missing and failed settings remain in that family. Coverage assumes independent identically distributed
Bernoulli events within each setting; histogram aggregation does not establish that premise.

At 65,536 events, the worst interval half-width is 0.007257. A zero-event outcome has upper bound
0.0001401. These values establish a conditional precision design, rather than device performance.
All denominators include returned invalid-photon events. `nb_shots_used` counts detected events;
incident source pulses and undetected-photon loss require their own counters.

The profile's thresholds are prospective scientific requirements:

| Quantity | Qualification requirement |
|---|---|
| Requested versus returned-mesh output distribution | Total variation at most 0.01 |
| Each dark herald | Simultaneous upper bound at most 0.02 |
| Each bright herald | Simultaneous lower bound at least 0.98 |
| Fixture herald | Entire interval within [0.47, 0.53] |
| Each repeated dark/bright difference | Entire derived difference interval within [-0.01, 0.01] |
| Each identity pilot setting | Correct-output lower bound at least 0.95 |
| Each cross-basis pilot setting | Observed-versus-returned-mesh total-variation upper bound at most 0.05 |
| Each setting's nonlogical/invalid leakage | Upper bound at most 0.02 |

For category intervals `[L_i,U_i]` and reference probabilities `q_i`, use
`min(1, sum(max(abs(L_i-q_i),abs(U_i-q_i)))/2)` as the total-variation upper bound, including the
invalid category with reference probability zero. Derived bounds reuse the frozen intervals.
The signed dark-minus-bright contrast is `(dark-bright-bright_repeat+dark_repeat)/2`.
Report contrast estimability, returned-mesh equality, temporal ordering, optical qualification and
conditional precision separately. Chronological order alone supplies no claim of exact drift cancellation.

The full 54-setting campaign becomes eligible only if all twelve pilot settings qualify and every
required pilot result is complete. A failed or incomplete pilot stops automatic expansion. Repeating
until qualification would require a separately specified sequential decision rule. The full campaign
uses a fresh confirmation cohort and its own confidence family. Intensity measurements test finite
transition distributions; they establish neither a universal dimension-six MUB bound nor a spacetime effect.

## Replay and operator commands

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 GOROROBA_WORKERS=4
"$PYTHON" scripts/ascella_experiment_request.py --check
"$PYTHON" scripts/ascella_experiment_request.py --validate
"$PYTHON" scripts/ascella_experiment_request.py \
  --prepare docs/evidence/ascella-cancellation-transition-acquisition/README.md
```

`--prepare` writes the first review-bound successor under `results/quandela/runs/`. Only the first dark case
receives ready admission. The cohort guard creates later successors after checking their prerequisites;
prospective cases stay outside the retained acquisition census. The manifest records the
written case's SHA-256 and frozen packed-manifest SHA-256. A different existing file causes refusal.
The [local validation](local-validation.json) reconstructs all seventeen complete operators using the
provider SDK and checks exact per-iteration budgets. The guarded `qd_platform.py plan` command captures
the exact serialized request without job creation. The guarded `submit` command binds a fresh plan to
its retained body and submission checkpoint. The
[cohort guard](../../../scripts/ascella_experiment_run.py) admits the next case only after every
predecessor supplies the complete attributed target and a valid duration. The guard checks the pilot's
packing model, binds a prerequisite receipt and compares the fresh serialized body with its preflight.
The comparison excludes only the SDK's process UUID and validates that UUID's shape; receipts retain
both complete request bodies and their full hashes.
Invoke the guard with `--submit-next --approval 'USER INSTRUCTION'`; its approval text records the user's
instruction to run the five cancellation jobs followed by the twelve-setting pilot.

Collect lossless raw bytes with `qd_platform.py collect` before analysis. The dedicated acquisition
analyzer verifies per-iteration attribution and the frozen profile before assigning scientific labels.
The research registry and provider inventory receive the retained acquisitions through the standard
research-state procedure. Raw files and original analyses retain their bytes; revised analyses use
successor filenames.
