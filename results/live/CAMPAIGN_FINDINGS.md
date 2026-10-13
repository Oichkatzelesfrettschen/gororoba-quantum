# QPU campaign findings

This note interprets every retained hardware acquisition: nine Runtime jobs
in six acquisitions on ibm_kingston and ibm_fez, 2026-10-11 to 2026-10-13.
Each section names its retained record, the measured quantity, the result,
and what the result does and does not establish. Numbers come from the named
`collect.json`, adjudication or analysis files. The coordination ledger
[qpu-coordination.json](qpu-coordination.json) carries the job ids and
settled charges of sections 2-6; the pilot's record and adjudication carry its
own job and 9-second charge.

## 1. Pilot: hybrid Shor and folded QPE, mod 15

Record [2026-10-11T152922.787095Z](2026-10-11T152922.787095Z/ADJUDICATION.md),
job `db5qmqclf4us73c4e1ug`, ibm_kingston, six dynamic PUBs at 4096 shots.

- The hybrid Shor factor yield is 0.4971 [0.4726, 0.5216] against the exact
  uniform null 0.2969 and the identity null 0.0042. For order 4 the ideal
  outcome law is the same with and without the conditional phases, so the
  yield validates the controlled arithmetic and the decoder on hardware and
  leaves the feed-forward untested.
- Packed replica 0 against its isolated reference on identical qubits gives
  +0.0020 (hybrid Shor) and -0.0037 (folded QPE), inside the 0.03 margin
  under the preregistered Newcombe interval; the distribution-free 90 percent
  interval for folded QPE, [-0.0306, +0.0234], crosses that margin. The
  scheduler tables show identical per-qubit instruction sequences, and
  shot-wise failure correlation across the fifteen replica pairs of the
  packed PUB stays below 0.045.
- Correctness per 512-shot block stays within sampling error: no drift
  inside a job.
- Execution takes 272.9 us per shot against a 250 us default repetition delay
  and a 22.9 us mean circuit: the repetition delay dominates charged time.

## 2. Folded-QPE intervention ladder

Record [2026-10-12T055624.091217Z](2026-10-12T055624.091217Z/ANALYSIS.md),
jobs `db67fqsvf2bc73d0pk4g` and `db67frimb58s738bci4g`, ibm_kingston, 16 PUBs
at 8192 shots: archived dynamic QPE, a delay arm, a no-feed-forward arm and a
coherent two-control arm for each eigenstate label.

- Coherent minus archived terminal accuracy is +5.8 to +10.9 percentage
  points with every simultaneous interval above zero. The two-control circuit
  outperforms the measurement-and-feed-forward circuit on this device.
- Delay minus archived intervals all contain zero (estimates -0.3 to +1.9
  points). The run detects no difference and establishes no equivalence: the
  s0 interval still allows a +6.0-point gain, comparable to the smallest
  coherent-arm gain, so the measurement's share of the loss stays open.
- Odd-label no-feed-forward intervals fall below zero, as the exact law
  predicts: the correction carries real information on hardware.
- The coherent arm also changes routing, the terminal readout qubit and the
  control count, so its advantage is a property of the complete
  implementations, not a single isolated mechanism.

## 3-4. Folded correction: measured bit against known label

Records [2026-10-13T020454.599853Z](2026-10-13T020454.599853Z/analysis-1fdb68508f14.json)
(job `db6p55clf4us73c5nd9g`) and
[2026-10-13T022433.333775Z](2026-10-13T022433.333775Z/collect.json)
(job `db6pepklf4us73c5nqcg`), ibm_kingston, four dynamic PUBs at 8192 shots
per run (eight in total), 11 s each against 11.59 s predicted.

- Both runs reach `retain_measured_correction`: known-label correction does
  not clear the preregistered +0.01 gain on both odd labels; the one-sided
  rule establishes neither equivalence nor absence of improvement (gain lower bounds
  -0.021 and -0.0077 in the first run, -0.0346 and -0.0006 in the second).
