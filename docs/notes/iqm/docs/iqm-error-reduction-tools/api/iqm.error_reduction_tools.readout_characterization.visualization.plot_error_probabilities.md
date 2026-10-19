> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 85a25850bf020e4588436bbbf1675e57e14c1a51b56e79d15401d1d5b035f1b1.

# iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities

iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities(*error_data*, *title='Readout Error Probabilities'*, *show_plot=True*)  
Plot readout error probabilities.

Wraps [`compute_error_probabilities()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities "iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities") output.

Accepts the dictionary returned by `compute_error_probabilities` and renders a grouped bar chart of P(1\|0) and P(0\|1) for each measured qubit, with optional error bars from the standard-deviation matrices.

Parameters:  
- **error_data** ([*ErrorProbabilities*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities")) – Obtained from `compute_error_probabilities`.

- **title** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Title for the plot.

- **show_plot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, displays the plot. If `False`, returns the `Figure`.

Returns:  
Matplotlib figure if `show_plot=False`, otherwise `None`.

Return type:  
[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)") \| None
