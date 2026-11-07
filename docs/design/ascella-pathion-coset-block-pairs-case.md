# Ascella two-coset-block pathion case

This is the written case for one `sim:ascella` job followed by one `qpu:ascella` job of 52 single-photon iterations each. Every iteration shares one photon between two 4 x 4 coset blocks of the A_5 (32-dimensional Cayley-Dickson, "pathion") four-term operands, on 9 of Ascella's 12 modes. The jobs test four things: whether the compiled mesh realizes two programmed blocks at their interference levels at one common scale, whether the blocks leak into each other (crosstalk and independence arms), whether each block reads the same level in either half of the mode set, and whether the predecessor's C8 spread (blocks 4, 5 and 6 read about 0.024 low, block 7 about 0.023 high) follows the block or the mode slot. The client computes every `cd_core` sign and writes it into the programmed unitary, so a result is a conformance record of programmed operator blocks against their exact interference law; it does not show that the chip computes the algebra. The jobs ran on 2026-11-07: `sim:ascella` job `64b1ba77-7f79-4f2f-a1c1-37740eeecf2a` (`results/quandela/runs/2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00`) and `qpu:ascella` job `db6355f7-87d5-4e7a-91f5-b898c33c839a` (`results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00`), both completed; the scored records are the `analysis.json` files beside each run.

[scripts/ascella_pathion_coset_block_pairs.py](../../scripts/ascella_pathion_coset_block_pairs.py) builds the frozen requests, [scripts/ascella_pathion_coset_block_pairs_analysis.py](../../scripts/ascella_pathion_coset_block_pairs_analysis.py) scores a collected run, [tests/scripts/test_ascella_pathion_coset_block_pairs.py](../../tests/scripts/test_ascella_pathion_coset_block_pairs.py) and [its analysis test](../../tests/scripts/test_ascella_pathion_coset_block_pairs_analysis.py) check them, and the requests live in `results/quandela/cases/ascella_pathion_coset_block_pairs/` (`sim-00/` and `job-00/`, each with `cases.json` and `circuit.json`). The case is the successor of the [pathion-only four-term block case](ascella-pathion-four-term-blocks-case.md), whose digest-bound script, case directories and retained run stay unchanged; the new script imports its block census, arm programs and `cd_core` checks.

## What the fold buys

The fold changes the number of reconfigurations, not the number of samples. A fold level is read as twice a click share, so its binomial variance is L (2 - L) / n against L (1 - L) / n for a block read alone, a factor (2 - L) / (1 - L) of 5 at L = 3/4 and 3.9 at L = 0.6545. Equal per-block error would take about five times the samples per iteration (163,840 against 32,768), above the 156,159 shots per iteration that any retained Ascella job measured; the case uses four times (131,072), which reads each block to within 12 % of the predecessor's standard error, and bills 1.131072 credits against 1.032768. The analysis reports the standard error of each calibrated level by the delta method through the dark subtraction and the efficiency calibration, with the dark and anchor counts included (`level_errors`), not this planning variance. What the fold saves is reconfigurations per block reading: each of the 46 pooled block-item readings comes from two iterations that read two blocks each, where the predecessor spent every iteration on one block, and the freed time inside the 300 s cut pays for the slot swap, the crosstalk arms and the independence arms. The fold is one job on each platform, as the predecessor was, so it saves no runs.

## Live state

`qd_platforms`, `qd_availability`, `qd_usage` and `qd_platform` for `qpu:ascella` read at about 23:15 UTC on 2026-11-06 (15:15 PST), and `scripts/qd_platform.py plan` at 23:30 and 23:31 UTC.

