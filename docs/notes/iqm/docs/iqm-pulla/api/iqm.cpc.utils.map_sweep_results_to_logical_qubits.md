> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.map_sweep_results_to_logical_qubits.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.utils.map_sweep_results_to_logical_qubits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2e937c502324d02bd9d531afbda7fbb7ed975c615739d56b6e96a5190076a199.

# iqm.cpc.utils.map_sweep_results_to_logical_qubits

iqm.cpc.utils.map_sweep_results_to_logical_qubits(*sweep_results*, *readout_mappings*, *heralding_mode*)  
Convert sweep results returned by Station Control to the circuit measurement results the client expects.

Parameters:  
- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[np.ndarray\]\]*) – mapping of acquisition labels to a list of soft sweep spots, each represented by a 1D array of readout results, with `shots * num_triggers_for_label` elements.

- **readout_mappings** (*ReadoutMappingBatch*) – for each circuit in the batch, a mapping of measurement keys to corresponding tuples of result parameter names.

- **heralding_mode** (*HeraldingMode*) – Whether we use heralded readout or not.

Returns:  
Converted, filtered measurement results, with the heralding measurement data removed.

Return type:  
CircuitMeasurementResultsBatch
