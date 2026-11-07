# Written case: whole-operand nullity of two-term operands of the 64- and 128-dimensional Cayley-Dickson algebras on ibm_fez and ibm_kingston

Status: awaiting the owner's approval. Each run is a binding dry run and `--submit` back to back through
`scripts/approved_run.sh` with `scripts/pathion_wide_coset_check.py` as its check. Nothing is submitted, booked or
charged until the owner approves this case. This file is the case for both runs; the file of the same name beside the
ibm_kingston binding dry run holds that run's rows and points here.

Source of numbers. Model values come from the `record.json` of each binding dry run (`summary`,
`summary_readout_corrected`, `summary_interval`, `summary_per_replica` of the group `pathion_wide_coset`), the noise-model
prediction on that device's live calibration, and this case cites them only as predictions ("model"). Measured values
will come from `collect.json` of the submitted job: the pooled summary and its readout-corrected counterpart, each the
mean over placements of the value computed on one placement.

## What it measures

A two-term operand e_i + t e_j of A_n (D = 2^n) has a kernel map whose SELECT tiles into D / 8 independent four-qubit
blocks, one per coset of a 3-dimensional subspace V that contains m = i XOR j (`pathion_coset_block.py`, now taking the
dimension D). The aligned XOR pairs of block b number N_b, the blocks sum to the nullity of L_(e_i + t e_j), and
`cd_core` certifies that nullity from the integer rank (python-flint `fmpz_mat`) on every operand. The census
(`docs/evidence/pathion-kernel-map/census-wide.json`) finds no block class that first occurs at D = 64 or D = 128: the
same five two-term classes (N_b = 0 to 4) and nine four-term classes occur at every dimension. The quantity new above
D = 32 is the operand nullity, 16 to 28 at D = 64 and 32 to 60 at D = 128. The case reads the whole nullity of a
maximal-nullity operand at each dimension, 28 of 64 over 8 blocks (32 qubits) and 60 of 128 over 16 blocks (64
qubits), with a null control and a mutation arm per dimension, on two devices.

Group `pathion_wide_coset` (`gororoba_quantum/pathion_wide_coset.py`) holds 144 four-qubit circuits that compile onto
one layout, so each of its 145 fused PUBs (144 members and live_run's isolated reference) reads one block arm on every
placement at once: 17 placements on ibm_fez and 16 on ibm_kingston.

| Operand | Role | Nullity (cd_core) | Blocks | N_b of the blocks (ideal) | Ideal sum of N_b |
|---|---|---:|---:|---|---:|
| `o64` e1 + e36 | target | 28 of 64 | 8 | 2, 2, 4, 4, 4, 4, 4, 4 | 28 |
| `o128` e4 + e72 | target | 60 of 128 | 16 | 3, 3, 3, 3, 4 (twelve times) | 60 |
| `n64` e1 + e33 | null control | 0 | 8 | 0 (eight times) | 0 |
| `n128` e1 + e65 | null control | 0 | 16 | 0 (sixteen times) | 0 |
| `m64` cocycle-free tiling of e1 + e36 | mutation | 28 | 8 | 0, -2, 0, 0, 0, 0, 0, 0 | -2 |
| `m128` cocycle-free tiling of e4 + e72 | mutation | 60 | 16 | 4, -4, 2, -4, then 4, -4 alternating | -2 |

Both targets have the largest nullity of any two-term operand at their dimension and a block structure that differs
(N_b = 2 and 4 at D = 64; 3 and 4 at D = 128), so the classes N_b = 2, 3 and 4 enter through the targets and N_b = 0
through the null controls; N_b = 1 occurs only in mid-nullity operands, which the budget leaves out. The null controls
have the shape of e1 + e17 of A_5 (m = D / 2, the highest bit). The mutation replaces every L_m of the SELECT by its
unsigned XOR permutation, so the sign pattern the cocycle supplies vanishes while the circuit keeps the same oracle;
its ideal sum is -2 where the true tiling sums to 28 and 60 (separations 30 and 62). Every block of every operand
equals the module's full-map law on its output coset (`restriction_error` below 1e-12 for both arms and the mutation;
`tile` covers all D algebra indices once and its aligned counts sum to the cd_core nullity).

## Design

