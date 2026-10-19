> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bf87daa096e3df656564ed11afc70f7dfdf0ffb3538f91504196352242340807.

# iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache

iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache(*tags*, *storage*, *dut_label*)  
Load the cache for the [`GetLatestForTags`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags.html#iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags "iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags") load rule.

The latest observation is returned per each DUT and `dut_field` and a set of tags such that the `tags` given as the function argument is a subset of it.

NOTE: This function is mainly used under the hood in [`ObservationHandler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.ObservationHandler.html#iqm.cpc.core.observation.observation_handler.ObservationHandler "iqm.cpc.core.observation.observation_handler.ObservationHandler"), and may behave unintuitively (e.g. return several observations per `dut_field`).

Parameters:  
- **tags** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – List of tags to query for. Only the observations that have at least one tag in this list are returned.

- **storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The storage backend to query.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the device being used.

Returns:  
Dict of the latest observations mapped to their `dut_field`.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)")\]\]
