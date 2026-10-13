# Unapproved QPU case: rank-sector

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096-per-pub` with per-PUB shot allocation (used tiers: 1024, 4096; 2 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-12T195828.029302Z`.
- [record.json](record.json) SHA-256: `74ac892864d222180125f1050e148293e264b194f0b66d0bd892d6f05d6284b2`.
- [isa.qpy](isa.qpy) SHA-256: `fbf129f9edd014a60a326243c7e7200818b4282d67c1a5b43e19cae1328ca857`.
- Experiment source digest: `91e64dab6f8a5db8a41ac88c33f3e4860b82d33e5719fee30160bb7de63def9d`.
- Source commit: `f9bdbbe814c28d335ea2d0a3423be8218c0f5e7d`; sources_modified=`false`.
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
| rank_sector_0 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261010 | `[93, 94, 73, 79]` |
| rank_sector_1 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261010 | `[94, 93, 79, 73]` |
| rank_sector_2 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261010 | `[79, 73, 94, 93]` |
| rank_sector_3 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261010 | `[93, 94, 73, 79]` |
| rank_sector_4 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_5 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_6 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_7 | ibm_kingston | 2026-10-12T12:14:06-07:00 | 20261011 | `[79, 93, 94, 73]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "measurement_sites": {
    "rank_sector_0_basis_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_basis_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_basis_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_basis_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_basis_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_two_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_two_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_two_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t0d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t1d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t3d2": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t2d1": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1_reference": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1_reference": [
      [
        94
      ],
      [
        93
      ]
    ],
    "rank_sector_1_basis_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_basis_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_basis_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_basis_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_basis_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_two_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_two_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_two_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1_reference": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1_reference": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_2_basis_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_basis_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_basis_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_basis_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_basis_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_two_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_two_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_two_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_3_basis_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_basis_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_basis_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_basis_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_basis_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_two_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_two_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_two_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_4_persistent_kernel_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_persistent_kernel_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_persistent_kernel_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_zero_two_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_zero_two_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_zero_two_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_one_two_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_one_two_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_pulse_one_two_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t0d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t1d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t1d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t3d2": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t2d1": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1_reference": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_4_bright_t1d1_reference": [
      [
        82
      ],
      [
        81
      ]
    ],
    "rank_sector_5_persistent_kernel_t0d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_persistent_kernel_t3d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_persistent_kernel_t2d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_zero_two_t0d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_zero_two_t3d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_zero_two_t2d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_one_two_t0d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_one_two_t3d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_pulse_one_two_t2d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t0d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t1d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t1d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t3d2": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t2d1": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1_reference": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_5_bright_t1d1_reference": [
      [
        152
      ],
      [
        151
      ]
    ],
    "rank_sector_6_persistent_kernel_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_persistent_kernel_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_persistent_kernel_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_zero_two_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_zero_two_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_zero_two_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_one_two_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_one_two_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_pulse_one_two_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t0d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t1d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t1d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t3d2": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t2d1": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1_reference": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_6_bright_t1d1_reference": [
      [
        71
      ],
      [
        58
      ]
    ],
    "rank_sector_7_persistent_kernel_t0d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_persistent_kernel_t3d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_persistent_kernel_t2d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_zero_two_t0d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_zero_two_t3d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_zero_two_t2d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_one_two_t0d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_one_two_t3d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_pulse_one_two_t2d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t0d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t1d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t1d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t3d2": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t2d1": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1_reference": [
      [
        109
      ],
      [
        108
      ]
    ],
    "rank_sector_7_bright_t1d1_reference": [
      [
        109
      ],
      [
        108
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "rank_sector_0": [
      {
        "73": 95,
        "79": 94,
        "93": 93,
        "94": 92
      }
    ],
    "rank_sector_1": [
      {
        "73": 104,
        "79": 105,
        "93": 117,
        "94": 125
      }
    ],
    "rank_sector_2": [
      {
        "73": 14,
        "79": 15,
        "93": 19,
        "94": 35
      }
    ],
    "rank_sector_3": [
      {
        "73": 3,
        "79": 2,
        "93": 1,
        "94": 0
      }
    ],
    "rank_sector_4": [
      {
        "73": 83,
        "79": 82,
        "93": 81,
        "94": 80
      }
    ],
    "rank_sector_5": [
      {
        "73": 153,
        "79": 152,
        "93": 151,
        "94": 150
      }
    ],
    "rank_sector_6": [
      {
        "73": 70,
        "79": 71,
        "93": 58,
        "94": 51
      }
    ],
    "rank_sector_7": [
      {
        "73": 118,
        "79": 109,
        "93": 108,
        "94": 107
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

The noise model predicts 0.488929748535; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.482527473086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.360916137695; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.354513862246.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489143371582; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.482741096133.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.323585510254; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.317183234805.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.251251220703; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.244848945254.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489761352539; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.48335907709.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0576095581055; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0512072826562.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.028076171875; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0216738964257.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0718841552734; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0654818798241.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.24976348877; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.24336121332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489974975586; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.483572700137.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.349105834961; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.342703559512.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.49063873291; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.484236457461.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.163764953613; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.157362678164.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0216751098633; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.015272834414.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489891052246; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.483488776797.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.668212890625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.661810615176.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.953552246094; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.947149970644.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.574462890625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.568060615176.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.251174926758; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.244772651309.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.925476074219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.91267152332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.91267152332, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_0_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000480651855469; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0123238990432.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000160217285156; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0129647681838.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485961914062; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.479559638613.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.362869262695; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.356466987246.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486968994141; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.480566718691.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.322158813477; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.315756538027.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252883911133; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.246481635684.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486740112305; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.480337836855.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0852432250977; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0788409496483.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0437240600586; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0373217846093.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0598068237305; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0534045482812.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.139099121094; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.132696845644.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487571716309; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.481169440859.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.22257232666; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.216170051211.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.264961242676; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.258558967226.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.103179931641; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0967776561913.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0301818847656; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0237796093163.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.486862182617; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.480459907168.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.640419006348; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.634016730898.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.931373596191; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.924971320742.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.591163635254; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.584761359805.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.367134094238; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.360731818789.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.887649536133; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.874844985234.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.874844985234, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_1_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000633239746094; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0121713111525.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000633239746094; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0121713111525.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481788635254; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.475386359805.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.359672546387; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.353270270937.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489952087402; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.483549811953.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.322135925293; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.315733649844.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252555847168; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.246153571719.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481452941895; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.475050666445.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0884323120117; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0820300365624.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0515747070312; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0451724315819.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0635681152344; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0571658397851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.140411376953; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.134009101504.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.482261657715; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.475859382266.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.226142883301; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.219740607851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.271636962891; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.265234687441.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.106674194336; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.100271918887.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0332107543945; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0268084789452.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481803894043; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.475401618594.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.637908935547; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.631506660098.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.929420471191; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.923018195742.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.587692260742; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.581289985293.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.364593505859; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.35819123041.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.87784576416; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.865041213262.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.865041213262, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_2_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000465393066406; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0123391578322.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00131225585938; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0114922950392.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.492156982422; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.485754706973.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.365119934082; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.358717658633.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.495292663574; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.488890388125.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.327087402344; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.320685126894.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.253662109375; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.247259833926.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.493194580078; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.486792304629.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.059211730957; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0528094555077.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0298690795898; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0234668041405.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0734024047852; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0670001293358.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.25227355957; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.245871284121.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.493583679199; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.48718140375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.352996826172; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.346594550723.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.496726989746; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.490324714297.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.166809082031; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.160406806582.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0232925415039; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0168902660546.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.493179321289; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.48677704584.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.67440032959; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.667998054141.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.962799072266; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.956396796816.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.5791015625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.572699287051.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.253715515137; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.247313239687.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.932929992676; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.920125441777.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.920125441777, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_3_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000526428222656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.012278122676.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000137329101562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0129418800002.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0308837890625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0244815136132.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0266418457031; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0202395702538.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0314025878906; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0250003124413.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0177612304688; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0113589550194.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0128479003906; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00644562494131.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0307312011719; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0243289257226.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.538864135742; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.532461860293.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.940483093262; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.934080817812.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.296745300293; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.290343024844.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0249862670898; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0185839916405.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.94164276123; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.935240485781.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.154449462891; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.148047187441.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0322189331055; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0258166576562.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0356369018555; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0292346264062.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0276412963867; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0212390209374.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.944046020508; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.937643745059.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.722961425781; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.716559150332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.940269470215; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.933867194766.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.937889099121; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.931486823672.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.937103271484; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.930700996035.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.908866882324; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.896062331426.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.896062331426, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0128045508986.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000511169433594; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.012293381465.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_minus_rank_sector_4_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.50813293457; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.495328383672.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.495328383672, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_one_two_t1d2_minus_rank_sector_4_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.122230529785; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.109425978887.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.109425978887, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_zero_two_t3d2_minus_rank_sector_4_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.271759033203; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.258954482305.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.258954482305, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0320587158203; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.025656440371.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0255432128906; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0191409374413.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0294723510742; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0230700756249.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0184860229492; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0120837474999.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0142593383789; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00785706292959.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.03173828125; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0253360058007.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.545196533203; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.538794257754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.952682495117; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.946280219668.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.299499511719; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.293097236269.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0230712890625; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0166690136132.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.957962036133; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.951559760684.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.155372619629; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.14897034418.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0305709838867; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0241687084374.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0338516235352; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0274493480858.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0250854492188; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0186831737694.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.959861755371; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.953459479922.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.73250579834; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.726103522891.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.95263671875; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.946234443301.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.94994354248; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943541267031.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949897766113; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943495490664.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.923164367676; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.910359816777.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.910359816777, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000274658203125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0125298926955.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000167846679688; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0126367042189.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_minus_rank_sector_5_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.513458251953; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.500653701055.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.500653701055, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_one_two_t1d2_minus_rank_sector_5_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.124801635742; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.111997084844.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.111997084844, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_zero_two_t3d2_minus_rank_sector_5_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.276428222656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.263623671758.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.263623671758, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0266799926758; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0202777172265.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0246505737305; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0182482982812.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0288314819336; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0224292064843.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0170974731445; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0106951976952.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0122909545898; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00588867914053.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.026611328125; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0202090526757.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.54264831543; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.53624603998.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.952903747559; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.946501472109.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.296226501465; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.289824226016.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0214385986328; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0150363231835.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.953826904297; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.947424628848.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.154075622559; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.147673347109.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0298233032227; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0234210277733.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0328216552734; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0264193798241.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0242767333984; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0178744579491.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.955352783203; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.948950507754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.73078918457; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.724386909121.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.953216552734; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.946814277285.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949562072754; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943159797305.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.948905944824; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.942503669375.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.924385070801; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.911580519902.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.911580519902, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 8.39233398438e-05; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0127206275588.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000679016113281; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0121255347853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_minus_rank_sector_6_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.516036987305; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.503232436406.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.503232436406, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_one_two_t1d2_minus_rank_sector_6_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.124252319336; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.111447768437.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.111447768437, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_zero_two_t3d2_minus_rank_sector_6_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.274787902832; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.261983351933.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.261983351933, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.029655456543; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0232531810937.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0279693603516; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0215670849023.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0344619750977; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0280596996483.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0193099975586; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0129077221093.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0134658813477; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.00706360589834.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0295639038086; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0231616283593.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.543312072754; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.536909797305.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949440002441; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943037726992.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.298896789551; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.292494514101.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0236587524414; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0172564769921.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949508666992; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943106391543.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.15731048584; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.150908210391.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0355606079102; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0291583324608.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0380706787109; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0316684032616.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0295944213867; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.0231921459374.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.95133972168; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.94493744623.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.729423522949; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.7230212475.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949485778809; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.943083503359.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.944892883301; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.938490607851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.943504333496; the simultaneous finite-simulation allowance is +/-0.00640227544931. The lower modeled value is 0.937102058047.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.915023803711; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.902219252812.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.902219252812, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -6.103515625e-05; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0128655860549.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000442504882812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.0123620460158.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_minus_rank_sector_7_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.513748168945; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.500943618047.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.500943618047, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_one_two_t1d2_minus_rank_sector_7_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.12174987793; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.108945327031.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.108945327031, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_zero_two_t3d2_minus_rank_sector_7_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.275238037109; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.262433486211.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.262433486211, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

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
| ibm_kingston/static/1 | 15 | 15360 | 6.22853504 | 30 |
| ibm_kingston/static/2 | 21 | 86016 | 24.2205632 | 30 |

The cost model predicts 30.44909824 seconds. The per-job service ceilings sum to 60 seconds against an invocation cap of 60 seconds. The global reserve is 60 seconds; the saved quota reports 551 seconds remaining.

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
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
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
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --optimize \
  --backends ibm_kingston \
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
  --approved-record ../results/live/2026-10-12T195828.029302Z \
  --approved-record-sha256 74ac892864d222180125f1050e148293e264b194f0b66d0bd892d6f05d6284b2 \
  --submit
```