- One block per PUB. Each member is one four-qubit circuit (H on three data qubits, the oracle diagonal, H on the
  selector, a four-qubit diagonal, CNOT, H) with the orientation parameter bound to 0 (minus arm) or pi (plus arm), and
  each fused PUB reads that block arm on every placement. The first member is the minus arm of block k0 of `n64`; it fixes
  the placement and takes the isolated reference, the same circuit alone on replica 0.
- Why blocks are not side by side in one shot. The two targets side by side need 8 + 16 = 24 four-qubit placements with
  the one-qubit buffer; the placement search returns 17 and 16 (each buffered placement blocks 9 to 10 of the 156
  qubits). A fused PUB in which each placement runs a different block is refused by `Group._check_patterned_members`
  (patterned bodies must share one ideal law and one coupler set; the blocks' laws differ and they route to 1 to 29 CZ)
  and `_pooled_summaries` averages per-placement values where the nullity is a sum over blocks. The case keeps the
  drain case's design instead and loses nothing in seconds: a shot reads 17 or 16 copies of one block arm, so the
  block-arm samples per execution are 17 or 16 under either design, and the whole nullity of an operand is the sum over
  its blocks of per-block estimates, each pooled over 17 or 16 placements. The cost is simultaneity: the blocks of one
  operand are read in different PUBs seconds apart, so drift between PUBs enters a sum as block-to-block variation.
  `full_width_circuit` builds the side-by-side circuit (4 qubits per block, 64 for `o128`) and the simulations below
  read it; no hardware run places it.
- Estimator. N_hat of a block is the half-sum of its output contrasts c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y)
  divided by their signed visibility (`pathion_parallel_coset.estimate`); the readout-corrected value applies it to the
  replica laws after inversion of each placement's own confusion matrices (live_run `corrected_summary`). live_run keeps
  only the mean of that corrected value, so `scripts/pathion_wide_coset_analysis.py` recomputes it on every placement from
  `collect.json` (the execution-start `placed_qubit_calibration` of each member's PUB, at the physical qubit that the
  archived routed circuit measures into each clbit), takes the Student-t interval over the placements, evaluates the rules
  below and reports its difference from live_run's pooled value; its bounded test builds a synthetic run. The summed
  N_hat per operand is `wide_<operand>_nullity_estimate`, the per-block values are `wide_<operand>_k<coset>_...`, and
  `wide_<operand>_selector_contrast_sum` is the estimator-free sum of plus-minus selector contrasts (ideal nullity / 4).
- Clifford structure. A +-1 diagonal is Clifford when its sign function has degree at most 2 over GF(2). Blocks with
  both diagonals of degree at most 2 number 7 of 8 (`n64`), 6 of 8 (`o64`), 7 of 8 (`m64`), 15 of 16 (`n128`), 12 of 16
  (`o128`) and 15 of 16 (`m128`); the rest carry diagonals of degree 3 or 4, so no stabilizer simulation covers the full
  width.
- Seeds. Both runs share the transpiler and simulator seeds, indices 0 and 1 of the ANU QRNG draw
  `docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json` (1,024 uint16 values drawn 2026-11-07T05:15:16Z); index 2 seeds
  the test simulations (`docs/evidence/qrng_seeds/allocations.json`). The change that retains the runs adds the runtime
  ledger rows with `ci/seed_provenance.py --add-runtime`.
- Placement. `place_replicas` takes the best-scored placements of the group's compiled pattern with a one-qubit buffer
  and replica floor 0.5. ibm_fez excludes qubits 2-4 and 16 (`--exclude-qubits`), the exclusion of the drain jobs whose
  recorded reason the repository does not hold; with it the search returns 17 placements and without it 16. The placed
  qubits have median readout error 0.0100 (ibm_fez) and 0.0098 (ibm_kingston), median T1 139 and 247 us, minimum T2 28.8
  and 34.4 us, replica scores 0.56 to 0.85 and 0.72 to 0.84, and E10 minus E01 from -0.010 to 0.053 and -0.021 to 0.031.
  The members route to 1 to 29 CZ (depth up to 118), both arms of every block alike.

## Why a noise simulation cannot answer it

