# Case addendum: state-prep-control at the default delay on ibm_kingston

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. This run is the 250 us baseline of the pair whose
question, model gap and decision rule
`results/live/2026-10-17T193940.625280Z/CASE_ADDENDUM.md` states; the
decision reads both runs.

**What this run adds.** The same three PUBs on the same fourteen qubits at
the backend's default repetition delay (250 us, no `--rep-delay`), so A here
is the reference the 50 us excess subtracts. A also checks the calibration's
own prob_meas1_prep0, which IBM measures at the default delay: a qubit whose
A leaves its e10 by more than its 3-sigma binomial radius carries an
excitation the n21 noise model misprices even at 250 us.

**Expected seconds.** Two jobs, 8192 shots per PUB:

| Job | PUBs | Planner charge (s) | Ceiling (s) |
|---|---:|---:|---:|
| ibm_kingston/static/1 (A, C) | 2 | 6.432 | 8 |
| ibm_kingston/dynamic/1 (B) | 1 | 4.384 | 8 |

Planner charge 10.816 s: 2 x 2.3 s overhead plus 8192 x (250 us + Target
duration) per PUB. Ceiling: the smallest integer at or above 1.14 x the
larger job's charge (7.33 s), 8 s per job and 16 s combined, with the 60 s
reserve; the 50 us run adds 5.901 s against 8 s of ceilings.

**Order.** Submit the two runs back to back, after a fresh dry run of each
under one calibration: the excess compares two jobs, and a recalibration
between them moves e10 and e01 under the comparison. The C columns of the two
runs carry the check (rule 2 of the paired addendum).
