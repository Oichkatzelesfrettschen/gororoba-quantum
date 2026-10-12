# QPU execution and optimization roadmap

The approved folded-QPE ladder completes sixteen PUBs in two Kingston jobs
for 40 final charged QPU seconds. The [hardware report](../results/live/2026-10-12T055624.091217Z/ANALYSIS.md)
retains the scientific intervals, raw-shot replay, and component-level timing.
The runner uses installed CPU Qiskit Aer; custom CUDA work remains paused.
The next hardware case follows the measured model discrepancy and the shared
campaign ownership record, with separate approval for every changed design.

The [parallel-experiment literature synthesis](../literature/notes/quantum_experiment_parallelism.md)
connects packing, context controls, drift, and blocking to primary research.
Its [design-source note](../literature/notes/quantum_experiment_design_sources.md)
links the official execution and experimental-design manuals. Those sources
supply prior mechanisms and qualification gates for the candidate work below.

The [executed record](../results/live/2026-10-12T055624.091217Z/record.json)
records source `c6b8a79e8981` and the exact approved QPY. Historical N21 and
static evidence remains linked below. Each record retains its dependency
versions and source-modification flag. The tested environment uses Qiskit
2.5.2, Runtime 0.50.0, and Aer 0.17.2. Fresh calibration can change every
future layout, job allocation, duration, and admission decision.

## Execution queue and budget

| Scientific case | Job structure | PUBs | QPU seconds | Admission state |
|---|---|---:|---|---|
| Folded-QPE mechanism ladder | Two completed Kingston jobs | 12 + 4 | 40 measured; 39.632400 nominal forecast | Completed, collected, reusable evidence |
| N21 feedback diagnostic | Intended one dynamic job | 2 | New estimate follows successful redesign | Retained candidates fail statistical admission |
| [Static algebraic witnesses](../results/live/2026-10-11T203535.690679Z/STATIC_CASE.md) | Historical allocation uses two backends | 17 historical | Historical estimate about 23; fresh pricing required | Renew and reconcile overlap with ripple/rank-sector |
| [Ripple finite walk/box-kite comparison](../results/ripple/PREPARATION.md) | One prepared static Kingston job | 146 | 157.0873 nominal; ceiling 180 | Locally admitted; unapproved |
| [Rank-sector controls](../results/ripple/PREPARATION.md) | One prepared static Kingston job | 36 | 39.9347 nominal; ceiling 60 | Locally admitted; unapproved |

The completed folded case spends 40 seconds. The prepared ripple/rank subset
contains two independent jobs, totaling 197.0220 nominal seconds, 201.6220
stress-scenario seconds, and a 240-second aggregate service ceiling. Its
1,334 endpoint names and roles are disjoint; repeated historical Design C
members act as fresh-patch and neighboring-workload controls. The coordinator
excludes duplicate folded execution. Additional N21 and historical static
cases remain outside that admitted subset and require separate qualification
and overlap reconciliation.

The [shared coordination record](../results/live/qpu-coordination.json) names
one execution owner per family across `ibm_fez`, `ibm_kingston`, and
`ibm_marrakesh`. The settled account read reports 551 seconds remaining with
an empty pending-job list. The two proposed ceilings total 240 seconds;
one shared 60-second reserve leaves 251 seconds unallocated at that snapshot.
All three backends draw on the same rolling 600-second allowance. Multiple
QPUs can reduce queue contention; assigning duplicate experiments to them
adds charge and changes the calibration conditions.

Before any future submission, the coordinator refreshes usage and pending
jobs, reconciles accepted IDs, confirms the owner and question, and binds a
complete control family to its independently admitted backend. Scientific
identity includes endpoints, preparation, controls, precision, and the intended
replication question; a changed transpilation hash alone does not establish a
new question. The submitted QPY/manifests remain the exact execution identity.
A second machine receives existing raw data or a disjoint local analysis task.
Independent backend replication needs its own explicit scientific purpose and
approved case. The shared JSON file is cooperative coordination, not an
account-wide atomic lock; external submitters require the same handoff.

