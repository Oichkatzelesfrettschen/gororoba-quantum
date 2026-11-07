# Ascella pathion-only four-term block case

This is the written case for one `sim:ascella` job followed by one `qpu:ascella` job of 88 single-photon iterations each. The jobs test whether Ascella's compiled 12-mode mesh realizes the programmed 4 x 4 coset blocks of two A_5 (32-dimensional Cayley-Dickson, "pathion") four-term operands whose block classes occur only at dimension 32, and whether the realized interference levels follow three mutations of those blocks. The client computes every `cd_core` sign and writes it into the programmed unitary, so the result is a conformance record of programmed operator blocks against their exact interference law; it does not show that the chip computes the algebra. Nothing has been submitted: no job, session, upload or credit.

[scripts/ascella_pathion_four_term_blocks.py](../../scripts/ascella_pathion_four_term_blocks.py) builds the frozen requests, [tests/scripts/test_ascella_pathion_four_term_blocks.py](../../tests/scripts/test_ascella_pathion_four_term_blocks.py) checks them, and the requests live in `results/quandela/cases/ascella_pathion_four_term_blocks/` (`sim-00/` and `job-00/`, each with `cases.json` and `circuit.json`). The retained [Ascella A5 kernel slice](ascella-a5-kernel-slice.md) (job 66331d15 on 2026-10-30) is the template: one photon in 8 logical modes on 4 sentinel-padded modes, a fixed Rx/phase mesh with one parameter per free angle, and a matched simulator job before the hardware job.

## Live state

`qd_platforms`, `qd_availability` and `qd_usage` read at about 18:35 UTC on 2026-11-06 (10:35 PST), `qd_platform` for `qpu:ascella` seconds later, and `scripts/qd_platform.py plan` between 18:59 and 19:22 UTC.

| Item | Reading |
|---|---|
| `qpu:ascella` Explorer status | `running` at 18:35 and 18:59 UTC, `calibration` at 19:03 and 19:06 UTC, `running` again at 19:22 UTC (the public list reads `available` throughout); the processor record read `available` at 18:35 and 19:22 UTC and `calibration` at 19:06 UTC |
| Daily availability, 2026-10-30 to 11-06 (%) | 92.03, 92.2, 92.03, 92.13, 91.97, 90.17, 80.43, 91.77 (11-06 partial) |
| Maintenance | none listed for `qpu:ascella` |
| Processor record | 12 modes, at most 6 photons, source-connected inputs 0, 2, 4, 6, 8, 10; clock 13.33 MHz, HOM 89.04 %, g2 2.1 %, transmittance 5.6 %, dark counts 84 to 186 per second on modes 0 to 7 (305 and 319 on modes 8 and 9); platform software perceval-quandela 1.3.0 |
| `sim:ascella` | `available` |
| Account | 0 running and 0 queued jobs against limits of 1 and 1; the platform queue depth needs the dashboard session and is unread |
| `qpu:belenos` | `unreachable`, 0 to 2.19 % availability since 2026-11-02; the case does not use it |

`plan` admits a QPU only when the Explorer row and the processor record read `available`, or `running` when the written case names it with `--admit-status` ([calibration.md](../notes/quandela/calibration.md), gating rules). The retained slice plan admitted `available` and `running`, and this case admits the same two. The QPU job therefore waits while the chip reads `calibration`; an earlier plan at 19:06 UTC under `--admit-status calibration` on a previous build of the same request was a read-only check of the job body under a status this case does not admit, and it submits nothing. The simulator job needs no admission. The MCP `qd_plan` tool cannot name an admitted status and resolves its case directory against the checkout that serves it, so it refused this worktree path ("outside results/quandela/", `not run`); the repository's own `plan` command produced the plan below.

## Credits and the monthly pool

The usage report is cumulative, so the November spend is a difference. The latest retained snapshot, `usage_after` of `results/quandela/runs/2026-10-31T102907Z-qpu_belenos-belenos_mode_swap_interleaved-job-10/results.json`, holds 158 jobs and 174.6941 free credits (collected 2026-10-31T10:34:51Z, before the reset on the 1st). The 18:35 UTC read holds 160 jobs and 176.6941: two `sim:ascella` jobs at 1 credit each (that platform moved from 8 to 10 jobs and from 8 to 10 free credits) ran since that snapshot. The retained records therefore bound the November spend between 0 (both jobs ran before the reset) and 2.0 credits, so the pool of 200 credits per month ([strategy.md](../notes/quandela/strategy.md), section 1) holds between 198.0 and 200.0 before this case. The dashboard stays the authority for the balance (verify before submission).

