# Unapproved QPU case: rank-sector

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096-per-pub` with per-PUB shot allocation (used tiers: 1024, 4096; 2 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-13T031726.380783Z`.
- [record.json](record.json) SHA-256: `5563c7e59b7e3a90d49cecefed223d354afcbbbacc121d7d2f3899455c6e37f6`.
- [isa.qpy](isa.qpy) SHA-256: `403e859eeca7839d8e5e89f305b9cd3dd247bf10c167cef2df9bfa652b5ec459`.
- Experiment source digest: `7ef53372c68e8b1fd7b4cb76bc51ff3a71241747dbf66cd3e4b4e4e2774de6ee`.
- Source commit: `ee6608ba481f304f8e3a21573e027a7ba0b5fb86`; sources_modified=`false`.
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

| Group | Backend | Calibration | Transpiler seed | Initial layout |
|---|---|---|---:|---|
| rank_sector_0 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261011 | `[144, 143, 142, 136]` |
| rank_sector_1 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261011 | `[143, 142, 144, 136]` |
| rank_sector_2 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261011 | `[143, 142, 144, 136]` |
| rank_sector_3 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261010 | `[124, 125, 136, 123]` |
| rank_sector_4 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261010 | `[136, 144, 143, 142]` |
| rank_sector_5 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261010 | `[136, 144, 143, 142]` |
| rank_sector_6 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261010 | `[136, 144, 143, 142]` |
| rank_sector_7 | ibm_fez | 2026-10-12T19:20:46-07:00 | 20261010 | `[136, 144, 143, 142]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "measurement_sites": {
    "rank_sector_0_basis_t0d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_basis_t1d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_basis_t1d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_basis_t3d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_basis_t2d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t0d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t3d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t2d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_two_t0d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_two_t3d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_two_t2d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t0d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t1d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t3d2": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t2d1": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1_reference": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1_reference": [
      [
        121
      ],
      [
        122
      ]
    ],
    "rank_sector_1_basis_t0d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_basis_t1d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_basis_t1d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_basis_t3d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_basis_t2d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t0d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t3d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t2d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_two_t0d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_two_t3d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_two_t2d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t0d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t1d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t3d2": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t2d1": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1_reference": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1_reference": [
      [
        143
      ],
      [
        142
      ]
    ],
    "rank_sector_2_basis_t0d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_basis_t1d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_basis_t1d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_basis_t3d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_basis_t2d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t0d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t3d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t2d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_two_t0d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_two_t3d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_two_t2d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t0d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t1d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t3d2": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t2d1": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1_reference": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1_reference": [
      [
        3
      ],
      [
        2
      ]
    ],
    "rank_sector_3_basis_t0d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_basis_t1d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_basis_t1d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_basis_t3d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_basis_t2d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t0d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t3d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t2d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_two_t0d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_two_t3d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_two_t2d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t0d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t1d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t3d2": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t2d1": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1_reference": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1_reference": [
      [
        138
      ],
      [
        151
      ]
    ],
    "rank_sector_4_persistent_kernel_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_persistent_kernel_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_persistent_kernel_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_zero_two_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_zero_two_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_zero_two_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_one_two_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_one_two_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_pulse_one_two_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t0d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t1d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t1d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t3d2": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t2d1": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1_reference": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_4_bright_t1d1_reference": [
      [
        105
      ],
      [
        106
      ]
    ],
    "rank_sector_5_persistent_kernel_t0d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_persistent_kernel_t3d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_persistent_kernel_t2d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_zero_two_t0d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_zero_two_t3d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_zero_two_t2d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_one_two_t0d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_one_two_t3d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_pulse_one_two_t2d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t0d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t1d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t1d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t3d2": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t2d1": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1_reference": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_5_bright_t1d1_reference": [
      [
        25
      ],
      [
        26
      ]
    ],
    "rank_sector_6_persistent_kernel_t0d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_persistent_kernel_t3d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_persistent_kernel_t2d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_zero_two_t0d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_zero_two_t3d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_zero_two_t2d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_one_two_t0d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_one_two_t3d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_pulse_one_two_t2d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t0d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t1d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t1d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t3d2": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t2d1": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1_reference": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_6_bright_t1d1_reference": [
      [
        87
      ],
      [
        86
      ]
    ],
    "rank_sector_7_persistent_kernel_t0d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_persistent_kernel_t3d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_persistent_kernel_t2d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_zero_two_t0d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_zero_two_t3d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_zero_two_t2d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_one_two_t0d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_one_two_t3d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_pulse_one_two_t2d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t0d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t1d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t1d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t3d2": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t2d1": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1_reference": [
      [
        51
      ],
      [
        50
      ]
    ],
    "rank_sector_7_bright_t1d1_reference": [
      [
        51
      ],
      [
        50
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "rank_sector_0": [
      {
        "136": 120,
        "142": 122,
        "143": 121,
        "144": 116
      }
    ],
    "rank_sector_1": [
      {
        "136": 136,
        "142": 142,
        "143": 143,
        "144": 144
      }
    ],
    "rank_sector_2": [
      {
        "136": 16,
        "142": 2,
        "143": 3,
        "144": 4
      }
    ],
    "rank_sector_3": [
      {
        "123": 138,
        "124": 151,
        "125": 152,
        "136": 131
      }
    ],
    "rank_sector_4": [
      {
        "136": 117,
        "142": 106,
        "143": 105,
        "144": 104
      }
    ],
    "rank_sector_5": [
      {
        "136": 37,
        "142": 26,
        "143": 25,
        "144": 24
      }
    ],
    "rank_sector_6": [
      {
        "136": 97,
        "142": 86,
        "143": 87,
        "144": 88
      }
    ],
    "rank_sector_7": [
      {
        "136": 52,
        "142": 50,
        "143": 51,
        "144": 58
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

The noise model predicts 0.483032226562; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.476426677563.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.358116149902; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.351510600903.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480445861816; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.473840312817.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.321823120117; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.315217571118.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252197265625; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.245591716626.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.483200073242; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.476594524243.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0780487060547; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0714431570553.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0578308105469; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0512252615475.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0907211303711; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0841155813717.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.251190185547; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.244584636547.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.482345581055; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.475740032055.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.34741973877; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.34081418977.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.483261108398; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.476655559399.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.178787231445; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.172181682446.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0454788208008; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0388732718014.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485664367676; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.479058818676.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.639533996582; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.632928447583.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.905776977539; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.89917142854.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.55394744873; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.547341899731.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.254913330078; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.248307781079.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.847946166992; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.834735068993.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.834735068993, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_0_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000373840332031; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0128372576667.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.00122833251953; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0144394305183.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.484870910645; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478265361645.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.364730834961; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.358125285962.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486434936523; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.479829387524.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.322525024414; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.315919475415.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.254005432129; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.24739988313.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485229492188; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478623943188.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0888366699219; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0822311209225.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0495223999023; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.042916850903.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0642471313477; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0576415823483.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.141639709473; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.135034160473.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485969543457; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.479363994458.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.227661132812; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.221055583813.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.27018737793; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.26358182893.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.107299804688; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.100694255688.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0346221923828; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0280166433834.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.484901428223; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478295879223.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.636505126953; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.629899577954.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.924186706543; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.917581157544.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.587905883789; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.58130033479.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.366561889648; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.359956340649.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.874664306641; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.861453208642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.861453208642, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_1_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000228881835938; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0129822161628.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000152587890625; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0130585101081.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487670898438; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.481065349438.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.360748291016; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.354142742016.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.482666015625; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.476060466626.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.323753356934; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.317147807934.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.256607055664; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.250001506665.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485778808594; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.479173259594.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0896453857422; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0830398367428.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0500106811523; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.043405132153.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0673370361328; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0607314871334.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.144317626953; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.137712077954.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488166809082; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.481561260083.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.227668762207; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.221063213208.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.264839172363; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.258233623364.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.112014770508; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.105409221508.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0415954589844; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.034989909985.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489860534668; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.483254985669.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.634101867676; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.627496318676.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.910820007324; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.904214458325.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.578392028809; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.571786479809.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.363929748535; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.357324199536.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.860809326172; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.847598228173.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.847598228173, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_2_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -5.34057617188e-05; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0132645037605.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000244140625; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0129669573738.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.483840942383; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.477235393383.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.367286682129; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.36068113313.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.494598388672; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.487992839672.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.326538085938; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.319932536938.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.255599975586; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.248994426587.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.484855651855; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478250102856.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0740203857422; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0674148367428.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0530471801758; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0464416311764.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0881423950195; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0815368460202.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.254119873047; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.247514324047.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485580444336; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478974895337.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.352745056152; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.346139507153.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.494827270508; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.488221721508.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.176147460938; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.169541911938.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0381851196289; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0315795706295.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.484817504883; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.478211955883.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.656433105469; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.649827556469.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.934120178223; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.927514629223.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.569274902344; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.562669353344.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.256790161133; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.250184612133.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.881072998047; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.867861900048.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.867861900048, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_3_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000694274902344; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0125168230964.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000312805175781; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.012898292823.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0595474243164; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.052941875317.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0386581420898; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0320525930905.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0430679321289; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0364623831295.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0281600952148; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0215545462155.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0221786499023; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.015573100903.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0587844848633; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0521789358639.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.540977478027; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.534371929028.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.934181213379; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.92757566438.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.3076171875; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.301011638501.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0427169799805; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0361114309811.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.935386657715; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.928781108715.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.162040710449; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.15543516145.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0444717407227; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0378661917233.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0417022705078; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0350967215084.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0316925048828; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0250869558834.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.938179016113; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.931573467114.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.718620300293; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.712014751294.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.934112548828; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.927506999829.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.925155639648; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.918550090649.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.922470092773; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.915864543774.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.891044616699; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.8778335187.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.8778335187, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000106811523438; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0133179095222.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000404357910156; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0128067400886.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_minus_rank_sector_4_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.482192993164; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.468981895165.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.468981895165, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_one_two_t1d2_minus_rank_sector_4_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.117568969727; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.104357871728.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.104357871728, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_zero_two_t3d2_minus_rank_sector_4_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.26490020752; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.251689109521.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.251689109521, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0463333129883; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0397277639889.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0328674316406; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0262618826412.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0373840332031; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0307784842037.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0233612060547; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0167556570553.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0178680419922; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0112624929928.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0466461181641; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0400405691647.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.545516967773; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.538911418774.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947319030762; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.940713481762.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.305572509766; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.298966960766.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0339584350586; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0273528860592.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950592041016; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.943986492016.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.159805297852; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.153199748852.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0383987426758; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0317931936764.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0390167236328; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0324111746334.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0302505493164; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.023645000317.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951927185059; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.945321636059.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.728363037109; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.72175748811.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947151184082; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.940545635083.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.940422058105; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.933816509106.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.93824005127; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.93163450227.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.909767150879; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.89655605288.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.89655605288, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 7.62939453125e-05; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0131348040534.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000473022460938; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0127380755378.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_minus_rank_sector_5_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.498870849609; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.485659751611.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.485659751611, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_one_two_t1d2_minus_rank_sector_5_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.121406555176; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.108195457177.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.108195457177, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_zero_two_t3d2_minus_rank_sector_5_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.271614074707; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.258402976708.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.258402976708, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0890197753906; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0824142263912.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0483474731445; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0417419241452.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0453643798828; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0387588308834.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0320663452148; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0254607962155.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.025390625; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0187850760006.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0893173217773; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.082711772778.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.532409667969; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.525804118969.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.904304504395; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.897698955395.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.319107055664; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.312501506665.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0728149414062; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0662093924069.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.909873962402; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.903268413403.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.162406921387; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.155801372387.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.046142578125; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0395370291256.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0456848144531; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0390792654537.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.035758972168; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0291534231686.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.911186218262; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.904580669262.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.698059082031; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.691453533032.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.903915405273; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.897309856274.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.896820068359; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.89021451936.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.895233154297; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.888627605297.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.858551025391; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.845339927392.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.845339927392, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0001220703125; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0130890276863.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000564575195312; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0126465228034.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_minus_rank_sector_6_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.443092346191; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.429881248193.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.429881248193, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_one_two_t1d2_minus_rank_sector_6_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.116264343262; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.103053245263.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.103053245263, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_zero_two_t3d2_minus_rank_sector_6_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.246292114258; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.233081016259.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.233081016259, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0695648193359; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0629592703366.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0343017578125; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0276962088131.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0304107666016; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0238052176022.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0222702026367; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0156646536373.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0176239013672; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0110183523678.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0704803466797; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0638747976803.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.543212890625; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.536607341626.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.932052612305; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.925447063305.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.318092346191; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.311486797192.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0566864013672; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0500808523678.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.935928344727; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.929322795727.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.156204223633; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.149598674633.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0306625366211; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0240569876217.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.031623840332; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.0250182913327.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0232849121094; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.01667936311.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.936164855957; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.929559306958.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.719032287598; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.712426738598.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.931831359863; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.925225810864.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.926780700684; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.920175151684.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.924530029297; the simultaneous finite-simulation allowance is +/-0.00660554899938. The lower modeled value is 0.917924480297.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.901420593262; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.888209495263.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.888209495263, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000167846679688; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0133789446784.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 7.62939453125e-05; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is -0.0131348040534.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_minus_rank_sector_7_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.472732543945; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.459521445947.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.459521445947, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_one_two_t1d2_minus_rank_sector_7_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.125541687012; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.112330589013.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.112330589013, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_zero_two_t3d2_minus_rank_sector_7_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.261405944824; the simultaneous finite-simulation allowance is +/-0.0132110979988. The lower modeled value is 0.248194846825.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.248194846825, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 464 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| latency_stress | 4.6 | 60 | 35.013467136 |

The largest nominal/scenario charge is 35.013467136 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/static/1 | 15 | 15360 | 6.22257536 | 30 |
| ibm_fez/static/2 | 21 | 86016 | 24.190891776 | 30 |

The cost model predicts 30.413467136 seconds. The per-job service ceilings sum to 60 seconds against an invocation cap of 60 seconds. The global reserve is 60 seconds; the saved quota reports 463 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_01 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_02 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_04 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_05 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_06 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_07 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_09 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_10 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_11 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_14 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_15 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_16 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_17 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_19 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_20 | 1024 | 5.376e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/static/1` adds 2.3 seconds of modeled overhead.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_static_pub_03 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_08 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_12 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_13 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_18 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_21 | 4096 | 4.496e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_22 | 4096 | 4.496e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_23 | 4096 | 5.372e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_24 | 4096 | 5.372e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_25 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_26 | 4096 | 5.376e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_27 | 4096 | 3.696e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_28 | 4096 | 3.696e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_29 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_30 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_31 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_32 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_33 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_34 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_35 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |
| ibm_fez_static_pub_36 | 4096 | 3.712e-06 | 0.00025 | 0 | 0 |

Job `ibm_fez/static/2` adds 2.3 seconds of modeled overhead.

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
  --local-compute auto \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 4096 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
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
  --max-total-execution-seconds 60.0 \
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
  --local-compute auto \
  --simulation-threads 12 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 4096 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
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
  --max-total-execution-seconds 60.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-13T031726.380783Z \
  --approved-record-sha256 5563c7e59b7e3a90d49cecefed223d354afcbbbacc121d7d2f3899455c6e37f6 \
  --submit
```
