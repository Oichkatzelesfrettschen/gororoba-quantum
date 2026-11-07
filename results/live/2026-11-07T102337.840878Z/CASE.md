# Written case: whole-operand nullity of two-term operands of the 64- and 128-dimensional Cayley-Dickson algebras on ibm_fez and ibm_kingston

Status: awaiting the owner's approval. Each run is a binding dry run and `--submit` back to back through
`scripts/approved_run.sh` with `scripts/pathion_wide_coset_check.py` as its check. Nothing is submitted, booked or
charged until the owner approves this case. This file is the case for both runs; the file of the same name beside the
ibm_kingston binding dry run holds that run's rows and points here.

Source of numbers. Model values come from the `record.json` of each binding dry run (`summary`,
`summary_readout_corrected` and `placed_qubit_calibration` of the group), the noise-model prediction on that device's
live calibration, and this case cites them only as predictions ("model"). Model standard errors come from the same laws
through `scripts/pathion_wide_coset_analysis.py` (the delta-method interval below) at the planned shots. Measured values
will come from `collect.json` of the submitted job: the pooled summary and its readout-corrected counterpart, and the
analysis script's per-placement recomputation.

## What it measures

A two-term operand e_i + t e_j of A_n (D = 2^n) has a kernel map whose SELECT tiles into D / 8 independent four-qubit
blocks, one per coset of a 3-dimensional subspace V that contains m = i XOR j (`pathion_coset_block.py`, taking the
dimension D). The aligned XOR pairs of block b number N_b, the blocks sum to the nullity of L_(e_i + t e_j), and
`cd_core` certifies that nullity from the integer rank (python-flint `fmpz_mat`) on every operand. The census
(`docs/evidence/pathion-kernel-map/census-wide.json`) finds no block class that first occurs at D = 64 or D = 128: the
same five two-term classes (N_b = 0 to 4) and nine four-term classes occur at every dimension. The quantity new above
D = 32 is the operand nullity, 16 to 28 at D = 64 and 32 to 60 at D = 128. The case reads the whole nullity of a
maximal-nullity operand at each dimension, 28 of 64 over 8 blocks (32 qubits) and 60 of 128 over 16 blocks (64
qubits), with a null control and a mutation arm per dimension, on two devices.

Group `pathion_wide_coset` (ibm_kingston) and its variant `pathion_wide_coset_d32` (ibm_fez), both from
`gororoba_quantum/pathion_wide_coset.py`, hold twelve members, one per arm of each operand. Each member is one fused
PUB, and every placement of that PUB runs a different four-qubit block with its own ideal law, compiled body and coupler
set (`Group.per_placement_laws` in `gororoba_quantum/experiments.py`). Placement p of the 16 operand placements runs the
p-th coset of the operand, in ascending order, modulo its block count, for every operand at once.

| Operand | Role | Nullity (cd_core) | Blocks | Placements per block | N_b of the blocks (ideal) | Ideal sum of N_b |
|---|---|---:|---:|---:|---|---:|
| `o64` e1 + e36 | target | 28 of 64 | 8 | 2 | 2, 2, 4, 4, 4, 4, 4, 4 | 28 |
| `o128` e4 + e72 | target | 60 of 128 | 16 | 1 | 3, 3, 3, 3, 4 (twelve times) | 60 |
| `n64` e1 + e33 | null control | 0 | 8 | 2 | 0 (eight times) | 0 |
| `n128` e1 + e65 | null control | 0 | 16 | 1 | 0 (sixteen times) | 0 |
| `m64` cocycle-free tiling of e1 + e36 | mutation | 28 | 8 | 2 | 0, -2, 0, 0, 0, 0, 0, 0 | -2 |
| `m128` cocycle-free tiling of e4 + e72 | mutation | 60 | 16 | 1 | 4, -4, 2, -4, then 4, -4 alternating | -2 |

Both targets have the largest nullity of any two-term operand at their dimension and a block structure that differs
(N_b = 2 and 4 at D = 64; 3 and 4 at D = 128), so the classes N_b = 2, 3 and 4 enter through the targets and N_b = 0
through the null controls; N_b = 1 occurs only in mid-nullity operands, which the budget leaves out. The null controls
have the shape of e1 + e17 of A_5 (m = D / 2, the highest bit). The mutation replaces every L_m of the SELECT by its
unsigned XOR permutation, so the sign pattern the cocycle supplies vanishes while the circuit keeps the same oracle;
its ideal sum is -2 where the true tiling sums to 28 and 60 (separations 30 and 62). Every block of every operand
equals the module's full-map law on its output coset (`restriction_error` below 1e-12 for both arms and the mutation;
`tile` covers all D algebra indices once and its aligned counts sum to the cd_core nullity).

