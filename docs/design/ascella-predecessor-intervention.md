# Ascella predecessor intervention

Status: the owner selects the eight-iteration target-slot diagnostic with causal
attribution unavailable. A write-once builder produces a source-compatible
successor. Fresh provider admission, independent packet review, digest custody
and exact owner approval remain pending for that successor. Conditional uncertainty
additionally requires its reviewed sampling contract. The case authorizes zero
provider submissions.

The [gate-closure packet](../evidence/ascella-predecessor-admission/gate-closure.md)
records the historical request's source identities, findings, admission and
digest custody. That packet does not bind the source-compatible successor. A separate causal successor carries
the predecessor-causality objective.

The builder is [`scripts/ascella_predecessor_case.py`](../../scripts/ascella_predecessor_case.py).
The historical reviewed request is
[`results/quandela/cases/ascella_predecessor/reviewed-submission/`](../../results/quandela/cases/ascella_predecessor/reviewed-submission/cases.json).
`cases.json` sha256 `0e58c0b22c4f8650ae893c5a7dcae5daeb1e25e87012c1aa3be8318085c17c13`.
The [source-compatible successor](../../results/quandela/cases/ascella_predecessor/source-compatible/cases.json)
has `cases.json` sha256 `dd7757e087f5dff36efb78bc903ae7c5d1c6b5c24ea88537ee3b4e92e5357fce`.
`circuit.json` is the job-00 template, byte for byte, sha256
`1fed0081cd440ffd6bb3b6c286750484041d70146d3dc5f13855d61598d2da0f`.

## Question

Does a signed contrast of four twelve-mode target distributions exceed a
preregistered 0.1 total-variation margin when the request alternates the target
with two different settings? The target is the retained X-readout arm at the
third sampled angle (`theta2-x-arm0`). The request labels describe the proposed
predecessor conditions; returned iterator order establishes attribution rather
than physical chronology. Physical predecessor causation remains unavailable
from the metadata exposed by this case.

The predecessors are `theta2-x-arm1` and `theta0-x-arm0`. All three are the
seed-0 settings of
[job-00](../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/README.md),
cases digest `3c92af45df7502bab5c6f2d74779aa83b04f7af2094b62b499b6e29ca0e69520`.
Their compilation seeds are the values those settings already carry. Those
identifiers request reproduction of the retained meshes. The returned circuit
and input digests establish the digital identity checks; applied analog controls
and physical timing remain separate evidence requirements.

## Request

One job, family `ascella_predecessor`, name `ascella_predecessor/source-compatible`.
Platform `qpu:ascella` only. Command `sample_count`. Gate form `template`.
Twelve modes, one photon in mode 0, `min_detected_photons` 1, empty
mitigations, `max_duration` 300, output width 12. Eligible events are an
occupation sum of one across all twelve returned modes. Modes 4 through 11
stay in the histogram.

Eight iterations, 32,768 samples and 32,768 shots each. The manifest stores
the aggregates 262,144 and 262,144, which the template runner divides evenly.
The ceiling field `max_credits` is 1.032768.

| Index | Order | Role | Source setting | Job-00 index | Slot |
|---|---|---|---|---|---|
| 0 | A | predecessor | theta2-x-arm1 | 29 | even |
| 1 | A | target | theta2-x-arm0 | 28 | odd |
| 2 | A | predecessor | theta0-x-arm0 | 4 | even |
| 3 | A | target | theta2-x-arm0 | 28 | odd |
| 4 | B | predecessor | theta0-x-arm0 | 4 | even |
| 5 | B | target | theta2-x-arm0 | 28 | odd |
| 6 | B | predecessor | theta2-x-arm1 | 29 | even |
| 7 | B | target | theta2-x-arm0 | 28 | odd |

