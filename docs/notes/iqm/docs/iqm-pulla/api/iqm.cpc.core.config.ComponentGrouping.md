> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 058574064b8656b3ca8884620bafb972f62caf6b34ae892a1fac07b7e6361f5a.

# ComponentGrouping

Module: [`iqm.cpc.core.config`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html#module-iqm.cpc.core.config "iqm.cpc.core.config")

*class* iqm.cpc.core.config.ComponentGrouping(*components*, *validate=True*)  
Bases: [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")

Utility class for handling the `run` argument `components`.

ComponentGrouping is a list of one of the following types:

1.  `str` (QPU component names)

2.  `tuple[str, ...]` (component groups)

3.  `list[tuple[str, ...]]` (group of parallelizable units, each such group can be executed in parallel).

All the normal list operations and comprehensions work with ComponentGrouping. In addition, the class provides utility methods such as flattening the structure and checking whether components or groups are found within it. The attribute `grouping_mode` can be accessed to find out what kind of contents (one of the three above) the list contains.

Methods

|  |  |
|----|----|
| [`contains`](#iqm.cpc.core.config.ComponentGrouping.contains "iqm.cpc.core.config.ComponentGrouping.contains") | Checks if a component, a component group or a colour group is contained. |
| [`copy`](#iqm.cpc.core.config.ComponentGrouping.copy "iqm.cpc.core.config.ComponentGrouping.copy") | Copies the contents into a new instance. |
| [`flatten`](#iqm.cpc.core.config.ComponentGrouping.flatten "iqm.cpc.core.config.ComponentGrouping.flatten") | Flattens the contents into a list of unique strings. |
| [`limit_by_components`](#iqm.cpc.core.config.ComponentGrouping.limit_by_components "iqm.cpc.core.config.ComponentGrouping.limit_by_components") | Limits the component groups by a list of component names or component groups while preserving the order. |
| [`to_json_serializable`](#iqm.cpc.core.config.ComponentGrouping.to_json_serializable "iqm.cpc.core.config.ComponentGrouping.to_json_serializable") | Returns the contents as a JSON serializable format, using lists instead of tuples. |
| [`to_list`](#iqm.cpc.core.config.ComponentGrouping.to_list "iqm.cpc.core.config.ComponentGrouping.to_list") | Returns the contents as a normal list. |

Parameters:  
- **components** (*Components* *\|* *None*)

- **validate** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

to_list()  
Returns the contents as a normal list.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]\]

to_json_serializable()  
Returns the contents as a JSON serializable format, using lists instead of tuples.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]\]

copy()  
Copies the contents into a new instance.

Return type:  
[*ComponentGrouping*](#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping")

flatten()  
Flattens the contents into a list of unique strings.

Any duplicate entries are removed such that only the first occurrence is kept. Otherwise the order is preserved.

Returns:  
Unique component names as a flat list.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

contains(*elem*)  
Checks if a component, a component group or a colour group is contained.

The behaviour depends on the `` grouping_mode` `` and on the type of the searched element.

1\. If `self.grouping_mode == ComponentGroupingMode.LIST`: - Search for a string returns True if the string is contained within. - Search for a group returns True if all the elements of the group are contained within. - Search for a colour group returns True if all the groups in it are contained within (similarly as above).

2\. If `self.grouping_mode == ComponentGroupingMode.GROUP`: - Search for a string returns True if the string is contained within any of the groups. - Search for a group returns True if the group is contained within. - Search for a colour group returns True if all the groups in it are contained within.

3\. If `self.grouping_mode == ComponentGroupingMode.COLOUR_GROUP`: - Search for a string returns True if the string is contained within any of the groups in the colour groups. - Search for a group returns True if the group is contained within any of the colour groups. - Search for a colour group returns True if the colour group is contained within.

Returns:  
Whether the element was found or not.

Parameters:  
**elem** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]*)

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

limit_by_components(*component_list*)  
Limits the component groups by a list of component names or component groups while preserving the order.

If `self.grouping_mode == ComponentGroupingMode.LIST`, and limiting by flat lists, will return a new `ComponentGrouping` such that all components not belonging to the given `component_list` are removed. Lists cannot be limited by groups, an error is thrown instead.

If `self.grouping_mode == ComponentGroupingMode.GROUP` or `self.grouping_mode == ComponentGroupingMode.COLOUR_GROUP`, and limiting with flat lists, will return a new `ComponentGrouping` such that all groups that are not subsets of the `component_list` are removed. If limiting by groups, will return only the groups that belong to the limiting groups. Completely emptied colour groups will be removed.

Returns:  
The limited component grouping.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – When trying to limit flat lists with groups.

Parameters:  
**component_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]* *\|* *None*)

Return type:  
[*ComponentGrouping*](#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping")

Inheritance

![Inheritance diagram of iqm.cpc.core.config.ComponentGrouping](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-3d7b90a872d9628c99190495fc764e7cedeb9c86.png)
