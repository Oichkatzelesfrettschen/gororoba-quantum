# Pathion evidence pivots

`evidence_table.csv` holds one row per measured pathion reading on IBM Heron r2, Quantum Inspire and Quandela Ascella, each with its ideal, its standard error where the record's estimator produces one, and the claim ledger rows that cite its run. `scripts/pathion_evidence_table_build.py` writes both files; the pivots below are computed from the CSV read back from disk. The column definitions are the module docstring of `gororoba_quantum/pathion_evidence_table.py`.

## Inputs

| backend | platform | substrate | rows |
|---|---|---|---|
| ibm_fez | ibm | qpu | 2990 |
| ibm_kingston | ibm | qpu | 1254 |
| ibm_marrakesh | ibm | qpu | 818 |
| qpu:ascella | quandela | qpu | 316 |
| qx-emulator | quantum_inspire | sim | 317 |
| sim:ascella | quandela | sim | 316 |
| tuna-17 | quantum_inspire | qpu | 226 |

| run | backend | rows |
|---|---|---|
| 2026-11-06T183538.809814Z | ibm_fez | 918 |
| 2026-11-06T200832.558771Z | ibm_marrakesh | 818 |
| 2026-11-06T201037.234804Z | ibm_fez | 818 |
| 2026-11-07T042346.084449Z | ibm_kingston | 1254 |
| 2026-11-07T042521.359670Z | ibm_fez | 1254 |
| 2026-11-06T215025Z-sim_ascella-ascella_pathion_four_term_blocks-sim-00 | sim:ascella | 132 |
| 2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00 | qpu:ascella | 132 |
| 2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00 | sim:ascella | 184 |
| 2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00 | qpu:ascella | 184 |
| pathion_coset_block_qx_analysis.v2.json | qx-emulator | 242 |
| pathion_coset_block_tuna_17_analysis.json | tuna-17 | 1 |
| pathion_coset_coin_qx_analysis.v2.json | qx-emulator | 75 |
| pathion_coset_coin_tuna_17_analysis.json | tuna-17 | 225 |

IBM standard errors are the standard deviation over replicas divided by the square root of their count; readout-corrected IBM values and every four-term Ascella level carry no standard error because their records store no replica or counting variance for them. Quantum Inspire values keep the series analysis's delta-method errors. The unversioned QX analyses are superseded by their `.v2` successors, which the build compares template by template; the stopped Tuna-17 block series retains no template reading beyond the null selector contrast that the coin analysis pins, which enters as one row under the stopped series' path.

Pathion directories under `results/live` without collected results:

| directory under results/live | reason |
|---|---|
| 2026-11-06T180755.872625Z | written case and plan: record state planned, no job submitted (pathion_kernel_map; no raw/ results) |
| 2026-11-06T183051.978364Z | binding dry run: record state planned, approval consumed, no job submitted (pathion_kernel_map; no raw/ results) |
| 2026-11-06T194735.738910Z | written case and plan: record state planned, no job submitted (pathion_coset_map; no raw/ results) |
| 2026-11-06T194735.851653Z | plan record: state planned, no job submitted (pathion_coset_map; no raw/ results) |
| 2026-11-06T200151.093434Z | binding dry run: record state planned, approval consumed, no job submitted (pathion_coset_map; no raw/ results) |
| 2026-11-06T200151.405088Z | binding dry run: record state planned, approval consumed, no job submitted (pathion_coset_map; no raw/ results) |
| 2026-11-07T035554.327341Z | written case and plan: record state planned, no job submitted (pathion_parallel_coset; no raw/ results) |
| 2026-11-07T040239.842834Z | plan record: state planned, no job submitted (pathion_parallel_coset; no raw/ results) |
| 2026-11-07T041623.255956Z | binding dry run: record state planned, approval consumed, no job submitted (pathion_parallel_coset; no raw/ results) |
| 2026-11-07T041624.522872Z | binding dry run: record state planned, approval consumed, no job submitted (pathion_parallel_coset; no raw/ results) |

## Pivot a: readings per backend and observable

Sign agreement counts readings whose ideal is nonzero, for observables with a signed ideal. The medians run over defined readings; the z of a reading is (measured - ideal) / standard error where the standard error exists.

