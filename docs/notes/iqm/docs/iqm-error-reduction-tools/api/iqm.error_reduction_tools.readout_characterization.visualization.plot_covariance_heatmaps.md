> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_heatmaps.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_heatmaps.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7bd294eebfd0da07cf94e8f62e90287bd5bcc41d1f420c90ebc7396482393a5c.

# iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_heatmaps

iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_heatmaps(*covariance_data*, *vmax=None*, *show_plot=True*)  
Generate heatmap visualizations for all correlation matrices.

Creates one heatmap per error category from covariance analysis. Provides a matrix view complementary to topology-based visualization. Designed to accept direct outputs from `compute_*_covariance` functions.

Parameters:  
- **covariance_data** ([*SingleCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData") *\|* [*StateCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData")) – Obtained from the `compute_*_covariance` functions.

- **vmax** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Colormap saturation value. If `None`, uses max absolute covariance per matrix.

- **show_plot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, displays all heatmaps. If `False`, returns `Figure` list.

Returns:  
Matplotlib figures if `show_plot=False`, otherwise `None`.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\] \| None

Example

```
>>> result = compute_state_dependent_covariance(data)
>>> plot_covariance_heatmaps(result, vmax=0.01)
# Displays 12 heatmaps (one per error pair combination)
```
