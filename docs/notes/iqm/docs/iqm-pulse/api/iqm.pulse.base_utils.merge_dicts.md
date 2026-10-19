> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.base_utils.merge_dicts.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.base_utils.merge_dicts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 78e74a75cb41b8e18e2610b397e456f64478f24fe5ef65db02278e0d741a4a1e.

# iqm.pulse.base_utils.merge_dicts

iqm.pulse.base_utils.merge_dicts(*A*, *B*, *path=()*, *merge_nones=True*)  
Merge two dictionaries recursively, leaving the originals unchanged.

Parameters:  
- **A** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Dictionary.

- **B** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Another dictionary.

- **path** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Current path into the nested dictionaries, for error reporting.

- **merge_nones** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to also merge `None` and empty `Sized` values from B to A.

Returns:  
Copy of A, with the contents of B merged in (and taking precedence) recursively.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]
