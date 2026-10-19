> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0acc8002a637897b5a0f39503bf5f60c4ced4549f86e8684022ea3b7d92b0396.

# FromExperimentConfiguration

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration(*config*, *storage=None*)  
Bases: [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule")

Load observations from [`ExperimentConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration").

The settings tree root nodes (“controllers”, “gates”, “characterization”, “stages”) are given as attrs in the [`ExperimentConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration"). These are dicts that reflect the settings tree path structure. For each `dut_field`, this rule picks the corresponding root attribute and traverses the dict to find the value. Global default values for a component/locus are used if they exist and no specific value for that component/locus does. If no applicable value or global default value is found a `None` is returned.

The global default dict key is “common” for the “controllers” node, and an empty tuple for the other nodes.

Attributes

|  |  |
|----|----|
| [`attributes`](#iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.attributes "iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.attributes") | The experiment configuration the rule loads the observations from (no storage backend). |

Methods

|  |  |
|----|----|
| [`resolve_from_cache`](#iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.resolve_from_cache "iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.resolve_from_cache") | Applies the rule for preloaded cache. |

Parameters:  
- **config** ([*ExperimentConfiguration*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration"))

- **storage** (*StorageInterface* *\|* *None*)

*property* attributes*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ExperimentConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration"), [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*  
The experiment configuration the rule loads the observations from (no storage backend).

resolve_from_cache(*observation_name*, *cache_data*, *default_storage*)  
Applies the rule for preloaded cache.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **cache_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]*)

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*)

Return type:  
[*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "(in iqm-station-control-client v14.0.0)") \| None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-9c709ff6361df5698ede3943211632ec13ec9a7f.png)
