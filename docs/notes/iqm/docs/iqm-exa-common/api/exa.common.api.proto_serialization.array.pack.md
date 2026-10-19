> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.pack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.pack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 08026c2381ae105b2f166ef1eb78a1bb38a641e15b45f3be120840844f177bdb.

# exa.common.api.proto_serialization.array.pack

pack(*array*)  
Packs a numeric numpy array into protobuf format.

Parameters:  
**array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Numpy array to convert.

Returns:  
A protobuf instance that encapsulates array.

Return type:  
iqm.data_definitions.common.v1.data_types_pb2.Array
