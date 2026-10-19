> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.unpack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.unpack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 77cea31dcfa4979f4bf9d3110f9285f1097f90c7ce519b0d8967ca1a9fda57bf.

# exa.common.api.proto_serialization.nd_sweep.unpack

unpack(*proto*)  
Convert protobuf representation into a NdSweep. Reverse operation of [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.pack.html#exa.common.api.proto_serialization.nd_sweep.pack "exa.common.api.proto_serialization.nd_sweep.pack").

Parameters:  
**proto** (*iqm.data_definitions.common.v1.sweep_pb2.CartesianSweep*)

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep"), …\]\]
