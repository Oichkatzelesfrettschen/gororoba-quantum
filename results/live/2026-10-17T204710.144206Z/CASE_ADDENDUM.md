# Case addendum: n21-feedback-encoded at the default delay with a placeholder excitation

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. This record is the same-calibration reference of the
50 us case `results/live/2026-10-17T203941.331080Z`: the same command
without `--rep-delay`, both planned under the 2026-10-17T13:18:45-07:00
calibration with `--prep-excitation 0.01`, so the two records differ in
the repetition delay alone.

**Expected seconds.** One dynamic job of two PUBs at 98,304 shots per PUB,
one replica (qubits 104, 105, 106, 117, 124, 125, 126), 250 us: planner
charge 67.049 s = 2.3 s + 98,304 x 658.67 us per shot pair (PUB charges
33.294 s and 31.455 s); ceiling 77 s, the smallest integer at or above 1.14
x the charge; with the 60 s reserve it needs 137 s of the 266 s last read.

**Use.** At 250 us the calibration's prob_meas1_prep0 already carries the
default-delay excitation, so a placeholder of 0.01 here double-counts it;
the record exists to price the delay, not to be submitted as is. Submitted
at 250 us, the n21 run takes `--prep-excitation` from the state-prep-control
baseline only where that run's A exceeds the calibration's e10 beyond its
3-sigma radius (the baseline check of
`results/live/2026-10-17T194115.872682Z/CASE_ADDENDUM.md`), and is otherwise
planned without it.
