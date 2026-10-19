> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 358dc61e0aded8425f2a73ed37f4937c3c02abbe93fb159646100026d69b286a.

# GetObservationSet

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.GetObservationSet(*set_id*, *storage=None*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Get the observations for a given observation set.

The observations must belong to the specified set, but may also belong to others.

Raises: ValueError in case there are several observations for the same dut_field, or observations in the set belong  
to more than one DUT. If the set is of type ‘generic-set’ a warning is shown instead and the set is loaded as usual.

Attributes

|  |  |
|----|----|
| [`attributes`](#iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.attributes "iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.attributes") | The observation set id and the storage backend the rule loads the observations from. |
| [`full_name`](#iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.full_name "iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.full_name") | Returns the full name including the attributes. |
| [`set_id`](#iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.set_id "iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.set_id") | The observation set id the loading rule was initialized with. |

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.resolve_from_cache") | Applies the rule for preloaded cache. |

Parameters:  
- **set_id** ([*uuid.UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **storage** (*StorageInterface* *\|* *None*)

*property* full_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Returns the full name including the attributes.

*property* attributes*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"), [StorageInterface](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*  
The observation set id and the storage backend the rule loads the observations from.

*property* set_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
The observation set id the loading rule was initialized with.

resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **cache_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)")*\]\]*)

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*)

Return type:  
[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.GetObservationSet](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-621200b395d76f79cdc290576dc8429f1601d86d.png)
