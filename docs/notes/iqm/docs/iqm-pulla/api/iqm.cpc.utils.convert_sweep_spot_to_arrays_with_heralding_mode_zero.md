> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 456734f4000a4d1eac95918bc8d46c19e1dfd79e04564581d22ad697edb64a83.

# iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero

iqm.cpc.utils.convert_sweep_spot_to_arrays_with_heralding_mode_zero(*results*, *readout_mappings*)  
Like [`convert_sweep_spot_to_arrays()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.convert_sweep_spot_to_arrays.html#iqm.cpc.utils.convert_sweep_spot_to_arrays "iqm.cpc.utils.convert_sweep_spot_to_arrays"), but for results that contain heralding measurements.

- For each circuit we only keep the shots for which the heralding result is zero for all the qubits used in the circuit.

Parameters:  
- **results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *np.ndarray\]*) – Mapping of acquisition labels to 1D arrays of readout results with the length `num_shots * num_triggers_for_label_in_batch`. The herald results are found under `HERALDING_KEY`.

- **readout_mappings** (*ReadoutMappingBatch*) – For each circuit in the batch, a mapping of measurement keys to corresponding tuples of acquisition labels.

Yields:  
Converted measurement results for each circuit in the batch, filtered based on the result of  
the heralding measurement, , with the heralding measurement data removed.

Return type:  
Iterator\[\_CircuitMeasurementResultsNew\]
