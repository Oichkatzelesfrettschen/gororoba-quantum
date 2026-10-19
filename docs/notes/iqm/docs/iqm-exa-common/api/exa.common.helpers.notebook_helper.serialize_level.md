> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.serialize_level.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.serialize_level.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2ee002c5b2a1c6dc0a72049611eb0fc60900bff2d34a7c0d1753ca46f26d81cb.

# exa.common.helpers.notebook_helper.serialize_level

serialize_level(*node*)  
Serialize only `node`’s own level (its settings and immediate children) for display.

The children are described by metadata only (not recursed into), which is what makes the widget renderer lazy: deeper levels are serialized on demand when the user expands them.

Parameters:  
**node** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")) – The node whose own level is serialized.

Returns:  
A dict with `name`, `cls`, `settings` and `children` keys.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), *Any*\]
