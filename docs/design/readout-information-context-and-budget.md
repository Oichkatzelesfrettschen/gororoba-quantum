# Paired readout errors under controlled actor preparation

The [Fez full-register pilot findings](../evidence/ibm-fez-actor-pilot/findings.md)
report descriptive error tables and retain the acquisition's inferential limits.

This unapproved IBM design asks whether changing preparation on disjoint actor
qubits changes fixed reporters' error response, and whether a pair's
computational-basis parity error beats its cleaner individual bit by a frozen
margin. Preparation, gate, readout, reconstruction and drift errors all enter
the observed channel; a result does not identify a unique physical cause.
The information-order calculation below is a separate classical research
control, not a primary endpoint of the proposed IBM acquisition.

The [OpenAI mathematics collection, family 119](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/119.md)
describes the Courtade–Kumar information-contraction result for uniform inputs
and independent symmetric bit-flip noise. The collection labels its outputs
research data with varying verification. The two-bit controls below stand on
their own finite calculation; a QPU measurement neither proves nor disproves
the general mathematical statement. The original question predates the
collection: [Courtade and Kumar (2013)](https://doi.org/10.1109/ISIT.2013.6620221).

## Exact model and mutation

Let X be two independent uniform input bits and Y the full two-bit output.
Let F be the XOR of the two inputs. The baseline model independently flips
each bit with probability p = 1/4. Its two coordinate information values are
`1-h2(1/4) = 0.1887218755` bits, and its parity information is
`1-h2(3/8) = 0.0455659971` bits. Here `h2` is binary entropy.

The positive mutation flips both bits together with probability 1/4 and leaves
both unchanged otherwise. Each one-bit flip marginal stays 1/4, while parity is
always preserved: the coordinate information stays `0.1887218755` bits and
the parity information becomes 1 bit. The
[finite-channel control](../../scripts/readout_information_controls.py)
enumerates the exact rational probabilities and independently checks the
entropy identities. The example is a mathematical sensitivity control, not a
prediction that a device has a 25% readout error.

An observed positive value of
`I(F;Y) - max(I(X0;Y), I(X1;Y))` contradicts the independent symmetric-channel
model when input distribution, association and uncertainty assumptions hold.
The contrast includes preparation and measurement. Equal one-bit marginals do
not establish independent errors, and a negative or unresolved contrast does
not establish that a channel is independent. Noise context, input imbalance,
time drift and output-label mistakes remain alternative explanations.

## Proposed acquisition and falsifiers

### Fixed reporters and changing actors

The first IBM candidate holds reporter preparation and the measured register
fixed while changing activity on disjoint actor qubits. A controlled assignment
must be randomized at the unit the provider actually executes, with assignment
probabilities and carryover assumptions retained. Counterbalancing alone does
not identify a causal effect. If assignment or exposure is not qualified, the
result is an activity-associated response contrast. Equal measurement
instructions do not establish identical physical readout pulses; served
schedule evidence and its limits belong in the admission record.

Before discovery, freeze shot validity, candidate eligibility, input patterns,
selection, assignment, the maximum number of pairs, decision rules and the
error budget. Freeze selected pairs and any trained predictor after discovery
and before confirmation data are opened. A later acquisition can test
persistence; concealed data from the same acquisition supports a holdout but
does not by itself establish persistence. IBM does not guarantee PUB order or
one batch, so a later list entry is not proof of later physical execution.

For output bits compared with their commanded preparation, let `p_ab` be the
probability of paired error bits `(a,b)`. The parity improvement over the
better individual bit is `G = min(p_11-p_01, p_11-p_10)`. A per-pair
intersection-union decision requires both one-sided tests to clear a frozen
practical margin; the family of pairs and other claims needs its own error
allocation. The two component tests do not themselves require an additional
division of the per-pair level. A failure to reject is inconclusive, not
equivalence. A separate upper-bound test and frozen equivalence region support
an equivalence decision.

Write `s = p_11`, `r = p_01 + p_10` and `d = p_01 - p_10`. Then
`G = s - r/2 - |d|/2`. A context comparison must report the change in `G`,
parity error `r` and each marginal error together. Additional simultaneous
errors can increase `G` while leaving parity error unchanged and worsening
both individual bits. These descriptive quantities need separate registered
uncertainty and multiplicity rules before supporting confirmatory claims.

For error signs `Z_i = (-1)**E_i`, `G` equals
`(E[Z_i Z_j] - max(E[Z_i], E[Z_j])) / 2`. Under the specific model
`E_i = B xor U_i` with mutually independent common and private flips, even
group parity signs cancel `B` and odd group parity signs retain it. The model
also implies `E[Z_1 Z_2 Z_3] = E[Z_1] E[Z_2 Z_3]`, and the two analogous
permutations. These equations are falsifiable model restrictions; agreement
does not identify a physical mechanism. A fourth cumulant is likewise not a
four-body mechanism identifier: four copies of a shared Bernoulli error have
fourth cumulant `p(1-p)(1-6p(1-p))`, including zero for nontrivial values of
`p`. A Cayley-Dickson claim additionally needs the separate sign mutation and
interference test.

For fixed marginal error probabilities, `G <= 2 p_min - p_max`, attained by
the maximally shared joint distribution. Consequently, `G > delta` requires
`p_max + delta < 2 p_min`. An empirical estimate is not a population bound;
candidate screening must account for estimation uncertainty. The
`parity_error_summary` calculation returns exact fractions from decoded shot
bits and is descriptive. It supplies neither confidence bounds nor an
admission decision. Input patterns remain separate unless a preregistered
pooled estimand is justified.

An illustrative one-sided Hoeffding intersection-union bound for a fixed-size
IID sample uses the fact that each component
has a per-shot difference in `[-1,1]`, and the common radius is
`sqrt(2 log(1/alpha)/n)`. The lower bound for `G` is the smaller of the two
component lower bounds. This construction controls one pair at its declared
level, not a family of pairs. For 100,000 shots with 3,000 joint errors and
500 of each isolated error, `G_hat = 0.025` and the 5% illustrative lower
bound is approximately 0.0173. The hypothetical frequencies are not hardware
predictions. The arithmetic appears only in a test, not an exported analyzer
or CLI result. Its IID and fixed-completion assumptions need evidence and
independent review. One exact finite-sample boundary-null enumeration is a
checked example, not a proof of least favorability over the composite null.

For one pair at one-sided alpha 0.05, the same radius is approximately
0.0173 at 20,000 shots. If the smaller marginal error is 0.01, the population
feasibility bound limits `G` to at most 0.01. The illustrative Hoeffding
construction therefore cannot certify a positive improvement at that sample
size when the sample marginals also obey the 0.01 cap. A valid sharper paired
method might have useful power; a realistic case must establish that with its
own assumptions, multiplicity, marginal ranges and shot budget. The existing
[empirical Bernstein contract](../../gororoba_quantum/QPU_OPTIMIZATION.md)
belongs to other registered families and does not automatically admit this
case. For a paired score with range 2, sample variance 0.02, 20,000 shots and a
one-sided tail 0.05, the full stated radius is approximately 0.00358, including
the range-dependent correction. At 8,192 shots it is approximately 0.00635.
These are hypothetical fixed-variance calculations before multiplicity or
power allowances, not a claim that a 0.005 effect is resolvable. A future
analyzer needs separate score variances, an independently reviewed coverage and
sampling contract, numerical outward rounding and fail-closed admission. A
choice between empirical Bernstein and another interval needs a prespecified
method and appropriate error allocation.

The case retains shot order, preparation, actor assignment, block identity,
mapping and available timing alongside joint counts. It specifies dependence
assumptions and uses inference justified under them. A purge window, alternating
shots, or a sequential method alone does not establish independence. Each
endpoint reports one of invalid acquisition, inconclusive, confirmed effect,
or bounded equivalence. A diagnostic burst search has its own exposure and
requires measured wall-clock timing for rate claims.

1. Freeze the reporter-pair candidate universe, calibration-based eligibility,
   physical mapping rule, actor set, input patterns, allocation and validity
   rules before discovery. Freeze selected reporter pairs before confirmation.
2. Build `actor_alternatives` for each chosen input and fixed measured register.
   Randomize actor assignment at an execution unit whose ordering and identity
   the provider exposes. Retain assignment probabilities and predeclare
   carryover assumptions. Compare compiled arm duration and reporter exposure;
   an unresolved mismatch remains a confound.
3. Retain complete joint outcomes, input and actor assignments, calibration,
   block identity and all available timing. Decode error bits against each
   commanded preparation and calculate `G` separately by input and context.
4. Freeze the actor response and paired parity decisions, including practical
   margins, multiplicity, selection, dependence and confirmation rules. A
   missing input stratum, ambiguous order, changed map or failed reference makes
   the affected claim inconclusive. Calibration and repeated shots do not alone
   prove stationarity or independent observations.

The classical information-order positive mutation remains an exploratory
model check. Any fixed bijection on the full output preserves all three mutual
information values and is an invariance check, not a negative control. An
independently assigned source/outcome association permutation or an explicitly
specified dependence-breaking channel, changed input weights, and a preparation
fault are separate alternatives; their allocation and any randomness require
the repository's recorded quantum-random source. A held-out confirmation and a
justified error bound are prerequisites for a device claim; this design does
not supply a completed uncertainty method.

The [logical circuit catalogue](../../scripts/readout_information_circuits.py)
constructs both contexts and all four inputs for a selected target pair and
measures every register bit. The catalogue is not an execution schedule or a
native case: it chooses neither physical layout nor assignment order, timing,
calibration, or provider. Ideal-state tests verify target preparation and
full-register mapping on a small statevector and check all 156 logical bits
structurally; they do not simulate a 156-qubit device. A source-bound provider
case must add the missing allocation, compilation, ordering, cost and
uncertainty controls.

The same catalogue's `actor_alternatives` constructs all four reporter inputs
with a specified, disjoint nonempty set of actor qubits either unexcited or
prepared with `x`, and measures the entire logical register in every arm.
The preparation intervention changes actor state as well as drive activity.
The constructor selects no physical layout, assignment order, repetitions or
timing; equal compiled duration and equal physical measurement pulses are
unverified. It is an unapproved source catalogue, not a randomized case.
The separate `padded_actor_alternatives` accepts per-qubit X durations in
ticks and pads each preparation to the maximum selected duration. It requires
caller-supplied durations and selects no physical layout. Native compilation
and provider scheduling remain independent checks.

The separate [IQM native-source catalogue](../../scripts/readout_information_iqm.py)
constructs the same unassigned preparations using `prx` angles in radians and a
single ordered measurement locus. Its tests compare every preparation with the
logical catalogue. The native-source catalogue has no job body, shot count,
randomized schedule or approval, and its tests do not establish provider
compilation or execution. A 28 October read-only Garnet dynamic-architecture
observation listed 20 qubits and single-qubit `prx` and `measure` loci for all
20. That observation does not establish that a 20-qubit measurement is admitted
as one joint operation or that a particular case fits the 2.50-credit limit.

The classical control module also computes descriptive plug-in information
from four nonempty integer-count rows, weighting each input stratum by one
quarter. The tests reconstruct both exact synthetic channels. Reweighting does
not randomize the actual acquisition order, correct drift, authenticate source
association or provide confidence bounds; no retained device result enters
this calculation without a separate acquisition and analysis contract.

An illustrative, conservative 99% simultaneous information-order bound for a
fixed number `n` of completed observations in each input stratum
and context. For one pair, a union bound covers 32 output-cell events. If each
cell indicator has a predictable conditional mean and the stratum membership
and fixed sample schedule satisfy the martingale assumptions, the two-sided
cell radius is `sqrt(log(6400)/(2n))`. For uniformly weighted inputs, the
corresponding joint total-variation radius is at most twice that cell radius,
capped at one. Entropy continuity for the four-output and eight joint outcomes
then bounds each information error; twice their sum bounds the error of the
parity-minus-maximum-coordinate contrast. The predictable target is the
realized average of conditional probabilities, which can vary with history; it
is not automatically a stationary channel or a causal context effect.

At 20,000 observations per stratum the computed contrast radius is about 1.03
bits, larger than the largest possible one-bit contrast. This particular bound
therefore cannot certify a positive contrast at that sample size. A sharper
justified method or multiple fixed-size blocks could change the result. The
test-only calculation illustrates feasibility; it does not provide an
outward-rounded admission decision, correct confounding, or justify stopping
based on observed outcomes. The fixed completion, ordering, multiplicity and
predictability assumptions need independent review before any device claim.
The continuity and concentration ingredients are described by
[Audenaert](https://doi.org/10.1088/1751-8113/40/28/S18) and
[Hoeffding](https://doi.org/10.1214/aop/1176996452).

A read-only IBM Target query on 28 October 2026 found 156 physical qubits on
`ibm_kingston`, with `x` and `measure` supported on each qubit. That observation
qualifies neither a logical-to-physical mapping nor a served schedule, duration,
or future calibration. The current logical catalogue has one selected target
pair per source; simultaneous multiple-pair coverage requires a separately
specified input assignment and covariance contract.

An offline preliminary layout uses reporters 0 and 1 and actor 2. The retained
Kingston snapshot's 14 October 2026 calibration lists coupling edges 0-1 and
1-2 and readout-error metrics 0.0126953125 and 0.0084228515625 for reporters
0 and 1. Those metrics do not establish the error-bit marginals under the
candidate intervention. A local Qiskit `optimization_level=0`, ALAP schedule
using a reconstructed 156-qubit Target containing only the snapshot's `x`
and `measure` instructions and an identity layout places all measurements at
tick 0 for the idle `00` arm and tick 8 for every other arm; the snapshot has
4 ns ticks. The 32 ns discrepancy is a concrete source-level schedule
confound, not evidence about served pulses. The offline
[schedule replay](../../scripts/readout_actor_schedule_replay.py) rebuilds the
restricted Target from the retained snapshot, prints the snapshot digest and
the replay and constructor source digests, checks compiled X preparations and
measurement mapping, and reports padded and unpadded schedules under ASAP and
ALAP. The stdout is a diagnostic, not a retained byte-checked receipt; the
restricted Target omits the full provider Target and scheduler. A complete
fresh Target, compilation and readout evidence remain required before physical
admission.

A read-only primary-account query at 2026-10-28 18:41 UTC reported 68 rolling
seconds, Kingston active with 42 queued jobs, and a configured 0--2 ms
repetition range. The separate Heron published 20 microsecond floor still
applies. A full live Target read at 18:42--18:43 UTC reported `dt = 4 ns`,
32 ns X, 2.180 microsecond measurement and 2.212 microsecond reset on every
one of its 156 qubits, with calibration timestamp 2026-10-28 17:56:30 UTC.
For reporters 0 and 1 and actor 2, local level-zero compilation with identity
layout placed the unpadded `idle 00` measurement at tick 0 and the other seven
at tick 8. With per-qubit padding derived from that Target, both ASAP and ALAP
placed every measurement at tick 8 and the last measurement end at tick 553.
These local observations have no retained replay producer or digest and do not
establish a provider-served schedule, physical pulses, initialization or
carryover. A new case must bind its own full Target and compilation evidence.

## Full-register delay-and-activity pilot

The [operational case](readout-actor-delay-qualification.json) fixes a
156-qubit measured register, reporters 0 and 1, and actor 2 on `ibm_kingston`.
All remaining qubits receive ground preparation and terminal measurement.
Every shot retains the complete register. Declared pair and sign-parity
projections use those same shots; separate component acquisitions cannot
replace them. Qubit 155 supplies a distant descriptive projection, rather
than a qualified spatial control. Fresh connectivity and scheduling evidence
bound every claim about physical separation.

The pilot measures preparation-associated activity response and compares
three repetition-delay conditions. The pilot qualifies the acquisition and
decoding software on this layout. The pilot neither confirms parity protection
nor establishes initialization adequacy, causal directed influence or
chip-wide protection. A local noise simulation cannot determine the device's
unmodeled joint error process or its delay response.

### Frozen allocation and complete cost scenario

| Stage | Repetition delay | Shots per preparation and actor arm | Conditions | Full-register shots | Modeled seconds including one job overhead |
|---|---:|---:|---:|---:|---:|
| Pilot | 30 microseconds | 4,096 | 8 | 32,768 | 3.128005632 |
| Pilot | 50 microseconds | 4,096 | 8 | 32,768 | 3.783365632 |
| Longer-delay reference | 250 microseconds | 1,024 | 8 | 8,192 | 4.084241408 |
| Discovery | Unallocated | 0 | 0 | 0 | 0 |
| Confirmation | Unallocated | 0 | 0 | 0 | 0 |
| Total | Three jobs, 24 PUBs | | | 73,728 | 10.995612672 |

Each delay tier contains reporter preparations 00, 01, 10 and 11 under both
idle and excited actor preparation. The operational input integer places its
least significant bit on reporter 0. Actor activity means one X preparation
on qubit 2, rather than a repeated gate drive. Idle actors still receive
terminal readout. The compiler pads idle wires from the fresh Target and
requires matched terminal measurement start ticks across all conditions.
Compilation establishes local instruction timing; physical pulse equivalence
requires additional provider evidence.

The scenario uses a 2.212 microsecond compiled body, a 2.212 microsecond
initialization proxy, and two seconds overhead per job. The retained
[platform snapshot](../evidence/heron_platform/targets.json) records the
250-microsecond default delay. The
[cost regression](../../tests/scripts/test_readout_actor_cost_model.py)
loads the actual operational JSON, checks the runner's three batches and all
24 condition allocations, and reproduces the total using exact nanosecond
arithmetic. These historical duration inputs support sizing; fresh full-Target
compilation governs admission. The
[execution-time reference](../notes/ibm_quantum/estimate-job-run-time.md)
documents the initialization proxy and approximate overhead. Provider splitting
can add overhead within a submitted job.

Each job requests a six-second execution ceiling. Three ceilings sum to
18 seconds inside the complete 20-second program envelope. The 48-second
reserve gives an immediate per-check threshold of 66 freshly reported seconds
on the selected IBM instance. The submitter repeats that full threshold before
each job, including after earlier charges post. A 68-second start can therefore
produce a partial acquisition: a posted charge above two seconds triggers a
later refusal. A conservative 78-second start covers the repeated checks after
two earlier six-second ceilings, conditional on provider accounting and outside
usage. The [acquisition review](../evidence/readout-actor-acquisition-review/README.md)
records that operational limitation separately from the protected 48-second
reserve. The [budget admission closure](../evidence/readout-actor-acquisition-review/budget-admission-closure.md)
binds the documented backup instance with an observed 160 seconds and a fresh
compiled case; the default primary remains below the conservative start rule.
Quotas remain separate. Historical balances establish neither available time nor an allocation.
The runner refuses an estimated batch above six seconds,
aggregate ceilings above 20 seconds, or insufficient quota after reserve.
The two-second envelope remainder authorizes zero additional jobs or retries.
Provider enforcement and returned billing remain separate checks.

Runtime `init_qubits` requests implicit initialization. An explicit circuit
reset is a separate operation; this constructor contains preparation, delay,
barrier and measurement instructions. The estimator's Target-reset proxy
establishes a cost input, rather than physical reset behavior or successful
state preparation. Repetition delay forms part of each condition's definition.

### Sampling, controls and decision boundaries

The pair and projections are fixed before acquisition. The pilot uses fixed
counts and reports every condition. Outcome-dependent stopping, pair selection,
post-acquisition exclusions and pooling across preparations are prohibited.
The program has three contiguous shot/delay tiers. Submitted PUB order lacks
a physical execution-order guarantee, and the pilot has no randomized causal
assignment. Delay and acquisition period remain associated. Activity contrasts
therefore remain preparation-associated contrasts, rather than identified
causal effects. A future causal case randomizes at a provider-supported unit,
retains assignment probabilities, and freezes carryover assumptions.

The 250-microsecond tier supplies pattern- and actor-matched preparation
references. Similar marginals cannot establish similar temporal dependence.
Within-PUB shot order supports recorded-lag diagnostics only to the extent the
provider's ordering evidence permits. An immediate physical predecessor,
wall-clock lag and cross-PUB chronology remain unknown when the execution
records omit them. A fitted decorrelation lag or a purge window cannot certify
independence against arbitrary slow drift.

The analysis derives exact error cells, both paired-score moments and their
covariance, parity error `r`, marginal errors, shared errors `s`, imbalance
`d`, and `G = s-r/2-|d|/2`. Every actor comparison reports `Delta G`,
`Delta r`, `Delta p_0` and `Delta p_1` together. Declared triplet sign moments
support descriptive common/private-flip model checks. A positive change in
`G` can accompany unchanged parity error and worse constituent bits.
The model checks identify compatibility, rather than a physical mechanism.
Raw full-register records support later analyses under separate declarations.
The sparse collector and adjudicator emit the four cells and group parity
counts; derived quantities use those counts directly. For counts
`(n00,n01,n10,n11)` and total `n`, the worksheet uses
`s=n11/n`, `r=(n01+n10)/n`, `d=(n01-n10)/n`,
`p_0=(n10+n11)/n`, and `p_1=(n01+n11)/n`.
`paired_component_moments` in the
[exact controls](../../scripts/readout_information_controls.py) supplies
separate sample variances and covariance. These derived values remain
descriptive and cannot promote the collector's inference status.

Operational outcomes have the following boundaries:

- Valid descriptive acquisition: exact-case, compiled timing, measurement map,
  raw receipt, completeness and accounting checks pass. Every scientific
  qualification remains separate.
- Invalid acquisition: an observed binding, mapping, compilation or raw-evidence
  mismatch rejects the corresponding acquisition. Partial completed PUBs
  remain retained and descriptive, with missing conditions explicitly listed.
- Incomplete qualification: absent records, unresolved scheduling or a failed
  accounting check withhold the affected operational conclusion.

The analyzer emits `hardware_verdict: null`. The pilot assigns zero inferential
alpha and issues neither superiority nor equivalence decisions. Initialization
and carryover qualification remain unresolved even after a valid descriptive
acquisition. A later case supplies numerical tolerances, supported sampling
assumptions, references, power and complete costs; the pilot supplies planning
information and grants zero automatic continuation authority.

### Pattern-specific feasibility and confirmation successor

The retained compilation fingerprint for reporters 0 and 1 records directional
assignment metrics `(0.002197265625, 0.0029296875)` after commanded zero and
`(0.0048828125, 0.010498046875)` after commanded one. The naming follows
`live_run.py`'s `prob_meas1_prep0` and `prob_meas0_prep1` fields. Substitution
into `2 p_min-p_max` gives 0.00146484375 for ground preparation and
-0.000732421875 for excited preparation. Calibration assignment metrics are
not experimental error marginals. Their asymmetry nevertheless demonstrates
why averaged calibration screening cannot qualify every preparation pattern.
The pilot retains all four patterns instead of discarding a difficult pattern.

A successor freezes selected pairs, each tested preparation, practical margin,
family allocation and confirmation shots before opening confirmation data.
The per-pair intersection-union test uses the full per-pair alpha for each
component and requires both to pass; multiplicity across pairs and conditions
is separate. The two scores share their exact four-cell law. Power uses that
joint law, rather than independently generated component fluctuations.
A sample-variance scenario narrows a Bernstein planning radius; a valid
sampling contract determines whether that expression applies to hardware.
A target radius alone supplies neither power nor a fixed stopping rule.

### Submit-free preparation and evidence binding

The [Fez alternative](readout-actor-fez-delay-qualification.json) is an
unapproved descriptive candidate. A 29 October 2026 live Target compilation
finds matched measurement starts across its 24 conditions and flags none of
reporters 0 and 1, actor 2, or exploratory qubit 154. The same review flags
Fez qubit 155 for low T2 and Marrakesh reporter 1 for 0.157 readout error;
the original 155 projection therefore changes to 154 on Fez. All 156
qubits remain measured. These calibration observations and queue depths are
time-dependent, and a fresh Target and admission check decide any later run.
The local timing check does not establish physical initialization or
carryover. The three approved Kingston jobs remain a separate outstanding
liability: a Fez submission requires an independently reviewed case, fresh
quota evidence, and a mechanical budget bound covering both programs' unsettled
ceilings and the reserve. The existing per-case admission alone does not
establish that combined bound.

The operational JSON is an unapproved review candidate. The following command
builds a fresh plan and QPY archive, reads current backend and quota information,
and submits zero jobs:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
"$PYTHON" gororoba_quantum/live_run.py --family readout-actor \
  --actor-case docs/design/readout-actor-delay-qualification.json \
  --out results/live --max-execution-seconds 6 --max-total-execution-seconds 20
```

The fresh plan checks backend discovery, permitted delays, full measured width,
Target duration proxies, matched compiled exposure and all allocations.
The planning function performs zero quota reads. A separate read-only usage
observation supplies the review's admission evidence; submission refreshes
quota before every batch.
The [retained submit-free plan](../../results/live/2026-10-29T002839.028671Z/UNAPPROVED_CASE.md)
and its [record](../../results/live/2026-10-29T002839.028671Z/record.json)
bind all 24 compiled conditions. Every terminal measurement starts at tick 8;
the three modeled job costs match the allocation table. The record has state
`planned`, carries descriptive-only inference, and contains zero submission
records. The local compile establishes scheduled timing within Qiskit;
provider-served timing and physical initialization remain unmeasured.
The case writer binds the plan, operational JSON and QPY archive into a
reviewable written case. Exact-case approval precedes the binding dry-run and
submit invocation. A changed source closure, layout, timing, shot allocation,
account or delay requires the existing approved-record comparison and renewed
review when that comparison refuses the change.
Independently retained submission and collection digest anchors bind analysis;
recomputing an anchor from the analyzed directory supplies consistency only.
IQM's provider-enforced 2.50-credit gate remains a separate execution block.

### Runner and sampling integration gates

The [full-PUB actor family](../../gororoba_quantum/readout_actor_family.py)
registers `live_run.py --family readout-actor --actor-case CASE.json`. The
operational case names the backend, complete measured width, two reporters,
disjoint actors, declared pair and group projections, each allocation's arm,
preparation, stage, shots and repetition delay, resource ceilings, and explicit
reference, carryover and selection rules. Its inference field accepts
`descriptive`; a declaration cannot enable a confirmatory verdict. The CLI
requires an output directory and execution ceilings matching the case.

The family plans before generic dense ideals are constructed. It compiles on
the complete fresh Target, checks preparation and measurement wiring, preserves
the full-register barrier, and requires equal terminal-measurement start ticks.
Each circuit remains a whole PUB with one synchronization owner. Generic packed
components keep their strict ownership validation. The family binds its local
source dependency closure, bounded prepared-bit ideals, QPY archive, calibration,
account instance and explicit allocation to the existing approved-record checks.
Shot and delay tiers create separate submission batches; their summed ceilings
and the account reserve must fit the fresh quota. Cost estimates remain
scenarios rather than evidence of physical initialization or provider scheduling.

The unapproved case writer binds the record, QPY and operational case bytes,
and gives a binding-run command that compares every fresh plan against the
separately reviewed record. Actor submission requires that reviewed record and
its digest even when called directly. Before the first provider call, a
digest-keyed marker under the repository's common Git directory is created
exclusively; linked worktrees and copied reviewed directories share that marker.
The marker also closes the attempt if a process fails before provider contact.
Separate clones or hosts do not share this local registry and require an
independent coordination mechanism. The marker and hashes establish local
one-time use and byte identity, not the authenticity of the user's review.

The generic collector and legacy adjudicator retain their dense and `int64`
paths for existing families. Actor records dispatch before those paths and
retain full shot strings before computing declared projections. Collection
requires `--collect RUN --actor-record-sha256 SHA256`, where the digest is an
independently retained submission-record anchor. Offline adjudication uses
`adjudicate.py RUN --actor-collection-sha256 SHA256`, binding the immutable
collection receipt and its acquisition artifacts. A locally recomputed digest
establishes consistency only; the operator must retain the anchor independently
of the files being verified. Missing or changed bindings reject analysis.

The [integration regression](../../tests/gororoba_quantum/test_readout_actor_family.py)
uses a 156-bit synthetic backend and actual raw serialization to exercise
planning, mocked approved submission, collection and offline adjudication.
It makes dense conversion fail if reached and tests changed approval, quota,
instance, source, calibration, preparation and measurement mappings. Mocked
submission checks establish software behavior, not hardware alignment or cost.
The current [ownership regression](../../tests/scripts/test_readout_barrier_ownership.py)
shows that component-local barriers pass, while the validator rejects both a
cross-component synchronization barrier and a cross-component CZ. A future
versioned packed-component validator would need to distinguish those operations
without discarding synchronization or weakening computational-gate ownership.
The full-PUB route avoids that reconstruction and validates its restricted
preparation, delay, full barrier and measurement instruction set directly.
The case must check its required synchronization against compiled and served
schedule evidence; source instruction order alone is insufficient.
Ordered raw bitstrings within one PUB do not establish the
immediately preceding physical circuit in a mixed-PUB job: the provider does
not guarantee PUB order or a single batch, and retained execution windows need
not be per-shot times. Missing predecessor evidence withholds any claim that
requires it.

| Stage | Observed execution path | Sparse-case obligation |
|---|---|---|
| Construction | The full-PUB actor family validates physical preparation, complete measurement wiring and a global synchronization barrier. | Freeze a complete operational case and retain the compiled evidence. |
| Planning and submission | Actor planning uses prepared-bit ideals and existing approval checks before generic dense group construction. | Review the exact allocation, cost scenario, source closure and QPY; approve the case separately. |
| Raw serialization | `write_raw_result` retains ordered bitstrings and an immutable acquisition index. | Retain submission and collection digest anchors independently of the analyzed files. |
| Collection and adjudication | Actor records dispatch to sparse projection before dense conversion or `int64` narrowing. | Validate the complete ledger, receipt and QPY chain; preserve full raw shots. |
| Inference | The current paired helpers return descriptive values. | Validate assignment, ordering, sampling and multiplicity evidence before a separately reviewed analyzer issues a decision. |

Projecting multiple components from the same full-register shot preserves the
supplied same-index relationship. Separate component acquisitions cannot
establish simultaneous cross-component failure. Equal list lengths are a
structural check, not independent proof that the provider aligned registers.
The receipt must connect the independently approved submission identity and QPY
digest to the actual job and PUB, register and measurement map, preparation,
raw index and file digests. A receipt recomputed from the same untrusted
manifest establishes internal consistency only. Provider-result alignment
requires a documented contract or supporting evidence beyond those hashes.
`snapshot_metrics` updates the raw index as metrics arrive, so a receipt that
binds an index must name the exact indexed snapshot and its lifecycle; an
earlier index digest cannot authenticate a later rewrite.
`write_raw_result` writes a separate `acquisition-index.json` containing the
job identity and raw PUB and result-metadata hashes. Atomic create-once
publication rejects a different existing snapshot. The raw result files use
the same create-once publication, and a per-job advisory lock serializes raw
collection and metrics updates. Concurrent identical collectors preserve the
same indexed bytes; a conflicting collector refuses the existing raw file.
Metrics revisions continue through the existing index and cannot alter those snapshot bytes. The snapshot
is also written by `preserve_raw`, whose weaker checks do not authenticate a
submission. The actor collector binds that snapshot, QPY and projection
receipts to an externally supplied submission-record digest; the offline
adjudicator requires the independently retained collection digest. Operational
provenance therefore depends on the origin and retention of those external
anchors. Recomputing the expected digest from mutable files establishes
consistency only. Neither the anchor chain nor matching bit counts establishes
physical shot alignment or statistical independence.
Adjudication checks every raw PUB and the result-metadata file named by the
anchored acquisition index, using bounded file reads. That byte check does not
establish that the provider's metadata proves physical shot ordering.
The offline retention tests include a collector process that exits before
publishing its acquisition index; recollection acquires the released job lock
and binds the raw bytes already written. That test covers the observed local
filesystem behavior, not arbitrary filesystem failures or provider provenance.

The local `project_reporter_shots` helper projects ordered single-register
Qiskit bitstrings onto two specified classical-bit indices without constructing
a `2**156` distribution. It rejects malformed or oversized input and preserves
the supplied list order, up to one million shots and 100 million input
characters per call. The helper does not authenticate the source register,
physical mapping, provider timing or predecessor identity, and is not wired
into the IBM collector or an admitted acquisition case.

The separate [sparse PUB projection](../../scripts/readout_sparse_projection.py)
accepts complete declared register, classical-bit, logical-bit, physical-bit and
preparation maps, validates equal register lengths and bitstrings, and computes
only declared pair error tables and group error-parity counts. It pairs list
positions from one PUB without mutating the full input. Its ordered register
hashes and manifest digest describe the supplied data; neither authenticates a
provider response or proves physical cross-register alignment. The projection
is not wired into collection, QPY validation or confirmatory inference.

The offline [receipt verifier](../../scripts/readout_sparse_receipt.py) checks a
caller-supplied receipt digest, the bound bytes and the QPY measurement wiring
before projecting. The receipt's `manifest_sha256` binds the original JSON
bytes; the projection's `manifest_canonical_sha256` binds a canonical JSON
serialization. The verifier returns the former as `manifest_bytes_sha256`.
The verifier checks neither the active actor's gates nor preparation semantics,
approval or provider provenance; its family label is supplied by the caller.
QPY byte limits and decoded-size checks do not bound the decoder's peak
resources, so QPY input needs an independent trust and resource boundary.
The verifier has no production collection or adjudication route and issues no
statistical decision.

A separate synthetic probe of input construction, serialization, JSON and QPY
parsing, receipt checking and projection used 180,345 shots across two
registers totaling 156 bits, one pair and one group. Python 3.14.7 and NumPy
2.5.4 reported cumulative peak RSS of 98,744 KiB initially, 149,096 KiB after
input construction and 206,824 KiB after serialization, verification and
projection. The raw JSON occupied 29,576,760 bytes and elapsed time was 0.34 s.
The synthetic receipt and its anchor share an origin; the probe measures
consistency and local resource use, not provenance or provider collection.

A deterministic local probe of 180,345 distinct 156-bit strings, one pair and
one three-bit group used 29,035,545 declared work units. On Python 3.14.7 and
NumPy 2.5.4, process high-water RSS was 70,160 KiB after constructing the
input and 73,264 KiB after projection, an observed increase of 3,104 KiB; the
projection took 0.064 s. The observation excludes raw JSON loading, provider
collection, input construction and larger projection families. High-water RSS
is not an exact allocation, and the work cap is not a universal memory or
runtime guarantee.

A separate local probe includes creation of 180,345 distinct strings, JSON
serialization and `json.loads` before projection. On Python 3.14.7 and NumPy
2.5.4, process high-water RSS was 31,716 KiB initially, 70,244 KiB after input
construction, 126,180 KiB after serialization, 126,180 KiB after parsing, and
127,252 KiB after projection. The JSON payload was 28,674,957 bytes; total
elapsed time was 0.254 s. High-water readings are cumulative, and Python's
allocator can retain freed input memory. This test includes synthetic parsing
but not provider collection, QPY parsing, receipt validation or real results.

The full-PUB offline [audit test](../../tests/gororoba_quantum/test_readout_actor_family.py)
executes planning, fake submission, raw serialization, receipt verification and
adjudication for one 156-bit PUB with 40,000 synthetic shots. Linux
`/proc/self/status` reports initial `VmRSS` and `VmHWM` of 227,428 KiB and
final `VmRSS` of 264,932 KiB and `VmHWM` of 276,764 KiB on the local pinned
Python 3.14.7 run. The process high-water includes imports and input creation;
the fixture's identical synthetic shots do not model provider output or bound
other shot distributions. Replay the measurement with:

```sh
"$PYTHON" -m pytest -q -s -m audit tests/gororoba_quantum/test_readout_actor_family.py::test_full_width_collection_includes_input_and_parsing_memory
```

```sh
"$PYTHON" - <<'PY'
import resource
import sys
import time
sys.path.insert(0, "scripts")
from readout_sparse_projection import project_pub
width, shots = 156, 180345
raw = {"pub_name": "wide", "pub_index": 0, "registers": {
    "c": {"num_bits": width, "num_shots": shots,
          "bitstrings": [format(index, "0156b") for index in range(shots)]}}}
manifest = {
    "schema": "readout-sparse-projection-v1", "condition": "wide-ground",
    "pub_name": "wide", "pub_index": 0, "registers": {"c": width},
    "bits": [{"register": "c", "index": index, "logical": index,
              "physical": index, "prepared": 0} for index in range(width)],
    "pairs": [[0, 155]], "groups": [[0, 1, 155]],
}
before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
start = time.perf_counter()
result = project_pub(raw, manifest)
elapsed = time.perf_counter() - start
after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print("shots", result["num_shots"], "work", result["work_units"])
print("peak RSS KiB before/after", before, after, "seconds", elapsed)
PY
```

For error-cell order `00, 01, 10, 11`, the two paired component scores are
`(0, -1, 0, 1)` and `(0, 0, -1, 1)`. Each uses the same joint shots but its
own variance and one-sided lower bound; their minimum tests the margin `G`.
`paired_component_moments` computes the two means and `n-1` sample
variances and covariance exactly from a four-cell table. Their usual
unbiasedness for population moments assumes IID sampling; dependence can
invalidate it. The function supplies descriptive
moments only: it authenticates neither the table nor the sampling assumptions
and returns no confidence interval or confirmatory decision.
Existing empirical-Bernstein machinery is registered for other families and
assumes stationary IID shots within each PUB. Its planning path also accounts
for uncertainty in a modeled variance. A numerical radius at a hypothetical
variance is not a power calculation. Any extension to independent but
non-identical observations needs its own reviewed estimand and contract; none
of these assumptions permits arbitrary dependence. Power for both component
inequalities must account for failures of both, while multiplicity across
selected pairs and other claims remains separate.
The two component scores share outcomes: their population covariance is
`p_11 - (p_11-p_01)(p_11-p_10)`. With the two score means `mu_1` and
`mu_2`, the covariance `c` determines `p_11 = c + mu_1 mu_2`,
`p_01 = p_11 - mu_1`, `p_10 = p_11 - mu_2`, and normalization determines
`p_00`. Covariance alone is insufficient, but the means and same-shot
covariance identify this four-cell law. For empirical data, the unbiased
sample covariance uses denominator `n-1`, so the reconstruction first
multiplies it by `(n-1)/n`. Exact cell counts avoid that normalization and
retain the joint outcome distribution directly. Joint power still requires
the case's shot model and the joint law; the algebraic identity establishes
neither independence nor physical shot alignment. A conservative
joint-power lower bound from component miss-probability bounds needs no
independence between the two scores, but still needs a justified shot model
for each component.

For 30,000 confirmation shots per condition, range 2 and one-sided alpha 0.05,
sample variances 0.005, 0.02 and 0.05 give illustrative empirical-Bernstein
radii 0.001683, 0.002792 and 0.004080, respectively, before multiplicity.
An observed lower bound above a practical margin also requires a sufficiently
large realized improvement: at sample variance 0.02 and a 0.0035 margin, the
observed `G` must exceed approximately 0.006292 for that illustrative radius.
The two component scores may have different sample variances; a future test
must compute both bounds before taking their minimum. The radius alone does
not establish power. The
10,000/30,000 split, candidate count, conditions requiring precision, margin,
randomization and simultaneous family remain unapproved design choices.

Delay qualification is a separate acquisition if hardware observations choose
between 30 and 50 microseconds. A proposed qualification reads, for each frozen
reporter and preparation pattern, the difference in next-shot error probability
conditional on the previous observed reporter error, and requires a simultaneous
interval entirely inside a prespecified practical equivalence region. The
criterion requires established predecessor identity and a justified dependence
model; unavailable ordering, an interval crossing the region, or missing strata
returns inconclusive. Marginal initialization references alone do not establish
temporal independence. The tolerance, method and required exposures are not yet
frozen, and neither delay is declared scientifically superior.

The proposed 20-second IBM ceiling is a design target, not an allocation or a
confirmed runtime. Eight conditions at 8,192 total shots each and an assumed
250 microsecond repetition delay consume 16.384 seconds in repetition delays
alone; discovery and confirmation must share those shots or add their cost.
Eight conditions at 20,000 shots and 100 microseconds consume 16 seconds in
repetition delays alone. Both arithmetic examples exclude circuit duration,
reference controls and other overhead. The shorter delay also changes the
initialization exposure and needs its own controls and fresh backend range.
The 28 October balance observation does not establish today's quota.

## Provider-specific envelopes

The IBM row contemplates the paired-error endpoint. The IQM information-order,
IQM driven-idle, Open Quantum and Ascella rows are separate questions or
provider candidates requiring their own cases and admission.
The balances below are ephemeral read-only observations on 28 October 2026;
the query identities were not retained. Refresh and retain a sanitized,
timestamped account and backend snapshot before admission.

| Candidate | Working objective | Live balance observation and remaining admission |
|---|---|---|
| IBM Heron | Large-register target-pair and spectator-context test with fresh Target-derived physical maps and ordered joint outcomes | Primary account reported 68 seconds remaining on 28 October. Compile, estimate the full batch including overhead, prove the map/order and fit the approved limit. |
| IQM Garnet | 20-qubit information-order candidate | Account reported 2.50 credits, expiring 31 October 2026 at 17:00 Pacific. Garnet charges 0.50 per billed second; server-side credit cap is unavailable. |
| IQM Garnet, separate follow-up | Matched driven-versus-idle successor to the retained schedule discrepancy | The follow-up shares the same 2.50-credit balance and needs its own intervention, estimand, controls and case. |
| Open Quantum Rigetti | Separate, unapproved larger-register candidate; retain unpublished work outside Public Compute | Account reported 25 Spark credits. Public Compute publishes uploads and results; fresh native admission and exact cost precede any upload. |
| Quandela Ascella, separate follow-up | Same target optical mesh after randomized high/low programmed predecessor, with anchors | Platform reported available; account-wide remaining credit is unverified. Served iteration order and fixed target compilation must be demonstrated. |

IQM bills each job at `ceil(runtime_seconds) * rate`, where runtime includes
server compilation and execution. The observed rates imply at most 5 whole
billed seconds on Garnet, 3 on Emerald, or 8 on Sirius for 2.50 credits, before
allowing any margin. A previously measured 24-circuit Garnet job cost 1 credit,
but its 1.92-second runtime does not bound a new circuit's runtime. The
[idle schedule study](iqm-garnet-idle-schedule-train-readout.md) found excess
spectator decay and measured parallel versus isolated trains; the successor must
hold spectator preparation, duration and measurement fixed while comparing the
train intervention and include controls for initialization and actual schedule.
The server lacks a hard per-job credit cap; cancellation can race billing. The
strict 2.50-credit ceiling requires an enforceable provider-side bound before
submission. A historical timing estimate or client watchdog does not supply it.

A read-only Sirius observation at 16:26 UTC on 28 October returned a 16-qubit
computer summary while its default dynamic architecture listed 24 qubit labels.
The default `measure` and `prx` implementations each listed the same 16 loci;
the separate `measure_fidelity` implementation listed all 24 labels. The 24
labels are therefore not evidence that 24 qubits support the proposed
preparation and readout. Any case must inspect the required instruction loci
under its own fresh calibration rather than infer usable width from either
the label count or a different measurement implementation.

IBM's observed 68 seconds are part of its rolling 28-day quota. A read-only
account query on 28 October returned 43 jobs created in the preceding 365 days,
all with finalized reported QPU charges totaling 532 seconds. If IBM counts
exactly those charges toward its published 20-minute, 12-month eligibility
threshold, another 668 seconds would be needed; the provider's eligibility
counter and full boundary conditions are authoritative. Spending the observed
68 seconds alone would not reach 20 minutes under that assumption. The
[IBM offer](https://www.ibm.com/quantum/blog/open-plan-updates) requires opt-in;
the rolling-quota balance is not the eligibility counter.

Ascella is Quandela's photonic QPU; QX is Quantum Inspire's simulator. A
predecessor intervention on Ascella would test end-to-end history dependence,
not a thermal mechanism. Programmed phase-load proxies do not measure heater
voltages. The existing Ascella seed-order analysis treated predecessor association
as exploratory, so a randomized successor needs a fresh outcome-independent
schedule, confirmed iteration order and source-bound anchors.

The separate [predecessor draft](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention)
defines the 0.1 minimum effect as a total-variation distance, with simultaneous
coverage of 18 distributions at family alpha 0.05 under an independent-trial
model. Its frozen target, counterbalanced orders, compilation identity and
observation-chain assumptions remain admission obligations. QX can check its own
documented program and output semantics; its outcome does not establish IBM,
IQM or Ascella execution order, compilation or physical noise.

The separate unsubmitted Ascella eight-iteration draft in the primary checkout
uses target positions 1, 3, 5 and 7 and compares the magnitudes of the two
reversed-order differences. That decision rule admits linear drift as a false
history effect. For 32,768 events at each target, counts 3,277, 8,192, 13,107
and 18,022 for one output follow an exactly linear sequence and give both
pairwise total-variation distances `4915/32768`, about 0.149994; subtracting
the draft's 0.028591 radius exceeds its 0.1 threshold. The rule is inadmissible
for a predecessor claim until revised and reviewed. The signed contrast
`(P_1 - P_3 - P_5 + P_7)/2` cancels linear drift only when the four actual
observation times have the required spacing. Quadratic drift remains perfectly
confounded with endpoint assignment in that schedule. A changed schedule,
timing evidence, carryover model, uncertainty contract, cost and fresh approval
are separate admission obligations.
For eight equally spaced target observations, the candidate assignment
`A,B,B,A,B,A,A,B` and weights `(1,-1,-1,1,-1,1,1,-1)/4` cancel
constant, linear and quadratic functions of observation index. The cancellation
is a property of the proposed contrast, not evidence of physical timing or
independence.

Retained [context results](../evidence/ascella-transition-context-diagnostics/findings.md)
show identity input 5 singleton-to-reverse total variation 0.0654, with
simultaneous interval [0.0568, 0.0747] under the stated IID model and matching
returned mesh and input serializations. The comparisons span jobs and cannot
identify order, packing, calibration or drift. The draft's 0.1 threshold can
bound movement below 0.1 without excluding smaller operationally relevant
movement. The [mesh and port results](../evidence/ascella-transition-mesh-port-diagnostics/findings.md)
also show moving identity-input-0 anchors and stable-within-uncertainty
identity-input-2 anchors, so one reference does not establish stationarity for
every target response.

The [coherence transform](../../scripts/ascella_coherence_analysis.py) uses
five angles `theta_k = k pi/5` and fits five basis functions. On that grid,
`cos(6 theta_k) = cos(4 theta_k)`, `sin(6 theta_k) = -sin(4 theta_k)` and
`cos(10 theta_k) = 1`. A fitted fourth-harmonic coefficient describes the
sampled response but does not identify its harmonic mechanism. A discrimination
case needs preregistered off-grid angles and competing response predictions;
more events at the same five angles cannot resolve exact aliases.

The IBM actor case and IQM case proceed independently. The IQM balance is a
strict ceiling: a server-enforced bound must guarantee the 2.50-credit limit
before submission. Historical runtime fits and client cancellation inform risk
but do not guarantee the charged amount. The IBM case needs its own explicit
approval for the actor intervention and endpoints; an existing approval for a
different family or constructor is not transferable by name.

## Prior-art challenge and remaining work

| Question | Existing evidence and boundary | Added candidate question |
|---|---|---|
| Actor-dependent response | [Packed Pauli response](packed-pauli-response-current-balance.md) already fixes the measured register while changing preparation load. | Measure a fixed reporter error contrast and retain the actual assignment and exposure; the earlier design's phase-sensitive Pauli score is a different endpoint. |
| Correlated bursts | [Heron burst plan](../state/plans/heron-correlated-error-burst-search.json) calls for a rate and resource calculation. | Describe a shot-weight tail only when the acquisition contract supports it; require measured exposure for a rate claim. |
| Parity | The finite common-flip control above demonstrates a possible classical improvement. | Test the paired error-table margin on frozen candidates and input patterns; the control is not evidence of device protection. |
| Prediction | Shared-shot outcomes are retained by the proposed fixed-register design. | Compare disjoint features against a frozen activity/time baseline on held-out data; same-shot diagnosis and lagged prediction are distinct. |
| Predecessor history | The [Ascella predecessor draft](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention) specifies an optical target and requires qualified order and trial assumptions. | Compare a fixed target after assigned interventions without interpreting phase settings as measured power. |

This table indexes the nearest repository comparisons; it is not a completed
primary-source novelty review. The OpenAI/math family 119 scope states an
information-contraction claim under independent symmetric noise. Its parity
information question differs from the error-probability contrast `G` above.
The repository's existing finite-channel controls do not prove the general
statement or establish a physical mechanism.

The retained [Starmon-5 study](../notes/papers/2310.01120.md) is a concrete
published comparison within its documented reading scope: it prepared all
32 five-qubit computational states and measured a full assignment matrix,
combining preparation and readout errors. The proposed IBM case adds a
prespecified actor assignment and held-out comparison of the error-table
margin `G`; the existing [packed Pauli case](packed-pauli-response-current-balance.md)
already changes preparation load with a fixed measured register but targets a
different response. The Starmon source is not established as the globally
nearest publication, and the proposed combination remains unverified as novel.

The retained [Rudinger et al. IBM experiment](../notes/papers/1810.05651.md)
is a closer intervention precedent: a fixed target is measured under idle and
neighboring CNOT activity, and the authors identify unequal exposure time as a
confound. The proposed `G` decision under randomized actor preparation differs
in endpoint; context-dependent error is established prior art. The Starmon-5
assignment matrix could in principle yield paired error tables by marginalizing
its input-associated outcomes. The retained source review does not establish
access to the full numeric matrix or its randomization, and does not establish
novelty of this particular analysis.

The underlying methods are established. The [Starmon-5 study](../notes/papers/2310.01120.md)
measured a multi-qubit assignment matrix and explicitly noted that preparation
and readout errors were combined. [Unfolding quantum computer readout noise](https://doi.org/10.1038/s41534-020-00309-7)
and [spatially correlated driven-qubit noise](https://doi.org/10.1038/s41534-024-00842-9)
are close precedents. [Simultaneous randomized benchmarking](https://doi.org/10.1103/PhysRevLett.109.240504),
[crosstalk detection](https://doi.org/10.22331/q-2020-09-11-321),
[driven-idle crosstalk suppression](https://doi.org/10.1088/2058-9565/ad5a37), and
[2026 spatial crosstalk characterization](https://doi.org/10.1103/2zb3-4vwq)
also preclude a broad claim that correlated error or driven-idle comparisons are new.
The [packed Pauli response design](packed-pauli-response-current-balance.md)
already proposes sparse/dense preparation on large registers. The IBM
candidate's distinct proposed endpoint is a held-out paired-error improvement,
not a claim that packed crosstalk characterization is new. Whether this precise
combination has appeared elsewhere remains unestablished.

Before requesting approval, finish the primary-source comparison, specify a
bounded uncertainty and holdout contract, generate exact source and decoder
artifacts, verify native placement and served ordering, estimate and bound each
provider's charge, refresh account and device admission, and independently
review the complete case. No simulator job, QPU job, upload, booking or
provider random draw is authorized by this document.
