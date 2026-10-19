> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fba7515e32fc728fdd90f9973f6e3ddd6479c4049c210699211bfde430b85843.

# QPUTopology

Module: [`iqm.qrisp_iqm.passes.routing.core.graph_processing_tools`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.html#module-iqm.qrisp_iqm.passes.routing.core.graph_processing_tools "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools")

*class* iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology(*indptr*, *indices*, *dist_matrix*, *predecessors*)  
Bases: [`tuple`](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")

Describes the QPU topology.

All the items are of the type `np.ndarray[int]`. The adjacency matrix A of the QPU coupling graph is stored here in [CSR form](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format)). The nodes are qubits, and the edges correspond to available native two-qubit gates.

- [`indices`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indices "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indices") is a 1-D array containing column indices of the nonzero elements of A.

- [`indptr`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indptr "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indptr") is a 1-D array, where `indptr[k]` is the number of nonzero elements in A above row `k`.

- [`dist_matrix`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix") is a dense matrix where `dist_matrix[a, b]` is the length of the shortest path between nodes `a` and `b`.

- [`predecessors`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors") is a dense matrix where `predecessors[a, b]` is the index of the next node to take when traversing the shortest path from node `a` to node `b`.

[`dist_matrix`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix") and [`predecessors`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors") could be computed on demand, but since we care for performance and they are required A LOT, we precompute them and pass them around along the CSR matrix.

Attributes

|  |  |
|----|----|
| [`dist_matrix`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.dist_matrix") | Alias for field number 2 |
| [`indices`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indices "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indices") | Alias for field number 1 |
| [`indptr`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indptr "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.indptr") | Alias for field number 0 |
| [`predecessors`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.predecessors") | Alias for field number 3 |

Methods

dist_matrix  
Alias for field number 2

indices  
Alias for field number 1

indptr  
Alias for field number 0

predecessors  
Alias for field number 3

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-0eb54caf2477d88c3a72a594974354b4c63db208.png)
