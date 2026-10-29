# Sequential destination comparison: bounded response uncertainty

The [frozen analyzer](../../../scripts/qi_tuna_readout_destination_analysis.py) compares selected binary
response probabilities in six fixed jobs. The analysis qualifies a realized response contrast. It cannot
attribute a change to classical destinations, electronics, readout physics or an unobserved transient.

The case contains prepared-zero and prepared-one sequences. Each sequence has a baseline, a circuit whose
three early classical destinations are cyclically permuted, and a byte-identical baseline repeat. Every job
has 4096 shots. Each successor job must be created at least 30 seconds after the preceding job's recorded
finish. The six positive job IDs and six positive batch IDs must be distinct. `queued_at` remains a recorded
queue timestamp; the analysis never substitutes that field for a documented execution-start timestamp.

## Estimand and conditional probability

For one nominal preparation, ancilla and early/final outcome cell, let X[j,t] be the cell indicator in shot t
of job j. The four cells are 00, 01, 10 and 11, with the early bit first. The decoder maps classical destinations
back to physical qubits 4, 11 and 6 before constructing indicators. There are 24 selected cells across both
preparations; cells within a shot may be dependent.

Let F[j,t-1] contain the complete earlier acquisition history, including earlier shots, jobs and preparation
choices. Define p[j,t] = E[X[j,t] | F[j,t-1]] and P[j] = sum_t p[j,t]/4096. The P[j] are realized predictable
averages: they can change with the acquisition's random history. They are not necessarily stationary detector
probabilities or repeated-campaign population means. The fixed response target is

    D = P[rotated] - (P[before] + P[after])/2,

and the baseline endpoint target is R = P[after] - P[before]. Their estimators substitute empirical cell
frequencies. The arithmetic mean is part of the frozen definition; unequal wall-clock spacing does not silently
turn it into a time-interpolated counterfactual.

A maximally dependent example prevents a misleading effective-sample-size interpretation. If every shot
X[1] = ... = X[n] = Z for a Bernoulli(p) variable Z, then the predictable average is
(p + (n-1) Z)/n. A narrow concentration interval covers that history-dependent average while learning almost
nothing precise about the repeated-run mean p. The method does not recover thousands of independent physical
interventions from thousands of correlated shots.

## Finite-sample bound from conditional boundedness

For X in [0,1] and p = E[X | F], the conditional moment generating function obeys

    E[exp(lambda*(X-p)) | F] <= exp(lambda^2/8).

One derivation uses the convex chord exp(lambda*x) <= 1-x+x*exp(lambda), then centers by p. The second derivative
of the logarithm of the centered Bernoulli moment generating function is the variance of a tilted Bernoulli
variable, at most 1/4. Its value and first derivative vanish at lambda=0. Integrating that bound twice gives
lambda^2/8. Applying the inequality conditionally and iterating over the full history gives, for fixed weights w,

    P(|sum w*(X-p)| >= r) <= 2 exp(-2*r^2/sum(w^2)).

The response weights are -1/(2n), +1/n and -1/(2n) over the three jobs, so sum(w^2)=3/(2n). The endpoint weights
are -1/n and +1/n, so sum(w^2)=2/n. Arbitrary temporal dependence and unequal p[j,t] are allowed. The feature
list, weights and sample counts are fixed before acquisition; outcome-driven sample-size changes are excluded.

A union bound covers 24 response and 24 endpoint contrasts, with two tails each and familywise alpha=0.01:

    rD = sqrt(3*log(96/0.01)/(4*4096))
    rR = sqrt(log(96/0.01)/4096).

The analyzer evaluates the logarithm and square root with 60-digit Decimal precision and rounds each radius
upward to 12 decimal places: rD=0.040975467792 and rR=0.047314394719. It tests the resulting union bound in the
focused suite. Every interval is intersected with [-1,1], the known contrast range. The guarantee is a
simultaneous repeated-process false-report bound, not a confidence statement conditional on selecting only
successful or favorable completed campaigns. Missing or failed jobs produce invalidity, never favorable
postselection or an automatic replacement acquisition.

## Frozen decisions and separation at the finite budget

Both practical margins equal 0.10. The margins define a coarse instrument-response diagnostic; they are
engineering choices rather than literature-derived device specifications or full-law equivalence tolerances.
Statistical classification happens once, after all six complete jobs pass identity, hash, raw-width, histogram,
shot-count, timing, ordering and zero-charge checks.

1. A missing required artifact produces **implementation route unavailable**.
2. A malformed artifact, changed manifest/source/decoder, failed or partial job, charge, repeated identity or
   ordering/pause violation produces **protocol inadmissible**.
3. Every endpoint interval must fit inside [-0.10,+0.10]. An uncertified endpoint produces **inconclusive within
   budget**, even when a rotated response differs strongly. This multiplicity-controlled check certifies only
   the two endpoint predictable averages; it does not establish stationarity between them.
4. With admitted endpoints, any response interval lying strictly outside [-0.10,+0.10] produces **specified
   alternative supported**: a selected realized response contrast exceeds the margin.
5. With admitted endpoints, all response intervals inside the closed margin produce **objective established
   within scope**. Remaining overlapping intervals produce **inconclusive within budget**.

On the simultaneous good event, endpoint targets satisfying |R| <= 0.005371210562 guarantee endpoint admission.
If every selected response target satisfies |D| <= 0.018049064416, that event guarantees bounded response
equivalence. A selected |D| > 0.181950935584 guarantees departure when endpoints admit. These are uniform
finite-sample separation statements about random predictable targets, not conventional power at a fixed
stationary effect. More formally, the probability of a wrong classification *and* the corresponding separation
conditions is at most 0.01. Conditioning on a rare realized separation event does not preserve that probability.
The budget has a nonempty equivalence separation region; the baseline condition is deliberately stringent.

## Attribution remains unresolved

The before/after endpoint check cannot bound the counterfactual baseline response during the rotated job.
A transient synchronized with that job can reproduce any apparent destination effect. For a sensitivity display
only, suppose a counterfactual baseline at the rotated job differed from the arithmetic endpoint average by at
most gamma. Expanding a response interval by gamma then gives a conditional attribution interval. The analyzer
prints gamma=0, 0.02 and 0.05; every row records `verified=false`. The retained data establish none of those
bounds. Sensitivity rows never change the primary decision, and every report retains `attribution_status=unresolved`
and `physical_continuation_admitted=false`.

Readout labels do not independently measure excited-state population. Trusted chronological raw records,
fixed-size complete acquisitions and the declared decoder are operational assumptions. Provider analog IQ,
thresholds, acquisition-index association and served schedules remain separate evidence obligations. The
[retained failure diagnosis](readout-cause-diagnosis.md) explains the physical and implementation alternatives.
The [sequential design](../../design/tuna-readout-ordered-response-admission.md) owns acquisition scope and approval.
