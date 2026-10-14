# Unapproved QPU case: rank-sector

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096-per-pub` with per-PUB shot allocation (used tiers: 1024, 4096; 2 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-14T214325.271357Z`.
- [record.json](record.json) SHA-256: `2dde22ad03ae0342756b6ec99f5792d7cc50448fc206393d32199b06a5cd6e18`.
- [isa.qpy](isa.qpy) SHA-256: `d79e920aefe534f4dd186b2873dade29905403568029565d817c7f55c9ac96db`.
- Experiment source digest: `4d9fafa97c54ca8eadeb4b17527acac648c431f7ae9497c78602a2075e8ebe48`.
- Source commit: `a2392dc8ab9cbbcaff7e220cad00cb4eaafbb8c1`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.5.2 |
| qiskit-aer | 0.17.2 |
| qiskit-ibm-runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The rank-sector family measures the selector-success norm of each four-dimensional sector of the specified dimension-32 multiplication path. Two data and two selector qubits implement each sector with coefficient-dependent LCU normalization. Fixed probe and parameter bindings share one routed template per sector. Persistent-kernel, exceptional-point and bright probes test bounded norm predictions. A finite noisy frequency cannot certify an exact rank, an exact zero, or the topology of the full zero-divisor space.

The family retains every declared scientific member and explicit packed/isolated row. Each lane has one physical placement, and simultaneous lanes share a shot index. The execution PUB manifests in record.json bind the exact condition, lane, registers, and neighboring workload. Comparisons across different physical patches retain patch and routing confounds unless a matched crossover is explicitly recorded.

Calibration-based simulation supplies conditional gate/readout predictions and statistical admission. Physical crosstalk, common disturbances, initialization, drift and scheduler effects require the future hardware observations. The simultaneous intervals allow arbitrary within-shot dependence; independent stationary repetitions remain an assumption. Packing-control intervals measure the observed distortion for their stated representatives, rather than certifying every possible packed edge or condition.

