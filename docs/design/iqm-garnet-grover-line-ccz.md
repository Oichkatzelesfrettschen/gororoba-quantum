# IQM Garnet Grover search with a line-native CCZ

The case measures whether three-qubit Grover search compiled with a
seven-CZ line-native CCZ keeps more of its marked-state probability on a
Garnet path than a generic compile of the same search, and whether a
second iteration still raises the marked probability once its doubled CZ
count meets the hardware's errors. Ideal Grover search over eight items
peaks at two iterations: P(marked) = sin^2((2k + 1) asin(1/sqrt 8)) gives
0.125, 0.781, 0.945 and 0.330 for k = 0 to 3 (Grover, Phys. Rev. Lett. 79,
325, 1997).

## Mechanism

Garnet's couplers form a square lattice with no triangle, so CCZ runs on a
path a-b-c whose end qubits share no coupler. CCZ is the phase polynomial

    pi x0 x1 x2 = (pi/4)(x0 + x1 + x2 - x0^x1 - x0^x2 - x1^x2 + x0^x1^x2),

so a CNOT network on the path's two couplers that brings each of the seven
parities onto some wire implements it with one diag(1, exp(+-i pi/4)) per
parity. `line_networks()` in `scripts/iqm_grover_line.py` searches every
reachable pair (linear map of GF(2)^3, set of parities already carried)
breadth first over the four nearest-neighbor CNOTs:

| network end | CNOTs |
|---|---|
| every wire holds its input | 8 |
| any wire permutation | 7 (the middle wire exchanges with one end) |

Grover's layers between two CCZs act qubit by qubit, so the compiler
tracks the exchange as a relabeling of logical qubits onto path positions
and measures each logical qubit where it ends. A CNOT is a CZ between
Hadamards on its target. Every Z rotation travels as a frame into the
phase of the qubit's next `prx`, since CZ commutes with it, and the frame
left before measurement is dropped. A k-iteration search costs 14k CZ.
The generic arm is qiskit's optimization level 3 on the same path with
transpiler seed 53987 (index 3 of the ANU draw of 2026-11-16): 18 CZ and
68 `prx` for one iteration under qiskit 2.6.2, the release
`requirements.txt` pins. The count follows the seed and the qiskit
release (qiskit 2.1.2 compiles the same circuit with the same seed to 25
CZ), so the build runs under the pinned requirements and the arm stands
for one seeded compile of that release.

The self-test multiplies out every compiled circuit: for both networks,
marked strings 000, 101, 011, 110, 111 and zero to three iterations, the
native unitary equals the logical one times the tracked permutation up to
a final diagonal (largest off-diagonal residual 4e-11, from angles rounded
to 10 digits), and each marked probability equals the sin^2 law.

Six CNOTs are necessary for TOFFOLI, and so for CCZ, on any connectivity
(Shende and Markov, Quantum Inf. Comput. 9, 2009; arXiv:0803.2316). Seven
is the minimum on a line within CNOT-plus-phase circuits only.
Hypothesis: no six-CZ line construction exists with general single-qubit
gates between the CZs; a search over that wider family is its falsifier.

## Why it needs the service

The prediction models depolarizing `prx` and CZ errors from randomized
benchmarking, idle T1 and T2 over the as-soon-as-possible schedule that
Garnet circuit jobs run (`docs/notes/iqm/README.md`, "Schedule"), with each
qubit idle from its last gate to the joint measure, and the readout
assignment conditioned on the all-zeros herald that the kept shots pass. Coherent over-rotation, leakage, crosstalk between the path
and its spectators, and calibration drift are outside it, and they decide
how a 28-CZ circuit compares with a 14-CZ one on the chip. The comparison
of compile strategies is therefore a hardware question.

## Pre-flight

- Hypothesis: the 14-CZ line-native compile keeps more marked probability
  than the 18-CZ generic compile, and a second iteration (28 CZ) still
  raises it on QB20-QB16-QB17.
- Quantity: the heralded frequency of the marked string per arm, with bit q
  read from the q-th qubit of the measurement locus, pooled over an arm's
  copies.
- Falsifier: a resolved negative line-minus-generic difference, or a
  resolved negative k2-minus-k1 difference.
