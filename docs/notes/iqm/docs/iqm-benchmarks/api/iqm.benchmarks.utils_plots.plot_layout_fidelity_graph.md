> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.plot_layout_fidelity_graph.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.plot_layout_fidelity_graph.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 907bafb9732511ce5a58e5da481a2e26001db30c79ef898e50e1334fc50c5b97.

# iqm.benchmarks.utils_plots.plot_layout_fidelity_graph

iqm.benchmarks.utils_plots.plot_layout_fidelity_graph(*backend: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *qubit_layouts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *sq_metric: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'coherence'*, *show_ghz_path: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *tree_options: [TreeSearchOptions](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")  
Plot a graph showing the quantum chip layout with fidelity information.

Creates a visualization of the quantum chip topology where nodes represent qubits and edges represent connections between qubits. Edge thickness indicates gate errors (thinner edges mean better fidelity) and selected qubits are highlighted in orange.

Parameters:  
- **backend** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to visualize, either as a string name or an IQMBackendBase instance.

- **qubit_layouts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – List of qubit layouts where each layout is a list of qubit indices

- **sq_metric** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Optional single qubit metric to use for the visualization, can be either “fidelity”, “coherence”, or “readout”.

- **show_ghz_path** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to highlight the edges that are part of the GHZ state creation tree path. The path shown is the one the “tree” state generation routine would build for the first layout, from the same calibration, so it is what a run would actually play.

- **tree_options** ([*TreeSearchOptions*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions") *\|* *None*) – What the GHZ tree search minimizes when show_ghz_path is set. None uses the same defaults as GHZConfiguration, so the drawn path matches a default run; pass a TreeSearchOptions built from the tree\_\* options of a non-default configuration.

Returns:  
The generated figure object containing the graph visualization

Return type:  
[matplotlib.figure.Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")
