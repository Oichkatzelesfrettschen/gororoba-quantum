# Readout attribution of the idle phase rate on ibm_kingston: design

The idle-penalty probe ([findings](../../results/live/IDLE_PENALTY_PROBE_FINDINGS.md)) measured a negative Ramsey
phase rate on idling qubits while readout trains played: a pair mean of -2.72 kHz (t -5.1) against two quiet
references, up to -21.5 kHz on one probe, with a quiet null at -0.010 kHz. Every replica read at once, so the run
cannot say whether a probe's shift comes from its own coupled partner's readout, from readout a few couplers away,
or from readout anywhere on the chip. This campaign splits the shift into three patterned contrasts in one job on
the probe's 31 ordered pairs. The split is an intervention on CZ-graph distance; it identifies no physical
mechanism (Limits).

## Estimand

For probe p (one qubit of pair k), the phase rate in a readout window is modeled as

    delta_p = a_p * own + c_p * near + b * f_other

- `own` is 1 when the probe's own partner plays its train;
- `f_other` is the fraction of the 30 other pairs' partners that play, and `b` the baseline coefficient per
  reading partner fraction, one per chip;
- `near` is 1 when every reading partner of another pair within three CZ hops of p plays, and `c_p` is the
  within-three-hop excess above that baseline.

The quiet reference fixes delta at zero. The probe's during arm sets own = near = f_other = 1 and measures
`a_p + c_p + b` without splitting them.

## Classes

Pairs k and j conflict when any qubit of one lies within three CZ hops of any qubit of the other on the Kingston
coupler graph (`docs/evidence/heron_platform/targets.json`, `backends.ibm_kingston.instructions.cz.qargs`). On the
31 pinned pairs that graph is bipartite: 28 edges, maximum degree 3, five components of 23, 4, 2, 1 and 1 pairs.
A 2-coloring puts every within-three-hop reader of a probe in the opposite class. Two partitions, both proper
colorings, differ by which components flip; each is stored explicitly in its patterned members, in pin order:

    P1  ABABAAABBABABBBBBABBAABAAABBBAA   (15 A, 16 B)
    P2  ABBBAAABBBBBBBBBAABBAAAAAABABAA   (15 A, 16 B)

P2 changes the same-class relation for 150 of the 437 non-conflicting pair-pairs, so a far-reader set and the
pattern PUB a probe draws each coefficient from both change between the partitions. Five components bound how far
a second proper coloring can move; the partitions counterbalance pattern-PUB offsets and part of the far-reader
membership, not all of it.

For each partition, pattern A plays the train on class A partners and holds class B partners quiet over the same
window; pattern B swaps them. For a probe in class X with n_same reading other-pair partners in its own class and
n_opp in the opposite class (n_same + n_opp = 30):

- the own-class pattern: `R_p = a_p + b n_same / 30`;
- the opposite pattern: `Q_p = c_p + b n_opp / 30`;
- the all-read arm: `D_p = a_p + c_p + b`;
- the residual `D_p - R_p - Q_p` is zero under the model.

## Isolated probes and b

20 of the 62 probes (8 targets reading spectators, 12 spectators reading targets; 10 in each class under both
partitions, from 7 isolated pairs in A and 8 in B) have no
other pair's reader within three hops. For them `near` is identically zero, `c_p` is structurally absent, and
`Q_p = b n_opp / 30`. Their `30 Q_p / n_opp` estimate b; the residuals of the remaining isolated probes about that
estimate are a far-field homogeneity diagnostic and enter no share.

- **b functional**: the median over isolated physical pairs of the pair's mean `30 Q_p / n_opp` across its isolated
  roles (15 pairs; five contribute both roles), per partition; the pooled b is the mean of the two per-partition
  medians.
- **Class agreement** (diagnostic): b from class A and from class B isolated pairs, each with its bootstrap
  interval. With 7 and 8 isolated pairs per class it detects only a disagreement several times b's own interval
  width; non-overlapping intervals mark every decision below "unresolved", and overlap establishes no
  homogeneity.
- **Coefficients**: `a_p = R_p - b n_same / 30` and, for non-isolated probes, `c_p = Q_p - b n_opp / 30`, per
  partition and averaged over the two partitions.

## Resampling

A stratified pair-cluster bootstrap: 4000 replicates, each drawing physical pairs with replacement within three
strata (isolated pairs of P1 class A, isolated pairs of P1 class B, the 16 non-isolated pairs), so no replicate
lacks the isolated pairs b and class agreement need; both roles of a pair stay together; and recomputing within the replicate the per-probe contrasts from the drawn pairs' laws resampled
multinomially at their shot counts, b, every coefficient, the D_p selection, the shares and the residual.
Intervals are percentile 95%. The generator is numpy's `default_rng` seeded by one value from an ANU draw, spelled
`qrng:<draw>#<index>` in the case and the analysis record. Every replicate's pair indices and multinomial draws
come from that one generator in a fixed order before any estimate runs; the estimates are batched across
replicates with numpy and pooled through parallel.py, and a gate proves the batched path returns the scalar
reference's bits ([vectorized-fits.md](../runbooks/vectorized-fits.md)). All pairs share
each wide PUB's shots, so the bootstrap describes pair-to-pair and shot variation and makes no claim of
independence across PUBs.

