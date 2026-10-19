> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.pack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.pack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d03bd9da7ba49de5cc8820ae79a60544fddfa722deae6b070c80e8719ce8b5e9.

# exa.common.api.proto_serialization.sequence.pack

pack(*values*)  
Packs a sequence of native Python types into protobuf format.

Parameters:  
**values** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")) – Sequence to convert.

Returns:  
A protobuf instance that encapsulates values.

Raises:  
**ValueError in case** **of** **unsupported value.** –

Return type:  
iqm.data_definitions.common.v1.data_types_pb2.Sequence
