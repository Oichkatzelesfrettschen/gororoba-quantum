> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 65053af249b1b13ac784aa23cf869c6547ba3b0fcc6211a498a51d525fce4942.

# exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget

build_setting_node_widget(*node*)  
Build a lazy, collapsible ipywidgets view of `node`.

Only `node`’s own level is built immediately (its settings plus one collapsed button per child subtree); each child level is built on demand the first time its button is clicked, and cached.

Parameters:  
**node** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode")) – The root [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") to render.

Returns:  
An ipywidgets widget suitable for display in a Jupyter frontend.

Return type:  
widgets.Widget