The [consumed folded case](../results/live/2026-10-12T055017.711575Z-prepared/APPROVAL.md)
uses 8192 shots per PUB, or 131072 submitted PUB-shots. Each job has a 60-second
service ceiling, and the invocation has a 120-second combined ceiling. Final
usage is 29 seconds dynamic plus 11 seconds static. The nominal prediction is
39.632399872 seconds; the declared latency-stress scenario is 45.543119872.
The 60-second quota reserve remains available. Queue delay and local CPU
preparation lie outside those QPU figures.

The service circuit-execution metrics total 35.571614464 seconds. Summed
scheduler durations plus the declared repetition delays give 35.572154368
seconds; the 0.000539904-second difference remains unattributed. Final charge
exceeds the service metric by 4.428385536 seconds. Scheduler
residuals include unseparated controller and initialization work; the aggregate
forecast error of +0.367600128 seconds does not establish the correctness of
every cost component. Future cases retain fresh Target and calibration reads.

The runner calls `Sampler(mode=backend)`. Its internal word `batch` denotes the
PUB list within one job; the runner creates zero IBM Runtime `Batch` contexts.
It records acceptance of the dynamic job and then submits the static job,
without waiting for the first result. Each job retains its complete controls.
Two jobs preserve separate static/dynamic contracts and option compatibility.

A real [Runtime Batch][modes] can group independent same-backend jobs and
parallelize classical preprocessing. Batch mode preserves separate job charges,
permits intervening calibration, and guarantees neither job order nor an
unchanging device. Implementing Batch requires mode-aware approval binding and
local API qualification. Two folded jobs remain two jobs after that change.
IBM's [execution-mode guidance][modes-faq] favors combining small compatible
jobs to avoid repeated overhead; a Batch wrapper alone supplies no demonstrated
reduction in charged QPU seconds.

## Cost decomposition identifies the largest lever

The selected folded ledger supplies these nominal components:

| Component | Seconds | Share |
|---|---:|---:|
| 250-microsecond repetition delay | 32.768000000 | 82.68% |
| Two modeled job overheads | 4.600000000 | 11.61% |
| Target circuit duration, including explicit reset instructions | 1.609039872 | 4.06% |
| Explicit classical-latency allowance | 0.655360000 | 1.65% |

The [IBM usage model][usage] includes circuit duration, repetition delay, and
job overhead. Eliminating every Target-circuit and modeled classical-latency term would
save only 5.71% here. Gate improvement still matters for fidelity, but shot design
and initialization delay dominate this experiment's throughput opportunity.
These percentages describe the retained modeled components. Implicit
initialization and scheduler residuals can change the physical shares.

## Precision choices use the existing optimizer

The retained case uses `precision_at_budget`: it buys stronger precision than
the hard 0.08 target. Twelve contrasts each receive alpha `0.05/12`. The existing
bounded interval has half-width `H(S) = 2*sqrt(log(960)/(2*S))` for uniform shots
`S`. More shots narrow statistical uncertainty; they leave systematic hardware
bias intact.

| Shots/PUB | Half-width | Nominal seconds | Stress seconds | Interpretation |
|---:|---:|---:|---:|---|
| 2048 | 0.081890 | 13.358100 | 18.285780 | Fails the 0.08 target |
| 2146 | 0.079998 | 13.777189 | 18.720549 | Derived minimum integer tier for 0.08 |
| 4096 | 0.057905 | 22.116200 | 27.371560 | Retained feasible candidate |
| 5494 | 0.049998 | 28.094630 | 33.573670 | Derived minimum integer tier for 0.05 |
| 8192 | 0.040945 | 39.632400 | 45.543120 | Selected precision-at-budget case |

The 4096-shot candidate saves 44.2% of nominal charge while meeting the existing
hard target. A finer 5494-shot tier saves 29.1% and meets a newly declared 0.05
target. The two derived rows use the retained cost ledger and interval formula;
they are candidate designs, not fresh dry runs. Neither reduction preserves
the selected 0.040945 precision. A new `minimum_charge` case explicitly records
the desired precision and the chosen integer tier before approval.