Raw outcomes and joint shot order, calibration windows, executed schedules, and final charged usage must be retained. Model residuals and uncertainty remain visible in measured visualizations. The family is independently admitted from the folded-QPE and N21 cases.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| rank_sector_0_basis_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_0_basis_t1d2 | `[0.3671875, 0.1640625, 0.328645833333, 0.140104166667]` |
| rank_sector_0_basis_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_0_basis_t3d2 | `[0.326446280992, 0.177685950413, 0.323553719008, 0.172314049587]` |
| rank_sector_0_basis_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_0_kernel_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_0_kernel_at_one_t1d2 | `[0.0390625, 0.024308251406, 0.656770833333, 0.27985841526]` |
| rank_sector_0_kernel_at_one_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_0_kernel_at_one_t3d2 | `[0.053719008264, 0.177685950413, 0.596280991736, 0.172314049587]` |
| rank_sector_0_kernel_at_one_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_0_kernel_at_two_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_0_kernel_at_two_t1d2 | `[0.3515625, 0.1640625, 0.344270833333, 0.140104166667]` |
| rank_sector_0_kernel_at_two_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_0_kernel_at_two_t3d2 | `[0.152892561983, 0.349459584222, 0.497107438017, 0.000540415778]` |
| rank_sector_0_kernel_at_two_t2d1 | `[0.0, 0.5, 0.5, 0.0]` |
| rank_sector_0_bright_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_0_bright_at_one_t1d2 | `[0.6953125, 0.303816748594, 0.000520833333, 0.000349918073]` |
| rank_sector_0_bright_at_one_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_0_bright_at_one_t3d2 | `[0.599173553719, 0.177685950413, 0.050826446281, 0.172314049587]` |
| rank_sector_0_bright_at_one_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_0_kernel_at_one_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_0_bright_at_one_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_1_basis_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_1_basis_t1d2 | `[0.3671875, 0.1640625, 0.328645833333, 0.140104166667]` |
| rank_sector_1_basis_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_1_basis_t3d2 | `[0.326446280992, 0.177685950413, 0.323553719008, 0.172314049587]` |
| rank_sector_1_basis_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_1_kernel_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_1_kernel_at_one_t1d2 | `[0.0546875, 0.094185375703, 0.641145833333, 0.209981290964]` |
| rank_sector_1_kernel_at_one_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_1_kernel_at_one_t3d2 | `[0.028925619835, 0.091799133509, 0.621074380165, 0.258200866491]` |
| rank_sector_1_kernel_at_one_t2d1 | `[0.125, 0.125, 0.375, 0.375]` |
| rank_sector_1_kernel_at_two_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_1_kernel_at_two_t1d2 | `[0.2109375, 0.1640625, 0.484895833333, 0.140104166667]` |
| rank_sector_1_kernel_at_two_t1d1 | `[0.25, 0.0, 0.75, 0.0]` |
| rank_sector_1_kernel_at_two_t3d2 | `[0.078512396694, 0.177685950413, 0.571487603306, 0.172314049587]` |
| rank_sector_1_kernel_at_two_t2d1 | `[0.0, 0.25, 0.5, 0.25]` |
| rank_sector_1_bright_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_1_bright_at_one_t1d2 | `[0.6796875, 0.233939624297, 0.016145833333, 0.07022704237]` |
| rank_sector_1_bright_at_one_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_1_bright_at_one_t3d2 | `[0.623966942149, 0.263572767317, 0.026033057851, 0.086427232683]` |
| rank_sector_1_bright_at_one_t2d1 | `[0.375, 0.375, 0.125, 0.125]` |
| rank_sector_1_kernel_at_one_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_1_bright_at_one_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_2_basis_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_2_basis_t1d2 | `[0.3671875, 0.1640625, 0.328645833333, 0.140104166667]` |
| rank_sector_2_basis_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_2_basis_t3d2 | `[0.326446280992, 0.177685950413, 0.323553719008, 0.172314049587]` |
| rank_sector_2_basis_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_2_kernel_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_2_kernel_at_one_t1d2 | `[0.0546875, 0.094185375703, 0.641145833333, 0.209981290964]` |
| rank_sector_2_kernel_at_one_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_2_kernel_at_one_t3d2 | `[0.028925619835, 0.091799133509, 0.621074380165, 0.258200866491]` |
| rank_sector_2_kernel_at_one_t2d1 | `[0.125, 0.125, 0.375, 0.375]` |
| rank_sector_2_kernel_at_two_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_2_kernel_at_two_t1d2 | `[0.2109375, 0.1640625, 0.484895833333, 0.140104166667]` |
| rank_sector_2_kernel_at_two_t1d1 | `[0.25, 0.0, 0.75, 0.0]` |
| rank_sector_2_kernel_at_two_t3d2 | `[0.078512396694, 0.177685950413, 0.571487603306, 0.172314049587]` |
| rank_sector_2_kernel_at_two_t2d1 | `[0.0, 0.25, 0.5, 0.25]` |
| rank_sector_2_bright_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_2_bright_at_one_t1d2 | `[0.6796875, 0.233939624297, 0.016145833333, 0.07022704237]` |
| rank_sector_2_bright_at_one_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_2_bright_at_one_t3d2 | `[0.623966942149, 0.263572767317, 0.026033057851, 0.086427232683]` |
| rank_sector_2_bright_at_one_t2d1 | `[0.375, 0.375, 0.125, 0.125]` |
| rank_sector_2_kernel_at_one_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_2_bright_at_one_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_3_basis_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_3_basis_t1d2 | `[0.3671875, 0.1640625, 0.328645833333, 0.140104166667]` |
| rank_sector_3_basis_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_3_basis_t3d2 | `[0.326446280992, 0.177685950413, 0.323553719008, 0.172314049587]` |
| rank_sector_3_basis_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_3_kernel_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_3_kernel_at_one_t1d2 | `[0.0390625, 0.024308251406, 0.656770833333, 0.27985841526]` |
| rank_sector_3_kernel_at_one_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_3_kernel_at_one_t3d2 | `[0.053719008264, 0.177685950413, 0.596280991736, 0.172314049587]` |
| rank_sector_3_kernel_at_one_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_3_kernel_at_two_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_3_kernel_at_two_t1d2 | `[0.3515625, 0.1640625, 0.344270833333, 0.140104166667]` |
| rank_sector_3_kernel_at_two_t1d1 | `[0.5, 0.0, 0.5, 0.0]` |
| rank_sector_3_kernel_at_two_t3d2 | `[0.152892561983, 0.349459584222, 0.497107438017, 0.000540415778]` |
| rank_sector_3_kernel_at_two_t2d1 | `[0.0, 0.5, 0.5, 0.0]` |
| rank_sector_3_bright_at_one_t0d1 | `[0.5, 0.5, 0.0, 0.0]` |
| rank_sector_3_bright_at_one_t1d2 | `[0.6953125, 0.303816748594, 0.000520833333, 0.000349918073]` |
| rank_sector_3_bright_at_one_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_3_bright_at_one_t3d2 | `[0.599173553719, 0.177685950413, 0.050826446281, 0.172314049587]` |
| rank_sector_3_bright_at_one_t2d1 | `[0.25, 0.25, 0.25, 0.25]` |
| rank_sector_3_kernel_at_one_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_3_bright_at_one_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_persistent_kernel_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_4_persistent_kernel_t1d2 | `[0.0, 0.25, 0.6, 0.15]` |
| rank_sector_4_persistent_kernel_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_4_persistent_kernel_t3d2 | `[0.0, 0.011824633209, 0.3, 0.688175366791]` |
| rank_sector_4_persistent_kernel_t2d1 | `[0.0, 0.0, 0.0, 1.0]` |
| rank_sector_4_pulse_zero_two_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_4_pulse_zero_two_t1d2 | `[0.5625, 0.25, 0.0375, 0.15]` |
| rank_sector_4_pulse_zero_two_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_pulse_zero_two_t3d2 | `[0.297520661157, 0.698919168443, 0.002479338843, 0.001080831557]` |
| rank_sector_4_pulse_zero_two_t2d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_4_pulse_one_two_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_pulse_one_two_t1d2 | `[0.140625, 0.078125, 0.651041666667, 0.130208333333]` |
| rank_sector_4_pulse_one_two_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_4_pulse_one_two_t3d2 | `[0.00826446281, 0.0, 0.99173553719, 0.0]` |
| rank_sector_4_pulse_one_two_t2d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_4_bright_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_bright_t1d2 | `[0.765625, 0.078125, 0.026041666667, 0.130208333333]` |
| rank_sector_4_bright_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_bright_t3d2 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_bright_t2d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_4_persistent_kernel_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_4_bright_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_persistent_kernel_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_5_persistent_kernel_t1d2 | `[0.0, 0.25, 0.6, 0.15]` |
| rank_sector_5_persistent_kernel_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_5_persistent_kernel_t3d2 | `[0.0, 0.011824633209, 0.3, 0.688175366791]` |
| rank_sector_5_persistent_kernel_t2d1 | `[0.0, 0.0, 0.0, 1.0]` |
| rank_sector_5_pulse_zero_two_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_5_pulse_zero_two_t1d2 | `[0.5625, 0.25, 0.0375, 0.15]` |
| rank_sector_5_pulse_zero_two_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_pulse_zero_two_t3d2 | `[0.297520661157, 0.698919168443, 0.002479338843, 0.001080831557]` |
| rank_sector_5_pulse_zero_two_t2d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_5_pulse_one_two_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_pulse_one_two_t1d2 | `[0.140625, 0.078125, 0.651041666667, 0.130208333333]` |
| rank_sector_5_pulse_one_two_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_5_pulse_one_two_t3d2 | `[0.00826446281, 0.0, 0.99173553719, 0.0]` |
| rank_sector_5_pulse_one_two_t2d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_5_bright_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_bright_t1d2 | `[0.765625, 0.078125, 0.026041666667, 0.130208333333]` |
| rank_sector_5_bright_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_bright_t3d2 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_bright_t2d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_5_persistent_kernel_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_5_bright_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_persistent_kernel_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_6_persistent_kernel_t1d2 | `[0.0, 0.25, 0.6, 0.15]` |
| rank_sector_6_persistent_kernel_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_6_persistent_kernel_t3d2 | `[0.0, 0.011824633209, 0.3, 0.688175366791]` |
| rank_sector_6_persistent_kernel_t2d1 | `[0.0, 0.0, 0.0, 1.0]` |
| rank_sector_6_pulse_zero_two_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_6_pulse_zero_two_t1d2 | `[0.5625, 0.25, 0.0375, 0.15]` |
| rank_sector_6_pulse_zero_two_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_pulse_zero_two_t3d2 | `[0.297520661157, 0.698919168443, 0.002479338843, 0.001080831557]` |
| rank_sector_6_pulse_zero_two_t2d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_6_pulse_one_two_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_pulse_one_two_t1d2 | `[0.140625, 0.078125, 0.651041666667, 0.130208333333]` |
| rank_sector_6_pulse_one_two_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_6_pulse_one_two_t3d2 | `[0.00826446281, 0.0, 0.99173553719, 0.0]` |
| rank_sector_6_pulse_one_two_t2d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_6_bright_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_bright_t1d2 | `[0.765625, 0.078125, 0.026041666667, 0.130208333333]` |
| rank_sector_6_bright_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_bright_t3d2 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_bright_t2d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_6_persistent_kernel_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_6_bright_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_persistent_kernel_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_7_persistent_kernel_t1d2 | `[0.0, 0.25, 0.6, 0.15]` |
| rank_sector_7_persistent_kernel_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_7_persistent_kernel_t3d2 | `[0.0, 0.011824633209, 0.3, 0.688175366791]` |
| rank_sector_7_persistent_kernel_t2d1 | `[0.0, 0.0, 0.0, 1.0]` |
| rank_sector_7_pulse_zero_two_t0d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_7_pulse_zero_two_t1d2 | `[0.5625, 0.25, 0.0375, 0.15]` |
| rank_sector_7_pulse_zero_two_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_pulse_zero_two_t3d2 | `[0.297520661157, 0.698919168443, 0.002479338843, 0.001080831557]` |
| rank_sector_7_pulse_zero_two_t2d1 | `[0.0, 1.0, 0.0, 0.0]` |
| rank_sector_7_pulse_one_two_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_pulse_one_two_t1d2 | `[0.140625, 0.078125, 0.651041666667, 0.130208333333]` |
| rank_sector_7_pulse_one_two_t1d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_7_pulse_one_two_t3d2 | `[0.00826446281, 0.0, 0.99173553719, 0.0]` |
| rank_sector_7_pulse_one_two_t2d1 | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_7_bright_t0d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_bright_t1d2 | `[0.765625, 0.078125, 0.026041666667, 0.130208333333]` |
| rank_sector_7_bright_t1d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_bright_t3d2 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_bright_t2d1 | `[1.0, 0.0, 0.0, 0.0]` |
| rank_sector_7_persistent_kernel_t1d1_reference | `[0.0, 0.0, 1.0, 0.0]` |
| rank_sector_7_bright_t1d1_reference | `[1.0, 0.0, 0.0, 0.0]` |

| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |
|---|---|---|---:|---|---|
| rank_sector_0 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 73, 92, 93]` | `[[19, 35, 14, 15]]` |
| rank_sector_1 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261011 | `[73, 79, 93, 92]` | `[[80, 81, 82, 83]]` |
| rank_sector_2 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[93, 92, 73, 79]` | `[[94, 95, 92, 93]]` |
| rank_sector_3 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 73, 92, 93]` | `[[67, 68, 47, 57]]` |
| rank_sector_4 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 93, 92, 73]` | `[[2, 1, 0, 3]]` |
| rank_sector_5 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 93, 92, 73]` | `[[105, 106, 107, 104]]` |
| rank_sector_6 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 93, 92, 73]` | `[[75, 74, 73, 59]]` |
| rank_sector_7 | ibm_kingston | 2026-10-14T14:25:47-07:00 | 20261010 | `[79, 93, 92, 73]` | `[[71, 58, 51, 70]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "measurement_sites": {
    "rank_sector_0_basis_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_basis_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_basis_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_basis_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_basis_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_two_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_two_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_two_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_basis_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_basis_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_basis_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_basis_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_basis_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_two_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_two_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_two_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1_reference": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1_reference": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_2_basis_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_basis_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_basis_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_basis_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_basis_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_two_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_two_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_two_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1_reference": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1_reference": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_3_basis_t0d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_basis_t1d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_basis_t1d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_basis_t3d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_basis_t2d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t0d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t3d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t2d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_two_t0d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_two_t3d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_two_t2d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t0d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t1d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t3d2": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t2d1": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1_reference": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1_reference": [
      [
        57
      ],
      [
        67
      ]
    ],
    "rank_sector_4_persistent_kernel_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_zero_two_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_zero_two_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_zero_two_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_one_two_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_one_two_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_pulse_one_two_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_bright_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_5_persistent_kernel_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_zero_two_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_zero_two_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_zero_two_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_one_two_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_one_two_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_pulse_one_two_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1_reference": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_bright_t1d1_reference": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_6_persistent_kernel_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_persistent_kernel_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_persistent_kernel_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_zero_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_zero_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_zero_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_one_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_one_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_pulse_one_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1_reference": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_6_bright_t1d1_reference": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_7_persistent_kernel_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_zero_two_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_zero_two_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_zero_two_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_one_two_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_one_two_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_pulse_one_two_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1_reference": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_bright_t1d1_reference": [
      [
        71
      ],
      [
        58
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "rank_sector_0": [
      {
        "73": 35,
        "79": 19,
        "92": 14,
        "93": 15
      }
    ],
    "rank_sector_1": [
      {
        "73": 80,
        "79": 81,
        "92": 83,
        "93": 82
      }
    ],
    "rank_sector_2": [
      {
        "73": 92,
        "79": 93,
        "92": 95,
        "93": 94
      }
    ],
    "rank_sector_3": [
      {
        "73": 68,
        "79": 67,
        "92": 47,
        "93": 57
      }
    ],
    "rank_sector_4": [
      {
        "73": 3,
        "79": 2,
        "92": 0,
        "93": 1
      }
    ],
    "rank_sector_5": [
      {
        "73": 104,
        "79": 105,
        "92": 107,
        "93": 106
      }
    ],
    "rank_sector_6": [
      {
        "73": 59,
        "79": 75,
        "92": 73,
        "93": 74
      }
    ],
    "rank_sector_7": [
      {
        "73": 70,
        "79": 71,
        "92": 51,
        "93": 58
      }
    ]
  }
}
```

