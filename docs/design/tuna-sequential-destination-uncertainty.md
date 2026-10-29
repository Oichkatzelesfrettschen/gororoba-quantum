# Tuna destination response under sequential job assignment

The [randomized-block draft](tuna-destination-randomized-blocks.md) needs a way to
handle unknown dependence on earlier jobs. This note derives a conservative alternative
for one prespecified early-q6 response. It is a design calculation, not an admitted case
or a new hardware result. The [provider trace request](../notes/quantum_inspire/destination-response-upstream-request.md)
remains the direct route to checking acquisition reconstruction.

## Assignment and estimand

At each job position `t`, let `F[t-1]` include all earlier assignments, observed jobs,
provider states and other information used to decide whether to proceed. A prospective
mechanism assigns `Z[t] = +1` to the rotated destination source or `-1` to the baseline
source with conditional probability `1/2` each, independently of the potential current
job outcomes given `F[t-1]`. The rule and random-source allocation must be frozen before
acquisition. The current value must be protected from selection and withheld until its
pre-assignment history is fixed; it is then disclosed as needed to submit the assigned
source. Future assignments must remain concealed from processes that can affect current
outcomes. If values are drawn in advance, the formal history excludes their unread
values and the operational process must enforce that exclusion. This fairness and
conditional independence are assumptions to justify, not facts established by the
quantum origin of the random source.

For a complete job, `Y[t]` is the inverse-decoded fraction of early-q6 ones among its
4096 retained shots. Define potential fractions `Y[t](+)` and `Y[t](-)` at the same
realized prior history. Each lies in `[0,1]`. Their joint law may change with that
history, include arbitrary shot dependence, and include all queue and apparatus effects
of the current assignment. Consistency requires the observed `Y[t]` to equal the
potential outcome for the assigned source. The predictable response contrast is

    tau[t] = E[Y[t](+) - Y[t](-) | F[t-1]].

The target `sum(tau[t])/n` is a path-dependent average along the histories actually
encountered. It is not automatically a stationary population effect, a direct classical
packing effect, or an average over every counterfactual campaign. A source-dependent
queue, compiler, schedule or physical response is part of the end-to-end contrast.
Correct association of a binary result with its declared source and actual job is a
separate prerequisite.

The two complete potential fractions must exist at every included position, including
for the source that was not assigned. A timeout, partial result or undefined decoder
under either hypothetical source makes that complete-job estimand undefined unless the
case specifies a justified potential-outcome model. Defining a bounded failure outcome
instead is possible in principle but changes the target to include availability and
requires its own review; selecting only whichever source completed does not repair the
complete-job estimand.

If the actual conditional assignment probability is `p` rather than `1/2`, the score's
conditional bias relative to `tau[t]` equals

    (2p - 1) E[Y[t](+) + Y[t](-) - 1 | F[t-1]].

Its magnitude can reach `|2p-1|`: a probability of `0.55` can create a bias as large as
`0.10`. A known non-half propensity can support an inverse-propensity score with a
separate concentration bound, provided it stays bounded away from zero and one; this
note does not assume that probability is known. A finite sample of source bits does not
prove the required conditional assignment law.

## Fixed-length concentration

Use the score and its average

    X[t] = 2 Z[t] (Y[t] - 1/2),       T[n] = sum(X[t])/n.

Under the assignment assumptions, `E[X[t] | F[t-1]] = tau[t]` and `X[t]` lies in
`[-1,1]`. Conditional Hoeffding's lemma on the length-2 score interval gives, for a
fixed, predetermined number of complete positions,

    Pr(|T[n] - sum(tau[t])/n| >= r) <= 2 exp(-n r^2/2).

The two-sided 99% radius is `sqrt(2 log(200)/n)`. An interval can be intersected with
the known response-contrast range `[-1,1]`. The guarantee is unconditional over the
assignment and outcome process, and concerns the realized predictable target. It does
not require independent shots or a bound on past-memory length. It does require fresh
conditional randomization, a well-defined potential-outcome intervention and complete,
correctly associated job observations.

| Complete job assignments | Radius at 99% | Illustrative stress hours |
|---:|---:|---:|
| 16 | 0.813812 | 10.06393 |
| 32 | 0.575452 | 20.13619 |
| 46 | 0.479960 | 28.94942 |
| 48 | 0.469854 | 30.20845 |
| 183 | 0.240635 | 115.19317 |
| 1060 | 0.099984 | 667.27903 |

Radii are displayed rounded to six decimals; a case analyzer must round an actual bound
upward. The stress column multiplies each job by the historical maximum observed
creation-to-`queued_at` interval of 1936.258985 s, adds a 300 s execution ceiling per
job and a 30 s pause for each gap. The calculation excludes admission, collection and
other overhead. It is an arithmetic scenario, not a forecast, guaranteed bound or
lower bound on provider time. The six recorded intervals are not a validated queue
model. The provider limits and account conditions require fresh admission.

The retained nominal-zero prefix has a retrospective empirical response of
`0.4818115234375`; its original six-job endpoint remains unavailable. If a *new*
16-job score were exactly that value, this conservative interval would include zero.
At 46 jobs the radius is below that value, so an observed score of that size would
exclude zero; this statement is not a forecast of the new score or its power. At 183
jobs the radius is below half that value. On the bound's good event, a realized target
larger than twice the radius forces the corresponding interval to exclude zero. The
unconditional probability that both the target satisfies that separation and the test
misses it is at most 0.01; the calculation does not claim a 99% probability conditional
on an observed or selected target.

A narrower bound can be possible under additional justified variance, sampling,
randomization or memory assumptions. The calculation does not prove that 46 or 183
jobs are necessary for every valid design. It shows that this assumption-light bound
alone does not justify a short, precise equivalence claim.

## Faster assignment within one job is unqualified

The retained [Tuna operation reference](../notes/quantum_inspire/site/kbase_tuna-operational-specifics.md)
allows mid-circuit measurement but lists binary-controlled `c-` gates and the classical
`Not` instruction as unavailable. A mid-circuit measurement by itself therefore does not
establish a supported, shot-randomized classical destination selector. Any proposed
within-job assignment needs a documented and locally compiled mechanism, a specified
randomization law and a check that reconstruction returns the selected label correctly.
Without such evidence, treating 4096 shots from a fixed circuit as 4096 independently
assigned destination interventions would be invalid.

## Stopping and failure

The fixed-length radius does not authorize repeated interim looks or make an interval
conditionally valid after selection on favorable completion. Missing, malformed,
misassociated or partially collected jobs cannot be silently replaced. A stopped
campaign remains inconclusive unless a separately reviewed procedure defines a valid
observed-data target and accounts for stopping and missingness. A confidence-sequence
construction or an alpha-spending rule could allow specified adaptive stopping, at a
precision cost, but neither is admitted here. Provider `queued_at` records ordering of
that field, not physical pulse starts or equal served schedules.

Before any case uses this method, specify a random-source law, secure allocation,
assignment concealment, exact intervention and decoder, outcome and failure rules,
fixed number of positions or a valid anytime analysis, practical margin, queue horizon,
execution and credit ceilings, complete-case interpretation and independent review.
Then refresh provider admission and obtain approval of the exact written case before
any job or upload. The mathematical construction does not authorize execution.