## Design

- Simultaneity achieved. One PUB reads the whole block set of one operand arm in one shot: the 16 blocks of `o128`,
  `n128` or `m128` occupy the 16 placements, and the 8 blocks of a 64-dimensional operand run twice. The whole-operand
  nullity is the sum over the blocks of one shot, so no drift between PUBs enters a block-to-block sum. The plus and
  minus arm of every block sit on the same placement in two PUBs, since the contrast c(y) pairs the two arms, and those
  two PUBs run one after the other inside the job; the target, its null control and its mutation share one placement for
  each block index. The earlier layout of this case read one block arm per PUB, 17 or 16 copies of it, and ran the blocks
  of an operand in different PUBs seconds apart.
- Placement. `place_replicas` takes the best-scored placements of the union of every body's qubits and couplers (the
  bodies route over subsets of one four-qubit pattern), with a one-qubit buffer and
  replica floor 0.5. `live_run.check_replica_isolation` refuses a body that acts outside its placement and replicas that
  share a qubit or sit within one coupler of the admitted graph. ibm_fez excludes qubits 2-4 and 16 (`--exclude-qubits`),
  the exclusion of the drain jobs whose recorded reason the repository does not hold; with it the search returns 17
  placements and without it 16. `--max-replicas` fixes the placement count (16 on ibm_kingston, 17 on ibm_fez), because a
  per-placement member names exactly one body per placement. The placed qubits have median readout error 0.0098
  (ibm_kingston) and 0.0100 (ibm_fez), median T1 247 and 139 us, minimum T2 34.4 and 28.8 us, placement scores 0.718 to
  0.837 and 0.559 to 0.847, and E10 minus E01 from -0.021 to 0.031 and -0.010 to 0.053. The bodies route to 1 to 29 CZ,
  both arms of every block alike on every placement, and each PUB runs at the duration of its deepest placement.
- Reference block on ibm_fez. The 17th placement of `pathion_wide_coset_d32` runs both arms of block k0 of the
  32-dimensional null operand e1 + e17, the 20-CZ block of the drain case (its N_hat is ideally 0), inside all twelve PUBs.
  It reads the drain case's block at the density and time of this case, six times at six moments of the job (one per
  operand's PUB pair), and ties this case to the drain readings (retained ibm_fez run: +0.026 before and -0.010 after the
  pooled readout correction; selector contrast -0.0019 +- 0.0020).
- Estimator. N_hat of a block is the half-sum of its output contrasts c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y)
  divided by their signed visibility (`pathion_parallel_coset.estimate`), scored against that placement's own block laws;
  the readout-corrected value applies it to the placement's laws after inversion of its own confusion matrices
  (live_run `corrected_summary`). `placed_summary` scales a block's quantity by the operand's block count, so live_run's
  pooled mean over placements is the whole-operand sum (the mean over the two copies for a 64-dimensional operand).
  `scripts/pathion_wide_coset_analysis.py` recomputes every placement from `collect.json` (the execution-start
  `placed_qubit_calibration` of each member's PUB, at the physical qubit that the archived routed circuit measures into
  each clbit), reports per placement and per block, and agrees with the pooled value to the 6-decimal rounding of the
  stored laws. `wide_<operand>_selector_contrast_sum` is the estimator-free sum of plus-minus selector contrasts (ideal
  nullity / 4).
- Interval. A block's N_hat is a smooth function of its plus and minus laws, each a multinomial sample of the PUB's shots.
  The delta method with the multinomial covariance (M (diag p - p p^T) M^T / shots for the readout inverse M of the
  corrected value, the identity for the raw one) gives its variance; the placements are disjoint and the arms are
  separate PUBs, so the variances add over blocks, and the 95 percent interval is the estimate +- 1.96 standard errors.
  This replaces the Student t over placements that an earlier layout of this case used: a block of `o128`, `n128` or
  `m128` is read on one placement per PUB, so placements no longer replicate it, and the spread over placements would
  mix the unequal blocks of one operand. A test simulates the multinomial sampling and matches the delta-method standard
  error within 15 percent. The bands below keep the 0.05 per block allowance for the unmodeled offset, which also
  covers placement-to-placement error.
