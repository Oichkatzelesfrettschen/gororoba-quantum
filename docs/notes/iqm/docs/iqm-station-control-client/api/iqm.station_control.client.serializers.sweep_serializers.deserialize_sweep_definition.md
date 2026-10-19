> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eb45590cfdfe1ffd1cbc360097d8c99ca8e60e8b895d9f724061d318b57fdb74.

# iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition

deserialize_sweep_definition(*sweep_definition_proto*)  
Convert sweep proto into SweepDefinition.

Raises:  
**ValidationError** – If `sweep_definition_proto` does not decode into a valid sweep definition.

Parameters:  
**sweep_definition_proto** ([*SweepRequest*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.station_control.v1.sweep_request_pb2.SweepRequest.html#iqm.data_definitions.station_control.v1.sweep_request_pb2.SweepRequest "(in IQM data definitions v3.1.0)"))

Return type:  
[*SweepDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinition.html#iqm.station_control.interface.models.sweep.SweepDefinition "iqm.station_control.interface.models.sweep.SweepDefinition")
