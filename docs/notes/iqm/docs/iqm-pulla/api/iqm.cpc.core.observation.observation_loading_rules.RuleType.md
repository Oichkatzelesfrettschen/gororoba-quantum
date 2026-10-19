> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.RuleType.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cb70d8e877829eba19344ab1d44edf35a986f078531b46442b62cb260bc12de4.

# RuleType

Module: [`iqm.cpc.core.observation.observation_loading_rules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_loading_rules.html#module-iqm.cpc.core.observation.observation_loading_rules "iqm.cpc.core.observation.observation_loading_rules")

*class* iqm.cpc.core.observation.observation_loading_rules.RuleType(*storage=None*)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

Base class for observation loading rules.

Parameters:  
**storage** (*StorageInterface* *\|* *None*) – The storage backend the rule loads observations from. Rules that don’t connect to a storage backend can leave this as `None` (default).

Attributes

|  |  |
|----|----|
| [`attributes`](#iqm.cpc.core.observation.observation_loading_rules.RuleType.attributes "iqm.cpc.core.observation.observation_loading_rules.RuleType.attributes") | Returns the attributes, including the storage backend. |

Methods

*property* attributes*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), ...\]*  
Returns the attributes, including the storage backend.

The storage backend is always the last attribute.

Inheritance

![Inheritance diagram of iqm.cpc.core.observation.observation_loading_rules.RuleType](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-50ec013b49b70f7573cf02368bf4657a8d03835e.png)
