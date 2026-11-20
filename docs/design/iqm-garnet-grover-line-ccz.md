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
