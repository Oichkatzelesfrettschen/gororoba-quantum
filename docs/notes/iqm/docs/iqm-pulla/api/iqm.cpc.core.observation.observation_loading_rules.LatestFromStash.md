> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.LatestFromStash.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.LatestFromStash.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b96246066f2168587537d0d73fdb5da85169c5c8a43b0e9706d385448baea62e.

# LatestFromStash

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.LatestFromStash(*stash*, *tags=None*)  
Bases: [`RuleType`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html#iqm.cpc.core.observation.observation_loading_rules.RuleType "iqm.cpc.core.observation.observation_loading_rules.RuleType")

Load rule that gets the observation from the local stash.

Attributes

Methods

Parameters:  
- **stash** (*\_ObservationStash*)

- **tags** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.LatestFromStash](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-72ca49925ae9fe8ecf1e65553931287feaec69ce.png)