The CLI already accepts arbitrary positive integer `--shot-tiers`. A future
free planning action compares `minimum_charge` at 0.05 and 0.08 with the
retained stronger-precision plan. The case preserves all sixteen PUBs and all
twelve endpoints; the cost saving comes from declared precision, not deleted
controls. [QPU_OPTIMIZATION.md](QPU_OPTIMIZATION.md) defines the statistical
assumptions and full submit-free command surface.

## Initialization delay requires a fidelity constraint

IBM's [qubit initialization guide][initialization] warns that shorter
`rep_delay` increases state-preparation error. The production runner binds the
backend default; a tunable delay requires new policy, range checking, cost
accounting, and approval binding.

At unchanged circuits, shots, and overheads, the cost model gives:

| Hypothetical qualified delay | Nominal seconds | Stress seconds | Nominal reduction |
|---|---:|---:|---:|
| 100 microseconds | 19.971600 | 25.882320 | 49.61% |
| 50 microseconds | 13.418000 | 19.328720 | 66.14% |

These are conditional sensitivities, excluding the cost of qualification.
They establish neither supported live ranges nor acceptable hardware fidelity.
A delay pilot keeps initialization enabled, uses paired ground/excited-state
reset controls on the chosen qubits, tests successive-shot dependence, and
sets a tolerated preparation-error increase before sampling. Pilot shot counts
follow those error tolerances. Different repetition-delay settings need
separate job-level execution options, with their overheads and ceilings priced
explicitly. The planner admits a pilot only when its information value and
expected downstream saving justify its own QPU charge.

The general design criterion becomes minimum charge subject to precision,
reset-error, temporal-dependence, and scientific-control constraints. Extra
shots cannot repair a violated reset-error constraint.

## Native server-side dry-run access remains unavailable

Runtime 0.50 exposes [`Sampler.run(..., dry_run=True)`][native-dry-run]. The
[retained access probe](../results/live/2026-10-12T054229.702537Z/native-validation.json)
resolves that request through `mock_kingston` and receives
`QiskitBackendNotFoundError` before a job ID exists. The owner then approves
physical execution using passing local compilation/Aer checks and live guards.
The access failure supplies neither mock results nor a server cost estimate.

If access changes, native mock validation can check exact admitted QPY circuits
without physical execution. Returned randomized mock outcomes stay outside
fidelity prediction and scientific adjudication. Scheduled-time estimates,
CPU predictions, executed scheduler metadata, and final billing retain
separate provenance. The local dry-run mode remains submit-free.

## Dynamic-circuit fidelity uses native mechanisms

1. **Qualify `MidCircuitMeasure`.** IBM [recommends][dynamic] the `measure_2`
   instruction when the backend supports it because mid-circuit measurement
   has different tuning and overhead from terminal readout. Runtime 0.50
   imports the instruction; Aer 0.17.2 CPU omits it from its supported operation
   names. An admitted implementation therefore needs an explicitly verified
   local representation, instruction-specific Target duration/error handling,
   ideal-law tests, and rederived matching-delay controls. Silent substitution
   with terminal measurement would lose the physical distinction under test.
2. **Fit latency from executed schedules.** [Scheduler metadata][timing]
   captures controller broadcasting and branch determination that static
   scheduling omits. The collection path already retains those tables. Use
   the folded controls and shot-order results to distinguish scheduling,
   layout, drift, and measurement effects before changing the noise model.
   Circuit schedule time and billed QPU time remain separate quantities.
3. **Qualify explicit idle echoes.** IBM's [stretch guide][stretch] describes
   XX echoes on a work qubit during another qubit's conditional block. An
   echo can protect an existing idle window, subject to pulse alignment and
   measured benefit. Qualification checks ideal identity, resolved timing,
   unchanged experimental contrasts, and noise performance. Automatic Sampler
   DD remains outside the dynamic execution path; explicit scheduled echoes
   require their own implementation and evidence.
