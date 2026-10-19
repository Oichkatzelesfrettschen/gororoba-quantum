> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_return_parameters.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_return_parameters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 363309410470083444326c9351d7a9bfc894878887a6e2c06bd01257e5f4840a.

# exa.common.sweep.database_serialization.decode_return_parameters

decode_return_parameters(*json_str*)  
Deserialize return parameters.

For backwards compatibility, changes values of the return parameters dict to a new, more general format: NdSweeps, which is a list of tuples of Sweeps.

Return parameters JSON syntax: `[{"parameter": readout_parameter_json, "hard_sweeps": [hard_sweep,...]}, ...]`.

`readout_parameter_json` may be a Parameter or a Setting; both will be converted to a Parameter. `hard_sweeps` are converted with the following rules:

- 1 is converted to an empty NdSweep, i.e., a scalar.

- Other integers are converted to a [`linear_index_sweep()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.linear_index_sweep.html#exa.common.sweep.util.linear_index_sweep "exa.common.sweep.util.linear_index_sweep")

- Sweep is converted to an NdSweep that contains only the sweep

- NdSweep and None are not converted.

Parameters:  
**json_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – JSON representation of the `return_parameters` loaded from e.g. persistence

Returns:  
a reconstituted, typed `return_parameters` structure

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep"), …\]\] \| *None*\]
