# Bounded QPU experiment design

The runner chooses a concrete experiment from a finite set before spending
QPU time. `live_run.py --family folded-qpe --optimize` and
`--family n21-feedback --optimize` retain fresh hardware admission,
deterministic compilation, exact QPY archives, and owner approval. The
optimizer ranks admitted designs by minimum estimated charge or strongest
worst-endpoint precision within the declared budget. ESP and coherence screen routed candidates;
they do not define statistical power or useful information per second.

The core implementation uses the following modules:

| Module | Responsibility |
|---|---|
| `qpe_diagnostics.py` | Circuit controls, exact labeled laws, and local conformance checks |
| `diagnostic_experiments.py` | Complete experiment families and signed observable contracts |
| `experiment_optimizer.py` | Bounded statistical and cost admission, deterministic choice, and Pareto frontier |
| `qpu_planning.py` | Fresh-calibration compilation, finite-shot predictions, matched layouts, and invocation accounting |
| `pub_shot_allocation.py` | Endpoint minima and bounded, cost-aware whole-tier promotions for complete static PUBs |
| `qpu_planning_contracts.py` | Credential-free integration checks against fake backend fixtures |
| `qpu_cases.py` | Unapproved written cases bound to feasible saved records and their QPY evidence |
| `qpu_case_allocation_contracts.py` | Allocated-case identity, budget, scenario, reproduction and artifact-preservation checks |
| `local_compute.py` | Explicit CPU execution policy, ordered simulation evidence, and GPU/hybrid capability rejection |

## Measured quantities and exact laws

The folded-QPE ladder has four rungs for each supplied eigenstate label
`s = 0, 1, 2, 3`:

| Rung | Intervention | Recorded bits |
|---|---|---|
| `archived` | Semiclassical measurement, reset, and conditional correction | First bit and terminal bit |
| `delay` | Replace the first measurement with a calibrated delay; retain reset and apply the prepared label's correction unconditionally | Terminal bit only |
| `no_feed_forward` | Retain measurement and reset; omit the conditional correction | First bit and terminal bit |
| `coherent` | Use a second control qubit and a controlled phase; measure both controls at the end | First bit and terminal bit |

The two-bit outcome index is `y = first_bit + 2 * terminal_bit`. The
archived and coherent ideal laws place all mass at `y = s`. The delay arm
places all mass at `terminal_bit = floor(s / 2)` and records that bit as its
only classical bit. Its supplied label is metadata, never a fabricated
measurement. Without feed-forward, even labels remain deterministic; each
odd label gives equal mass at `y = 1` and `y = 3`.

The shared observable is terminal-bit correctness relative to the supplied
label. Each non-archived rung contributes four signed contrasts against its
archived counterpart, giving twelve separate endpoints. Their ideal values
are zero for delay and coherent controls, zero for even no-feed-forward
labels, and `-1/2` for odd no-feed-forward labels. The design asks for
interval precision rather than a common positive effect across those
different controls. The default half-width is 0.08, and each endpoint uses
`alpha / 12`; default `alpha = 0.05` bounds the family-wide interval failure
probability by 0.05 through a union bound.

The compiler starts from an admitted coherent layout and pins the common
logical control and four work qubits to the same initial physical mapping
for the dynamic arms. The coherent arm retains its additional control.
The family uses one fixed placement per candidate and searches alternative
layouts; `--replica-tiers` does not replicate this ladder. Shared initial
mapping preserves the comparison's device patch, while routed trajectories
and complete schedules can differ. The dynamic arms produce twelve PUBs;
the coherent controls produce four PUBs in a separate static job. For each
phase label, the compiler identifies the first measurement's physical writer
in the compiled archived arm. That writer's fresh Target measurement duration,
rounded up to Target timing granularity, sets the matching delay. Admission
requires the compiled delay to remain on that writer. The record preserves
the four delay values and replaced writers, plus every arm's measurement
sites. The coherent arm can use different terminal readout sites and routed
trajectories. Replacing a measurement and its conditional correction changes
multiple mechanisms, so a difference alone cannot isolate measurement
backaction, reset, or controller error.

The N=21 diagnostic starts from `|1>`, uses base 4 and two phase bits, and
compares feed-forward against its omitted-correction control. The exact
probabilities in `y = 0, 1, 2, 3` order are:

