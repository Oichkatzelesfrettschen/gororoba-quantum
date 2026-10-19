> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 64c2150381b1157b3001d465c934ec9aee17665f0e3c6d1a04b886f6c5b976b5.

# CacheableLoadRule

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule(*storage=None*)  
Bases: [`RuleType`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")

Interface for an observation loading rule for which the observation data can be preloaded to a cache.

Note that generally load rules do not need to implement this interface — it is enough that they subclass [`RuleType`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType").

Attributes

|  |  |
|----|----|
| [`full_name`](#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.full_name "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.full_name") | Returns the full name including the attributes. |

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.resolve_from_cache") | Applies the rule for preloaded cache. |

Parameters:  
**storage** (*StorageInterface* *\|* *None*)

*property* full_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Returns the full name including the attributes.

*abstractmethod* resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The `dut_field` of the observation to be loaded.

- **cache_data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The cache data to be used for loading the observation.

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The default storage backend to use if the rule does not have its own storage backend.

Returns:  
The loaded observation, or `None` if the rule could not load the observation.

Return type:  
[*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-cefe3534798afa030da6269b2e13cbc31f92fc1d.png)
