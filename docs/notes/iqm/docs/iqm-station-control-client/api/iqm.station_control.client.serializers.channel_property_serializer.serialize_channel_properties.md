> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f8beaa6fd60a9e92a37f121cb94587055bdf8efc5b1eff19955004981e504fee.

# iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties

serialize_channel_properties(*channel_property_dictionary*)  
Pack the given dictionary of channel properties into a protobuf format for further serialization.

Parameters:  
- **channel_properties** – channel properties to pack

- **channel_property_dictionary** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")*\]*)

Returns:  
`ChannelPropertyDictionary`

Return type:  
[*ChannelPropertyDictionary*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary.html#iqm.data_definitions.common.v1.channel_properties_pb2.ChannelPropertyDictionary "(in IQM data definitions v3.1.0)")
