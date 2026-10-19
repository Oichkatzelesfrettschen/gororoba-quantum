> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ababfb1860617c925593dc1ba7186836f0984beb0b15aee145cc66ae9a1f70f7.

# utils

Full path: iqm.cpc.utils

Utility functions for the circuit-to-pulse compiler.

Functions

|  |  |
|----|----|
| [`calset_from_observations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.calset_from_observations.html#iqm.cpc.utils.calset_from_observations "iqm.cpc.utils.calset_from_observations")(calset_observations) | Create a calibration set from the given observations. |
| [`calset_to_cal_data_tree`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.calset_to_cal_data_tree.html#iqm.cpc.utils.calset_to_cal_data_tree "iqm.cpc.utils.calset_to_cal_data_tree")(calibration_set_values) | Build an iqm-pulse QuantumOp calibration data tree from a calibration set. |
| [`convert_sweep_spot_to_arrays`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays.html#iqm.cpc.utils.convert_sweep_spot_to_arrays "iqm.cpc.utils.convert_sweep_spot_to_arrays")(results, ...) | Convert the sweep measurement results from Station Control into circuit batch measurement results. |
| [`convert_sweep_spot_to_arrays_with_heralding_mode_zero`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero.html#iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero "iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero")(...) | Like [`convert_sweep_spot_to_arrays()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays.html#iqm.cpc.utils.convert_sweep_spot_to_arrays "iqm.cpc.utils.convert_sweep_spot_to_arrays"), but for results that contain heralding measurements. |
| [`map_sweep_results_to_logical_qubits`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.map_sweep_results_to_logical_qubits.html#iqm.cpc.utils.map_sweep_results_to_logical_qubits "iqm.cpc.utils.map_sweep_results_to_logical_qubits")(...) | Convert sweep results returned by Station Control to the circuit measurement results the client expects. |

Exceptions

|  |  |
|----|----|
| [`PostSelectionError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.PostSelectionError.html#iqm.cpc.utils.PostSelectionError "iqm.cpc.utils.PostSelectionError") | Error in performing post selection via heralded results. |