The binding dry runs simulate every placement with its live calibration (T1, T2, gate error and duration, each qubit's
asymmetric readout channel). The calibrated model carries no coherent error, no crosstalk between active neighbors, no
two-level-system defect, no residual excitation from the 20 us repetition delay and no drift, and the drain jobs found
its visibility about 0.07 above the hardware's. The hardware answers whether the compiled sign network of a 16-block
tiling reads the certified integer nullity at 20 to 29 routed CZ per block with that unmodeled error, whether an
estimator offset grows with the number of blocks it sums (the null controls), whether the cocycle structure is what
makes the nullity (the mutation), and whether two devices agree on the whole nullity.

## Reachability at the budget

- Model, binding dry runs (mean over placements; readout-corrected value in brackets):

| Operand | ibm_fez N_hat | ibm_kingston N_hat | Ideal |
|---|---|---|---:|
| `n64` | 0.209 (0.001) | 0.279 (-0.008) | 0 |
| `o64` | 28.163 (27.998) | 28.142 (27.997) | 28 |
| `m64` | -2.054 (-2.023) | -2.055 (-2.038) | -2 |
| `n128` | 0.377 (-0.035) | 0.564 (-0.018) | 0 |
| `o128` | 60.481 (60.178) | 60.357 (60.062) | 60 |
| `m128` | -1.902 (-1.983) | -1.920 (-1.992) | -2 |

  Every model sign agrees on all 64 or 128 bins. The model's 95 percent Student-t half-width of the raw placement mean
  is 0.06 and 0.05 (`o64`), 0.10 and 0.05 (`o128`), 0.12 and 0.17 (`n64`), 0.25 and 0.30 (`n128`) on ibm_fez and
  ibm_kingston, at least 2.4 times smaller than the bands below. The worst per-block readout-corrected deviation from the
  integer N_b is 0.063 (ibm_fez) and 0.021 (ibm_kingston). The model separates each target from its mutation by 30.0 and
  62.2 (`o64`, `o128`, ibm_fez) and 30.0 and 62.1 (ibm_kingston). The raw null readings 0.2 to 0.6 come from the
  asymmetric readout channel and the inversion removes them.
- Noise-free matrix-product-state samples of the full-width circuits (`simulate_full_width`, 64 qubits for `o128` and
  `m128`, bond dimension at most 8, about 2 s) read every operand's ideal sum with all signs correct
  (`test_full_width_matrix_product_state_reads_the_ideal_sum`); a stabilizer simulation of the 12 Clifford blocks of
  `o128` (48 qubits) reads that subset's ideal sum.
- The budget reaches every decision rule below except the two stated under report-only readings.

## Backends, shots, seconds

Billed seconds follow charge = 2.3 + executions x (rep_delay + planner bound + residual), the residual measured on the
drain jobs: 6.6 to 7.2 us (ibm_fez) and 8.1 to 9.2 us (ibm_kingston) per execution. The check script prices a plan at
7.2 us and 9.2 us, rounds the estimate up to whole seconds and admits it at least 1 s below the remaining seconds.

| Run | Account (remaining at 05:41 UTC) | Binding dry run | Placements | PUBs x shots | Executions | Estimated charge, drain residual range | Ceiling, reserve |
|---|---|---|---:|---|---:|---|---|
| ibm_fez | `backup-ibm-quantum-platform` (10 s) | `2026-11-07T054149.796663Z`, calibration 2026-11-06T21:11:35-08:00 | 17 | 145 x 1,536 | 222,720 | 8.87 s (8.73 to 8.87) | 10 s, 0 s |
| ibm_kingston | primary (12 s) | `2026-11-07T054147.895357Z`, calibration 2026-11-06T21:03:52-08:00 | 16 | 145 x 1,792 | 259,840 | 10.66 s (10.37 to 10.66) | 12 s, 0 s |

Repetition delay 20 us. Block reads: 145 x 1,536 x 17 = 3.79 million on ibm_fez and 145 x 1,792 x 16 = 4.16 million on
ibm_kingston. The circuit set is the same on both devices; the shots differ because each account is sized to its own
remainder (worst-case billed charge 9 s of 10 s and 11 s of 12 s). The two jobs run as separate invocations, one after
the other or in parallel.

