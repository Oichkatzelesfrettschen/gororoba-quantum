> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.unpack.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.unpack.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6824c8c9e7d15a2c46105d716815116a85f9887b5d7856f2804838dd761aa5ce.

# exa.common.api.proto_serialization.setting_node.unpack

unpack(*proto*)  
Convert protobuf representation into a SettingNode. Reverse operation of [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.pack.html#exa.common.api.proto_serialization.setting_node.pack "exa.common.api.proto_serialization.setting_node.pack")

Parameters:  
**proto** (*iqm.data_definitions.common.v1.setting_pb2.SettingNode*) – Protobuf instance to unpack, recursively.

Returns:  
Unpacked SettingNode. In case proto only contains the parameter names (see `optimize` in [`pack()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.setting_node.pack.html#exa.common.api.proto_serialization.setting_node.pack "exa.common.api.proto_serialization.setting_node.pack")), dummy Parameters are generated.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")
