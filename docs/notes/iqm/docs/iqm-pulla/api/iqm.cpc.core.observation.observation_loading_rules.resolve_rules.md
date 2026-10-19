> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.resolve_rules.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.resolve_rules.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a465cdeafcb2921ddb32525be941b5718db7dde2ca40d2d206e1a413879bea26.

# iqm.cpc.core.observation.observation_loading_rules.resolve_rules

iqm.cpc.core.observation.observation_loading_rules.resolve_rules(*observation_name*, *rules*, *dut_label*, *default_storage*, *rule_cache=None*)  
Resolves the rules related to loading and fall back one by one.

If an observation is loaded successfully from the DB, the rule resolving is terminated. Returns the loaded observation and the rule that ended up producing it.

If global observation loading rules has been set with `set_global_default_observation_loading_rules()`, then those rules will override anything given in `rules`. Global observation rules can be set to an empty list, in that case no rules will be used, i.e. observation will not be loaded at all. If global observations rules are set to None, then those will be ignored and original rules given as a parameter will be used.

Parameters:  
- **observation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – the name of the observation to search for in the database.

- **rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]*) – the list of rules to be resolved in loading the observation.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – the label of the DUT for which this observation will be loaded.

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – the default storage to be used for loading observations if the rule does not have its own storage backend.

- **rule_cache** ([*RuleCache*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html#iqm.cpc.core.observation.observation_loading_rules.RuleCache "iqm.cpc.core.observation.observation_loading_rules.RuleCache") *\|* *None*) – cache of preloaded observations for certain load rules. Loading from the rule cache takes precedence over the normal rule execution.

Returns:  
- The observation that was loaded (None if no rule successfully fetched an observation).

- The name of the rule class that produced the above observation (None if no rule successfully fetched an observation).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – in case a rule could not be applied and a ValueError was thrown.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ObservationBase*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html#iqm.station_control.interface.models.observation.ObservationBase "(in iqm-station-control-client v14.0.0)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[None, None\]
