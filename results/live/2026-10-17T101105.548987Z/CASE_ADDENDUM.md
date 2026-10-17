# Case addendum: n21-feedback-encoded at the 02:30 Kingston calibration

Status: UNAPPROVED and SUPERSEDED by `results/live/2026-10-17T114216.070396Z`
(04:20 calibration, 131,072 shots, 88.5 s), whose case and addendum carry
the collection-time covariance falsifier and the exact-model bias
sensitivity. This record stays as an audit record; its experiment digest
predates those changes, so the runner refuses to submit against it. This
addendum accompanies `UNAPPROVED_CASE.md` and authorizes nothing.

**Replica covariance falsifier, as preregistered for this design.** The
statistic is, per PUB, the biased sample variance over the 118,784 shots of
the replica-average signed score (weights +1/2 on the feedback PUB, -1/2 on
the control PUB). The threshold is the declared projection 0.55 / 2 = 0.275
plus the Hoeffding allowance eps2 + D eps1, D = 2, s = sqrt(ln(4 / t) / (2n)),
eps1 = D s, eps2 = (D^2 / 4) s, t = 1e-3 / 2: 0.275 + 0.0308 = 0.3058. Both
PUBs at or below it apply the declared bound; otherwise the endpoint takes
the Hoeffding radius, which leaves the detection threshold unchanged at R = 2
and reports the power underpowered.

**What the run measures.** The signed-contrast difference between the
feed-forward and no-feed-forward arms of the encoded two-round N=21 order
finding, one-sided at alpha 0.05: whether removing the semiclassical
correction changes the device's two-bit outcome distribution in the
predicted direction (ideal laws (3, 2, 1, 2)/8 and (3, 1, 1, 3)/8).

**Why noise simulation cannot answer it.** The Aer model predicts the
contrast (0.0252 averaged over the two replicas, exact branch-resolved law)
from reported gate, readout and T1/T2 calibration alone. It carries no
feed-forward latency, no idle noise (the ISA carries no scheduled delays), no leakage, no
crosstalk and no measurement-induced dephasing of the spectator qubits
during the mid-circuit readout; whether the device's contrast survives those
channels is the question, and only the device answers it.

**Expected seconds.** One dynamic job of two PUBs, 118,784 shots per PUB,
two replicas per shot (qubits 104, 105, 106, 107, 117, 125, 126 and 57, 65,
66, 67, 68, 69, 70), 250 us repetition delay. Planner charge 80.4 s
(2.3 s overhead plus 118,784 x 657.5 us). The metered model of the 23
retained jobs (scheduler duration = Target bound + 2246 dt + 133 dt per
feed-forward stage; charge = ceil(execution + 1.7 s)) gives 80 s. Service
ceiling 95 s per job; with the 60 s reserve the run needs 155 s of the
266 s last read.

**Assumptions the power rests on.**
- The exact model law (validated against 65,536 sampled shots per replica
  in the dry run and 589,824 Kaggle shots, gate core-485).
- Per-replica score variance at most 0.55 and independent replicas
  (one-hop-buffered disjoint placements). After collection,
  `"$PYTHON" scripts/n21_replica_covariance.py --run-dir RUN` tests that
  bound on the shot-ordered raw registers; a failure sends the analysis to
  the arbitrary-dependence Hoeffding radius, which needs 154,202 shots for
  the same power at this contrast. One replica without that assumption
  costs 103.7 s.
- Calibration at submission. The modeled contrast moved from 0.0308 to
  0.0248 between 12:13 and 02:30; the runner re-plans at submission and
  stops for renewed approval when the fresh plan differs from this record.

The full decomposition and every lever are in
`gororoba_quantum/N21_USAGE_BUDGET.md`.
