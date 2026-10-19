> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 11e04b1b54fb8c840b0f4895fce2331aa4fed15f49b1f508c834a71cdebbdd04.

# observation_load_utils

Full path: iqm.cpc.core.observation.observation_load_utils

Utilities for loading observations from `StorageInterface`.

Contains the storage queries used by the observation loading rules, as well as the cache loading functions that [`RuleCache`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html#iqm.cpc.core.observation.observation_loading_rules.RuleCache "iqm.cpc.core.observation.observation_loading_rules.RuleCache") maps the cacheable loading rules to.

All functions here are self-contained: they take the `StorageInterface` instance they operate on as an argument and have no dependency on any ambient runtime.

Functions

|  |  |
|----|----|
| [`get_all_latest_observations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_all_latest_observations.html#iqm.cpc.core.observation.observation_load_utils.get_all_latest_observations "iqm.cpc.core.observation.observation_load_utils.get_all_latest_observations")(storage, dut_label) | Get the latest observation corresponding to each `dut_field`. |
| [`get_default_calset_observations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations.html#iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations "iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations")(storage) | Loads all observations related to the default calibration set. |
| [`get_latest_observation`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation.html#iqm.cpc.core.observation.observation_load_utils.get_latest_observation "iqm.cpc.core.observation.observation_load_utils.get_latest_observation")(dut_field, \*, ...\[, ...\]) | Get the latest valid observation for the given DUT, based on the created timestamp. |
| [`get_latest_observation_set_data`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data.html#iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data "iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data")(set_type\[, ...\]) | Find the latest finalized observation set of given type. |
| [`get_latest_observation_set_observations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations.html#iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations "iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations")(set_type) | Loads all observations related to the latest finalized observation set of given type. |
| [`get_observation_set_observations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations.html#iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations "iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations")(set_ids, ...) | Loads all observations related to a given observation set, one set at a time. |
| [`get_observation_set_type`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_observation_set_type.html#iqm.cpc.core.observation.observation_load_utils.get_observation_set_type "iqm.cpc.core.observation.observation_load_utils.get_observation_set_type")(set_id, storage) | Get the type of an observation set. |
| [`load_get_latest_for_tags_cache`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache.html#iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache "iqm.cpc.core.observation.observation_load_utils.load_get_latest_for_tags_cache")(tags, ...) | Load the cache for the [`GetLatestForTags`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags.html#iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags "iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags") load rule. |
| [`populate_from_configs`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.populate_from_configs.html#iqm.cpc.core.observation.observation_load_utils.populate_from_configs "iqm.cpc.core.observation.observation_load_utils.populate_from_configs")(items, dut_label) | Populate the settings values from multiple ExperimentConfigurations into a dict. |