- Known-label correction beats measured-bit correction on s3 in both runs
  (+0.013, +0.021) and not on s1.
- About 11 percent of shots record the first bit as 0 in every arm. Within
  that stratum the arms reverse by label (s3: known 0.567 and 0.553 against
  measured 0.451 and 0.429; s1: measured 0.573 and 0.553 against known 0.540
  and 0.512). An assignment error favors the known label; a true state change
  favors the recorded bit. [Roadmap item 9](../../docs/RESEARCH_ROADMAP.md)
  turns this into a repeated-readout and delayed-readout experiment.
- The exposed scheduler table places the else-branch frame update 4 dt after
  the then-branch update in every PUB, and the pulse-window schedule rule
  qualifies both runs; per-shot controller timing remains uncertified.

## 5. Ripple: box-kite contrasts and depth-4 class return

Record [2026-10-13T025444.603480Z](2026-10-13T025444.603480Z/collect.json),
jobs `db6q2p2mb58s738c75gg` and `db6q2rklf4us73c5oq90`, ibm_fez, 146 static
PUBs (929 logical entries), 66 s against 63.97 s predicted.

- All 84 registered box-kite bright-minus-dark contrasts reject the null under
  family-wise Hoeffding bounds, with estimates +0.282 to +0.731: every
  configured contrast has its predicted sign on hardware. The rejections
  establish those signs; exact zeros, rank and topology stay outside them,
  since the circuits encode the selected edges.
- The separately registered depth-4 class-return contrast is null:
  -0.0101 [-0.0848, +0.0645], against a detection radius of 0.072. The run
  rules out a class return larger than about 0.085 in either direction and
  cannot distinguish a smaller one from zero. A follow-up that spends its
  shots on the class-return PUBs alone shrinks that interval; it either
  detects the return or bounds it below the size that matters.

## 6. Rank-sector: sector contrasts and pulse-difference laws

Record [2026-10-13T032011.664435Z](2026-10-13T032011.664435Z/collect.json),
jobs `db6q9qo4qg6s73c57020` and `db6q9rsvf2bc73d1kpug`, ibm_fez, 36 static
PUBs (176 logical entries), 31 s against 30.41 s predicted.

- All 8 sector bright-minus-dark-at-one contrasts reject the null, +0.612 to
  +0.868.
- All 12 pulse-difference laws in sectors 4-7 reject the null: the zero-two
  t1d2-t0d1 law at +0.435 to +0.486, the zero-two t3d2-t2d1 law at +0.249 to
  +0.276 and the one-two t1d2-t1d1 law at +0.111 to +0.126. The ordering of
  the three laws is consistent across the four sectors.

## Findings across runs

- **The charge model holds to about 5 percent.** Settled charges differ from
  prediction by -5.1 percent (11 against 11.59 s, twice), +3.2 percent (66
  against 63.97 s) and +1.9 percent (31 against 30.41 s), so ceilings near
  1.1 times nominal charge cover every observed run.
- **Repetition delay is the largest cost.** Shots are short compared with the
  250 us default delay; a tuned delay is the largest available per-second
  saving and needs its own accuracy check, because it trades relaxation time
  for throughput.
- **Packing showed no measured loss in the pilot's layouts.** Packed and
  isolated replica 0 agree under the preregistered statistic, and replica
  failures were uncorrelated; that evidence covers the pilot PUB's layouts
  and statistic, so each new packed family keeps its own reference check.
- **The recorded first bit disagrees with the prepared label in about 11
  percent of correction shots,** an effect larger than the measured
  correction contrast; assignment error and a true state change both remain
  candidate explanations.
- **Open question.** Coherent control gains 6 to 11 points on the ladder,
  while the delay arm detects no difference and the correction arms show no
  preregistered gain. Neither result rules out the mid-circuit measurement as
  a contributor. Roadmap item 9 separates assignment from true state error,
  and the coherent arm's routing and readout-qubit changes remain a separate
  candidate explanation.
