# Measured-feedback versus known-label correction

The execution priority is model discrimination and a measurable optimizer
decision before broad atlas expenditure. The prepared 197-second ripple/rank
campaign remains retained and unapproved behind that decision gate. The
four-PUB pilot below is a design recommendation; the runner does not yet
implement its family, and its time estimate is historical rather than a
freshly admitted execution case.

## Existing evidence first: zero additional QPU seconds

The [folded raw audit](../results/ripple/folded-job-review.md) retains all
sixteen observed joint distributions. Its common appended-channel falsifier
rejects a narrow explanatory model; replacing the modeled readout channel
requires pre-readout predictions and remains a distinct question.

First-bit mismatch with the supplied label is not a directly measured
readout-discriminator error. Preparation, gates and the measurement instrument
can each contribute. The no-feed-forward s0 arm has terminal correctness
6349/7516 = 0.844731 when its first bit matches, versus 393/676 = 0.581361
when it differs. The s2 figures are 5863/7551 = 0.776453 and
332/641 = 0.517941. Those observed associations occur in circuits that omit
outcome-conditioned correction, so feedback is an insufficient explanation
for all first/terminal dependence. The conditional estimates remain
descriptive here. Their mechanism is unresolved.

All old shots have been inspected. They can train candidate models and choose
a prospective intervention, but repartitioning them cannot create a fresh
validation set. Freeze each candidate model's parameters and joint-outcome
predictions before the new acquisition. The entire new pilot is prospective
validation. The existing [source synthesis](../literature/notes/reality_ripple_measurement_design.md)
and [Corcoles note](../literature/notes/2102.01682.md) retain prior-work limits.

## Smallest direct optimizer comparison

Use the odd known-eigenstate labels s1 and s3. For each label, acquire two
arms, giving four PUBs:

| Arm | Correction rule | Retained observations |
| --- | --- | --- |
| F | Apply P(-pi/2) when the first measured bit is one | First measurement, reset, first bit and terminal bit |
| U | Apply P(-pi/2) unconditionally from the supplied odd label | The same first measurement, reset and two bits |

Both arms have the same ideal labeled law. Keep their quantum preparation,
compiled prefix/suffix, physical mapping and terminal writer fixed. Match
and audit schedules, including conditional latency and measurement/reset
timing. A common initial layout alone is insufficient: the completed ladder
used different terminal writers after routing. A zero-angle conditional can
be optimized away, and padding needs backend timing evidence. Schedule
matching remains a qualification requirement; the unavailable Kingston mock
service leaves that requirement open.

When the recorded first bit B=1, both arms apply the same phase. When B=0,
the arms differ in whether they apply the phase. Those strata provide
prespecified descriptive diagnostics. Optimizer admission uses unconditional
terminal success, retaining every shot. A favorable rare stratum cannot be
selected into an unconditional gain. The comparison estimates the effect of
the specified correction policy; it does not uniquely attribute a difference
to discriminator error, preparation, quantum back-action or controller noise.

A fixed order such as F(s1), U(s1), U(s3), F(s3) balances the policy order
across labels, but four PUBs do not identify arbitrary drift. The inference
requires independent stationary repetitions within each PUB and a stable
comparison context. A future blocked design would need fresh pricing.

## Proposed decision and uncertainty

Declare a practical improvement threshold of 0.01 for each label. For each
binomial count, use a one-sided Clopper-Pearson bound with tail probability
0.05/4: lower bounds for U and upper bounds for F at both labels. Select U
only when both inequalities hold:

`lower_U(s) - upper_F(s) > 0.01`, for `s in {1,3}`.

The union bound gives at least 95 percent simultaneous directional coverage
under the within-PUB sampling assumptions, while allowing dependence across
PUBs. A failed gate retains F and establishes neither equivalence nor a
controller diagnosis. The admitted policy would apply only to the two supplied
odd-label witness circuits. Unknown-eigenstate QPE and general order finding
remain outside the substitution. Covering all four labels requires eight PUBs
and a revised uncertainty allocation.

