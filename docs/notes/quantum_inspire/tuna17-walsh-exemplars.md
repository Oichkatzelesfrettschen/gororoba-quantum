# Tuna-17 Walsh exemplars: the two cubic classes and the q13 readout context

`scripts/qi_walsh_exemplar_cases.py` writes the series
`results/quantum_inspire/cases/walsh_exemplar_tuna_17/` and its QX twins;
`scripts/qi_walsh_exemplar_analysis.py` holds the preregistered analysis.
Gates core-428 (case regeneration) and core-432 (qxelarator conformance,
`requires: qi`) hold the cases; the generator and analysis self-tests run in
the behavioral suite (`tests/test_cli_self_tests.py`).

## What the circuits measure

The associator phase omega_{i,j} of a dimension-32 pair is a cubic Boolean
function for every pair with j at least 16, and the census
(`scripts/associator_walsh_classes.py`) splits the cubic pairs into two
spectral classes: |W| multiset {0: 24, 8: 7, 24: 1} with K = 11/32 (234
pairs) and {0: 22, 8: 8, 16: 2} with K = 5/32 (126 pairs). The exemplars are
(1,16), whose phase is OR(x1, x2, x3), and (9,18), affine-equivalent to
a b c + b d. Design C samples the Walsh distribution P(y) = W(y)^2 / 1024
through H^5, the diagonal phase and H^5.

Under |+>^n input every linear change of variables before the diagonal is
free and every linear network after it relabels the measured string, so a
phase h with omega(x) = (-1)^h(Ax + b) up to affine terms gives
P_omega(y) = P_h(z) at y = M z + u. Each class therefore runs as a four-qubit
phase circuit; the generator records the first injective affine map
(`census_map`) that carries the block distribution onto the census spectrum
outcome by outcome, and the analysis reads z.

These circuits measure how Tuna-17 moves two spectra that differ by one
quadratic term on a fixed CCZ phase polynomial. They do not compose the
three sedenion multiplication blocks; the factorized Design C circuits that
do cost 94 and 99 routed CZ on Kingston
([design_c_cubic_noise](../../evidence/design_c_cubic_noise/README.md)) and
stay an IBM question.

## Circuits

`path_search` enumerates, breadth first by two-qubit gate count, every
circuit of CNOT and CZ gates on a four-qubit path with diagonal phases
k pi/4 on the parities the CNOT network visits and a free final linear map.
A phase polynomial sum_p c_p (pi/4) [p.x] is a Boolean phase pi h(x) exactly
when, in the expansion [p.x] = sum over nonempty T in p of (-2)^(|T|-1) x_T,
the sums of c_p over p containing T vanish mod 4 for |T| = 1, are even for
|T| = 2 (their halves give the quadratic part of h) and give the cubic part
mod 2 for |T| = 3; only c_p mod 4 matters. The minimum is 5 two-qubit gates
for the high class and 6 for the low class, with or without CZ moves; no
circuit of that gate set reaches either class with fewer. The high circuit
uses three positions and leaves the fourth idle in |0>.

CNOT is written H CZ H, two H on one qubit with no gate between them cancel,
and the phases are T, S and Tdag, on the pi/36 grid and native on Tuna-17.
Every text is checked against the exact state vector of its own gate list,
both blocks against the census spectrum through the recorded map, and
OpenSquirrel's decomposition passes keep each gate sequence
(`docs/evidence/quantum_inspire/toolchain_check.json`). qxelarator returns
no shot outside either support and every outcome within |z| < 4.5 of its
exact probability at 8192 shots
(`results/quantum_inspire/walsh_exemplar_qx_conformance.json`).

## Layout

With q0, q5, q6, q7 and q9 excluded and q15 avoided
([tuna-17.md](tuna-17.md)), the usable graph holds 18 four-qubit paths and
exactly four vertex-disjoint pairs of them, each joined by at least two
couplers: X = (1|2, 4, 8, 12) with Y = (10, 13, 11, 14) or
(13, 11, 14, 16). No buffered pair exists, so the series carries the static
ZZ of the parked couplers 8-11 and 12-14 ([experiments.md](experiments.md)).
The series uses X = (1, 4, 8, 12) and Y = (10, 13, 11, 14): both usable
neighbors of q13 then lie in block Y, so the readout model conditions q13 on
block variables. walsh-c1 runs the high class on X and the low class on Y,
walsh-c2 swaps them, and class and block separate inside one calibration.

## Readout context

The ladder established a context-dependent |1> misassignment on q13: e10
0.088 with all 17 qubits excited, 0.042 with every coupled neighbor in |0>
([tuna-17-run-design.md](tuna-17-run-design.md), ladder results). In a
Walsh circuit q10 and q11 vary shot by shot, so a bracket value biases every
Y-block distribution. Four context readouts measure q13 after its X:

| circuit | q10, q11 | separates |
|---|---|---|
| readout-q13 | idle, \|0> | isolated reference |
| readout-q13-xx | X X each, \|0> | drive crosstalk that grows with pulse count, at fixed state |
| readout-q13-q10 | X on q10 | state of q10 |
| readout-q13-q11 | X on q11 | state of q11 |

The analysis builds the Y-block response from q13's e10 chosen by the true
state of (q10, q11), with readout-1 for (1, 1), and reports the bracket and
isolated corrections beside it. In the self-test a state-dependent truth
leaves the bracket and isolated corrections biased and their depolarizing
shape test rejected, so a shape rejection on hardware is read against the
readout variant that produced it.