| Arm | Labeled law | Mean of `w = (0, 1, 0, -1)` |
|---|---|---|
| Feed-forward | `(3, 2, 1, 2) / 8` | `0` |
| Without feed-forward | `(3, 1, 1, 3) / 8` | `-1/4` |

The signed difference of those means is `1/4`; their total variation
distance is `1/8`. This endpoint measures the labeled distribution's
response to feed-forward. Two phase bits give zero verified order recovery
for this experiment and do not establish factor recovery. The two arms
share a routed group and replica mappings, remain dynamic, and occupy two
PUBs in one job. `--replica-tiers` bounds the placements considered.

`qpe_diagnostics.py` derives both families' laws independently of Qiskit
using exact integer branch amplitudes and rational probabilities. The gate
compares those labels with exact circuit branches and seeded Aer sampling.
A deliberately swapped classical register must fail the N=21 labeled check;
sorting the probability masses would discard that witness.

Before each candidate's noise prediction, a branch-resolved statevector
check validates every compiled replica's labeled ideal law against the exact
oracle on its active wires, with absolute tolerance `1e-10`. A mismatch
rejects the planning run. The record's `compiled_ideal_validation` carries
the method, tolerance, `all_candidates_passed`, and
`noise_method="density_matrix"`. The fixed Aer kernel supports reproducible
mixed dynamic batches: a local Aer 0.17.2 reproducer exposed batch-order
sensitivity when automatic selection switched between statevector and
density-matrix methods for two-bit feedback and one-bit reset-only members.
The explicit density-matrix method retains the gate, coherence, and readout
noise channels. Exact compiled validation checks circuit conformance;
agreement with a noise model remains a separate empirical question.

The [local compute plan](LOCAL_COMPUTE.md) records the execution policy,
failed noisy branching comparison, CPU/CUDA/Aer capability distinctions,
precision frontier, and remaining GPU qualification gates. Local simulation
time stays separate from IBM QPU charge. Additional shots narrow sampling
intervals without establishing improved hardware fidelity.

## Statistical admission

Each `ObservableContract` names signed score vectors, an alpha, and either
a precision target or a directional effect/power target. Every endpoint
must pass separately. The optimizer adds no arbitrary weights across
unrelated scientific quantities.

For one PUB, the per-shot score averages each member's replica scores and
then applies the declared term signs. The conservative score range is the
sum of the contributing score-vector ranges. Replicas and fused members
within a shot may be arbitrarily correlated. Adding replicas therefore
provides no automatic reduction in the statistical bound. Independent,
stationary repetitions remain an explicit assumption; calibration checks
and shot-order diagnostics supply evidence about that assumption but cannot
prove it from layout separation.