- Prediction and budget: model differences +0.034 (line against generic),
  +0.072 (101) and +0.072 (011); 20 circuits x 4000 shots, of which
  heralding kept 85 % on the last Garnet run (about 3400 per circuit, 13600
  per line-against-generic arm over its four copies); ceiling 2.50 credits.
- Next step by result: a resolved line-native gain makes the
  phase-polynomial line synthesis the CCZ compile for Garnet cases and
  carries it to the degree-three sedenion sign oracle; no gain sends the
  next case to coherent-error compensation of the seven-CZ network. A
  resolved second-iteration gain sets the three-qubit depth budget at 28 CZ
  or more; a loss measures the per-CZ error the model omits.

Retained measurements of the same shape put Garnet's measured contrast
below this model: visibility 0.36 against 0.48 in the
[kernel cancellation probe](iqm-garnet-kernel-cancellation-probe.md) and an
odd part of 0.198 against 0.266 of its law through a 199-CZ compile in the
[signed kernel probe](iqm-garnet-signed-kernel-probe.md), both about 0.75
of the model. Scaling each arm's excess over 1/8 by that shortfall:

| shortfall | line - generic | z | P(resolve) | k2 - k1 (101) | z | P(resolve) | k2 - k1 (011) | z | P(resolve) |
|---|---|---|---|---|---|---|---|---|---|
| none (model) | +0.034 | 6.0 | 1.00 | +0.072 | 8.6 | 1.00 | +0.072 | 6.8 | 1.00 |
| 0.75 on every arm | +0.025 | 4.2 | 0.89 | +0.054 | 5.7 | 1.00 | +0.054 | 4.5 | 0.94 |
| 0.745 per 199 CZ (0.99852 per CZ) | +0.036 | 6.3 | 1.00 | +0.058 | 6.7 | 1.00 | +0.058 | 5.3 | 0.99 |

P(resolve) is the probability that the measured z exceeds 3 when the true
difference is the row's value, at 3400 kept shots per circuit, every arm
pooled over its copies: four copies each for `m101-k1` and the generic
arm, one for `m101-k2`, `m011-k1` and `m011-k2`. Six copies would lift
the line-against-generic resolution under the flat shortfall to 0.97 and
the ceiling to 3.00 credits, above the approved 2.50.

The four copy pairs run in ABBA order (line first, generic first, generic
first, line first), so the summed circuit positions of the two arms are
equal and a drift linear in position within the job cancels from their
pooled difference.

The prediction carries one stated uncertainty in its idle term: the
retained idle-schedule case measured relaxation faster than the calibrated
T1 over an ASAP schedule (apparent T1 a median 0.53 of calibrated, with an
unsettled per-layer duration), so qubits that wait longest before the joint
measure may lose more than predicted.

## Case

`"$PYTHON" scripts/iqm_grover_line.py build results/iqm/cases/grover-line-ccz
--calibration SRC` writes the case from the calibration snapshot of
2026-11-20 (calibration set `03975719-b1c2-4805-a212-877a026e1724`), copied
into the case; `check` rebuilds it byte for byte. The builder scores all
136 oriented calibrated paths by the mean predicted marked probability of
the four line-native arms. QB20-QB16-QB17 (QB16 in the middle) scores
0.729; the next three score 0.724, 0.723 and 0.723. Predictions are exact
density-matrix probabilities rounded to 9 digits; the builder refuses a
simulated circuit that keeps a measure or reset before the joint final
measure, since a mid-circuit measure turns the density-matrix
probabilities into a sampled average.

One job `grover`: 20 circuits x 4000 shots, active reset
(`active_reset_cycles` 1) with all-zeros heralding, pinned to the
calibration set above on Garnet. Bit q of a marked string is logical
qubit q, and the measurement locus lists the logical qubits in order.
The job runs, in order: `m101-k1`, `m101-k1-generic`, `k0`, `m101-k2`,
`m011-k1`, `m011-k2`, `m101-k1-generic-c1`, `m101-k1-c1`, `ro-000` to
`ro-011`, `m101-k1-generic-c2`, `m101-k1-c2`, `ro-100` to `ro-111`,
`m101-k1-c3` and `m101-k1-generic-c3`. The line-native arms and the
readout preparations measure QB20, QB16, QB17; the generic compile routes
its logical qubits to QB16, QB17, QB20 and measures them in that order.

