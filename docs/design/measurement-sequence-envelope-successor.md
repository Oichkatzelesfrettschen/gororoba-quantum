# Measurement-sequence envelope successor: an equalized end state and an in-job carryover bound

Status: design v2, after the adversarial review and the advisor review of v1; Codex review pending. The width-32
envelope run of 2026-10-27 (`results/live/2026-10-27T014422.881898Z`,
[findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)) executed as planned and billed 38 s, and its
reset screen withheld all 32 qubits, so it returned no device verdict. This successor keeps the envelope contract of
[measurement-sequence-adaptive-envelope.md](measurement-sequence-adaptive-envelope.md) (layout rule, width tiers,
20 us repetition delay with the 50 us fallback, one client-side Sampler job per attempt, aggregate cap, replan bound)
and changes the member constructor, the reset screen, the settle verdict and the null.

## What the carryover does to the departure

`scripts/msq_carryover_sensitivity.py` plants an extra initial excitation delta through the analysis's own device
model and reports the signed departure shift per unit delta, per qubit and per member class, on the eight fixture
qubits and on the retained run's 30 informative qubits at that run's contexts and counts
([carryover-sensitivity.json](../evidence/measurement_sequence/carryover-sensitivity.json)):

| Excitation on | fixture: median (range) | run contexts: median (range) |
|---|---|---|
| every member | 0.000 (0.000 to 0.000) | +0.024 (-0.029 to +0.083) |
| measure arm, N = 16 | -0.744 (-0.760 to -0.720) | -0.719 (-0.753 to -0.644) |
| ro0 | +0.868 (+0.844 to +0.882) | +0.840 (+0.800 to +0.887) |
| t1 delay 0 (the ro1 bracket) | -0.815 (-1.111 to -0.525) | -0.681 (-1.234 to -0.279) |
| t1 delays 1, 2, 3 | +0.16 to +0.37 | +0.12 to +0.32 |
| t1 delay 4 | -0.211 (-0.301 to -0.124) | -0.175 (-0.339 to -0.046) |
| delay, unitary and settle arms | 0 | 0 |

The service fixes no circuit order within a job (docs/notes/ibm_quantum/repetition-rate-execution.md), so each member
class inherits the excitation its unknown predecessor leaves, anywhere in [eps0, eps0 + D] with D the difference
between the excitation an |1> end state and an |0> end state leave at the next shot's start. The departure bias is then
bounded by D times the allocation coefficient max(sum of positive coefficients, |sum of negative ones|): 1.37 to 2.17
on the fixture, median 1.59 and maximum 2.31 on the run's contexts. Every qubit's member at row r sits in the same
fused PUB, so the allocation, and with it the sign of the bias, is shared by every qubit. With D at the run's in-job
reset residual (median 0.0123), the bound at the median, 0.020, matches the run's departure offset (+0.0187 median,
positive on 32 of 32 qubits). Carryover is therefore a live explanation of that offset, and the successor tests it.

An excitation common to every member divides out exactly on the fixture and to 0.024 per unit (median) on the run's
contexts, where the in-job T1 fit is misspecified (below). Equalizing the end state therefore reduces the bias
coefficient by a factor of about 25 to 70.

## Equalized end state

Every member, the reset controls and the pattern members included, ends with `sx; measure into coin; reset` after
its final measurement, in place of the bare terminal reset. The final measurement leaves a diagonal state; `sx` maps
both |0> and |1> to the equator, so the coin reads 1 with probability 1/2 whatever the member left, and every member
hands the next shot the same end-state distribution. The coin is its own one-bit classical register. The analysis
marginalizes it out before every existing summary, so each member's ideal law over its own registers and every
existing endpoint stay as they are; the coin's joint law with the final bit is the equalization check.

The equalization is imperfect by the coin's memory of the end state, c_q = P(coin 1 | final 1) - P(coin 1 | final 0)
pooled over the qubit's members and divided by the readout contrast 1 - e01 - e10. An sx over-rotation by delta gives
c = sin(delta); the calibrated sx error of 2.6e-4 (median, Kingston snapshot of docs/evidence/heron_platform) bounds a
purely coherent delta at sqrt(6 * 2.6e-4) = 0.039. Each qubit's c_q is measured in-shot over about 720,000 shots, a
standard error near 0.0012.

## Carryover screen

A qubit stays usable when the upper confidence bound of its departure bias,
`B_q = A_q * D_q * |c_q| + A0_q * D_q / 2`, lies below the margin `0.25 * 0.0188 = 0.0047`, fixed before the run:

- A_q: the qubit's allocation coefficient, computed by the sensitivity probe at the run's own execution contexts
  and counts when the analysis runs (the probe's run section is the procedure; the table above is its sizing).
- A0_q: the qubit's every-member coefficient from the same computation, which carries the residual common shift;
  the coin raises the common level by at most D/2 over an |0>-end baseline.
- D_q: the readout-corrected difference of the in-job reset controls rc1 and rc0 (`x; measure; reset; idle;
  measure` against the same without x). It reads the excitation one measure-and-flip reset leaves immediately; the
  repetition delay and `init_qubits` that follow can only relax it further, so it bounds D from above. Its run values:
  median 0.0123, range 0.0049 to 0.0366.
- |c_q|: two-sided, the coin's memory above.

Confidence bounds on D_q and |c_q| are Bonferroni over the W qubits at family alpha 0.05. Both come from the same job
as the endpoint they gate, so inter-job drift (the 2026-10-18 history-control pair, 18 minutes apart, shows 31 of 148
qubits moving by up to 0.032 between jobs) does not enter. With the run's reset-control counts (8192 shots each, an
upper bound about 0.005 above D) and a coherent c of 0.039 plus three standard errors, B at the run's median A, A0 and
D is 0.0014, under a third of the margin; a qubit carrying the run's worst A (2.31), A0 (0.083) and D (0.0366) at once
reaches about 0.006 and is withheld. The margin is a quarter of the bound floor; the null below checks it against the
false-fire bound.

