> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a352464e534b9a82c55f1161b497ffe60b016b95952322c0fbb94c6a9d9bbad3.

# GetDefaultCalibrationSet

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet(*\*\*kwargs*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Get the observations for the default calibration set.

The default calibration set results from a calibration run and contains all observations needed for successful circuit execution.

Attributes

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet.resolve_from_cache") | Applies the rule for preloaded cache. |

resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **cache_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)")*\]\]*)

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*)

Return type:  
[*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-421a8ffd910a243a111f1f8bd7a13bd0aded1629.png)
