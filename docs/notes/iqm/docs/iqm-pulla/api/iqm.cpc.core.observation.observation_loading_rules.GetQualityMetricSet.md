> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec5478d29de48c3b153e9f4fb2486edf4d6bba8c123f10daa2900f689fbd5916.

# GetQualityMetricSet

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet(*calibration_set_id*, *storage=None*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Get the observations of a specific calibration set’s latest quality metric set.

Maps directly to `StorageInterface.get_calibration_set_quality_metric_set()`.

Parameters:  
- **calibration_set_id** (*StrUUIDOrDefault*) – ID of the calibration set whose latest quality metric set to get.

- **storage** (*StorageInterface* *\|* *None*)

Attributes

|  |  |
|----|----|
| [`attributes`](#iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.attributes "iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.attributes") | The calibration set id and the storage backend the rule loads the observations from. |
| [`calibration_set_id`](#iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.calibration_set_id "iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.calibration_set_id") | The calibration set id the loading rule was initialized with. |
| [`full_name`](#iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.full_name "iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.full_name") | Returns the full name including the attributes. |

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.resolve_from_cache") | Applies the rule for preloaded cache. |

*property* full_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Returns the full name including the attributes.

*property* attributes*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\], [StorageInterface](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*  
The calibration set id and the storage backend the rule loads the observations from.

*property* calibration_set_id*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\]*  
The calibration set id the loading rule was initialized with.

resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **cache_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\],* *dict\[str,* *~iqm.station_control.interface.models.observation.ObservationData\]\]\]*)

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*)

Return type:  
[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-581d26b84fef48061c7829c1d678fbd007400d85.png)
