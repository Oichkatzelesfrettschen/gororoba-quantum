** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
# IQM Garnet complex strata of the A_5 kernel map on 2 to 4 qubit coset blocks

Status: written case awaiting the owner's approval of the digest below; nothing submitted to `garnet`. The `garnet:mock` twin
(0 credits) runs after the live rebuild and reports acceptance and estimates only.
The case is ledger row A5-632 (pool row QPU-68). It spends part of the 11.75 IQM credits that lapse 2026-12-01T00:00Z; the
ceiling of the job is 10.5 credits, within the 11.0 the owner set.

Backend `iqm:garnet`, calibration set `a8782702-7021-4533-ba2c-468cfb504bb8` (metrics set created 2026-11-28T02:46:31Z; copy in the case's
`calibration/`). One job of 80 circuits at 5,800 shots (464,000 executions; the limits are 100 circuits and
2,000,000 executions), built by `scripts/iqm_complex_kernel_case.py`. The digest of
`results/iqm/cases/a5-complex-kernel-garnet/cases.json` is in the pull request body. Garnet rotates its calibration set about
daily and a job that pins a retired set fails at station control; a rebuild (`build --live`, a free read of the current set)
changes the digest, and an approval names the digest after that rebuild.

## Question

Does the selector-zero difference of the coset-block kernel map of A_5 on Garnet read the complex nullity of e_i + i e_j
(16, 12, 8 and 4 at the strata 0/16, 4/12, 8/8 and 12/4, with e_1 + e_3, e_1 + e_26, e_1 + e_10 and e_1 + e_18) rather than the
real nullity (0, 4, 8, 12), and does the plain-phase mutation of the oracle read the opposite sign at s412?

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
  (`gororoba_quantum/pathion_complex_block.py`). On every coset, phase and orientation of the four operands the gate form, the
  folded-diagonal form and the six-qubit statevector restriction agree to 4e-15 (the folded form differs from the six-qubit
  restriction by 3.66e-15 at most and the gate form by 3.94e-15 at most; `tests/test_pathion_complex_block.py` checks every
  pairwise difference below 1e-13).
- The selector-zero difference D = P_plus(s = 0) - P_minus(s = 0) of a block is the mean of its output contrasts, and for the
  chosen subspaces every coset reads D = N / 16 exactly, for t = 1, i and -i. A single block therefore reads the nullity N of
  L_(e_i + t e_j) over C. The strata fix N in {0, 4, 8, 12, 16}, so N / 16 has the denominator 2^(d-1) with d = 1 (N = 0 or 16),
  2 (N = 8) and 3 (N = 4 or 12). The audit test finds, for each of the 465 pairs of imaginary units, a subspace of that
  dimension whose cosets all read N exactly (closed-form amplitudes to 1e-9 and exact integer nullities, every pair).
- Complement law (A5-629): D_complex + D_real = 1 on every operand, so the pair measures the visibility V = D_c + D_r with no
  reference to the complex sign table.

## Synthesis: real and complex differ in PRX phase alone

The block template keeps each phase gate as an RZ behind barriers. After the compile, every Z rotation moves to the end of the
circuit as a shift of the phase of each later PRX (r(theta, phi) after Rz(a) equals Rz(a) after r(theta, phi - a); CZ commutes
with Z; a Z before a measure changes no outcome), so the circuits that run contain PRX, CZ and measure alone. Real and complex
kinds, the sentinel, and both orientations carry identical PRX amplitudes and CZ gates and differ in PRX phases (the builder
refuses a circuit that breaks this, and a test checks the emitted files). A Z rotation merged into a neighboring rotation
would change that rotation's amplitude, so a PRX amplitude error would act differently on the two kinds.

## The mutation coset

