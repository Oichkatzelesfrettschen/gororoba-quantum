# Unapproved QPU case: rank-sector

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-8192-per-pub` with per-PUB shot allocation (used tiers: 1024, 4096, 8192; 3 jobs). Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-14T113945.518703Z`.
- [record.json](record.json) SHA-256: `e39aaccec1c6cd3c64cb034602ac52089688633a4b167d1d20143f5c88c38c8b`.
- [isa.qpy](isa.qpy) SHA-256: `bac329070162e4e003ddc9155057bd8638e31f6564b8fcfc4eb52d7c1a2aad9e`.
- Experiment source digest: `4d9fafa97c54ca8eadeb4b17527acac648c431f7ae9497c78602a2075e8ebe48`.
- Source commit: `c84c4905fff70371f176055881108f3790b8c7eb`; sources_modified=`false`.
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
| rank_sector_0 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[59, 55, 74, 75]` | `[[94, 95, 92, 93]]` |
| rank_sector_1 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[55, 59, 75, 74]` | `[[80, 81, 82, 83]]` |
| rank_sector_2 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[75, 74, 55, 59]` | `[[15, 14, 35, 19]]` |
| rank_sector_3 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[59, 55, 74, 75]` | `[[67, 68, 47, 57]]` |
| rank_sector_4 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[75, 59, 55, 74]` | `[[75, 74, 73, 59]]` |
| rank_sector_5 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[75, 59, 55, 74]` | `[[105, 106, 107, 104]]` |
| rank_sector_6 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[75, 59, 55, 74]` | `[[126, 125, 124, 127]]` |
| rank_sector_7 | ibm_kingston | 2026-10-14T03:51:35-07:00 | 20261010 | `[75, 59, 55, 74]` | `[[2, 1, 0, 3]]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "measurement_sites": {
    "rank_sector_0_basis_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_basis_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_basis_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_basis_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_basis_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_two_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_two_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_two_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1_reference": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1_reference": [
      [
        93
      ],
      [
        94
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
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_persistent_kernel_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_persistent_kernel_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_zero_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_zero_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_zero_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_zero_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_one_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_one_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_one_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_pulse_one_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_persistent_kernel_t1d1_reference": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_4_bright_t1d1_reference": [
      [
        75
      ],
      [
        74
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
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_persistent_kernel_t3d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_persistent_kernel_t2d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_zero_two_t0d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_zero_two_t1d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_zero_two_t3d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_zero_two_t2d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_one_two_t0d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_one_two_t1d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_one_two_t3d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_pulse_one_two_t2d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t0d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t1d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t1d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t3d2": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t2d1": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_persistent_kernel_t1d1_reference": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_6_bright_t1d1_reference": [
      [
        126
      ],
      [
        125
      ]
    ],
    "rank_sector_7_persistent_kernel_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_persistent_kernel_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_persistent_kernel_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_zero_two_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_zero_two_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_zero_two_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_one_two_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_one_two_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_pulse_one_two_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t0d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t1d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t1d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t3d2": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t2d1": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ],
    "rank_sector_7_bright_t1d1_reference": [
      [
        2
      ],
      [
        1
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "rank_sector_0": [
      {
        "55": 95,
        "59": 94,
        "74": 92,
        "75": 93
      }
    ],
    "rank_sector_1": [
      {
        "55": 80,
        "59": 81,
        "74": 83,
        "75": 82
      }
    ],
    "rank_sector_2": [
      {
        "55": 35,
        "59": 19,
        "74": 14,
        "75": 15
      }
    ],
    "rank_sector_3": [
      {
        "55": 68,
        "59": 67,
        "74": 47,
        "75": 57
      }
    ],
    "rank_sector_4": [
      {
        "55": 73,
        "59": 74,
        "74": 59,
        "75": 75
      }
    ],
    "rank_sector_5": [
      {
        "55": 107,
        "59": 106,
        "74": 104,
        "75": 105
      }
    ],
    "rank_sector_6": [
      {
        "55": 124,
        "59": 125,
        "74": 127,
        "75": 126
      }
    ],
    "rank_sector_7": [
      {
        "55": 0,
        "59": 1,
        "74": 3,
        "75": 2
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

The noise model predicts 0.488433837891; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.475629286992.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.370849609375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.358045058476.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.501251220703; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.488446669805.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.331634521484; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.318829970586.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.256439208984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.243634658086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.492492675781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.479688124883.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0689086914062; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0561041405076.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0471801757812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0343756248826.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0838012695312; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0709967186326.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.25634765625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.243543105351.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.497131347656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.484326796758.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.356079101562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.343274550664.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.504791259766; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.491986708867.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.17724609375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.164441542851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0320434570312; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0192389061326.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.490478515625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.477673964726.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.667755126953; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.654950576055.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.956268310547; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.943463759648.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.578247070312; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.565442519414.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.260375976562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.247571425664.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_0_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.909088134766; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.883479032968.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.883479032968, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_0_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0018310546875; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0237780471097.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000762939453125; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0248461623441.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.482757568359; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.469953017461.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.364196777344; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.351392226445.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487152099609; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.474347548711.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.324798583984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.311994033086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252471923828; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.23966737293.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485778808594; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.472974257695.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0880737304688; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0752691795701.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0490112304688; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0362066795701.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0624694824219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0496649315233.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.140472412109; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.127667861211.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.490783691406; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.477979140508.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.224914550781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.212109999883.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.269592285156; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.256787734258.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.108551025391; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.095746474492.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0323486328125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0195440819139.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.483642578125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.470838027226.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.632476806641; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.619672255742.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.924743652344; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.911939101445.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.585754394531; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.572949843633.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.368316650391; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.355512099492.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_1_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.875732421875; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.850123320078.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.850123320078, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_1_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00216674804688; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0234423537504.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000946044921875; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0246630568754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.477996826172; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.465192275273.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.358917236328; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.34611268543.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.485717773438; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.472913222539.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.321655273438; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.308850722539.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.251190185547; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.238385634648.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.474914550781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.462109999883.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0909118652344; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0781073143358.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0590209960938; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0462164451951.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0672302246094; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0544256737108.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.140960693359; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.128156142461.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480499267578; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.46769471668.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.22607421875; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.213269667851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.272766113281; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.259961562383.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.111511230469; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0987066795701.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0371398925781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0243353416795.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.473480224609; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.460675673711.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.626251220703; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.613446669805.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.912506103516; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.899701552617.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.576934814453; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.564130263555.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.363037109375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.350232558476.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_2_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.853485107422; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.827876005625.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.827876005625, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_2_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00103759765625; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.024571504141.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -3.0517578125e-05; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0256396193754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489685058594; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.476880507695.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.373718261719; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.36091371082.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.503082275391; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.490277724492.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.334564208984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.321759658086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.259674072266; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.246869521367.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.493804931641; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.481000380742.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0751953125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0623907616014.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0567626953125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0439581444139.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0908203125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0780157616014.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.259826660156; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.247022109258.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.498260498047; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.485455947148.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.359252929688; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.346448378789.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.506896972656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.494092421758.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.182220458984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.169415908086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0388793945312; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0260748436326.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.49169921875; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.478894667851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.665435791016; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.652631240117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950592041016; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.937787490117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.576568603516; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.563764052617.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.263092041016; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.250287490117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_3_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.893829345703; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.868220243906.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.868220243906, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_3_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.002197265625; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0234118361722.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00152587890625; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.024083222891.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0317077636719; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0189032127733.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0217590332031; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0089544823045.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0234375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0106329491014.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0140991210938; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00129457019513.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0110473632812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.00175718761737.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.03173828125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0189337303514.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.54833984375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.535535292851.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.959838867188; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.947034316289.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.308166503906; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.295361953008.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0267639160156; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.013959365117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.961151123047; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.948346572148.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.152984619141; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.140180068242.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0243225097656; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.011517958867.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0283813476562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0155767967576.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0197143554688; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00690980457013.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.963256835938; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.950452285039.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.734893798828; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.72208924793.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.959777832031; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.946973281133.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.957611083984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.944806533086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.956756591797; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.943952040898.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_4_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.936340332031; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.910731230234.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.910731230234, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.0018310546875; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0274401564847.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.001220703125; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0243883986722.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_minus_rank_sector_4_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.5166015625; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.490992460703.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.490992460703, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_one_two_t1d2_minus_rank_sector_4_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.128662109375; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.103053007578.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0485636997466; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0467889682212 (null 0 plus one-sided radius 0.0467889682212). The admitted alternative effect is 0.103053007578, with conditional target power 0.8 and lower-tail radius 0.0237097988966. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_zero_two_t3d2_minus_rank_sector_4_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.281402587891; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.255793486093.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.255793486093, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0332641601562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0204596092576.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0313110351562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0185064842576.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0386352539062; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0258307030076.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0225524902344; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00974793933575.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0162963867188; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00349183582013.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.034912109375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0221075584764.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.541839599609; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.529035048711.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949310302734; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.936505751836.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.304779052734; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.291974501836.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0270385742188; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0142340233201.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.948913574219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.93610902332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.159301757812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.146497206914.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0399780273438; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0271734764451.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0410461425781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0282415916795.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0320129394531; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0192083885545.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951873779297; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.939069228398.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.725982666016; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.713178115117.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947967529297; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.935162978398.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.945007324219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.93220277332.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.943878173828; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.93107362293.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_5_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.909332275391; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.883723173593.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.883723173593, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0256091017972.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0008544921875; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0247546096097.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_minus_rank_sector_5_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.506927490234; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.481318388437.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.481318388437, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_one_two_t1d2_minus_rank_sector_5_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.119323730469; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.0937146286715.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0485636997466; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0467889682212 (null 0 plus one-sided radius 0.0467889682212). The admitted alternative effect is 0.0937146286715, with conditional target power 0.8 and lower-tail radius 0.0237097988966. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_zero_two_t3d2_minus_rank_sector_5_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.277740478516; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.252131376718.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.252131376718, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0268249511719; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0140204002733.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0351867675781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0223822166795.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0474243164062; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0346197655076.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0238952636719; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0110907127733.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0138244628906; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.001019911992.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0282592773438; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0154547264451.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.539825439453; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.527020888555.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947265625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.934461074101.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.30078125; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.287976699101.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0213623046875; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00855775378888.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946075439453; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.933270888555.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.166046142578; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.15324159168.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0497741699219; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0369696190233.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0515441894531; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0387396385545.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.043212890625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0304083397264.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950561523438; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.937756972539.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.726165771484; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.713361220586.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946075439453; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.933270888555.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947235107422; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.934430556523.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.943542480469; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.93073792957.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_6_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.898651123047; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.87304202125.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.87304202125, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000335693359375; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0259447951566.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000885009765625; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0247240920316.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_minus_rank_sector_6_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.511566162109; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.485957060312.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.485957060312, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_one_two_t1d2_minus_rank_sector_6_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.116271972656; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.090662870859.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0485636997466; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0467889682212 (null 0 plus one-sided radius 0.0467889682212). The admitted alternative effect is 0.090662870859, with conditional target power 0.8 and lower-tail radius 0.0237097988966. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_zero_two_t3d2_minus_rank_sector_6_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.279418945312; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.253809843515.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.253809843515, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0449829101562; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0321783592576.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0305786132812; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0177740623826.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0330505371094; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0202459862108.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.018310546875; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.00550599597638.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.011962890625; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is -0.000841660273623.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0463256835938; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0335211326951.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.545593261719; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.53278871082.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951141357422; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.938336806523.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.314086914062; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.301282363164.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0390930175781; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0262884666795.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950775146484; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.937970595586.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.157257080078; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.14445252918.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0355224609375; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0227179100389.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0233944841106; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0377807617188; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0249762108201.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0296325683594; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.0168280174608.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.954254150391; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.941449599492.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.729309082031; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.716504531133.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950103759766; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.937299208867.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949798583984; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.936994033086.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947235107422; the simultaneous finite-simulation allowance is +/-0.0128045508986. The lower modeled value is 0.934430556523.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0661695934278; requested precision is 0.08.

### rank_sector_7_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.917053222656; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.891444120859.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.891444120859, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -3.0517578125e-05; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0256396193754.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00042724609375; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is -0.0251818557035.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_minus_rank_sector_7_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.499267578125; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.473658476328.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.473658476328, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_one_two_t1d2_minus_rank_sector_7_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.121734619141; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.0961255173434.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0485636997466; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0467889682212 (null 0 plus one-sided radius 0.0467889682212). The admitted alternative effect is 0.0961255173434, with conditional target power 0.8 and lower-tail radius 0.0237097988966. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_zero_two_t3d2_minus_rank_sector_7_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.274993896484; the simultaneous finite-simulation allowance is +/-0.0256091017972. The lower modeled value is 0.249384794687.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.137358885641; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.132339186856 (null 0 plus one-sided radius 0.132339186856). The admitted alternative effect is 0.249384794687, with conditional target power 0.8 and lower-tail radius 0.0670614383215. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 232 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| latency_stress | 4.6 | 60 | 41.744316928 |

The largest nominal/scenario charge is 41.744316928 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 15 | 15360 | 6.22853504 | 25 |
| ibm_kingston/static/2 | 19 | 77824 | 22.125344512 | 25 |
| ibm_kingston/static/3 | 2 | 16384 | 6.490437376 | 25 |

The cost model predicts 34.844316928 seconds. The per-job service ceilings sum to 75 seconds against an invocation cap of 75 seconds. The global reserve is 60 seconds; the saved quota reports 390 seconds remaining.

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

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_12 | 8192 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_13 | 8192 | 5.764e-06 | 0.00025 | 0 | 0 |

Job `ibm_kingston/static/3` adds 2.3 seconds of modeled overhead.

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
  --shots 8192 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 25 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096,8192 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 75.0 \
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
  --shots 8192 \
  --seeds 2 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 25 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 1024,4096,8192 \
  --replica-tiers 1 \
  --optimizer-candidates 2 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 75.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-14T113945.518703Z \
  --approved-record-sha256 e39aaccec1c6cd3c64cb034602ac52089688633a4b167d1d20143f5c88c38c8b \
  --submit
```
