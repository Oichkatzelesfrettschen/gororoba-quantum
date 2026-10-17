# Case addendum: n21-feedback-encoded at 50 us with a placeholder excitation

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. Like the 100 us case
(`results/live/2026-10-17T201931.783685Z`), it is a sizing case whose
declared excitation `--prep-excitation 0.01` is a placeholder; it stays
held until the state-prep-control pair (`...193940.625280Z`,
`...194115.872682Z`) measures the excess excitation at 50 us and its
decision rule selects this delay.

**What the run measures and why noise simulation cannot answer it.** As in
the 100 us addendum: the feed-forward contrast of the encoded N=21 pair, with
the model gaps (latency, idle noise, leakage, crosstalk, measurement-induced
dephasing) and the declared excitation as the only initial-state error.

**Expected seconds.** One dynamic job of two PUBs at 98,304 shots per PUB,
one replica (qubits 104, 105, 106, 117, 124, 125, 126), 50 us repetition
delay, calibration 2026-10-17T13:18:45-07:00:

| PUB | Target duration (us) | rep_delay (us) | latency (us) | charge (s) |
|---|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 68.69 | 50 | 20 | 13.634 |
| ibm_kingston_dynamic_pub_02 | 69.98 | 50 | 0 | 11.794 |

Planner charge 27.728 s = 2.3 s + 98,304 x 258.67 us per shot pair; ceiling
32 s, the smallest integer at or above 1.14 x the charge (the n21 record's
95 s over 83.13 s); with the 60 s reserve the run needs 92 s of the 266 s
last read.

**Against 250 us.** The same command at the default delay and the same
calibration, `results/live/2026-10-17T204710.144206Z`, selects the same
design (98,304 shots, one replica, contrast 0.03128 with eps = 0.01) and
plans 67.049 s (ceiling 77 s); 50 us saves 39.32 s of it, the 200 us of
delay removed from each of 2 x 98,304 executions. The 05:40 case plans
83.13 s with two replicas and 122,880 shots at eps = 0; the rest of that
difference is the calibration's, which admits one replica and a larger
contrast now.

**Power at these shots.** Detection 0.01733 plus power 0.01369 = 0.03102
against the exact effect 0.03128 at eps = 0.01: a margin of 0.00026, so an
excess near 0.01 already sits at the edge, and any larger measured excess
moves the plan to the next tier (106,496 shots, 29.85 s at this delay) or
beyond. The exact model passes its falsifier (probabilities within 0.00335
of 65,536 sampled shots, radius 0.00750; contrast 0.03128 exact against
0.03146 sampled, radius 0.02004).

**Placement.** q124 lies outside the fourteen qubits the control pair
measures; the control is re-planned with `--layout` naming the placed
qubits before this case can be sized on a measured excess.
