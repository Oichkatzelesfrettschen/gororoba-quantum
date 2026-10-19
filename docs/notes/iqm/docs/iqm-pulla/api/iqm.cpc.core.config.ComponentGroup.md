> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGroup.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGroup.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 41d330ac51a222b21f5e69ffa85dc1482a33a955914487748ddc573267676823.

# ComponentGroup

Module: [`iqm.cpc.core.config`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html#module-iqm.cpc.core.config "iqm.cpc.core.config")

*class* iqm.cpc.core.config.ComponentGroup(*member_names*, *controllers*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Collection of chip components, and the executor Controllers meant to control them.

Attributes

|  |  |
|----|----|
| [`member_names`](#iqm.cpc.core.config.ComponentGroup.member_names "iqm.cpc.core.config.ComponentGroup.member_names") | Names of the components that belong to this group. |
| [`controllers`](#iqm.cpc.core.config.ComponentGroup.controllers "iqm.cpc.core.config.ComponentGroup.controllers") | Mapping from control operation to the name of the controller. |

Methods

|  |  |
|----|----|
| [`from_dict`](#iqm.cpc.core.config.ComponentGroup.from_dict "iqm.cpc.core.config.ComponentGroup.from_dict") | Construct an instance from a dictionary. |

Parameters:  
- **member_names** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **controllers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

member_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the components that belong to this group.

controllers*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Mapping from control operation to the name of the controller.

*static* from_dict(*config*)  
Construct an instance from a dictionary.

Parameters:  
**config** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*ComponentGroup*](#iqm.cpc.core.config.ComponentGroup "iqm.cpc.core.config.ComponentGroup")

Inheritance

![Inheritance diagram of iqm.cpc.core.config.ComponentGroup](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-95e7a7970bc6635c2a681f1be67e4f0388bd8bec.png)
