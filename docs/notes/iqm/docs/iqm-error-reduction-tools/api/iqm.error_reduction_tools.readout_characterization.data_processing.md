> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 66b9c2c7af7dcb2c0600723e182b7ab11cc4de7183855ef2d19a5201f45b765f.

# iqm.error_reduction_tools.readout_characterization.data_processing

Functions for computing readout error correlations from characterization data.

Module Attributes

|  |  |
|----|----|
| [`CountsByPrep`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep.html#iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep "iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep") | Mapping from preparation string to measurement outcome counts. |
| [`ErrorId`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId") | Error category identifier. |
| [`AssignmentMatrix`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.AssignmentMatrix.html#iqm.error_reduction_tools.readout_characterization.data_processing.AssignmentMatrix "iqm.error_reduction_tools.readout_characterization.data_processing.AssignmentMatrix") | 2×2 column-stochastic assignment matrix `[[P(0|0), P(0|1)], [P(1|0), P(1|1)]]` characterizing the readout errors for a qubit. |

Functions

|  |  |
|----|----|
| [`compute_double_twirled_covariance`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance "iqm.error_reduction_tools.readout_characterization.data_processing.compute_double_twirled_covariance")(data) | Compute double-twirled (syndrome-based) readout error correlations. |
| [`compute_error_probabilities`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities "iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities")(data) | Compute single-qubit readout error probabilities from calibration data. |
| [`compute_single_twirled_covariance`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance "iqm.error_reduction_tools.readout_characterization.data_processing.compute_single_twirled_covariance")(data) | Compute single-twirled readout error correlations between qubit pairs. |
| [`compute_state_dependent_covariance`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance.html#iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance "iqm.error_reduction_tools.readout_characterization.data_processing.compute_state_dependent_covariance")(data) | Compute fully state-dependent readout error correlations between qubit pairs. |

Classes

|  |  |
|----|----|
| [`CalibrationData`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData") | Calibration dataset container. |
| [`ErrorProbabilities`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities") | Single-qubit characterization probabilities and standard deviations. |
| [`SingleCovarianceData`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.SingleCovarianceData") | Single- and double-twirled covariance output container. |
| [`StateCovarianceData`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData.html#iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData "iqm.error_reduction_tools.readout_characterization.data_processing.StateCovarianceData") | State-dependent covariance output container. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.readout_characterization.data_processing](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-abb7d6a8b1950d558afeb152573931451040c4b5.png)
