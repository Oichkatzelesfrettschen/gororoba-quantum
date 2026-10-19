> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eccb80089dbb98f2749418cb8e3b5b7af0f9384ffaa01846a2de6b9f7d7b06e7.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology(*connectivity: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*) → [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")  
Take a connectivity list and compute the QPU topology.

The topology graph preserves the original qubit indices from `connectivity` as node labels. Qubits that do not participate in any edge are included as isolated nodes so that the output circuit’s qubit indices correspond directly to the original indices — no renumbering occurs.

Parameters:  
**connectivity** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – Pairs of qubits that are connected to each other.

Returns:  
QPU topology description.

Return type:  
[*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")
