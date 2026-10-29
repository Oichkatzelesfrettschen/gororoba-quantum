# Ascella predecessor intervention

Status: the corrected offline request and analyzer are built. The case remains
unapproved; the sampling contract, independent review and Perceval body digest
remain outstanding. The case authorizes zero provider submissions.

The builder is [`scripts/ascella_predecessor_case.py`](../../scripts/ascella_predecessor_case.py).
The retained request is
[`results/quandela/cases/ascella_predecessor/job-00/`](../../results/quandela/cases/ascella_predecessor/job-00/cases.json).
`cases.json` sha256 `9778e3a35512bcbf80b79d2c36d2530d13057b313926333921a61bb9c940a2b9`.
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

One job, family `ascella_predecessor`, name `ascella_predecessor/job-00`.
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

## Procedure after approval

Run the check, copy the request into a new run directory, and plan against
the copy so the canonical case directory stays the request. The plan sends
nothing. Submit only after the owner has approved this case and the plan's
credit estimate is within 1.032768.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
"$PYTHON" scripts/ascella_predecessor_case.py --check
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-qpu_ascella-ascella_predecessor-job-00
mkdir -p "$RUN"
cp results/quandela/cases/ascella_predecessor/job-00/cases.json \
   results/quandela/cases/ascella_predecessor/job-00/circuit.json "$RUN"/
"$PYTHON" scripts/qd_platform.py plan "$RUN" \
  --platform qpu:ascella --admit-status running \
  --max-credits 1.032768 \
  --expected-seconds 40 \
  --per-job-credits 1
```

After that plan is retained and the approval text is the owner's:

```sh
"$PYTHON" scripts/qd_platform.py submit "$RUN" \
  --platform qpu:ascella --admit-status running \
  --max-credits 1.032768 \
  --expected-seconds 40 \
  --per-job-credits 1 \
  --approval "APPROVAL TEXT"
"$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600
```

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