| backend | observable | calibration | level | n | undefined | sign agreement | median abs dev | median abs z |
|---|---|---|---|---|---|---|---|---|
| ibm_fez | N_hat | raw | block | 72 | 0 | 37/37 | 0.0197 | 1.89 |
| ibm_fez | N_hat | raw | operand | 29 | 0 | 25/25 | 0.1434 | 2.13 |
| ibm_fez | N_hat | readout_corrected | block | 72 | 0 | 37/37 | 0.0084 | - |
| ibm_fez | N_hat | readout_corrected | operand | 29 | 0 | 25/25 | 0.0409 | - |
| ibm_fez | bin_tvd | raw | block | 4 | 0 | - | 0.0451 | 12.80 |
| ibm_fez | bin_tvd | readout_corrected | block | 4 | 0 | - | 0.0399 | - |
| ibm_fez | closure | raw | block | 11 | 0 | - | 0.0049 | 2.06 |
| ibm_fez | closure | readout_corrected | block | 11 | 0 | - | 0.0066 | - |
| ibm_fez | contrast_ratio | raw | operand | 11 | 1 | 10/10 | 0.7843 | 14.44 |
| ibm_fez | contrast_ratio | readout_corrected | operand | 11 | 1 | 10/10 | 0.7780 | - |
| ibm_fez | even_half_sum | raw | block | 8 | 0 | - | 0.0164 | 1.62 |
| ibm_fez | even_half_sum | raw | operand | 2 | 0 | - | 1.0645 | 5.52 |
| ibm_fez | even_half_sum | readout_corrected | block | 8 | 0 | - | 0.0180 | - |
| ibm_fez | even_half_sum | readout_corrected | operand | 2 | 0 | - | 0.8488 | - |
| ibm_fez | even_nullity | raw | block | 8 | 0 | - | 0.0008 | 1.13 |
| ibm_fez | even_nullity | raw | operand | 2 | 0 | - | 0.0247 | 1.42 |
| ibm_fez | even_nullity | readout_corrected | block | 8 | 0 | - | 0.0010 | - |
| ibm_fez | even_nullity | readout_corrected | operand | 2 | 0 | - | 0.0253 | - |
| ibm_fez | half_sum | raw | block | 72 | 0 | 37/37 | 0.2612 | 7.90 |
| ibm_fez | half_sum | raw | operand | 13 | 0 | 11/11 | 3.0591 | 12.35 |
| ibm_fez | half_sum | readout_corrected | block | 72 | 0 | 37/37 | 0.2386 | - |
| ibm_fez | half_sum | readout_corrected | operand | 13 | 0 | 11/11 | 3.0268 | - |
| ibm_fez | level | raw | block | 15 | 0 | - | 0.0405 | 9.45 |
| ibm_fez | level | readout_corrected | block | 15 | 0 | - | 0.0338 | - |
| ibm_fez | mean_abs_output_contrast | raw | operand | 11 | 0 | - | 0.7882 | 42.01 |
| ibm_fez | mean_abs_output_contrast | readout_corrected | operand | 11 | 0 | - | 0.7780 | - |
| ibm_fez | nullity_ratio_12_over_4 | raw | operand | 1 | 0 | - | 1.5162 | 13.21 |
| ibm_fez | nullity_ratio_12_over_4 | readout_corrected | operand | 1 | 0 | - | 1.4943 | - |
| ibm_fez | nullity_ratio_8_over_4 | raw | operand | 1 | 0 | - | 0.4024 | 0.68 |
| ibm_fez | nullity_ratio_8_over_4 | readout_corrected | operand | 1 | 0 | - | 0.4273 | - |
| ibm_fez | odd_half_sum | raw | block | 8 | 0 | - | 0.0086 | 1.21 |
| ibm_fez | odd_half_sum | raw | operand | 2 | 0 | - | 0.0418 | 1.97 |
| ibm_fez | odd_half_sum | readout_corrected | block | 8 | 0 | - | 0.0033 | - |
| ibm_fez | odd_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0348 | - |
| ibm_fez | odd_nullity | raw | block | 8 | 0 | - | 0.0055 | 1.27 |
| ibm_fez | odd_nullity | raw | operand | 2 | 0 | - | 0.0488 | 1.32 |
| ibm_fez | odd_nullity | readout_corrected | block | 8 | 0 | - | 0.0066 | - |
| ibm_fez | odd_nullity | readout_corrected | operand | 2 | 0 | - | 0.0302 | - |
| ibm_fez | output_contrast | raw | bin | 864 | 0 | 849/864 | 0.2474 | 10.36 |
| ibm_fez | output_ratio | raw | bin | 864 | 0 | 810/864 | 0.0212 | 1.33 |
| ibm_fez | p_selector0 | raw | operand | 22 | 0 | - | 0.0997 | 13.26 |
| ibm_fez | p_selector0 | readout_corrected | operand | 22 | 0 | - | 0.0992 | - |
| ibm_fez | pair_half_sum_gap | raw | block | 8 | 0 | - | 0.0040 | 0.76 |
| ibm_fez | pair_half_sum_gap | raw | operand | 2 | 0 | - | 0.0095 | 1.06 |
| ibm_fez | pair_half_sum_gap | readout_corrected | block | 8 | 0 | - | 0.0036 | - |
| ibm_fez | pair_half_sum_gap | readout_corrected | operand | 2 | 0 | - | 0.0094 | - |
| ibm_fez | quad_half_sum | raw | block | 8 | 0 | - | 0.0213 | 1.25 |
| ibm_fez | quad_half_sum | raw | operand | 2 | 0 | - | 1.1016 | 5.35 |
| ibm_fez | quad_half_sum | readout_corrected | block | 8 | 0 | - | 0.0152 | - |
| ibm_fez | quad_half_sum | readout_corrected | operand | 2 | 0 | - | 0.8651 | - |
| ibm_fez | quad_nullity_estimate | raw | block | 8 | 0 | - | 0.0194 | 1.18 |
| ibm_fez | quad_nullity_estimate | raw | operand | 2 | 0 | - | 0.0634 | 1.14 |
| ibm_fez | quad_nullity_estimate | readout_corrected | block | 8 | 0 | - | 0.0053 | - |
| ibm_fez | quad_nullity_estimate | readout_corrected | operand | 2 | 0 | - | 0.0118 | - |
| ibm_fez | repeat_half_sum | raw | block | 8 | 0 | - | 0.0215 | 1.30 |
| ibm_fez | repeat_half_sum | raw | operand | 2 | 0 | - | 1.0968 | 5.29 |
| ibm_fez | repeat_half_sum | readout_corrected | block | 8 | 0 | - | 0.0166 | - |
| ibm_fez | repeat_half_sum | readout_corrected | operand | 2 | 0 | - | 0.8630 | - |
| ibm_fez | repeat_nullity_estimate | raw | block | 8 | 0 | - | 0.0179 | 1.05 |
| ibm_fez | repeat_nullity_estimate | raw | operand | 2 | 0 | - | 0.0620 | 1.12 |
| ibm_fez | repeat_nullity_estimate | readout_corrected | block | 8 | 0 | - | 0.0055 | - |
| ibm_fez | repeat_nullity_estimate | readout_corrected | operand | 2 | 0 | - | 0.0093 | - |
| ibm_fez | selector_contrast | raw | block | 40 | 0 | 20/20 | 0.0556 | 8.62 |
| ibm_fez | selector_contrast | raw | operand | 13 | 0 | 11/11 | 0.1994 | 12.04 |
| ibm_fez | selector_contrast | readout_corrected | block | 40 | 0 | 20/20 | 0.0488 | - |
| ibm_fez | selector_contrast | readout_corrected | operand | 13 | 0 | 11/11 | 0.1976 | - |
| ibm_fez | separation | raw | block | 6 | 0 | - | 0.1048 | 11.33 |
| ibm_fez | separation | readout_corrected | block | 6 | 0 | - | 0.0957 | - |
| ibm_fez | sign_count | raw | block | 64 | 0 | - | 0.0000 | - |
| ibm_fez | sign_count | raw | operand | 27 | 0 | - | 0.0000 | 2.08 |
| ibm_fez | sign_count | readout_corrected | block | 64 | 0 | - | 0.0000 | - |
| ibm_fez | sign_count | readout_corrected | operand | 27 | 0 | - | 0.0000 | - |
| ibm_fez | skeleton_p0 | raw | operand | 1 | 0 | - | 0.0104 | 2.63 |
| ibm_fez | skeleton_p0 | readout_corrected | operand | 1 | 0 | - | 0.0010 | - |
| ibm_fez | strut9_ratio_e1e24_over_e2e27 | raw | operand | 1 | 0 | - | 1.8294 | 4.96 |
| ibm_fez | strut9_ratio_e1e24_over_e2e27 | readout_corrected | operand | 1 | 0 | - | 1.8294 | - |
| ibm_fez | twin_difference_e17me10 | raw | operand | 1 | 0 | - | 0.0117 | 1.57 |
| ibm_fez | twin_difference_e17me10 | readout_corrected | operand | 1 | 0 | - | 0.0120 | - |
| ibm_fez | twin_difference_e17me2 | raw | operand | 1 | 0 | - | 0.0635 | 3.55 |
| ibm_fez | twin_difference_e17me2 | readout_corrected | operand | 1 | 0 | - | 0.0618 | - |
| ibm_fez | twin_nullity_difference | raw | operand | 2 | 0 | - | 0.0082 | 0.75 |
| ibm_fez | twin_nullity_difference | readout_corrected | operand | 2 | 0 | - | 0.0081 | - |
| ibm_fez | twin_nullity_difference_e17me10 | raw | operand | 1 | 0 | - | 23.6753 | 0.71 |
| ibm_fez | twin_nullity_difference_e17me10 | readout_corrected | operand | 1 | 0 | - | 20.6512 | - |
| ibm_fez | twin_nullity_difference_e17me2 | raw | operand | 1 | 0 | - | 0.7743 | 3.67 |
| ibm_fez | twin_nullity_difference_e17me2 | readout_corrected | operand | 1 | 0 | - | 0.6306 | - |
| ibm_fez | visibility | raw | block | 74 | 0 | 74/74 | 0.1847 | 9.55 |
| ibm_fez | visibility | raw | operand | 27 | 0 | 27/27 | 0.2261 | 10.78 |
| ibm_fez | visibility | readout_corrected | block | 74 | 0 | 74/74 | 0.1447 | - |
| ibm_fez | visibility | readout_corrected | operand | 27 | 0 | 27/27 | 0.1730 | - |
| ibm_fez | within_minus_half_sum | raw | block | 8 | 0 | - | 0.0018 | 0.57 |
| ibm_fez | within_minus_half_sum | raw | operand | 2 | 0 | - | 0.0061 | 0.85 |
| ibm_fez | within_minus_half_sum | readout_corrected | block | 8 | 0 | - | 0.0016 | - |
| ibm_fez | within_minus_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0066 | - |
| ibm_fez | within_plus_half_sum | raw | block | 8 | 0 | - | 0.0020 | 0.84 |
| ibm_fez | within_plus_half_sum | raw | operand | 2 | 0 | - | 0.0038 | 0.77 |
| ibm_fez | within_plus_half_sum | readout_corrected | block | 8 | 0 | - | 0.0028 | - |
| ibm_fez | within_plus_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0029 | - |
| ibm_kingston | N_hat | raw | block | 40 | 0 | 20/20 | 0.0092 | 1.34 |
| ibm_kingston | N_hat | raw | operand | 10 | 0 | 8/8 | 0.0513 | 1.97 |
| ibm_kingston | N_hat | readout_corrected | block | 40 | 0 | 20/20 | 0.0123 | - |
| ibm_kingston | N_hat | readout_corrected | operand | 10 | 0 | 8/8 | 0.0389 | - |
| ibm_kingston | bin_tvd | raw | block | 4 | 0 | - | 0.0436 | 9.68 |
| ibm_kingston | bin_tvd | readout_corrected | block | 4 | 0 | - | 0.0413 | - |
| ibm_kingston | closure | raw | block | 11 | 0 | - | 0.0061 | 1.38 |
| ibm_kingston | closure | readout_corrected | block | 11 | 0 | - | 0.0058 | - |
| ibm_kingston | even_half_sum | raw | block | 8 | 0 | - | 0.0060 | 1.18 |
| ibm_kingston | even_half_sum | raw | operand | 2 | 0 | - | 0.7813 | 7.38 |
| ibm_kingston | even_half_sum | readout_corrected | block | 8 | 0 | - | 0.0066 | - |
| ibm_kingston | even_half_sum | readout_corrected | operand | 2 | 0 | - | 0.6447 | - |
| ibm_kingston | even_nullity | raw | block | 8 | 0 | - | 0.0015 | 0.66 |
| ibm_kingston | even_nullity | raw | operand | 2 | 0 | - | 0.0082 | 0.88 |
| ibm_kingston | even_nullity | readout_corrected | block | 8 | 0 | - | 0.0015 | - |
| ibm_kingston | even_nullity | readout_corrected | operand | 2 | 0 | - | 0.0090 | - |
| ibm_kingston | half_sum | raw | block | 40 | 0 | 20/20 | 0.1231 | 8.22 |
| ibm_kingston | half_sum | raw | operand | 2 | 0 | 1/1 | 0.7939 | 7.61 |
| ibm_kingston | half_sum | readout_corrected | block | 40 | 0 | 20/20 | 0.0997 | - |
| ibm_kingston | half_sum | readout_corrected | operand | 2 | 0 | 1/1 | 0.6779 | - |
| ibm_kingston | level | raw | block | 15 | 0 | - | 0.0303 | 9.90 |
| ibm_kingston | level | readout_corrected | block | 15 | 0 | - | 0.0254 | - |
| ibm_kingston | odd_half_sum | raw | block | 8 | 0 | - | 0.0065 | 1.05 |
| ibm_kingston | odd_half_sum | raw | operand | 2 | 0 | - | 0.0235 | 1.29 |
| ibm_kingston | odd_half_sum | readout_corrected | block | 8 | 0 | - | 0.0097 | - |
| ibm_kingston | odd_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0528 | - |
| ibm_kingston | odd_nullity | raw | block | 8 | 0 | - | 0.0066 | 1.16 |
| ibm_kingston | odd_nullity | raw | operand | 2 | 0 | - | 0.0309 | 1.55 |
| ibm_kingston | odd_nullity | readout_corrected | block | 8 | 0 | - | 0.0096 | - |
| ibm_kingston | odd_nullity | readout_corrected | operand | 2 | 0 | - | 0.0550 | - |
| ibm_kingston | output_contrast | raw | bin | 256 | 0 | 256/256 | 0.1421 | 12.83 |
| ibm_kingston | output_ratio | raw | bin | 256 | 0 | 256/256 | 0.0088 | 1.42 |
| ibm_kingston | pair_half_sum_gap | raw | block | 8 | 0 | - | 0.0053 | 0.84 |
| ibm_kingston | pair_half_sum_gap | raw | operand | 2 | 0 | - | 0.0139 | 1.26 |
| ibm_kingston | pair_half_sum_gap | readout_corrected | block | 8 | 0 | - | 0.0055 | - |
| ibm_kingston | pair_half_sum_gap | readout_corrected | operand | 2 | 0 | - | 0.0141 | - |
| ibm_kingston | quad_half_sum | raw | block | 8 | 0 | - | 0.0214 | 1.81 |
| ibm_kingston | quad_half_sum | raw | operand | 2 | 0 | - | 0.7937 | 7.85 |
| ibm_kingston | quad_half_sum | readout_corrected | block | 8 | 0 | - | 0.0293 | - |
| ibm_kingston | quad_half_sum | readout_corrected | operand | 2 | 0 | - | 0.6830 | - |
| ibm_kingston | quad_nullity_estimate | raw | block | 8 | 0 | - | 0.0066 | 1.07 |
| ibm_kingston | quad_nullity_estimate | raw | operand | 2 | 0 | - | 0.0380 | 1.72 |
| ibm_kingston | quad_nullity_estimate | readout_corrected | block | 8 | 0 | - | 0.0095 | - |
| ibm_kingston | quad_nullity_estimate | readout_corrected | operand | 2 | 0 | - | 0.0469 | - |
| ibm_kingston | repeat_half_sum | raw | block | 8 | 0 | - | 0.0213 | 1.61 |
| ibm_kingston | repeat_half_sum | raw | operand | 2 | 0 | - | 0.7870 | 7.80 |
| ibm_kingston | repeat_half_sum | readout_corrected | block | 8 | 0 | - | 0.0299 | - |
| ibm_kingston | repeat_half_sum | readout_corrected | operand | 2 | 0 | - | 0.6808 | - |
| ibm_kingston | repeat_nullity_estimate | raw | block | 8 | 0 | - | 0.0060 | 1.02 |
| ibm_kingston | repeat_nullity_estimate | raw | operand | 2 | 0 | - | 0.0368 | 1.59 |
| ibm_kingston | repeat_nullity_estimate | readout_corrected | block | 8 | 0 | - | 0.0060 | - |
| ibm_kingston | repeat_nullity_estimate | readout_corrected | operand | 2 | 0 | - | 0.0480 | - |
| ibm_kingston | selector_contrast | raw | block | 40 | 0 | 20/20 | 0.0425 | 8.19 |
| ibm_kingston | selector_contrast | raw | operand | 2 | 0 | 1/1 | 0.1976 | 6.97 |
| ibm_kingston | selector_contrast | readout_corrected | block | 40 | 0 | 20/20 | 0.0371 | - |
| ibm_kingston | selector_contrast | readout_corrected | operand | 2 | 0 | 1/1 | 0.1634 | - |
| ibm_kingston | separation | raw | block | 6 | 0 | - | 0.0790 | 9.04 |
| ibm_kingston | separation | readout_corrected | block | 6 | 0 | - | 0.0691 | - |
| ibm_kingston | sign_count | raw | block | 32 | 0 | - | 0.0000 | - |
| ibm_kingston | sign_count | raw | operand | 8 | 0 | - | 0.0000 | - |
| ibm_kingston | sign_count | readout_corrected | block | 32 | 0 | - | 0.0000 | - |
| ibm_kingston | sign_count | readout_corrected | operand | 8 | 0 | - | 0.0000 | - |
| ibm_kingston | twin_nullity_difference | raw | operand | 1 | 0 | - | 0.0244 | 1.98 |
| ibm_kingston | twin_nullity_difference | readout_corrected | operand | 1 | 0 | - | 0.0250 | - |
| ibm_kingston | visibility | raw | block | 42 | 0 | 42/42 | 0.1375 | 13.64 |
| ibm_kingston | visibility | raw | operand | 8 | 0 | 8/8 | 0.1464 | 14.63 |
| ibm_kingston | visibility | readout_corrected | block | 42 | 0 | 42/42 | 0.1090 | - |
| ibm_kingston | visibility | readout_corrected | operand | 8 | 0 | 8/8 | 0.1190 | - |
| ibm_kingston | within_minus_half_sum | raw | block | 8 | 0 | - | 0.0023 | 0.43 |
| ibm_kingston | within_minus_half_sum | raw | operand | 2 | 0 | - | 0.0046 | 0.50 |
| ibm_kingston | within_minus_half_sum | readout_corrected | block | 8 | 0 | - | 0.0025 | - |
| ibm_kingston | within_minus_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0049 | - |
| ibm_kingston | within_plus_half_sum | raw | block | 8 | 0 | - | 0.0039 | 1.06 |
| ibm_kingston | within_plus_half_sum | raw | operand | 2 | 0 | - | 0.0124 | 1.97 |
| ibm_kingston | within_plus_half_sum | readout_corrected | block | 8 | 0 | - | 0.0039 | - |
| ibm_kingston | within_plus_half_sum | readout_corrected | operand | 2 | 0 | - | 0.0127 | - |
| ibm_marrakesh | N_hat | raw | block | 32 | 0 | 17/17 | 0.0299 | 2.13 |
| ibm_marrakesh | N_hat | raw | operand | 8 | 0 | 7/7 | 0.1291 | 2.78 |
| ibm_marrakesh | N_hat | readout_corrected | block | 32 | 0 | 17/17 | 0.0186 | - |
| ibm_marrakesh | N_hat | readout_corrected | operand | 8 | 0 | 7/7 | 0.0440 | - |
| ibm_marrakesh | half_sum | raw | block | 32 | 0 | 17/17 | 0.3480 | 6.63 |
| ibm_marrakesh | half_sum | readout_corrected | block | 32 | 0 | 17/17 | 0.3211 | - |
| ibm_marrakesh | output_contrast | raw | bin | 256 | 0 | 256/256 | 0.1850 | 8.46 |
| ibm_marrakesh | output_ratio | raw | bin | 256 | 0 | 256/256 | 0.0102 | 1.29 |
| ibm_marrakesh | sign_count | raw | block | 32 | 0 | - | 0.0000 | - |
| ibm_marrakesh | sign_count | raw | operand | 8 | 0 | - | 0.0000 | - |
| ibm_marrakesh | sign_count | readout_corrected | block | 32 | 0 | - | 0.0000 | - |
| ibm_marrakesh | sign_count | readout_corrected | operand | 8 | 0 | - | 0.0000 | - |
| ibm_marrakesh | twin_nullity_difference | raw | operand | 1 | 0 | - | 0.0140 | 1.01 |
| ibm_marrakesh | twin_nullity_difference | readout_corrected | operand | 1 | 0 | - | 0.0149 | - |
| ibm_marrakesh | visibility | raw | block | 32 | 0 | 32/32 | 0.1962 | 8.91 |
| ibm_marrakesh | visibility | raw | operand | 8 | 0 | 8/8 | 0.1845 | 9.50 |
| ibm_marrakesh | visibility | readout_corrected | block | 32 | 0 | 32/32 | 0.1380 | - |
| ibm_marrakesh | visibility | readout_corrected | operand | 8 | 0 | 8/8 | 0.1478 | - |
| qpu:ascella | level | anchor_dark_normalized | block | 90 | 0 | - | 0.0063 | - |
| qpu:ascella | level | branch_odds_corrected | block | 44 | 0 | - | 0.0066 | - |
| qpu:ascella | level | per_slot_anchor_dark | block | 46 | 0 | - | 0.0075 | 8.02 |
| qpu:ascella | level | raw | block | 90 | 0 | - | 0.0072 | - |
| qpu:ascella | mirror_difference | per_slot_anchor_dark | block | 46 | 0 | - | 0.0259 | - |
| qx-emulator | D_y | raw | bin | 48 | 0 | - | 0.0159 | 0.50 |
| qx-emulator | D_y | readout_corrected | bin | 48 | 0 | - | 0.0159 | 0.50 |
| qx-emulator | N_hat | raw | block | 6 | 0 | 4/4 | 0.0021 | 0.53 |
| qx-emulator | N_hat | readout_corrected | block | 3 | 0 | 2/2 | 0.0010 | 0.26 |
| qx-emulator | output_contrast | raw | bin | 64 | 0 | 64/64 | 0.0002 | 0.50 |
| qx-emulator | output_contrast | readout_corrected | bin | 32 | 0 | 32/32 | 0.0002 | 0.57 |
| qx-emulator | output_ratio | raw | bin | 64 | 0 | 64/64 | 0.0003 | 1.00 |
| qx-emulator | output_ratio | readout_corrected | bin | 32 | 0 | 32/32 | 0.0003 | 1.00 |
| qx-emulator | selector_contrast | raw | block | 8 | 0 | 6/6 | 0.0039 | 0.43 |
| qx-emulator | visibility | raw | block | 8 | 0 | 8/8 | 0.0010 | 1.73 |
| qx-emulator | visibility | readout_corrected | block | 4 | 0 | 4/4 | 0.0012 | 3.00 |
| sim:ascella | level | anchor_dark_normalized | block | 90 | 0 | - | 0.0006 | - |
| sim:ascella | level | branch_odds_corrected | block | 44 | 0 | - | 0.0005 | - |
| sim:ascella | level | per_slot_anchor_dark | block | 46 | 0 | - | 0.0006 | 0.61 |
| sim:ascella | level | raw | block | 90 | 0 | - | 0.0008 | - |
| sim:ascella | mirror_difference | per_slot_anchor_dark | block | 46 | 0 | - | 0.0015 | - |
| tuna-17 | D_y | raw | bin | 48 | 0 | - | 0.0709 | 1.75 |
| tuna-17 | D_y | readout_corrected | bin | 48 | 0 | - | 0.0594 | 1.47 |
| tuna-17 | N_hat | raw | block | 3 | 0 | 2/2 | 0.1537 | 4.82 |
| tuna-17 | N_hat | readout_corrected | block | 3 | 0 | 2/2 | 0.0805 | 2.60 |
| tuna-17 | output_contrast | raw | bin | 32 | 0 | 32/32 | 0.5628 | 54.76 |
| tuna-17 | output_contrast | readout_corrected | bin | 24 | 0 | 24/24 | 0.5217 | 42.04 |
| tuna-17 | output_ratio | raw | bin | 32 | 0 | 32/32 | 0.0595 | 2.43 |
| tuna-17 | output_ratio | readout_corrected | bin | 24 | 0 | 24/24 | 0.0538 | 2.23 |
| tuna-17 | selector_contrast | raw | block | 5 | 0 | 3/3 | 0.2650 | 51.93 |
| tuna-17 | visibility | raw | block | 4 | 0 | 4/4 | 0.5623 | 160.00 |
| tuna-17 | visibility | readout_corrected | block | 3 | 0 | 3/3 | 0.4952 | 123.22 |

