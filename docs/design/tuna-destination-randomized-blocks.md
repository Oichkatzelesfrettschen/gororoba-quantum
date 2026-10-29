# Tuna destination association under randomized job blocks

This draft examines whether the unusually large nominal-zero qubit-6 response in the
[retained prefix](../evidence/tuna-projector-geometry/joint-response-analysis.md) recurs
as a destination-dependent binary response. The contrast was selected after seeing the
old data. The successor would supply new observations; it cannot turn the old stopped
six-job endpoint into a completed result.

The [identifiability construction](tuna-readout-mapping-identifiability.md) shows that
binary responses alone do not identify physical transitions, thresholding or result
reconstruction. A provider's job-bound acquisition trace and pre-packing labels could
address reconstruction on already acquired shots. The existing
[private request](../notes/quantum_inspire/destination-response-upstream-request.md)
remains unsent; provider contact requires explicit authorization.

## Alternatives and question

- **Trace-first:** compare provider-retained acquisition labels and mapping with each
  returned bit, then repack the same shots under destination permutations. This directly
  tests a stated reconstruction rule without another QPU acquisition, but depends on
  provider retention and authenticated event identities.
- **One repeated bracket:** acquire baseline, rotated and baseline again. This is cheaper
  and can describe a single realized response, but gives only one rotated intervention
  and remains vulnerable to a coincident transient.
- **Randomized blocks:** independently assign baseline and rotated sources to the two
  serial positions of each block. Multiple treatment assignments can test a specified
  invariance null under explicit no-carryover and randomization assumptions. Such a
  result would locate neither the responsible subsystem nor the physical qubit state.

The proposed successor uses the third option while preserving the first as a separate
information route. The primary question is: under the frozen nominal-zero source, is the sharp null
that changing the three early destinations leaves each job position's inverse-decoded
early-q6 fraction unchanged compatible with the randomized assignments? A rejection
does not by itself estimate an average effect or test equality of marginal distributions. The control changes
`(q4,q11,q6)` destinations from `(17,18,19)` to `(19,17,18)`; the terminal destinations
remain fixed. The two cQASM sources must have identical physical instruction streams
and declared register widths when the three early destinations are removed. Local
compiler agreement does not establish equal served pulses, scheduling or configuration.

## Working assignment and analysis contract

Eight blocks each contain two serial, complete 4096-shot jobs: one baseline and one
rotated destination source. Each block's order is selected independently with one
unbiased bit from an identified quantum-random source. The random source, extraction,
allocation, unused values, draw identity and assignment procedure must be frozen and
verified before the first dispatch. A random value is consumed once. All sixteen jobs
are needed for the specified inferential result; an incomplete block or campaign is
retained and reported descriptively with an inconclusive verdict. Assignments must be
fixed before the campaign and cannot depend on the acquired outcomes.

For block `j`, let `D_j` be the rotated early-q6 one fraction minus the baseline
fraction, both decoded by the destination declared in the source. The primary statistic
is `T = sum(D_j)/8`, with a two-sided exact randomization test at `alpha = 0.01`.
Enumerate all 256 possible within-block order assignments and compare the absolute
value of the corresponding signed sum to the observed absolute value, including ties.
The test is exact for the sharp no-destination-effect null if the random bits are
independent and unbiased, all potential job outcomes are fixed independently of the
assignment, and a job's outcome does not depend on prior assignments or carryover. The
potential outcomes may vary between blocks and positions; the test does not require
independent shots. Provider scheduling or shared apparatus memory that depends on
assignment can violate the fixed-potential-outcome and no-carryover conditions. Capture
actual execution order and provider timestamps and refuse the inferential verdict when
that contract fails or cannot be justified. A statistical rejection challenges the
specified sharp null, not a particular physical cause.

With eight independent binary assignments, the smallest attainable two-sided p-value
is `2/256 = 0.0078125`; ties can make it larger. Fewer than eight blocks cannot attain
0.01 under this specified two-sided test. This arithmetic is a resolution condition,
not a power guarantee. A non-rejection does not establish equivalence, and the draft
has no prequalified confidence interval for an average causal effect. The 0.4818
historical contrast is a retrospective planning observation, not a predicted effect.

### Assignment-source assumptions