4. **Keep mitigation selective.** The broad [Sampler manual][sampler] allows
   some twirling outside conditional blocks. The retained Runtime 0.50
   samplomatic probe nevertheless rejects `if_else`, so that installed path
   remains disabled. Later static cases can compare native twirling or DD
   against a matched unmitigated reference at equal total charge. IBM warns
   that DD can hurt densely packed circuits and that standard ZNE adds roughly
   threefold overhead in its [mitigation guide][mitigation]. Estimator examples
   do not establish applicability to these Sampler diagnostics.

## Prioritize N21 signal improvement before more sampling

The [retained N21 case](../results/live/2026-10-12T020459.130482Z/record.json)
rejects every supplied hardware tier through 16384 shots. The two-PUB test
requires an effect above 0.075971 even at zero model-sampling error at that
largest tier. Retained noisy estimates lie below that threshold, while the
true modeled contrast remains uncertain. More CPU samples alone cannot admit
the retained tiers if the contrast stays fixed. Synthesis improvement is a
planning priority, rather than a necessity established by those estimates.

The [shared-predicate challenger](../results/local_compute/n21_shared_predicate/README.md)
reduces each controlled multiplier from 243 to 204 unrouted CX gates, a 16.0%
reduction, using native Qiskit KG24 synthesis and shared scratch computation.
The full controlled-permutation and clean-scratch checks report zero numerical
error. Production integration follows phase-sensitive mutation tests, identical
Target/layout/seed comparisons, routed native two-qubit counts, complete
schedules, and fresh CPU noise admission. Unrouted savings establish neither
physical savings nor a new modeled effect.

A useful planning relation connects fidelity to cost: at fixed score ranges,
alpha, power, and positive net effect after model allowance, the required shot
term scales as the inverse square of that net effect. Doubling that effect
therefore quarters the corresponding shot requirement under those assumptions.
The relation motivates reducing N21 circuit noise before buying samples; the
relation supplies no prediction that the challenger doubles the effect.

The diagnostic retains labeled outcomes and the exact feed-forward laws.
Two phase bits still yield zero verified order recovery. The hardware claim
concerns a distribution change, rather than successful N21 factor recovery.

## Mixed-job and preparation optimization

The [mixed-PUB client probe](../results/local_compute/mixed_pub_client/README.md)
returns ordered deterministic dynamic and static outcomes through one local
Runtime 0.50 client call with twirling and DD disabled. Removing one modeled
2.3-second overhead gives 37.332399872 nominal seconds for the executed
folded case, conditional on hardware compatibility and internal subdivision.
The production runner still separates intrinsic static/dynamic PUB kinds.
Supporting mixed jobs requires a separate job-policy identity through pricing,
approval, manifests, recovery, and collection. CPU success alone establishes
neither physical job subdivision nor saved charge.

The rejected stale-approval record retains 132.5 seconds of Aer batch timings;
its captured initial candidate pass adds a separate 70.7 seconds. The runner
rejects changed calibration/layout/QPY after those evaluations. An early stale-record check and a
prepared-process approval boundary can remove redundant host work while
preserving source, calibration, quota, QPY, and one-use guards immediately
before submission. That optimization addresses wall-clock preparation and
approval churn; billed QPU savings require a physical mechanism.

## Lower-priority statistical and orchestration work

Each folded archived arm supports three contrasts. Under equal per-shot cost
and fixed confidence allocation, minimizing the sum-of-Hoeffding radii permits
about 1.491 times the uniform shots for the archived arm and 0.717 times for
each other arm. Total shots fall about 8.96% at the same contrast radius.
Actual costs, integer tiers, and all twelve endpoints change that optimum.

The installed client-side Runtime blocks direct deployment: its
`executor_sampler.utils.extract_shots_from_pubs` rejects mixed shot counts.
A local two-PUB probe at 100/200 shots raises `IBMInputValueError` with
`All pubs must have the same number of shots`. Supporting unequal allocation
therefore requires grouping equal-shot PUBs into additional jobs, then updating
reservations, approval binding, and collection. A third folded job's overhead
can consume most of the theoretical gain. The [Runtime 0.50 implementation][shot-source]
takes precedence over broad per-PUB-shot wording in the manual.