Decisions for the owner. The ceiling equals the account's whole remainder (the planner requires ceiling plus reserve
not above it), so a job that overruns its estimate is killed at the ceiling, billed the remainder and loses its data;
the margins above the worst-case estimate are 1.1 s (ibm_fez) and 1.3 s (ibm_kingston). A reserve of 0 s sits below the
60 s account reserve that the retention audit records (`account_reserve_met`); it follows the drain directive. Lowering
the shots (1,408 and 1,664 give margins of about 1.7 s and 1.9 s) buys margin at a cost of 7 to 8 percent of the block reads.

## Preregistered readout and decision rules

Intervals are Student t over the placements (17 and 16), computed by `scripts/pathion_wide_coset_analysis.py`. Bands add the model's deviation from the integer (at most 0.2 on
the readout-corrected sum) to an allowance of 0.05 per block for an offset the model lacks, the largest per-block value
that a retained run measured after readout correction (the ibm_marrakesh one-CZ null blocks of the drain case, +0.045).
The readout-corrected summary is the primary reading; the raw one is reported beside it.

- Sign resolution. For every operand the mean over placements of `wide_<operand>_sign_agreement` is at least bins - 0.5
  (63.5 of 64, 127.5 of 128). The model reads every bin correctly on every placement at visibility 0.78 to 0.97, so a
  miss is a sign pattern of the compiled network that departs from cd_core.
- Whole-operand nullity. The interval of the readout-corrected `wide_o64_nullity_estimate` lies within 28 +- 0.6 and that
  of `wide_o128_nullity_estimate` within 60 +- 1.0. Outside the band, the compiled sign network of that nullity departs
  from cd_core by more than the allowance, unless the null control below names an additive offset that explains it.
- Null control. The interval of the readout-corrected `wide_n64_nullity_estimate` lies within 0 +- 0.4 and that of
  `wide_n128_nullity_estimate` within 0 +- 0.8 (0.05 per block). A reading outside names an estimator offset above the
  allowance and scales with the number of blocks; its size per block is the reading divided by 8 or 16.
- Null-referenced difference. The interval of the readout-corrected `wide_d64_target_minus_null` lies within 28 +- 0.5 and
  that of `wide_d128_target_minus_null` within 60 +- 0.8 (model 27.997 and 60.213 on ibm_fez, 28.005 and 60.080 on
  ibm_kingston). A per-block offset that adds to both operands cancels here, so a miss of the whole-operand rule with a
  pass of this rule is an offset, and a miss of both is a sign-network departure.
- Mutation. The readout-corrected `wide_m64_nullity_estimate` lies within -2 +- 0.6 and `wide_m128_nullity_estimate`
  within -2 +- 1.0, and `wide_d64_target_minus_mutation` is at least 27 and `wide_d128_target_minus_mutation` at least
  55 (90 percent of the ideal 30 and 62). A mutated tiling that reads like its true operand means the signs of the
  cocycle do not drive the reading; every mutated block also meets the sign-resolution rule.
- Per-block localization. Every block's readout-corrected `..._k<coset>_nullity_estimate` lies within 0.25 of its integer
  ideal in the table above (model deviation at most 0.063, offset allowance 0.05, model placement standard error at most
  0.021). A failing block names the coset and the class (N_b = 0, 2, 3, 4 or a mutated value) that carries a wrong sign.
- Null selector contrast (estimator-free). The sum of `wide_n64_k<coset>_selector_contrast` lies within 0 +- 0.05 and that
  of `wide_n128_..._selector_contrast` within 0 +- 0.10 (0.006 per block, the bound the drain case set for k0); an
  asymmetric product readout channel maps a null block's contrast to exactly 0, so a positive sum is a coherent error
  (model -0.004 to -0.012).
- Visibility floor. Every block's raw `..._visibility` interval lies above 0.5 (model 0.78 to 0.97; the drain jobs read
  about 0.07 below their model).
- Device agreement. For each operand the difference of the two devices' readout-corrected whole-operand estimates, less
  the model's difference, lies within the sum of the two 95 percent half-widths plus 0.4 (D = 64) or 0.8 (D = 128).
  A larger difference names a device-specific offset or sign-network departure, which the per-block rule localizes.
