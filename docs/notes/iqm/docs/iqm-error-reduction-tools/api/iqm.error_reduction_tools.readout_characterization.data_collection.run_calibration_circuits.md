> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7d72b88dad80b985f67439fe6930f154eb0aa7598bb7deff763e4768c6127fd6.

# iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits

iqm.error_reduction_tools.readout_characterization.data_collection.run_calibration_circuits(*iqm_client*, *qubits=None*, *number_of_circuits=50*, *shots=50000*, *symmetrize=True*, *seed=None*, *equatorial_randomization=True*)  
Execute readout error characterization circuits on a quantum computer and collect measurement results.

Generates random basis state preparation circuits and runs them on the specified QC.

Parameters:  
- **iqm_client** ([*IQMClient*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "(in IQM client v36.0.0)")) – Client for connecting to an IQM quantum computer.

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Use `None` to characterize every *operational* QPU qubit (qubits with a calibrated `measure` gate), or a list of specific qubit names (e.g., `["QB1", "QB2"]`). Explicitly requested qubits that are not operational are dropped with a warning.

- **number_of_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of distinct calibration circuits to run.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total measurement shots distributed across all circuits. Each circuit receives `shots // number_of_circuits` shots.

- **symmetrize** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, generates complementary preparation pairs (I↔X).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Random seed for reproducible preparation string generation.

- **equatorial_randomization** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, randomizes X gate phase angles.

Returns:  
Tracker for submitted job, metadata about the job.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `shots` \< `number_of_circuits` (no shots per circuit), or if no operational qubits remain to characterize.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*RunJobTracker*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.job_trackers.RunJobTracker.html#iqm.station_control.client.job_trackers.RunJobTracker "(in iqm-station-control-client v14.0.0)"), [*CalibrationJobInfo*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo")\]