## Pivot b: the same blocks on several backends

Two-term blocks. A Tuna-17 bin and an IBM bin meet at their algebra output label, never at a coset index. D(y) is the Tuna-17 readout-corrected ratio c(y)/V minus the IBM raw ratio at the same label, its standard error the quadrature sum of the Tuna-17 delta-method error and the IBM replica spread, as `pathion_coset_analysis.cross_platform` computes it. The stored D(y) of each device matches the IBM run named here (resolved by value): ibm_fez: 2026-11-06T201037.234804Z; ibm_marrakesh: 2026-11-06T200832.558771Z.

| Tuna-17 block | operand | IBM device | bins within 3 combined standard errors | largest z |
|---|---|---|---|---|
| b0 | e1+e17 | ibm_fez | 7 of 8 | bin 5 at 4.3 |
| b0 | e1+e17 | ibm_marrakesh | 7 of 8 | bin 5 at 3.4 |
| ba | e1+e18 | ibm_fez | 5 of 8 | bin 5 at 5.1 |
| ba | e1+e18 | ibm_marrakesh | 6 of 8 | bin 5 at 4.1 |
| bb | e1+e26 | ibm_fez | 7 of 8 | bin 2 at 4.5 |
| bb | e1+e26 | ibm_marrakesh | 7 of 8 | bin 2 at 4.1 |

