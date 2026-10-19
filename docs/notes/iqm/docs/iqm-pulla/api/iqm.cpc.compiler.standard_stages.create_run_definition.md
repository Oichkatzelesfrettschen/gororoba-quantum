> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.create_run_definition.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.create_run_definition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5a99ecf2cbbbb046a34c78114a3a5b169a19df28b11132d7ddba91ab2165afbb.

# iqm.cpc.compiler.standard_stages.create_run_definition

iqm.cpc.compiler.standard_stages.create_run_definition(*playlist*, *context*, *data_size_safety_switch=True*, *force_ragged_data=False*)  
Create MQE-style RunDefinition.

Parameters:  
- **playlist** (*Playlist*) – The Playlist to create the RunDefinition for.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The Compiler context.

- **data_size_safety_switch** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to throw an error with exceedingly large return data sizes (set to `False` if you want to still run the job and are sure the DB and/or the stack can handle it).

- **force_ragged_data** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to force the return data to the sparse ragged format even if the dimensions are representable as a cartesian product.

Returns:  
The RunDefinition.

Return type:  
[*RunDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "(in iqm-station-control-client v14.0.0)")
