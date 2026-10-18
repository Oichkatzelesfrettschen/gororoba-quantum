# Case addendum: n21-feedback-encoded at the 05:40 Kingston calibration

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. It supersedes the cases of the dry runs
2026-10-17T101105Z, 2026-10-17T111902Z and 2026-10-17T114216Z, which were
planned under the rule that read the declared replica variance whenever its
falsifier did not reject it. Those records stay as audit records.

**What the run measures.** The signed-contrast difference between the
feed-forward and no-feed-forward arms of the encoded two-round N=21 order
finding, one-sided: whether removing the semiclassical correction changes
the device's two-bit outcome distribution in the predicted direction (ideal
laws (3, 2, 1, 2)/8 and (3, 1, 1, 3)/8).

**Why noise simulation cannot answer it.** The Aer model predicts the
contrast (0.0252 averaged over the two replicas, exact branch-resolved law)
from reported gate, readout and T1/T2 calibration alone. It carries no
feed-forward latency, no idle noise (the ISA carries no scheduled delays),
no leakage, no crosstalk and no measurement-induced dephasing of the
spectator qubits during the mid-circuit readout; whether the device's
contrast survives those channels is the question, and only the device
answers it.

**Expected seconds.** One dynamic job of two PUBs, 122,880 shots per PUB,
two replicas per shot (qubits 104, 105, 106, 107, 117, 125, 126 and 57, 65,
66, 67, 68, 69, 70), 250 us repetition delay. Planner charge 83.1 s
(2.3 s overhead plus 122,880 x 657.5 us). The metered model of the 23
pinned retained jobs gives 83 s. Service ceiling 95 s per job; with the
60 s reserve the run needs 155 s of the 266 s last read.

**Preregistered replica covariance rule.** The power rests on the declared
bound: per-replica score variance at most 0.55 and independent replicas,
projection 0.55 / 2 = 0.275 for each PUB's replica-average score. Collection
never reads the bare declaration:

- Statistic, per PUB: the biased sample variance over the 122,880 shots of
  the replica-average signed score (weights +1/2 on the feedback PUB, -1/2 on
  the control PUB).
- Upper confidence limit, per PUB: UCL = statistic + eps2 + D eps1 with
  D = 2, s = sqrt(ln(4 / t) / (2n)), eps1 = D s, eps2 = (D^2 / 4) s,
  t = 1e-3 / 2; the allowance is 0.0302 at these shots.
- Decision: a PUB's radius reads 0.275 when its UCL is at or below 0.275 and
  the UCL otherwise, through Cantelli only where that beats Hoeffding.
  Absent or inconsistent registers leave the endpoint on the Hoeffding
  radius at the full alpha 0.05.
- Alpha split: 0.05 = falsifier tail 0.001 + confidence and detection tail
  0.049; the power tail stays 0.2.
- collect.json's `family_analysis.replica_covariance` records each PUB's
  sample variance, UCL, variance used, the branch and the alpha split;
  `scripts/n21_replica_covariance.py --run-dir` replays it from the raw
  files.

The plan sized the shots on that rule: each PUB's projection is 0.275 plus
the 0.0302 allowance, the variance collection reads when the sample
variance meets the declaration, at alpha 0.049. The detection radius at
these shots is Hoeffding's, 0.01554, so the directional decision does not
depend on the bound; the power radius is 0.00946 (Cantelli) against 0.01224
for Hoeffding alone, and detection plus power, 0.02500, covers the admitted
effect 0.02523. The Aer model puts each replica's score variance at 0.494
to 0.496, so with independent replicas the expected UCL is near
0.248 + 0.030 = 0.278: above the declared 0.275, so collection reads the
UCL, and below the planned 0.305. A device variance well above the model's,
or replica correlation, raises the UCL past 0.305 and leaves the endpoint
underpowered, which collect.json reports.
Without retained registers the Hoeffding fallback rejects above 0.01550 and
detection plus power, 0.02774, leaves the endpoint underpowered.

Under the earlier declared-variance rule this calibration would admit R = 2
at 115,591 shots (78.3 s); the UCL rule needs 120,625 (81.6 s), and the
optimizer took the 122,880 tier. One replica needs 152,183 shots, 102.4 s,
above the ceiling.

**Assumptions the power rests on.**
- The exact model law. In this dry run every probability lies within 0.0044
  of its 65,536-shot sample (radius 0.0078) and the contrast reads 0.0252
  exact against 0.0240 sampled, inside a Bernstein radius of 0.0208 that is
  about the effect itself. The Kaggle pool of 589,824 shots per arm (12:13
  snapshot, gate core-485) reads its contrast 2.04 standard deviations below
  the exact law; at that 0.914 fraction the effect would be 0.0231 and power
  0.8 would need about 144,353 shots, 97.3 s, above the 95 s ceiling.
- The replica covariance rule above.
- Calibration at submission. The modeled one-replica contrast moved between
  0.0229 and 0.0308 over eighteen hours; the runner re-plans at submission
  and stops for renewed approval when the fresh plan differs from this
  record.

The full decomposition and every lever are in
`gororoba_quantum/N21_USAGE_BUDGET.md`.
