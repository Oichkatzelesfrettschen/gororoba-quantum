> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_in_topology.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_in_topology.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 443c01d781d7a2786a8aa547eb16540bedf2492ca450b796a3f780c941c2049a.

# iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_in_topology

iqm.error_reduction_tools.readout_characterization.visualization.plot_covariance_in_topology(*covariance_data*, *topology*, *qubits_to_plot=None*, *thresholds=None*, *vmax=None*, *show_plot=True*)  
Generate topology-based correlation plots for all error types.

Wrapper around [`visualize_qubit_correlations_on_grid()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid.html#iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid "iqm.error_reduction_tools.readout_characterization.visualization.visualize_qubit_correlations_on_grid") that creates one plot per error category from covariance analysis functions. Designed to accept direct outputs from `compute_*_covariance` functions.

Parameters:  
- **covariance_data** ([*SingleCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData") *\|* [*StateCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData")) – Obtained from the `compute_*_covariance` functions.

- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology")) – QPU topology for qubit positioning. Use [`topology_from_qc()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.topology_from_qc "iqm.error_reduction_tools.utils.topology_utils.topology_from_qc") to obtain a fully-populated instance from a connected quantum computer.

- **qubits_to_plot** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Optional list of qubit labels to visualize. If `None`, uses `measured_qubits` from `covariance_data`.

- **thresholds** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Optional (upper, lower) correlation thresholds for edge filtering.

- **vmax** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Colormap saturation value for correlation strength.

- **show_plot** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, displays all plots. If `False`, returns `Figure` list.

Returns:  
Matplotlib figures if `show_plot=False`, otherwise `None`.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\] \| None

Example

```
>>> corr, labels, qubits = compute_double_twirled_covariance(data)
>>> topology = topology_from_qc(client)
>>> plot_covariance_in_topology(corr, labels, qubits, topology=topology, vmax=0.005)
# Displays 3 topology plots (one per syndrome type)
```
