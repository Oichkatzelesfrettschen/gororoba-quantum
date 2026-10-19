> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6c240296f8fbda4a575abb4fe276d8a72d1dbbeca5a8c26c15180493c71fe6e3.

# iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance

iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance(*data*)  
Compute double-twirled (syndrome-based) readout error correlations.

Aggregates state-dependent errors into preparation-independent syndrome categories based on which qubits experience readout flips. This reveals correlated errors that persist regardless of preparation states.

Syndrome categories:  
0: Qubit j flips, qubit i correct (errors: (0,2), (0,3), (1,2), (1,3)) 1: Qubit i flips, qubit j correct (errors: (2,0), (3,0), (2,1), (3,1)) 2: Both qubits flip (errors: (2,2), (3,3), (2,3), (3,2))

Parameters:  
**data** ([*CalibrationData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData")) – Calibration data from `run_calibration_circuits()`.

Returns:  
Single- and double-twirled covariance output.

Return type:  
[*SingleCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData")