- Report-only readings. The isolated-reference crosstalk interval (90 percent Newcombe-Wilson, packed minus isolated
  replica-0 score of the null block k0 minus arm) has a model half-width of 0.014 at these shots, so it cannot certify
  the drain's +-0.015 bound unless the difference is near zero; the drain jobs hold the crosstalk decision for the same
  buffer. The ratio of `wide_o128_nullity_estimate` to `wide_o64_nullity_estimate` (ideal 2.143; model 2.149 on ibm_fez
  and 2.145 on ibm_kingston) is reported without a band, and so is a split of relaxation from residual excitation, which
  needs an arm at a longer repetition delay.

## Commands

Run from the repository root after approval:

    GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_wide_coset_check.py 16 10' -- \
      --groups pathion_wide_coset --backends ibm_fez --shots 1536 --rep-delay 2e-5 --replica-floor 0.5 \
      --exclude-qubits ibm_fez:2-4,16 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#1 \
      --max-total-execution-seconds 10 --max-execution-seconds 10 --reserve-seconds 0 \
      --min-remaining-seconds 1 --max-pending 100 --out ../results/live

    GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh \
      --check '"$PYTHON" ../scripts/pathion_wide_coset_check.py 16 12' -- \
      --groups pathion_wide_coset --backends ibm_kingston --shots 1792 --rep-delay 2e-5 --replica-floor 0.5 \
      --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#0 \
      --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json#1 \
      --max-total-execution-seconds 12 --max-execution-seconds 12 --reserve-seconds 0 \
      --min-remaining-seconds 1 --max-pending 100 --out ../results/live

After both jobs are collected, `"$PYTHON" scripts/pathion_wide_coset_analysis.py results/live/<ibm_fez run> results/live/<ibm_kingston
run>` prints every rule's verdict and the device-agreement rule.

Both binding dry runs pass the check script (worst-case charge 8.87 s of 10 s and 10.66 s of 12 s), made from a clean
source tree at 64f3f42ab. The check's last argument is the account's `usage_remaining_seconds`; read each account's
`usage()` again before the submit and lower the argument and the shots if the remainder moved.

## Limits of this case

- The arm order inside a job is IBM's choice; the blocks of an operand run in different PUBs, so drift between PUBs
  enters a sum as block-to-block variation, and the per-block rule and the null controls are the guard.
- The cost model rests on the drain jobs' residual range for each backend and on the 2.3 s job overhead of the retained
  jobs; this case runs 1,536 and 1,792 shots over 145 PUBs, fewer shots per PUB than the drain jobs (8,192 to 16,384).
  A fit of billed charge minus (2.3 s + planned charge) against executions and PUBs over the retained single-job runs
  (8 on ibm_fez, 14 on ibm_kingston, each billed in whole seconds) gives a residual of 7.5 +- 0.7 us (ibm_fez) and
  9.2 +- 0.4 us (ibm_kingston) per execution and a per-PUB term of -4.4 +- 5.0 ms and -1.1 +- 1.8 ms: consistent with zero,
  not proof of zero. Its two-sigma upper bounds, 5.7 ms and 2.6 ms, would add 0.8 s and 0.4 s at 145 PUBs, inside the
  1.1 s and 1.3 s margins to the ceilings and past the 1 s margin under the remainder on ibm_fez. Two retained jobs run in
  this regime without an excess: ibm_fez 48 PUBs of 1,536 shots (6.6 us) and ibm_kingston 99 PUBs of 800 shots (9.1 us).
  This is the case's main billing risk. The levers are fewer PUBs at more shots (dropping `m128` removes 32 PUBs and
  lets the same seconds carry 1,970 shots on ibm_fez) or fewer shots at the same PUBs (1,280 on ibm_fez keeps the
  two-sigma bound 1 s under the remainder).
- A per-block offset below 0.05 is near what one block resolves (model placement standard error 0.007 to 0.008 median,
  0.02 at most, per block); the whole-operand rules resolve it at 8 or 16 blocks.
- Relaxation and residual excitation both land in the offset the null controls read; separating them needs an arm at a
  longer repetition delay, which this case omits.
- This branch changes `pathion_coset_block.py` and `pathion_kernel_map.py` and adds a module to
  `live_run.EXPERIMENT_SOURCE_MANIFEST`, so the experiment digest differs from the one the drain jobs were planned
  under; `--collect` of those jobs runs from the drain branch's source.
