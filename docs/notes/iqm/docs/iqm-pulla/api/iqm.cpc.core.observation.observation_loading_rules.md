> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6552206b210d4b985f46dd43e5abbb8d0f91acfe460e6e6e4ca140a769543083.

# observation_loading_rules

Full path: iqm.cpc.core.observation.observation_loading_rules

Loading rule interfaces and base classes.

Module Attributes

|  |  |
|----|----|
| [`RuleCacheDataType`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCacheDataType.html#iqm.cpc.core.observation.observation_loading_rules.RuleCacheDataType "iqm.cpc.core.observation.observation_loading_rules.RuleCacheDataType") | Represents cached data for a single CacheableLoadRule subclass. |
| [`LoadFunction`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.LoadFunction.html#iqm.cpc.core.observation.observation_loading_rules.LoadFunction "iqm.cpc.core.observation.observation_loading_rules.LoadFunction") | Function for loading [`RuleCache`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html#iqm.cpc.core.observation.observation_loading_rules.RuleCache "iqm.cpc.core.observation.observation_loading_rules.RuleCache") data for a single subclass of CacheableLoadRule. |
| [`DEFAULTS_FROM_YML_SOURCE`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.DEFAULTS_FROM_YML_SOURCE.html#iqm.cpc.core.observation.observation_loading_rules.DEFAULTS_FROM_YML_SOURCE "iqm.cpc.core.observation.observation_loading_rules.DEFAULTS_FROM_YML_SOURCE") | Source for settings that get their values from the EXA configuration YML. |

Functions

|  |  |
|----|----|
| [`resolve_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.resolve_rules.html#iqm.cpc.core.observation.observation_loading_rules.resolve_rules "iqm.cpc.core.observation.observation_loading_rules.resolve_rules")(observation_name, rules, ...) | Resolves the rules related to loading and fall back one by one. |

Classes

|  |  |
|----|----|
| [`CacheableLoadRule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule.html#iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule "iqm.cpc.core.observation.observation_loading_rules.CacheableLoadRule") | Interface for an observation loading rule for which the observation data can be preloaded to a cache. |
| [`Fail`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.Fail.html#iqm.cpc.core.observation.observation_loading_rules.Fail "iqm.cpc.core.observation.observation_loading_rules.Fail") | Terminates rule application chain on error. |
| [`FromExperimentConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration.html#iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration "iqm.cpc.core.observation.observation_loading_rules.FromExperimentConfiguration") | Load observations from [`ExperimentConfiguration`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentConfiguration.html#iqm.cpc.core.config.ExperimentConfiguration "iqm.cpc.core.config.ExperimentConfiguration"). |
| [`GetCalibrationSet`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet.html#iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet "iqm.cpc.core.observation.observation_loading_rules.GetCalibrationSet") | Get the observations of a specific calibration set, or the current default one. |
| [`GetDefaultCalibrationSet`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet.html#iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet "iqm.cpc.core.observation.observation_loading_rules.GetDefaultCalibrationSet") | Get the observations for the default calibration set. |
| [`GetLatest`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatest.html#iqm.cpc.core.observation.observation_loading_rules.GetLatest "iqm.cpc.core.observation.observation_loading_rules.GetLatest") | Get the latest observation. |
| [`GetLatestCharacterizationSet`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatestCharacterizationSet.html#iqm.cpc.core.observation.observation_loading_rules.GetLatestCharacterizationSet "iqm.cpc.core.observation.observation_loading_rules.GetLatestCharacterizationSet") | Get the observations for the latest finalized characterization set. |
| [`GetLatestForTags`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags.html#iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags "iqm.cpc.core.observation.observation_loading_rules.GetLatestForTags") | Get the latest observation for a given list of tags. |
| [`GetObservationSet`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetObservationSet.html#iqm.cpc.core.observation.observation_loading_rules.GetObservationSet "iqm.cpc.core.observation.observation_loading_rules.GetObservationSet") | Get the observations for a given observation set. |
| [`GetQualityMetricSet`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet.html#iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet "iqm.cpc.core.observation.observation_loading_rules.GetQualityMetricSet") | Get the observations of a specific calibration set's latest quality metric set. |
| [`LatestFromStash`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.LatestFromStash.html#iqm.cpc.core.observation.observation_loading_rules.LatestFromStash "iqm.cpc.core.observation.observation_loading_rules.LatestFromStash") | Load rule that gets the observation from the local stash. |
| [`RuleCache`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html#iqm.cpc.core.observation.observation_loading_rules.RuleCache "iqm.cpc.core.observation.observation_loading_rules.RuleCache") | Stores cached observation values for the CacheableLoadingRule subclasses. |
| [`RuleType`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType") | Base class for observation loading rules. |

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-b7b8592c28f82eb6c1f74604c5dd0674b8445161.png)