Template `b0` (e1+e17, nullity-0):

| bin | label | ideal sign | Tuna-17 corrected ratio | ibm_marrakesh 2026-11-06T200832 | ibm_fez 2026-11-06T201037 | ibm_kingston 2026-11-07T042346 | ibm_fez 2026-11-07T042521 | D(y) z vs ibm_fez | D(y) z vs ibm_marrakesh |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | -1 | -0.9232 +- 0.0209 | -0.9626 +- 0.0144 | -0.9494 +- 0.0082 | -0.9772 +- 0.0054 | -0.9563 +- 0.0113 | 0.66 | 0.76 |
| 1 | 17 | 1 | 0.9229 +- 0.0215 | 0.9612 +- 0.0137 | 0.9729 +- 0.0050 | 0.9855 +- 0.0084 | 0.9653 +- 0.0091 | -1.68 | -0.76 |
| 2 | 0 | -1 | -0.9486 +- 0.0229 | -1.0100 +- 0.0099 | -0.9895 +- 0.0058 | -0.9913 +- 0.0086 | -0.9979 +- 0.0055 | 1.23 | 1.53 |
| 3 | 16 | 1 | 0.9545 +- 0.0220 | 1.0274 +- 0.0108 | 1.0075 +- 0.0052 | 1.0214 +- 0.0076 | 1.0176 +- 0.0079 | -1.72 | -1.74 |
| 4 | 3 | -1 | -1.0459 +- 0.0241 | -0.9886 +- 0.0107 | -1.0143 +- 0.0073 | -0.9834 +- 0.0090 | -0.9983 +- 0.0049 | -0.82 | -1.34 |
| 5 | 19 | 1 | 1.1598 +- 0.0229 | 1.0116 +- 0.0111 | 1.0189 +- 0.0058 | 1.0024 +- 0.0103 | 1.0067 +- 0.0099 | 4.26 | 3.41 |
| 6 | 2 | -1 | -1.0018 +- 0.0255 | -1.0099 +- 0.0149 | -1.0211 +- 0.0061 | -1.0083 +- 0.0062 | -1.0219 +- 0.0053 | 0.54 | 0.15 |
| 7 | 18 | 1 | 1.0432 +- 0.0238 | 1.0287 +- 0.0136 | 1.0265 +- 0.0053 | 1.0306 +- 0.0075 | 1.0359 +- 0.0080 | 0.52 | 0.28 |

