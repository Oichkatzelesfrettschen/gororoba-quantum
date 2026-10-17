# Case addendum: n21-feedback-encoded at 100 us with a placeholder excitation

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. It is a sizing case: the declared excitation
`--prep-excitation 0.01` is a placeholder, not a measurement, so the case
stays held until the state-prep-control pair
(`results/live/2026-10-17T193940.625280Z` and `...194115.872682Z`) supplies
the excess excitation at the shorter delay and its decision rule names the
delay and the value.

**What the run measures.** The same endpoint as the 250 us cases: the
signed-contrast difference between the feed-forward and no-feed-forward arms
of the encoded two-round N=21 order finding, one-sided, ideal laws
(3, 2, 1, 2)/8 and (3, 1, 1, 3)/8. The question is unchanged; the
repetition delay and the declared initial excitation are new planning
inputs the policy binds.

**Why noise simulation cannot answer it.** As in the 250 us case: the model
carries no feed-forward latency, idle noise, leakage, crosstalk or
measurement-induced dephasing of the spectators, and it carries the
initial excitation only as the declared 0.01 per qubit.

**Expected seconds.** One dynamic job of two PUBs at 90,112 shots per PUB,
one replica (qubits 104, 105, 106, 117, 124, 125, 126), 100 us repetition
delay, calibration 2026-10-17T12:27:27-07:00:

| PUB | Target duration (us) | rep_delay (us) | latency (us) | charge (s) |
|---|---:|---:|---:|---:|
| ibm_kingston_dynamic_pub_01 | 68.72 | 100 | 20 | 17.006 |
| ibm_kingston_dynamic_pub_02 | 69.98 | 100 | 0 | 15.317 |

Planner charge 34.623 s = 2.3 s overhead + 90,112 x 358.70 us per shot pair.
The ceiling is the smallest integer at or above 1.14 x the charge, the ratio
of the n21 record (95 s over 83.13 s): 40 s; with the 60 s reserve the run
needs 100 s of the 266 s last read.

**Against 250 us.** The 05:40 case (`results/live/2026-10-17T130242.718497Z`)
plans 83.13 s: two replicas, 122,880 shots, no excitation. This calibration
plans a different design, so the delay alone does not account for the drop:

- At the 12:27 calibration the planner admits only one replica at the
  0.55 floor, and the exact contrast with eps = 0.01 is 0.03293 against
  0.02523 for the 05:40 two-replica plan, so 90,112 shots suffice (detection
  0.01810 plus power 0.01430 = 0.03240 against the 0.03293 effect).
- At the 13:18 calibration the same command at 50 us and at the default
  delay, both with eps = 0.01, isolate the delay: see those addenda. At the
  12:27 calibration the 100 us charge per shot pair is 358.70 us against
  658.70 us at 250 us for the same circuits: 34.62 s against
  2.3 + 90,112 x 658.70 us = 61.66 s for this design at the default delay.

**Assumptions the power rests on.**
- eps = 0.01 on every active qubit; the exact model and its sampled
  falsifier both carry it (exact probabilities within 0.00273 of 65,536
  sampled shots, radius 0.00750; exact contrast 0.03293 against 0.03006
  sampled, Bernstein radius 0.01975). At the 05:40 snapshot the same
  channel lowers the exact contrast by 0.0016
  (`docs/evidence/n21_exact_model/crosscheck_prep_excitation.json`); a
  measured excess above 0.01 lowers it further and raises the shots.
- Calibration at submission: the replica count and the placed qubits moved
  between the 05:40 and 12:27 calibrations. q124 of this placement lies
  outside the fourteen qubits the state-prep-control pair measures; before
  this case is submitted the control is re-planned with `--layout` naming
  the placed qubits, or the n21 plan returns to qubits the control covers.
