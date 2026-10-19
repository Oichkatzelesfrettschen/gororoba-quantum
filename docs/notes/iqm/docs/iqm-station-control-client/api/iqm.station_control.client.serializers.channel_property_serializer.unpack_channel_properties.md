> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 56cb667b4f50720a7818b0db33c42a341401080208118b38b672bf8573882f03.

# iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties

unpack_channel_properties(*payload*, *convert_instructions=True*)  
Parse the Channel Property Dictionary from a string serialised protobuf payload.

Parameters:  
- **payload** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")) – protobuf serialised payload of channel property dictionary.

- **convert_instructions** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to convert string representation of instruction types to actual python types.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")\]