Assumptions the screen does not cover, each stated in the case with its size: leakage to |2> (a measure-and-flip reset
does not return it, and the measure arm's sixteen mid-circuit measurements may leak more than other members);
a heating or TLS effect of measurement-heavy members on the next shot beyond the qubit's population; and the first
shot of each executor chunk, whose predecessor is a shot of another job.

## In-job T1 fit and the departure offset

The run's in-job T1 fit is misspecified: its shape parameter q lies below 1 on 29 of 30 informative qubits, p_init
reads negative (q50: p_init -1.17, q 0.30, T1 127 us against a calibrated 299 us), and the corrected series is nearer
linear than exponential. The departure is positive on all 32 qubits, median +0.0187. Neither is a device verdict; the
successor reports both per qubit and pooled, and preregisters one descriptive comparison: if the median departure over
the kept qubits falls below half the run's median on the same qubits, the offset is consistent with carryover; if it
stays at or above, carryover is refuted as its source and the offset belongs to the model.

## Settle verdict becomes descriptive

The run's settle test read `reduced_by_gap` on 16 qubits, pooled z 18.7, with no measure-arm deficit for a gap to
reduce. `chain_matrix` zeroes the transverse state at every pinch, so the settle gap's extra idles act through T1
alone: halving T2 in the model moves the settle gap by exactly zero. The model has no parameter that produces the
excess, so a settle verdict could not attribute it. The successor reports the settle gap per qubit and pooled,
labeled descriptive, and no device verdict reads it. The departure and mutation decisions stay preregistered.

## Fewer than 8 kept qubits

`msq_envelope_analysis.collected` reports the per-qubit pinching analysis over the kept qubits whenever any qubit is
kept, and withholds only the device verdict below 8, as the original design stated.

## Null calibration

The null of `msq_envelope_null.py` is rebuilt as the batched estimator of issue #579 (numpy across replicates with a
scalar bit-identity gate) before it runs at the successor's width. Its replicates plant what the run shows, each
coherent across qubits: the sx-error residual; each qubit's measured departure offset from the run; the run's t1
series shape (the corrected series per qubit, in place of the model's exponential); and the carryover bias at the
screen margin with the shared sign of the fused allocation. The family-wise false-fire bound must stay below 0.01 on
the departure and count-rule verdicts. A null that fires above it with the run's offset planted withholds the departure
verdict from the case, and the case reports why.

## Cost and approval scope

The coin adds one sx (32 ns) and one measure (2.18 us) per member shot: 1.6 s of circuit time over the run's 720,896
shots, priced by the planner with the measured 9 us per-shot residual at dry run, so about 40 s at width 32 against
the 147 s cap. An attempt stays one job; the fallback signature, `envelope_drift`, the replan bound and attempt
accounting stand as ratified. The change is a new constructor inside the `msq-envelope-v1` contract, which binds the
constructor by digest, so the case binds the new one and needs no doctrine change.

## Sequence

1. Reviews of this design: the adversarial review skill and the advisor (done on v1, dispositions below), Codex
   gpt-daybreak-blue in tmux on v2.
2. Issue #579: the batched null with its gate.
3. Implementation: the coin ending and its register, the marginalization, c_q and D_q, the screen, the descriptive
   settle and offset comparison, the per-qubit report; tests and lanes.
4. A sizing replay of the screen and every verdict over the retained run's counts (c_q set to the coherent bound,
   since that run has no coin), then the null at the chosen width.
5. Dry run on the live calibration, the written case, approval, run.

Falsifiers: an every-member coefficient above 0.1 per unit at the planned contexts; a coin memory |c_q| above 0.05 on
a kept qubit; a screen input taken from another job; a margin derived from run counts; a settle reading that enters a
device verdict; a null that omits the run's offset or t1 shape.

## Review dispositions of v1

- Single-class coefficient 1.111 understated the bias (adversarial review): adopted; the allocation coefficient and
  every class enter, at the run's contexts.
- Two control jobs measure drift above the margin, and a one-sided bound passes it: adopted by removing the control
  jobs; every screen input comes from the family job, and the coin memory bound is two-sided.
- The null planted a T2 shortfall that cannot move the settle gap: adopted; the null plants the run's offset and t1
  shape.
- The corrected screen could repeat the predecessor's unattainability: answered by the coin, which divides the
  coefficient by 25 to 70; the worst run qubit reaches B 0.0037 under 0.0047.
- A three-job attempt changes the ratified contract: moot; an attempt stays one job.
- Chunk boundaries, collective end state, leakage: listed as assumptions above; no screen conditions on shot order.
- Advisor: the coin needs the every-member row checked at the run's contexts before adoption (done: median 0.024 per
  unit), a separate coin register, and stated residual and cost numbers (above).