| circuit | CZ | prx | ideal P(marked) | predicted P(marked) |
|---|---|---|---|---|
| `k0` | 0 | 3 | 0.125 each | 0.120 to 0.130 |
| `m101-k1` (4 copies) | 14 | 22 | 0.781 | 0.689 |
| `m101-k1-generic` (4 copies) | 18 | 68 | 0.781 | 0.655 |
| `m101-k2` | 28 | 42 | 0.945 | 0.761 |
| `m011-k1` | 14 | 22 | 0.781 | 0.696 |
| `m011-k2` | 28 | 42 | 0.945 | 0.768 |
| `ro-000` to `ro-111` | 0 | 0 to 3 | 1 | readout assignment |

The marked string 011 is not a palindrome, so a reversed bit order would
show as a peak at 110; 101 alone could not reveal it.

## Seconds and credits

The builder sizes the job at 37.5 us per active-reset shot, the time the
reset and billing pilot measured on Garnet (`ACTIVE_SHOT_SECONDS` in
`scripts/iqm_signed_probe.py`), and `iqm_jobs.py submit` adds the 1.6 s
fixed job cost before rounding up: 80000 shots give 3.00 s and a ceiling of
ceil(4.6) x 0.50 = 2.50 credits on Garnet, 0.00 on `garnet:mock`.
(`iqm_jobs.py` holds its own 8.7 us per shot, which fits only the mock's
estimates.) The kernel cancellation probe ran 108000
heralded shots in a 2.23 s runtime, so the likely bill is 2 s to 3 s, 1.00
to 1.50 credits. `collect` cancels a job whose runtime nears the ceiling.

The pinned calibration set lasts until Garnet's next daily calibration
(the queue-availability gap near 01:15 UTC). After it, the QPU refuses
the pinned set, and the case is rebuilt from a new snapshot, which
changes `cases.json` and its digest and needs a new approval.

## Preregistered decisions

A difference resolves when it lies 3 binomial standard errors from zero.
Each arm pools all its copies: its frequency is the marked count over its
summed heralded kept shots, and its standard error is binomial in that sum.
The decisions read raw frequencies. Readout-corrected values are reported
beside them: the 8 x 8 assignment matrix from the `ro` circuits, read in
their measurement order QB20, QB16, QB17, is permuted into each circuit's
own measurement order (QB16, QB17, QB20 for the generic copies) before it
is inverted.

- Line-native against generic: P(m101-k1) - P(m101-k1-generic), predicted
  +0.034, four ABBA copies of each arm. A resolved negative difference
  falsifies the claim that the 14-CZ compile preserves more marked
  probability than the 18-CZ one.
- Second iteration, for each marked string: P(k2) - P(k1), predicted
  +0.072 (101) and +0.072 (011). A resolved negative difference is a
  finding: the hardware loses more per added CZ than the model carries.
- Bit order: the most frequent outcome of `m011-k1` and `m011-k2` is 011.
- Each Grover arm's measured value is reported against its prediction; the
  gap estimates the error budget the model omits.

## Result

Garnet job `01a1fb31-c2c2-72fc-a9b2-b7b028c37bc0` ran the 20-circuit case
on 2026-11-20 against the pinned calibration set: 1.27 s runtime, 2 billed
seconds, 1.00 credit. Heralding kept 3329 to 3746 shots per circuit (86 %).
The readout preparations read back their state with probability 0.964 to
0.986. Measured, raw frequencies, copies pooled
(`results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover`):

| arm | kept shots | P(marked) | predicted | measured excess / predicted excess |
|---|---|---|---|---|
| `m101-k1` (4 copies) | 13688 | 0.6747 | 0.6894 | 0.97 |
| `m101-k1-generic` (4 copies) | 13924 | 0.6048 | 0.6554 | 0.90 |
| `m101-k2` | 3485 | 0.7188 | 0.7612 | 0.93 |
| `m011-k1` | 3412 | 0.6530 | 0.6960 | 0.92 |
| `m011-k2` | 3449 | 0.6964 | 0.7684 | 0.89 |

| decision | measured | standard error | z | predicted |
|---|---|---|---|---|
| line - generic | +0.0699 | 0.0058 | 12.1 | +0.034 |
| k2 - k1 (101) | +0.0441 | 0.0086 | 5.1 | +0.072 |
| k2 - k1 (011) | +0.0434 | 0.0113 | 3.8 | +0.072 |

