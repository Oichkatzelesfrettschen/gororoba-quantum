> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.widgets.setting_node_widget.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.widgets.setting_node_widget.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 95b6f9de430b881d2a7c07a069ac5d956313f3d6deca4d5df74b97eba7f14c06.

# setting_node_widget

Full path: exa.common.helpers.widgets.setting_node_widget

Lazy Jupyter renderer for [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") built from stock `ipywidgets`.

A [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode") tree can be huge (tens of thousands of settings for a 50+ qubit system), and rendering the whole tree up front is slow and produces a very large DOM. This builds a collapsible view from stock ipywidgets: each subtree is a `Button` (styled as a summary row) plus a hidden `VBox` body that is only built the first time the user opens it, and wide levels are paginated with a “Show more” button, so the initial display cost is proportional to the root level alone.

It uses only core ipywidgets (`Button`/`VBox`/`HTML`), which are bundled into the Jupyter frontends (incl. VS Code) - no custom JavaScript, no bundling, no comm wiring. Styling is done through our own scoped CSS classes (`exa-*`) rather than the frontend’s internal widget classes, so it is stable across frontends.

This module imports `ipywidgets` at import time. It is imported lazily by [`exa.common.helpers.notebook_helper.repr_mimebundle()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.repr_mimebundle.html#exa.common.helpers.notebook_helper.repr_mimebundle "exa.common.helpers.notebook_helper.repr_mimebundle"), which falls back to a static summary when `ipywidgets` is missing, so importing [`exa.common.data.setting_node`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.html#module-exa.common.data.setting_node "exa.common.data.setting_node") never requires `ipywidgets`.

Functions

|  |  |
|----|----|
| [`build_setting_node_widget`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget.html#exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget "exa.common.helpers.widgets.setting_node_widget.build_setting_node_widget")(node) | Build a lazy, collapsible ipywidgets view of `node`. |
