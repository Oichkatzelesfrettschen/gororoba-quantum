> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6412fd9ba0295800903513fe0dc0e278716dde8097a48c70f96c84853a1c2189.

# iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties

deserialize_channel_properties(*channel_property_dictionary*, *convert_instructions=True*)  
Convert the given protobuf dictionary of channel properties into a dictionary of `ChannelProperties`.

Parameters:  
- **channel_properties_dictionary** – channel property dictionary in protobuf format

- **convert_instructions** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to convert string representation of instruction types to actual python types.

- **channel_property_dictionary** ([*ChannelPropertyDictionary*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary.html#iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary "(in IQM data definitions v3.1.0)"))

Returns:  
dictionary of channel properties

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]
