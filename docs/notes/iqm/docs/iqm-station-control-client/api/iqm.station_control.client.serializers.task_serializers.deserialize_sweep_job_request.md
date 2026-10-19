> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d531dd8119849d61ff3e322d23396b05e6e532d6e64fd960b2dca7720f520a56.

# iqm.station_control.client.serializers.task_serializers.deserialize_sweep_job_request

deserialize_sweep_job_request(*data*)  
Deserialize `sweep_definition` and `queue_name` from the serialized data.

Parameters:  
**data** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")) – The serialized data.

Returns:  
Deserialized sweep definition, queue name.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*SweepDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinition.html#iqm.station_control.interface.models.sweep.SweepDefinition "iqm.station_control.interface.models.sweep.SweepDefinition"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