The exact test uses a uniform distribution over all 256 order sequences. A source's
quantum origin, a retained draw and a test of a finite sample do not prove independent,
unbiased bits. The case must state and justify the assignment law and avoid selecting
or replacing draws after examining the resulting orders. As a sensitivity example, if
bits are independent with probability `0.55` for one order, and fixed nonzero position
differences are equal under the sharp null, the nominal `2/256` rejection occurs with
probability `0.55**8 + 0.45**8 = 0.010054906328125`, above 0.01. If all eight bits
are perfectly correlated but each is marginally fair, the same false-rejection
probability is 1. These examples describe assignment-law violations, not measurements
of any particular random-number source.

### Carryover can mimic a destination effect

A counterexample shows why ordered timestamps alone cannot validate the no-carryover
assumption. In every block, suppose the first job returns early-q6 one fraction `0.5`
regardless of its source. Suppose the second job returns `1` after a baseline first job
and `0` after a rotated first job, regardless of the second job's source. Baseline then
rotated produces a rotated-minus-baseline difference of `1 - 0.5 = 0.5`; rotated then
baseline produces `0.5 - 0 = 0.5`. All eight differences are positive and the
randomization test returns `2/256`, despite the stipulated absence of any direct effect
of the current job's source. The apparent response is caused entirely by dependence on
the preceding source in this construction.

A schedule and timestamp record cannot exclude that hidden memory. A justified
washout or an independently measured carryover intervention and job-bound configuration
trace are needed before interpreting rejection as a direct destination effect. Without those anchors, a randomization test can instead target the global sharp null
that no assignment in the whole sequence changes any position's outcome, provided the
full assignment law and fixed potential outcomes satisfy that test. A rejection of that
global null does not distinguish a direct effect from carryover, reconstruction or qubit
physics. Merely inserting a delay with an unknown settling time is not a validated washout.

### Resolution is a severe power constraint

For eight nonzero block contrasts, the 1% two-sided test rejects exactly when all eight
contrasts have the same sign. Every sign-flip enumeration has a complementary result of
equal absolute magnitude; a mixed-sign observed sum is strictly below the maximum,
while a zero contrast duplicates the largest tail and cannot achieve the required p-value.
Consequently, even a real positive effect can yield an inconclusive result when one block
reverses sign. This deterministic fact does not require a shot-independence assumption.

For illustration only, suppose the eight block signs are independent, each contrast is
nonzero, and each sign is positive with probability `p`. The chance of rejection is
`p**8 + (1-p)**8`: 0.167775 at `p=0.80`, 0.430467 at `p=0.90`, and 0.663420 at
`p=0.95`. These are toy-model probabilities, not power estimates for Tuna. The retained
three-job prefix does not establish the block-sign distribution, and arbitrary job-level
memory can invalidate independence. Additional blocks can improve resolution and permit
some sign reversals, but they also increase queue exposure; a revised case must justify
its chosen power model and completion risk rather than infer either from the old shots.

The tradeoff is not monotonic at fixed significance. Under a stronger toy model in
which every block contrast has the same nonzero absolute magnitude and independent
signs, exact enumeration gives the following rejection probabilities. The number of
allowed opposite-sign blocks follows from the 1% two-sided randomization tail.

| Blocks | Jobs | Opposite signs allowed | `p=0.80` | `p=0.90` | `p=0.95` |
|---:|---:|---:|---:|---:|---:|
| 8 | 16 | 0 | 0.167775 | 0.430467 | 0.663420 |
| 10 | 20 | 0 | 0.107374 | 0.348678 | 0.598737 |
| 12 | 24 | 1 | 0.274878 | 0.659002 | 0.881640 |
| 16 | 32 | 2 | 0.351844 | 0.789249 | 0.957062 |

Ten blocks still require unanimous signs and have lower toy-model power than eight.
Twelve blocks allow one reversal under the equal-magnitude model. Unequal magnitudes
change the randomization tail, so the table is an explicit counterexample to choosing
block count by intuition, not a sample-size recommendation or a Tuna power forecast.

Terminal q6, all three early/terminal joint tables and the full six-bit response are
secondary descriptions. A terminal change may indicate a broader served-context or
time effect; the treatment modifies no declared terminal destination. Secondary
contrasts carry no confirmatory error-rate guarantee unless a family and multiplicity
rule are frozen before acquisition. Exploratory algebraic encodings do not acquire
physical meaning through this test.

