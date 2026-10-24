# Evidence-map resolution and closure requirements

This design maps the sedenion-derived quantum evidence infographic to the
repository work it actually requires. It is not a new claim registry, a
hardware certificate, or permission to submit an experiment. The authoritative
claims remain in [research_state.json](../state/research_state.json); the
[research-state validator](../../scripts/research_state.py) owns their schema.

The inspected main snapshot is
`4e56b8097e8227c757cff80df30e6a7ccb285fb7`. The infographic is a dated secondary
summary, not evidence of new physical execution. Its eight lettered
conjectures are not eight confirmed software defects. Proven identities,
observed discrepancies, implementation bugs, and unanswered physical questions
require different closure evidence.

The [disposition record](../evidence/evidence-map-resolution/disposition.json)
identifies the source pins, status, next action and closure condition for every
item below. The [targeted checks](../evidence/evidence-map-resolution/checks.json)
recalculate only the explicitly listed extracted records. Their
[validation boundary](../evidence/evidence-map-resolution/README.md) excludes
full raw-provider replay, account refresh, live hardware and repository-wide CI.

## Corrections completed by this change

The canonical [BDSC source map](../notes/quandela/bdsc_sources.md) now makes the
certificate's separation premise explicit: `F >= 0` and
`0 <= a_U < gamma_L` precede `sin^2(theta_max) <= a_U / gamma_L`.
The angle is between the frozen rank-four target and the four lowest-response
eigenvectors; it is not inferred from a few dark counts.

The Clements source now supplies ideal universal interferometer synthesis,
not a promise that the current cloud interface preserves the requested full
transformation or that physical loss is scalar.

The GST paragraph now distinguishes changing numerical meshes from changing
physical effects. Different unitaries can implement the same measured effect.
A self-consistent fit requires an applicable model and has gauge freedom; it
cannot manufacture one common physical instrument from arbitrary label-dependent
operations or independently fix the mathematical target frame.

The infographic's six-state label, "FAILED UNDER CURRENT CONDITIONING", needs
this qualified reading: retained response residuals disagree with the ideal
linear prediction; the physical fixed-effect claim remains unqualified while
preparation, acceptance, processing, and the sampling law are unresolved. An
exploratory residual is not automatically a confidence-qualified falsification
of the physical measurement. Do not assign preparation error or coherent phase
error as the unique cause.

The graphic's "98 established" headline is a quoted snapshot, not a freshly
regenerated count in this change. Report class, scope, source commit and support
roots beside any later count. The registry already distinguishes evidence classes;
that distinction does not need to be invented again.

## Work disposition

| ID | Subject | Repository action | Evidence that closes the action |
|---|---|---|---|
| EM-01 | Exact target and finite determinant checks | Preserve existing exact target, contracts and negative controls | Existing bounded exact replay; no new hardware claim |
| EM-02 | Certificate preconditions in summaries | Correct the source map; require separation and qualified confidence | Explicit premises and alignment scope, now stated |
| EM-03 | Ideal mesh theorem versus cloud behavior | Correct the source attribution | Ideal synthesis no longer asserted as hardware qualification |
| EM-04 | Common-effect and GST overclaim | Correct the source map and preserve M2/M4 blockers | Model and gauge boundary, now stated; no fabricated physical closure |
| EM-05 | Two Belenos anomalies conflated across branches | Keep separate job/mesh identities and pins | Count-level evidence for each; a shared cause remains unestablished |
| EM-06 | Transform mismatch resembles its predecessor | Finish the retained raw-to-analysis replay; design a separate predecessor intervention | Held-fixed target across changed predecessors and target-only control, with valid records |
| EM-07 | Opening-budget association on mesh 29dc6ef8 | Preserve descriptive scope; retain the candidate sweep and matched controls | Counterbalanced opening budgets, actual timing, recovery versus prevention kept separate |
| EM-08 | Sum rules and observation semantics | Keep count-level diagnostics distinct from physical-effect inference | Admitted preparation, acceptance and processing model; simultaneous decision rule |
| EM-09 | Phase and seed-ensemble explanations | Use the existing diagnostic and genuinely phase-sensitive controls | Matched compilations, state-independent seed weights or bounded alternatives; specified recombination |
| EM-10 | Tuna Pauli series | Preserve the registered stationarity refusal | Retained stop diagnostics; a successor needs a new approved case |
| EM-11 | 24 ledger jobs described as unretained | Join provider IDs across pinned branches; do not recount them | Equality of the 24-ID sets and integrated retention coverage |
| EM-12 | Registry branches and evidence classes | Reconcile schema-aware records through reviewed PRs | No lost claims/acquisitions, semantic conflicts explicit, fresh render on integrated tree |
| EM-13 | Denominator and support-concentration gaps | Add derived corpus reports using existing adapters and dependency fields | Unique executions; planned/returned/eligible units separate; shared support roots and coverage stated |
| EM-14 | Current CI/numerical replay failures | Rely on the #358 repair, merged into main, rather than duplicate it | Reviewed head, required gates and native-environment qualification; not a PR-body assertion alone |
| EM-15 | Provider-dependent capability and hardware certificate | Keep M2-M4 unresolved until supported | Bound provider evidence and a frozen qualified experiment; no source-code patch alone suffices |
| EM-16 | Mathematical frontier and future hardware spending | Keep frontier papers and proposals separate from physical validation | Explicit hypothesis, observation model, budget, and closure rule before execution |

The plan record [evidence-map-resolution](../state/plans/evidence-map-resolution.json)
owns the status, owner and receipts of the open items (EM-06 to EM-09, EM-11 to
EM-13 and EM-15); the disposition record supplies their context.
These IDs are work-item identifiers only. They do not replace registered claim
IDs, change a frozen verdict, or assert that an open question is refuted.

