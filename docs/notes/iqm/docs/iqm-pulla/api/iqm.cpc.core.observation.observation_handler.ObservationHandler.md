> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.ObservationHandler.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.ObservationHandler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ba21789b46a06d8a4145aa163e0a3a2058566d27044e2ed584c35a6f2745d6e9.

# ObservationHandler

Module: [`iqm.cpc.core.observation.observation_handler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.html#module-iqm.cpc.core.observation.observation_handler "iqm.cpc.core.observation.observation_handler")

*class* iqm.cpc.core.observation.observation_handler.ObservationHandler(*observation_parameters*, *dut_label*, *default_storage*, *load_rules=None*, *rule_cache=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Base class for loading observations from the DB or another source.

The load_rules of for a given set of observations can be set and the observations loaded accordingly.

Parameters:  
- **observation_parameters** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – list of observation names or parameters.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The label of the DUT for which this ObservationHandler is associated with.

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The default storage to be used for loading observations when the load rules do not specify a storage.

- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]* *\|* *None*) – The loading rules to be set for the above `observation_parameters`.

- **rule_cache** ([*RuleCache*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html#iqm.cpc.core.observation.observation_loading_rules.RuleCache "iqm.cpc.core.observation.observation_loading_rules.RuleCache") *\|* *None*) – optional user inputted custom rule cache.

load_rules  
The load rules for each observation.

loaded_observations  
The loaded observation and the load rule that produced it mapped to the observation `dut_field`.

Methods

|  |  |
|----|----|
| [`add_observations`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.add_observations "iqm.cpc.core.observation.observation_handler.ObservationHandler.add_observations") | Adds observations, load rules for them and optionally loads them. |
| [`change_load_rules`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.change_load_rules "iqm.cpc.core.observation.observation_handler.ObservationHandler.change_load_rules") | Change all the non-empty load rules into the provided rules. |
| [`get_rule_names_and_attributes`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.get_rule_names_and_attributes "iqm.cpc.core.observation.observation_handler.ObservationHandler.get_rule_names_and_attributes") | Returns the rule names mapped to all their attributes (e.g. the tags) for caching of cacheable load rules. |
| [`get_value`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.get_value "iqm.cpc.core.observation.observation_handler.ObservationHandler.get_value") | Get the loaded observation value for a given observation path. |
| [`load_observations`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.load_observations "iqm.cpc.core.observation.observation_handler.ObservationHandler.load_observations") | Load the observations for the given components based on their loading rules. |
| [`populate_from`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.populate_from "iqm.cpc.core.observation.observation_handler.ObservationHandler.populate_from") | Set up the handler's loading from a settings tree. |
| [`print_observations`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.print_observations "iqm.cpc.core.observation.observation_handler.ObservationHandler.print_observations") | Prints the observations and the load rule that produces them. |
| [`set_load_rules`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.set_load_rules "iqm.cpc.core.observation.observation_handler.ObservationHandler.set_load_rules") | Set given load rule to specific observations. |
| [`value_dict`](#iqm.cpc.core.observation.observation_handler.ObservationHandler.value_dict "iqm.cpc.core.observation.observation_handler.ObservationHandler.value_dict") | Return loaded observation values mapped to the respective dut_fields. |

set_load_rules(*load_rules*, *matches=None*, *starts_with=None*, *includes=None*)  
Set given load rule to specific observations.

Parameters:  
- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]*) – the rules to be set.

- **matches** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply function to only the observations whose names that match one of the strings exactly. Does not support regex.

- **starts_with** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names start with one of these strings. Supports regex.

- **includes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names contain one of the given strings. Supports regex.

Return type:  
None

change_load_rules(*load_rules*)  
Change all the non-empty load rules into the provided rules.

Parameters:  
**load_rules** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]*) – the rules to be applied.

Return type:  
None

load_observations(*matches=None*, *starts_with=None*, *includes=None*, *load_rule_cache=True*)  
Load the observations for the given components based on their loading rules.

In case a list of component names is not provided, load observations for all components. Allows preloading the observation into the rule cache for certain load rules in order improve the performance.

Parameters:  
- **matches** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply function to only the observations whose names match one of these strings exactly. Does not support regex.

- **starts_with** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names start with one of these strings. Supports regex.

- **includes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names contain one of the given strings. Supports regex.

- **load_rule_cache** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, preload observations into the cache.

Return type:  
None

print_observations(*matches=None*, *starts_with=None*, *includes=None*)  
Prints the observations and the load rule that produces them.

Parameters:  
- **matches** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply function to only the observations whose names that match one of these strings exactly. Does not support regex.

- **starts_with** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names start with one of these strings. Supports regex.

- **includes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names contain one of the given strings. Supports regex.

Return type:  
None

add_observations(*observation_parameters*, *load_rules=None*, *load=False*)  
Adds observations, load rules for them and optionally loads them.

Parameters:  
- **observation_parameters** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)")*\]*) – The observation dut_fields or Parameters to be added to.

- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]* *\|* *None*) – Sets the given load rules for the aforementioned paths/dut_fields. The global default rules will be used if left `None`.

- **load** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If set `True` will load the newly added observations using the specified `load_rules`. Note: for cached load rules, assumes the cache is loaded before this call and will not reload it.

Return type:  
None

populate_from(*settings*, *load_rules=None*, *override_rules=False*)  
Set up the handler’s loading from a settings tree.

Will add all the settings tree paths to be loaded.

Parameters:  
- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")) – The settings tree from which to read the paths.

- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]* *\|* *None*) – Sets the given load rules for the aforementioned paths/dut_fields. The global default rules will be used if left `None`.

- **override_rules** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, will override any already existing rules with the given `load_rules`.

Return type:  
None

get_value(*name*, *load=False*, *load_rules=None*)  
Get the loaded observation value for a given observation path.

If the specified observation is not yet found in `self`, it can optionally be loaded first and then returned.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Observation path.

- **load** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to try to add & load the observation if no value is found. Note: for cached load rules, assumes the rule cache has been loaded before this call and will not reload it.

- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]* *\|* *None*) – Load rules to add for the observation named `name` in case it was not yet found in `self`. If not given, the global default rules are used. Has no effect if `load == False`.

Returns:  
The observation value or `None` if the observation was not found in `self`.

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")

value_dict(*matches=None*, *starts_with=None*, *includes=None*, *return_full_observation=False*)  
Return loaded observation values mapped to the respective dut_fields.

Parameters:  
- **matches** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply function to only the observations whose names that match one of these strings exactly. Does not support regex.

- **starts_with** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names start with one of these strings. Supports regex.

- **includes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names contain one of the given strings. Supports regex.

- **return_full_observation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Return the full observations in the dict instead of just the observation values.

Returns:  
A dictionary mapping the loaded values to the respective dut_fields. `None` values are skipped  
and not found in the dict.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_rule_names_and_attributes(*matches=None*, *starts_with=None*, *includes=None*)  
Returns the rule names mapped to all their attributes (e.g. the tags) for caching of cacheable load rules.

Parameters:  
- **matches** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply function to only the observations whose names that match one of these strings exactly. Does not support regex.

- **starts_with** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names start with one of these strings. Supports regex.

- **includes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Apply to only the observations whose names contain one of the given strings. Supports regex.

Returns:  
Mapping from CacheableLoadRule subclass names to the rule attributes of all the rules of the same type.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_handler.ObservationHandler](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-5ba1bf3c15542c1e2ae0b7007cdf73ffd47eec55.png)