This case adds 1.0 credit (simulator, 1 credit per job) and 1.032768 credits (QPU: 1 + 1e-6 x 32,768, see Cost), 2.032768 credits in all, so at least 195.97 of the pool remains after it if nothing else spends.

## Mathematics

For a four-term operand p = e_a + s_b e_b + s_c e_c + s_d e_d on a 2-flat (a ^ b ^ c ^ d = 0), the left multiplication L_p maps each coset of the XOR group {0, a^b, a^c, a^d} onto one coset, so L_p is block diagonal with 8 blocks B of size 4 x 4. Every entry of B is +1 or -1, and each block carries 16 independent `cd_core` cocycle signs. Block B maps inputs[c] to outputs[r] with B[r, c] = (coefficient) x `cd_sign(32, term, input)`; `check_against_cd_core` compares every column with `cd_core.cd_multiply_exact` on the basis element.

The 12 equivalence classes of 4 x 4 +-1 matrices under row and column permutations and negations hold 5 classes among the coset blocks at D = 16 and 9 at D = 32, so 4 classes occur only at D = 32. `verify_classes` recomputes both censuses from `cd_core` over every four-term flat (including flats containing e0) and every sign choice, and requires 5, 9 and 4. The independent census `block_classes.py` (a local scratch script over flats of nonzero indices: 528 distinct blocks at D = 16, 2688 at D = 32) agrees: 5 classes, 9 classes, 4 absent at D = 16. The 4 classes new at D = 32 have Gram spectra {0,0,0,16}, {0,0,4,12} (two inequivalent classes) and {0,1.5279,4,10.4721}.

| Operand | Blocks used | Gram spectrum of B^T B | Class | Top level lambda/16 |
|---|---|---|---|---|
| B12 = e1 + e10 + e20 + e31 (nullity 12) | 2 and 7 | {0,0,4,12} | pathion-only, first class | 3/4 |
| B12 | 3 and 6 | {0,0,4,12} | pathion-only, second class (inequivalent to the first) | 3/4 |
| C8 = e1 + e8 + e18 + e27 (nullity 8) | 4, 5, 6, 7 (one class) | {0,1.5279,4,10.4721} | pathion-only | (3 + sqrt 5)/8 = 0.6545 |
| B12 | 0 (reference) | {0,4,4,8} | present at D = 16 | 1/2 |
| A16 = e1 + e10 + e18 - e25 (nullity 16) | 4 (anchor) | {0,0,0,16} | pathion-only, rank 1 | 1 |

The rank-1 class is excluded as a test: every rank-1 +-1 matrix equals the all-ones matrix up to diagonal signs, which a click basis cannot see, so the A16 block is a balanced 4-mode projector that serves only as the bright anchor. The three other pathion-only classes are inequivalent to their own cocycle-free pattern, which is the criterion that makes the readout sensitive to the signs. B12 block 3 is the one exception to sign sensitivity under the cocycle-free mutation: its all-ones level equals its true level (3/4), so block 3 carries no cocycle-free arm.

**Circuit.** V = B/4 is a contraction (spectral norm of any +-1 4 x 4 matrix is at most 4). The Halmos dilation U = [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]], computed by singular value decomposition, is orthogonal to 1e-12. A Householder reflection R with R e_0 = y prepares the input y in modes 0 to 3, so the photon enters source-connected mode 0 and U_tot = U diag(R, I_4). Modes 0 to 3 carry V y (success, label law (V y)^2) and modes 4 to 7 the failure branch, so the algebra level is a = |V y|^2 = y^T B^T B y / 16. Modes 8 to 11 are sentinels. `build_setting` checks, for all 88 settings, that Perceval 1.3.1 SLOS output on the 12-mode unitary equals the analytic law |U_tot[:, 0]|^2 (largest deviation 1.0e-15 against the 1e-9 gate), that the modes 0 to 3 probabilities equal (V y)^2, and that modes 8 to 11 carry none; `template_experiment` then requires the parameterized mesh to reproduce each setting's column and full 12 x 12 operator within 1e-9. The fixed mesh has 148 parameters on modes 0 to 7 and the identity on the sentinels.

## Request

