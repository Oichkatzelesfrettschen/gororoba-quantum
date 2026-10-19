> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.fallback_text.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.fallback_text.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 51cde5ba911477f6b1c7a5479de567f85926a25ad27cd14daf461b53e02726ee.

# exa.common.helpers.notebook_helper.fallback_text

fallback_text(*node*)  
Plain-text root-only summary, used as the widget’s `text/plain` degradation message.

This goes in `text/plain` (the lowest-priority MIME) rather than `text/html` so that it never shadows the widget view when a widget manager is present, while still showing something readable in static / no-manager contexts.

Parameters:  
**node** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "exa.common.data.setting_node.SettingNode"))

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
