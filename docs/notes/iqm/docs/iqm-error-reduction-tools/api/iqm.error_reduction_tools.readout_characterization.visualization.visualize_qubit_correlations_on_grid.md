> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd1f8801ac9e2336842baa8eea5d3cf5147b35e0debe446f4a8ccdda57948c17.

# iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid

iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid(*correlation_matrix*, *topology*, *thresholds=None*, *vmax=None*, *qubit_labels=None*, *title='Qubit Correlations'*, *edge_curvature=0.2*, *show_plot=True*)  
Visualize readout error correlations overlaid on QPU topology.

Creates a network graph showing qubits positioned according to their physical layout, with directed edges representing correlation strength and sign. Qubits are colored by readout line grouping.

Parameters:  
- **correlation_matrix** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – NxN array of correlation coefficients. Element \[i,j\] represents correlation from qubit i to qubit j.

- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology")) – `QPUTopology` defining qubit positions and readout lines. Use [`topology_from_qc()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.topology_from_qc "iqm.error_reduction_tools.utils.topology_utils.topology_from_qc") to obtain a fully-populated instance from a connected quantum computer.

- **thresholds** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Optional (upper, lower) thresholds for edge filtering. Only correlations ≥upper or ≤lower are displayed. If `None`, all edges are shown.

- **vmax** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Colormap saturation value. Correlations are mapped to \[-vmax, +vmax\] range (red=negative, blue=positive).

- **qubit_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of qubit labels corresponding to the correlation matrix rows/columns. If `None`, assumes matrix represents all topology qubits in order. Can be a subset to visualize only specific qubits (unlisted qubits appear faded).

- **title** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Plot title. String or tuple (error_id, title_string).

- **edge_curvature** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Curvature radius for edges (0=straight, 0.2=default curve).

- **show_plot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, displays plot and returns `None`. If `False`, returns `Figure`.

Returns:  
Matplotlib figure if `show_plot=False`, otherwise `None`.

Return type:  
[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)") \| None

Note

Arrows point from dimension 1 to dimension 2 of correlation_matrix. E.g., arrow QB0→QB1 shows `correlation_matrix[QB0_idx, QB1_idx]`.
