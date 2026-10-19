> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a1c30993cf94773fdff0e21c8d9325f3cacc30c5360b2af6abe50821e23d63b8.

# iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance

iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance(*data*)  
Compute single-twirled readout error correlations between qubit pairs.

Calculates covariances where one qubit has a state-dependent error (conditioned on its preparation) and the other has a preparation-averaged (twirled) error. This reveals correlations that persist regardless of the second qubit’s state.

Parameters:  
**data** ([*CalibrationData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData")) – Calibration data from `run_calibration_circuits()`.

Returns:  
Single- and double-twirled covariance output.

Return type:  
[*SingleCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData")

Note

Error IDs match `_get_error_ids_for_shot()` encoding (0=00, 1=11, 2=01, 3=10). Correlation\[i,j\] = P(error_i, syndrome_j) - P(error_i)P(syndrome_j)
