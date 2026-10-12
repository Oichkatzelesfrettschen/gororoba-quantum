# QPU execution and optimization roadmap

The next hardware expenditure answers the folded-QPE model discrepancy. The
runner uses installed Qiskit Aer on the CPU for preparation. Custom CUDA work
remains paused. Each hardware case requires a fresh admitted dry run, a written
case, and explicit owner approval. Local validation establishes circuit and
planning conformance; hardware observations establish accuracy and stability.

This roadmap reads the retained evidence at source `b3be72c` and the official
manuals on 2026-10-11, America/Los_Angeles. The tested environment uses Qiskit
2.5.2, Runtime 0.50.0, and Aer 0.17.2. Later calibration can change every layout,
job allocation, duration, and admission decision below.

## Execution queue and budget

| Scientific case | Job structure | PUBs | QPU seconds | Admission state |
|---|---|---:|---|---|
| Folded-QPE mechanism ladder | Two jobs on ibm_kingston: dynamic, then static coherent controls | 12 + 4 | 39.611690 nominal; 45.522410 stress | Retained feasible case, unapproved |
| N21 feedback diagnostic | Intended one dynamic job | 2 | New estimate follows successful redesign | Retained candidates fail statistical admission |
| Static algebraic witnesses | Historical allocation uses two jobs on two backends | 17 | Historical case estimates about 23; fresh pricing required | Case requires renewal |

The outline therefore contains five jobs and 35 PUBs if the N21 design becomes
admissible and the static allocation remains the same. Only the first two jobs
have a fresh feasible case. The complete campaign has no admitted total yet.
The static program remains independent of the N21 synthesis problem; a changed
scientific priority can move its separately renewed case ahead of N21.

The [folded case](../results/live/2026-10-12T024756.245948Z/UNAPPROVED_CASE.md)
uses 8192 shots per PUB, or 131072 submitted PUB shots:

| Job | Nominal seconds | Stress seconds | Service ceiling |
|---|---:|---:|---:|
| Twelve dynamic PUBs | 28.827006720 | 32.437726720 | 60 |
| Four static PUBs | 10.784683776 | 13.084683776 | 60 |
| Invocation | 39.611690496 | 45.522410496 | 120 |

The plan also retains 60 seconds of quota reserve. The saved quota observation
reports 591 seconds remaining in the 600-second rolling 28-day allowance.
Fresh execution rechecks that shared allowance. Ceilings reserve invocation
quota capacity; owner approval authorizes spending. Ceilings differ from
predicted charge and final billing. Queue delay and the
246-second retained CPU preparation lie outside the QPU usage estimates.

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
| 250-microsecond repetition delay | 32.768000000 | 82.72% |
| Two modeled job overheads | 4.600000000 | 11.61% |
| Target circuit duration, including reset instructions | 1.588330496 | 4.01% |
| Explicit classical-latency allowance | 0.655360000 | 1.65% |

The [IBM usage model][usage] includes circuit duration, repetition delay, and
job overhead. Eliminating every Target-circuit and modeled classical-latency term would
save only 5.66% here. Gate improvement still matters for fidelity, but shot design
and initialization delay dominate this experiment's throughput opportunity.
These percentages belong to the retained folded workload, not every QPU job.

## Precision choices use the existing optimizer

The retained case uses `precision_at_budget`: it buys stronger precision than
the hard 0.08 target. Twelve contrasts each receive alpha `0.05/12`. The existing
bounded interval has half-width `H(S) = 2*sqrt(log(960)/(2*S))` for uniform shots
`S`. More shots narrow statistical uncertainty; they leave systematic hardware
bias intact.

| Shots/PUB | Half-width | Nominal seconds | Stress seconds | Interpretation |
|---:|---:|---:|---:|---|
| 2048 | 0.081890 | 13.352923 | 18.280603 | Fails the 0.08 target |
| 2146 | 0.079998 | 13.771764 | 18.715124 | Derived minimum integer tier for 0.08 |
| 4096 | 0.057905 | 22.105845 | 27.361205 | Retained feasible candidate |
| 5494 | 0.049998 | 28.080741 | 33.559781 | Derived minimum integer tier for 0.05 |
| 8192 | 0.040945 | 39.611690 | 45.522410 | Selected precision-at-budget case |

The 4096-shot candidate saves 44.2% of nominal charge while meeting the existing
hard target. A finer 5494-shot tier saves 29.1% and meets a newly declared 0.05
target. The two derived rows use the retained cost ledger and interval formula;
they are candidate designs, not fresh dry runs. Neither reduction preserves
the selected 0.040945 precision. A new `minimum_charge` case explicitly records
the desired precision and the chosen integer tier before approval.

The CLI already accepts arbitrary positive integer `--shot-tiers`. The first
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
| 100 microseconds | 19.950890 | 25.861610 | 49.63% |
| 50 microseconds | 13.397290 | 19.308010 | 66.18% |

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

## Native server-side dry runs can refine schedule estimates

Runtime 0.50 exposes [`Sampler.run(..., dry_run=True)`][native-dry-run]. IBM
states that the server validates the job and supplies usage estimates and
circuit timing metadata without executing the job on a QPU. The installed
Sampler and Executor source contain that path. Account access remains to be
checked; the API reference explicitly allows restricted access.

A separate preparation mode can use the exact admitted QPY circuits to obtain
server scheduling information before a hardware case. Its records must label
the returned measurements as randomized mock data and exclude them from
fidelity prediction, scientific adjudication, and measured-hardware evidence.
Server-side schedule estimates can constrain modeled latency; executed
scheduler tables and final billing remain separate evidence. The preparation
mode also needs tests proving that its submitted request binds `dry_run=True`.
The present local dry-run implementation does not call this server feature.

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

Packing retains arbitrary same-shot dependence until a justified covariance
bound supports a tighter interval. Physical separation alone supplies no such
certificate. Adaptive shot stopping also requires a valid sequential inference
contract and job-granularity cost model; repeated fixed-sample interval checks
would change coverage. Both ideas rank behind the existing uniform-shot and
reset-delay mechanisms.

## Ordered delivery gates

1. Resolve evidence-integrity review findings, run all required gates, complete
   review, merge, synchronize the canonical checkout, and prune merged residue.
2. Qualify access to the native server-side dry-run path and distinguish its
   mock outcomes from CPU simulation and hardware results. Produce fresh folded
   cases for explicitly chosen precision targets using the installed CPU Aer.
   Compare modeled charge, stress charge, and ceilings; obtain owner approval
   for one concrete plan.
3. Execute the approved folded plan, preserve raw ordered outcomes first, then
   adjudicate the twelve contrasts, executed schedules, drift, and final charge.
4. Use those observations to prioritize `measure_2`, targeted echoes, or a
   repetition-delay pilot. Each physical variant receives exact local checks,
   a separately priced case, and approval before execution.
5. Promote and qualify the native N21 challenger; renew the static witness
   case independently. Recompute the campaign job count and budget from
   admitted cases instead of adding historical or rejected estimates.
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
