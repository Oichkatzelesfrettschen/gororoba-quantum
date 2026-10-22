# BDSC target effect on Tuna-17: four-qubit Pauli readout pilot

The binary-effect dark-subspace certificate's target effect E0 is the
three-term Pauli sum I/2 - YIXY/4 + YZXY/4 on four qubits
([bdsc-pauli-readout.md](../notes/topics/bdsc-pauli-readout.md), record
`docs/evidence/bdsc/pauli/pauli_form.json`). A transmon reads the whole
sixteen-dimensional effect in one local basis, so Tuna-17 can measure the
same target that the Belenos optical case measures, through a different
preparation, readout and noise model. This pilot measures the response of
Tuna-17 patches to a bank of states whose ideal scores are 0, 1/2 and 1,
and tests whether a contraction alone explains the deviations. It does not
certify the device and its result does not qualify the Belenos case.

## Encoding and readout

Logical qubits q3 q2 q1 q0 carry algebra index bits 3..0. Every state in the
bank holds q2 in a definite Z state, so q2 needs no coupler. Kernel and
bright states are GHZ-type on (q3, q1, q0): H on q3, CNOT q3 -> q1,
CNOT q1 -> q0, then X and Z corrections, so (q3, q1, q0) is a connected
three-qubit path with q1 in the middle. CNOT is H CZ H on the target; every
gate is Clifford and sits on Tuna's 5 degree angle grid.

The readout uses the native pulses of the cQASM v3 standard gate set
(`docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/`): X90
puts the Y eigenbasis of q3 and q0 on Z and mY90 does the same for the X
eigenbasis of q1; q2 is left in Z and all four are measured. Both matrices equal
their spec R_n forms, and U P U^dagger = Z holds for each; the outcome
probabilities equal those of the Sdag-then-H and H rotations of
`pauli_form.json`, so the score table carries over (checked for every bank state
in `ideal_scores()`). One pulse per qubit shortens the readout layer to one
cycle and removes the two-pulse H on q1 and q2 that drove simultaneously.
With signs z2, y3, x1, y0 and t = y3 x1 y0, the score is 1/2 for z2 = +1 and
(1 - t)/2 for z2 = -1; its mean is Tr(E0 rho) and z2 = -1, t = +1 is the kernel
outcome.

## State bank

| group | states | ideal score | role |
|---|---|---:|---|
| kernel | k1..k4 = (e7 + e12, e6 - e13, e5 + e14, e4 - e15)/sqrt2 | 0 | target nulls, `bdsc.kernel_frame()` |
| bright | (e7 - e12, e6 + e13, e5 - e14, e4 + e15)/sqrt2 | 1 | sign partners of the kernel |
| middle | e0, e10 | 1/2 | z2 = +1: the score is 1/2 whatever q3, q1, q0 read |
| sector | e7, e12 | 1/2 | z2 = -1 basis states: t is a fair coin ideally |

The layout of the twelve states over the patches follows.

## Witness layout

Let H be the middle or sector slot. The six assignments of (kernel, bright, H)
to the three patches form three swap pairs that differ by exchanging kernel and
bright. A batch holds one swap pair on patches a and b with H on the third
patch m: circuit 1 puts k_na on a, b_nb on b and an H state on m; circuit 2
puts b_na on a, k_nb on b and the other H state. `WITNESS_PLAN` uses each swap
pair twice (six witness batches, twelve circuits, 36 state-patch cells):

| batch | m | (n_a, n_b) | circuit 1 (patch 0, 1, 2) | circuit 2 |
|---|---:|---|---|---|
| 01 | 2 | (1, 3) | k1 b3 e0 | b1 k3 e7 |
| 02 | 1 | (3, 1) | k3 e0 b1 | b3 e7 k1 |
| 03 | 0 | (1, 3) | e0 k1 b3 | e7 b1 k3 |
| 05 | 2 | (2, 4) | k2 b4 e12 | b2 k4 e10 |
| 06 | 1 | (4, 2) | k4 e12 b2 | b4 e10 k2 |
| 07 | 0 | (2, 4) | e12 k2 b4 | e10 b2 k4 |

Balance properties, counted by `balance_tables()` (which raises on any unequal
count and writes the counts to `cases.json`):

- every one of the 12 states meets every patch exactly once;
- each group meets each patch equally (kernel and bright 4 cells, middle and
  sector 2 cells per patch);
- each group meets each patch and each ordered pair of neighbor groups equally:
  a kernel or bright state sits twice in every (patch, partner-first or
  half-first) context and a middle or sector state once in every (patch,
  kernel-first or bright-first) context, so the neighbor activity (kernel and
  bright patches entangle, middle and sector patches hold basis states) is
  crossed with the group and the patch;
