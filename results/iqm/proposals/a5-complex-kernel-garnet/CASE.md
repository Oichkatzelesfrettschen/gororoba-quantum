# IQM Garnet complex strata of the A_5 kernel map on 2 to 4 qubit coset blocks

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
The case is ledger row A5-632 (pool row QPU-68). It spends part of the 11.75 IQM credits that lapse 2026-12-01T00:00Z; the
ceiling of the job is 10.5 credits, within the 11.0 the owner set.

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (created 2026-11-22T03:02:20Z; copy in the
case's `calibration/`). One job of 80 circuits at 8,500 shots (680,000 executions; the limits are 100 circuits and 2,000,000
executions), built by `scripts/iqm_complex_kernel_case.py`. The digest of `results/iqm/cases/a5-complex-kernel-garnet/cases.json`
is in the pull request body. A live rebuild (`build --live`, a free read of the current calibration set) changes it, and an
approval names the digest after that rebuild.

## Question

Does the selector-zero difference of the coset-block kernel map of A_5 on Garnet read the complex nullity of e_i + i e_j
(16, 12, 8 and 4 at the strata 0/16, 4/12, 8/8 and 12/4, with e_1 + e_3, e_1 + e_26, e_1 + e_10 and e_1 + e_18) rather than the
real nullity (0, 4, 8, 12), and does the plain-phase mutation of the oracle read the opposite sign?

The ideal map is the exact statevector of [docs/evidence/a5-complex-kernel-map](../../../../docs/evidence/a5-complex-kernel-map/README.md):
the complex circuit is the real circuit with S phases on one data qubit and on the selector, 16 against 0 at e_1 + i e_3 and 12
against 4 at e_1 + i e_26, and plain phases read -14 and -2. The six-qubit map costs 91 to 96 CZ before routing, and the IBM
record of the real six-qubit map left 23 of 32 signs unresolved
([findings](../../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)). This case reads the same strata on blocks of 2 to 4 qubits
with 1 to 29 routed CZ.

## Why a simulation cannot answer it

The noise model of the case (depolarizing PRX and CZ, idle T1 and T2, herald-conditioned readout) carries no coherent error,
leakage or crosstalk, and it predicts the strata at every operand (below). The question is whether Garnet's own phase
conventions and coherent errors carry the S rotations and the pair-sign diagonals through 1 to 29 CZ to the selector bit. Only
the chip answers it: a simulation returns the ideal law it is built from.

## Mechanism of the block reading

- A coset block of dimension d holds the 2^d inputs of a coset of a subspace V of (Z/2)^5 that contains m = i XOR j, on d data
  qubits and the selector. The block law is the six-qubit law of the complex map restricted to the output coset
  (`gororoba_quantum/pathion_complex_block.py`; exact statevector agreement to 3e-16 on every coset, phase and orientation of the
  four operands, and with the folded-diagonal law, `tests/test_pathion_complex_block.py`).
- The selector-zero difference D = P_plus(s = 0) - P_minus(s = 0) of a block is the mean of its output contrasts, and for the
  chosen subspaces every coset reads D = N / 16 exactly, for t = 1, i and -i. A single block therefore reads the nullity N of
  L_(e_i + t e_j) over C. The strata fix N in {0, 4, 8, 12, 16}, so N / 16 has the denominator 2^(d-1) with d = 1 (N = 0 or 16),
  2 (N = 8) and 3 (N = 4 or 12). The audit test finds, for each of the 465 pairs of imaginary units, a subspace of that
  dimension whose cosets all read N exactly (closed-form amplitudes to 1e-9 and exact integer nullities, every pair).
- Real and complex circuits of an operand share one gate skeleton: the complex circuit adds one P(phase) on data qubit 0 and one
  on the selector to the real circuit, the basis having bit h of m on vector 0 alone. The compiled circuits of t = 1, i and
  orientations + and - differ in rotation angles alone (a test). The plain-phase kind drops the pair sign s_k of the oracle and
  has its own compile.
- Complement law (A5-629): D_complex + D_real = 1 on every operand, so the pair measures the visibility V = D_c + D_r with no
  reference to the complex sign table.

## Circuits, order and operands