`sim-00/cases.json` sha256 `d65f1675733bfa0e370a0232ce76f01ae3782712bb877b4e2fe76df02d9e7092`; `job-00/cases.json` sha256 `61befd8f8f7bf68f4758127804230142cdfd3943f3a6ef84f76c0dcbbbf053a5`; both `circuit.json` sha256 `8d05c0fcf57c7a2a3a5c7933d5c6ad128d4970cf4119598b4ea0c84bf2795fa2`. The manifests differ in `job` and `platforms` only. `command` is `sample_count`, `min_detected_photons` 1, `mitigations` the explicit empty list, 32,768 samples and at most 32,768 shots per iteration (aggregate 2,883,584 each), `max_duration` 300 s, `max_credits` 1.04. No retry follows a failure.

**Segments.** Each segment holds consecutive iterations on one block under one compilation seed, with arms that mirror about the middle, so the two iterations of each arm repeat one request (same parameters and seed, hence the same served mesh by the retained evidence in [strategy.md](../notes/quandela/strategy.md) section 7, "Per-seed mesh variance of a share") and measure drift directly. Iteration indices are 0-based.

| Segment | Iterations | Block | Arms in order | Seed index |
|---|---|---|---|---|
| anchor-early | 0 to 3 | A16 block 4 | T D D T | 0 |
| reference-b12-0 | 4 to 9 | B12 block 0 | T D F F D T | 1 |
| b12-2 | 10 to 19 | B12 block 2 | T D F C N N C F D T | 2 |
| c8-4 | 20 to 29 | C8 block 4 | T D F C N N C F D T | 3 |
| b12-3 | 30 to 37 | B12 block 3 | T D F N N F D T | 4 |
| c8-5 | 38 to 43 | C8 block 5 | T D F F D T | 5 |
| b12-6 | 44 to 53 | B12 block 6 | T D F C N N C F D T | 6 |
| c8-6 | 54 to 63 | C8 block 6 | T D F C N N C F D T | 7 |
| b12-7 | 64 to 73 | B12 block 7 | T D F C N N C F D T | 8 |
| c8-7 | 74 to 79 | C8 block 7 | T D F F D T | 9 |
| null-b12-2 | 80 to 83 | B12 block 2 | E0 E1 E1 E0 | 10 |
| anchor-late | 84 to 87 | A16 block 4 | T D D T | 0 |

**Arms.** T programs B/4 with the top Gram eigenvector as input (bright, the "+" arm). D programs B/4 with the first rational kernel vector of B (dark, ideal level 0). F flips one sign of the top input, the component whose flip moves the level most (the "-" arm). C replaces B by the cocycle-free all-ones block with the true top input. N negates the one entry of B whose negation moves the level most. E0 and E1 feed basis inputs 0 and 1, which read 1/4 in every four-term block. The sign pair T F F T of a palindrome follows the +, -, -, + order that balances a linear drift, and every mutation arm sits inside that palindrome. Separation is asserted in code: each F, C and N level differs from the block's true top level by at least 0.10 (smallest in this case 0.1667).

**Ideal levels** (exact, from the blocks; the case manifest carries the 8-mode label law of every setting):

| Segment | T | D | F | C | N |
|---|---|---|---|---|---|
| anchor | 1 | 0 | | | |
| reference-b12-0 | 0.5 | 0 | 0 | | |
| b12-2, b12-7 | 0.75 | 0 | 0.25 | 0 | 0.5625 |
| b12-3 | 0.75 | 0 | 0.0833 | omitted (C level equals T) | 0.5833 |
| b12-6 | 0.75 | 0 | 0.0833 | 0.0833 | 0.5833 |
| c8-4 | 0.6545 | 0 | 0.0691 | 0.9472 | 0.4523 |
| c8-5, c8-7 | 0.6545 | 0 | 0.0691 | | |
| c8-6 | 0.6545 | 0 | 0.0691 | 0.0528 | 0.4523 |
| null (E0, E1) | 0.25 each | | | | |

**Seeds.** One fresh ANU QRNG draw of 11 distinct uint16 values, `docs/evidence/anu_qrng/draw-2026-11-06T184402Z.json`, index 0 to 10 as the segment table lists, each used once; the anchor-late segment repeats index 0 so its request equals anchor-early byte for byte. The simulator and hardware cases take the same indices. The case manifest names the draw, so the seed ledger treats the draw as owned by this case (`ci/seed_provenance.py --check` passes).

## Readout

Per iteration, the level a is the share of single clicks in modes 0 to 3 among clicks in modes 0 to 7. Sentinel clicks and invalid events are reported with their denominators. The two iterations of an arm pool into one reading.

