> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.to_json_dict.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.to_json_dict.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ac1b165840680fe7c9164991951e5a355fc8a4a93d641e7368bf83ae8f64ddf5.

# iqm.iqm_client.util.to_json_dict

iqm.iqm_client.util.to_json_dict(*obj: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")  
Convert a dict to JSON serializable dict.

Parameters:  
**obj** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – dict to convert

Returns:  
dict containing converted data

Raises:  
**ValueError if the original dict contains unsupported datatypes** –

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")
