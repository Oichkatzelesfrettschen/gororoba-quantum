# Case addendum: n21-feedback-encoded at the 04:20 Kingston calibration

Status: UNAPPROVED and SUPERSEDED by `results/live/2026-10-17T130242.718497Z`
(05:40 calibration, 122,880 shots, 83.1 s). This record's plan and its
preregistered falsifier read the declared variance whenever the sample
variance stayed within the allowance of it; a true variance above the
declaration but inside the allowance then shrank the radii below their
stated level. The superseding run reads each bound through its variance
upper confidence limit and spends the falsifier tail from alpha (0.05 =
0.001 + 0.049); under that rule this calibration needs 130,627 shots
(88.2 s) at R = 2, so the 131,072 tier still admits, and 180,205 (120.8 s)
at R = 1. The experiment digest has changed, so the runner refuses to submit
against this record; it stays as an audit record.

This addendum accompanies `UNAPPROVED_CASE.md` and authorizes nothing. It
supersedes the cases of the dry runs
2026-10-17T101105Z (02:30 calibration, 118,784 shots, 80.4 s) and
2026-10-17T111902Z (03:41 calibration; its generated case named the
contrast check's radius Hoeffding where the code computes Bernstein). Both
stay in place as audit records.

**What the run measures.** The signed-contrast difference between the
feed-forward and no-feed-forward arms of the encoded two-round N=21 order
finding, one-sided at alpha 0.05: whether removing the semiclassical
correction changes the device's two-bit outcome distribution in the
predicted direction (ideal laws (3, 2, 1, 2)/8 and (3, 1, 1, 3)/8).

**Why noise simulation cannot answer it.** The Aer model predicts the
contrast (0.0242 averaged over the two replicas, exact branch-resolved law)
from reported gate, readout and T1/T2 calibration alone. It carries no
feed-forward latency, no idle noise (the ISA carries no scheduled delays),
no leakage, no crosstalk and no measurement-induced dephasing of the
spectator qubits during the mid-circuit readout; whether the device's
contrast survives those channels is the question, and only the device
answers it.

**Expected seconds.** One dynamic job of two PUBs, 131,072 shots per PUB,
two replicas per shot (qubits 104, 105, 106, 107, 117, 125, 126 and 57, 65,
66, 67, 68, 69, 70), 250 us repetition delay. Planner charge 88.5 s
(2.3 s overhead plus 131,072 x 657.5 us). The metered model of the 23
pinned retained jobs (scheduler duration = Target bound + 2246 dt + 133 dt
per feed-forward stage; charge = ceil(execution + 1.7 s)) gives 88 s.
Service ceiling 95 s per job; with the 60 s reserve the run needs 155 s of
the 266 s last read.

**Preregistered replica covariance falsifier.** The power above rests on
the declared bound: per-replica score variance at most 0.55 and independent
replicas. Collection tests it on the retained shot-ordered replica registers
before applying it (`n21_exact_planning.covariance_falsifier`, record.json
`covariance_falsifier`):

- Statistic, per PUB: the biased sample variance over the 131,072 shots of
  the replica-average signed score Y = (s_r0 + s_r1) / 2 (weights +1/2 on the
  feedback PUB, -1/2 on the control PUB).
- Threshold, per PUB: the declared projection 0.55 / 2 = 0.275 plus the
  Hoeffding allowance eps2 + D eps1 with D = 2, s = sqrt(ln(4 / t) / (2n)),
  eps1 = D s, eps2 = (D^2 / 4) s, t = 1e-3 / 2: 0.275 + 0.0293 = 0.3043.
- Decision: both PUBs at or below 0.3043 apply the declared bound; either
  above it, or either PUB's registers absent, analyzes the endpoint under the
  Hoeffding arbitrary-dependence radius. collect.json's
  `family_analysis.replica_covariance` records the branch, both statistics
  and the power condition; `scripts/n21_replica_covariance.py --run-dir`
  replays it from the raw files.

At R = 2 the detection radius is Hoeffding's in both branches (0.01501), so
the directional decision, reject above 0.01501, does not depend on the
falsifier. Only the power statement does: the declared branch's power
radius is 0.00869 (Cantelli), the Hoeffding branch's 0.01185, and
detection plus power 0.02686 then exceeds the admitted effect 0.02423, so
the Hoeffding branch reports the endpoint underpowered. The one-replica
Hoeffding design needs 180,205 shots, 120.8 s, above the ceiling.

**Assumptions the power rests on.**
- The exact model law. In this dry run every probability lies within 0.0043
  of its 65,536-shot sample (radius 0.0078) and the contrast reads 0.0242
  exact against 0.0278 sampled, inside a Bernstein radius of 0.0207 that is
  about the effect itself: this check cannot see a bias of 10 percent of the
  contrast. The Kaggle pool of 589,824 shots per arm (12:13 snapshot, gate
  core-485) passes every check but reads its contrast 2.04 standard
  deviations below the exact law, 0.0282 against 0.0308. If the true model
  contrast here were the same 0.914 of the exact one, 0.0221, power 0.8
  would need about 150,070 shots per arm, 101.0 s, above the 95 s ceiling;
  the 131,072-shot plan would then fall short of power 0.8 while keeping
  its alpha.
- The declared replica covariance, tested at collection as above.
- Calibration at submission. The modeled one-replica contrast moved from
  0.0308 to 0.0229 between 12:13 and 03:41; the runner re-plans at
  submission and stops for renewed approval when the fresh plan differs from
  this record.

The full decomposition and every lever are in
`gororoba_quantum/N21_USAGE_BUDGET.md`.
