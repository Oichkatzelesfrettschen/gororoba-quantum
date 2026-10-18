# Case addendum: n21-feedback-encoded at 50 us under the empirical-Bernstein detection rule

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. It re-plans the 50 us sizing case of
`results/live/2026-10-17T203941.331080Z` with `--empirical-bernstein`; the
declared excitation `--prep-excitation 0.01` is still the placeholder the
state-prep-control pair (`...193940.625280Z`, `...194115.872682Z`) replaces,
so the case stays held until that pair measures the excess at 50 us.

**What the run measures and why noise simulation cannot answer it.** As in
the 100 us and 50 us addenda: the feed-forward contrast of the encoded N=21
pair, one-sided against zero, with the model gaps (latency, idle noise,
leakage, crosstalk, measurement-induced dephasing) and the declared
excitation as the only initial-state error.

**Detection rule.** Each PUB's confidence and detection radius is the
smaller of the Hoeffding radius and the Maurer-Pontil empirical-Bernstein
radius (arXiv:0907.3740 Theorem 4), each at half of alpha: 0.05 = 0.025
data-free + 0.025 empirical-Bernstein. The record's `empirical_bernstein`
block and the case's section of that name preregister the inequality, the
split, the planned variances and the per-PUB radii. Planning reads the exact
law's variance raised to its Theorem 10 (4) upper limit, 0.54585 and
0.54505 for the two PUBs, and runs the power radius at tail 0.199, the miss
probability 0.2 less the 0.001 variance tail. Collection recomputes each
empirical-Bernstein radius from the measured frequencies; a variance above
plan widens it and costs power, never coverage.

**Expected seconds.** One dynamic job of two PUBs at 90,112 shots per PUB,
one replica (qubits 104, 105, 106, 117, 124, 125, 126), 50 us repetition
delay, calibration 2026-10-17T13:50:45-07:00:

| PUB | Target duration (us) | rep_delay (us) | latency (us) | charge (s) |
|---|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 68.59 | 50 | 20 | 12.488 |
| ibm_kingston_dynamic_pub_02 | 68.65 | 50 | 0 | 10.692 |

Planner charge 25.480 s = 2.3 s + 90,112 x 257.24 us per shot pair;
ceiling 30 s, the smallest integer at or above 1.14 x the charge; with the
60 s reserve the run needs 90 s of the 266 s last read.

**Against the Hoeffding plan.** PR #229's 50 us record plans 98,304 shots
and 27.728 s at the 13:18 calibration; re-planned from that record under
this rule it needs 90,112 shots and 25.609 s. At this record's calibration
the same design under Hoeffding needs the 106,496 tier and 29.695 s
(100,352 shots at 1024-shot resolution against 89,088 under this rule), so
the rule saves 4.21 s at this calibration and 2.12 s at PR #229's; the rest of
that difference is the calibration's, whose exact contrast moved from
0.03128 to 0.03073.

**Power at these shots.** Detection 0.016202 plus power 0.014313 = 0.030516
against the exact effect 0.030731: a margin of 0.00022. Hoeffding at the
full alpha gives detection 0.018097 at these shots. The exact model passes
its falsifier: probabilities within 0.00334 of 65,536 sampled shots (radius
0.00750), contrast 0.03073 exact against 0.03410 sampled (Bernstein radius
0.02004).

**Placement.** q124 lies outside the fourteen qubits the control pair
measures; the control is re-planned with `--layout` naming the placed
qubits before this case can be sized on a measured excess.
