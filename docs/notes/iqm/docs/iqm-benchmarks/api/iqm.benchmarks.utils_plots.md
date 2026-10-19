> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1327b31a3d05a0853f335e3cb097ff10810ceed76654571ae393b1af4f040d6e.

# iqm.benchmarks.utils_plots

Plotting and visualization utility functions.

Functions

|  |  |
|----|----|
| [`calculate_node_radii`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.calculate_node_radii.html#iqm.benchmarks.utils_plots.calculate_node_radii "iqm.benchmarks.utils_plots.calculate_node_radii")(metric_dict, ...) | Calculate node radii based on the specified single qubit metric. |
| [`draw_graph_edges`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.draw_graph_edges.html#iqm.benchmarks.utils_plots.draw_graph_edges "iqm.benchmarks.utils_plots.draw_graph_edges")(backend_coupling_map, ...) | Draw given edges on a graph within the given backend. |
| [`evaluate_hamiltonian_paths`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths.html#iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths "iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths")(n_vertices, ...) | Evaluates Hamiltonian paths according to the product of 2Q gate fidelities on the edges of the backend graph. |
| [`plot_layout_fidelity_graph`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.plot_layout_fidelity_graph.html#iqm.benchmarks.utils_plots.plot_layout_fidelity_graph "iqm.benchmarks.utils_plots.plot_layout_fidelity_graph")(backend\[, ...\]) | Plot a graph showing the quantum chip layout with fidelity information. |
| [`rx_to_nx_graph`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.rx_to_nx_graph.html#iqm.benchmarks.utils_plots.rx_to_nx_graph "iqm.benchmarks.utils_plots.rx_to_nx_graph")(backend_coupling_map) | Convert the Rustworkx graph returned by a backend to a Networkx graph. |

Classes

|  |  |
|----|----|
| [`GraphPositions`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.GraphPositions.html#iqm.benchmarks.utils_plots.GraphPositions "iqm.benchmarks.utils_plots.GraphPositions")() | A class to store and generate graph positions for different chip layouts. |

Inheritance

![Inheritance diagram of iqm.benchmarks.utils_plots](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-45f9359fd71b95b8bc82e5b3312a82e70956bda2.png)
