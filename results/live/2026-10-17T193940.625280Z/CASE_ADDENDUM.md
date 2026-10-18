# Case addendum: state-prep-control at 50 us on ibm_kingston

Status: UNAPPROVED. This addendum accompanies `UNAPPROVED_CASE.md` and
authorizes nothing. The case is a pair: this run at `--rep-delay 0.00005`
and the baseline `results/live/2026-10-17T194115.872682Z` at the backend
default (250 us). Each run is its own approval, but the decision below reads
both, so approving one without the other answers no question.

**What the pair measures.** On the fourteen n21-feedback-encoded R = 2
qubits of the retained dry run `results/live/2026-10-17T130242.718497Z`
(57, 65, 66, 67, 68, 69, 70, 104, 105, 106, 107, 117, 125, 126), the
excited fraction after Runtime's implicit initialization (PUB A,
init-measure), after an added active reset (PUB B), and after an X (PUB C,
the |1> column of the assignment matrix), every qubit in every shot. The
excess A(50 us) - A(250 us) per qubit is the residual excitation the shorter
delay adds; IBM's repetition-rate guide states it rises as the delay falls
and gives no number for Kingston.

**Why noise simulation cannot answer it.** The calibration noise model
starts every qubit in |0>, so its only source of a 1 after initialization
is the readout channel prob_meas1_prep0, and it predicts zero excess by
construction. The residual excitation is a
device property at a given delay, and only the device has it.

**Expected seconds (this run).** Two jobs, 8192 shots per PUB:

| Job | PUBs | Planner charge (s) | Ceiling (s) |
|---|---:|---:|---:|
| ibm_kingston/static/1 (A, C) | 2 | 3.155 | 4 |
| ibm_kingston/dynamic/1 (B) | 1 | 2.746 | 4 |

Planner charge 5.901 s: 2 x 2.3 s declared overhead plus 8192 x (50 us +
Target duration) per PUB, the Target durations being 2.18 us (A), 2.21 us
(C) and 4.39 us (B, reset plus measure). The ceiling is the smallest integer
at or above 1.14 x the larger job's charge, the ratio the n21 record used
(95 s over 83.13 s): 4 s per job, 8 s combined. The baseline run costs
10.816 s (6.432 s and 4.384 s, ceilings 8 s, 16 s combined), so the pair
plans 16.72 s against 24 s of ceilings. With the 60 s reserve the pair needs
84 s of the 266 s the dry runs read. The plan's earlier estimate of about
12 s counted one job per delay; the job-kind split runs the reset in its own
job, which adds a 2.3 s overhead per delay.

**Resolution.** The 42 recorded precision endpoints (A, A - B and C per
qubit, half-widths 0.025, 0.05 and 0.025 at alpha 0.05 / 42 each) are
Hoeffding radii valid under any dependence between qubits; 8192 shots is the
smallest admitted tier (0.0213 against 0.025; 4096 gives 0.0301). The
excess comparison spans two runs, so it sits outside those contracts and
uses the binomial standard error of each run's A: at the calibrated
prob_meas1_prep0 p, 3 x sqrt(2 p (1 - p) / 8192) ranges from 0.0010 (q105,
q117) to 0.0065 (q70); the median over the fourteen qubits is 0.0031.

**Decision rule, stated before measuring.**

1. Per qubit, excess eps_q = (A_q(50 us) - A_q(250 us)) / (1 - e01 - e10)
   with the calibration's e10 = prob_meas1_prep0 and e01 = prob_meas0_prep1
   (diagnostic_experiments.state_prep_excitation applied to the difference);
   its upper bound adds 3 x sqrt(var A(50) + var A(250)) / (1 - e01 - e10)
   from the observed binomial variances. The default-delay excitation is
   already inside the calibration's e10, which the n21 model applies, so
   only the excess enters `--prep-excitation`.
2. eps = the largest upper bound over the seven qubits of the replica the
   n21 plan places (all fourteen if it places R = 2). The C column of both
   runs must agree within its own 3-sigma binomial radius on every qubit;
   a moved |1> column means the readout channel changed between the jobs
   and the pair answers nothing.
3. Re-run the n21-feedback-encoded dry run at `--rep-delay 0.00005
   --prep-excitation eps`. Admitted with power 0.8 inside its ceiling: run
   n21 at 50 us. Otherwise re-run at `--rep-delay 0.0001` with the same eps
   (the guide's curve falls monotonically with delay, so the 50 us excess
   bounds the 100 us one): admitted, run at 100 us. Otherwise n21 keeps
   250 us; the falsifier of the shortened plan is then met and the pair's
   16.7 s is the price of knowing it.
4. An initial reset enters the n21 circuits only on a qubit whose A - B
   interval at the chosen delay lies above zero; that is a circuit change
   with its own dry run and case.

The n21 placeholder dry runs at eps = 0.01 (results/live/ records listed in
the 100 us and 50 us addenda) show the charge such a plan would carry.
