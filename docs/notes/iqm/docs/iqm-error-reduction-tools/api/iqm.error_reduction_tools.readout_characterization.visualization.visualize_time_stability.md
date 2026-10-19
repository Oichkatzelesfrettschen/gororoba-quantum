> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_time_stability.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_time_stability.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a049d7780bd59cfe55326ca8066f406e97d0cfb977b3e94afa647356cf6b6e5.

# iqm.error_reduction_tools.readout_characterization.visualization.visualize_time_stability

iqm.error_reduction_tools.readout_characterization.visualization.visualize_time_stability(*data*, *std_shots*, *threshold_err=0.1*, *threshold_ratio=3*, *upper_y_label=None*)  
Visualize temporal stability of readout characterization data across multiple runs.

Creates a two-panel visualization to assess the temporal stability of readout measurements. The first panel shows the distribution of measurements across qubits with violin plots, individual data points, and error bars representing pure statistical uncertainty. The second panel displays the ratio of total standard deviation to shot-noise standard deviation for each qubit.

Parameters:  
- **data** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of shape (`num_runs`, `num_qubits`) containing measurement data from multiple characterization runs.

- **std_shots** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of shot-noise standard deviations for each qubit, representing pure statistical uncertainty expected from finite sampling.

- **threshold_err** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Threshold value for acceptable error level, displayed as a horizontal line in the first panel. Default is 0.1 (10%).

- **threshold_ratio** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Threshold value for the ratio of standard deviations, displayed as a horizontal line in the second panel. Default is 3.

- **upper_y_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Label for the y-axis of the first panel. If `None`, no label is set.

Returns:  
`None`. Displays a matplotlib figure with two subplots.

Return type:  
None

Note

- The first panel shows violin plots with overlaid scatter points (with jitter) and error bars representing shot-noise limited uncertainty.

- The second panel uses a logarithmic y-scale to show the ratio of total standard deviation to shot-noise standard deviation. A ratio near 1 indicates that the measurement is shot-noise limited, while higher ratios suggest additional sources of variability (e.g., temporal drift).

- Horizontal reference lines at y=1 and y=threshold_ratio help identify qubits with excessive time-dependent variability.
