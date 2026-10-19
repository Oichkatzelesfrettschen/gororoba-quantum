> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_return_parameters.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_return_parameters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f0d1cb4386d5d15ad9a66d5005cd98df84dc92ab3206401a06287d6ebcbe049f.

# exa.common.sweep.database_serialization.encode_return_parameters

encode_return_parameters(*return_parameters*, *\*\*kwargs*)  
Encode sweeps to a JSON string.

Parameters:  
- **return_parameters** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep")*,* *...\]\]* *\|* *None\]*) – Return parameters as specified by `sweep()`.

- **kwargs** – keyword arguments passed to json.dumps

Returns:  
json as a string

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
