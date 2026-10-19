> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleCache.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b24565b66eb6208c93fe2cd1e8302b48758b4bffae63fa24984ad544bdde3500.

# RuleCache

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.RuleCache(*load_function_mapping*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Stores cached observation values for the CacheableLoadingRule subclasses.

Parameters:  
**load_function_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *LoadFunction\]*) – Maps the load rule names to the functions used to load the cached observations. Note that each rule should have its own function/database query as they are (generally) not applicable for other rules.

data  
maps rule name to the loaded data for that rule

load_function_mapping  
maps the rule names to the associated load functions.

Methods

|  |  |
|----|----|
| [`load_cache`](#iqm.cpc.core.observation.observation_loading_rules.RuleCache.load_cache "iqm.cpc.core.observation.observation_loading_rules.RuleCache.load_cache") | Loops through the mapped load functions and applies them to load the cache. |

load_cache(*rule_name_to_attributes*)  
Loops through the mapped load functions and applies them to load the cache.

If the rule has attributes, those are passed to the load function.

Parameters:  
**rule_name_to_attributes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]*) – the rule names mapped to the attributes of that rule.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.RuleCache](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-955d6253612d4ae2bba7b6f0adb6e37dcfb3ef40.png)
