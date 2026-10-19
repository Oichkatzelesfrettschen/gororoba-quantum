> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 74a966d049fb6a3c97666d6316157bbe0aefc81df59384068d102958a6978c62.

# proto_serialization

Full path: exa.common.api.proto_serialization

Conversions between Protocol buffers in `iqm.data_structures.common` and Python objects in exa-common.

Each submodule corresponds to a Protobuf definition from `iqm.data_structures.common`. Each module has at least 2 functions, `pack` and `unpack`, which pack the Python type into a Protobuf instance or vice versa.

The packed objects can be nested when constructing new Protobuf objects. It is intended that the user does the final serialization using the Protobuf service methods.

Subpackages and modules

|  |  |
|----|----|
| [`array`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.array.html#module-exa.common.api.proto_serialization.array "exa.common.api.proto_serialization.array") | Convert numpy arrays to protos and back. |
| [`datum`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.html#module-exa.common.api.proto_serialization.datum "exa.common.api.proto_serialization.datum") | Convert native Python types and numpy arrays to protos and back. |
| [`nd_sweep`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.nd_sweep.html#module-exa.common.api.proto_serialization.nd_sweep "exa.common.api.proto_serialization.nd_sweep") | Convert NdSweeps to protos and back. |
| [`sequence`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.sequence.html#module-exa.common.api.proto_serialization.sequence "exa.common.api.proto_serialization.sequence") | Convert Python Sequences to protos and back. |
| [`setting_node`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.html#module-exa.common.api.proto_serialization.setting_node "exa.common.api.proto_serialization.setting_node") | Convert SettingNodes to protos and back. |
