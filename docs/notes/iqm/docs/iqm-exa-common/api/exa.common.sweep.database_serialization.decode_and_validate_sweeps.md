> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_and_validate_sweeps.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_and_validate_sweeps.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 deabe30eda822b99dff8658864969c3d733dc096c1229b8387bf1ccd3707bdbc.

# exa.common.sweep.database_serialization.decode_and_validate_sweeps

decode_and_validate_sweeps(*sweeps_json*)  
Decodes and validates json string of list of Sweeps and tuples of Sweeps.

Parameters:  
**sweeps_json** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – json string of nested structure of Sweep objects

Returns:  
list of sweeps and tuples of sweeps

Raises:  
**ValidationError if decoded result is not expected return type** –

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep") \| [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep"), …\]\]
