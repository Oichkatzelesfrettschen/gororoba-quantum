> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad895e27036953ad0cd3091f9854eceb38ff8804b74c8a09b7a48b878d533fc7.

# task_serializers

Full path: iqm.station_control.client.serializers.task_serializers

Serializers and deserializers for task related models.

Functions

|  |  |
|----|----|
| [`deserialize_sweep_job_request`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request.html#iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request "iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request")(data) | Deserialize `sweep_definition` and `queue_name` from the serialized data. |
| [`serialize_run_job_request`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_run_job_request.html#iqm.station_control.client.serializers.task_serializers.serialize_run_job_request "iqm.station_control.client.serializers.task_serializers.serialize_run_job_request")(run_definition, ...) | Wrap run_definition and queue_name into a protobuf message and serialize into a bitstring. |
| [`serialize_sweep_job_request`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request.html#iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request "iqm.station_control.client.serializers.task_serializers.serialize_sweep_job_request")(...\[, ...\]) | Wrap sweep_definition and queue_name into a protobuf message and serialize into a bitstring. |
