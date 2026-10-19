> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e15b0e48bcca5a5cfaa95fc90770a96f5578cbd76f94bdfb8f5dc7d35fa6e248.

# iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance

iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance(*data*)  
Compute fully state-dependent readout error correlations between qubit pairs.

Calculates covariances conditioned on the preparation states of both qubits. This captures the full joint error distribution P(measure_i, measure_j \| prep_i, prep_j).

Parameters:  
**data** ([*CalibrationData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData")) – Calibration data from `run_calibration_circuits()`.

Returns:  
State-dependent covariance output.

Return type:  
[*StateCovarianceData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData")

Note

Computes 12 correlation types corresponding to all relevant error pair combinations: (2,0), (3,0), (2,1), (3,1), (0,2), (0,3), (1,2), (1,3), (2,2), (3,3), (2,3), (3,2). Excludes trivial (0,0), (0,1), (1,0), (1,1).
