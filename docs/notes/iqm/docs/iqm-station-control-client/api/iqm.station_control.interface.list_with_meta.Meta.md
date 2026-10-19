> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.Meta.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.Meta.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ebf1151fbc4968857c899ddf8401d9c186df08906b7319e186ac5270ae8ad250.

# Meta

Module: [`iqm.station_control.interface.list_with_meta`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.html#module-iqm.station_control.interface.list_with_meta "iqm.station_control.interface.list_with_meta")

*class* Meta(*\**, *count=None*, *order_by=None*, *limit=None*, *offset=None*, *errors=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Class holding metadata for list return values, including pagination and query statistics.

Attributes

|  |  |
|----|----|
| [`count`](#iqm.station_control.interface.list_with_meta.Meta.count "iqm.station_control.interface.list_with_meta.Meta.count") | Total number of items existing in the storage that match the query criteria. |
| [`errors`](#iqm.station_control.interface.list_with_meta.Meta.errors "iqm.station_control.interface.list_with_meta.Meta.errors") | List of error messages encountered during the execution of the query. |
| [`limit`](#iqm.station_control.interface.list_with_meta.Meta.limit "iqm.station_control.interface.list_with_meta.Meta.limit") | Maximum number of items returned in this query response (page size). |
| [`offset`](#iqm.station_control.interface.list_with_meta.Meta.offset "iqm.station_control.interface.list_with_meta.Meta.offset") | Number of items to skip from the beginning of the result sequence. |
| [`order_by`](#iqm.station_control.interface.list_with_meta.Meta.order_by "iqm.station_control.interface.list_with_meta.Meta.order_by") | Ordering rule applied to the queried items (e.g., "-created_timestamp" for descending). |

Methods

Parameters:  
- **count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **order_by** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **limit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **offset** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **errors** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

count*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Total number of items existing in the storage that match the query criteria.

order_by*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Ordering rule applied to the queried items (e.g., “-created_timestamp” for descending).

limit*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Maximum number of items returned in this query response (page size).

If set to 0 or a negative integer, pagination is disabled and the query attempts to return all available records (matching `count - offset`). Note: Disabling the limit may result in extremely heavy database and network load.

offset*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Number of items to skip from the beginning of the result sequence.

This value can be incremented in successive queries to loop through pages until `count` is reached.

errors*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
List of error messages encountered during the execution of the query.

Inheritance

![Inheritance diagram of iqm.station_control.interface.list_with_meta.Meta](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a62db104236a2429e9557d922b163e0f05211668.png)