### Completion and timing selection

The inferential procedure concerns all attempted campaigns under the stated assignment
law. Conditioning its reported error guarantee on completing all sixteen jobs requires a
separate proof: assignment-dependent queue behavior, failures or administrative stops can
select the observed order sequences. A stopped campaign reports its retained observations
and an inconclusive verdict. The operator must not substitute completed blocks, discard
unfavorable observations or repeat failed jobs under the same approval. The exact case
must predefine every failure and order veto before acquisition.

Provider `queued_at` and completion fields support only their documented timestamp
interpretation; they do not identify pulse starts, actual integration windows or identical
served schedules. Exact case admission must name which observed chronology, configuration,
calibration and carryover deviations invalidate the test, and must state which of those
conditions are unobservable rather than treating missing evidence as agreement.

## A history-control alternative

A four-job block can examine a restricted carryover model instead of assuming the
preceding job has no effect. Let `A` be the baseline source and `B` the rotated source.
Randomly select `ABBA` or `BAAB` per block, collect every job serially, and use positions
2, 3 and 4 so each has a recorded preceding source. Eight complete blocks require 32
jobs and 131,072 shots. The first position's preceding source and longer history remain
uncontrolled. The sources still require exact compiled-stream and decoder checks.

For an illustrative model, encode `A=-1` and `B=+1`. In `ABBA`, the current and preceding
source signs at positions 2–4 are `x=(+1,+1,-1)` and `h=(-1,+1,+1)`. Let `z=+1` for
`ABBA` and `z=-1` for `BAAB`, so the alternative negates both vectors. For each block and
position, suppose the potential job fraction has the additive form

    y_t = mu_t + z (tau x_t + gamma h_t),  t = 2,3,4.

Here `mu_t` may vary by block and position but is fixed independently of the randomized
block order; `tau` and `gamma` are direct-source and immediately preceding-source
coefficients for that block. They are response coefficients, not necessarily classical
mapping or physical-state parameters. With independently fair `z` and complete blocks,
set `U_t = z y_t`, `a = sum_t x_t U_t`, and `b = sum_t h_t U_t`. Because the design
matrix has Gram matrix `[[3,-1],[-1,3]]`, the estimates `(3a+b)/8` and `(a+3b)/8` have
randomization expectations `tau` and `gamma`, respectively, conditional on the
realized pre-block history when the current order is independent of that history.
Averaging targets a path-dependent average of the coefficients along the realized
history, not automatically a fixed finite-population average across counterfactual
histories. The calculation permits position effects fixed before the block order and
does not treat shots as independent assignments.

The estimator retains randomization variation from position baselines. For example, if
all three position fractions equal `1/2` with `tau=gamma=0`, both block estimates equal
`z/4`. Under eight independent fair block orders, each average has standard deviation
`1/(4 sqrt(8))`, approximately `0.0884`. This idealized arithmetic is not a measured
Tuna noise level; it demonstrates that the number of shots alone cannot establish the
precision of the job-level history coefficients.

The additive model excludes nonlinear source-by-history interaction and memory beyond
one preceding job; a changed served schedule, hidden state or assignment-dependent
missingness can violate it. The first job of a block can itself be affected by the prior
block, and the model needs future block orders concealed from any process that can alter
current outcomes. This design does not qualify a washout and needs explicit uncertainty,
model falsifiers, multiplicity, missingness and completion-selection rules. It can expose
some history sensitivity that a simple pair leaves inseparable, but even a nonzero
`gamma` does not locate the responsible subsystem. The larger workload requires a new
queue and feasibility case; no choice between the two designs is frozen here.

An independent check gives a concrete omitted-history counterexample. Suppose every
position's one fraction is `1/2 + delta` times the source sign two jobs earlier, with
`delta=1/8`, and the direct and immediately preceding-source effects are both zero.
Conditioning on the previous block, the half-difference of the expected `ABBA` and
`BAAB` responses at positions 2–4 is `(0,-delta,+delta)`. Applying the additive-model
formula above gives apparent coefficients `-3/32` and `-1/32`, although neither named
mechanism exists in the construction. The example also violates a model restriction:
if `Delta_t` is the half-difference of the two order-specific position means, then the
additive model requires `Delta_2 + Delta_4 = 0`. The two-job-memory example gives
`delta` instead. A prespecified uncertainty-qualified test of that restriction could
falsify this particular additive model; failure to reject cannot establish it or rule
out other longer-memory mechanisms.