| Operand | Pair | Stratum real/complex | Circuit qubits | Physical qubits | CZ (real, complex; plain) | Kinds |
|---|---|---|---|---|---|---|
| s016 | e_1 + e_3 | 0/16 | 2 | QB1, QB2 | 1; 1 | real, complex, plain |
| s412 | e_1 + e_26 | 4/12 | 4 | QB11, QB5, QB6, QB7 | 23; 29 | real, complex, plain |
| s808 | e_1 + e_10 | 8/8 | 3 | QB1, QB2, QB4, QB5 | 11 | real, complex |
| s124 | e_1 + e_18 | 12/4 | 4 | QB11, QB5, QB6, QB7 | 29 | real, complex |

Each kind runs in the orientations + and -, ordered +, -, -, + (a quad), once per kind in the first half and in reverse kind order
in the second half, so each kind meets its mirror image at the same distance from the job's center; 10 kinds, 80 circuits, four
copies per orientation. s808 is the null operand: its real and complex readings coincide at 8/8, so the ideal double difference
vanishes. The plain kind sits at the two operands where the six-qubit mutation is recorded (-14 and -2 as tile sums over all
cosets; the chosen coset reads -1 at s016 and -0.75 at s412 against +1 and +0.75 for the complex kind). The qubit QB12 is outside
every layout because the calibration set holds no herald-conditioned readout for it. Eight transpiler seeds (ANU draw
2026-11-27T222523Z, indices 10 to 17) give identical CZ counts and predicted visibilities at s016, s412 and s124 and two distinct values at s808, so the seeds
do not search the layout (s808 routes through one extra physical qubit).

## Estimators and the preregistered rule

