> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.pack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.pack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b87aaaca3e697bfb9654c9589d70439312dfcd1b333c21a26689d5eba2cb8bfe.

# exa.common.api.proto_serialization.nd_sweep.pack

pack(*nd_sweep*, *minimal=True*)  
Convert an NdSweep into protobuf representation.

Note: The protobuf does not make any distinction between different types of Sweeps, so the type information is lost.

Parameters:  
- **nd_sweep** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep")*,* *...\]\]*)

- **minimal** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Return type:  
iqm.data_definitions.common.v1.sweep_pb2.CartesianSweep
