> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.struct_serializer.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.struct_serializer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd465e87cce82000a5ab8eecbdb3cf7e85343d8727c20b0892336af2ddf4cc31.

# struct_serializer

Full path: iqm.station_control.client.serializers.struct_serializer

Serializers and deserializers for struct related models.

We use custom Struct model instead of standard Struct from protobuf, since standard Struct doesn’t support integers but instead casts them always to floats.

Functions

|  |  |
|----|----|
| [`deserialize_struct`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.struct_serializer.deserialize_struct.html#iqm.station_control.client.serializers.struct_serializer.deserialize_struct "iqm.station_control.client.serializers.struct_serializer.deserialize_struct")(proto) | Deserialize a Struct protobuf representation into a free-form dict. |
| [`serialize_struct`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.struct_serializer.serialize_struct.html#iqm.station_control.client.serializers.struct_serializer.serialize_struct "iqm.station_control.client.serializers.struct_serializer.serialize_struct")(data) | Serialize a free-form dict into a Struct protobuf representation. |
