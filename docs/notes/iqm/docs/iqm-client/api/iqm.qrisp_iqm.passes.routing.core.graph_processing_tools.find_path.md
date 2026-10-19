> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6ad1b057d9ccc7ea3975c9f5b438596139e0127bec3a77883e0c95fb58b66a95.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path(*a: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *b: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Reconstruct the shortest path between two qubits.

Uses the predecessor matrix from `topology` to reconstruct the shortest path from node `a` to node `b`.

Parameters:  
- **a** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **b** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology"))

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
