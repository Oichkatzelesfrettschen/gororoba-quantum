# Evidence closure and acquisition decisions

The [derived evidence view](../evidence/evidence-closure/README.md) reconciles
the four requested commits and two explicitly labelled supplemental PR heads.
Its [pins](../evidence/evidence-closure/pins.json) are immutable inputs, not
moving branch names. The authoritative registry remains
[research_state.json](../state/research_state.json). No historical acquisition,
analysis, approval receipt, registry or frozen readout is replaced by the view.

## Replay before acquisition

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B scripts/evidence_closure.py --check --fetch-pins
"$PYTHON" -B -m pytest tests/scripts/test_evidence_closure.py -n 0
```

`--fetch-pins` obtains missing Git source commits. It contacts no hardware
provider. Omitting it requires all commits already present. `--write` explicitly
regenerates the view. A shallow checkout needs the source commits before replay.

Reconciliation keys executions by `(provider, job_id)`. Every directory, source
commit, schema and observation version remains visible. A missing observation
is not zero. A missing acquisition on one branch that is retained on another
is cross-branch coverage, not evidence of missing physical data. A semantic
delta is flagged for adjudication; the flag does not prove a logical
contradiction. Main is not overwritten by whichever branch is newer.

The denominator census covers registry-bound executions plus the pinned IBM
service retention audit. Planned-observation counts are the design slots of
these submitted jobs, not a sum over every overlapping unsubmitted proposal.
It separately classifies every tracked IBM `record.json` outside registry-bound
runs. Legacy records without dispatch metadata remain unresolved. No success
rate is computed over these directories.

Provider-reported completed shots, returned samples, eligible estimator trials
and exclusions are different objects. Counts from multiple classical registers
of one PUB never multiply its trial count. Quandela top-level `shots` can be an
iteration ceiling; `shots_used` or the complete `nb_shots_used` sum supplies the
retained total. Do not convert an absent effective mitigation policy into `[]`.
Do not interpret `physical_perf` as independent coherent-input acceptance.

## Distinct Belenos cases

The [opening-budget/load-history record](../archive/handoffs/belenos-first-load-hypothesis-2026-10-18.md)
concerns mesh `29dc6ef8`. The observed small/large opening split is descriptive;
single and iterated payloads appear on both sides. Recovery after another mesh
load is not prevention. The no-match search constrains the 135 declared complete
mesh candidates; its missing per-mesh replay artifact remains an explicit gap.
It excludes neither partial configurations nor unrecorded states.

The transform-setting mismatch concerns job
`e99c049c-b9c1-4663-bbd0-e57e59bb6993`, observation indices 6, 14 and 22.
The derived snapshot recomputes own-request and immediate-predecessor distances
from its retained eligible mode counts. This is a count-level reconciliation,
not a complete raw-provider-response replay. Similarity is established;
predecessor causation is not. Do not join it to the opening-entry case.

## First acquisition candidate: predecessor intervention

The generated [candidate](../evidence/evidence-closure/fourier-candidate.json)
retains the exact historical target setting and its parameter hash, the returned
compiled target hash, and four distinguishable predecessor settings. Their
minimum pairwise requested TVD is checked, rather than assumed. It proposes two
counterbalanced invocation orders. In every paired invocation the unchanged
target is the second iteration. Each order also includes one target-only
invocation. Target-only means no earlier iteration within that invocation; it
does not establish a clean provider state and changes the payload form.

This is a written **draft, not an admitted executable case**. The conditional
planning calculation uses 40,000 eligible events per setting and simultaneous
coverage of 18 empirical distributions at family alpha 0.05. For 24 outcomes,
the subset-Hoeffding union bound is

`epsilon = sqrt((24 ln(2) + ln(18/alpha)) / (2 n))`.

The error radius of an empirical-to-empirical TVD comparison is at most
`2 epsilon` under that model. The minimum relevant history effect is 0.1.
These calculations require independent trials and a qualified physical
observation chain. Returned service samples do not establish either premise.
The actual effective sample size, current layout/timing, shot/seconds/credit
ceilings, reserve and approval remain admission blockers. No IBM time is
allocated to this photonic candidate.

Freeze the target seed, source mode, logical operation, parameters and effective
processing. Compare the returned target compilation against the frozen identity
for every target occurrence. A changed compilation stops the comparison as an
invalid intervention; do not label it drift. Confirm that predecessor controls
themselves change as intended. Retain execution order, full output categories,
and requested, returned-model and observed laws separately.

Support predecessor dependence only when a simultaneous lower bound on a
counterbalanced target difference exceeds 0.1. Support target invariance only
when simultaneous upper bounds stay below 0.1 across distinct responding
predecessors while the target remains wrong. Otherwise stop inconclusive within
the written budget. Neither outcome separates stale applied controls from result
association without provider-side execution evidence. Do not retry automatically.

## Frozen and terminal cases

| Case | Retained scope and disposition | Remaining boundary |
| --- | --- | --- |
| Opening-budget anomaly, existing observations | Objective established within scope: the named wrong-response observations and recovery are descriptive facts | Budget-only causation and universal wrong configuration remain unidentified; the new intervention is a separate case |
| Transform-setting mismatch, existing fixed-order repetitions | Objective established within scope: repeatable wrong output and predecessor resemblance | Causal discrimination is the separate unsubmitted candidate above |
| Tuna Pauli series | Protocol inadmissible for its intended stationary inference: preserve the frozen drift refusal and emit operational diagnostics only | No favorable error-rate direction, subset or pilot rule reopens the inference |
| Tuna order pilot | Objective established within its descriptive scope | Scientific continuation is not admitted; assignment inversion remains sensitivity |
| Three canceled BDSC diagnostic attempts | Protocol inadmissible as acquisitions in a completed measurement sequence | Retain each job identity and cancellation separately; never concatenate them with later jobs |
| BDSC diagnostic second block | Pending under PR #350's frozen case; no terminal outcome is fabricated | The supplied pinned tree has block 1 only. A qualified operator must retain block 2, perform the frozen matched check, and run the unchanged readout |
| Nine-job Tuna successor | Unsubmitted proposal; no acquisition outcome exists | Its own admission, covariance analysis, current backend/queue/budget checks and approval apply |

The ledger above closes completed observation scopes. It does not manufacture
a scientific endpoint for an unfinished or unsubmitted case. When such a case
ends, record exactly one of: objective established within scope; specified
alternative supported; implementation route unavailable; inconclusive within
budget; protocol inadmissible. State which objective and population the outcome
closes. A case ending inconclusive does not automatically authorize another job.

The successor's original matched-response proposal retains its bytes and its
own endpoint. Publish raw science probabilities first and any assignment
inversion as labelled sensitivity. An unqualified correction cannot be promoted
to a physical-effect certificate by inheriting a pilot or stopped-series rule.
Its frozen inference still needs its separately specified admission; this
reporting rule does not retroactively rewrite the preregistration.

## Support withdrawal and numerical sensitivity

The snapshot lists declared physical and analytical support for every established
hardware claim at each source. Removing one declared root makes that stated
support incomplete. It does not prove the claim false. Calibration identities,
preparation maps, shared analysis closures and missing assumptions remain
qualification gaps, not implied independence.

Numerical re-estimation is separate. The raw Tuna visibility sensitivity removes
all scores of each shared-shot Latin job together before recalculating the raw
bright-minus-dark fraction. This does not re-adjudicate the registered calibrated
contraction endpoint. Every other claim-specific endpoint deletion contract
that is unavailable remains labelled unavailable. Session/calibration/family
leave-one-out cannot be inferred from job leave-one-out or from directory names.

## Future decisions and cancellation authority

Before submitting a future case, retain an `acquisition-decision-v1` record and
validate it with `scripts/acquisition_decisions.py decision CASE.json`. It must
state distinct alternatives, discriminating observable, trial definition,
observation chain, processing, dependence and qualified power/covariance model,
current layout/timing identity, shot/seconds/credit ceilings, reserve, all five
terminal decisions, and the end-without-retry condition. This local preflight
grants no approval and does not alter a provider state. Existing frozen
acquisition runners are not silently retrofitted by this standalone validator.
They still require their own explicit approval receipts and guards.

The reported 117 remaining IBM seconds belong to the dated retained account
observation. They are not a current balance or an allocation. Leave the amount
unallocated and refresh it only when an independently admitted case needs it.

A shared queue is not cancellation authority. Before any cancellation, obtain
explicit authority naming the provider and exact job ID and bind it to the
original submission receipt SHA256. Validate the
`job-cancellation-authority-v1` record with:

```sh
"$PYTHON" -B scripts/acquisition_decisions.py cancellation AUTHORITY.json \
  --provider PROVIDER --job-id JOB_ID --submission-receipt SUBMISSION.json
```

No worker cancels another worker's job because it appears in an account-wide
queue. The standalone check verifies the recorded scope, not the authenticity
of user approval; the acting operator remains responsible for that evidence.

## Physical interpretation and sources

The [algebra rules](../notes/algebra_circuit_rules.md) separate mathematical
prediction, physical implementation and recorded observations. A returned
model can match a request while the observations do not. Report separately
`TV(returned, requested)` and `TV(observed, returned)`; average neither into one
fidelity. Conditional probabilities need qualified acceptance on coherent inputs.
Equal basis survival alone does not establish a scalar acceptance effect.

The retained [detector tomography](../notes/papers/0807.2444.md),
[gate-set tomography](../notes/papers/2009.07301.md),
[drift analysis](../notes/papers/1907.13608.md) and
[certificate sources](../notes/quandela/bdsc_sources.md) delimit what the
preparation frame, likelihood and instrument model must establish. None converts
a repeated service histogram into a physical-effect certificate by itself.
