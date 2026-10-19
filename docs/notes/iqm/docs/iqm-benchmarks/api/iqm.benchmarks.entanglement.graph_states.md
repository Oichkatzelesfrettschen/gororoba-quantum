> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19228c10db5288727910c15f8af34bb53d09ed550aedbdc685e89cc54bc9f60f.

# iqm.benchmarks.entanglement.graph_states

Graph states benchmark.

Functions

|  |  |
|----|----|
| [`find_edges_with_disjoint_neighbors`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.find_edges_with_disjoint_neighbors.html#iqm.benchmarks.entanglement.graph_states.find_edges_with_disjoint_neighbors "iqm.benchmarks.entanglement.graph_states.find_edges_with_disjoint_neighbors")(graph) | Finds sets of edges with non-overlapping neighboring nodes. |
| [`generate_graph_state`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_graph_state.html#iqm.benchmarks.entanglement.graph_states.generate_graph_state "iqm.benchmarks.entanglement.graph_states.generate_graph_state")(qubits, backend) | Generates a circuit with minimal depth preparing a native graph state for a given backend using given qubits. |
| [`generate_minimal_edge_layers`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers.html#iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers "iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers")(cp_map) | Sorts the edges of a coupling map. |
| [`negativity_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.negativity_analysis.html#iqm.benchmarks.entanglement.graph_states.negativity_analysis "iqm.benchmarks.entanglement.graph_states.negativity_analysis")(run) | Analysis function for a Graph State benchmark experiment. |
| [`plot_density_matrix`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.plot_density_matrix.html#iqm.benchmarks.entanglement.graph_states.plot_density_matrix "iqm.benchmarks.entanglement.graph_states.plot_density_matrix")(matrix, qubit_pair, ...) | Plots a density matrix for corresponding qubit pairs, neighbor qubit projections, and negativities. |
| [`plot_max_negativities`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.plot_max_negativities.html#iqm.benchmarks.entanglement.graph_states.plot_max_negativities "iqm.benchmarks.entanglement.graph_states.plot_max_negativities")(negativities, ...\[, ...\]) | Plots the maximum negativity for each corresponding pair of qubits. |
| [`plot_max_negativities_graph`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.plot_max_negativities_graph.html#iqm.benchmarks.entanglement.graph_states.plot_max_negativities_graph "iqm.benchmarks.entanglement.graph_states.plot_max_negativities_graph")(negativities, ...) | Plots the maximum negativity for each corresponding pair of qubits in a graph layout of the given backend. |
| [`shadow_tomography_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.shadow_tomography_analysis.html#iqm.benchmarks.entanglement.graph_states.shadow_tomography_analysis "iqm.benchmarks.entanglement.graph_states.shadow_tomography_analysis")(dataset, ...) | Performs shadow tomography analysis on the given dataset. |
| [`state_tomography_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.state_tomography_analysis.html#iqm.benchmarks.entanglement.graph_states.state_tomography_analysis "iqm.benchmarks.entanglement.graph_states.state_tomography_analysis")(dataset, ...) | Performs state tomography analysis on the given dataset. |
| [`update_pauli_expectations`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.update_pauli_expectations.html#iqm.benchmarks.entanglement.graph_states.update_pauli_expectations "iqm.benchmarks.entanglement.graph_states.update_pauli_expectations")(...) | Helper function that updates the input Pauli expectations dictionary of dictionaries. |

Classes

|  |  |
|----|----|
| [`GraphStateBenchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.html#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark")(backend_arg, configuration) | The Graph States benchmark estimates the bipartite entangelement negativity of native graph states. |
| [`GraphStateConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.html#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration")(\*, benchmark, shots, ...) | Graph States Benchmark configuration. |
| [`TomographyType`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.TomographyType.html#iqm.benchmarks.entanglement.graph_states.TomographyType "iqm.benchmarks.entanglement.graph_states.TomographyType")(value) | Supported types of tomography. |

Inheritance

![Inheritance diagram of iqm.benchmarks.entanglement.graph_states](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-f829b8b277f2347f8c7f99120f48fd92015db855.png)
