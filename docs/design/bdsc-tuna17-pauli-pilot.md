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

The readout rotates q3 and q0 by `Sdag` then `H` (Y basis), q1 by `H`
(X basis), leaves q2, and measures all four. With signs z2, y3, x1, y0 and
t = y3 x1 y0, the score is 1/2 for z2 = +1 and (1 - t)/2 for z2 = -1; its
mean is Tr(E0 rho) and z2 = -1, t = +1 is the kernel outcome.

## State bank

| group | states | ideal score | role |
|---|---|---:|---|
| kernel | k1..k4 = (e7 + e12, e6 - e13, e5 + e14, e4 - e15)/sqrt2 | 0 | target nulls, `bdsc.kernel_frame()` |
| bright | (e7 - e12, e6 + e13, e5 - e14, e4 + e15)/sqrt2 | 1 | sign partners of the kernel |
| middle | e0, e10 | 1/2 | z2 = +1: the score is 1/2 whatever q3, q1, q0 read |
| sector | e7, e12 | 1/2 | z2 = -1 basis states: t is a fair coin ideally |

Twelve states on three patches give 36 state-patch cells. A Latin rotation
puts each state on each patch once across 12 witness circuits of three
patches each, so state and patch separate.

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

## Series and shots

A batch holds at most three circuits (`HARDWARE_BATCH_CIRCUITS`) 120 s
apart. The series runs six batches of two witness circuits and one readout
reference, alternating readout-0 and readout-1, so every witness shares a
calibration with an assignment reference no more than one batch away; 18
jobs. At 32768 shots a job takes about 20 s under the retained fit
(2.6 s + 0.53 ms per shot), 6 minutes of execution and about 15 minutes of
wall time with the pauses. Shot order is retained.

## Preregistered analysis

- Per state and patch: the raw score mean with an empirical-Bernstein 95 %
  interval (the score is bounded in [0, 1] and is not a binomial
  proportion), and the kernel-outcome fraction with a Wilson interval.
- A readout-corrected score from the tensor product of single-qubit
  assignment matrices of the adjacent readout reference, reported beside
  the raw value.
- Contraction law: under a depolarizing contraction V of the (q3, q1, q0)
  parity, kernel and bright states read (1 - V)/2 and (1 + V)/2, so
  kernel + bright - 1 is consistent with zero, and middle and sector states
  read 1/2. A violation at |z| >= 3 per patch names an error outside the
  contraction (readout bias, leakage or a coherent preparation error).
- Patches are analyzed separately; a pooled value is reported only with
  equal patch weights and names that estimand.

## Stop conditions

- Batch 0's readout reference shows a patch qubit with P(1|0) or P(0|1)
  above 0.15: the series stops and the placement is redrawn.
- A job fails or returns fewer shots than requested.
- The account-wide pause or the three-circuit limit would be broken.

## Dry run and approval

The dry run builds every circuit, runs the identical cQASM on local
qxelarator under `QI_PYTHON`, and requires each witness to reproduce its
ideal scores within shot noise. A remote QX twin is a job and joins the
written case. The written case states what the pilot measures, why noise
simulation cannot answer it (the device's own readout and preparation define
the physical effect), the backend, shots, expected seconds and credits.