## Series

| batch | circuits |
|---|---|
| batch-00 | readout-0, readout-1, readout-q13 |
| batch-01 | walsh-c1, walsh-c2, readout-q13-xx |
| batch-02 | walsh-c1, walsh-c2, readout-q13-q10 |
| batch-03 | readout-0, readout-1, readout-q13-q11 |

131072 shots per job. The fitted Tuna-17 cost of 2.6 s per job plus 0.53 ms
per shot gives about 72 s per job, 12 jobs and about 870 s of execution;
with the 120 s pause after each batch and the queue, the series takes about
25 minutes. Each batch is three circuits, one batch queued at a time.

## Preregistered decisions

The manifest's `preregistered` block carries every rule and threshold:

- Class order: K_high > K_low on each block at z >= 3 in every batch,
  comparing the block's high-class job with its low-class job so the
  block's fidelity cancels; a reversal refutes the emitted circuits.
- Interaction: I = ln V(high, X) - ln V(high, Y) - ln V(low, X) +
  ln V(low, Y) with V = (K - 1/16) / (K_ideal - 1/16). A per-block
  multiplicative fidelity gives I = 0; |I| >= 3 SE establishes an error that
  depends on the class, such as a coherent phase error on the CCZ or the
  parked-coupler ZZ acting on the extra CZ.
- Shape: per job and block, the maximum-likelihood depolarizing fit through
  the readout response and its G test on 14 degrees of freedom;
  log10 p <= -3 rejects the depolarizing shape.
- Attribution of q13: drive, state, both or neither, each delta established
  at |delta| >= 0.02 and |z| >= 3. readout-q13 runs in batch-00 and the
  context readouts in later batches, so q13's bracket drift between
  batch-00 and batch-03 joins each delta's SE in quadrature.
- Reported without a decision: forbidden weight, replicate TVD against a
  0.03 batch-scatter allowance, and the global
  depolarizing prediction K_high 0.2595 and K_low 0.1236 at retention 0.965
  per CZ, which the ladder's rho above 1 already excludes as the whole
  channel.

Errors come from a parametric bootstrap of 2000 draws on seed 20261018 that
redraws every readout circuit's counts and, for each Walsh circuit, the
joint histogram of both blocks, so the draws keep the covariance of blocks
read in the same shots, and the class order takes the SE of the drawn
high-minus-low difference, whose two jobs share each response draw. The
response averages the batch-00 and batch-03 brackets around the Walsh
batches; each decision is also evaluated with one bracket in its place and
q13's context e10s moved by that bracket's q13 offset, the larger shift
joins the class-order and interaction SEs in quadrature, and a shape
rejection stands only under all three responses.

## Results, 2026-10-18

The QX twins read no shot outside either support. The Tuna-17 series ran
from 17:00Z to 17:31Z, every job completed and every stop rule passed
(`results/quantum_inspire/walsh_exemplar_tuna_17_analysis.json`, gate
core-557; claims `qi-tuna17-q13-readout-context-q11` and
`qi-tuna17-walsh-exemplar-classes`). Bracket drift stayed at or below
0.0037 on every block qubit.

- **q13 context.** q13's e10 reads 0.0456 alone, 0.0913 beside an excited
  q11 (+0.046, about 21 SE with q13's bracket drift in the SE), 0.0396
  beside an excited q10 and 0.0419 after
  X X on both neighbors; readout-1 reads 0.0898. The preregistered
  attribution is "state", and the state that matters is q11's. The drive
  control gives each neighbor two pulses and returns it to |0>, and q10's
  single pulse raises nothing, so the ladder's context effect follows q11
  ending in |1>; a transient of q11's single pulse that a second pulse
  cancels needs a control with one X on q11 and q11 returned to |0>.
- **Classes.** On each block and in both batches the high-class job's K
  exceeds the low-class job's at z 105 to 114.

  | class | block X | block Y | ideal |
  |---|---|---|---|
  | high | 0.2896, 0.2890 | 0.3050, 0.3054 | 0.34375 |
  | low | 0.1296, 0.1313 | 0.1251, 0.1252 | 0.15625 |

  Replicates agree within a TVD of 0.004 to 0.008.
- **Interaction.** I = -0.148 (SE 0.010), established: the high class does
  better on Y and the low class on X. The high circuit leaves its block's
  fourth qubit idle, so the low class alone uses q12 and q14 and the couplers
  q8-q12 and q11-q14; the two classes run on different hardware subsets, and
  the interaction does not isolate a class-specific coherent error.
- **Shape.** The depolarizing G test rejects every job and block. For the
  high class the rejection is uninformative: its forbidden outcomes measure
  the idle qubit alone (weight 0.003 on X, below 0.0002 on Y), against which
  a uniform-over-16 null is misspecified. Its K below ideal with no forbidden
  weight shows the noise moving weight among the eight allowed outcomes. The
  low-class rejection (log10 p -1066 and -1042 on X, -26 and -33 on Y with
  the context correction) holds under all three q13 corrections.

A follow-up that separates hardware subset from class runs both classes on
three-qubit paths, or gives the high class's fourth qubit an identity-
equivalent CZ pair, and states a shape null over the qubits a circuit
touches.
