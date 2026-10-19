> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONSystemMetric.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONSystemMetric.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c5c2e0b1a8b1d4ca12053c80cf1a81ee06f67bf70b08ee78d5de11c3acd56492.

# QONSystemMetric

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONSystemMetric(*\**, *locus_str*, *method*, *metric*, *suffixes=\<factory\>*)  
Bases: [`QONMetric`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html#iqm.station_control.client.qon.QONMetric "iqm.station_control.client.qon.QONMetric")

QON representing a system quality metric.

Has the form `metrics.{method}.{locus_str}.{metric}`.

Can parse/represent e.g. the following metrics:

`metrics.ghz_state.QB1__QB2.coherence_lower_bound`

> method: ghz_state locus_str: QB1\_\_QB2 metric: coherence_lower_bound

`metrics.surface_code_memory.QB3__QB4__QB9.logical_error_rate:d=3:n=20:state=0`

> method: surface_code_memory locus_str: QB3\_\_QB4\_\_QB9 metric: logical_error_rate suffixes: {“d”: “3”, “n”: “20”, “state”: “0”}

Subclasses implement parsing and string representation for specific methods.

Attributes

|  |  |
|----|----|
| `method` | Name of the method by which the metric was measured. |
| `metric` | Measured metric. |
| `locus_str` | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
- **locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **method** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **metric** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z_0-9\]\[A-Za-z0-9\_\]\*\$')\])\]*)

- **suffixes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONSystemMetric](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-9aa00fc2cdc126ed7e0d8c6f4348cd623a9d11cb.png)
