> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9bffeecfc911182c89705cfd4889b3f44ce4d3a108c51dbe38d0078f15584028.

# iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings

iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings(*counts*)  
Remove whitespace from bitstring keys in a counts dictionary.

Parameters:  
**counts** ([*Mapping*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *\_V\]*) – Dictionary mapping bitstrings (possibly with spaces) to counts.

Returns:  
Dictionary with whitespace removed from all bitstring keys.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), *\_V*\]

Example

```
>>> remove_whitespace_from_bitstrings({"0 1": 10, "1 0": 5})
{'01': 10, '10': 5}
```