## Members

Retained from the probe (23): `idle_cz_kick` (the placement anchor), `idle_ground`, `idle_excited`, and for each
probe role (`idle_` and `idle_s_`) Ramsey x/y at 2500 and 10000 dt and x/y of `meas_during`, `meas_after` and
`meas_short`. These carry the all-read shift, its short-window unwrap and its two quiet references. Dropped (21):
the relaxation ladder, the static-ZZ pair, the echo ladder and Ramsey at 25000 dt, which the stability repeat
measures.

Added (32), per partition, pattern, window (long MEAS_DT with twelve reads, short SHORT_MEAS_DT with three),
quadrature and probe role: a patterned member whose replica k runs the reader body when its class reads in that
pattern and the quiet body otherwise. Each patterned phase unwraps through its own short twin, because five
probes of the probe run exceeded 12.5 kHz, half the 25 kHz alias.

The quiet bodies (`meas_quiet` and `meas_short_quiet`, per quadrature and role) are the reader bodies with the
partner's train replaced by an idle over the same barrier window. They are templates, never executed alone; the
all-quiet reference with that barrier window is the retained `meas_after`. Their ideal laws equal the reader
bodies', because every mid-circuit read acts on a partner in |0>.

Total: 55 PUBs.

## Execution changes

1. `experiments.Group` gains `body_templates`: circuits compiled and validated with the group (routed violations,
   ISA lookup, source identity) and excluded from `_entry_bases`, so they never form a PUB. `experiments.Member`
   gains `replica_bodies: tuple[str, ...] | None`, one member or template name per replica in path order;
   `Group.__post_init__` refuses bodies that differ in width, classical registers or ideal law, or name nothing
   in the group, and live_run refuses a plan whose replica count differs from the tuple's length.
2. live_run `_entry_bases`, `_set_entries` and `_entry`: a patterned member takes `base` from its first body and
   builds a per-replica ISA list from the compiled bodies.
3. `packing.pack` accepts a sequence of ISAs, relabels each replica's own ISA and takes the measurement-tail start
   per replica, as `packing.fuse` does for components.
4. `Entry`, `_member_fields` and `PubComponent.manifest` carry, only for a patterned member, `replica_bodies` and a
   per-replica digest of the compiled body's canonical instruction sequence on its logical qubits.
   `_archived_entries` restores both, and after `packing.split` every replica's archived body must match its
   digest and the group record's tuple, so a mislabeled body refuses collection.
5. idle_penalty.py: a readout campaign group with the 23 retained members, the 32 patterned members and the
   templates, listed in `standalone_campaign_groups` and `EXPERIMENT_SOURCE_MANIFEST`.
6. A new analyzer, scripts/idle_readout_attribution.py, built on idle_penalty_report.py's loading, unfolding,
   phase and unwrap functions:
   - per probe and partition: R_p, Q_p from the patterned long arms, unwrapped through the patterned short arms;
     D_p from `meas_during` against `meas_after` and Ramsey, as the probe computed it;
   - b, class agreement, a_p, c_p, the residual, the shares and the bootstrap above;
   - the exposure gate per class: within a class every replica shares one schedule, every replica idles over one
     absolute window (`scheduler_timing`), and that window contains every other reading replica's train;
   - a readout digest over the retained members' replica-0 per-role ISA sequences, excluding the placement anchor
     `idle_cz_kick` as `campaign_digest` does (`PLACEMENT_ANCHORS`: a pinned compile commutes the partner's X
     through the CZ), which the unpinned probe run's records also yield, for the replication comparison;
   - the batched bootstrap and its bit-equality gate against the scalar reference.

Collection itself needs no new decoding: `_archived_entries` splits replicas by register and decodes each
replica's laws regardless of body.

Sequencing: these edits move `experiment_digest`, which approved records bind and `--collect` checks. The
stability repeat and the focal jobs are approved and uncollected on `heron/idle-penalty-repeat`; that branch
collects on its own code, and this branch merges into it only after both collections.

## Gates before a case

- **Mutation test**: synthetic laws on the pinned geometry with planted a_p, c_p, b, phases past the 25 kHz alias,
  and a class-dependent pattern offset. The analyzer must recover each planted term within its bootstrap interval,
  flag the offset through class disagreement, and fail when any planted term is removed or two body labels swap.
