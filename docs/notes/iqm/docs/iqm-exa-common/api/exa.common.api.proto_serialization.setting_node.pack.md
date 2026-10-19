> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.pack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.pack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a809c51456d5fae2a66cc8fac7bdc0938157186a8cb1ebdc8d6621c224c9174.

# exa.common.api.proto_serialization.setting_node.pack

pack(*node*, *minimal*)  
Convert a SettingNode into protobuf representation.

Silently coerces some datatypes to be compatible with the proto definition of `Datum`: - Numpy arrays of 32-bit ints are converted to 64-bits (Windows only). - Singular numpy types are converted into corresponding native types.

Parameters:  
- **node** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")) – SettingNode to pack, recursively.

- **minimal** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, only the [`Parameter.name`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter.name "exa.common.data.parameter.Parameter.name") of each Setting is preserved along with the setting value. Otherwise, the whole `Setting` is packed. Set to True only when transmitting Settings from clients to Station Control, in the other direction we need all the data.

Returns:  
Protobuf instance that represents node.

Return type:  
iqm.data_definitions.common.v1.setting_pb2.SettingNode
