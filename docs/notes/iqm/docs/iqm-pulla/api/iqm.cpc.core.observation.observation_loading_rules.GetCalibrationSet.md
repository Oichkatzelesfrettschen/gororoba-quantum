> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a4efee8e5127e76c7534ac14253ddab5cc6df1905682eed96e823e69f0c852af.

# GetCalibrationSet

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet(*calibration_set_id*, *storage=None*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Get the observations of a specific calibration set, or the current default one.

Maps directly to `StorageInterface.get_calibration_set()`.

Parameters:  
- **calibration_set_id** (*StrUUIDOrDefault*) – ID of the calibration set to get.

- **storage** (*StorageInterface* *\|* *None*) – The storage backend the rule loads the observations from. If `None`, the default storage will be used.

Attributes

|  |  |
|----|----|
| [`attributes`](#iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.attributes "iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.attributes") | The calibration set id and the storage backend the rule loads the observations from. |
| [`calibration_set_id`](#iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.calibration_set_id "iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.calibration_set_id") | The calibration set id the loading rule was initialized with. |
| [`full_name`](#iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.full_name "iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.full_name") | Returns the full name including the attributes. |

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.resolve_from_cache") | Applies the rule for preloaded cache. |

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

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-9aba0f09f205c90373d4407fc9e2bd0370cde2ec.png)