Every preregistered decision resolves in the predicted direction, and the
most frequent outcome of `m011-k1` and `m011-k2` is 011. The four copies
of each decision arm agree within 0.023 (line 0.672 to 0.680, generic
0.598 to 0.620). The line-native gain is twice the model's: the generic
compile keeps 0.90 of its predicted excess against 0.97 for the line-native
one, so its extra 4 CZ and 46 `prx` cost more than the depolarizing model
carries (hypothesis: coherent single-qubit error accumulating over the
68-`prx` sequence; falsifier: a generic compile re-synthesized to 22 `prx`
at 18 CZ keeping the same 0.90 ratio). The second iteration gains less than
predicted, 0.044 against 0.072, which measures the per-CZ loss the model
omits at 28 CZ. Garnet's contrast reached 0.89 to 0.97 of the model here,
above the 0.75 of the retained 199-CZ probes.

## Analysis

`"$PYTHON" scripts/iqm_grover_line.py analyze RUN --out results/iqm/grover_line_ccz_analysis.json`
(gate core-774 replays it) passes the run, validated by
`gororoba_quantum/iqm_records.py`, and the prediction's herald-conditioned
readout errors to `gororoba_quantum/grover_line_analysis.py`, which reads
every arm three ways from the retained counts.

**Readout correction.** Each circuit's distribution is corrected by the
assignment matrix of the eight `ro` circuits, permuted into that
circuit's measurement order, with delta-method standard errors over both
the circuit's and the `ro` circuits' counts. Correction moves every marked
probability up by 0.016 to 0.018 and leaves the decisions unchanged: line
minus generic +0.0706 (standard error 0.0065), second iteration +0.0453
(101) and +0.0446 (011).

**Walsh spectrum.** The ideal Grover output is a peak on the marked string
over a uniform floor, so each of its seven parity correlators <Z_S>,
S in F_2^3 \ {0}, equals chi_S(marked) (8 P_k - 1) / 7: one magnitude with
the marked string's character as its sign. These seven characters are the
seven parities of the CCZ phase polynomial. The ratio r_S of a correlator
to its ideal value separates two noise shapes: global depolarizing noise
scales every r_S alike, and independent bit flips with retention f damp a
weight-w parity as f^w. The table sets the readout-corrected spectrum
against the model's spectrum before its readout channel (the raw spectrum
against the model with readout is in the analysis record); mean r_S by
weight 1, 2, 3:

| arm | measured, corrected | model before readout | measured / model |
|---|---|---|---|
| `m101-k1` | 0.878, 0.850, 0.862 | 0.900, 0.890, 0.882 | 0.98, 0.96, 0.98 |
| `m011-k1` | 0.845, 0.814, 0.835 | 0.900, 0.889, 0.881 | 0.94, 0.92, 0.95 |
| `m101-k1-generic` | 0.781, 0.742, 0.723 | 0.855, 0.833, 0.824 | 0.91, 0.89, 0.88 |
| `m101-k2` | 0.759, 0.739, 0.730 | 0.815, 0.800, 0.791 | 0.93, 0.92, 0.92 |
| `m011-k2` | 0.752, 0.699, 0.676 | 0.814, 0.800, 0.790 | 0.92, 0.87, 0.86 |

The model's own spectrum is nearly flat in weight, and so is the measured
one of both one-iteration line-native arms: independent flips at the
measured weight-1 ratio would put the weight-3 ratio of `m101-k1` near its
cube, 0.68, against 0.862 measured. The error the circuits carry reaches
the output close to globally depolarized. The deeper arms (the 18-CZ,
68-`prx` generic compile and the 28-CZ second iterations) lose 1 to 6
points more at weight 3 than at weight 1 relative to the model, a small
local component that grows with depth. The Hamming profile says the same
in the outcome basis: the corrected unmarked mass sits 0.457, 0.426, 0.117
at distance 1, 2, 3 from the marked string in `m101-k1`, against 3/7,
3/7, 1/7 for uniform error. Grover's diffuser mixes a mid-circuit fault
over all eight strings before measurement, so one number per circuit, its
retention, carries most of its noise.

