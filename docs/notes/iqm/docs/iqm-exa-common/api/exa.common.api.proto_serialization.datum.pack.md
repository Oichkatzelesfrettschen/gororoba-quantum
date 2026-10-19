> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.pack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.pack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 50f59b5268300be4b733d63073bce8fa1012bb0bccbcc8650cb10b04ec03d4ce.

# exa.common.api.proto_serialization.datum.pack

pack(*value*)  
Packs a string, numerical value, or an array thereof into protobuf format.

Supported data types are: - str - bool - int, float and complex - Sequences of above. Note that the type of Sequence (list, tuple…) is lost in the conversion. - numeric numpy arrays - None

Parameters:  
**value** (*None* *\|* [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")) – The piece of data to convert.

Returns:  
A protobuf instance that encapsulates value.

Raises:  
**ValidationError in case** **of** **unsupported type.** –

Return type:  
iqm.data_definitions.common.v1.data_types_pb2.Datum
