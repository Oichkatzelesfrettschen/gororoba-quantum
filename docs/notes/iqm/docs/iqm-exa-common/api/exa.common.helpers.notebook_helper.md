> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 407681b92da81a75dc68db2d55b96529b59bc543de9fc126b74bda88a3f15d82.

# notebook_helper

Full path: exa.common.helpers.notebook_helper

Jupyter notebook rendering helpers for [`SettingNode`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode").

Functions

|  |  |
|----|----|
| [`fallback_html`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.fallback_html.html#exa.common.helpers.notebook_helper.fallback_html "exa.common.helpers.notebook_helper.fallback_html")(node) | Cheap root-only HTML summary, used when no live widget manager is available. |
| [`fallback_text`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.fallback_text.html#exa.common.helpers.notebook_helper.fallback_text "exa.common.helpers.notebook_helper.fallback_text")(node) | Plain-text root-only summary, used as the widget's `text/plain` degradation message. |
| [`json_safe`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.json_safe.html#exa.common.helpers.notebook_helper.json_safe "exa.common.helpers.notebook_helper.json_safe")(value) | Convert a value into a JSON-serializable form for display tooltips. |
| [`node_header_html`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.node_header_html.html#exa.common.helpers.notebook_helper.node_header_html "exa.common.helpers.notebook_helper.node_header_html")(key, name, cls) | Render the per-node header line (key + name + class). |
| [`repr_mimebundle`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.repr_mimebundle.html#exa.common.helpers.notebook_helper.repr_mimebundle "exa.common.helpers.notebook_helper.repr_mimebundle")(node\[, include, exclude\]) | Backing implementation of `SettingNode._repr_mimebundle_()`. |
| [`serialize_level`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.serialize_level.html#exa.common.helpers.notebook_helper.serialize_level "exa.common.helpers.notebook_helper.serialize_level")(node) | Serialize only `node`'s own level (its settings and immediate children) for display. |
| [`settings_html`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.settings_html.html#exa.common.helpers.notebook_helper.settings_html "exa.common.helpers.notebook_helper.settings_html")(settings) | Render a single level's serialized settings as an HTML table (empty string if none). |
| [`value_type_and_display`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.value_type_and_display.html#exa.common.helpers.notebook_helper.value_type_and_display "exa.common.helpers.notebook_helper.value_type_and_display")(value) | Classify a value and format it for display, mirroring the jinja template. |
