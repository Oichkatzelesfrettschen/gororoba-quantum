> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_run_job_request.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_run_job_request.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 54d24fba257749b5f274dd3a7413e94f747ee09998c4a6a6078e1f67b5c032ef.

# iqm.station_control.client.serializers.task_serializers.serialize_run_job_request

serialize_run_job_request(*run_definition*, *queue_name*)  
Wrap run_definition and queue_name into a protobuf message and serialize into a bitstring.

Parameters:  
- **run_definition** ([*RunDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "iqm.station_control.interface.models.run.RunDefinition")) – The content of the run.

- **queue_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the destination queue.

Returns:  
[`SweepTaskRequest`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v1.task_service_pb2.SweepTaskRequest.html#iqm.data_definitions.station_control.v1.task_service_pb2.SweepTaskRequest "(in IQM data definitions v3.1.0)") encoded into a bitstring.

Return type:  
[*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")
