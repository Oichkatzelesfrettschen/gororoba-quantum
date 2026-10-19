> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a67b815fa594920b5cd80cb95fab85af16892d29efd6ab358a2770c23f87b89d.

# CircuitDAG

Module: [`iqm.qrisp_iqm.passes.routing.core.graph_processing_tools`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.html#module-iqm.qrisp_iqm.passes.routing.core.graph_processing_tools "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools")

*class* iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG(*indptr*, *indices*, *instruction_data*)  
Bases: [`tuple`](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")

Describes the quantum circuit as a DAG.

All the items are of the type `np.ndarray[int]`. The `m * m` adjacency matrix A of the DAG is stored here in [CSR form](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format)). The nodes are instructions in the circuit, and the edges correspond to qubits the instructions are acting on. Edge direction represents causality (relative time ordering).

- [`indices`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indices "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indices") is a 1-D array containing column indices of the nonzero elements of A.

- [`indptr`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indptr "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indptr") is a 1-D array, where `indptr[k]` is the number of nonzero elements in A above row `k`.

- [`instruction_data`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.instruction_data "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.instruction_data") is a `shape==(m, 3)` array describing the instructions:

  - `instruction_data[i, 0]`: index of the first qubit of the instruction locus

  - `instruction_data[i, 1]`: index of the second qubit of the instruction locus (for one-qubit gates the same as first)

  - `instruction_data[i, 2]`: index that identifies the `qrisp.Instruction` the node corresponds to. The list of Instruction objects is kept outside of the jitted code, and is used to reconstruct the `qrisp.QuantumCircuit` object once jit-based compilation has concluded.

Attributes

|  |  |
|----|----|
| [`indices`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indices "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indices") | Alias for field number 1 |
| [`indptr`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indptr "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.indptr") | Alias for field number 0 |
| [`instruction_data`](#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.instruction_data "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.instruction_data") | Alias for field number 2 |

Methods

indices  
Alias for field number 1

indptr  
Alias for field number 0

instruction_data  
Alias for field number 2

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-eb1d79688b82d00ca999684982d99358ae249446.png)