**Retention.** The corrected retention lambda_k = (P_k - 1/8) / (P_k^ideal
- 1/8) is 0.864 and 0.746 at one and two iterations for 101 (0.830 and
0.718 for 011). The second iteration multiplies the first by 0.864 (101)
and 0.866 (011): retention is multiplicative per 14-CZ iteration, with no
extra preparation or measurement cost left after readout correction, and the
same for both marked strings, as the oracle's X conjugation predicts. The
generic iteration retains 0.756, 0.875 of the line-native one. Writing
-ln lambda = a n_CZ + b n_prx over the two one-iteration compiles gives
a = 0.0069 per CZ and b = 0.0023 per `prx` including their idle time
(computed from two equations, so a fit with no residual; hypothesis: the
`prx` term exceeds randomized benchmarking's about 0.001 through coherent
error, and the falsifier is a generic compile resynthesized to 22 `prx` at
18 CZ that keeps 0.756).

**Stability.** The four ABBA copies of the line arm agree (chi-squared 0.67
on 3 degrees of freedom, slope +0.0002 per circuit position); the generic
copies scatter more (chi-squared 5.0, p about 0.17, from copy c2 at 0.620).
The uniform reference `k0` reads Pearson's chi-squared 11.5 on 7 degrees
of freedom against 1/8 each (p about 0.12).

**Consequence for the Cayley-Dickson oracles.** For the algebra of
dimension 2^n, the sign cd_sign(2^n, m, q) as a phase on the n qubits of q
has algebraic degree n - 1 for every m other than 0 (computed with
`boolean_anf.anf_degree` through dimension 32: 2 for octonions, 3 for
sedenions, 4 for pathions), and the associator phases of
`predict.associator_phase` reach degree 3 first at dimension 32 (360 of
465 pairs). Each doubling adds one control to the largest phase gate an
oracle needs: CZ for the octonions, CCZ for the sedenion sign oracle, CCCZ
for the pathions. On Garnet's triangle-free lattice the cubic rung costs 7
CZ per monomial on a line, and this run calibrates it: about 0.99 retained
per line-native CZ with its single-qubit gates, so a sedenion sign oracle
keeps half its contrast at roughly 66 CZ. Because the output noise is close
to global, a measured Walsh spectrum keeps its shape and loses one scalar,
which is the assumption behind reading spectral classes from samples
through the collision probability (`scripts/associator_walsh_classes.py`)
and the depolarizing-shape test of the Tuna-17 Walsh exemplars
(`scripts/qi_walsh_exemplar_analysis.py`); this run measures that
assumption on Garnet at depths up to 28 CZ.

## Commands

```sh
export PYTHON="${PYTHON:-python3}" IQM_TOKENS_FILE=TOKENS.json
CASE=results/iqm/cases/grover-line-ccz
HEX=$(sha256sum "$CASE/cases.json" | cut -d' ' -f1)
"$PYTHON" scripts/iqm_jobs.py submit "$CASE" grover --qc garnet:mock \
  --approval "QUOTE" --approved-cases-sha256 "$HEX" --max-credits 0.0 --dry
"$PYTHON" scripts/iqm_jobs.py submit "$CASE" grover --qc garnet:mock \
  --approval "QUOTE" --approved-cases-sha256 "$HEX" --max-credits 0.0
"$PYTHON" scripts/iqm_jobs.py submit "$CASE" grover --qc garnet \
  --approval "QUOTE" --approved-cases-sha256 "$HEX" --max-credits 2.5
"$PYTHON" scripts/iqm_jobs.py collect results/iqm/runs/STAMP-garnet-grover-line-ccz-grover
```

The mock job proves the request format and returns the compiler's runtime
estimate at no cost; its random bits enter no analysis.

## Residual risk

- The model omits coherent error, leakage and crosstalk, so the predicted
  differences are upper estimates of the measurable ones.
- Heralding discards shots whose pre-circuit readout is not all zeros; the
  kept count, not 4000, sets each standard error.
- The generic arm is one seeded compile of the pinned qiskit release, not
  IQM's client-side transpiler and not the best of qiskit's seeds.
- The idle term of the prediction rests on calibrated T1 and T2 over an
  ASAP schedule, which the idle-schedule case found optimistic; the
  measured gap of each arm is reported against it.
