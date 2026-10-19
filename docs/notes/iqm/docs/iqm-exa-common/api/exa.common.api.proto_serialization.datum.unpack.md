> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.unpack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.unpack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b42c5b4ddfc5b8e8b6363ef96a91634a44a81f6f83ae0ca95a732ad0e9b4cc44.

# exa.common.api.proto_serialization.datum.unpack

unpack(*source*)  
Unpacks a protobuf into a native Python type or a numpy array. Reverse operation of [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.pack.html#exa.common.api.proto_serialization.datum.pack "exa.common.api.proto_serialization.datum.pack").

Parameters:  
**source** (*iqm.data_definitions.common.v1.data_types_pb2.Datum*) – A protobuf instance that encapsulates some data.

Returns:  
Unpacked data.

Raises:  
[**ValidationError**](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError") **or** **google.protobuf.message.DecodeError in case** **of** **invalid buffer** –

Return type:  
*None* \| [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")