- Clifford structure. A +-1 diagonal is Clifford when its sign function has degree at most 2 over GF(2). Blocks with
  both diagonals of degree at most 2 number 7 of 8 (`n64`), 6 of 8 (`o64`), 7 of 8 (`m64`), 15 of 16 (`n128`), 12 of 16
  (`o128`) and 15 of 16 (`m128`); the rest carry diagonals of degree 3 or 4, so no stabilizer simulation covers the full
  width. The side-by-side circuit of an operand (`full_width_circuit`, 4 qubits per block, 64 for `o128`) is the one-shot
  reading the PUB now runs on hardware, and its matrix-product-state simulation reads every operand's ideal sum.
- Seeds. Both runs share the transpiler and simulator seeds, indices 0 and 1 of the ANU QRNG draw
  `docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json` (1,024 uint16 values drawn 2026-11-07T05:15:16Z); index 2 seeds the
  circuit simulations of `test_pathion_wide_coset.py` and index 3 the multinomial draws of
  `test_pathion_wide_coset_analysis.py` (`docs/evidence/qrng_seeds/allocations.json`). The change that retains the runs
  adds the runtime ledger rows with `ci/seed_provenance.py --add-runtime`.

## Why a noise simulation cannot answer it

The binding dry runs simulate every placement with its live calibration (T1, T2, gate error and duration, each qubit's
asymmetric readout channel). The calibrated model carries no coherent error, no crosstalk between active neighbors, no
two-level-system defect, no residual excitation from the 20 us repetition delay and no drift, and the drain jobs found
its visibility about 0.07 above the hardware's. The hardware answers whether the compiled sign network of a 16-block
tiling reads the certified integer nullity at up to 29 routed CZ per block with that unmodeled error, with every block of
an operand running at once next to 15 neighbors (the crosstalk the one-qubit buffer allows; the drain jobs measured
-0.0042 and -0.0018 within 0.03), whether an estimator offset grows with the number of blocks it sums (the null
controls), whether the cocycle structure is what makes the nullity (the mutation), and whether two devices agree on the
whole nullity.

## Reachability at the budget

- Model, binding dry runs (whole-operand N_hat; readout-corrected value in brackets; model standard error of the
  corrected value after the +-):

| Operand | ibm_fez N_hat | ibm_kingston N_hat | Ideal |
|---|---|---|---:|
| `n64` | 0.251 (0.029 +- 0.019) | 0.322 (-0.004 +- 0.015) | 0 |
| `o64` | 28.211 (28.024 +- 0.013) | 28.187 (27.978 +- 0.011) | 28 |
| `m64` | -2.087 (-2.066 +- 0.026) | -2.068 (-2.044 +- 0.020) | -2 |
| `n128` | 0.463 (-0.015 +- 0.038) | 0.539 (-0.035 +- 0.030) | 0 |
| `o128` | 60.348 (60.102 +- 0.020) | 60.327 (60.031 +- 0.018) | 60 |
| `m128` | -1.878 (-1.973 +- 0.010) | -1.912 (-1.988 +- 0.010) | -2 |

  Every model sign agrees on all 64 or 128 bins. The 95 percent half-widths of the model values are at most 0.08, at least 10 times smaller than the bands below. The worst per-block readout-corrected deviation from the integer N_b is
  0.032 (ibm_fez) and 0.017 (ibm_kingston), with block standard errors up to 0.015. The model separates each target from
  its mutation by 30.09 and 62.08 (ibm_fez) and 30.02 and 62.02 (ibm_kingston) and from its null control by 27.995 and
  60.118 (ibm_fez), 27.981 and 60.066 (ibm_kingston). The raw null readings 0.25 to 0.54 come from the asymmetric readout
  channel and the inversion removes them. The model passes every rule below on both devices. The copy agreement of the
  64-dimensional operands reads z between -1.1 and +1.7 in the model. The model reads the reference block of ibm_fez at
  N_hat -0.024 to +0.048 per operand pair (standard error 0.031 each, 0.013 pooled) at raw visibility 0.58 to 0.59: the
  17th placement is the worst-scored placement of the layout (0.559).
