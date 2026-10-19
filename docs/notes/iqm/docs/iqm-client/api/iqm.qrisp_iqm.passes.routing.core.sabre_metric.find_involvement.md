> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e7f6df75ef55158226845ce4f48073099a34e72d13194fd10ff598a05cf58814.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement

iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement(*instruction_data: np.ndarray*, *front_layer_indices: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *extended_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[np.int16\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[np.int16\]\]\]  
Determine involvement lists for SABRE cost-change computation.

Describes which instruction each qubit is involved in. This is required in order to call the compute_sabre_cost_change function with the corresponding relevant instructions.

Single-qubit gates are excluded from the involvement lists because they have distance 0 under any qubit placement and therefore contribute nothing to the SABRE cost metric.

Parameters:  
- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **front_layer_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the front layer.

- **extended_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the extended_set.

- **topology** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – A topology tuple (see graph_processing_tools for more details).

Returns:  
- **front_layer_res** (*list\[list\[int\]\]*) – A list of lists indicating which front layer instructions each qubit is involved in.

- **extended_set_res** (*list\[list\[int\]\]*) – A list of lists indicating which extended set instructions each qubit is involved in.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[np.int16\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[np.int16\]\]\]