## Already implemented: do not reopen obsolete defects

At the inspected main, [bdsc.md](../notes/quandela/bdsc.md) and
[bdsc.py](../../gororoba_quantum/bdsc.py) already contain:

- the target/complement principal-angle theorem and its numerical successor;
- the global higher-eigenvalue census with separate low-direction findings;
- the approximate-acceptance range `0 <= F <= (1 + delta) I`;
- real and imaginary extra-null controls, the complex preparation bank, and
  independent target/complement confidence constructions;
- expected-count planning explicitly distinguished from probability of success;
- qualification blockers and a provider-contract record.

The [provider contract](../evidence/bdsc/provider_contract.json) has unresolved
or unsupported capabilities. This change neither edits that retained record
nor promotes any capability to supported. Completed requests do not by
themselves establish a raw-event law or a separately controlled preparation.

## Two anomalies, two experiments

The [first-load record](../archive/handoffs/belenos-first-load-hypothesis-2026-10-18.md)
owns the opening-budget association. Its stable wrong response is episode-scoped;
its 135-whole-mesh search is a reported bounded search whose per-candidate replay
needs retention. A nearest non-match does not identify a previous configuration.
Recovery after a switch does not establish prevention by a different opening.

The separate transform acquisition is provider job
`e99c049c-b9c1-4663-bbd0-e57e59bb6993`, setting
`transform-forward-imaginary-superposition-representative0`, observations
6, 14 and 22, retained in PR #352 at
`bc797e7d562faf751e3eb1af0bb2f6d084ad4f86`.
The count-level extraction gives total-variation distances above 0.996 from
its own requested distribution and below 0.035 from the preceding requested
distribution. Those observations establish resemblance, not predecessor causation.
Their existence on that branch is compatible with absence from another branch.
The requested, returned-model and observed distributions stay distinct.

Source record:
https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/bc797e7d562faf751e3eb1af0bb2f6d084ad4f86/results/hypercomplex/belenos-repeat-readout.json

Do not spend another job merely to narrow the uncertainty of the same wrong
histogram. A useful prospective case changes a discriminating variable while
retaining a target-only control, complete outcomes, source identity and an
approved ceiling. A new case is not authorized by this document.

## Evidence reconciliation and denominator requirements

Use `(provider, account_scope, provider_job_id)` to identify physical executions;
use non-sensitive account-scope identities already permitted by the repository.
Run directories, copied analyses and recollections are not new executions.

The targeted ledger comparison identifies the 24 IDs listed as unretained at
QI branch `bba9586549c9e17900229dd74705936cdcd64bbf` as the 24 retained jobs in
`results/quantum_inspire/runs/tuna17-quaternion-order-noise/pilot-summary.json`
on the inspected main. They total 393216 shots. This closes the identity
question in those snapshots; it is not a complete retention-adapter replay.
Do not rewrite the historical ledger snapshot or add the jobs twice.

Report each provider's own units: requested ceilings, completed provider shots,
returned samples, eligible outcomes, exclusions and charges. Unknown physical
attempt or acceptance denominators remain unknown. For each established hardware
claim, report physical jobs, sessions, calibration identities and compiled
implementations, and which of those differences the design actually tests.
Count-based diversity does not by itself establish independence.

Build the dependency report from existing `acquisitions`, `depends_on`,
`assumptions`, evidence digests and gate roles. Distinguish direct support from
transitive support and conjunction from alternative support. A replay of one
job is a second analysis, not a second physical replication. Withdraw one
support root in a sensitivity report without deleting its historical record.
Classify unbound IBM record directories before treating them as attempted jobs.

The stop in the pinned Tuna analysis is a reference change of
926 / 32768 = 0.02825927734375, exceeding its frozen 0.02 limit.
The analysis accounts for 27 records at 32768 shots and withholds science
inference. Preserve that outcome; do not lower the limit after observing it.

Source record:
https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/bba9586549c9e17900229dd74705936cdcd64bbf/results/quantum_inspire/bdsc_pauli_tuna_17_analysis.json

## Integration ownership

The resolution pass read three pull requests open at the time; each has
since merged into main under its own review and gates:

- #349 at `2f9168052148f1dce851dabbffbe41bc277ba025`, merged as
  `af209218e09d86710396e00f879d401827f2201a`: Tuna Pauli evidence and controls;
- #352 at `27e31f46554b99086cc8b0f235e7ce9d27967f0d`, merged as
  `b2eb6a6f36e8b6f7418c8d9615a239cb9ea645dd`: photonic conformance records;
- #358 at `d4a95cc3ee87512e42a1e97db86cf26c8291d523`, merged as
  `4250b062fc3f09870dd8c602a2658ed61e12658b`: numerical fitting,
  runner-image replay, case-schema selection, toolchain coverage and gate repairs.

Read every active review thread and the full diff before merging. Do not use a
historical test summary as a current-head clean review. No force-push, branch
merge, provider account read, QRNG draw or hardware submission occurs in this
resolution pass. A source-map correction does not merge branch-only evidence
into main or resolve #358's environmental validation obligation.

## Closure policy

Each unresolved work item has one of four next actions: offline replay,
reviewed integration, provider clarification, or separately approved physical
measurement. Close it only when its stated acceptance evidence exists.

A mathematical theorem remains a theorem under its hypotheses. An exact finite
replay proves only its finite contract. A diagnostic mismatch can motivate an
experiment without certifying a physical mechanism. An inconclusive or stopped
case is a legitimate end of its allocated experiment, not permission for an
automatic retry. A proposed theory paper remains a source for mathematical
questions, not validation of this hardware.

The research sources and their reading/authority boundaries remain centralized
in [bdsc_sources.md](../notes/quandela/bdsc_sources.md). The resolution does not
add or reclassify external literature.