- Noise-free matrix-product-state samples of the full-width circuits (`simulate_full_width`, 64 qubits for `o128` and
  `m128`, bond dimension at most 8, about 2 s) read every operand's ideal sum with all signs correct
  (`test_full_width_matrix_product_state_reads_the_ideal_sum`); a stabilizer simulation of the 12 Clifford blocks of
  `o128` (48 qubits) reads that subset's ideal sum.
- The budget reaches every decision rule below.

## Backends, shots, seconds

Billed seconds follow charge = 2.3 + executions x (rep_delay + planner bound + residual) + PUBs x (per-PUB term). The
residual is measured on the drain jobs: 6.6 to 7.2 us (ibm_fez) and 8.1 to 9.2 us (ibm_kingston) per execution. The
per-PUB term is the two-sigma upper bound of a fit over the retained single-job runs: 5.7 ms (ibm_fez) and 2.6 ms
(ibm_kingston), consistent with zero. The check script prices a plan at 7.2 us and 9.2 us plus those terms, rounds the
estimate up to whole seconds and admits it at least 1 s below the remaining seconds. The planner bound of a PUB is that
of its deepest placement (933 to 1,506 dt on ibm_kingston, 965 to 1,190 dt on ibm_fez).

| Run | Account (remaining at 10:23 UTC) | Binding dry run | Group, placements | PUBs x shots | Executions | Worst-case charge | Ceiling, reserve |
|---|---|---|---|---|---:|---|---|
| ibm_fez | `backup-ibm-quantum-platform` (10 s) | `2026-11-07T102337.840878Z`, calibration 2026-11-07T01:58:21-08:00 | `pathion_wide_coset_d32`, 17 | 13 x 16,000 | 208,000 | 8.87 s (billed 9 s) | 10 s, 0 s |
| ibm_kingston | primary (12 s) | `2026-11-07T102253.403258Z`, calibration 2026-11-07T02:02:41-08:00 | `pathion_wide_coset`, 16 | 13 x 19,456 | 252,928 | 10.90 s (billed 11 s) | 12 s, 0 s |

Repetition delay 20 us. Each PUB reads 16 operand blocks per shot (19,456 and 16,000 shots, so 311,296 and 256,000 block
reads per arm of each operand; the 64-dimensional operands read each block twice) and 12 PUBs hold the operand arms; the
13th PUB is live_run's isolated reference. The circuit set differs by the reference block only, and the shots differ
because each account is sized to its own remainder. The earlier layout ran 145 PUBs of 1,536 and 1,792 shots over 17 and 16 copies of each block arm (26,112 and 28,672
samples per block arm); this layout collects 16,000 and 19,456 samples per block arm of a 128-dimensional operand on one
placement and twice that for a 64-dimensional operand in the same seconds, and it cuts the per-PUB billing term from 0.8 s
and 0.4 s to 0.07 s and 0.03 s. The two jobs run as separate invocations, one after the other or in parallel.

Decisions for the owner. The ceiling equals the account's whole remainder (the planner requires ceiling plus reserve
not above it), so a job that overruns its estimate is killed at the ceiling, billed the remainder and loses its data;
the margins from the worst-case estimate to the ceiling are 1.13 s (ibm_fez) and 1.10 s (ibm_kingston), and the shots
sit at the largest multiple of 128 that keeps 0.1 s of margin in the unrounded estimate. A reserve of 0 s sits below the
60 s account reserve that the retention audit records (`account_reserve_met`); it follows the drain directive. Lowering
the shots to 15,872 (ibm_fez) and 19,328 (ibm_kingston) buys about 0.05 s of margin at a cost of under 1 percent of the
block reads.

## Preregistered readout and decision rules