## Preregistered endpoints

Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's PUB grouping. Two-sided intervals report measurement precision.

Directional endpoints also use the planner's one-sided detection radius for the preregistered collection test.

### rank_sector_0_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480155944824; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.473753669375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.363792419434; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.357390143984.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.490539550781; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.484137275332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.323188781738; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.316786506289.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.253112792969; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.246710517519.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480888366699; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.47448609125.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.072883605957; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0664813305077.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0514602661133; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.045057990664.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0862045288086; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0798022533593.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.251396179199; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.24499390375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481727600098; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.475325324648.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.349594116211; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.343191840762.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.491470336914; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.485068061465.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.172714233398; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.166311957949.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0350189208984; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0286166454491.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481132507324; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.474730231875.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.653434753418; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.647032477969.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.930564880371; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.924162604922.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.566619873047; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.560217597598.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.254554748535; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.248152473086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.879104614258; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.866300063359.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.866300063359, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_0_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000724792480469; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0120797584182.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000419616699219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0123849341994.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487442016602; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481039741152.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.366065979004; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.359663703555.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489273071289; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.48287079584.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.324180603027; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.317778327578.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.255012512207; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.248610236758.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.48754119873; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481138923281.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0900573730469; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0836550975976.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0507278442383; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.044325568789.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0653381347656; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0589358593163.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.143249511719; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.136847236269.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488151550293; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481749274844.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.228256225586; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.221853950137.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.271492004395; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.265089728945.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.107925415039; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.10152313959.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0351791381836; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0287768627343.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487701416016; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481299140566.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.638717651367; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.632315375918.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.927963256836; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.921560981387.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.589492797852; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.583090522402.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.366912841797; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.360510566348.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.877235412598; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.864430861699.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.864430861699, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_1_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000648498535156; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0121560523635.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000923156738281; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0118813941603.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488433837891; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.482031562441.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.364219665527; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.357817390078.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488525390625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.482123115176.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.323196411133; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.316794135684.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.253944396973; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.247542121523.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486267089844; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.479864814394.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0834121704102; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0770098949608.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0431518554688; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0367495800194.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.059211730957; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0528094555077.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.14087677002; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.13447449457.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488235473633; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481833198184.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.224571228027; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.218168952578.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.268676757812; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.262274482363.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.104293823242; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0978915477929.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0314788818359; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0250766063866.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487564086914; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481161811465.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.644218444824; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.637816169375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.935096740723; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.928694465273.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.594635009766; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.588232734316.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.368095397949; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.3616931225.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.891944885254; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.879140334355.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.879140334355, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_2_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000740051269531; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0120644996291.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 9.91821289062e-05; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0127053687697.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486618041992; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.480215766543.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.37035369873; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.363951423281.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.500198364258; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.493796088809.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.329162597656; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.322760322207.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.257385253906; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.250982978457.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487983703613; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481581428164.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0753021240234; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0688998485741.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0547409057617; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0483386303124.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.088005065918; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0816027904687.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.255310058594; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.248907783144.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.48811340332; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481711127871.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.355949401855; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.349547126406.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.500686645508; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.494284370059.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.17603302002; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.16963074457.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0356674194336; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0292651439843.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487701416016; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481299140566.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.663200378418; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.656798102969.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946357727051; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.939955451601.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.575675964355; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.569273688906.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.258674621582; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.252272346133.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.891616821289; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.87881227039.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.87881227039, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_3_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0013427734375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0114617774611.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000450134277344; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0123544166213.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0326309204102; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0262286449608.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0247421264648; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0183398510155.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0282897949219; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0218875194726.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0160903930664; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00968811761709.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0117568969727; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00535462152334.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0325546264648; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0261523510155.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.547096252441; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.540693976992.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.954917907715; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.948515632266.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.30290222168; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.29649994623.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0274963378906; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0210940624413.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.955375671387; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.948973395937.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.154304504395; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.147902228945.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0290069580078; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0226046825585.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0322265625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0258242870507.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0240097045898; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0176074291405.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.95726776123; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.950865485781.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.734077453613; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.727675178164.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.955444335938; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.949042060488.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951347351074; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.944945075625.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951049804688; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.944647529238.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.927154541016; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.914349990117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.914349990117, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -7.62939453125e-06; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0128121802932.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000846862792969; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0119576881057.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_minus_rank_sector_4_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.514541625977; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.501737075078.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.501737075078, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_one_two_t1d2_minus_rank_sector_4_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.125297546387; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.112492995488.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.112492995488, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_zero_two_t3d2_minus_rank_sector_4_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.275405883789; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.26260133289.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.26260133289, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0392608642578; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0328585888085.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0303802490234; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0239779735741.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0349807739258; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0285784984765.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0215377807617; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0151355053124.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0164108276367; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0100085521874.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0387420654297; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0323397899804.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.546943664551; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.540541389101.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.95068359375; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.944281318301.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.30451965332; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.298117377871.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0315933227539; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0251910473046.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.95068359375; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.944281318301.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.158584594727; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.152182319277.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0359878540039; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0295855785546.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0378723144531; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0314700390038.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0293197631836; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0229174877343.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.952705383301; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.946303107851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.731132507324; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.724730231875.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950981140137; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.944578864687.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946006774902; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.939604499453.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.944625854492; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.938223579043.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.916000366211; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.903195815312.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.903195815312, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 9.1552734375e-05; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0127129981642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000282287597656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.012522263301.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_minus_rank_sector_5_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.508201599121; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.495397048222.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.495397048222, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_one_two_t1d2_minus_rank_sector_5_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.122596740723; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.109792189824.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.109792189824, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_zero_two_t3d2_minus_rank_sector_5_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.272926330566; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.260121779668.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.260121779668, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.039665222168; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0332629467187.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0268936157227; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0204913402733.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0281448364258; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0217425609765.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0158081054688; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00940583001944.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0111465454102; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00474426996084.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0394821166992; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0330798412499.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.544563293457; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.538161018008.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946731567383; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.940329291934.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.304618835449; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.29821656.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0344848632812; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0280825878319.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.948234558105; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.941832282656.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.154319763184; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.147917487734.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0291137695312; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0227114940819.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0320053100586; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0256030346093.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0244674682617; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0180651928124.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.948928833008; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.942526557559.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.727508544922; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.721106269473.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946952819824; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.940550544375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.944641113281; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.938238837832.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.943977355957; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.937575080508.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.918807983398; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.9060034325.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.9060034325, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000457763671875; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0132623145705.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000198364257812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0126061866408.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_minus_rank_sector_6_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.505081176758; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.492276625859.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.492276625859, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_one_two_t1d2_minus_rank_sector_6_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.125205993652; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.112401442754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.112401442754, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_zero_two_t3d2_minus_rank_sector_6_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.270133972168; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.257329421269.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.257329421269, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0280151367188; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0216128612694.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0214233398438; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0150210643944.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0232009887695; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0167987133202.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0157699584961; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00936768304678.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0125732421875; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00617096673819.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0280456542969; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0216433788476.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.525451660156; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.519049384707.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.92121887207; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.914816596621.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.286964416504; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.280562141055.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0219650268555; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0155627514062.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.922142028809; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.915739753359.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.145774841309; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.139372565859.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.024299621582; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0178973461327.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0273208618164; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0209185863671.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0188369750977; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0124346996483.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.923782348633; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.917380073184.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.706932067871; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.700529792422.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.920303344727; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.913901069277.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.918281555176; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.911879279726.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.917282104492; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.910879829043.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.897102355957; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.884297805058.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.884297805058, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00054931640625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0122552344924.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.00107574462891; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0138802955275.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_minus_rank_sector_7_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.497406005859; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.484601454961.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.484601454961, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_one_two_t1d2_minus_rank_sector_7_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.121475219727; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.108670668828.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.108670668828, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_zero_two_t3d2_minus_rank_sector_7_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.264999389648; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.25219483875.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.25219483875, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 232 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| latency_stress | 4.6 | 60 | 35.04909824 |