The plain-phase kind drops the pair sign s_k of the oracle. A pair sign that is constant on the upper members of the block
multiplies every upper amplitude by one sign, which equals the orientation phase pi, so the plain kind then reproduces the
complex kind with the orientations swapped and no sign table is tested. The builder therefore keeps a coset only when
the plain selector difference is negative and the outcome law of the plain kind differs from that of the complex kind with the
orientations swapped by at least 0.05 (`plain_gap`; the choice reads exact laws alone, never a compile). No coset of s016 (one
pair, one sign) passes both tests: the cosets with a negative plain difference have gap 0, and the one coset with a gap
(0.5) has a positive plain difference, so s016 carries no plain kind. At s412 the cosets of the subspace read the gap 0.125,
0.125, 0.125 and 0 and the plain selector difference +0.25, -0.75, +0.75 and -0.75; coset 1 is the only one that passes both
(pair sign not constant), and its plain kind compiles to 29 CZ against 23 CZ of the real and complex kinds. The mutation
reading D_p / V therefore divides a contrast through 29 CZ by a visibility through 23 CZ; the rule asks only that it fall below
zero.

## The star of four qubits

All four operands run on one star (a center and three neighbors on calibrated couplers), so the null operand's offset applies
to the others. The rule that chooses it is written in `rank_stars` and runs on the calibration set of the build: every star of four
usable qubits ranks by the fewest qubits whose retained parallel PRX train is not linear
(`results/iqm/idle_schedule_probe_analysis.json`, set a18a947f of 2026-10-25, sha256 dc81ac1b23bf), then the
fewest qubits that train did not measure, then the largest product of the three CZ fidelities, then the largest PRX RB fidelity of
the weakest qubit, then the names. On this calibration set 32 stars are usable; the first is the patch
(QB13, QB3, QB8, QB9 with QB9 at the center; CZ product 0.991283,
weakest PRX RB fidelity 0.999456, every train linear). The patch of the previous build (QB14, QB4, QB9, QB8) ranks 2 of 32 on this set. The star of the first draft of the case (QB6 with QB11, QB5 and QB7) ranks
28 of 32: three of its four trains failed the linear fit (QB7 chi-square 227, QB5 20.7, QB11 19.3).
The full ranking is in `prediction.json` (`star`). The layout of each operand is the injective placement on the patch of the largest
predicted visibility.

## Operands, circuits and order

| Operand | Pair | Stratum real/complex | Circuit qubits | Physical qubits | CZ | Kinds |
|---|---|---|---|---|---|---|
| s016 | e_1 + e_3 | 0/16 | 2 | QB8, QB9 | 1 | cplx, real |
| s412 | e_1 + e_26 | 4/12 | 4 | QB13, QB3, QB8, QB9 | 23 (real, complex), 29 (plain) | cplx, plain, real |
| s808 | e_1 + e_10 | 8/8 | 3 | QB3, QB8, QB9 | 9 | cplx, real, sent |
| s124 | e_1 + e_18 | 12/4 | 4 | QB13, QB3, QB8, QB9 | 29 | cplx, real |

