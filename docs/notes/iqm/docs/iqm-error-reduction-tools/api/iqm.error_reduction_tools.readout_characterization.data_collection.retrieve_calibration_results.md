> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3f13ebce871a9085c9efe0b8f5ead2da0ecd3b81d30c1c21a9a79f961abeba3d.

# iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results

iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results(*job*, *job_info*)  
Retrieve and organize measurement results from the calibration circuits.

Groups raw measurement counts by their preparation string. The raw counts are preserved so that [`compute_error_probabilities()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities "iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities") can compare them directly against the preparation string to compute P(0\|1) and P(1\|0).

Parameters:  
- **job** ([*RunJobTracker*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html#iqm.station_control.client.job_trackers.RunJobTracker "(in iqm-station-control-client v14.0.0)")) – Job tracker for the calibration job.

- **job_info** ([*CalibrationJobInfo*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo")) – Metadata about the submitted calibration job.

Returns:  
Calibration results. Multiple circuits with the same preparation string have merged counts.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If the job did not complete after multiple wait attempts.

Return type:  
[*CalibrationData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData")