| Item | Reading |
|---|---|
| `qpu:ascella` Explorer status | `running` (the public list reads `available`); the processor record reads `available` |
| Daily availability, 2026-10-30 to 11-06 (%) | 92.03, 92.2, 92.03, 92.13, 91.97, 90.17, 80.43, 88.82 (11-06 partial) |
| Maintenance | none listed for `qpu:ascella` |
| Processor record | 12 modes, at most 6 photons, source-connected inputs 0, 2, 4, 6, 8, 10; clock 13.33 MHz, HOM 88.88 %, g2 2.1 %, transmittance 5.57 %, dark counts 184, 89, 77, 81, 81, 122, 88, 113, 260, 304, 125, 141 per second on modes 0 to 11; platform software perceval-quandela 1.3.0 |
| `sim:ascella` | `available` |
| Account | 0 running and 0 queued jobs against limits of 1 and 1; the platform queue depth needs the dashboard session and is unread |

`plan` admits a QPU on `available`, or on `running` when the case names it with `--admit-status`; this case admits both, as the predecessor did. The MCP `qd_plan` tool resolves case directories against the checkout that serves it and refuses this worktree, so the repository's `plan` command produced both plans (`not run`: the MCP tool).

## Credits and the monthly pool

The usage report is cumulative: 163 jobs and 179.7596 free credits across the four platforms at about 23:15 UTC, against 160 jobs and 176.6941 at the 18:35 UTC read that the predecessor case cites. The spend since the reset is bounded by the retained snapshots in that case's "Credits and the monthly pool" section, and the dashboard stays the authority for the balance (verify before submission). This case adds 1.0 credit (simulator job) and 1.131072 credits (QPU: 1 + 1e-6 x 131,072, billed on the largest iteration's `max_shots`), 2.131072 credits in all, against the pool of 200 credits per month ([strategy.md](../notes/quandela/strategy.md), section 1).

## Mathematics

**Blocks.** For a four-term operand p on a 2-flat, L_p is block diagonal with 8 blocks B of size 4 x 4 and entries +1 or -1 ([predecessor case](ascella-pathion-four-term-blocks-case.md), "Mathematics"). The nine sign-carrying blocks are the D = 16 reference B12 block 0 and the eight pathion-only blocks B12 blocks 2, 3, 6 and 7 and C8 blocks 4, 5, 6 and 7; `verify_classes` re-derives the census (5 classes at D = 16, 9 at D = 32, 4 only at D = 32, [census.json](../evidence/pathion-kernel-map/census.json)). The fourth pathion-only class, the rank-1 A16 blocks 4 to 7, reads the same in any click basis, so A16 blocks 4 and 5 serve only as the bright anchor and as a kernel input. Every arm of the predecessor applies: T (top Gram eigenvector, the "+" arm), F (one flipped input sign, "-"), C (cocycle-free all-ones block with the true top input), N (the entry whose negation moves the level most negated), D (kernel input, ideal 0) and E0 and E1 (basis inputs, ideal 1/4 in every four-term block). `resolve` checks the level of each T, D, F and E arm against the full 32-dimensional product from `cd_core.left_mult_matrix`, and `check_against_cd_core` checks every block column against `cd_multiply_exact`.