(`gororoba_quantum/a5_complex_kernel_decision.py`; the case's `prediction.json` carries the predictions and the thresholds.)

- D of a kind is the difference of the selector-zero frequencies of the kept (herald zeros) shots of the + and - orientations,
  pooled over the four copies; its variance is the binomial variance times phi = 1.54, the 95 percent upper bound of the retained
  Garnet copy dispersion of the grover-plane case.
- Per operand: the raw double difference DD = D_c - D_r (ideal (2 D_c - 1) V; no division); V = D_c + D_r; the visibility-corrected
  nullity N_c = 16 D_c / V with delta-method standard error, undefined unless V exceeds 5 standard errors.
- Mutation reading D_p / V at s016 and s412, with the standard error of the ratio.
- Side of an operand: "complex-side" when (N_c - 8) has the sign of the complex reading and lies 5 standard errors from 8,
  "real-side" for the opposite, "unresolved" otherwise (N_r + N_c = 16 on every pair, so both readings split at 8).
- Verdict "complex strata" when s016, s412 and s124 are complex-side (above, above, below 8), the plain readings are negative by
  5 standard errors at s016 and s412, and |DD| / V at s808 stays within 0.10. "real strata" when the three read on the real side.
  "complex side, a control fails" when the three read complex-side and a control fails. "no reading" otherwise.
- The estimators never read the ideal sign table of the complex circuit. Tests feed them the real-map law in place of the complex
  circuit (reads N_c = 8 or an unresolved visibility, verdict "no reading"), the plain law (unresolved, "no reading"), the
  swapped kinds ("real strata") and a failed mutation control ("complex side, a control fails").

## Predictions and power

Exact density matrix of the touched qubits of each compiled circuit under the case's calibration copy (no sampling), planned at
a kept fraction of 0.5 of the shots (17,000 kept shots per orientation of a kind; the run's kept counts decide the analysis).

| Operand | D_c ideal, predicted | D_r ideal, predicted | V predicted | DD predicted | N_c ideal, predicted (SE) | z from 8 |
|---|---|---|---|---|---|---|
| s016 | 1.000, 0.980 | 0.000, 0.000 | 0.980 | 0.980 | 16, 16.00 (0.11) | 72.8 |
| s412 | 0.750, 0.529 | 0.250, 0.170 | 0.699 | 0.359 | 12, 12.11 (0.12) | 34.5 |
| s808 | 0.500, 0.449 | 0.500, 0.448 | 0.897 | 0.0015 | 8, 8.01 (0.08) | 0.18 |
| s124 | 0.250, 0.158 | 0.750, 0.481 | 0.639 | -0.323 | 4, 3.96 (0.13) | 31.0 |

The plain kind reads D_p / V = -1.00 at s016 and -0.70 at s412 in the model (ideal -1 and -0.75). Under the model the
probability that all three discriminating operands and both mutation readings reach 5 standard errors is 1.0 (normal
approximation, independent circuits). The z of each discriminating operand scales with V: the case still resolves 5 standard
errors at an absolute visibility of 0.067 (s016), 0.101 (s412) and 0.103 (s124), against the predicted 0.98, 0.70 and 0.64. The
model has no coherent error or leakage, so the predicted visibility is an upper bound, and the shots buy the margin.

## Cost

Billing v4 sizing (`gororoba_quantum/grover_plane_sizing.py`, inputs pinned in
`docs/evidence/iqm-garnet-grover-plane/billing_v4_inputs.json`): the three Garnet models v3, v4_max and v4_sum price the job at
10.37, 9.85 and 9.43 s of execution, expected runtime 10.80 s, expected billed 6.0 credits under each. The ceiling is the largest
of the models' all-jobs bands: 10.5 credits (21 billed seconds, cancel threshold 20 s); 9.0 credits under the Grover-jobs band.
The shot count is the largest in steps of 500 whose ceiling stays within 11.0. Margin of the cancel threshold over the longest
expected runtime: 9.2 s at 1 times, 3.8 s at 1.5 times and -3.8 s at 2.2 times (the sibling Emerald run's overrun), which the
ceiling does not cover: such a run would be cancelled and billed.

DECISION NEEDED (owner): the `garnet:mock` compile estimate (`execution_runtime_estimate_seconds`) is required before approval
and is not read here; keep 10.5 credits or raise it to 11.0 after reading it. The calibration set above was created 2026-11-22;
a job pins its set and fails if Garnet no longer holds it, in which case a live rebuild changes the digest and the approval.

## Steps before a submission

`build --live` (free read of the current calibration set; changes the digest), owner approval of the digest for the mock, mock run
and collect, owner approval of the identical digest for Garnet, `submit`, `collect`, analysis. Not run. A reader of the
collected run records that applies `a5_complex_kernel_decision.analyze` to the kept counts at bit d of each measure locus is not
written; the estimators are tested on synthetic counts.

## Falsifiers

- "no reading" or "real strata": the S rotations do not carry the complex stratum to the selector on Garnet, or the visibility of
  a discriminating operand falls under 5 standard errors.
- A failed mutation control (plain reading not negative at 5 standard errors at s016 or s412): the pair-sign diagonal does not
  determine the reading, so the complex readings are not the nullity read through the sign table.
- A null operand outside 0.10 of its visibility: the S gates alone shift the reading by that much at a stratum where the ideal
  complex and real readings coincide, a compile or position effect that confounds the three discriminating operands.

## Retention plan

The run record keeps `submission.json`, `raw/job.json`, `raw/measurements.json` and `results.json` byte for byte under
`results/iqm/runs/`, with the case's `cases.json`, `prediction.json` and `calibration/`. The ledger row A5-632 gains the
verdict and the estimates in the change that analyzes the run; the QRNG allocations of the case are in
`docs/evidence/qrng_seeds/allocations.json`.

## Residual risk

- The layout is not searched: eight transpiler seeds give one compile at three operands. s412 and s124 share the patch QB11, QB5,
  QB6, QB7, so a defect of the patch affects both.
- The model has no coherent error, leakage or crosstalk. The depolarizing visibility bound is an upper estimate, and the
  mutation and null controls guard the reading against an offset that is not the stratum.
- The kept fraction of the heralded shots is planned at 0.5 and unmeasured for these qubit sets.
- phi = 1.54 is a depth-1 bound of the Grover case applied to these circuits.
- The model's N_c bias is at most 0.11 (s412); a device offset that is arm-asymmetric enters D and cancels only to first order.
- The 2.2 times overrun is not covered by the ceiling (above).
- The block-dimension law and the complement-law visibility are checked in exact arithmetic on the repository's A_5 tables; their
  novelty is bounded by the code and notes of this repository, and no literature search was made for them.