Packing different required endpoints in one physical shot offers a separate
planning opportunity: amortize repetition delay while retaining each endpoint's
shot count and conservative precision bound. Endpoint independence is
unnecessary for the marginal bounds and their union. The
[family planner](qpu_planning.py) keeps folded members in separate PUBs on one
shared patch; N21 replica tiers repeat each arm inside its own PUB. Candidate
extensions include static witness companions to coherent controls and
same-rung folded labels on disjoint patches. A label-to-patch crossover would
preserve each label's complete ladder while testing layout effects; that
design changes the shared-patch contract and needs its own interpretation.

These candidates remain unimplemented. The
[retained packing adjudication](../results/live/2026-10-11T152922.787095Z/ADJUDICATION.md)
records extra scheduler cost and equivalence that depends on interval choice.
Controller and readout contention can extend fused duration beyond the longest
scheduled component. Candidate pricing therefore needs the complete fused
schedule, repetition delay, and job overhead.
Qualification needs isolated references, matched controls, executed schedules,
and final charge. The pipeline must extend family selection and joint
placement, preserve member/register identities and static/dynamic policies,
validate routed laws, and bind revised PUB manifests, inference, cost,
collection, and owner approval. Hardware evidence must establish any saving
at the required precision. Repeated replicas still supply no automatic
precision gain under arbitrary same-shot dependence; tighter bounds require
a justified covariance contract.

Adaptive shot stopping also requires a valid sequential inference contract
and job-granularity cost model; repeated fixed-sample interval checks would
change coverage. These extensions remain behind the existing uniform-shot
and reset-delay planning mechanisms.

## Ordered delivery gates

1. Preserve and integrate the completed folded raw evidence, all twelve
   contrasts, usage, calibration windows, and supplemental shot-order results.
   Complete review, synchronize main, and Git-prune the merged evidence branch.
2. Reconcile each candidate's question and ownership with the shared campaign.
   Reuse folded data. Resolve overlap between the historical static witness
   case and the other chat's ripple/rank-sector controls before authorizing
   additional measurements on any of the three QPUs.
3. Fit labeled intervention-specific model hypotheses locally, then validate
   them independently. Hardware-minus-replay errors change sign for odd
   no-feed-forward labels, so a uniform accuracy penalty cannot fit the data.
   Qualify matched readout/routing crossovers before interpreting the coherent
   advantage as one physical error mechanism.
4. Price explicitly chosen precision, qualify repetition-delay controls, and
   implement compatible mixed-job policy after local contracts pass. Bind each
   new physical variant to a fresh written case and approval. Preserve all
   complete control families and the single shared quota reserve.
5. Promote and qualify the native N21 challenger. Fresh CPU noise admission
   determines its next case. Renew static cases independently, with scientific
   deduplication; recompute campaign totals from admitted cases.
6. Keep the mathematical classification program on its classical proof path.
   Compatible semialgebraic decompositions for the remaining dimension-32
   rank loci precede full attachments, global invariants, and an unrestricted
   all-dimensional theorem. [RANK_STRATUM_TOPOLOGY.md](RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates)
   records those obligations. A QPU fringe experiment cannot certify them.

[modes]: https://quantum.cloud.ibm.com/docs/en/guides/execution-modes
[modes-faq]: https://quantum.cloud.ibm.com/docs/en/guides/execution-modes-faq
[usage]: https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time
[initialization]: https://quantum.cloud.ibm.com/docs/en/guides/repetition-rate-execution
[dynamic]: https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits
[timing]: https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-circuit-timing
[stretch]: https://quantum.cloud.ibm.com/docs/en/guides/stretch
[sampler]: https://quantum.cloud.ibm.com/docs/en/guides/sampler-options
[mitigation]: https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques
[shot-source]: https://github.com/Qiskit/qiskit-ibm-runtime/blob/0.50.0/qiskit_ibm_runtime/executor_sampler/utils.py

[native-dry-run]: https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/executor-sampler-sampler#run
