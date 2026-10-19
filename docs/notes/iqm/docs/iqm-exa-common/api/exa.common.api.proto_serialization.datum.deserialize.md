> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.deserialize.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.deserialize.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d97716f9180d991f032dec3047783a6d521cf46da68a52f29421b7cecd151937.

# exa.common.api.proto_serialization.datum.deserialize

deserialize(*source*)  
Deserialize a bitstring into a native Python type or a numpy array. Reverse operation of [`serialize()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.serialize.html#exa.common.api.proto_serialization.datum.serialize "exa.common.api.proto_serialization.datum.serialize").

Parameters:  
**source** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")) – Bitstring that encodes some data.

Returns:  
Deserialized data.

Return type:  
*None* \| [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")
