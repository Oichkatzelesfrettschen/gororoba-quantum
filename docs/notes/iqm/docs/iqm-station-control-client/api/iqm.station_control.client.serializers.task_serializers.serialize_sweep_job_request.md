> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a33ae0bbd21b8419197b611bfd055699c61964beb37a43833087be0416d93519.

# iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request

serialize_sweep_job_request(*sweep_definition*, *queue_name*, *sweep_results_format=SweepResultsArtifactFormat.LEGACY_PROTOBUF*)  
Wrap sweep_definition and queue_name into a protobuf message and serialize into a bitstring.

Parameters:  
- **sweep_definition** ([*SweepDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinition.html#iqm.station_control.interface.models.sweep.SweepDefinition "iqm.station_control.interface.models.sweep.SweepDefinition")) – The content of the sweep.

- **queue_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the destination queue.

- **sweep_results_format** ([*SweepResultsArtifactFormat*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat.html#iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat "iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat"))

Returns:  
[`SweepTaskRequest`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v1.task_service_pb2.SweepTaskRequest.html#iqm.data_definitions.station_control.v1.task_service_pb2.SweepTaskRequest "(in IQM data definitions v3.1.0)") encoded into a bitstring.

Return type:  
[*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")
