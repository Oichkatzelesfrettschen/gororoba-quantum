> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6bd16f0edfc78efd43fcc00415631da647c360028aeae133e3ecadf8a4e3ac43.

# graph_processing_tools

Full path: iqm.qrisp_iqm.passes.routing.core.graph_processing_tools

Graph processing tools for plasma-sabre routing passes.

This module implements functions that operate on two different graphs:

1.  The hardware topology graph [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology").

2.  The quantum circuit in DAG form [`CircuitDAG`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG").

Module Attributes

|  |  |
|----|----|
| [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")(indptr, indices, dist_matrix, ...) | Describes the QPU topology. |
| [`CircuitDAG`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")(indptr, indices, instruction_data) | Describes the quantum circuit as a DAG. |

Functions

|  |  |
|----|----|
| [`connectivity_to_topology`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.connectivity_to_topology")(connectivity) | Take a connectivity list and compute the QPU topology. |
| [`convert_qc_to_sparse_dag`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag")(qc\[, topo_sort\]) | Convert a quantum circuit into a DAG. |
| [`find_path`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path")(a, b, topology) | Reconstruct the shortest path between two qubits. |
| [`find_path_length`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path_length.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path_length "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.find_path_length")(index_0, index_1, topology) | Return the shortest-path distance between two qubit indices. |
| [`gen_swap_candidates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.gen_swap_candidates.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.gen_swap_candidates "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.gen_swap_candidates")(instruction_data, ...) | Generate deduplicated swap candidates for the front layer. |
| [`permute_instruction_dag`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.permute_instruction_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.permute_instruction_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.permute_instruction_dag")(circuit_dag, permutation) | Apply a qubit layout permutation to an instruction DAG. |
| [`prune_dag`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag")(circuit_dag, pruning_threshold) | Prune instructions below a threshold from an instruction DAG. |
| [`reachability_counts_csr`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr")(indptr, indices, ...) | Count how many nodes each node can reach in a CSR-encoded DAG. |
| [`reverse_dag`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag")(circuit_dag) | Build a backward instruction DAG by reversing the topological order. |

Classes

|  |  |
|----|----|
| [`CircuitDAG`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG") | Describes the quantum circuit as a DAG. |
| [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology") | Describes the QPU topology. |

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.passes.routing.core.graph_processing_tools](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-469a5e408f15c1ce8e6774bd0a310edbe7939715.png)
