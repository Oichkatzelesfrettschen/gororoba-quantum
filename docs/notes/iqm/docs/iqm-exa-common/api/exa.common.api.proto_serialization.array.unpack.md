> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.unpack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.unpack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a880dfd7117d9133b4354347ee742496ca7dfb7a6d52522037ab78661cb161d3.

# exa.common.api.proto_serialization.array.unpack

unpack(*source*)  
Unpacks protobuf to array. Reverse operation of [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.pack.html#exa.common.api.proto_serialization.array.pack "exa.common.api.proto_serialization.array.pack").

Parameters:  
**source** (*iqm.data_definitions.common.v1.data_types_pb2.Array*) – A protobuf instance that encapsulates some data.

Returns:  
Unpacked data.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") **or** **google.protobuf.message.DecodeError in case** **of** **invalid buffer** –

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