Template `ba` (e1+e18, nullity-2):

| bin | label | ideal sign | Tuna-17 corrected ratio | ibm_marrakesh 2026-11-06T200832 | ibm_fez 2026-11-06T201037 | ibm_kingston 2026-11-07T042346 | ibm_fez 2026-11-07T042521 | D(y) z vs ibm_fez | D(y) z vs ibm_marrakesh |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | -1 | -0.9065 +- 0.0219 | -0.9707 +- 0.0156 | -0.9691 +- 0.0085 | -0.9753 +- 0.0097 | -0.9899 +- 0.0153 | 1.51 | 1.14 |
| 1 | 19 | 1 | 0.8346 +- 0.0225 | 1.0020 +- 0.0197 | 0.9835 +- 0.0086 | 1.0014 +- 0.0063 | 0.9913 +- 0.0074 | -3.55 | -2.42 |
| 2 | 2 | -1 | -1.0488 +- 0.0220 | -1.0227 +- 0.0163 | -1.0268 +- 0.0065 | -1.0256 +- 0.0067 | -1.0165 +- 0.0070 | -0.63 | -0.45 |
| 3 | 17 | 1 | 0.9468 +- 0.0224 | 1.0323 +- 0.0154 | 1.0388 +- 0.0061 | 1.0163 +- 0.0069 | 1.0253 +- 0.0109 | -2.74 | -1.53 |
| 4 | 12 | 1 | 0.9988 +- 0.0233 | 0.9957 +- 0.0058 | 0.9898 +- 0.0062 | 1.0015 +- 0.0047 | 0.9982 +- 0.0066 | 0.26 | 0.10 |
| 5 | 31 | 1 | 1.1240 +- 0.0225 | 0.9936 +- 0.0069 | 0.9949 +- 0.0028 | 1.0009 +- 0.0056 | 1.0024 +- 0.0036 | 5.09 | 4.06 |
| 6 | 14 | 1 | 1.0074 +- 0.0213 | 0.9731 +- 0.0086 | 0.9945 +- 0.0032 | 0.9893 +- 0.0070 | 0.9941 +- 0.0041 | 0.52 | 0.97 |
| 7 | 29 | 1 | 1.1332 +- 0.0213 | 0.9906 +- 0.0086 | 1.0008 +- 0.0048 | 0.9992 +- 0.0039 | 0.9887 +- 0.0043 | 4.53 | 4.00 |

Template `bb` (e1+e26, nullity-2):

| bin | label | ideal sign | Tuna-17 corrected ratio | ibm_marrakesh 2026-11-06T200832 | ibm_fez 2026-11-06T201037 | ibm_kingston 2026-11-07T042346 | ibm_fez 2026-11-07T042521 | D(y) z vs ibm_fez | D(y) z vs ibm_marrakesh |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | -1 | -1.0543 +- 0.0262 | -0.9569 +- 0.0086 | -0.9542 +- 0.0108 | -0.9468 +- 0.0115 | -0.9601 +- 0.0117 | -1.94 | -2.52 |
| 1 | 26 | 1 | 1.0065 +- 0.0279 | 1.0117 +- 0.0107 | 1.0133 +- 0.0066 | 1.0052 +- 0.0068 | 1.0127 +- 0.0060 | -0.17 | -0.11 |
| 2 | 3 | 1 | 0.8433 +- 0.0273 | 1.0046 +- 0.0086 | 0.9995 +- 0.0052 | 1.0047 +- 0.0068 | 0.9967 +- 0.0048 | -4.48 | -4.07 |
| 3 | 24 | 1 | 0.9207 +- 0.0276 | 1.0169 +- 0.0114 | 1.0156 +- 0.0073 | 1.0249 +- 0.0105 | 1.0183 +- 0.0068 | -2.32 | -2.05 |
| 4 | 8 | 1 | 1.0926 +- 0.0270 | 1.0215 +- 0.0091 | 0.9879 +- 0.0105 | 0.9959 +- 0.0063 | 0.9975 +- 0.0115 | 2.05 | 1.75 |
| 5 | 19 | 1 | 1.0614 +- 0.0295 | 1.0671 +- 0.0139 | 1.0305 +- 0.0096 | 1.0174 +- 0.0091 | 1.0345 +- 0.0112 | 0.62 | -0.10 |
| 6 | 10 | -1 | -1.0362 +- 0.0262 | -0.9544 +- 0.0150 | -0.9580 +- 0.0110 | -0.9799 +- 0.0113 | -0.9489 +- 0.0112 | -1.49 | -1.45 |
| 7 | 17 | 1 | 0.9851 +- 0.0277 | 0.9886 +- 0.0149 | 1.0085 +- 0.0071 | 1.0137 +- 0.0068 | 1.0121 +- 0.0139 | -0.58 | -0.06 |

Four-term blocks. Both IBM parallel-coset runs and both Ascella jobs read blocks B12/2 and C8/5 of the same four-term operands (the Ascella block ordinal equals the IBM coset). IBM levels are raw P(selector = 00) per arm; Ascella levels appear raw (a) and normalized by the job's anchor and dark readings (a prime; l hat for the pair job, normalized per slot).

| block | census class | arm | ideal | ibm_fez raw P(00) 2026-11-07T042521 | ibm_kingston raw P(00) 2026-11-07T042346 | qpu:ascella four-term raw a | qpu:ascella four-term a prime | qpu:ascella pairs raw a | qpu:ascella pairs l hat | sim:ascella four-term raw a | sim:ascella four-term a prime | sim:ascella pairs raw a | sim:ascella pairs l hat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B12/2 | census-13119 | C | 0.0000 | 0.0208 +- 0.0020 | 0.0143 +- 0.0011 | 0.0007 | -0.0015 | 0.0028 | 0.0010 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| B12/2 | census-13119 | D | 0.0000 | 0.0569 +- 0.0060 | 0.0443 +- 0.0026 | 0.0018 | -0.0005 | - | - | 0.0000 | 0.0000 | - | - |
| B12/2 | census-13119 | D2 | 0.0000 | 0.0576 +- 0.0056 | 0.0447 +- 0.0027 | - | - | - | - | - | - | - | - |
| B12/2 | census-13119 | E0 | 0.2500 | 0.2671 +- 0.0029 | 0.2648 +- 0.0055 | 0.2813 | 0.2800 | 0.2668 | 0.2569 | 0.2483 | 0.2483 | 0.2479 | 0.2472 |
| B12/2 | census-13119 | E1 | 0.2500 | 0.2596 +- 0.0020 | 0.2628 +- 0.0039 | 0.2494 | 0.2480 | - | - | 0.2515 | 0.2515 | - | - |
| B12/2 | census-13119 | F | 0.2500 | 0.2519 +- 0.0019 | 0.2562 +- 0.0039 | 0.2549 | 0.2535 | 0.2895 | 0.2783 | 0.2476 | 0.2476 | 0.2510 | 0.2503 |
| B12/2 | census-13119 | N | 0.5625 | 0.4804 +- 0.0062 | 0.4986 +- 0.0040 | 0.5289 | 0.5284 | 0.5745 | 0.5616 | 0.5602 | 0.5602 | 0.5602 | 0.5591 |
| B12/2 | census-13119 | T | 0.7500 | 0.6565 +- 0.0082 | 0.6813 +- 0.0065 | 0.7417 | 0.7419 | 0.7565 | 0.7479 | 0.7483 | 0.7483 | 0.7468 | 0.7461 |
| C8/5 | census-4415 | C | 0.0000 | 0.0221 +- 0.0021 | 0.0162 +- 0.0016 | - | - | 0.0039 | 0.0020 | - | - | 0.0000 | 0.0000 |
| C8/5 | census-4415 | D | 0.0000 | 0.0593 +- 0.0063 | 0.0439 +- 0.0030 | 0.0044 | 0.0021 | - | - | 0.0000 | 0.0000 | - | - |
| C8/5 | census-4415 | E0 | 0.2500 | 0.2504 +- 0.0038 | 0.2511 +- 0.0041 | - | - | - | - | - | - | - | - |
| C8/5 | census-4415 | E1 | 0.2500 | 0.2489 +- 0.0034 | 0.2467 +- 0.0034 | - | - | - | - | - | - | - | - |
| C8/5 | census-4415 | F | 0.0691 | 0.1096 +- 0.0045 | 0.0993 +- 0.0034 | 0.0660 | 0.0640 | 0.0817 | 0.0771 | 0.0700 | 0.0700 | 0.0703 | 0.0701 |
| C8/5 | census-4415 | N | 0.4523 | 0.3898 +- 0.0038 | 0.4036 +- 0.0028 | - | - | 0.4741 | 0.4574 | - | - | 0.4530 | 0.4517 |
| C8/5 | census-4415 | T | 0.6545 | 0.5529 +- 0.0072 | 0.5835 +- 0.0086 | 0.6293 | 0.6292 | 0.6496 | 0.6391 | 0.6528 | 0.6528 | 0.6544 | 0.6536 |