**One photon over two blocks.** Block X in slot A (modes 0 to 3) and block Y in slot B (modes 4 to 7) take the amplitudes (B_X y_X, B_Y y_Y) / (4 sqrt 2), where y is the arm's unit input vector and 1/4 is one scale for both blocks, so each block reads its own level L = |B y|^2 / 16 as twice its click share, and the remainder of the photon, amplitude sqrt(1 - (L_A + L_B) / 2) on mode 8, is the failure branch. A 9 x 9 Householder reflection R with R e_0 = (psi, failure amplitude) carries the photon from source-connected mode 0 to that column, and modes 9 to 11 stay sentinels under the identity. `build_iteration` checks, for every iteration, that Perceval 1.3.1 SLOS on the 12-mode unitary equals the analytic law |U[:, 0]|^2 to 1e-9, that each slot's modes carry exactly its block's squared amplitudes divided by two, that mode 8 carries the failure share and modes 9 to 11 carry none; `template_experiment` then requires the parameterized triangular mesh (189 parameters on modes 0 to 8) to reproduce each column and full operator within 1e-9. In the ideal circuit the two slots are orthogonal mode sets, so crosstalk and independence are zero by construction: those arms test the device's unitary, and the SLOS agreement proves the arithmetic only. `sim:ascella` is noiseless (the predecessor's simulator job read anchor 1.0, dark 0.0 and every spread 0.0) and checks the client and pipeline; neither it nor the SLOS check is fidelity evidence, and only the QPU job tests the fold.

**Per-slot references.** A programmed 50/50 split error between the blocks moves L_A and L_B in opposite directions, and crosstalk and independence arms cannot separate it from a level error. Each slot therefore carries its own references, in the same job, on the same slots the sign blocks use:
- Anchor: A16 block 4 at ideal level 1 in the slot under test with a kernel input of A16 block 5 in the other slot. The slot holds half the photon and the failure mode half, so the dark-subtracted level is a* = 2 r / (1 + r) and r = a* / (2 - a*) is the slot's efficiency relative to the failure mode. The anchor runs in both slot orientations, early and late.
- Dark: kernel inputs in both slots, so the photon sits in the failure mode and every slot click is leakage; its share d of the labeled clicks is the slot's dark. The kernel slot of the anchor and of the T/D settings is a second dark reading beside a bright partner (the crosstalk null).
- Swap: every sign setting runs once in each slot orientation, so each block item reads against slot A's references and against slot B's, and the item's pooled level averages the two.

**Levels.** The raw level is a = 2 x (clicks in the slot's four modes) / (clicks in modes 0 to 8). The calibrated level l = 2 (n* / r_s) / (n*_A / r_A + n*_B / r_B + n_failure) divides each slot's dark-subtracted clicks n* by its efficiency r before forming the ratio; it removes the denominator coupling that makes A's raw reading depend on B's arm when r differs from 1 (at r = 1.076 the raw level of a C8 T block moves by about 0.007 when its partner, C8 block 4, switches from T to C). The predecessor's normalized level a' = (a - a_dark) / (a_anchor - a_dark) is reported beside it with the slot's own anchor and dark; a' reads about 0.015 low at C8 T when r = 1.076, where the predecessor's branch-odds shift read 0.012 to 0.017 high, so absolute levels are not compared across the two cases and the C8 test below uses within-class contrasts.

## Request

`sim-00/cases.json` sha256 `837f6bd6422dffb922798fa8c38deefe1c15ab4905966a52ec1beba57a3cd89c`; `job-00/cases.json` sha256 `63e270d72df8f3faad285244df062717d0688515f997f42086764890febe19fa`; both `circuit.json` sha256 `8f34c960de556007b5e3405cc0b190c97876f6baf9bab46aa25728e9f5e196aa`. The manifests differ in `job` and `platforms` only. `command` is `sample_count`, `min_detected_photons` 1, `mitigations` the explicit empty list, 131,072 samples and at most 131,072 shots per iteration (aggregate 6,815,744 each), `max_duration` 300 s, `max_credits` 1.14. No retry follows a failure.

**Sequence.** The 25 distinct settings (anchor, dark, 22 sign settings and the null) take one compilation seed each; the two slot orientations of a setting share it. The setting order is a palindrome: anchor (slot orientation 0), anchor (orientation 1), dark, the 23 sign and null settings in the order below with alternating first orientation, the same 23 settings in reverse order with the orientation swapped, dark, anchor (1), anchor (0). The mirrored anchor and dark requests are identical, so their early and late readings measure drift directly. Blocks are written by code: a = B12/0 (D = 16 reference), b = B12/2, c = B12/3, d = B12/6, e = B12/7, f = C8/4, g = C8/5, h = C8/6, i = C8/7. Iteration positions run 0 to 51; positions 3 to 25 hold the first half and 26 to 48 the mirror, the null at the center (positions 25 and 26).

| Setting | Item 0 | Item 1 | Purpose |
|---|---|---|---|
| i-f-TT, i-f-TD, i-f-TC, i-f-TN | i T | f T, D, C, N | C8 independence group (item 0 fixed at T); T/T is the high-versus-low swap pair; TD is a crosstalk null |
| c-d-TT, c-d-TD, c-d-TC, c-d-TN | c T | d T, D, C, N | B12 independence group of class {3, 6} |
| e-b-TT | e T | b T | B12 class {2, 7} swap pair |
| g-h-TT | g T | h T | C8 control pair (two blocks the predecessor read low) |
| b-i-CC, e-g-CN, b-i-NN, e-c-NN, a-g-TC, a-h-CC, a-h-NN | | | remaining C and N arms of every block (B12 block 3 has no C arm: its cocycle-free level equals T) |
| e-h-FT, d-i-FF, a-f-FF, b-g-FF, c-h-FF | | | remaining F arms; e-h-FT also reads h at T |
| b-f-EE | b E0 | f E1 | null: both blocks read 1/4 with 3/4 of the photon in the failure mode |

Settings carrying block 7 items (e, i) come early; the mirror puts each setting at the matching late position, so every block's mean job position equals the job midpoint and the predecessor's confound (both block-7 segments ran last) is removed. Every sign block carries T, F and N and, except block c, C; the same-class T/T pairs are (i, f), (e, b), (c, d) and (g, h); `check_coverage` and `check_sequence` assert all of this.

**Ideal levels** (exact, from the blocks): T 3/4 for B12 blocks 2, 3, 6 and 7, 1/2 for the reference, (3 + sqrt 5) / 8 = 0.6545 for C8; F 0.25 (B12 blocks 2 and 7), 0.0833 (blocks 3 and 6), 0 (reference), 0.0691 (C8); C 0 (all B12 and C8 blocks 5 and 7, reference), 0.0833 (block 6), 0.0528 (C8 block 6), 0.9472 (C8 block 4); N 0.5625 (blocks 2, 7), 0.5833 (blocks 3, 6), 0.375 (reference), 0.4523 (C8); E 0.25; D 0; anchor T 1. `"$PYTHON" scripts/ascella_pathion_coset_block_pairs.py --ideal` prints every item. Each F, C and N level differs from its block's true top level by at least 0.10 (asserted).

**Seeds.** One fresh ANU QRNG draw of 25 distinct uint16 values, `docs/evidence/anu_qrng/draw-2026-11-06T230523Z.json`, index 0 for the anchor, 1 for the dark and 2 to 24 for the 23 sign and null settings in first-half order, each used once; the case manifest names the draw, so the seed ledger treats the draw as owned by this case. A seed in a new case answers the new case's own question: the predecessor's circuits (8-mode Halmos blocks) differ from these (9-mode Householder pairs), so no predecessor seed reproduces a predecessor mesh here. The simulator and hardware cases take the same indices.

## Readout, thresholds and decisions (preregistered)

The numbers sit in `cases.json` (`preregistered.thresholds`). Per iteration the analysis counts single clicks in slot A (modes 0 to 3), slot B (4 to 7), the failure mode 8 and the sentinels 9 to 11; invalid events and sentinel clicks are reported with their denominators. Two orientations of an item pool by averaging their calibrated levels.

**Binomial error.** A level L read as twice a share carries variance L (2 - L) / n. One iteration of 131,072 samples reads L = 3/4 to 0.0027, 0.6545 to 0.0026, 1/2 to 0.0024 and 1/4 to 0.0018; a pooled item (two iterations) reads 0.0019, 0.0018, 0.0017 and 0.0013. The predecessor's pooled arms read 0.0017 to 0.0019, so the case holds the predecessor's per-block error. The sample count is sized to that error, not to the conformance tolerance: 0.07 needs about 0.005 only, and 131,072 buys the resolution that the spread test below uses.

**Instrument admission.** The device is admitted when all of these hold:
1. each slot's bright anchor raw level is at least 0.90 and its dark raw level at most 0.05;
2. the early and late anchors of each slot differ by at most 0.03, and the early and late darks of each slot by at most 0.03;
3. sentinel clicks are at most 5 % of the events of every iteration;
4. the two null readings lie within 0.07 of 1/4 and differ from each other by at most 0.07;
5. at most 10 % (rounded down) of the pooled block readings differ between the two slot orientations by more than 0.07.

A failed condition marks the run `instrument not admitted`; the block readings are then reported and not interpreted, except the C8 spread, which is reported whatever the admission. A cut at 300 s that loses the late anchors leaves conditions 2 unevaluated and the verdicts carry that caveat; a cut that loses the early anchors or dark stops the scoring.

**Conformance.** Given admission, every T reading (16 pooled readings) lies within 0.07 of its ideal level and at most floor(0.10 x 25) = 2 of the T and F readings (25) lie farther.

**Mutation sensitivity.** Given admission, each of the 8 C and 9 N readings lies within 0.07 of its mutated ideal level; a reading within 0.07 of the block's true top level instead shows that the readout ignores that sign structure (the arms differ by at least 0.1667 from the true level, except the reference block's N arm at 0.125, whose window overlaps the true level's by 0.015).

**Crosstalk.** Given admission, the dark slot beside a bright partner (ideal level at least 0.5: the four anchor iterations and the four iterations of the two T/D settings) reads at most 0.03 above that slot's own dark reading. The sentinel-scale comparison (the sentinel share of the iteration times 2 x 4/3, for 4 slot modes against 3 sentinel modes) is reported beside it. The definition is differential because a kernel input leaks about 0.35 % to 0.44 % of the clicks into the slot even with no second block lit (the predecessor's two anchor-segment dark arms read raw levels 0.0044 and 0.0035 against sentinel shares of 0.0025 and 0.0019), so an absolute null below the sentinel share would fail a clean device; a synthetic leaky-but-ideal return passes (tests).

**Independence.** Given admission, the calibrated level of each group's fixed T block ranges at most 0.07 over the partner arms T, C, N and D. The uncalibrated range is reported beside it; the calibration absorbs the coupling through the shared failure mode.

**C8 spread (preregistered, reported whatever the admission).** For each slot the contrast is the mean deviation of C8 block 7's T readings minus the mean of the mean deviations of blocks 4, 5 and 6 (deviation = calibrated level minus 0.6545). The predecessor's contrast, from its retained `analysis.json` (sha256 in `cases.json`), is +0.0470 (deviations -0.0234, -0.0253, -0.0241 and +0.0227). The spread reproduces in a slot when that slot's contrast is at least half the predecessor's, 0.0235. Both slots reproduce: the spread follows the block. Exactly one slot reproduces (the other reads below the threshold or reversed): it follows the mode slot. Neither: not reproduced. The same-class T/T settings (i-f-TT, g-h-TT, e-b-TT, c-d-TT) give the clean 2 x 2: the difference between the two blocks keeps its sign across the swap for a block effect and flips for a slot effect. A maximum-likelihood fit of one efficiency per mode 0 to 8 to all returned counts is reported with the contrast it reproduces, since a per-mode efficiency pattern is the mechanism by which a slot-following spread would arise.

**Power of the spread test.** The block-7 cell and the three low cells are one-iteration readings with variance L (2 - L) / n each plus an assumed mesh variance sigma^2, so the contrast has standard deviation sqrt((0.0026^2 + sigma^2) x 4/3). With no mesh variance it is 0.0030 and the threshold sits 7.8 sigma below the predecessor's effect. The verdict "follows the mode slot" is exactly one slot clearing the threshold, so the test misattributes a block effect to the slot, or reports a slot effect where none exists, at the rate 2 p (1 - p) for the one-slot probability p:

| sigma per cell | contrast sd | one slot reproduces, effect present | both slots, present | one slot, effect absent | exactly one slot (misattribution), present or absent |
|---|---|---|---|---|---|
| 0 | 0.0030 | 1.000 | 1.000 | 0.000 | 0.000 |
| 0.005 | 0.0065 | 0.9998 | 0.9997 | 0.0002 | 0.0003 |
| 0.01 | 0.0119 | 0.976 | 0.952 | 0.025 | 0.048 |
| 0.02 | 0.0233 | 0.843 | 0.711 | 0.157 | 0.264 |

At sigma 0.01 the block verdict is right 95 % of the time under a block effect and the false slot verdict is 5 %; at sigma 0.02 a quarter of runs carry the wrong attribution whichever hypothesis holds, so a "follows the mode slot" verdict at that spread is read together with the same-class T/T pair (a slot effect flips the block 7 minus block 4 difference across the swap, a block effect keeps its sign). The predecessor's B12 within-class T readings, which carry no spread under test, estimate sigma independently: class {2, 7} differs by 0.015 and class {3, 6} by 0.004, which gives sigma of about 0.008 (the difference of two cells has standard deviation sigma x sqrt 2, and the estimate includes the binomial part, so it is an upper bound). Blocks 4, 5 and 6 agreeing to 0.002 is the effect under test and carries no information on sigma. `"$PYTHON" scripts/ascella_pathion_coset_block_pairs.py --power` prints the table; the block 7 cells have several readings (four for block i) that shrink their share of sigma.

**Outcomes.** All decisions pass and the spread reproduces in both slots: the retained evidence is a conformance record of two programmed blocks per photon with no measurable crosstalk, and the C8 spread follows the block's sign pattern and input vector, independent of the dilation (this case programs a 9 x 9 Householder pair, the predecessor an 8 x 8 Halmos dilation) and of the slot. The spread reproduces in one slot: the mode slot carries it, and a case on the per-mode efficiencies follows. Not reproduced: the spread was specific to the predecessor's dilation and compile, or to that day, and this case does not separate the two. A failure localizes by setting and block; no remedy run starts without a new written case. A simulator level that departs from its ideal by more than 0.01 on any pooled reading stops the sequence before the QPU job; this gate checks the client and pipeline only.

## Why a simulation cannot answer it

The question concerns the physical mesh, which the service compiles from the circuit parameters and a seed into heater phases, and whether two blocks sharing one photon read independently on it. `sim:ascella` is noiseless, so it returns the ideal law and says nothing about crosstalk, the slot swap or the C8 spread; the local Perceval SLOS run proves the ideal laws and the unitary convention only. The matched `sim:ascella` job is the software-model control: it confirms that the client, the template binding, the scoring path and the mirror bookkeeping close on the ideal laws before hardware time is spent.

## Cost

Per-iteration time on Ascella is about 3 s in every retained job: 10,000 one-photon samples (job 66331d15, 6 iterations in 18 s), 32,768 (job f3a11b5f, 88 iterations in 266 s) and 65,536 (five iterations in 16 s), and 156,159 two-photon shots (job ae37fae6, 3.1 s per iteration). The 131,072 shots per iteration of this case lie inside that measured shot range, and the measured 3.1 s at 156,159 shots bounds the throughput below by 48,000 shots per second, so 131,072 shots need at least 2.7 s of the 3.2 s the case budgets; `check_duration` asserts that the shot count stays in the measured range, that the throughput floor sits below the budgeted iteration time, and that the iterations fit floor(0.9 x 300 / 3.2) = 84. Expected seconds 52 x 3.2 = 166.4 on the QPU (133.6 s inside the cut) and about 60 s on `sim:ascella` (retained simulator jobs ran 0.7 to 0.8 s per iteration at 32,768 samples; the simulator at 131,072 samples is unmeasured and 60 s is a bound the 300 s cut covers five times). A cut at 300 s would lose the mirrored anchors first.

Billing follows 1 + 1e-6 x the largest iteration `max_shots` on an iterated job ([runbook](../runbooks/quandela-credit-optimization.md), "The billing rule"): the QPU job bills 1 + 1e-6 x 131,072 = 1.131072 credits; the simulator job bills 1.0. `plan` agrees: estimated shots 6,815,744, credit ceiling 1.0 (`sim:ascella`) and 1.131072 (`qpu:ascella`), payload version 2 (declared commands), body sha256 `a9fd69effdddb68ef34a726a67f847d06f1132f28508dcede0140db905e65282` for the simulator (2026-11-06 23:30 UTC, Explorer and processor `available`) and `be6894ff64e30f95fada48cf22b3b6d345e30c64f02541a22538ea50e8d048b5` for the QPU (23:31 UTC, Explorer `running`, processor `available`, admitting `running`). Planning arguments: `--max-credits 1.14 --per-job-credits 1 --admit-status running` with `--expected-seconds 60` (simulator) and `166.4` (QPU).

## Execution

On the owner's approval of this case, with `PYTHON` set and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` exported:

```sh
C=results/quandela/cases/ascella_pathion_coset_block_pairs
"$PYTHON" scripts/qd_platform.py submit --platform sim:ascella --max-credits 1.14 --expected-seconds 60 \
  --per-job-credits 1 --admit-status running --approval "<the owner's approval, quoted>" "$C/sim-00"
"$PYTHON" scripts/qd_platform.py collect RUN_DIR_OF_SIM
"$PYTHON" scripts/ascella_pathion_coset_block_pairs_analysis.py RUN_DIR_OF_SIM --sim-gate
"$PYTHON" scripts/qd_platform.py plan --platform qpu:ascella --max-credits 1.14 --expected-seconds 166.4 \
  --per-job-credits 1 --admit-status running "$C/job-00"
"$PYTHON" scripts/qd_platform.py submit --platform qpu:ascella --max-credits 1.14 --expected-seconds 166.4 \
  --per-job-credits 1 --admit-status running --approval "<the owner's approval, quoted>" "$C/job-00"
"$PYTHON" scripts/qd_platform.py collect RUN_DIR_OF_QPU
"$PYTHON" scripts/ascella_pathion_coset_block_pairs_analysis.py RUN_DIR_OF_QPU --out RUN_DIR_OF_QPU/analysis.json
```

`submit` prints the run directory under `results/quandela/runs/`. The simulator gate exits 1 unless every pooled reading sits within 0.01 of its ideal and every iteration returned; on exit 1 the QPU job does not start. The QPU job runs while the Explorer row and the processor record read `available` or `running`; the binding plan at submission replaces the plan quoted here.

## Not run

Both jobs of the case ran (header). Local Perceval SLOS runs and the repository `plan` command (read-only network calls) preceded them. Not run, with reasons:
- the MCP `qd_plan` tool: it resolves case directories against the checkout that serves it and refuses this worktree path;
- the dashboard balance and the platform queue depth, which need the dashboard session;
- an interpretation of the returned runs, which lands in a later change: the analysis path and its tests cover ideal, uniformly contracted, per-slot-efficiency, leaky, crosstalk, independence-breaking, block-following and slot-following spread, flipped-block, mutation-failure, drift, slot-bias, sentinel, null, cut and request-mismatch synthetic returns only;
- an overall pass probability of the decision chain under mesh spread (the predecessor's `--power` quadrature has no counterpart here; the spread test's power is stated above);
- the full `sh ci/pr_checks.sh tests` lane (the targeted tests ran under the host interpreter, which differs from the hosted pins);
- a measurement of the iteration time at 131,072 samples: the budget rests on the retained 3 s per iteration up to 156,159 shots, and the first QPU iterations are the measurement.
