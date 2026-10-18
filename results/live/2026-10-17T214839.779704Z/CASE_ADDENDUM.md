# Case addendum: n21-feedback-encoded at the default delay under the empirical-Bernstein detection rule

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. It is the default-delay reference of the 50 us case
`results/live/2026-10-17T214153.170495Z`: the same command with
`--empirical-bernstein` and `--prep-excitation 0.01`, without `--rep-delay`.

**Calibration.** This record reads the ibm_kingston calibration stamp
2026-10-17T14:35:51-07:00, the 50 us record 13:50:45. Both select the same
placement (qubits 104, 105, 106, 117, 124, 125, 126), the same Target
durations (68.59 and 68.65 us) and the same exact contrast 0.0307314410552,
so the two records differ in the repetition delay alone.

**Expected seconds.** One dynamic job of two PUBs at 90,112 shots per PUB,
one replica, 250 us: planner charge 61.525 s = 2.3 s + 90,112 x 657.24 us
per shot pair (PUB charges 30.511 s and 28.714 s); ceiling 71 s, the
smallest integer at or above 1.14 x the charge; with the 60 s reserve it
needs 131 s of the 266 s last read. 50 us saves 36.04 s of it.

**Against the Hoeffding plan.** PR #229's default-delay record plans 98,304
shots and 67.049 s at the 13:18 calibration; re-planned from that record
under this rule it needs 90,112 shots and 61.654 s. At this calibration the
same design under Hoeffding needs the 106,496 tier and 72.293 s, above this
case's 71 s ceiling, so the rule saves 10.77 s at this calibration and
5.40 s at PR #229's.

**Detection rule and power.** As in the 50 us addendum: 0.05 = 0.025
data-free + 0.025 empirical-Bernstein per endpoint, planned variances 0.54585
and 0.54505, power radius at tail 0.199. Detection 0.016202 plus power
0.014313 = 0.030516 against the exact effect 0.030731, margin 0.00022.

**Use.** At 250 us the calibration's prob_meas1_prep0 already carries the
default-delay excitation, so the 0.01 placeholder double-counts it; the
record prices the delay and the rule. Submitted at 250 us, the n21 run takes
`--prep-excitation` from the state-prep-control baseline only where that
run's A exceeds the calibration's e10 beyond its 3-sigma radius (the
baseline check of `results/live/2026-10-17T194115.872682Z/CASE_ADDENDUM.md`),
and is otherwise planned without it.
