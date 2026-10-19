> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2f3bec1bd28bd1e6a454ffe95e1658b2806fb818edf547b0d18fafe6b58b89d9.

# channel_property_serializer

Full path: iqm.station_control.client.serializers.channel_property_serializer

Serializers and deserializers for [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")

Module Attributes

|  |  |
|----|----|
| [`InstructionType`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.InstructionType.html#iqm.station_control.client.serializers.channel_property_serializer.InstructionType "iqm.station_control.client.serializers.channel_property_serializer.InstructionType") | One of the instruction classes that can appear in `ChannelProperties.compatible_instructions`. |

Functions

|  |  |
|----|----|
| [`deserialize_channel_properties`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties.html#iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties "iqm.station_control.client.serializers.channel_property_serializer.deserialize_channel_properties")(...\[, ...\]) | Convert the given protobuf dictionary of channel properties into a dictionary of `ChannelProperties`. |
| [`deserialize_instructions`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.deserialize_instructions.html#iqm.station_control.client.serializers.channel_property_serializer.deserialize_instructions "iqm.station_control.client.serializers.channel_property_serializer.deserialize_instructions")(instructions) | Convert a repeated scalar container of instruction type strings into a tuple of python types. |
| [`serialize_channel_properties`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties.html#iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties "iqm.station_control.client.serializers.channel_property_serializer.serialize_channel_properties")(...) | Pack the given dictionary of channel properties into a protobuf format for further serialization. |
| [`unpack_channel_properties`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties.html#iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties "iqm.station_control.client.serializers.channel_property_serializer.unpack_channel_properties")(payload\[, ...\]) | Parse the Channel Property Dictionary from a string serialised protobuf payload. |