- **Mixed-PUB schedule**: the alignment of quiet windows with reading trains is a scheduling hypothesis, observed
  on uniform bodies in the probe (all 31 windows from 1700 to 11700 dt, trains from 4392 to 11391 dt) and untested
  on mixed bodies. The dry run must show it in a local ALAP schedule of every mixed PUB; the post-collection
  exposure gate refuses a run whose service schedule breaks it.
- **Self-check**: Aer has no readout crosstalk, and the dry run's predicted laws are shot-sampled at the job's
  shots, so the null is checked at cohort level: b's interval contains zero, the counts of "resolved" a_p and c_p
  labels do not exceed the 99th percentile of a binomial count at the label's two-sided rate (0.001) over the
  family, the median residual's interval lies inside [-0.5, 0.5] kHz, and decision 4 reads "unresolved".

## Placement, shots and seconds

- Placement: the probe's 31 ordered pairs, pinned.
- Shots: 4096; per-probe phase-rate shot noise was about 0.11 kHz in the probe.
- Seconds: 16 s x 55 / 44 = 20 s expected at 20 us by count scaling; the binding dry run's estimate governs.
  Ceiling 30 s.
- Account: backup (229 s at the 2026-10-26 20:04 PDT read, less the focal jobs' ceilings, against a 60 s reserve).

## Preregistered decisions

The probe's pair means spread with SD 2.95 kHz, so a cohort mean is a weak instrument. Per-probe labels are
descriptive; the cohort decisions use the bootstrap.

1. **Per-probe labels** (descriptive) on two axes for a_p and c_p: "resolved" when |estimate| exceeds 3.29 times its
   bootstrap standard error, else "unresolved"; and "material" when the 95% interval lies wholly outside
   [-0.5, 0.5] kHz, "negligible" when it lies wholly inside, else "indeterminate". The family is 62 a_p and 42 c_p
   labels; a probe-level claim needs a later replication.
2. **Far-field baseline**: b "present" when its 95% interval excludes zero and class agreement holds.
3. **Additivity**: the median residual over all probes (the model sets it to zero on every probe), with its
   interval. "Additive" when the
   interval lies inside [-0.5, 0.5] kHz, "non-additive" when it lies wholly beyond one edge, else "unresolved".
   On "non-additive", R_p and Q_p are reported as patterned contrasts and decisions 2, 4 and the a_p/c_p labels
   are withdrawn.
4. **Attribution**, over probes whose D_p is resolved in the replicate (selection redone in each replicate), from
   the medians of a_p / D_p, c_p / D_p (non-isolated probes only) and b / D_p. It reads "unresolved" when class
   agreement fails (first, since a pattern-PUB offset also breaks additivity), "withdrawn" on non-additivity,
   "unresolved" when fewer than 10 probes resolve D_p in the observed data or fewer than 97.5% of replicates
   resolve any; otherwise:
   - "opposed" when any two of the three medians have opposite signs with intervals excluding zero;
   - otherwise "own-partner", "within-three-hop" or "baseline" when exactly one share's interval lies above 0.5;
   - otherwise "mixed".
5. **Replication of the probe's shift**: the all-read pair-mean shift `meas_during` against both quiet references
   is negative with a t statistic below the one-sided alpha 1e-3 quantile of t on 30 degrees of freedom (-3.385),
   with the quiet null not reading present. No decision here uses the chi-square branch of the probe's rule.

## Limits

- The partner's twelve reads write one classical bit. The probe's final-excitation bound (median -0.0005, maximum
  0.038) bounds only the population left after the train. a_p therefore cannot separate transient partner
  excitation, partner leakage, measurement-induced probe transitions, and drive on the partner's own resonator or
  feedline.
- Three CZ hops is a reproducible graph-distance cut. The registered Heron r2 sources hold no Kingston resonator
  linewidth, dispersive shift, feedline map or amplifier topology
  ([readout resonator note](../notes/ibm_quantum/heron-r2-readout-resonator.md)), so c_p is a within-three-hop
  excess and b a baseline, not a near field and a feedline drive. A physical attribution needs a feedline map or a
  cutoff-sensitivity experiment.
- A b that varies across the chip folds into c_p for the probes that see it; the isolated-probe residuals and the
  two partitions measure that heterogeneity rather than remove it.

## Open before a case

- The owner's approval of the written case, [IDLE_READOUT_ATTRIBUTION_CASE.md](../../results/live/IDLE_READOUT_ATTRIBUTION_CASE.md),
  and its binding dry run, before any submit.

Done: the analyzer and its planted-law mutation tests; the measured-run loader with the collector refusals, the
one-calibration rule and the per-class exposure gate; the execution changes; a validation dry run on the 31
pinned pairs under the 2026-10-26T20:57:35-07:00 calibration, whose local ALAP schedule puts every replica's probe
window at 561 to 10561 dt and every reading train inside it (7680 quiet-window and train pairs), and whose
predictions pass the self-check (b -0.071 kHz, interval [-0.174, 0.127]; additive; attribution unresolved).
