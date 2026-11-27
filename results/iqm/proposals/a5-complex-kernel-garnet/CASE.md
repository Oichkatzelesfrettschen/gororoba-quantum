# IQM Garnet complex strata of the A_5 kernel map on 2 to 4 qubit coset blocks

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
The case is ledger row A5-632 (pool row QPU-68). It spends part of the 11.75 IQM credits that lapse 2026-12-01T00:00Z; the
ceiling of the job is 10.5 credits, within the 11.0 the owner set.

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (created 2026-11-22T03:02:20Z; copy in the
case's `calibration/`). One job of 80 circuits at 7,000 shots (560,000 executions; the limits are 100 circuits and 2,000,000
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
  (`gororoba_quantum/pathion_complex_block.py`; exact statevector agreement to 3.7e-15 at most on every coset, phase and
  orientation of the four operands, and with the folded-diagonal law, `tests/test_pathion_complex_block.py`).
- The selector-zero difference D = P_plus(s = 0) - P_minus(s = 0) of a block is the mean of its output contrasts, and for the
  chosen subspaces every coset reads D = N / 16 exactly, for t = 1, i and -i. A single block therefore reads the nullity N of
  L_(e_i + t e_j) over C. The strata fix N in {0, 4, 8, 12, 16}, so N / 16 has the denominator 2^(d-1) with d = 1 (N = 0 or 16),
  2 (N = 8) and 3 (N = 4 or 12). The audit test finds, for each of the 465 pairs of imaginary units, a subspace of that
  dimension whose cosets all read N exactly (closed-form amplitudes to 1e-9 and exact integer nullities, every pair).
- Complement law (A5-629): D_complex + D_real = 1 on every operand, so the pair measures the visibility V = D_c + D_r with no
  reference to the complex sign table.

## Synthesis: real and complex differ in PRX phase alone

The earlier compile merged the two phase gates of the complex circuit into the neighboring single-qubit runs. Measured on the
earlier circuits: 2 PRX gates of every operand (of 12, 84, 107 and 45) differed in amplitude between the real and complex
circuits and none in phase. A Z rotation between two rotations about X changes the net rotation's amplitude, so a PRX amplitude
error then acted differently on the two kinds.

The block template now keeps each phase gate as an RZ behind barriers. After the compile, every Z rotation moves to the end of
the circuit as a shift of the phase of each later PRX (r(theta, phi) after Rz(a) equals Rz(a) after r(theta, phi - a); CZ
commutes with Z; a Z before a measure changes no outcome), so the circuits that run contain PRX, CZ and measure alone. Real and
complex kinds, and both orientations, carry identical PRX amplitudes and CZ gates and differ in PRX phases (the builder
refuses a circuit that breaks this, and a test checks the emitted files). The plain-phase kind has its own compile; its
coset is the one whose plain circuit compiles to the CZ count of the real kind (19 against 19 at s412, 1 against 1 at s016).

## Operands, circuits and order

All four operands run on one patch, the star of QB11, QB5, QB6 and QB7 about QB6 (calibrated couplers QB6-QB11, QB6-QB5,
QB6-QB7), so the null operand's offset applies to the others. The layout of each operand is the injective placement on the patch
of the largest predicted visibility.

| Operand | Pair | Stratum real/complex | Circuit qubits | Physical qubits | CZ (every kind) | Kinds |
|---|---|---|---|---|---|---|
| s016 | e_1 + e_3 | 0/16 | 2 | QB11, QB6 | 1 | real, complex, plain |
| s412 | e_1 + e_26 | 4/12 | 4 | QB11, QB5, QB6, QB7 | 19 | real, complex, plain |
| s808 | e_1 + e_10 | 8/8 | 3 | QB11, QB6, QB7 | 9 | real, complex |
| s124 | e_1 + e_18 | 12/4 | 4 | QB11, QB5, QB6, QB7 | 29 | real, complex |

Each kind runs in the orientations + and -, ordered +, -, -, + (a quad), once per kind in the first half and in reverse kind order
in the second half, so each kind meets its mirror image at the same distance from the job's center; 10 kinds, 80 circuits, four
copies per orientation. s808 is the null operand: its real and complex readings coincide at 8/8, so the ideal double difference
vanishes. The plain kind sits at the two operands where the six-qubit mutation is recorded (-14 and -2 as tile sums over all
cosets; the chosen coset reads -1 at s016 and -0.75 at s412 against +1 and +0.75 for the complex kind). The qubit QB12 is outside
every layout because the calibration set holds no herald-conditioned readout for it. Eight transpiler seeds (ANU draw
2026-11-27T222523Z, indices 10 to 17) give identical CZ counts and predicted visibilities at the chosen layout of every operand, so
the seeds do not search anything beyond the placements.

## Estimators and the preregistered rule

(`gororoba_quantum/a5_complex_kernel_decision.py`; the case's `prediction.json` carries the predictions.)

- D of a kind is the difference of the selector-zero frequencies of the kept (herald zeros) shots of the + and - orientations,
  pooled over the four copies; its variance is the binomial variance times phi = 1.54, the 95 percent upper bound of the retained
  Garnet copy dispersion of the grover-plane case.
- Per operand: the raw double difference DD = D_c - D_r (ideal (2 D_c - 1) V; no division); V = D_c + D_r; r = DD / V and the
  nullity N_c = 8 + 8 r = 16 D_c / V with delta-method standard error, undefined unless V exceeds 5 standard errors. At s016
  D_r = 0 makes N_c identically 16 for any D_c > 0, so the visibility test carries that operand's resolution.
- Null subtraction (the hardware-probe rule, odd(t) - odd(0), in place of a gate): r_null is r of s808, whose ideal value is 0;
  the reading of each discriminating operand is N_c' = 8 + 8 (r - r_null) with the standard error of both. The null's
  visibility must resolve; its offset is subtracted, not bounded.
- Mutation reading D_p / V at s016 and s412, with the standard error of the ratio.
- Side of an operand: "complex-side" when (N_c' - 8) has the sign of the complex reading and lies 5 standard errors from 8,
  "real-side" for the opposite, "unresolved" otherwise (N_r + N_c = 16 on every pair, so both readings split at 8).
- Verdict "complex strata" when s016, s412 and s124 are complex-side (above, above, below 8), the null visibility resolves and the
  plain readings are negative by 5 standard errors at s016 and s412. "real strata" when the three read on the real side.
  "complex side, a control fails" when the three read complex-side and a control fails. "no reading" otherwise.
- The estimators never read the ideal sign table of the complex circuit. Tests feed them the real-map law in place of the complex
  circuit (reads N_c = 8 or an unresolved visibility, verdict "no reading"), the plain law ("no reading"), the swapped kinds
  ("real strata"), a failed mutation control ("complex side, a control fails") and an unresolved null ("no reading").
- The run reader `scripts/iqm_complex_kernel_analyze.py RUN_DIR` validates a retained run with `iqm_records.read_run`, refuses a
  mock run, a run whose cases.json or prediction.json differs from the retained case and a run compiled against another
  calibration set, tallies the kept shots at the selector bit of each measure locus, applies `analyze` and reports the kept
  fraction, the billed seconds and the first-half against second-half z of each kind. Tests run it on synthetic run records built
  from the predicted laws.

## Predictions and power

Exact density matrix of the touched qubits of each compiled circuit under the case's calibration copy (no sampling; ASAP idle
relaxation, as the idle-schedule case resolved on Garnet at 13 to 59 standard errors,
[design](../../../../docs/design/iqm-garnet-idle-schedule-train-readout.md)), planned at a kept fraction of 0.5 of the shots
(14,000 kept shots per orientation of a kind; the run's kept counts decide the analysis).

| Operand | D_c ideal, predicted | D_r ideal, predicted | V predicted | N_c ideal, predicted | N_c' predicted (SE) |
|---|---|---|---|---|---|
| s016 | 1.000, 0.974 | 0.000, 0.000 | 0.974 | 16, 16.00 | 16.03 (0.15) |
| s412 | 0.750, 0.565 | 0.250, 0.186 | 0.751 | 12, 12.04 | 12.07 (0.15) |
| s808 | 0.500, 0.427 | 0.500, 0.430 | 0.857 | 8, 7.97 | null: r_null = -0.0039 |
| s124 | 0.250, 0.154 | 0.750, 0.480 | 0.634 | 4, 3.88 | 3.92 (0.17) |

The plain kind reads D_p / V = -1.00 at s016 and -0.75 at s412. The z of the six conditions of the complex verdict (three
discriminating operands, two mutation readings, the null visibility) are 53.4, 27.1, 24.0, 125.4, 60.0 and 90.4, so the
probability that all six reach 5 standard errors is 1.0 under the model (normal approximation, independent circuits). The
model has no coherent error, so its visibility is an upper bound; the audit below measures the coherent errors.

## Coherent-error audit (first order and beyond, through the noise model)

As `scripts/iqm_probe_audit.py` does, each error enters after the scheduling, and every kind and orientation of the case runs
through the exact density matrix at the error; the predicted counts pass through the preregistered rule
(`prediction.json`, `coherent_audit`). Errors: every PRX angle times 1 + e for e = +-1 to +-5 percent; an RZZ(+-0.05 rad) after
every CZ; the ALAP schedule.

| Error | Verdict | r_null | N_c' s412 (ideal 12) | N_c' s124 (ideal 4) | N_c s412, s124 without subtraction |
|---|---|---|---|---|---|
| none | complex strata | -0.004 | 12.07 | 3.92 | 12.04, 3.88 |
| PRX +1 percent | complex strata | -0.000 | 11.88 | 3.65 | 11.87, 3.64 |
| PRX +2 percent | complex strata | 0.001 | 11.52 | 3.49 | 11.53, 3.50 |
| PRX +3 percent | complex strata | 0.001 | 11.05 | 3.47 | 11.05, 3.47 |
| PRX +5 percent | complex strata | 0.003 | 9.92 | 3.97 | 9.94, 4.00 |
| PRX -1 percent | complex strata | -0.012 | 12.09 | 4.32 | 11.99, 4.23 |
| PRX -2 percent | complex strata | -0.027 | 11.94 | 4.92 | 11.73, 4.71 |
| PRX -3 percent | complex strata | -0.054 | 11.69 | 5.84 | 11.26, 5.41 |
| PRX -4 percent | no reading | -0.098 | 11.44 | 7.34 | 10.66, 6.55 |
| PRX -5 percent | no reading | -0.172 | 11.38 | 10.25 | 10.00, 8.87 |
| RZZ +0.05 rad | complex strata | -0.007 | 12.25 | 4.05 | 12.19, 3.99 |
| RZZ -0.05 rad | complex strata | 0.008 | 11.94 | 3.84 | 12.00, 3.90 |
| ALAP schedule | complex strata | -0.001 | 12.06 | 3.91 | 12.05, 3.90 |

Reading. The synthesis removes the amplitude difference between the kinds, and a PRX amplitude error still enters the readings:
it rotates about axes that differ between the kinds, since their PRX phases differ. The verdict (the side of 8) holds for PRX
amplitude errors from -3 to +5 percent and for RZZ of 0.05 rad, and fails to "no reading" at -4 percent and below, where r_null
and the s124 reading cross toward 8. The case proposes the bound: the verdict is valid for a PRX amplitude error of at most 3
percent in magnitude; the readings N_c' carry biases of up to -1.0 (s412 at +3 percent) and +1.8 (s124 at -3 percent), so they are
side-of-8 decisions, not values of the nullity to better than about 2. The null subtraction follows the hardware-probe rule; it
lowers the bias at s412 by 0.4 at -3 percent and raises it by 0.4 at s124, where the null's offset adds to a bias of the
same sign. Garnet's PRX amplitude error is not measured here; the 3 percent bound is a
hypothesis about the device. The null's offset r_null reports a negative error (0.054 in magnitude at -3 percent, 0.098 at
-4 percent) and does not report a positive one (0.003 at +5 percent, where s412 reads 9.9).

## Cost

Billing v4 sizing (`gororoba_quantum/grover_plane_sizing.py`, inputs pinned in
`docs/evidence/iqm-garnet-grover-plane/billing_v4_inputs.json`): the three Garnet models v3, v4_max and v4_sum price the job at
8.43, 8.00 and 7.65 s of execution, expected runtime 8.87 s, expected billed 5.5, 5.0 and 5.0 credits. The all-jobs band prices
the ceiling at 9.0 credits at most; the job carries 10.5 credits (21 billed seconds, cancel threshold 20 s), within the owner's
11.0, so a 2.2 times overrun of the runtime (the overrun of the sibling Emerald run, 19.51 s) stays under the threshold. The
shot count is the largest in steps of 500 for which the band ceiling stays within 10.5 and that overrun fits: 7,000. Margin of
the cancel threshold over the runtime: 11.1 s at 1 times, 6.7 s at 1.5 times and 0.49 s at 2.2 times.

DECISION NEEDED (owner): the `garnet:mock` compile estimate (`execution_runtime_estimate_seconds`) is required before approval
and is not read here; keep 10.5 credits or raise it to 11.0 after reading it. The calibration set above was created 2026-11-22;
a job pins its set and fails if Garnet no longer holds it, in which case a live rebuild changes the digest and the approval.

## Steps before a submission

`build --live` (free read of the current calibration set; changes the digest), owner approval of the digest for the mock, mock run
and collect, owner approval of the identical digest for Garnet, `submit`, `collect`, `scripts/iqm_complex_kernel_analyze.py`. Not run.

## Falsifiers

- "no reading" or "real strata": the S rotations do not carry the complex stratum to the selector on Garnet, or the visibility of
  a discriminating operand falls under 5 standard errors.
- A failed mutation control (plain reading not negative at 5 standard errors at s016 or s412): the pair-sign diagonal does not
  determine the reading, so the complex readings are not the nullity read through the sign table.
- An unresolved null visibility: the null subtraction has no footing, and the complex verdict is not read.

## Retention plan

The run record keeps `submission.json`, `raw/job.json`, `raw/measurements.json` and `results.json` byte for byte under
`results/iqm/runs/`, with the case's `cases.json`, `prediction.json` and `calibration/`. The ledger row A5-632 gains the
verdict and the estimates in the change that analyzes the run; the QRNG allocations of the case are in
`docs/evidence/qrng_seeds/allocations.json`.

## Residual risk

- The layout search covers the patch only; s412 and s124 share the star, so a defect of the patch affects every operand (the
  null subtraction absorbs a common offset, and the mutation controls guard the sign).
- The model has no leakage or crosstalk, and the audit covers PRX amplitude, a CZ ZZ rotation and the schedule, each alone.
- The kept fraction of the heralded shots is planned at 0.5 and unmeasured for these qubit sets.
- phi = 1.54 is a depth-1 bound of the Grover case applied to these circuits.
- The 2.2 times overrun fits with 0.49 s to spare; a larger overrun is cancelled and billed.
- The block-dimension law and the complement-law visibility are checked in exact arithmetic on the repository's A_5 tables; their
  novelty is bounded by the code and notes of this repository, and no literature search was made for them.
