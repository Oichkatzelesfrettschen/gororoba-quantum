> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.populate_from_configs.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.populate_from_configs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2c2cfc4288d361019c0a350d0259102d60f392e82eaebac90efe802c648ed71a.

# iqm.cpc.core.observation.observation_load_utils.populate_from_configs

iqm.cpc.core.observation.observation_load_utils.populate_from_configs(*items*, *dut_label*)  
Populate the settings values from multiple ExperimentConfigurations into a dict.

The resulting dict maps the contents of each of the configs to [`ExperimentConfiguration.id`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration.id "iqm.cpc.core.config.ExperimentConfiguration.id") of that configuration. The contents for a particular configuration are observation paths mapped to the corresponding values.

Parameters:  
- **items** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*ExperimentConfiguration*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration")*,* *...\],* [*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None\]\]*) – list of `(tuple[ExperimentConfiguration, ...], storage)` to populate settings values from. NOTE: The storage is not used in this function, but is included to match the signature of the other cache loading functions.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label NOTE: not used in this function, but is included to match the signature of the other cache loading functions.

Returns:  
The dict containing the populated observation values.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]
