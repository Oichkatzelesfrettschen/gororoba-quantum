# Readout attribution of the idle phase rate on ibm_kingston: design

The idle-penalty probe ([findings](../../results/live/IDLE_PENALTY_PROBE_FINDINGS.md)) measured a negative Ramsey
phase rate on idling qubits while readout trains played: a pair mean of -2.72 kHz (t -5.1) against two quiet
references, up to -21.5 kHz on one probe, with a quiet null at -0.010 kHz. Every replica read at once, so the run
cannot say whether a probe's shift comes from its own coupled partner's readout, from readout a few couplers away,
or from readout anywhere on the chip. This campaign separates the three in one job on the probe's 31 ordered
pairs.

## Estimand

For probe p (one qubit of pair k), the phase rate in a readout window is modeled as

    delta_p = a_p * own + c_p * near + b * f_far

- `own` is 1 when the probe's own partner plays its train;
- `near` is 1 when every reading partner of another pair within three couplers of p plays (the near field);
- `f_far` is the fraction of the remaining partners that play, and `b` the far-field coefficient, one per chip.

The quiet reference fixes delta at zero. The probe's during arm sets own = near = f_far = 1 and measures
`a_p + c_p + b` without splitting them.

## Classes

Pairs fall into two classes, A and B, by a 2-coloring of the pair conflict graph: pairs k and j are joined when any
qubit of one lies within three CZ hops of any qubit of the other on the Kingston coupler graph
(`docs/evidence/heron_platform/targets.json`). That graph on the 31 pinned pairs is bipartite (28 edges, maximum
degree 3, 2 isolated pairs); the coloring, with components flipped and isolated pairs placed to balance the
classes, gives 15 pairs in A and 16 in B, in pin order:

    ABABAAABBABABBBBBABBAABAAABBBAA

Every near-field reader of a probe then sits in the opposite class. The class list is stored explicitly in the
member, not derived from replica index, so a change of path count cannot shift it.

Pattern A plays the train on class A partners and holds class B partners quiet over the same window; pattern B
swaps them. For a probe in class X:

- the own-class pattern R reads (own 1, near 0, f_far = f_same): `R_p = a_p + b f_same`;
- the opposite pattern Q reads (own 0, near 1, f_far = f_opp): `Q_p = c_p + b f_opp`;
- the all-read arm reads `D_p = a_p + c_p + b (f_same + f_opp)`.

`b` comes from probes with no other pair's reader within three hops (`Q_p = b f_opp` there; 20 of the 62 probes,
8 targets reading spectators and 12 spectators reading targets); then
`a_p = R_p - b f_same` and `c_p = Q_p - b f_opp`, and the additivity residual is `D_p - R_p - Q_p`, which the model
sets to zero. The three estimates use distinct combinations of the four arms, so the residual tests the model
rather than restating an estimator. The exact counts f_same and f_opp come from the class list.

## Members

- `meas_quiet_q` (new body, used only inside patterned members): the during arm with the partner's train replaced
  by an idle over the same barrier window, so a quiet replica's window has the reading replicas' duration and the
  ALAP schedule closes every replica together. Its ideal law equals the during arm's, because every mid-circuit
  read acts on a partner in |0>. The all-quiet reference with that barrier window is the probe's `meas_after_q`.
- `meas_half_a_q`, `meas_half_b_q`: replica k runs the during body when its class reads in that pattern and
  `meas_quiet_q` otherwise.
- `meas_short_half_a_q`, `meas_short_half_b_q`: the same patterns over the short window (SHORT_MEAS_DT, three
  reads), so every patterned phase unwraps through its own short twin, as the all-read arm does. Five probes of
  the probe run exceeded 12.5 kHz, half the 25 kHz alias, so the long-window phase alone would mis-branch them.
- Both probe roles (`idle_` and `idle_s_` prefixes), so each placed qubit gets its coefficients.

Added PUBs: 2 patterns x 2 windows x 2 quadratures x 2 probes = 16. With the probe's 44: 60 PUBs.

## Execution changes

The fused-PUB path assumes one body per member: `packing.pack` relabels one ISA per replica, `Entry` holds one
`base`, and `_member_fields` reads replica 0 only.

