> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_nd_sweeps.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_nd_sweeps.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a651424295693a9d4a547a7fde2453e406330a3872802f6036cf22a2c0eb2d7c.

# exa.common.sweep.database_serialization.encode_nd_sweeps

encode_nd_sweeps(*sweeps*, *\*\*kwargs*)  
Encode sweeps to a JSON string.

Parameters:  
- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep")*,* *...\]\]*) – sweeps to be serialized.

- **kwargs** – keyword arguments passed to json.dumps

Returns:  
json as a string

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
