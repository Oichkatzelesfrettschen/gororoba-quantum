> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_state_dep_matrix.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_state_dep_matrix.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 46e0c3d2d0cf75856d1fa910ce05480a810c80719b73f16263e16fe8022a29d7.

# iqm.error_reduction_tools.readout_characterization.visualization.visualize_state_dep_matrix

iqm.error_reduction_tools.readout_characterization.visualization.visualize_state_dep_matrix(*matrix*, *std*, *title=''*, *subset=None*)  
Visualizes the state-dependent error matrix.

Parameters:  
- **matrix** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The matrix to plot.

- **std** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The standard deviation to indicate on the colorbar.

- **title** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The title for the plot.

- **subset** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – A subset of qubit indices to plot.

Return type:  
None