For `B` contributing PUBs with ranges `R_b` and respective shot counts `S_b`,
the two-sided Hoeffding union bound uses half-width
`sum_b R_b * sqrt(log(2 * B / alpha) / (2 * S_b))`.
Uniform designs set every `S_b = S`. The
[fixed allocation](PACKED_ALGEBRA.md#fixed-shot-allocation) selects complete
PUB rows from declared tiers before hardware acquisition. Endpoint minima
and matched-row closure seed a complete whole-tier upward search, including
eligible uniform baselines. Full job overhead and cost scenarios enter the
existing objective ranking; the original model comparison count stays fixed.
The allocator retains one assignment per route for outer validation; a route
with every alternative infeasible retains a rejected diagnostic candidate.
Domains above 4096 assignments per route fail admission. Every endpoint retains its
precision or conditional-power target and its model allowance. The bounded
search establishes neither a global PUB allocation nor a packing or placement
optimum.
The one-sided bound replaces `2 * B` with `B`. The implementation clips a
bound to the possible score range. The union bound requires no independence
between PUBs or jobs. The standalone API also accepts a documented positive
semidefinite upper bound on the complete same-shot score covariance; a
Cantelli or Chebyshev bound can then tighten the interval. The family CLI
supplies no covariance certificate and retains the arbitrary-dependence
default. Physical separation alone supplies neither independence nor a
covariance certificate. Covariance admission rejects a negative numerical
eigenvalue or projected variance; rounding a negative value to zero would
fabricate precision.

The N=21 contract tests the positive direction against zero, using default
alpha 0.05 and power 0.8. `minimum_effect = 0` selects the positive modeled
gap after the simulation allowance as the alternative. The report records
that value as `effect_used_for_power`. Admission requires the alternative
to exceed the sum of the one-sided alpha radius and the miss-probability
radius. The standalone API also supports a positive minimum detectable
effect with conditional power evaluated at that declared effect.

Noise predictions use `--model-shots` samples, default 32768. A separate
Hoeffding allowance covers every scored candidate, observable term, and
replica marginal through a union bound; default `--simulation-alpha 0.01`
sets the search-wide failure allowance. Candidate selection therefore
accounts for finite simulation error. Hardware-model discrepancy remains
unquantified. The retained folded-QPE hardware result differs substantially
from the calibration noise model, as described in the
[hardware plan](HARDWARE_PLAN.md#hardware-evidence-and-next-cases).
Statistical design admission establishes conditional modeled power or
precision, and establishes neither hardware accuracy nor submission
authorization.

## Charged-time model and ceilings

Every job's estimate includes all submitted PUBs and controls:

```text
estimated charge = job overhead
                 + sum_PUB shots * (Target circuit duration
                                    + repetition delay
                                    + declared classical latency)
```

The Target circuit duration includes its explicit reset instructions. Dynamic
Target duration omits classical feed-forward latency, so the planner adds
`--classical-latency-us` times the deepest sequential feed-forward stage
count. The default 20 microseconds per stage is an explicit unmeasured
planning assumption. It is neither the retained job's measured round trip
nor a service bound. The 2.3-second `--job-overhead-seconds` default comes
from the retained dynamic job's non-circuit charge; a different job can
have different overhead. Sensitivity runs must name changes to either
assumption. Such runs qualify the declared cost model rather than the
physical charge.

The family planner leaves the additional `reset_seconds` term at zero.
Installed client-side Runtime 0.50 enables `init_qubits` by default, so the
service can insert implicit initialization before the supplied circuit.
IBM's [local usage-estimation example](https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time)
adds Target reset duration for that initialization separately. The retained
nominal and stress ledgers leave the implicit term unseparated; neither
scenario supplies a bound for it. The historical overhead residual can also
absorb unmodeled work, so an extra reset proxy requires a reconciled accounting
boundary. A renewed hardware case needs server timing and usage estimates
that distinguish implicit initialization, explicit resets, and overhead.
The service ceilings and invocation reservations enforce their separate limits.

The planner reads `backend.configuration().default_rep_delay` in seconds,
validates the backend's repetition-delay support and range, and binds the
value to `sampler.options.execution.rep_delay`. The serialized backend
configuration uses microseconds; mixing those two interfaces changes the
cost by a factor of a million. [Numerical environment validation](NUMPY_VALIDATION.md#execution-time-units)
records the SDK source and tested option paths.

`--max-execution-seconds` caps each job. The sum of every backend/kind job's
ceiling must fit `--max-total-execution-seconds`, and that sum plus
`--reserve-seconds` must fit the reported remaining quota. Each batch
rechecks the full invocation reservation and reserve against fresh quota.
The ledger retains every planned, attempted, and accepted job's ceiling
until collection, including accepted jobs whose charge has yet to appear
in usage. Acceptance therefore releases zero reserved seconds. The
reservation is local to the invocation; other clients can change the
shared quota. An instance without a finite remaining quota still receives
the explicit invocation cap.

Final accounting keeps the existing unit: submitted PUB shots divided by
the completed job's final `job.usage(partial=False)` charge. Replicas do
not multiply submitted PUB shots. A joint job charge has no exact
per-observable allocation. The optimizer minimizes an estimated total
charge or maximizes declared precision within the budget while preserving
separately labeled observables; neither objective measures scientific
information per charged second.

The collection header's `invocation_usage` retains known final charges,
including billing for failed or cancelled jobs. `charge_complete` records
complete final billing; `workload_complete` additionally requires every
planned job to finish successfully with status `DONE`. The full-workload
cost residual, `charge_prediction_residual_seconds`, compares final charge
with the selected prediction only when the complete workload succeeds and
every job has a final charge. Incomplete or unsuccessful execution retains
its billed usage and an explicit reason for withholding that residual.

## Bounded CLI and records

The command below reads fresh backend and quota metadata, compiles and
simulates locally, and writes a new audit directory. Backend eligibility
and quota can reject the supplied bounds. The command submits zero jobs.
Run it from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  "$PYTHON" live_run.py --family folded-qpe --optimize \
    --backends ibm_kingston --seeds 2 --optimizer-candidates 2 \
    --shot-tiers 2048,4096,8192,16384 --model-shots 32768 \
    --max-execution-seconds 60 --max-total-execution-seconds 120 \
    --reserve-seconds 60 --out ../results/live
)
```

For N=21, select `--family n21-feedback` and an explicit replica list such
as `--replica-tiers 1,2,4`. A 60-second per-job ceiling needs a combined cap
of at least 60 seconds for its single job. Folded QPE needs both job
ceilings in its combined cap. Those numbers define planning constraints;
the fresh record supplies the actual estimate and admission result.

| Option | Default and scope |
|---|---|
| `--seeds` | Eight transpiler seeds per group/backend; existing routing retains at most three per backend |
| `--optimizer-candidates` | Six ranked routed family candidates before replica and shot expansion |
| `--shot-tiers` | `2048,4096,8192,16384`; allowed fixed counts for the selected allocation mode |
| `--shot-allocation` | `uniform`; `per-pub` requires an optimized static algebra family and groups complete PUBs into homogeneous shot-tier jobs |
| `--replica-tiers` | `1,2,4`; N=21 only, with actual floor-qualified placement counts recorded |
| `--model-shots` | 32768 samples for each prediction |
| `--precision` | 0.08, folded terminal-contrast half-width |
| `--alpha`, `--power` | 0.05 and 0.8; folded alpha is divided among twelve precision contracts |
| `--simulation-alpha` | 0.01 over the supplied finite search |
| `--objective` | `minimum_charge`; `precision_at_budget` accepts folded precision-only contracts |
| `--cost-scenario` | Repeatable `NAME:OVERHEAD_SECONDS:LATENCY_US`; every supplied scenario must pass the same budget gates |
| `--local-compute` | `cpu`; GPU and hybrid requests fail capability admission before IBM service construction |
| `--simulation-threads`, `--simulation-memory-mb` | 2 threads and 512 MB; density matrices and double precision remain fixed |
| `--max-pending` | 25, unchanged backend queue admission |
| `--reserve-seconds` | 0; set an explicit reserve when the case requires one |

`--family` also works without `--optimize`, evaluating the explicit
`--shots` tier. Both per-job and aggregate ceilings remain required.
`--optimize` requires a named family. Families reject `--groups`,
`--twirl`, and `--dd`: each family retains its complete controls and common
unmitigated policy. General static jobs retain their existing mitigation
options; dynamic jobs keep twirling and DD disabled.

The default design search minimizes worst-case estimated charge across
nominal inputs and every declared cost scenario, then breaks ties by
candidate name. `precision_at_budget` minimizes the largest endpoint
confidence half-width divided by its precision target, then worst-case
charge and candidate name. The precision objective requires precision-only
contracts and the CLI restricts it to folded QPE. The search retains every
rejection and the feasible Pareto frontier across cost, per-endpoint
precision, and conservative modeled effects. The search is bounded by
supplied backends, retained routes, replica caps, and shot tiers. A selected candidate establishes
neither a global optimum nor a general hardware-performance claim.

Schema 7 records retain `family_configuration`, exact signed
`observable_contracts`, `optimizer_settings`, `optimization_budget`, the
candidate table, `budget_plan`, and `execution_contract`. The execution
contract binds each selected backend's repetition settings, every selected
job/PUB's cost inputs, and the selected cost scenarios to approval.
`optimizer_settings` binds the objective and scenario list; `policy.local_compute`
binds the simulation settings. `local_simulation_batches` and
`evaluation_simulation_batches` retain ordered circuit/noise identities and
Aer method/device metadata. The channel digest excludes custom delay
relaxation passes; the [compute plan](LOCAL_COMPUTE.md) names their separate
calibration inputs. The runner recomputes the contract after fresh selection, so unchanged QPY bytes alone cannot admit
changed repetition delays or cost assumptions. If every candidate fails
the design contracts, the runner writes `state="design_infeasible"`,
`optimization.selected=null`, all rejection reasons, and a concrete
candidate's QPY archive for diagnosis. A failed invocation reservation
writes `state="budget_infeasible"`. The diagnostic dry run can exit
successfully after preserving such a negative result. Submission requires
`state="planned"`; the presence of an archive alone grants no admission.

`qpu_cases.py` writes `UNAPPROVED_CASE.md` for a feasible family record in
the `planned` state. The writer binds the case to the saved record and QPY
digests and records the statistical assumptions, expected charge, both
ceilings, and reserve. The writer reads local artifacts and submits zero
jobs. Its `--check` gate uses credential-free fixtures. For a saved family
run, set `RUN_DIRECTORY` to the retained run directory and invoke the
writer from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  : "${RUN_DIRECTORY:?set RUN_DIRECTORY to the saved family run directory}"
  "$PYTHON" gororoba_quantum/qpu_cases.py "$RUN_DIRECTORY"
)
```

The writer declines nonfamily, infeasible, or submitted records and checks
saved-record equality, selected cost accounting, and ordered QPY circuit
names before recording the artifact hashes. An allocated case requires one
strictly positive shot count for every execution PUB, membership in the
declared tiers, homogeneous counts within each job, and matching ordered
budget membership and cost-scenario workloads. The top-level `shots` equals
the largest allocated count; the full PUB ledger supplies each actual count.
Reproduction includes `--shot-allocation` only when the saved design records
that option, preserving historical uniform commands. A written case still requires
owner approval. Fresh selection and calibration must match the approved
experiment, observable contracts, shots, policy, dependencies, layouts,
replica maps, execution contract, and QPY bytes. A changed plan requires a
fresh case and approval. Historical raw results, records, and earlier
interpretations remain retained under their original identities.

Collection reports `family_analysis` only when every required member has
compatible execution-time calibration evidence. The pure
`analyze_observations` helper groups measured members by their immutable
execution PUB identities and applies the same bounds as the planner. The
report preserves measured bit labels and gives signed estimates with
two-sided confidence intervals. Directional contracts separately report
`reject_null` from the one-sided alpha threshold used in the power design;
that test can reject even when the displayed two-sided interval contains
the null. Precision-only endpoints carry an interval and an absent
directional decision. Failed calibration or observation admission withholds
the family comparison. The `collect.json` header's `family_analysis` is the
canonical preregistered family inference. Inherited per-group replica
summaries remain diagnostics and set neither optimizer admission nor its
conditional-power guarantee. Their replica-based t summaries require
separate dependence assumptions; the family inference permits arbitrary
within-shot dependence.

## Verification and sources

The [repository gates](../AGENTS.md#layout-and-gates) run the exact labeled
QPE checks, standalone optimizer checks, and fake-backend planning
contracts. The planning checks cover the shared initial mapping,
per-phase calibrated delay sites, complete static/dynamic job accounting, shot-tier
admission, approval mismatches, and negative-record persistence. Those
checks consume zero QPU jobs. The allocated-case contracts run in normal
and optimized Python modes, reject inconsistent mappings and ledgers, preserve
retained artifact bytes on rejection, and parse reproduction commands with the
live CLI before any service call. A fresh live-calibration dry run remains a
separate admission surface. Historical allocation arithmetic and separate
4096-shot evaluation distributions remain outside current admission; the
[allocation note](PACKED_ALGEBRA.md#fixed-shot-allocation) identifies their
model-shot counts and limits.

- Wassily Hoeffding, ["Probability Inequalities for Sums of Bounded Random Variables"](https://doi.org/10.1080/01621459.1963.10500830),
  *Journal of the American Statistical Association* 58(301), 13-30 (1963),
  Theorem 2. The bound applies to sums of independent bounded variables;
  the repository applies independence across repetitions and union bounds
  across PUBs. The theorem supplies no hardware-model or replica-independence
  claim.
- IBM, [Estimate job run time](https://quantum.cloud.ibm.com/docs/guides/estimate-job-run-time),
  grounds the separate circuit duration, repetition delay, and job-overhead
  terms.
- IBM, [ExecutionOptions](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-execution-options),
  grounds `execution.rep_delay`, its units, and backend support requirements.
- IBM, [SamplerOptions](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-sampler-options)
  and [maximum execution time](https://quantum.cloud.ibm.com/docs/guides/max-execution-time),
  ground the per-job system-execution ceiling. Session or batch lifetime has
  separate semantics.