## Pivot c: sim:ascella against qpu:ascella

Each pair is one reading of the simulator job and the same reading of the QPU job (the same setting, block and arm); the delta is qpu minus sim.

| family | observable | calibration | pairs | median delta | median abs delta | max abs delta | largest at (setting block arm) |
|---|---|---|---|---|---|---|---|
| four-term | level | raw | 44 | 0.0011 | 0.0042 | 0.0331 | null-b12-2 B12/2 E0 |
| four-term | level | anchor_dark_normalized | 44 | -0.0009 | 0.0046 | 0.0333 | b12-6 B12/6 N |
| pairs | level | raw | 46 | 0.0105 | 0.0121 | 0.0421 | i-f-TD C8/7 T |
| pairs | level | per_slot_anchor_dark | 46 | 0.0035 | 0.0077 | 0.0310 | c-d-TN B12/3 T |
| pairs | mirror_difference | per_slot_anchor_dark | 46 | 0.0248 | 0.0248 | 0.1032 | a-h-NN C8/6 N |

four-term level (anchor_dark_normalized), every reading:

| setting | block | arm | control | ideal | sim:ascella | qpu:ascella | qpu - sim |
|---|---|---|---|---|---|---|---|
| anchor-early | A16/4 | D | anchor | 0.0000 | 0.0000 | 0.0017 | 0.0017 |
| anchor-early | A16/4 | T | anchor | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| anchor-late | A16/4 | D | anchor | 0.0000 | 0.0000 | 0.0013 | 0.0013 |
| anchor-late | A16/4 | T | anchor | 1.0000 | 1.0000 | 1.0000 | -0.0000 |
| b12-2 | B12/2 | C | cocycle-free | 0.0000 | 0.0000 | -0.0015 | -0.0015 |
| b12-2 | B12/2 | D | primary | 0.0000 | 0.0000 | -0.0005 | -0.0005 |
| b12-2 | B12/2 | F | primary | 0.2500 | 0.2476 | 0.2535 | 0.0059 |
| b12-2 | B12/2 | N | mutation | 0.5625 | 0.5602 | 0.5284 | -0.0318 |
| b12-2 | B12/2 | T | primary | 0.7500 | 0.7483 | 0.7419 | -0.0064 |
| b12-3 | B12/3 | D | primary | 0.0000 | 0.0000 | -0.0010 | -0.0010 |
| b12-3 | B12/3 | F | primary | 0.0833 | 0.0825 | 0.0892 | 0.0068 |
| b12-3 | B12/3 | N | mutation | 0.5833 | 0.5801 | 0.5892 | 0.0090 |
| b12-3 | B12/3 | T | primary | 0.7500 | 0.7494 | 0.7370 | -0.0124 |
| b12-6 | B12/6 | C | cocycle-free | 0.0833 | 0.0834 | 0.0789 | -0.0044 |
| b12-6 | B12/6 | D | primary | 0.0000 | 0.0000 | -0.0008 | -0.0008 |
| b12-6 | B12/6 | F | primary | 0.0833 | 0.0844 | 0.0819 | -0.0025 |
| b12-6 | B12/6 | N | mutation | 0.5833 | 0.5814 | 0.5481 | -0.0333 |
| b12-6 | B12/6 | T | primary | 0.7500 | 0.7495 | 0.7326 | -0.0169 |
| b12-7 | B12/7 | C | cocycle-free | 0.0000 | 0.0000 | -0.0009 | -0.0009 |
| b12-7 | B12/7 | D | primary | 0.0000 | 0.0000 | 0.0002 | 0.0002 |
| b12-7 | B12/7 | F | primary | 0.2500 | 0.2495 | 0.2457 | -0.0038 |
| b12-7 | B12/7 | N | mutation | 0.5625 | 0.5642 | 0.5469 | -0.0173 |
| b12-7 | B12/7 | T | primary | 0.7500 | 0.7523 | 0.7571 | 0.0047 |
| c8-4 | C8/4 | C | cocycle-free | 0.9472 | 0.9475 | 0.9525 | 0.0050 |
| c8-4 | C8/4 | D | primary | 0.0000 | 0.0000 | -0.0002 | -0.0002 |
| c8-4 | C8/4 | F | primary | 0.0691 | 0.0698 | 0.0741 | 0.0043 |
| c8-4 | C8/4 | N | mutation | 0.4523 | 0.4549 | 0.4635 | 0.0085 |
| c8-4 | C8/4 | T | primary | 0.6545 | 0.6574 | 0.6311 | -0.0263 |
| c8-5 | C8/5 | D | primary | 0.0000 | 0.0000 | 0.0021 | 0.0021 |
| c8-5 | C8/5 | F | primary | 0.0691 | 0.0700 | 0.0640 | -0.0060 |
| c8-5 | C8/5 | T | primary | 0.6545 | 0.6528 | 0.6292 | -0.0236 |
| c8-6 | C8/6 | C | cocycle-free | 0.0528 | 0.0526 | 0.0593 | 0.0067 |
| c8-6 | C8/6 | D | primary | 0.0000 | 0.0000 | -0.0005 | -0.0005 |
| c8-6 | C8/6 | F | primary | 0.0691 | 0.0695 | 0.0686 | -0.0009 |
| c8-6 | C8/6 | N | mutation | 0.4523 | 0.4488 | 0.4591 | 0.0103 |
| c8-6 | C8/6 | T | primary | 0.6545 | 0.6555 | 0.6304 | -0.0251 |
| c8-7 | C8/7 | D | primary | 0.0000 | 0.0000 | -0.0012 | -0.0012 |
| c8-7 | C8/7 | F | primary | 0.0691 | 0.0707 | 0.0630 | -0.0077 |
| c8-7 | C8/7 | T | primary | 0.6545 | 0.6552 | 0.6772 | 0.0220 |
| null-b12-2 | B12/2 | E0 | null | 0.2500 | 0.2483 | 0.2800 | 0.0317 |
| null-b12-2 | B12/2 | E1 | null | 0.2500 | 0.2515 | 0.2480 | -0.0035 |
| reference-b12-0 | B12/0 | D | reference | 0.0000 | 0.0000 | -0.0012 | -0.0012 |
| reference-b12-0 | B12/0 | F | reference | 0.0000 | 0.0000 | -0.0012 | -0.0012 |
| reference-b12-0 | B12/0 | T | reference | 0.5000 | 0.5020 | 0.4942 | -0.0078 |

pairs level (per_slot_anchor_dark), every reading:

| setting | block | arm | control | ideal | sim:ascella | qpu:ascella | qpu - sim |
|---|---|---|---|---|---|---|---|
| a-f-FF | B12/0 | F | primary | 0.0000 | 0.0000 | 0.0043 | 0.0043 |
| a-f-FF | C8/4 | F | primary | 0.0691 | 0.0690 | 0.0717 | 0.0027 |
| a-g-TC | B12/0 | T | primary | 0.5000 | 0.5013 | 0.5227 | 0.0214 |
| a-g-TC | C8/5 | C | cocycle-free | 0.0000 | 0.0000 | 0.0020 | 0.0020 |
| a-h-CC | B12/0 | C | cocycle-free | 0.0000 | 0.0000 | 0.0010 | 0.0010 |
| a-h-CC | C8/6 | C | cocycle-free | 0.0528 | 0.0534 | 0.0609 | 0.0075 |
| a-h-NN | B12/0 | N | mutation | 0.3750 | 0.3717 | 0.3939 | 0.0222 |
| a-h-NN | C8/6 | N | mutation | 0.4523 | 0.4521 | 0.4538 | 0.0016 |
| b-f-EE | B12/2 | E0 | null | 0.2500 | 0.2472 | 0.2569 | 0.0097 |
| b-f-EE | C8/4 | E1 | null | 0.2500 | 0.2501 | 0.2669 | 0.0169 |
| b-g-FF | B12/2 | F | primary | 0.2500 | 0.2503 | 0.2783 | 0.0281 |
| b-g-FF | C8/5 | F | primary | 0.0691 | 0.0701 | 0.0771 | 0.0071 |
| b-i-CC | B12/2 | C | cocycle-free | 0.0000 | 0.0000 | 0.0010 | 0.0010 |
| b-i-CC | C8/7 | C | cocycle-free | 0.0000 | 0.0000 | 0.0011 | 0.0011 |
| b-i-NN | B12/2 | N | mutation | 0.5625 | 0.5591 | 0.5616 | 0.0025 |
| b-i-NN | C8/7 | N | mutation | 0.4523 | 0.4547 | 0.4719 | 0.0173 |
| c-d-TC | B12/3 | T | primary | 0.7500 | 0.7506 | 0.7601 | 0.0095 |
| c-d-TC | B12/6 | C | cocycle-free | 0.0833 | 0.0820 | 0.0900 | 0.0079 |
| c-d-TD | B12/3 | T | primary | 0.7500 | 0.7513 | 0.7562 | 0.0050 |
| c-d-TD | B12/6 | D | primary | 0.0000 | 0.0000 | 0.0016 | 0.0016 |
| c-d-TN | B12/3 | T | primary | 0.7500 | 0.7468 | 0.7158 | -0.0310 |
| c-d-TN | B12/6 | N | mutation | 0.5833 | 0.5845 | 0.6105 | 0.0260 |
| c-d-TT | B12/3 | T | primary | 0.7500 | 0.7487 | 0.7435 | -0.0052 |
| c-d-TT | B12/6 | T | primary | 0.7500 | 0.7506 | 0.7549 | 0.0043 |
| c-h-FF | B12/3 | F | primary | 0.0833 | 0.0830 | 0.0851 | 0.0021 |
| c-h-FF | C8/6 | F | primary | 0.0691 | 0.0687 | 0.0691 | 0.0003 |
| d-i-FF | B12/6 | F | primary | 0.0833 | 0.0833 | 0.0917 | 0.0084 |
| d-i-FF | C8/7 | F | primary | 0.0691 | 0.0686 | 0.0737 | 0.0051 |
| e-b-TT | B12/2 | T | primary | 0.7500 | 0.7461 | 0.7479 | 0.0018 |
| e-b-TT | B12/7 | T | primary | 0.7500 | 0.7524 | 0.7406 | -0.0118 |
| e-c-NN | B12/3 | N | mutation | 0.5833 | 0.5822 | 0.5940 | 0.0118 |
| e-c-NN | B12/7 | N | mutation | 0.5625 | 0.5623 | 0.5355 | -0.0268 |
| e-g-CN | B12/7 | C | cocycle-free | 0.0000 | 0.0000 | 0.0003 | 0.0003 |
| e-g-CN | C8/5 | N | mutation | 0.4523 | 0.4517 | 0.4574 | 0.0057 |
| e-h-FT | B12/7 | F | primary | 0.2500 | 0.2478 | 0.2646 | 0.0168 |
| e-h-FT | C8/6 | T | primary | 0.6545 | 0.6540 | 0.6603 | 0.0063 |
| g-h-TT | C8/5 | T | primary | 0.6545 | 0.6536 | 0.6391 | -0.0145 |
| g-h-TT | C8/6 | T | primary | 0.6545 | 0.6527 | 0.6382 | -0.0145 |
| i-f-TC | C8/4 | C | cocycle-free | 0.9472 | 0.9455 | 0.9304 | -0.0151 |
| i-f-TC | C8/7 | T | primary | 0.6545 | 0.6544 | 0.6413 | -0.0131 |
| i-f-TD | C8/4 | D | primary | 0.0000 | 0.0000 | 0.0019 | 0.0019 |
| i-f-TD | C8/7 | T | primary | 0.6545 | 0.6544 | 0.6770 | 0.0226 |
| i-f-TN | C8/4 | N | mutation | 0.4523 | 0.4523 | 0.4695 | 0.0171 |
| i-f-TN | C8/7 | T | primary | 0.6545 | 0.6533 | 0.6295 | -0.0238 |
| i-f-TT | C8/4 | T | primary | 0.6545 | 0.6525 | 0.6591 | 0.0066 |
| i-f-TT | C8/7 | T | primary | 0.6545 | 0.6520 | 0.6267 | -0.0253 |

pairs mirror_difference (per_slot_anchor_dark), every reading:

