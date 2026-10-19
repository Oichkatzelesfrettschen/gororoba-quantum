> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 01025b87a34f7632a2f73a30fab61c23ca2390d0d8537a9f040079103180e566.

# post_process

Full path: iqm.cpc.compiler.post_process

Post-processing utility functions for Experiment.

Module Attributes

|  |  |
|----|----|
| [`COUNTER_INDEX`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.COUNTER_INDEX.html#iqm.cpc.compiler.post_process.COUNTER_INDEX "iqm.cpc.compiler.post_process.COUNTER_INDEX") | MultiQubitCounter state index. |
| [`MeasurementResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.MeasurementResults.html#iqm.cpc.compiler.post_process.MeasurementResults "iqm.cpc.compiler.post_process.MeasurementResults") | Measurement results for a single circuit. |
| [`MeasurementResultsBatch`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.MeasurementResultsBatch.html#iqm.cpc.compiler.post_process.MeasurementResultsBatch "iqm.cpc.compiler.post_process.MeasurementResultsBatch") | Type that represents measurement results for a batch of circuits. |
| [`GeneralReadoutMapping`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.GeneralReadoutMapping.html#iqm.cpc.compiler.post_process.GeneralReadoutMapping "iqm.cpc.compiler.post_process.GeneralReadoutMapping") | Type for matching measurement keys from a quantum circuit with acquisition labels in Station Control. |
| [`GeneralReadoutMappingBatch`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.GeneralReadoutMappingBatch.html#iqm.cpc.compiler.post_process.GeneralReadoutMappingBatch "iqm.cpc.compiler.post_process.GeneralReadoutMappingBatch") | Type that represents readout mappings for a batch of circuits. |

Functions

|  |  |
|----|----|
| [`add_counter_averaged_readout`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counter_averaged_readout.html#iqm.cpc.compiler.post_process.add_counter_averaged_readout "iqm.cpc.compiler.post_process.add_counter_averaged_readout")(run) | Add single-qubit excited state probabilities from the multi qubit counter results to the dataset. |
| [`add_counts_for`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counts_for.html#iqm.cpc.compiler.post_process.add_counts_for "iqm.cpc.compiler.post_process.add_counts_for")(run) | Add single-qubit excited state probabilities from the multi qubit counter results to the dataset. |
| [`average_single_shot_data`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.average_single_shot_data.html#iqm.cpc.compiler.post_process.average_single_shot_data "iqm.cpc.compiler.post_process.average_single_shot_data")(run) | Average the shots (or more generally the average bins) into a new data variable in the dataset. |
| [`classify_two_states`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.classify_two_states.html#iqm.cpc.compiler.post_process.classify_two_states "iqm.cpc.compiler.post_process.classify_two_states")(run) | Classify the complex data using the calibrated threshold. |
| [`compute_excitation_probability_from_data`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.compute_excitation_probability_from_data.html#iqm.cpc.compiler.post_process.compute_excitation_probability_from_data "iqm.cpc.compiler.post_process.compute_excitation_probability_from_data")(run) | Compute the excited state probability for several components. |
| [`construct_circuit_execution_results`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_circuit_execution_results.html#iqm.cpc.compiler.post_process.construct_circuit_execution_results "iqm.cpc.compiler.post_process.construct_circuit_execution_results")(...) | Construct a [`CircuitExecutionResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html#iqm.cpc.compiler.post_process.CircuitExecutionResults "iqm.cpc.compiler.post_process.CircuitExecutionResults"). |
| [`construct_run_result`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_run_result.html#iqm.cpc.compiler.post_process.construct_run_result "iqm.cpc.compiler.post_process.construct_run_result")(sweep_results, context) | Construct the dataset and attach it to a RunResult object. |
| [`contrast_data`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.contrast_data.html#iqm.cpc.compiler.post_process.contrast_data "iqm.cpc.compiler.post_process.contrast_data")(run) | Add contrast for several components/readouts. |
| [`create_ragged_data_index`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.create_ragged_data_index.html#iqm.cpc.compiler.post_process.create_ragged_data_index "iqm.cpc.compiler.post_process.create_ragged_data_index")(run) | Adds `MultiIndex` to the trigger index dimension for accessing ragged data via the hard sweep values. |
| [`extract_counter_group_data`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.extract_counter_group_data.html#iqm.cpc.compiler.post_process.extract_counter_group_data "iqm.cpc.compiler.post_process.extract_counter_group_data")(run) | Extracts the data for all counter readout groups into their own data variables in the dataset. |
| [`process_metadata`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.process_metadata.html#iqm.cpc.compiler.post_process.process_metadata "iqm.cpc.compiler.post_process.process_metadata")(run) | Process the metadata in the RunResult. |
| [`rename_data_variables`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.rename_data_variables.html#iqm.cpc.compiler.post_process.rename_data_variables "iqm.cpc.compiler.post_process.rename_data_variables")(run, context) | Rename the data variables in the dataset and optionally change their data types. |

Classes

|  |  |
|----|----|
| [`CircuitExecutionResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html#iqm.cpc.compiler.post_process.CircuitExecutionResults "iqm.cpc.compiler.post_process.CircuitExecutionResults") | Old Pulla style circuit execution results. |

Inheritance

![Inheritance diagram of iqm.cpc.compiler.post_process](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-bce10c20cf2220c14c4ca6a579519c0663ff82cb.png)
