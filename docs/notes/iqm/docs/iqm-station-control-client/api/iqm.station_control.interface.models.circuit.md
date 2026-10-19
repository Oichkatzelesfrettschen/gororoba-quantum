> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7c6a24a5b3bc8a1702029eb31efec331a6fb6acb9380e4fd90244c1d89f8b6e1.

# circuit

Full path: iqm.station_control.interface.models.circuit

Models related to quantum circuit execution.

Module Attributes

|  |  |
|----|----|
| [`PRXSequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PRXSequence.html#iqm.station_control.interface.models.circuit.PRXSequence "iqm.station_control.interface.models.circuit.PRXSequence") | Sequence of PRX gates. |
| [`QIRCode`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.QIRCode.html#iqm.station_control.interface.models.circuit.QIRCode "iqm.station_control.interface.models.circuit.QIRCode") | QIR program code in string representation. |
| [`CircuitBatch`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitBatch.html#iqm.station_control.interface.models.circuit.CircuitBatch "iqm.station_control.interface.models.circuit.CircuitBatch") | Sequence of quantum circuits to be executed together in a single batch. |
| [`CircuitMeasurementResults`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementResults.html#iqm.station_control.interface.models.circuit.CircuitMeasurementResults "iqm.station_control.interface.models.circuit.CircuitMeasurementResults") | Measurement results from a single circuit. |
| [`CircuitMeasurementResultsBatch`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementResultsBatch.html#iqm.station_control.interface.models.circuit.CircuitMeasurementResultsBatch "iqm.station_control.interface.models.circuit.CircuitMeasurementResultsBatch") | Type that represents measurement results for a batch of circuits. |
| [`QubitMapping`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.QubitMapping.html#iqm.station_control.interface.models.circuit.QubitMapping "iqm.station_control.interface.models.circuit.QubitMapping") | Mapping from logical qubit names to physical qubit names. |

Classes

|  |  |
|----|----|
| [`CircuitJobDefinition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitJobDefinition.html#iqm.station_control.interface.models.circuit.CircuitJobDefinition "iqm.station_control.interface.models.circuit.CircuitJobDefinition") | alias of [`PostJobsRequest`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest") |
| [`CircuitMeasurementCounts`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts") | Circuit measurement counts in histogram representation. |
| [`DDMode`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDMode.html#iqm.station_control.interface.models.circuit.DDMode "iqm.station_control.interface.models.circuit.DDMode") | Dynamical Decoupling (DD) mode for circuit execution. |
| [`DDStrategy`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "iqm.station_control.interface.models.circuit.DDStrategy") | Describes a particular dynamical decoupling strategy. |
| [`HeraldingMode`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.HeraldingMode.html#iqm.station_control.interface.models.circuit.HeraldingMode "iqm.station_control.interface.models.circuit.HeraldingMode") | Heralding mode for circuit execution. |
| [`MoveGateFrameTrackingMode`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.html#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode") | MOVE gate reference frame tracking mode for circuit compilation. |
| [`MoveGateValidationMode`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateValidationMode.html#iqm.station_control.interface.models.circuit.MoveGateValidationMode "iqm.station_control.interface.models.circuit.MoveGateValidationMode") | MOVE gate validation mode for circuit compilation. |
| [`PostJobsRequest`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest") | Request to Station Control run a job that executes a batch of quantum circuits. |
| [`RunRequest`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.RunRequest.html#iqm.station_control.interface.models.circuit.RunRequest "iqm.station_control.interface.models.circuit.RunRequest") | alias of [`PostJobsRequest`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.PostJobsRequest.html#iqm.station_control.interface.models.circuit.PostJobsRequest "iqm.station_control.interface.models.circuit.PostJobsRequest") |

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-5b896485da9d6d880b306d9de50a9d1cbf0c4b87.png)