A global sign-flip analysis that changes earlier assignments while holding later
observed outcomes fixed is invalid when earlier assignments change later histories.
A successor needs a sequential conditional or martingale analysis, or an independently
justified cross-block no-interference condition; this draft derives neither.

A second construction passes that residual check while still aliasing longer history.
Let the fraction at each position be `1/2 + delta (s[t-2] + s[t-3])`, where each `s` is
the source sign and `delta=1/8`. Every fraction lies between 1/4 and 3/4. Conditioned on
pre-block history, the three position half-differences are `(0,-delta,0)`, which satisfy
`Delta_2 + Delta_4 = 0` and yield both model coefficients `-delta/2 = -1/16`. The
construction contains neither a current-source nor a one-job-history term. Independent
variation of longer histories or a justified bound on memory is necessary to attribute
those coefficients to the named mechanisms.

The [sequential assignment alternative](tuna-sequential-destination-uncertainty.md)
allows dependence on all earlier jobs under conditional randomization, but its
assumption-light job-level uncertainty has a large time and precision cost.

## Queue and time stress scenario

The six retained jobs' creation-to-`queued_at` intervals have an observed median of
1006.377006 s and range from 496.451396 to 1936.258985 s. The observations span two
historical cases and do not establish a stationary queue or a future wait distribution.

The eight-block proposal requests 16 jobs and 65,536 shots. A transparent arithmetic
scenario assigns the historical maximum creation-to-`queued_at` wait of 1936.258985 s
to every job, a 30 s pause to each of the 15 gaps, and the historical 300 s per-job
execution ceiling to each job. Their sum is 36,230.143760 s, approximately 10 h 3 min
50 s, before admission, collection and other overhead. The three terms have different
meanings; the provider timestamp interval is not pulse duration, the ceiling is not
an expected execution time, and the pause is an operator constraint. The scenario is
neither a forecast, a worst-case guarantee nor a lower bound. Actual completion time
and the probability of finishing a complete campaign within any chosen horizon remain
unknown. A feasible request horizon, staffing and recovery procedure require explicit
review before the candidate can be approved.

Under the same artificial assumptions, 24 jobs total 54,360.215640 s, about 15 h
6 min, and 32 jobs total 72,490.287520 s, about 20 h 8 min. Each scenario uses one
less 30 s gap than the number of jobs and excludes the same overhead. Neither scenario
predicts actual completion or establishes a suitable unattended horizon.

## Admission work still required

The candidate is **unapproved and unadmitted**. Before an exact case can be reviewed:

1. Produce and hash the sixteen source/manifests and prove source and locally compiled
   physical-stream equality, decoder correctness and mutation sensitivity.
2. Freeze an unbiased assignment draw and a deterministic enumeration analyzer, test
   all possible assignments and ties, and independently review the statistical assumptions.
3. Establish an operational horizon using the measured 1936.258985-second maximum
   creation-to-`queued_at` interval, mandatory pauses and fresh queue conditions. The
   historical interval is a single observed maximum, not a worst-case guarantee or a
   provider service-level promise. Quantify the chance of completing sixteen jobs only
   if a defensible queue model exists; otherwise report the completion risk as unknown.
4. Define per-job and total execution ceilings, expected credits and stop conditions;
   retain every dispatched job even after the request horizon ends, and prohibit automatic
   retry. An account-wide queue does not authorize cancellation of another worker's job.
5. Establish how actual order, schedule identity, carryover and calibration changes are
   observed. Missing required evidence must produce an inconclusive outcome.
6. Bind the reviewed case, compiler receipts, analyzer, assignment, account rules and
   fresh admission into an exact approval packet. A separate user approval is required
   before any job, remote simulation or circuit upload.

The choice of eight blocks follows the exact test's minimum p-value, not a demonstrated
power or practical-completion calculation. If provider evidence makes the test redundant,
or operational and scientific assumptions cannot be qualified, do not submit the case.