1. `experiments.Member` gains `replica_bodies: tuple[str, ...] | None`, one body name per replica in path order.
   `Group.__post_init__` refuses a patterned member whose bodies differ in width, classical registers or ideal law,
   or name a member outside the group; live_run refuses a plan whose replica count differs from its length.
2. live_run `_entry_bases`, `_set_entries` and `_entry`: a patterned member takes `base` from its first body and
   builds a per-replica ISA list from the compiled bodies.
3. `packing.pack` accepts a sequence of ISAs, relabels each replica's own ISA and takes the measurement-tail start
   per replica, as `packing.fuse` does for components.
4. `Entry`, `_member_fields` and `PubComponent.manifest` carry `replica_bodies` only for a patterned member;
   `_validate_archived_pub` checks each replica's archived body against it.
5. scripts/idle_penalty_report.py: `planned_idles`, `quiet_reference` and `reader_train` take the replica's body;
   `exposure_violations` checks each class's schedule within the class and adds a cross-replica check that every
   quiet replica's probe window contains every reading replica's train in absolute schedule time;
   `campaign_digest` hashes an explicit list of the probe's 44 member names, so a run of this campaign still
   compares with the probe under `--compare`.

Sequencing: these edits move `experiment_digest`, which approved records bind and `--collect` checks. The
stability repeat and focal jobs are approved and uncollected on `heron/idle-penalty-repeat`; that branch collects
on its own code, and this branch merges into it only after both collections.

Aer has no readout crosstalk, so the dry run reads a = b = c = 0; that is the self-check. Before any case, a
mutation test must recover planted a_p, c_p and b, including phases past the 25 kHz alias, from synthetic laws on
the pinned geometry, and a local ALAP schedule of the mixed PUB must show the quiet windows containing the trains.

## Placement, shots and seconds

- Placement: the probe's 31 ordered pairs, pinned.
- Shots: 4096. Per-probe phase-rate shot noise was about 0.11 kHz in the probe, so a per-probe a_p carries about
  0.11 to 0.16 kHz.
- Seconds: 16 s x 60 / 44 = 21.8 s expected at 20 us; ceiling 30 s.
- Account: backup (229 s at the 2026-10-26 20:04 PDT read, less the focal jobs' 32 s, against a 60 s reserve).

## Preregistered decisions

The between-pair spread of the probe (SD 2.95 kHz over 31 pair means, so a pair-mean standard error near
0.53 kHz) makes a cohort mean a weak instrument, so the per-probe coefficient is primary:

1. **Per probe**, `a_p`, `c_p` read "present" when |estimate| exceeds 3.29 times its shot-noise standard error,
   "absent" when the 95% interval lies inside [-0.5, 0.5] kHz, else "unresolved".
2. **Far field**: `b` with a bootstrap 95% interval over the isolated probes; "present" when the interval excludes
   zero.
3. **Attribution share**: the cohort medians of a_p / D_p, c_p / D_p and b (f_same + f_opp) / D_p over probes whose
   all-read shift D_p is present (|D_p| above 3.29 standard errors), each with a bootstrap 95% interval over pairs.
   "Local" when the a-share interval lies above 0.5; "near-field" when the c-share interval does; "far-field" when
   the b-share interval does; otherwise "mixed".
4. **Additivity**: the median residual `D_p - R_p - Q_p` over the same probes, with a bootstrap interval; outside
   [-0.5, 0.5] kHz reads "non-additive", and decision 3 is withdrawn for the run.
5. **Replication of the probe**: the all-read arm's readout_shift decision against the probe's ("present",
   negative), by the probe's own rule.

No decision uses the chi-square branch of `_mean_decision`: with conditional shot-noise errors and a heterogeneous
cohort, it reads "present" for any nonzero spread.

## Limits

- The partner's twelve reads write one classical bit, so a partner left excited by its own reads and a dispersive
  pull from the drive both land in a_p. The probe's final-excitation bound (median -0.0005, maximum 0.038) caps the
  first at about 0.2 kHz through static ZZ.
- The class split is fixed by the coupler graph. A far-field b that varies across the chip folds into c_p for the
  probes that see it.

## Open before a case

- Codex daybreak-blue review in tmux and the advisor on this document.
- The mutation test and the mixed-PUB ALAP check above.
- A written case with the binding dry run, and the owner's approval of that case before any submit.