With a_dark the mean of every D reading and a_anchor the mean of the four T readings of the two anchor segments, the normalized level is a' = (a - a_dark) / (a_anchor - a_dark). An affine contraction of the success fraction toward a fixed mixture (uniform loss, dark counts, sentinel leakage) leaves a' = lambda/16 unchanged. A branch-dependent loss r = (efficiency of modes 0 to 3)/(efficiency of modes 4 to 7) changes the odds instead; the null arm reads true level 1/4 (odds 1/3), so odds(a_E)/(1/3) estimates r, and the retained slice's half-levels 0.5136 and 0.5187 imply r of 1.055 to 1.078, which moves a true 0.6545 to 0.667 to 0.671. The odds-corrected value is reported beside a'; the decisions use a'.

## Thresholds and decisions (preregistered)

The numbers sit in `cases.json` (`preregistered.thresholds`). Binomial standard error of a pooled arm (about 63,000 samples) is at most 0.0020. The level tolerance 0.07 is 35 times that. It covers the branch-odds shift the retained slice implies (+0.012 to +0.017 on the levels of this case) plus a per-mesh spread of about 0.02 at a level of 1/2; Ascella has no retained per-seed mesh spread for 8-mode blocks (the largest mid-level offset the slice read on hardware was 0.0187 at 10,000 samples, and Belenos 24-mode half blocks spread 0.0515), so the within-class spread below is reported as its estimate and the table below states what each spread does to the decisions. The retained slice read dark 0.0026 and 0.0020, bright 0.9982 and 0.9997 and at most 2.7 % of events on sentinel modes.

**Instrument admission.** The device is admitted when all of these hold:
1. a_anchor >= 0.90 and a_dark <= 0.05;
2. each segment's own dark reading lies within 0.03 of a_dark;
3. the early and late anchor T readings differ by at most 0.03;
4. at most 2 of the 44 repeated arm pairs differ by more than 0.03;
5. sentinel clicks are at most 5 % of the detected events of every iteration;
6. the null levels a(E0) and a(E1) lie within 0.07 of 1/4 and differ from each other by at most 0.07.

A failed condition marks the run `instrument not admitted`; the block readings are then reported and not interpreted. A cut at 300 s that loses the anchor-late segment leaves condition 3 unevaluated, and the verdicts carry that caveat.

**Conformance.** Given admission, the programmed pathion block is realized at its interference level when every T reading of the eight pathion-only blocks lies within 0.07 of its ideal level (3/4 for B12, 0.6545 for C8) and at most 1 of the 18 T and F readings (the eight pathion blocks and the reference block; 10 % of 18 rounded down) lies farther than 0.07 from its ideal level. The reference block, which D = 16 also produces, must conform on both of its readings. Any other pattern refutes "the compiled mesh realizes the programmed four-branch pathion block" at the 0.07 level.

**Mutation sensitivity.** Given admission, each of the 5 C readings (blocks b12-2, c8-4, b12-6, c8-6, b12-7) and 6 N readings (those five and b12-3) must lie within 0.07 of its mutated ideal level. A reading within 0.07 of the block's true top level instead shows that the readout does not follow that sign structure; the arms differ by at least 0.1667 from the true level, so the two windows never overlap. A conformance pass with a mutation failure supports realized levels without showing that they depend on the cocycle signs.

**Mesh spread (reported, no verdict).** The T readings of the four B12 blocks (two per class) and of the four C8 blocks give the spread across compiled meshes of one ideal level; a range above 0.07 within a class reads "mesh variance exceeds the tolerance" and withholds a per-block verdict.

**Decision-chain power.** `"$PYTHON" scripts/ascella_pathion_four_term_blocks.py --power` computes, by quadrature over mesh-angle errors, the probability that each decision passes when every distinct (segment, arm) mesh carries an independent angle error whose effect on a level at 1/2 has standard deviation sigma. The readout model takes the retained slice's dark floor 0.0023 and bright leak 0.0017 and a branch odds ratio of 1.07 (binomial error, at most 0.002, is omitted against the 0.07 tolerance). A scratch Monte Carlo of binomial cells at 31,800 events per iteration agreed with the quadrature within 0.015 on the joint pass probability; it is not retained.

| sigma | admission (null gate binds) | conformance | mutation | all three |
|---|---|---|---|---|
| 0.005 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.010 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.020 | 0.993 | 0.991 | 0.981 | 0.965 |
| 0.030 | 0.913 | 0.843 | 0.802 | 0.617 |
| 0.040 | 0.776 | 0.532 | 0.525 | 0.217 |