Each kind runs in the orientations + and -, ordered +, -, -, + (a quad), once per kind in the first half of the job and in reverse
kind order in the second half, so each kind meets its mirror image at the same distance from the job's center; 10 kinds, 80
circuits, four copies per orientation. The first half runs s808 real, s808 cplx, s124 real, s124 cplx, s016 real, s016 cplx,
s412 real, s412 cplx, s412 plain and s808 sent. The null pair sits at the outer end, the weakest kind (s124 cplx) away from both
ends, and the sentinel at the center. s808 is the null operand: its real and complex readings coincide at 8/8, so the ideal
double difference vanishes. The sentinel (s808 sent) is the real circuit of s808 again; its arm difference at the center
and that of s808 real at the outer end agree under a stationary device, and a drift symmetric about the center, which leaves
the half-to-half z of every kind at zero (each kind's two quads are mirror images), moves one of the two. Eight transpiler seeds
(ANU draw 2026-11-27T222523Z, indices 10 to 17) give identical CZ counts and predicted visibilities at the chosen layout of every
operand, so the seeds do not search anything beyond the placements.

## Estimators and the preregistered rule

(`gororoba_quantum/a5_complex_kernel_decision.py`; the constants are fixed numbers, not functions of the calibration set, and
`prediction.json` records them with the sha256 of the source.)

- D of a kind is the difference of the selector-zero frequencies of the kept (herald zeros) shots of the + and - orientations,
  pooled over the four copies; its variance is the binomial variance times phi = 1.54, the 95 percent upper bound of the retained
  Garnet copy dispersion of the grover-plane case.
- Per operand: the raw double difference DD = D_c - D_r (ideal (2 D_c - 1) V); V = D_c + D_r and the nullity
  N_c = 8 + 8 r = 16 D_c / V with r = DD / V and delta-method standard error, undefined unless V exceeds 5 standard errors. At s016
  D_r = 0 makes N_c identically 16 for any D_c > 0, so the visibility floor carries that operand's resolution.
- Null subtraction (the hardware-probe rule, odd(t) - odd(0), in place of a gate): r_null is r of s808, whose ideal value is 0;
  the reading of each discriminating operand is N_c' = 8 + 8 (r - r_null) with the standard error of both.
- Mutation reading D_p / V at s412 with the standard error of the ratio; a reading without spread (a dead control) reads
  minus infinity below zero and fails.
- Drift reading: z of D(s808 real, outer) - D(s808 sent, center).
- Side of an operand: "complex-side" when (N_c' - 8) has the sign of the complex reading and lies 5 standard errors from 8,
  "real-side" for the opposite, "unresolved" otherwise.
- The verdict **complex strata within tolerance** requires all of: s016, s412 and s124 complex-side; each |N_c' - ideal| at most
  2.0 of 16, 12 and 4; the plain reading below zero by 5 standard errors at s412; the null visibility resolved with |r_null| at
  most 0.08; V of s016 at least 0.5; and |drift z| at most 5. The tolerance 2.0 is half the distance of 4 between the complex
  reading and the nearest wrong stratum of s412 and s124. **real strata within tolerance**: the three read real-side within 2.0
  of 0, 4 and 12 with the null bound and the drift check holding. **complex side, off tolerance** and **real side, off
  tolerance**: the sides hold and a reading lies beyond the tolerance. **complex side, a control fails**: the sides and
  tolerance hold and the mutation, the null, the s016 visibility or the drift check fails. **no reading** otherwise. The verdict
  names what the rule tests: strata within a stated distance of the exact values, not a measured nullity to better than 2.
- The estimators never read the ideal sign table of the complex circuit. Tests feed them the real-map law in place of the
  complex circuit, the plain law, swapped kinds, a failed and a dead mutation control, an unresolved null, a wrong phase of 30,
  45 and 135 degrees (each refused), the exact quarter turn (accepted), an s016 visibility of 0.08 (refused) and a dip symmetric
  about the center (caught by the sentinel, missed by the half-to-half z).
- The run reader `scripts/iqm_complex_kernel_analyze.py RUN_DIR` validates a retained run with `iqm_records.read_run`, refuses a
  mock run, a job record that names another quantum computer than Garnet, a run whose cases.json or prediction.json differs
  from the retained case, a run compiled against another calibration set or with no compilation record, a shot that is not
  a bit and a circuit without the measure key; it tallies the kept shots at the selector bit of each measure locus, applies the rule,
  and reports the kept fraction, the billed seconds, the first-half against second-half z of each kind and the sentinel's
  inner_outer_z. Tests run it on synthetic run records built from the predicted laws.

## Predictions and power

Exact density matrix of the touched qubits of each compiled circuit under the case's calibration copy (no sampling; ASAP idle
relaxation, as the idle-schedule case resolved on Garnet at 13 to 59 standard errors,
[design](../../../../docs/design/iqm-garnet-idle-schedule-train-readout.md)), planned at a kept fraction of 0.5 of the shots
(11,600 kept shots per orientation of a kind; the run's kept counts decide the analysis).

| Operand | D_c ideal, predicted | D_r ideal, predicted | V predicted | N_c ideal, predicted | N_c' predicted (SE) |
|---|---|---|---|---|---|
| s016 | 1.000, 0.977 | 0.000, 0.000 | 0.977 | 16, 16.00 | 16.03 (0.16) |
| s412 | 0.750, 0.603 | 0.250, 0.195 | 0.798 | 12, 12.08 | 12.11 (0.15) |
| s808 | 0.500, 0.452 | 0.500, 0.455 | 0.908 | 8, 7.97 | null: r_null = -0.0033 |
| s124 | 0.250, 0.181 | 0.750, 0.558 | 0.739 | 4, 3.92 | 3.95 (0.16) |

The plain kind reads D_p / V = -0.70 at s412. The z margins of the six conditions that carry a number (three discriminating
operands, the s412 mutation, the null visibility, the s016 visibility over its floor) are 49.787, 26.62, 24.833, 56.45, 88.434, 57.233. The recorded power is
the probability that the complete rule returns the complex verdict when the counts of every kind and orientation scatter about the
predicted counts as normals of variance phi n p (1 - p): the joint rule runs on 4,096 unscrambled Sobol' draws, so the shared null
operand and the shared visibilities enter, and the result is 1.000 under the model. The model has no coherent error, so its
visibility is an upper bound; the audit below measures the coherent errors.

## Coherent-error audit (first order and beyond, through the noise model)

As `scripts/iqm_probe_audit.py` does, each error enters after the scheduling, and every kind and orientation of the case runs
through the exact density matrix at the error; the predicted counts pass through the preregistered rule
(`prediction.json`, `coherent_audit`). Errors: every PRX angle times 1 + e on all qubits (e = +-1 to +-5 percent) and on one qubit
of the star (+-3 and +-5 percent); an RZZ(+-0.05 rad) after every CZ; a conditional phase (cphase) of +-0.05 and +-0.10 rad after every
CZ; a residual Z rotation (zres) of +-0.05 and +-0.15 rad on both qubits after every CZ; the combined triple (PRX -2 percent, cphase
-0.05 rad, zres -0.05 rad) at 0.25, 0.5, 1 and 1.5 times and the triple of opposite sign at 1 times; the ALAP schedule.

| Family | Largest magnitude below which every row reads complex strata within tolerance |
|---|---|
| PRX amplitude, every qubit | 2 percent |
| PRX amplitude, one qubit | 3 percent |
| RZZ after every CZ | 0.05 rad |
| cphase after every CZ | 0.05 rad |
| zres after every CZ | 0.05 rad |
| combined (-2 percent, -0.05 rad, -0.05 rad) | 0.5 times the triple |
| combined, opposite sign | 1 times the triple |

| Error | Verdict | r_null | N_c' s412 (ideal 12) | N_c' s124 (ideal 4) |
|---|---|---|---|---|
| alap | complex strata within tolerance | -0.001 | 12.09 | 3.95 |
| combined+1x | complex strata within tolerance | 0.061 | 13.82 | 5.44 |
| combined-0.25x | complex strata within tolerance | -0.032 | 11.94 | 4.33 |
| combined-0.5x | complex strata within tolerance | -0.070 | 11.94 | 5.14 |
| combined-1.5x | no reading | -0.522 | 16.01 | 14.93 |
| combined-1x | no reading | -0.198 | 12.79 | 8.27 |
| cphase+0.05 | complex strata within tolerance | 0.034 | 12.10 | 3.90 |
| cphase+0.10 | complex side, a control fails | 0.083 | 12.05 | 3.82 |
| cphase-0.05 | complex strata within tolerance | -0.032 | 12.13 | 4.10 |
| cphase-0.10 | complex strata within tolerance | -0.055 | 12.21 | 4.50 |
| none | complex strata within tolerance | -0.003 | 12.11 | 3.95 |
| prx+0.01 | complex strata within tolerance | 0.000 | 12.64 | 3.69 |
| prx+0.02 | complex strata within tolerance | 0.001 | 13.36 | 3.54 |
| prx+0.03 | complex side, off tolerance | 0.001 | 14.32 | 3.53 |
| prx+0.03@QB13 | complex strata within tolerance | -0.003 | 12.11 | 3.36 |
| prx+0.03@QB3 | complex strata within tolerance | 0.053 | 12.30 | 3.57 |
| prx+0.03@QB8 | complex strata within tolerance | -0.019 | 12.57 | 4.26 |
| prx+0.03@QB9 | complex strata within tolerance | -0.024 | 13.02 | 3.67 |
| prx+0.04 | complex side, off tolerance | 0.002 | 15.56 | 3.67 |
| prx+0.05 | complex side, off tolerance | 0.004 | 17.08 | 4.06 |
| prx+0.05@QB13 | complex strata within tolerance | -0.003 | 12.15 | 2.90 |
| prx+0.05@QB3 | complex side, a control fails | 0.091 | 12.54 | 3.31 |
| prx+0.05@QB8 | complex strata within tolerance | -0.047 | 13.30 | 4.79 |
| prx+0.05@QB9 | complex strata within tolerance | -0.018 | 13.40 | 3.30 |
| prx-0.01 | complex strata within tolerance | -0.011 | 11.76 | 4.35 |
| prx-0.02 | complex strata within tolerance | -0.026 | 11.58 | 4.94 |
| prx-0.03 | complex strata within tolerance | -0.053 | 11.59 | 5.86 |
| prx-0.03@QB13 | complex strata within tolerance | -0.003 | 12.20 | 4.38 |
| prx-0.03@QB3 | complex strata within tolerance | -0.059 | 12.03 | 4.33 |
| prx-0.03@QB8 | complex strata within tolerance | -0.015 | 12.24 | 4.09 |
| prx-0.03@QB9 | complex strata within tolerance | 0.052 | 10.85 | 3.95 |
| prx-0.04 | no reading | -0.098 | 11.85 | 7.37 |
| prx-0.05 | no reading | -0.171 | 12.44 | 10.33 |
| prx-0.05@QB13 | complex strata within tolerance | -0.003 | 12.31 | 4.59 |
| prx-0.05@QB3 | complex side, a control fails | -0.096 | 12.03 | 4.59 |
| prx-0.05@QB8 | complex strata within tolerance | -0.037 | 12.57 | 4.18 |
| prx-0.05@QB9 | complex side, off tolerance | 0.108 | 9.82 | 3.80 |
| zres+0.05 | complex strata within tolerance | 0.054 | 12.12 | 3.95 |
| zres+0.15 | complex side, off tolerance | 0.211 | 11.07 | 1.82 |
| zres-0.05 | complex strata within tolerance | -0.063 | 12.01 | 4.25 |
| zres-0.15 | no reading | -0.237 | 12.53 | 7.58 |
| zz+0.05 | complex strata within tolerance | -0.007 | 12.27 | 4.08 |
| zz-0.05 | complex strata within tolerance | 0.008 | 12.03 | 3.87 |

Reading. No audited error reads real strata. The rule fails closed: a coherent error moves the verdict to "no reading", "complex
side, off tolerance" or "complex side, a control fails", never to a wrong stratum. The combined triple at 1 times breaks the verdict (s124 reads 8.27 at r_null = -0.20, "no reading"): PRX over-rotation, cphase and zres each below the single
error bound together add to a reading the rule refuses, so the complex verdict holds for a combined error of at most half the triple
(PRX -1 percent, cphase -0.025 rad, zres -0.025 rad). The uniform PRX amplitude bound (2 percent) is set by s412 at positive error (its reading moves up by about 0.7 per percent
and leaves the tolerance at +3 percent) and by s124 and the null at negative error (-4 percent reads no verdict).

Retained Garnet measurements bound the PRX terms only. The parallel PRX train of the idle-schedule case (2026-10-25, set a18a947f,
`results/iqm/idle_schedule_probe_analysis.json`) measured the over-rotation of the four qubits of this star, each train linear:
QB13 +0.01 +- 0.07 percent (chi-square 15.7, linear), QB3 -0.11 +- 0.07, QB8 +0.07 +- 0.07 and QB9 -0.19 +- 0.07. Isolated trains on QB11 and QB6 read -0.30 +- 0.06 and -0.18 +- 0.07
percent (the same set) and QB11 +0.15 +- 0.07 percent on set 68b0f1d0 (the amplification train of `results/iqm/kernel_cancellation_probe_analysis.json`); the
span -0.30 to +0.15 percent of these isolated measurements is well inside the 2 percent bound, and the parallel train of the star's own qubits stays within 0.19 percent. Those records come from other calibration sets, and the
amplitude error of the live set is not measured. The retained records hold no measurement of the CZ conditional phase or of the
residual Z rotation (searched: results/iqm, docs/notes/iqm, docs/evidence/iqm*, docs/design for cphase, conditional phase and zres), so the combined bound rests
on the model alone: a combined error beyond half the triple reads no verdict, and the case reports it as such. A four-circuit PRX
train on the star would measure the PRX term in the job; the 80 circuits carry the sentinel instead, and four more circuits fit the 100-circuit limit and the ceiling.

## Cost

Billing v4 sizing (`gororoba_quantum/grover_plane_sizing.py`, inputs pinned in
`docs/evidence/iqm-garnet-grover-plane/billing_v4_inputs.json`): the three Garnet models v3, v4_max and v4_sum price the job at
7.11, 6.75 and 6.49 s of execution, expected runtime 7.55 s, expected billed
4.5, 4.5 and 4.5 credits. The all-jobs band prices the ceiling at 7.5 credits at most; the job carries 10.5
credits (21 billed seconds, cancel threshold 20 s), within the owner's 11.0. The shot count is 5,800: the 2.2 times overrun of the runtime (the overrun of the sibling Emerald run,
18.45 s) clears the cancel threshold by 3.40 s, and the builder refuses a size whose margin falls under 1.5 s (the latency of the
station-control stop after a cancel). Margin of the cancel threshold over the runtime: 12.5 s at 1 times, 8.7 s at 1.5 times and
3.40 s at 2.2 times. The `garnet:mock` compile estimate of the 6,500-shot build read 8.50 s against 7.95 s modelled, so the shot count fell to 6,000. The 6,000-shot mock compile estimate (7.97 s) exceeded the modelled execution (7.35 s) by 0.623 s, so 5,800 shots keeps the 2.2 times overrun of the modelled runtime plus that excess above the 1.5 s floor (margin 2.03 s: 20 s less 2.2 times 8.17 s).

The ceiling stays 10.5 credits (the owner's limit is 11.0); the `garnet:mock` compile estimate
(`execution_runtime_estimate_seconds`) of this build is reported in the pull request. A job pins its calibration set and fails if Garnet no longer holds it.

## Steps before a submission

`build --live` (free read of the current calibration set; changes the digest), owner approval of the digest for the mock, mock run
and collect, owner approval of the identical digest for Garnet, `submit`, `collect`, `scripts/iqm_complex_kernel_analyze.py`. The
mock outcome never enters the analysis.

## Falsifiers

- "no reading", "real strata within tolerance" or a side outside the tolerance: the S rotations do not carry the complex stratum to the selector on
  Garnet within 2.0 of the exact value, or the visibility of a discriminating operand falls under 5 standard errors.
- A failed mutation control (plain reading not negative at 5 standard errors at s412): the pair-sign diagonal does not
  determine the reading, so the complex readings are not the nullity read through the sign table.
- An unresolved null visibility or |r_null| above 0.08: the null subtraction has no footing, and the complex verdict is not read.
- |drift z| above 5: the device is not stationary between the outer end and the center of the job, and the verdict is not read.

## Retention plan

The run record keeps `submission.json`, `raw/job.json`, `raw/measurements.json` and `results.json` byte for byte under
`results/iqm/runs/`, with the case's `cases.json`, `prediction.json` and `calibration/`. The ledger row A5-632 gains the
verdict and the estimates in the change that analyzes the run; the QRNG allocations of the case are in
`docs/evidence/qrng_seeds/allocations.json`.

## Residual risk

- The layout search covers the patch only; every operand shares the star, so a defect of the patch affects every operand (the
  null subtraction absorbs a common offset, and the mutation control guards the sign at one operand: s808 and s124 hold cosets
  whose pair sign is not constant and whose plain difference is negative, and no second mutation operand is run).
- The model has no leakage or crosstalk, and the audit covers the listed coherent errors, each alone or in the one combined triple.
- The kept fraction of the heralded shots is planned at 0.5 and unmeasured for these qubit sets.
- phi = 1.54 is a depth-1 bound of the Grover case applied to these circuits.
- The 2.2 times overrun fits with 2.03 s to spare after the mock excess (3.40 s on the modelled runtime alone); a larger overrun is cancelled and billed.
- The linearity of the star's trains is a prior from set a18a947f; a rotated calibration set can change the ranking and, with it, the digest.
- The block-dimension law and the complement-law visibility are checked in exact arithmetic on the repository's A_5 tables; their
  novelty is bounded by the code and notes of this repository, and no literature search was made for them.