At N=8192 and the old F success probabilities 6433/8192 and 6241/8192,
an assumed four-percentage-point U gain gives per-label planning powers
0.952058 and 0.928543. Their union lower bound is 0.880601. An assumed
three-point gain gives only 0.505748 and 0.455085. The gains are hypothetical;
the old delay arm is a different intervention and cannot predict U.

The power calculation enumerates every F success count k=0,...,N, finds the
smallest U count whose exact lower bound exceeds the F upper bound by 0.01,
and sums `BinomPMF(k;N,p_F)*BinomSF(k_U_min(k)-1;N,p_F+gain)`.
The enumeration truncates zero probability mass. Its planning model assumes
independent F/U binomial counts; the coverage statement above uses the weaker
union-bound requirement. Source probabilities come from the retained raw audit.

## Conditional timing and admission work

Use `H + sum(N_pub * (repetition_delay + scheduled_duration_pub))`.
Historical inputs H=2.3 s, repetition delay 250 us, and schedule 22.904 us give:

| Proposed acquisition | Historical estimate |
| --- | ---: |
| Four PUBs x 4096 shots | 6.7713 s |
| Four PUBs x 8192 shots | 11.2425 s |
| Six PUBs x 8192, with forced-wrong branch controls | 15.7138 s |
| Eight PUBs x 8192, covering all four labels | 20.1850 s |

These figures exclude queue and local preparation time. New calibration,
padding, backend schedule and service accounting can change the charge. They
are neither an approved budget nor a service ceiling. The four-PUB design is
the minimum comparison for the narrow optimizer decision. Forced-wrong
controls support a stronger branch-consistency question at additional cost.

Before proposing execution:

1. Add the explicit four-member family, independent ideal laws, contracts and
   record reconstruction. The existing folded CLI always builds sixteen PUBs.
2. Verify a common routed template, terminal writer, measurement/reset history
   and the schedule contract. Reject qualification when those checks fail.
3. Freeze model predictions and the one-percentage-point decision rule; keep
   conditional diagnostics outside that primary inference family.
4. Run fresh calibration-bound compilation, local model checks, timing and
   independent admission. Record its source/QPY digests and service ceiling.
5. Present the written case for explicit user approval. Submit only that case.

The successful witness decision would establish one concrete optimization in
its own circuit domain. Static ripple packing still needs its own practical
accuracy criterion and controls. A dynamic-witness improvement does not by
itself admit broad atlas spending.

## Targeted research gaps and ownership

The existing multiprogramming, context, drift and QPE literature already
supports the experiment class. The missing information that can change the
next decision is narrower: which joint instrument models are identifiable
from the two recorded bits and forced-branch interventions, and whether
backend scheduling can realize the matched comparison. Primary sources on
mid-circuit measurement instruments can refine causal interpretation; broad
additional literature collection is unnecessary for the F-versus-U decision.

The execution coordinator owns circuit matching, statistical admission,
timing and the coordination ledger. The research chats own source organization,
targeted instrument/sequential-inference references and the separate
Koebisu/rank-stratum proof synthesis. Exact global rank geometry requires
mathematical evidence; the proposed four-PUB pilot measures a hardware policy.

Targeted primary candidates are Rudinger et al.,
[quantum-instrument GST](https://arxiv.org/abs/2103.03008), and Wysocki et al.,
[interpretable mid-circuit measurement errors](https://arxiv.org/abs/2602.03938).
Their abstracts distinguish classical readout from post-measurement quantum
state errors and describe instrument characterization. The present handoff
verifies those abstracts; complete protocol assumptions and Runtime
compatibility remain assigned source-review work. The four-PUB pilot supplies
an optimizer comparison, not full instrument tomography. Fixed-sample bounds
remain the decision contract; adaptive stopping needs separate qualification.
