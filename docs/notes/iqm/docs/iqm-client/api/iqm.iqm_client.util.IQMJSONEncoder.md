> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.IQMJSONEncoder.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.IQMJSONEncoder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2761723022f88e3e0b4eda4959198ff1f7c01ab1573fdad15af90741586fe3e9.

# IQMJSONEncoder

Module: [`iqm.iqm_client.util`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.util.html#module-iqm.iqm_client.util "iqm.iqm_client.util")

*class* iqm.iqm_client.util.IQMJSONEncoder(*\**, *skipkeys=False*, *ensure_ascii=True*, *check_circular=True*, *allow_nan=True*, *sort_keys=False*, *indent=None*, *separators=None*, *default=None*)  
Bases: [`JSONEncoder`](https://docs.python.org/3.11/library/json.html#json.JSONEncoder "(in Python v3.11)")

JSONEncoder that that adds support for some non-JSON datatypes.

Attributes

Methods

|  |  |
|----|----|
| [`default`](#iqm.iqm_client.util.IQMJSONEncoder.default "iqm.iqm_client.util.IQMJSONEncoder.default") | Convert `o` into a serializable object. |

default(*o: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")  
Convert `o` into a serializable object.

Parameters:  
**o** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.iqm_client.util.IQMJSONEncoder](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-537cc93b949e0ac18f197d8075d602d135e835dc.png)
