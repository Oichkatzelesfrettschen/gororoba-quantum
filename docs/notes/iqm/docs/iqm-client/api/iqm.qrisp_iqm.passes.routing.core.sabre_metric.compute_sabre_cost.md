> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3b87311114449284fbd5f4c4fcc8be8e6db353217bba4834923a314da5935572.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost(*topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *front_layer_indices: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *extended_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *instruction_data: np.ndarray*, *citizen_to_address: np.ndarray*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Computes the SABRE metric with the modifications mentioned in the preamble.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")) – QPU topology.

- **front_layer_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of integer indices indicating which entries of the instruction data are currently at the front layer.

- **extended_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of integer indices indicating which entries of the instruction data are currently in the extended set.

- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **citizen_to_address** (*np.ndarray*) – An array indicating the current permutation of qubits.

Returns:  
The cost of the modified SABRE metric.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