Intervals are the delta-method 95 percent intervals above, computed by `scripts/pathion_wide_coset_analysis.py`. Bands
add the model's deviation from the integer (at most 0.2 on the readout-corrected sum) to an allowance of 0.05 per block
for an offset the model lacks, the largest per-block value that a retained run measured after readout correction (the
ibm_marrakesh one-CZ null blocks of the drain case, +0.045). The readout-corrected summary is the primary reading; the
raw one is reported beside it. The rules and bands are those of the earlier layout of this case; the interval and the
sign-resolution reading (the sum over blocks of the mean over a block's copies) are the only changes.

- Sign resolution. For every operand the sum over its blocks of the block's sign agreement (mean over copies) is at
  least bins - 0.5 (63.5 of 64, 127.5 of 128). The model reads every bin correctly on every placement (interval bounds of the
  block visibility 0.79 to 0.99), so a miss is a sign pattern of the compiled network that departs from cd_core.
- Whole-operand nullity. The interval of the readout-corrected `wide_o64_nullity_estimate` lies within 28 +- 0.6 and that
  of `wide_o128_nullity_estimate` within 60 +- 1.0. Outside the band, the compiled sign network of that nullity departs
  from cd_core by more than the allowance, unless the null control below names an additive offset that explains it.
- Null control. The interval of the readout-corrected `wide_n64_nullity_estimate` lies within 0 +- 0.4 and that of
  `wide_n128_nullity_estimate` within 0 +- 0.8 (0.05 per block). A reading outside names an estimator offset above the
  allowance and scales with the number of blocks; its size per block is the reading divided by 8 or 16.
- Null-referenced difference. The interval of the readout-corrected `wide_d64_target_minus_null` lies within 28 +- 0.5 and
  that of `wide_d128_target_minus_null` within 60 +- 0.8 (model 27.995 and 60.118 on ibm_fez, 27.981 and 60.066 on
  ibm_kingston). A per-block offset that adds to both operands cancels here, so a miss of the whole-operand rule with a
  pass of this rule is an offset, and a miss of both is a sign-network departure.
- Mutation. The readout-corrected `wide_m64_nullity_estimate` lies within -2 +- 0.6 and `wide_m128_nullity_estimate`
  within -2 +- 1.0, and `wide_d64_target_minus_mutation` is at least 27 and `wide_d128_target_minus_mutation` at least
  55 (90 percent of the ideal 30 and 62). A mutated tiling that reads like its true operand means the signs of the
  cocycle do not drive the reading; every mutated block also meets the sign-resolution rule.
- Per-block localization. Every block's readout-corrected `..._k<coset>_nullity_estimate` (the mean over its copies) lies
  within 0.25 of its integer ideal in the table above (model deviation at most 0.032, offset allowance 0.05, model
  standard error at most 0.015). A failing block names the coset and the class (N_b = 0, 2, 3, 4 or a mutated value) that
  carries a wrong sign.
- Null selector contrast (estimator-free). The sum of `wide_n64_k<coset>_selector_contrast` lies within 0 +- 0.05 and that
  of `wide_n128_..._selector_contrast` within 0 +- 0.10 (0.006 per block, the bound the drain case set for k0); an
  asymmetric product readout channel maps a null block's contrast to exactly 0, so a positive sum is a coherent error
  (model sums -0.015 to +0.032, standard error 0.02).
- Visibility floor. Every block's raw `..._visibility` interval lies above 0.5 (model lower bounds 0.79 to 0.84; the drain
  jobs read about 0.07 below their model).
- Device agreement. For each operand the difference of the two devices' readout-corrected whole-operand estimates, less
  the model's difference, lies within the sum of the two 95 percent half-widths plus 0.4 (D = 64) or 0.8 (D = 128).
  A larger difference names a device-specific offset or sign-network departure, which the per-block rule localizes.
- Report-only readings. (1) The isolated-reference crosstalk interval (90 percent Newcombe-Wilson, packed minus isolated
  replica-0 score of the null block k0 minus arm of `n64`) has a model half-width of about 0.004 at these shots, inside the
  drain's +-0.015 bound; the drain jobs hold the crosstalk decision for the same buffer. (2) Copy agreement: for each 64-dimensional operand the sum over blocks of copy A minus copy B of
  N_hat, over its standard error, stays within 3; a wider reading means the shot-noise interval understates the
  placement-to-placement error and the bands above carry the decision. (3) The ratio of `wide_o128_nullity_estimate` to
  `wide_o64_nullity_estimate` (ideal 2.143; model 2.145 on ibm_fez and 2.146 on ibm_kingston). (4) On ibm_fez the
  reference block's six readings, each against its drain value and the pooled mean. (5) A split of relaxation from
  residual excitation, which needs an arm at a longer repetition delay.