The largest nominal/scenario charge is 35.04909824 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 15 | 15360 | 6.22853504 | 27 |
| ibm_kingston/static/2 | 21 | 86016 | 24.2205632 | 27 |

The cost model predicts 30.44909824 seconds. The per-job service ceilings sum to 54 seconds against an invocation cap of 54 seconds. The global reserve is 60 seconds; the saved quota reports 390 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_02 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_04 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_05 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_06 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_07 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_09 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_10 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_11 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_14 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_15 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_16 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_17 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_19 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_20 | 1024 | 5.764e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_03 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_08 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_12 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_13 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_18 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_21 | 4096 | 4.596e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_22 | 4096 | 4.596e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_23 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_24 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_25 | 4096 | 5.728e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_26 | 4096 | 5.728e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_27 | 4096 | 4.464e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_28 | 4096 | 4.464e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_29 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_30 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_31 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_32 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_33 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_34 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_35 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_36 | 4096 | 3.972e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/2` adds 2.3 seconds of modeled overhead.

## Native server qualification

Native server timing remains unqualified for these archived bytes. The charge above is a local planning estimate.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family rank-sector \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --cost-scenario latency_stress:4.6:60.0 \
  --local-compute cpu \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 6 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 4096 \
  --seeds 2 \
  --max-pending 60 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 27 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 131072 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 54.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family rank-sector \
  --shot-allocation per-pub \
  --objective minimum_charge \
  --cost-scenario latency_stress:4.6:60.0 \
  --local-compute cpu \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 6 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
  --shots 4096 \
  --seeds 2 \
  --max-pending 60 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 27 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 131072 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 54.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-14T214325.271357Z \
  --approved-record-sha256 2dde22ad03ae0342756b6ec99f5792d7cc50448fc206393d32199b06a5cd6e18 \
  --submit
```
