> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.unpack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.unpack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7bed696578fbb41544e929e05d4e5a465ca4df1b076789f6e31fb8a7deff2ca3.

# exa.common.api.proto_serialization.sequence.unpack

unpack(*source*)  
Unpacks protobuf to list. Reverse operation of [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.pack.html#exa.common.api.proto_serialization.sequence.pack "exa.common.api.proto_serialization.sequence.pack").

Parameters:  
**source** (*iqm.data_definitions.common.v1.data_types_pb2.Sequence*) – A protobuf instance that encapsulates some data.

Returns:  
Unpacked data.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") **or** **google.protobuf.message.DecodeError in case** **of** **invalid buffer** –

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")