- each of the six assignments occurs in two circuits, with middle in one and
  sector in the other;
- k_n and b_n of a patch share a batch (the same two readout references, the
  same neighbor activity), and the four partner pairs of each patch are the
  indices 1 to 4 once.

A Latin rotation moves a group and the activity of its neighbors together, so
an activity-dependent loss difference d between kernel and bright circuits
enters kernel + bright - 1 as d/2 and can trip the pooled test.

## Placement

Tuna-17's coupling map is `TUNA17` of `scripts/qi_zero_divisor_cases.py`.
The candidate qubits are those outside `READOUT_EXCLUDED` and the visibility
exclusions of that script, re-read against a fresh readout batch, which is
the batch-0 stop condition below. Each patch is a three-qubit path for
(q3, q1, q0) plus one q2 qubit. Placement ranks disjoint triples of patches
by, in order:
1. no path that holds both q13 and q11, whose readout context is
   established (claim `qi-tuna17-boxkite-ladder-readout-context`);
2. the fewest couplers joining one patch's path qubits to another patch's
   path qubits, since the patches entangle simultaneously;
3. the fewest couplers from a q2 qubit to another patch's path;
4. the lexicographically least placement.

The admitted graph of 2026-10-17 has 12 qubits with q3 isolated, so three
patches fill it; a fourth patch needs 16 admitted qubits and does not fit.
The same graph forces q13 to be a q2 qubit beside q11: q10's only coupler
is to q13, so q10 is a q2 qubit, and every path through q13 holds q11. In
every placement that meets rules 1 to 3, q13 reads z2 of the patch whose
path holds q11, so the q13 readout-context effect enters that patch's z2
and its score; the analysis reports that patch separately, and the checkerboard
references measure q13 with q11 in |0> and in |1> (with q10 moving
together with q11).

## Series, references and shots

A batch holds at most three circuits (`HARDWARE_BATCH_CIRCUITS`) 120 s apart.
The series runs eight batches and 24 jobs at 32768 shots:

| batch | circuits |
|---|---|
| 00 | readout-0, readout-1, checkerboard-p (no witness) |
| 01 | witness-01, witness-02, checkerboard-q |
| 02 | witness-03, witness-04, readout-0 |
| 03 | witness-05, witness-06, readout-1 |
| 04 | quadrature-k1, quadrature-b1, quadrature-e7 |
| 05 | witness-07, witness-08, readout-0 |
| 06 | witness-09, witness-10, readout-1 |
| 07 | witness-11, witness-12, readout-0 |

References. Readout-0 prepares nothing. Readout-1 applies X to the 12 patch
qubits only, so the five idle qubits stay in |0> as they do in every witness.
The coupling graph of the patch qubits is bipartite (`bipartition()`); the
checkerboard references flip one part each (p: q1 q2 q3 q8 q13 q14 q15; q: q4
q10 q11 q12 q16), so with readout-0 and readout-1 every coupler of the patch
qubits meets all four joint preparations, q13 and q11 included. `build()`
checks this for each of the 12 couplers. Qubits that share a part cannot be
told apart by these references: q13 has two neighbors, q10 and q11, which both
sit in part q, so a context effect of q13 on q11 and on q10 reads the same and
the analysis lists the indistinguishable neighbors. Every witness is corrected
with its nearest readout-0 and readout-1 (the earlier batch on a tie), which
`readout_pairing` records.

The jobs take about 19.97 s each under the retained fit (2.6 s + 0.53 ms per
shot): 24 jobs are 479.2 s of execution, and the seven 120 s pauses bring the
wall time to 1319.2 s (22 minutes) before queue time. Shot order is retained.

## Quadrature batch

A GHZ pair (|a> + s e^{i phi}|~a>)/sqrt2 with a3 = 0 carries a branch phase phi
when a Z rotation acts on q3 (the q3 = 1 branch is ~a). For P with no Z factor,
<P> = Re(w e^{i phi} <a|P|~a>) with w the relative coefficient, and
<a|X|~a> = 1, <1|Y|0> = i, <0|Y|1> = -i give

- the witness parity <Y3 X1 Y0> = -w (2 a3 - 1)(2 a0 - 1) cos(phi) = s cos(phi)
  for k1 and b1 (a = (q3, q1, q0) = (0, 1, 1)): the kernel reads +cos(phi) and
  the bright state -cos(phi), so phi enters at second order;
- the quadrature parity <X3 X1 Y0> = -w (2 a0 - 1) sin(phi) = -s sin(phi), first
  order in phi, with q3 read by mY90.

