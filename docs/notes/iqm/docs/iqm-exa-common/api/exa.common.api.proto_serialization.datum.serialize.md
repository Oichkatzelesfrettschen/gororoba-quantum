> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.serialize.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.serialize.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0ef42df9c728f58dbd6e7de17d724ee09ab7549ef4c99217fc37919547afc21e.

# exa.common.api.proto_serialization.datum.serialize

serialize(*value*)  
Serialize a piece of data into a bitstring.

Parameters:  
**value** (*None* *\|* [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")) – same as in [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.pack.html#exa.common.api.proto_serialization.datum.pack "exa.common.api.proto_serialization.datum.pack").

Returns:  
Bitstring that encodes value.

Return type:  
[*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")