## Commands

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_wide_coset_check.py 17 10' -- \
      --groups pathion_wide_coset_d32 --backends ibm_fez --shots 16000 --rep-delay 2e-5 --replica-floor 0.5 \
      --max-replicas 17 --exclude-qubits ibm_fez:2-4,16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#1 \
      --max-total-execution-seconds 10 --max-execution-seconds 10 --reserve-seconds 0 \
      --min-remaining-seconds 1 --max-pending 100 --out ../results/live

    GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_wide_coset_check.py 16 12' -- \
      --groups pathion_wide_coset --backends ibm_kingston --shots 19456 --rep-delay 2e-5 --replica-floor 0.5 \
      --max-replicas 16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#1 \
      --max-total-execution-seconds 12 --max-execution-seconds 12 --reserve-seconds 0 \
      --min-remaining-seconds 1 --max-pending 100 --out ../results/live

After both jobs are collected, `"$PYTHON" scripts/pathion_wide_coset_analysis.py results/live/<ibm_fez run> results/live/<ibm_kingston
run>` prints every rule's verdict, the device-agreement rule, the copy agreement and every placement's block reading.

Both binding dry runs pass the check script (worst-case charge 8.87 s of 10 s and 10.90 s of 12 s), made from a clean
source tree at 5334661ce. The check's last argument is the account's `usage_remaining_seconds`; read each account's
`usage()` again before the submit and lower the argument and the shots if the remainder moved.

## Limits of this case

- The groups need exactly 17 (ibm_fez) and 16 (ibm_kingston) placements, because a per-placement member names one body
  per placement. A calibration at submit time that admits fewer placements makes `live_run` refuse the entry during the
  binding dry run, so `approved_run.sh` stops before any submit. The fallback on
  ibm_fez is `pathion_wide_coset` at 16 placements under a new approval; ibm_kingston below 16 placements has no
  fallback in this case.
- `summary_per_replica` in `record.json` and `collect.json` holds each placement's scaled contribution (the block's
  value times the operand's block count) and `summary_interval` is absent for these groups, because a spread over
  different blocks is no interval; the unscaled per-placement and per-block readings come from the analysis script.
- The arm order inside a job is IBM's choice. The plus and minus arm of an operand run in different PUBs, so drift between
  those two PUBs enters one block's contrast; every block of an operand shares both PUBs, so the drift acts alike on
  the blocks of a sum and the null controls and the reference block read it.
- A placement that holds one block per PUB carries that placement's calibration into the block: placement scores run 0.72
  to 0.84 (ibm_kingston) and 0.56 to 0.85 (ibm_fez), and the best-scored placement holds block 0 of every operand, so
  placement quality and block identity are crossed within an operand. The 64-dimensional operands read each block on a
  second placement (copy agreement), the null controls and mutations read the same placements, and the readout
  correction uses each placement's own calibration.
- The cost model rests on the drain jobs' residual range for each backend and on the 2.3 s job overhead of the retained
  jobs. A fit of billed charge minus (2.3 s + planned charge) against executions and PUBs over the retained single-job
  runs (8 on ibm_fez, 14 on ibm_kingston, each billed in whole seconds) gives a residual of 7.5 +- 0.7 us (ibm_fez) and
  9.2 +- 0.4 us (ibm_kingston) per execution and a per-PUB term of -4.4 +- 5.0 ms and -1.1 +- 1.8 ms: consistent with zero,
  not proof of zero. The estimate carries the two-sigma upper bounds, 13 x 5.7 ms and 13 x 2.6 ms. The drain
  jobs ran 8,192 to 16,384 shots per PUB; the ibm_kingston job's 19,456 exceeds that range by 19 percent and the ibm_fez
  job's 16,000 sits inside it.
- A per-block offset below 0.05 is near what one block resolves (model standard error 0.007 to 0.015 per block); the
  whole-operand rules resolve it at 8 or 16 blocks.
- Relaxation and residual excitation both land in the offset the null controls read; separating them needs an arm at a
  longer repetition delay, which this case omits.
- This branch changes `live_run.py`, `experiments.py`, `qpu_planning.py`, `pathion_coset_block.py`,
  `pathion_kernel_map.py` and `pathion_wide_coset.py` (in `live_run.EXPERIMENT_SOURCE_MANIFEST`), so the experiment digest
  differs from the one the drain jobs were planned under; `--collect` of those jobs runs from the drain branch's source.
  The drain case's own dry-run plan (group `pathion_parallel_coset` on ibm_kingston at 8,192 shots) is byte-identical
  under this branch: the archive digest and every group record equal the earlier source's on one calibration.