`verify_quadrature_derivation()` checks both closed forms against a Qiskit
Statevector of the emitted pulses with a synthetic phase on q3, for eight pair
states, four basis states and six phases (maximum difference 1e-15). The batch
holds k1, b1 and e7 on all three patches. With V the visibility of the parity,
S = (m_b1 - m_k1)/2 = V sin(phi) from the quadrature circuits and
C = (m_k1 - m_b1)/2 = V cos(phi) from the Y-basis witnesses of the same patch,
phi = atan2(S, C) and V = hypot(S, C); phi has the standard error
sqrt(C^2 var S + S^2 var C)/(S^2 + C^2). The half sums (m_k1 + m_b1)/2 in both
bases and the e7 parity are null statistics. The estimator separates a phase
from damping, which the contraction law cannot do. The three circuits drive all
patches with the same state, so the neighbor activity differs from the
witnesses; the phase is a per-patch property read to first order.

## Preregistered analysis

- Per state and patch: the raw score mean with an empirical-Bernstein 95 %
  interval (the score is bounded in [0, 1] and is not a binomial
  proportion), and the kernel-outcome fraction with a Wilson interval.
- A readout-corrected score from the inverse tensor product of the four
  single-qubit assignment matrices of the nearest references, with a 95 %
  percentile interval from a seeded parametric bootstrap (4000 draws, seed
  20261022, numpy-batched per cell and pooled over cells) that redraws the
  witness outcome counts (multinomial) and every assignment rate from its
  reference counts (binomial). It is reported beside the raw interval. The
  correction applies the closed-form inverse of each 2 x 2 matrix in one
  operation order in the scalar and in the batched path, and the self-test
  compares their bits.
- Contraction law: under a depolarizing contraction V of the (q3, q1, q0)
  parity, kernel and bright states read (1 - V)/2 and (1 + V)/2, so
  kernel + bright - 1 is consistent with zero, and middle and sector states
  read 1/2. Each kernel/bright pair of a batch, their pooled value and each
  middle and sector state are tested; a violation at |z| >= 3 names a
  multi-qubit error outside the contraction, such as an entangling coherent
  error or leakage. The law is blind to a branch phase (kernel and bright
  move by (1 -+ cos phi) V/2 and still sum to one) and to single-qubit
  coherent errors; the quadrature batch reads the phase. It is blind to
  readout bias as well, which the parity averages almost away (P(1|0) 0.03
  and P(0|1) 0.08 under a 0.3 depolarization move the pooled pair sum by
  about 0.004), so readout bias is read from the corrected score.
- Patches are analyzed separately. The equal-weight pooled value names its
  estimand, and its variance includes the covariance of the patches' per-shot
  scores inside each circuit, because the three patches of one circuit are
  measured in the same shots.
- References: the assignment of every patch qubit in every reference, the
  batch-00 stop test, the bracket drift between successive references of one
  kind, and for each coupler the assignment of a qubit with its neighbor
  prepared 0 and 1, with z statistics for the shift.

## Stop conditions

- Batch 00's readout-0 or readout-1 shows a patch qubit with P(1|0) or P(0|1)
  above 0.15: the series stops and the placement is redrawn. The test runs on
  batch 00 itself, before any witness.
- Bracket drift: two successive readout-0 circuits move a patch qubit's
  P(1|0), or two successive readout-1 circuits move its P(0|1), by more than
  0.02 (about ten standard errors at 32768 shots): the series stops. The
  operator runs `--references` on the run directories after each batch that
  carries a reference.
- A job fails or returns fewer shots than requested; `--analyze` refuses a
  hardware series whose shot list is short and names the file before it
  computes a cell.
- The account-wide pause or the three-circuit limit would be broken.

## Dry run and approval

The dry run builds every circuit, runs the identical cQASM on local
qxelarator under `QI_PYTHON` for the Tuna series and for its QX twin, and
requires every witness cell to read its ideal score, every quadrature cell its
ideal parity (phi = 0) and every reference its preparation within shot noise.
The local manifests carry `control: local_qxelarator`, the simulator version
and the shots actually run, so the analysis labels them an emulator control.

The remote emulator takes 10 qubits, so the QX twin (`bdsc_pauli_qx`) packs
two patches per circuit on qubits 0 to 3 and 4 to 7: 23 circuits with
readout-0 and readout-1 in 12 batches at 2048 shots. Each patch repeats its
Tuna gate sequence on relabeled qubits (`build()` requires the equality) and
names its Tuna patch, circuit and batch, so the analysis and the contraction
pairs read as in the Tuna series. It is a noiseless plumbing control, and a
remote run is a job that joins the written case. The written case states what
the pilot measures, why noise simulation cannot answer it (the device's own
readout and preparation define the physical effect), the backend, shots,
expected seconds and credits.
