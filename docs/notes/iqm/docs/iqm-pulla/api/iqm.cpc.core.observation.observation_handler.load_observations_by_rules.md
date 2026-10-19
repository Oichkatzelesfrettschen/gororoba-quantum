> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.load_observations_by_rules.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.load_observations_by_rules.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d0ba66468a3dcd880dc9ac10f8ebb7b1d9da8891b546b1c135ab44235520766b.

# iqm.cpc.core.observation.observation_handler.load_observations_by_rules

iqm.cpc.core.observation.observation_handler.load_observations_by_rules(*load_rules*, *dut_label*, *default_storage*)  
Load observations resolved by the given rules, keyed by whichever dut fields they resolve to.

Unlike populating an [`ObservationHandler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.ObservationHandler.html#iqm.cpc.core.observation.observation_handler.ObservationHandler "iqm.cpc.core.observation.observation_handler.ObservationHandler") with every known dut field, this only touches the dut fields that the given `load_rules` themselves surface from the DB, so it works without any prior knowledge of which dut fields exist for the DUT. As a consequence, a rule that isn’t a [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule") (e.g. [`Fail`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.Fail.html#iqm.cpc.core.observation.observation_loading_rules.Fail "iqm.cpc.core.observation.observation_loading_rules.Fail"), [`LatestFromStash`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.LatestFromStash.html#iqm.cpc.core.observation.observation_loading_rules.LatestFromStash "iqm.cpc.core.observation.observation_loading_rules.LatestFromStash")) never contributes any dut field to resolve against, since there’s no cached query result to discover them from. If `load_rules` contains no `CacheableLoadRule` at all, a warning is logged and no observations are returned.

Parameters:  
- **load_rules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*RuleType*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")*\]*) – Loading rules to resolve, tried in order per dut field.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT to resolve the rule for.

- **default_storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)")) – Default storage to use for loading observations in case the rules do not pin a storage backend.

Returns:  
Mapping from resolved dut field paths to their observations.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ObservationBase*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html#iqm.station_control.interface.models.observation.ObservationBase "(in iqm-station-control-client v14.0.0)")\]
