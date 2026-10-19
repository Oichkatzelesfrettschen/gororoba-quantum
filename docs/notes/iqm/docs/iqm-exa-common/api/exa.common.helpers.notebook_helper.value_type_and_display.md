> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.value_type_and_display.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.value_type_and_display.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 045781aec4e1bc6ef8d41090b6f23a563bfc00f4316b8a4c58320ae6f7537a51.

# exa.common.helpers.notebook_helper.value_type_and_display

value_type_and_display(*value*)  
Classify a value and format it for display, mirroring the jinja template.

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The (already SI-rescaled) value to classify and format.

Returns:  
A `(type, display)` pair where `type` is one of `none`, `bool`, `number`, `string`, `sequence` or `other`.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