| setting | block | arm | control | ideal | sim:ascella | qpu:ascella | qpu - sim |
|---|---|---|---|---|---|---|---|
| a-f-FF | B12/0 | F | primary | 0.0000 | 0.0000 | 0.0084 | 0.0084 |
| a-f-FF | C8/4 | F | primary | 0.0000 | 0.0032 | 0.0095 | 0.0063 |
| a-g-TC | B12/0 | T | primary | 0.0000 | 0.0043 | 0.0480 | 0.0437 |
| a-g-TC | C8/5 | C | cocycle-free | 0.0000 | 0.0000 | 0.0010 | 0.0010 |
| a-h-CC | B12/0 | C | cocycle-free | 0.0000 | 0.0000 | 0.0019 | 0.0019 |
| a-h-CC | C8/6 | C | cocycle-free | 0.0000 | 0.0006 | 0.0180 | 0.0173 |
| a-h-NN | B12/0 | N | mutation | 0.0000 | 0.0007 | 0.0594 | 0.0588 |
| a-h-NN | C8/6 | N | mutation | 0.0000 | 0.0050 | 0.1082 | 0.1032 |
| b-f-EE | B12/2 | E0 | null | 0.0000 | 0.0015 | 0.0250 | 0.0235 |
| b-f-EE | C8/4 | E1 | null | 0.0000 | 0.0009 | 0.0383 | 0.0374 |
| b-g-FF | B12/2 | F | primary | 0.0000 | 0.0041 | 0.0575 | 0.0534 |
| b-g-FF | C8/5 | F | primary | 0.0000 | 0.0016 | 0.0048 | 0.0032 |
| b-i-CC | B12/2 | C | cocycle-free | 0.0000 | 0.0000 | 0.0014 | 0.0014 |
| b-i-CC | C8/7 | C | cocycle-free | 0.0000 | 0.0000 | 0.0016 | 0.0016 |
| b-i-NN | B12/2 | N | mutation | 0.0000 | 0.0041 | 0.0695 | 0.0654 |
| b-i-NN | C8/7 | N | mutation | 0.0000 | 0.0016 | 0.0792 | 0.0776 |
| c-d-TC | B12/3 | T | primary | 0.0000 | 0.0056 | 0.0104 | 0.0048 |
| c-d-TC | B12/6 | C | cocycle-free | 0.0000 | 0.0028 | 0.0235 | 0.0207 |
| c-d-TD | B12/3 | T | primary | 0.0000 | 0.0036 | 0.0715 | 0.0679 |
| c-d-TD | B12/6 | D | primary | 0.0000 | 0.0000 | 0.0006 | 0.0006 |
| c-d-TN | B12/3 | T | primary | 0.0000 | 0.0024 | 0.0674 | 0.0650 |
| c-d-TN | B12/6 | N | mutation | 0.0000 | 0.0004 | 0.0992 | 0.0987 |
| c-d-TT | B12/3 | T | primary | 0.0000 | 0.0005 | 0.0496 | 0.0491 |
| c-d-TT | B12/6 | T | primary | 0.0000 | 0.0022 | 0.0732 | 0.0710 |
| c-h-FF | B12/3 | F | primary | 0.0000 | 0.0010 | 0.0147 | 0.0137 |
| c-h-FF | C8/6 | F | primary | 0.0000 | 0.0015 | 0.0158 | 0.0143 |
| d-i-FF | B12/6 | F | primary | 0.0000 | 0.0007 | 0.0058 | 0.0051 |
| d-i-FF | C8/7 | F | primary | 0.0000 | 0.0013 | 0.0063 | 0.0050 |
| e-b-TT | B12/2 | T | primary | 0.0000 | 0.0001 | 0.1006 | 0.1004 |
| e-b-TT | B12/7 | T | primary | 0.0000 | 0.0035 | 0.0866 | 0.0831 |
| e-c-NN | B12/3 | N | mutation | 0.0000 | 0.0007 | 0.0268 | 0.0261 |
| e-c-NN | B12/7 | N | mutation | 0.0000 | 0.0033 | 0.0001 | -0.0032 |
| e-g-CN | B12/7 | C | cocycle-free | 0.0000 | 0.0000 | 0.0004 | 0.0004 |
| e-g-CN | C8/5 | N | mutation | 0.0000 | 0.0020 | 0.0592 | 0.0573 |
| e-h-FT | B12/7 | F | primary | 0.0000 | 0.0022 | 0.0010 | -0.0012 |
| e-h-FT | C8/6 | T | primary | 0.0000 | 0.0012 | 0.0383 | 0.0371 |
| g-h-TT | C8/5 | T | primary | 0.0000 | 0.0024 | 0.0741 | 0.0716 |
| g-h-TT | C8/6 | T | primary | 0.0000 | 0.0066 | 0.0384 | 0.0317 |
| i-f-TC | C8/4 | C | cocycle-free | 0.0000 | 0.0031 | 0.0834 | 0.0803 |
| i-f-TC | C8/7 | T | primary | 0.0000 | 0.0045 | 0.0552 | 0.0507 |
| i-f-TD | C8/4 | D | primary | 0.0000 | 0.0000 | 0.0019 | 0.0019 |
| i-f-TD | C8/7 | T | primary | 0.0000 | 0.0045 | 0.0025 | -0.0021 |
| i-f-TN | C8/4 | N | mutation | 0.0000 | 0.0034 | 0.0016 | -0.0018 |
| i-f-TN | C8/7 | T | primary | 0.0000 | 0.0007 | 0.0579 | 0.0572 |
| i-f-TT | C8/4 | T | primary | 0.0000 | 0.0008 | 0.0510 | 0.0502 |
| i-f-TT | C8/7 | T | primary | 0.0000 | 0.0002 | 0.0170 | 0.0167 |

## Pivot d: ledger rows against their readings

Each check applies the row's own threshold to the table readings that the row's evidence column cites. Rows whose evidence is a conjecture log are marked as such and checked only for the table premise they use.

| ledger row | stated status | claim | readings used | what the table shows | agreement |
|---|---|---|---|---|---|
| A5-177 | certified | the nullity of L_(e_i + t e_j) equals the number of XOR pairs {k, k ^ (i ^ j)} on which L_i^T (t L_j) carri... | none | exhaustive census (census.json); no hardware reading | not a table claim |
| A5-178 | certified | the 4 x 4 coset blocks of four-term flat operands realize 5 of the 12 equivalence classes of 4 x 4 +-1 matr... | none | exhaustive census (census.json); no hardware reading | not a table claim |
| A5-179 | refuted | the calibrated noise model of ibm_fez predicts kernel-map visibilities 0.49 to 0.58 at 136 to 173 routed CZ... | 11 operand visibilities | 9 deep visibilities span 0.094 to 0.345, all below the model band's 0.49; 2 cocycle-free visibilities span 0.496 to 0.593 against a modeled 0.77 to 0.84; the stated deep range 0.09 to 0.24 omits e1+e17 (null) 0.345 | agrees on status; stated range disagrees |
| A5-180 | survives | one compiled A_5 SELECT on ibm_fez reproduces the cd_core sign network of e1 + e18 (N_hat 12.65 [11.87, 13.... | 4 N_hat readings and 8 sign counts | e1+e10 cocycle-free: -6.78 (ideal -6, interval misses it); e1+e18 mutation: 11.39 (ideal 11, interval covers it); e1+e18 primary: 12.65 (ideal 12, interval covers it); e17-e2 twin: 11.87 (ideal 12, interval covers it); criterion: each within 1.0 of its ideal, the one-unit step of N; sign counts of the deep operands 23 to 31 of 32, 6 below the preregistered 31 | agrees |
| A5-182 | survives | coset blocks of the kernel map at 1 to 20 routed CZ recover the nullity 0, 4, 4, 8, 12, 12 of all six opera... | 16 corrected N_hat, 16 sign counts | 16 corrected N_hat readings; largest deviation 0.1504 (ibm_marrakesh e1+e18 cocycle-free) against the stated 0.15, 1 above 0.15 unrounded and 0 above it rounded to two decimals; 16 of 16 sign counts at 32 | agrees at the stated precision |
| A5-184 | survives | the Tuna-17 coin-arm series reads the A_5 sign network of the coset blocks e1 + e18 and e1 + e26: every one... | 16 bin contrasts, 3 selector contrasts | 16 of 16 bins at the ideal sign, smallest z 25.45 (25.5 at the row's precision); selector contrast ba 0.2350, xor_ba -0.7181 | agrees |
| A5-185 | refuted | the Tuna-17 null block b0 of the coin series reads selector contrast 0, and its readout-corrected ratios ag... | b0 selector contrast and 48 D(y) bins | b0 selector contrast 0.0164 +- 0.0039 (z 4.19); template and device pairs under 7 of 8 bins: ba/ibm_fez 5 of 8, ba/ibm_marrakesh 6 of 8 | agrees |
| A5-186 | survives | hypothesis: one coherent X90 over-rotation of about +0.03 rad produces the Tuna-17 null selector offset, wh... | premise only | rests on conjecture logs, not table readings; the table holds the null offset the mechanism explains: pathion_coset_block_tuna_17_analysis.json +0.0167 +- 0.0055; pathion_coset_coin_tuna_17_analysis.json +0.0164 +- 0.0039 | not decidable from the table |
| A5-187 | survives | the Tuna-17 ba misses against IBM follow the logical bit d2 (main effect +0.066 in ba, +0.044 in bb, +0.063... | 16 D(y) bins, premise only | rests on conjecture logs, not table readings; failing `ba` bins (ibm_fez: bins [1, 5, 7]; ibm_marrakesh: bins [5, 7]) all have d0 = 1 | premise holds; mechanism not decidable from the table |
| A5-188 | survives | qpu:ascella realizes the pathion-only 4 x 4 coset blocks of B12 and C8 (ideal levels 0.75 and 0.6545), one ... | 8 top-vector levels, 11 mutated-arm levels | 8 of 8 T levels and 11 of 11 C and N levels within 0.07; C8 T spread 0.0480 | agrees |
| A5-189 | refuted | two coset blocks per Ascella photon read independently within 0.07 on qpu:ascella with per-slot anchors and... | 46 qpu and 46 sim mirror differences | 9 of 46 qpu mirror differences exceed 0.07 against an allowance of 4; 0 of 46 on sim:ascella | agrees |
| A5-190 | refuted | per-mode detection efficiencies explain the mirror failure of the two-block job and the C8 spread of the on... | 46 qpu mirror differences | observed median 0.0259 and maximum 0.1082; the efficiency model's prediction (median 0.0026, maximum 0.0155) is in conjecture logs, not the table | observed values agree |
| A5-191 | survives | hypothesis: the mirror failure of the two-block job follows the per-slot anchor calibration, with a static ... | 46 sim mirror differences | sim:ascella maximum 0.0066, 0 of 46 over 0.07; the anchor and phase mechanism rests on conjecture logs | sim statement agrees |
