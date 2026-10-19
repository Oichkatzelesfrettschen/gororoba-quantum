> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatest.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatest.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 defbe4c262ef0edbd3b623b533351f9b1d7442c85cb61a38a4b9ca12687efdbf.

# GetLatest

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.GetLatest(*storage=None*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Get the latest observation.

Attributes

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.GetLatest.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.GetLatest.resolve_from_cache") | Applies the rule for preloaded cache. |

Parameters:  
**storage** (*StorageInterface* *\|* *None*)

resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **cache_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)")*\]\]*)

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*)

Return type:  
[*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.GetLatest](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-4676d7b28cc073908196096a8e0616c2c0f90822.png)
