> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_settings.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_settings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c848af58086372d5e09a20cf4eb22f5c9150d8b1a40040243b0e11ad31a29bd5.

# exa.common.sweep.database_serialization.decode_settings

decode_settings(*json_str*)  
Deserialize settings from json string

Parameters:  
**json_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – JSON representation of `settings` loaded from e.g. persistence

Returns:  
deserialized settings

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")
