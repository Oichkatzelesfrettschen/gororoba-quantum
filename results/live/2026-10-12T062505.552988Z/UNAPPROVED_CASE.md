# Unapproved QPU case: rank-sector

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `candidate-000-shots-4096` at 4096 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-12T062505.552988Z`.
- [record.json](record.json) SHA-256: `f38dfe635415d264eea754e4d699080092ca7272f65e42304fac08f5b4f5fe7d`.
- [isa.qpy](isa.qpy) SHA-256: `8270326960c2339de5c7e5aefb50f98f5498810fc0ebc3db9a0b30e2ed7bee99`.
- Experiment source digest: `493d6d39d1197221d1d4a9610d5b542036e67e24a1323246ba14b828bfbbe085`.
- Source commit: `c998e4aa9a088bf58449dc320b95fff98fa31d6d`; sources_modified=`false`.
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
| rank_sector_0 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261010 | `[79, 73, 94, 93]` |
| rank_sector_1 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261010 | `[94, 93, 79, 73]` |
| rank_sector_2 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261010 | `[2, 3, 0, 1]` |
| rank_sector_3 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261010 | `[79, 73, 94, 93]` |
| rank_sector_4 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_5 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_6 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261011 | `[79, 93, 94, 73]` |
| rank_sector_7 | ibm_kingston | 2026-10-11T22:36:25-07:00 | 20261011 | `[79, 93, 94, 73]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "measurement_sites": {
    "rank_sector_0_basis_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_basis_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_basis_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_basis_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_basis_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_two_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_two_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_two_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_two_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t0d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t1d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t3d2": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t2d1": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_kernel_at_one_t1d1_reference": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_0_bright_at_one_t1d1_reference": [
      [
        105
      ],
      [
        117
      ]
    ],
    "rank_sector_1_basis_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_basis_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_basis_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_basis_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_basis_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_two_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_two_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_two_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_two_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t0d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t1d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t3d2": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t2d1": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_kernel_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_1_bright_at_one_t1d1_reference": [
      [
        15
      ],
      [
        19
      ]
    ],
    "rank_sector_2_basis_t0d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_basis_t1d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_basis_t1d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_basis_t3d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_basis_t2d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t0d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t3d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t2d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_two_t0d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_two_t1d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_two_t3d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_two_t2d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t0d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t1d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t3d2": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t2d1": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_kernel_at_one_t1d1_reference": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_2_bright_at_one_t1d1_reference": [
      [
        81
      ],
      [
        82
      ]
    ],
    "rank_sector_3_basis_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_basis_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_basis_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_basis_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_basis_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_two_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_two_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_two_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_two_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t0d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t1d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t3d2": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t2d1": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_kernel_at_one_t1d1_reference": [
      [
        93
      ],
      [
        94
      ]
    ],
    "rank_sector_3_bright_at_one_t1d1_reference": [
      [
        93
      ],
      [
        94
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
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_persistent_kernel_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_persistent_kernel_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_zero_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_zero_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_zero_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_zero_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_one_two_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_one_two_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_one_two_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_pulse_one_two_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t0d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t1d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t1d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t3d2": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t2d1": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_persistent_kernel_t1d1_reference": [
      [
        75
      ],
      [
        74
      ]
    ],
    "rank_sector_5_bright_t1d1_reference": [
      [
        75
      ],
      [
        74
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
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_persistent_kernel_t3d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_persistent_kernel_t2d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_zero_two_t0d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_zero_two_t1d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_zero_two_t3d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_zero_two_t2d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_one_two_t0d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_one_two_t1d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_one_two_t3d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_pulse_one_two_t2d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t0d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t1d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t1d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t3d2": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t2d1": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_persistent_kernel_t1d1_reference": [
      [
        150
      ],
      [
        149
      ]
    ],
    "rank_sector_7_bright_t1d1_reference": [
      [
        150
      ],
      [
        149
      ]
    ]
  },
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "rank_sector_0": [
      {
        "73": 125,
        "79": 117,
        "93": 105,
        "94": 104
      }
    ],
    "rank_sector_1": [
      {
        "73": 14,
        "79": 15,
        "93": 19,
        "94": 35
      }
    ],
    "rank_sector_2": [
      {
        "0": 83,
        "1": 82,
        "2": 81,
        "3": 80
      }
    ],
    "rank_sector_3": [
      {
        "73": 95,
        "79": 94,
        "93": 93,
        "94": 92
      }
    ],
    "rank_sector_4": [
      {
        "73": 3,
        "79": 2,
        "93": 1,
        "94": 0
      }
    ],
    "rank_sector_5": [
      {
        "73": 59,
        "79": 75,
        "93": 74,
        "94": 73
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
        "73": 151,
        "79": 150,
        "93": 149,
        "94": 148
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

The noise model predicts 0.487228393555; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.480425642329.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.36531829834; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.358515547114.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.49291229248; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.486109541255.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.323829650879; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.317026899653.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252975463867; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.246172712642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488746643066; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481943891841.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0634307861328; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0566280349072.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0367660522461; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0299633010205.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0771331787109; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0703304274853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.250938415527; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.244135664302.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488723754883; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481921003657.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.350708007812; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.343905256587.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.493698120117; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.486895368892.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.167022705078; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.160219953853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0253753662109; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0185726149853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.48819732666; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481394575435.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.665817260742; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.659014509517.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.950355529785; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.94355277856.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.57674407959; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.569941328364.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.254280090332; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.247477339106.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_0_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.913589477539; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.899983975088.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.899983975088, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_0_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000885009765625; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0127204926856.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_0_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_0_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_0_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000282287597656; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0133232148536.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.479553222656; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.472750471431.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.360740661621; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.353937910395.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.483276367188; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.476473615962.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.320579528809; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.313776777583.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252647399902; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.245844648677.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480613708496; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.47381095727.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0933609008789; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0865581496533.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0560684204102; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0492656691845.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0682144165039; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0614116652783.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.143096923828; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.136294172603.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.481117248535; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.47431449731.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.225624084473; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.218821333247.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.269470214844; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.262667463618.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.109146118164; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.102343366938.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0372543334961; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0304515822705.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.480361938477; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.473559187251.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.627937316895; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.621134565669.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.911720275879; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.904917524653.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.579864501953; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.573061750728.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.36262512207; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.355822370845.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_1_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.855651855469; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.842046353018.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.842046353018, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_1_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 5.34057617188e-05; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0135520966895.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_1_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_1_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_1_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000572204589844; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0130332978614.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488456726074; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481653974849.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.36060333252; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.353800581294.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.491271972656; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.484469221431.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.32300567627; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.316202925044.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252639770508; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.245837019282.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488731384277; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481928633052.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0796051025391; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0728023513134.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0375900268555; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0307872756299.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0544281005859; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0476253493603.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.136596679688; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.129793928462.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488502502441; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481699751216.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.223045349121; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.216242597895.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.265350341797; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.258547590571.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0993423461914; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0925395949658.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0253982543945; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0185955031689.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488883972168; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.482081220942.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.649101257324; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.642298506099.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.946868896484; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.940066145259.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.598442077637; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.591639326411.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.369583129883; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.362780378657.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_2_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.909278869629; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.895673367178.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.895673367178, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_2_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000999450683594; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0126060517676.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_2_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_2_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_2_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000633239746094; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0129722627051.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_basis_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.487159729004; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.480356977778.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.366172790527; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.359370039302.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.495895385742; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.489092634517.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.32445526123; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.317652510005.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_basis_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_basis_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.252563476562; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.245760725337.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488594055176; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.48179130395.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0616836547852; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0548809035595.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0347442626953; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0279415114697.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0755004882812; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0686977370556.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.250846862793; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.244044111567.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.489265441895; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.482462690669.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.3515625; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.344759748774.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.496215820312; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.489413069087.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.166198730469; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.159395979243.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_kernel_at_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0230331420898; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0162303908642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.488418579102; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.481615827876.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.668350219727; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.661547468501.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.956336975098; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.949534223872.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.57918548584; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.572382734614.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_at_one_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.253952026367; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.247149275142.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_3_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.921592712402; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.907987209951.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.907987209951, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_3_kernel_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_kernel_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_kernel_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000839233398438; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0127662690528.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_3_bright_at_one_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_3_bright_at_one_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_3_bright_at_one_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000679016113281; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0129264863379.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0290451049805; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0222423537549.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0215148925781; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0147121413525.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0241012573242; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0172985060986.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.013557434082; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00675468285642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.00920867919922; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00240592797361.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0293807983398; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0225780471142.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.552803039551; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.546000288325.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.966804504395; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.960001753169.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.304504394531; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.297701643306.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0249176025391; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0181148513134.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.966484069824; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.959681318599.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.152969360352; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.146166609126.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0245742797852; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0177715285595.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0282974243164; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0214946730908.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0201263427734; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0133235915478.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.968063354492; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.961260603267.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.742225646973; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.735422895747.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.966918945312; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.960116194087.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.963912963867; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.957110212642.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.96314239502; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.956339643794.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_4_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.942817687988; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.929212185537.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.929212185537, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000129699707031; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0137352021583.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_4_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000457763671875; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0131477387794.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_4_pulse_zero_two_t1d2_minus_rank_sector_4_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.523422241211; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.50981673876.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.50981673876, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_one_two_t1d2_minus_rank_sector_4_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.128395080566; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.114789578115.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.114789578115, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_4_pulse_zero_two_t3d2_minus_rank_sector_4_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_4_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_4_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.279586791992; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.265981289541.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.265981289541, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0319595336914; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0251567824658.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0237426757812; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0169399245556.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0260848999023; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0192821486767.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0154876708984; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00868491967282.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0113677978516; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00456504662595.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0315322875977; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.024729536372.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.54411315918; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.537310407954.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949699401855; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.94289665063.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.299186706543; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.292383955317.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0265884399414; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0197856887158.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.951637268066; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.944834516841.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.15323638916; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.146433637935.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0272369384766; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0204341872509.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0307540893555; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0239513381299.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0230407714844; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0162380202588.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.953147888184; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.946345136958.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.729545593262; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.722742842036.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.949882507324; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.943079756099.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947372436523; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.940569685298.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.947357177734; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.940554426509.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_5_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.923797607422; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.910192104971.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.910192104971, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts -0.000442504882812; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.014048007334.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_5_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000335693359375; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0132698090919.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_5_pulse_zero_two_t1d2_minus_rank_sector_5_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.512580871582; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.498975369131.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.498975369131, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_one_two_t1d2_minus_rank_sector_5_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.125999450684; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.112393948232.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.112393948232, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_5_pulse_zero_two_t3d2_minus_rank_sector_5_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_5_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_5_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.272598266602; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.25899276415.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.25899276415, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0266647338867; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0198619826611.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0239944458008; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0171916945752.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.028205871582; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0214031203564.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0159378051758; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00913505395017.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0108261108398; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.00402335961423.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0264739990234; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0196712477978.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.546913146973; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.540110395747.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.960510253906; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.953707502681.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.298439025879; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.291636274653.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0212554931641; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0144527419384.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.961860656738; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.955057905513.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.154731750488; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.147928999263.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.029167175293; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0223644240674.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0327453613281; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0259426101025.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0242614746094; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0174587233838.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.96346282959; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.956660078364.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.73607635498; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.729273603755.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.960815429688; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.954012678462.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.957489013672; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.950686262446.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.957000732422; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.950197981196.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_6_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.932609558105; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.919004055654.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.919004055654, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 5.34057617188e-05; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0135520966895.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_6_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000679016113281; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0129264863379.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_6_pulse_zero_two_t1d2_minus_rank_sector_6_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.520439147949; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.506833645498.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.506833645498, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_one_two_t1d2_minus_rank_sector_6_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.125564575195; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.111959072744.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.111959072744, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_6_pulse_zero_two_t3d2_minus_rank_sector_6_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_6_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_6_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.277183532715; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.263578030264.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.263578030264, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0419311523438; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0351284011181.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0309829711914; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0241802199658.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0333786010742; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0265758498486.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0237426757812; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0169399245556.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_persistent_kernel_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0204925537109; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0136898024853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0412979125977; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.034495161372.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.540237426758; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.533434675532.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.938133239746; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.93133048852.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.302955627441; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.296152876216.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0350189208984; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0282161696728.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.935455322266; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.92865257104.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.155662536621; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.148859785395.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0344390869141; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0276363356884.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0353698730469; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0285671218213.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_pulse_one_two_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.0263977050781; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.0195949538525.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t0d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t0d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.937210083008; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.930407331782.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t1d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.720733642578; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.713930891353.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t1d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.937713623047; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.930910871821.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t3d2_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.932029724121; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.925226972895.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_t2d1_success

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t2d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.930694580078; the simultaneous finite-simulation allowance is +/-0.00680275122561. The lower modeled value is 0.923891828853.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0330847967139; requested precision is 0.08.

### rank_sector_7_bright_minus_dark_at_one

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.904335021973; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.890729519521.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.890729519521, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_persistent_kernel_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_persistent_kernel_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_persistent_kernel_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000320434570312; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0132850678809.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_bright_t1d1_packed_minus_reference

Score terms (each member averages its recorded replicas):

- `rank_sector_7_bright_t1d1`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_bright_t1d1_reference`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.000579833984375; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is -0.0130256684669.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is 0.08.

### rank_sector_7_pulse_zero_two_t1d2_minus_rank_sector_7_pulse_zero_two_t0d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t0d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.49893951416; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.485334011709.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.485334011709, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_one_two_t1d2_minus_rank_sector_7_pulse_one_two_t1d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_one_two_t1d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_one_two_t1d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.121223449707; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.107617947256.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.107617947256, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

### rank_sector_7_pulse_zero_two_t3d2_minus_rank_sector_7_pulse_zero_two_t2d1

Score terms (each member averages its recorded replicas):

- `rank_sector_7_pulse_zero_two_t3d2`: sign +1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.
- `rank_sector_7_pulse_zero_two_t2d1`: sign -1, labeled score vector `[1.0, 0.0, 0.0, 0.0]`.

The noise model predicts 0.267936706543; the simultaneous finite-simulation allowance is +/-0.0136055024512. The lower modeled value is 0.254331204092.

At alpha 0.000255102040816, the two-sided confidence half-width is 0.0686794428207; requested precision is n/a.

Reject the directional null only when the measured score exceeds 0.0661695934278 (null 0 plus one-sided radius 0.0661695934278). The admitted alternative effect is 0.254331204092, with conditional target power 0.8 and lower-tail radius 0.0335307191608. The requested minimum effect is 0.

Zero requested minimum effect selects the positive modeled contrast after the simulation allowance. The power statement concerns that reported alternative, rather than every arbitrarily small effect.

The search-wide simulation error probability is 0.01 across 928 scored finite-shot marginals. Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary repetitions remain an assumption. Hardware-model discrepancy remains unquantified.

Power admission is conditional on the supplied outcome model and reported alternative effect.

## Selection objective and sensitivity assumptions

The objective is `minimum_charge`. Selection compares the declared finite candidate set after statistical and cost admission.

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| latency_stress | 4.6 | 60 | 42.23470336 |

The largest nominal/scenario charge is 42.23470336 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_kingston/static/1 | 36 | 147456 | 39.93470336 | 60 |

The cost model predicts 39.93470336 seconds. The per-job service ceilings sum to 60 seconds against an invocation cap of 60 seconds. The global reserve is 60 seconds; the saved quota reports 551 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_kingston_static_pub_01 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_02 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_03 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_04 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_05 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_06 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_07 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_08 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_09 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_10 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_11 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_12 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_13 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_14 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_15 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_16 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_17 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_18 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_19 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
| ibm_kingston_static_pub_20 | 4096 | 5.764e-06 | 0.00025 | 0 | 0 |
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

Job `ibm_kingston/static/1` adds 2.3 seconds of modeled overhead.

## Native server qualification

The [mock timing report](native-dry-run/20261012T062730.914121Z-f400b396/report.json) reports `unavailable`; SHA-256 `780f3a41ee21b6b9af8c499d5b121110fe2a4dedffc7f0e8e0e66ab384014e80`.

The native attempt leaves server timing unqualified; its report retains the failure.

Runtime mock execution validates a schedule without executing the QPU. Randomized mock outcomes are excluded from scientific analysis and visuals. Server estimates, schedule durations and future charged usage are distinct. Initialization and fixed overhead remain unseparated.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family rank-sector \
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
  --max-execution-seconds 60 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,5120,8192 \
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
  --max-execution-seconds 60 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 2048,4096,5120,8192 \
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
  --approved-record ../results/live/2026-10-12T062505.552988Z \
  --approved-record-sha256 f38dfe635415d264eea754e4d699080092ca7272f65e42304fac08f5b4f5fe7d \
  --submit
```