An ideal-realizing device with a mesh spread of 0.02 or less passes all three decisions at least 96 % of the time, so a failure at that spread refutes realization at the 0.07 level. At 0.03 to 0.04 an ideal device fails often (pass probability 0.62 to 0.22), so a failure is read together with the within-class T spread: a spread of 0.05 or more attributes the failure to mesh variance and withholds the refutation. The tolerance was raised from 0.05 to 0.07 for this reason; with the earlier tolerance 0.05 and null spread 0.03 the scratch Monte Carlo gave an all-pass probability of 0.44 at sigma 0.02.

**Outcomes.** All three pass: the retained evidence is an instrument-conformance record of programmed pathion-only block structure on this chip and day, and a second case (the remaining D = 16-class blocks and the eigenvalue ladder inputs, all 32 basis inputs per operand) becomes worth writing. Conformance fails with the instrument admitted: the record localizes the failure by class and seed and no remedy run starts without a new written case. A simulator result that departs from the ideal laws by more than 0.01 on any level stops the sequence before the QPU job.

## Why a simulation cannot answer it

The question concerns the physical mesh, which the service compiles from the circuit parameters and a seed into heater phases: the observable moves per seed far beyond binomial error ([strategy.md](../notes/quandela/strategy.md) section 7), and the retained slice read 0.5136 and 0.5187 on hardware against 0.502 and 0.498 on `sim:ascella` for the same ideal 1/2, with up to 2.7 % of events on sentinel modes that the simulator left empty. The local Perceval SLOS run proves the ideal laws and the unitary convention only. The matched `sim:ascella` job is the software-model control; its role is to confirm client and simulator conformance before hardware time is spent, not to predict the device.

## Cost

Per-iteration time on Ascella is 3.0 to 3.2 s for one photon and shows no dependence on samples up to 65,536 per iteration: 88 iterations of 32,768 samples took 265 s (2026-10-26), 96 took 288 and 289 s, and 84 iterations of 10,000 samples took 248 s. The packing rule k = floor(0.9 x 300 / 3.0) admits 90 iterations; this case runs 88, the set of arms that discriminate (B12 block 3 omits its cocycle-free arm), for an expected 264 s on the QPU, 36 s inside the 300 s cut, and about 60 s on `sim:ascella` (retained simulator jobs ran 0.7 s per iteration at 32,768 samples). A cut at 300 s would lose the final anchor-late segment first.

Billing follows 1 + 1e-6 x min(shots used, largest iteration max_shots) on the retained Ascella jobs, and one-photon shots equal samples. The QPU job bills 1 + 1e-6 x 32,768 = 1.032768 credits; the simulator job bills 1.0. `plan` agrees: estimated shots 2,883,584, credit ceiling 1.0 (`sim:ascella`) and 1.032768 (`qpu:ascella`), payload version 2 (declared commands), body sha256 `b0113f2c97e8c3d64229e1a0f697473045284aca6dcbaa1e57f0c27d2b22c184` for the simulator (2026-11-06, 19:21 UTC, Explorer and processor `available`) and `dff6ed06df16037d6487da7a90fc6d824df26d13bef600680609145df6118842` for the QPU (19:22 UTC, Explorer `running`, processor `available`, admitting `running`). Planning arguments: `--max-credits 1.04 --expected-seconds 264 --per-job-credits 1`.

## Execution

On the owner's approval of this case: submit `sim-00` on `sim:ascella`, collect it and compare every level with the ideal laws; then, with the Explorer row and processor record both `available` (or `running`, which this case admits), run `plan` again on the bytes above and submit `job-00` on `qpu:ascella` with the approval text, then collect. The binding plan at submission replaces the plan quoted here.

## Not run

No job, session, upload or credit. Local Perceval SLOS runs and the repository `plan` command (read-only network calls) are the only executions against Quandela services. Not run, with reasons:
- the MCP `qd_plan` tool: it refused the worktree path (it resolves case directories against the checkout that serves it);
- a QPU plan while the Explorer row reads `available`: both QPU plans on these bytes read `running`;
- the dashboard balance and the platform queue depth, which need the dashboard session;
- an analysis and collection script for the returned runs (the kernel slice has `ascella_a5_kernel_analysis.py`); the readout section and thresholds above fix what it computes;
- the full `sh ci/pr_checks.sh tests` lane (the targeted tests of this case and the kernel slice ran, with `ruff`, `mypy`, `ci/seed_provenance.py --check`, `scripts/check_markdown_links.py` and `scripts/hypercomplex_libraries.py --check`);
- Belenos, which is `unreachable`;
- the 32-input resolution of each operand and the eigenvalue-ladder inputs, outside this case.