Order A runs predecessor `theta2-x-arm1`, then the target, then predecessor
`theta0-x-arm0`, then the target. Order B runs that pair in the other
direction. Every target sits on an odd iteration index. The
[signed-coherence case](ascella-signed-coherence-conformance.md#permuted-repeat-job-01)
records why that parity is part of the request: job-00 outside-block log
counts alternate in execution order (lag-1 autocorrelation -0.66), and job-01
keeps the alternation (lag-1 -0.653) after the setting order changes. The
decision in this job is the contrast among preceded targets that share odd
slots. A target-only iteration is a different payload, and placing one
between these pairs would put a later target on an even index, so this job
contains only preceded targets.

The earlier analysis of separate invocations would have used six jobs, one
pair or one target-only payload each. This case is the one job that fits a
single acquisition: both orders share one iterator. A carry that lasts longer
than the immediately preceding iteration stays inside that same payload and
is not separated here.

Each setting's `circuit_params`, `column`, `operator` and compilation seed
are copied from the named job-00 setting. `--check` binds them through
`qd_platform.template_experiment`, so Perceval's unitary matches the retained
operator within 1e-9.

Requested total variation, half the L1 distance of the twelve-mode columns:

| Pair | Requested TVD |
|---|---|
| theta2-x-arm0 against theta2-x-arm1 | 0.9045084971874732 |
| theta2-x-arm0 against theta0-x-arm0 | 0.678381372890605 |
| theta2-x-arm1 against theta0-x-arm0 | 0.678381372890605 |

Each pair clears 0.5. Among the job-00 requested laws that sit at least 0.5
from the target, one pair of laws is also at least 0.5 apart: the law shared
by the eight theta0 arms, and the law shared by `theta2-x-arm1`,
`theta2-x-arm2`, `theta3-x-arm1` and `theta3-x-arm2`. No four of those laws
clear 0.5 pairwise. This job uses the seed-0 representatives `theta2-x-arm1`
and `theta0-x-arm0`. `mutation-arm1-ii` stays out; its requested TVD from the
target is 0.07161862710939487.

## Compilation identity

The analyzer compares sha256 of each iteration's `computed_circuit` and
`computed_input` strings with the retained source identities in the manifest.
The circuit identities are:

| Role | Source | Computed-circuit sha256 |
|---|---|---|
| target theta2-x-arm0 | job-00 iteration 28, job `739a5271-bb84-42b7-9fc3-0562ca5cef47` | `8afe0165defb330b7ab2018db97ba9dae0ca957d391cf2f5b2dc8c443c90cbd9` |
| predecessor theta2-x-arm1 | job-00 iteration 29 | `d0d60369f8c914c41b543f05f6d30709f530efbe7bff29205314049572081855` |
| predecessor theta0-x-arm0 | job-00 iteration 4 | `5501ec2b213bbddb1a79b9c68990062a367ecaa029296d0d67e2072b0a778a33` |

Job-01 repeats every job-00 `computed_circuit`, including these three.
Job-02 and job-03 each return eight seed-0 anchors, and all sixteen blobs
equal the target hash above. A target iteration whose blob differs from that
hash, or a predecessor iteration whose blob differs from its source hash,
stops the comparison before either reading below. The stop is an invalid
intervention. It is not called drift, and this case does not retry it.

## Signed response and conditional decision

The histogram conditions on occupation sum one across all twelve modes.
The analyzer retains each invalid-photon category and its count separately;
eligible counts exclude those categories. Every iteration must return the
full fixed 32,768-event target before conditional inference is admitted.

Let `P1`, `P3`, `P5` and `P7` denote the eligible laws at the four attributed
target slots. The analyzer preserves direction before taking an L1 norm:

```text
D_A = P1 - P3
D_B = P7 - P5
C = (D_A + D_B)/2 = (P1 - P3 - P5 + P7)/2
H = (D_B - D_A)/2 = (-P1 + P3 - P5 + P7)/2
```

The primary endpoint is `||C||_1 / 2`. The reversal diagnostic is `||H||_1 / 2`.
Both vectors have zero sum. Their components and norms use exact fractions.
The coefficient vector for `C` cancels constant and affine drift in requested
target position. Taking separate TVDs before combining destroys that
cancellation: two-mode target counts `(3277,29491)`, `(8192,24576)`,
`(13107,19661)` and `(18022,14746)` give two TVDs of about 0.15 from pure linear
drift, while `C` is exactly zero. The regression suite checks that counterexample.

Cancellation in physical time requires physical timing evidence. The provider
returns iteration attribution and job-level times, while individual physical
iteration timestamps remain unavailable in the retained format. Even equally
spaced physical observations leave curvature confounded: at centered target
positions `x=(-3,-1,1,3)`, `x^2=1+8 I_A`, where `I_A=(1,0,0,1)` marks the first
predecessor condition. A response `a+b*x+c*x^2+theta*I_A` gives `C=8*c+theta`.
A zero reversal diagnostic therefore cannot establish negligible drift.
Longer-history carryover remains unidentified by the four target observations.

The default analyzer emits descriptive vectors and norms with
`physical_predecessor_attribution=unavailable`. A separately reviewed,
externally digest-anchored sampling contract permits hypothesis-conditional
confidence envelopes for the slot-response estimand alone. The contract assumes
IID categorical returned events within each iteration, a fixed returned-event
count and conditioning on the single-photon eligibility count. Independence
between iterations is unnecessary for the union bound. Neither returned hashes
nor a contract assertion establishes physical IID sampling.
The analyzer validates submission and result records from the exact bytes
matched against the caller's digests, and it passes the captured run files to
the provider validator in a private local snapshot. The sampling contract is
also parsed from its anchored bytes. The raw hash chain and snapshot prevent
the analyzer from silently substituting later file contents; they do not
authenticate the external anchors or prove the stated sampling assumptions.

For eight laws, twelve eligible outcomes and family alpha 0.05, the per-law
subset-Hoeffding radius at eligible count `n_k` is

`epsilon_k = sqrt((12 ln 2 + ln(8 / 0.05)) / (2 n_k))`.

The subset union bound covers all eight true eligible laws simultaneously.
Triangle inequality then bounds the norm error of `C` and `H` by
`(epsilon_1+epsilon_3+epsilon_5+epsilon_7)/2`. A predecessor-pair TVD uses the
sum of its two radii. At 32,768 eligible events in each law, the common-contrast
radius is approximately 0.028590910871208422. The implementation rounds every
radius upward and interval endpoints outward with 60-digit decimal arithmetic.
The same simultaneous event covers every displayed deterministic contrast;
the analysis allocates zero additional alpha to the reversal diagnostic.

- Conditional response above margin: the lower bound on `||C||_1/2` exceeds 0.1,
  and both predecessor-pair TVD lower bounds exceed 0.1.
- Conditional response below margin: the upper bound on `||C||_1/2` is below 0.1,
  and both predecessor-pair TVD lower bounds exceed 0.1.
- Otherwise the conditional response decision is inconclusive.

The below-margin outcome concerns the common signed contrast, rather than
per-order invariance. Opposite effects can cancel in `C` and remain visible in
`H`. A 0.1 margin also permits changes of the size reported by the
[context diagnostic](../evidence/ascella-transition-context-diagnostics/findings.md):
its identity-input-5 requested-order TVD is 0.0462. Choosing a finer margin
requires a revised power, sampling and cost contract before acquisition.
Compilation, input, raw-binding or completeness failures invalidate acquisition
for this analyzer. A missing sampling contract leaves descriptive output.

The Belenos draft's clause that the target remains wrong stays with that
draft. These Ascella settings already return laws near their requests on the
retained jobs. The conditional below-margin outcome bounds the common signed
target-slot contrast and permits opposite movements across the two requested orders.
The Belenos phases, control indices and 24-outcome radius stay in
[the evidence-closure candidate](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention).

There is no automatic retry. A terminal error is reported. A second job
needs its own case.

## Precision, power and coefficient interpretation

The fixed allocation addresses a coarse common-response margin. With 32,768
eligible events in every iteration, the simultaneous radius is
`R(0.05) = 0.028590910871208422`. An observed common norm must exceed
0.128590910871208422 to clear the 0.1 margin; the predecessor controls must
also clear their bounds. The radius alone does not establish decision power.

Let `R(q) = 2 sqrt((12 ln 2 + ln(8/q))/(2 n))` for equal eligible count `n`.
On the simultaneous event with failure probability beta, every norm differs
from its population value by at most `R(beta)`. At beta 0.20 and n 32,768,
`R(beta) = 0.027070786680588680`. Triangle inequality gives the following
sufficient conditional power regions, with decision alpha 0.05:

| Decision | Population common norm | Each population predecessor-control TVD | Guaranteed conditional power |
|---|---:|---:|---:|
| Above 0.1 | Greater than 0.155661698 | Greater than 0.155661698 | At least 80% |
| Below 0.1 | Less than 0.044338302 | Greater than 0.155661698 | At least 80% |

The inequalities use rounded conservative thresholds. The guarantee follows
from one simultaneous event; cross-iteration independence is unnecessary.
Within-iteration IID events, fixed completion, conditional eligibility and
the anchored contract remain essential. Lost eligible events widen the actual
bounds. The guarantee concerns the common contrast and the two control
distances together; a control failure can withhold either decision.

For a population common norm `t`, sufficient equal eligible count is the
smallest integer strictly above
`2 (sqrt(12 ln 2 + ln(8/0.05)) + sqrt(12 ln 2 + ln(8/0.20)))^2 / (t-0.1)^2`.
The same requirement applies to each predecessor control's distance from 0.1.

| Sensitivity scenario for common norm | Direction | Sufficient eligible events per iteration |
|---|---|---:|
| 0.1500 | Above 0.1 | 40,610 |
| 0.1600 | Above 0.1 | 28,201 |
| 0.0462 | Below 0.1 | 35,076 |
| 0.0654 | Below 0.1 | 84,803 |

The retained context distances motivate the last two sensitivity scenarios;
they are different estimands and establish neither population value here.
The current 32,768-shot cap remains unchanged. Increasing shots or repeating
an inconclusive job requires a separately reviewed, costed and approved case.

The coefficient decomposition exposes the temporal ambiguity directly.
For centered requested positions `x=(-3,-1,1,3)`, the exact moments are:

| Contrast | Constant | x | x squared | x cubed | x to the fourth |
|---|---:|---:|---:|---:|---:|
| Common C | 0 | 0 | 8 | 0 | 80 |
| Reversal H | 0 | 2 | 0 | 26 | 0 |

For each output's law `a+b*x+c*x^2+d*x^3+e*x^4+theta*I_A`,
`C=theta+8*c+80*e` and `H=2*b+26*d`. The common contrast probes symmetric
curvature together with the assigned condition; the reversal probes odd drift
directions. A small reversal cannot bound curvature. Actual physical-time
cancellation requires timing evidence beyond requested index.

An eight-target successor with predecessor labels `A,B,B,A,B,A,A,B` and
weights `(1,-1,-1,1,-1,1,1,-1)/4` cancels polynomial index trends through
degree two and gives unit gain to an additive A-versus-B response. The
construction is the classical Prouhet–Thue–Morse contrast. Its cubic
coefficient at centered positions `(-7,-5,-3,-1,1,3,5,7)` is -96, so the
successor moves the drift ambiguity rather than establishing causality.
The two-output first-cell counts
`(263,10509,15115,16337,16431,17653,22259,32505)` out of 32,768 equal
`16384+47*x^3`. Pure cubic drift gives common norm `141/1024`; the
sixteen-law radius of approximately 0.029321435 leaves a lower endpoint above
0.10837, which clears 0.1 despite zero predecessor effect. The
[design regression](../../tests/scripts/test_ascella_predecessor_case.py)
checks the coefficient moments, sizing and drift counterexample.

Sixteen iterations at 32,768 shots would request 524,288 shots and extrapolate
to 48.6 seconds at the slowest retained relevant rate. The retained tariff
would give 1.032768 credits because the largest per-iteration cap stays fixed.
These are successor scenarios, rather than changes to the eight-iteration
case or a provider guarantee. A randomized repeated design with a supported
chronology and explicit carryover model remains the causal-design obligation.

## Review and evidence custody checklist

The frozen request remains eight iterations and one attempt. The preparation
review distinguishes the following gates:

| Gate | Required artifact | Result when missing or invalid |
|---|---|---|
| Digital identity | Byte-exact case replay, source closure, Perceval body and returned circuit/input identities | Refuse the affected comparison |
| Resource admission | Fresh live price, shot estimate, processor and token checks within 1.032768 credits | Withhold submission |
| Owner authority | Exact written-case approval covering the fresh planned body and single attempt | Withhold submission |
| Raw provenance | Independently retained submission and result digests with documented custody, raw hash chain and complete iteration attribution | Refuse analysis |
| Conditional inference | Pre-acquisition contract plus review artifacts for sampling, stopping and temporal limits, all externally digest-anchored | Emit descriptive output only |
| Physical attribution | Physical chronology and a design distinguishing drift and longer carryover | Preserve `physical_predecessor_attribution=unavailable` for this case |

The operator retains expected digests in a review record outside the analyzed
run directory and records the source and custodian of each digest. A local
recomputation from that directory checks consistency only. Review text states
the supported sampling evidence and residual assumptions; a signed assertion
cannot establish IID behavior. The existing analyzer contract enforces byte
bindings, while scientific review establishes the scope of the assumptions.
The preparation record distinguishes complete raw acquisition, descriptive
analysis, conditional above/below-margin response, and inconclusive response.
A below-margin common contrast permits opposite order-specific movements.

The retained running-platform admission remains evidence for its recorded
request and source bytes. Source or analyzer changes require a successor
bundle and a fresh plan. The case continues to admit `running` as a queueable
platform status while enforcing calibration, maintenance and token-occupancy
checks. The case has zero automatic retries.

## Causal successor preparation contract

The owner also requests a separate predecessor-causality design. The successor
keeps the exact target mesh, physical input and complete twelve-mode output
law and treats predecessor assignment as a randomized intervention. The
successor estimates the effect of assigned predecessor A versus B on each
target output probability, and reports absolute target error movement
separately from changes in relationships. The target-slot diagnostic supplies
neither a causal result nor continuation authority for that design.

The candidate execution unit is a complete provider invocation containing one
assigned predecessor followed by the fixed target. A randomized block contains
matched A-target and B-target invocations plus a target-sensitive reference.
The provider must expose evidence that the target physically follows the
assigned predecessor. Returned list position alone fails that gate. If only
invocation-level assignment is supported, the estimand remains the effect of
the assigned invocation; the design withholds an immediately preceding
physical-history interpretation until execution evidence supports it.

Before generating any request, the successor binds these obligations:

| Obligation | Required design artifact | Stop condition |
|---|---|---|
| Supported chronology | Provider execution evidence naming invocation membership, ordering and available timestamps | Physical predecessor attribution stays unavailable when evidence cannot identify chronology |
| Randomization | Supported assignment unit, balanced allocation rule, probabilities and registered QRNG draw/index provenance | No causal claim from deterministic alternation or unsupported circuit order |
| Carryover | Explicit admissible history length, initial-state model, target-sensitive references and any supported washout/reset behavior | Unidentified long carryover withholds the intended immediate-predecessor claim |
| Stable target | Frozen target/input identity and returned compilation checks for every occurrence | A changed target compilation invalidates the comparison |
| Reference interpretation | Target-sensitive settings spanning the response directions of interest, with reference-only payload effects declared | One stable unrelated reference cannot qualify all target responses |
| Sampling and power | Fixed completion, eligibility, dependent sampling unit, practical margin, multiplicity and power under the joint observations | A precision radius or nonsignificant drift test cannot establish adequate power or stationarity |
| Complete charge | Number of randomized blocks and invocations, reference exposures, current tariff, total ceiling and one-attempt rule | The eight-iteration tariff observation cannot price an unspecified successor |

The initial design comparison uses paired invocation blocks because the current
interface can name separate jobs while its iteration chronology remains
unqualified. A within-job randomized design remains an alternative only when
provider evidence establishes the actual controllable assignment and ordering
unit. The successor freezes block count and cost after those capabilities and
the joint power model qualify; its acquisition allocation remains zero until
then. A new compilation or schedule requires a new exact case and approval.

## Seconds and credits

The retained billing rule is one per-job price plus 1e-6 credits times the
largest iteration's `max_shots`, once per iterated job
([credit runbook](../runbooks/quandela-credit-optimization.md)). At 32,768
shots that is 1.032768. The builder recomputes the account's `qpu:ascella`
free-credit movement on six retained runs. Each movement is one new job, and
the movement equals that formula at the job's per-iteration `max_shots`.

| Retained job | Iterations | Shots per iteration | Duration | Charge |
|---|---|---|---|---|
| job-00 `739a5271-bb84-42b7-9fc3-0562ca5cef47` | 64 | 16,384 | 186 s | 1.016384 |
| job-03 `e2f30d83-17b1-402e-8b2f-319bb5a86f91` | 64 | 32,768 | 186 s | 1.032768 |
| job-04 `be11a4b0-ac35-4c6f-bfd0-689a13ac6b27` | 80 | 32,768 | 243 s | 1.032768 |
| job-05 `690c6e49-b4e7-4907-9fe3-54414d24a515` | 88 | 32,768 | 265 s | 1.032768 |
| job-06 `d54d0e9d-0d44-421a-a67b-b422f0a8febc` | 96 | 32,768 | 288 s | 1.032768 |
| job-07 `f27ad639-d947-4b99-84d6-42a9b6536d40` | 96 | 32,768 | 289 s | 1.032768 |

Job-03 used 16,384 samples and 32,768 shots per iteration and billed the same
1.032768 as the later jobs whose samples equal 32,768. The charge followed
the shot cap. Job-00 and job-03 both took 186 s at 64 iterations. The four
jobs at 32,768 samples took 243 to 289 s. The slowest retained rate among
those four is job-04, 243/80 = 3.0375 s per iteration. Eight iterations at
that rate are 24.3 s.

The written expectation is 40 s. An eight-iteration job at this sample count
has not itself been measured, so the 40 s figure leaves the unmeasured
startup inside the number and stays under the 300 s cap. The service's
behavior at `max_duration` is unobserved. Order B's second pair runs last, so
a truncated job loses that order and the reading is inconclusive.

This expectation is the retained rule applied to this budget. It becomes a
price only when `qd_platform.py plan` reads the live row. October balances
are not today's balance.

## Why a local simulation cannot answer it

Local SLOS returns each setting's ideal law from that iteration's unitary.
It carries no thermo-optic state from the previous iteration. The retained
jobs already show that Ascella's response is close to the requested law and
still carries outside-block structure that follows execution order. The
request probes target-response differences across programmed contexts.
A simulator that resets between settings does not contain an unmodeled device
state. The signed response alone leaves drift, physical order and carryover
unresolved, so it cannot identify that state as predecessor memory.

## Admission

The case admits `available` and `running` on both the Explorer row and
processor record. A running platform can queue an approved job; platform
occupancy does not establish the token's occupancy or the job's start time.
Both planning and submission pass `--admit-status running`. The token must
remain free of running and queued jobs under the existing single-job case policy.
The [Quandela runner guidance](../notes/quandela/README.md#use-in-this-repository)
distinguishes that case rule from the provider's separate running and queued
job limits. A successor that uses those limits needs a revised admission policy
and a newly bound review packet.

The retained [admission observation](../evidence/ascella-predecessor-admission/plan-status.json)
records a refusal under the earlier available-only policy. Its bytes remain
historical evidence. A fresh plan checks processor status, token occupancy,
body identity and cost under the revised policy before execution approval.

- Independent review resolves source, estimator, sampling and cost findings.
  The exact corrected case, analyzer identities and any conditional sampling
  contract freeze before approval. The case remains unapproved until then.

- `qd_platform.py plan` on a copy of the two request files. The plan reads
  the live Explorer row, the processor, the token occupancy and the body
  RemoteComputer would send. It sends nothing.
- Both platform records read `available` or `running`; calibration and maintenance remain inadmissible.
- The live price per shot keeps `1 + price * 32768` within 1.032768.
- Perceval's shot estimate for 262,144 samples is within 262,144.
- The token has no running job and no queued job. The plan refuses otherwise.
- HOM, g2, clock and dark rates are whatever that processor read reports.
  They are recorded with the plan. They are not copied from an October snapshot.
- The body digest is frozen only by retaining that plan. Until then it stays
  unfrozen.

The [running-platform plan](../evidence/ascella-predecessor-admission/running-plan.json)
passes with Explorer `running`, processor `available`, and zero token running
or queued jobs. The estimate is 262,144 shots and 1.032768 credits. The
observation binds the recorded case and source digests; a later submission
refreshes all admission checks and requires exact owner approval.

## Successor admission procedure

The current-source request uses `scripts/ascella_predecessor_current_case.py`
to derive the eight settings from the retained reference while using today's
`qd_platform.py`. Its separate case directory leaves the historical request
and simulator qualification intact. The current analyzer
`scripts/ascella_predecessor_current_analysis.py` validates the actual job
records and produces descriptive target-slot contrasts; it does not issue a
conditional confidence verdict. The runner checks the current builder and
analyzer digests along with the other case sources. A changed returned circuit
or input remains an invalid comparison, rather than evidence of history.

Build a request in a new run directory with `"$PYTHON"
scripts/ascella_predecessor_current_case.py --build --out RUN`; `--check --out
RUN` repeats the source and circuit comparison. The analyzer reads the request
from that run directory. A fresh provider plan determines actual availability,
command-schema basis and cost before any job. The simulator qualification is a
check of the same settings, not proof that the QPU compiles or orders them
identically.

The generic submit command enforces the reviewed packet for this registered
diagnostic. The token lock, externally anchored packet and atomic token-store
attempt marker bind the posted body, current source closure and one attempt.
The reviewed checkout remains quiescent during the invocation: the final source
recheck follows provider reads but does not lock external filesystem writers.
The successor needs its own reviewed packet and independent digest custody.
The historical packet retains its original bytes and cannot authorize the successor.

The case binds the bytes of six constructor and analyzer files that other
Quandela experiments share, and main moves past them: `qd_platform.py` on main
also restores a frozen Ascella command set across a driver-package change,
which three retained Ascella QPU runs used. The
[source pins](../evidence/quandela/frozen-case-source-pins.json) name, for each
bound case, the main revision whose tree holds every bound byte, and the gate
`core-ascella-predecessor-source-pin` holds each pin and requires one for every
bound case under `results/quandela/cases`. The check, plan, submit and analysis
run in a detached worktree at the pinned revision, so `acquisition_sources`
there sees the reviewed bytes; the run directory then moves to a branch off
main.

Create that worktree, run the check, copy the request into a new run
directory, and plan against the copy so the canonical case directory stays the
request. The plan sends nothing. Submit only after the owner has approved this
case and the plan's credit estimate is within 1.032768.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
CASE=results/quandela/cases/ascella_predecessor/source-compatible/cases.json
FROZEN="$HOME/worktrees/IBMQuantum/ascella-predecessor-frozen"
"$PYTHON" scripts/frozen_case_sources.py --worktree \
  docs/evidence/quandela/frozen-case-source-pins.json "$CASE" "$FROZEN"
cd "$FROZEN"
"$PYTHON" scripts/ascella_predecessor_case.py --check
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-qpu_ascella-ascella_predecessor-source-compatible
mkdir -p "$RUN"
cp results/quandela/cases/ascella_predecessor/source-compatible/cases.json \
   results/quandela/cases/ascella_predecessor/source-compatible/circuit.json "$RUN"/
"$PYTHON" scripts/qd_platform.py plan "$RUN" \
  --platform qpu:ascella --admit-status running \
  --max-credits 1.032768 \
  --expected-seconds 40 \
  --per-job-credits 1
```

After the plan, prepare and independently review the successor's exact POST
packet, retain its digest outside the run directory, and obtain exact owner
approval before constructing the submit command.

## Offline analysis and trust boundary

[`scripts/ascella_predecessor_analysis.py`](../../scripts/ascella_predecessor_analysis.py)
reads the completed run locally. The caller supplies previously retained
expected sha256 values for `submission.json` and `results.json` through
`--submission-sha256` and `--results-sha256`. The analyzer checks the canonical
case bytes and source digests, replays `qd_platform.run_facts` against
`raw/result.json`, validates the serialized Perceval body and echoed parameters,
and binds every returned circuit and input. The command writes its report to
stdout and submits zero jobs. A changed source requires a revised case; an
analysis of retained evidence keeps the frozen source revision available.

The optional `--contract PATH --contract-sha256 DIGEST` pair admits only the
conditional envelopes described above. The JSON contract contains:

| Field | Required value |
|---|---|
| `schema` | `ascella-predecessor-sampling-contract-v1` |
| `cases_sha256`, `analysis_sources` | The exact case-byte digest and its source-digest mapping |
| `sampling_model` | `iid-categorical-returned-events-within-each-iteration` |
| `stopping_rule` | `fixed-returned-event-count-with-conditional-single-photon-eligibility` |
| `eligibility` | The manifest's exact eligibility text |
| `scope` | `hypothesis-conditional-target-slot-response` |
| `physical_predecessor_attribution` | `unavailable` |
| `family_alpha`, `delta_tvd` | Decimal strings `0.05` and `0.1` |
| `frozen_utc` | A timezone-aware ISO timestamp earlier than the recorded submission |
| `evidence` | Exactly three file/digest/claim bindings for `sampling-model-review`, `stopping-rule-review`, and `temporal-limitations-review` |

Each evidence binding uses `file`, `sha256` and `claim`; the file stays beneath
the contract's directory. The externally supplied expected digest binds the
contract's bytes. Review and external custody establish the truth of its
evidence and freeze time: a self-declared timestamp and matching hashes cannot
prove historical existence. The analyzer explicitly reports that boundary.
There is no automatic contract generator or physical-history verdict. A failed,
partial or ambiguous acquisition requires diagnosis rather than automatic retry.

## What is known

| Statement | Standing |
|---|---|
| The eight settings, the requested TVDs, the three circuit hashes, and the six retained charges and durations | Known. `ascella_predecessor_case.py --check` rebuilds them from the retained files. |
| Today's price, queue, HOM, balance and body digest | Unread. The admission section is the gate. |
| Eight iterations at this budget take about 24 s, with 40 s written as the expectation | Hypothesized from the retained per-iteration times. This schedule has not been timed. |
| The common signed target-slot contrast exceeds 0.1 TVD | The response question, conditional on the sampling contract. |
| The immediate physical predecessor causes a response change | Unidentified by this case's returned metadata and four target observations. |
| On `sim:ascella` the case's eight iterations return their fixed 32,768 events each, the common target-slot contrast norm is 153/65536 and the reversal norm 71/65536, and every returned compiled circuit differs from the preregistered QPU compilation identity while every computed input matches | Measured by job `51c0552b`, read by [`ascella_predecessor_simulator.py`](../../scripts/ascella_predecessor_simulator.py) into [simulator-qualification.json](../evidence/ascella-predecessor-admission/simulator-qualification.json). The simulator has no predecessor memory, so its contrasts bound the analysis pipeline's zero, not the device's. The frozen analyzer reads only the QPU case bytes, and its digest stays bound by the case. |
