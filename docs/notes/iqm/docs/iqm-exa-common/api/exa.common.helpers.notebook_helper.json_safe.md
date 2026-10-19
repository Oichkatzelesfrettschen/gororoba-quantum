> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.json_safe.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.notebook_helper.json_safe.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1ce5efa25bdb20d6a84a4abc3e04826a0352c1585e01bff6e1c2ec02864acb00.

# exa.common.helpers.notebook_helper.json_safe

json_safe(*value*)  
Convert a value into a JSON-serializable form for display tooltips.

Parameters:  
**value** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – Arbitrary setting value (may contain numpy types).

Returns:  
A JSON-safe representation; non-convertible objects fall back to `str`.

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")
