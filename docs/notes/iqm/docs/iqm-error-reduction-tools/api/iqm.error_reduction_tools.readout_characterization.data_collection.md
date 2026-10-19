> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bbb2fbccc874964abdf41aa7bb73eca7bbed1ac95eefa447df1ac461878ca0fe.

# iqm.error_reduction_tools.readout_characterization.data_collection

Utility functions for generating calibration circuits for readout error characterization.

Functions

|  |  |
|----|----|
| [`create_calibration_circuits`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits.html#iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits "iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits")(qubits, ...\[, ...\]) | Generate readout error characterization (REC) circuits and preparation strings. |
| [`generate_strings`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings.html#iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings "iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings")(number_of_qubits, ...\[, ...\]) | Generate random preparation strings of 'I' and 'X' characters. |
| [`retrieve_calibration_results`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results.html#iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results "iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results")(job, job_info) | Retrieve and organize measurement results from the calibration circuits. |
| [`run_calibration_circuits`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits.html#iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits "iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits")(iqm_client\[, ...\]) | Execute readout error characterization circuits on a quantum computer and collect measurement results. |

Classes

|  |  |
|----|----|
| [`CalibrationJobInfo`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo")(num_circuits, ...) | Metadata about a submitted calibration job. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.readout_characterization.data_collection](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-4ce5f60a640135e6970dd8c20138d73ebb2ed713.png)
