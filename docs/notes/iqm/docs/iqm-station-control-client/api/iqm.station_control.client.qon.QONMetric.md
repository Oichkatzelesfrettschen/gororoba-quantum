> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f0c96cbed012ca8406e1d560000351c7efa47f2f5346e63122ef892da5d9fb8c.

# QONMetric

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONMetric(*\**, *locus_str*, *method*, *metric*, *suffixes=\<factory\>*)  
Bases: [`LocusQON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html#iqm.station_control.client.qon.LocusQON "iqm.station_control.client.qon.LocusQON")

Base class for QON representing a gate or system quality metric.

Subclasses implement parsing and string representation for specific methods.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONMetric.domain "iqm.station_control.client.qon.QONMetric.domain") | Return the QON domain for metrics. |
| [`suffix_str`](#iqm.station_control.client.qon.QONMetric.suffix_str "iqm.station_control.client.qon.QONMetric.suffix_str") | Return the all the suffixes encoded into a dut_field fragment. |
| [`suffixes`](#iqm.station_control.client.qon.QONMetric.suffixes "iqm.station_control.client.qon.QONMetric.suffixes") | Suffixes defining the metric further (if any). |
| [`method`](#iqm.station_control.client.qon.QONMetric.method "iqm.station_control.client.qon.QONMetric.method") | Name of the method by which the metric was measured. |
| [`metric`](#iqm.station_control.client.qon.QONMetric.metric "iqm.station_control.client.qon.QONMetric.metric") | Measured metric. |
| `locus_str` | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
- **locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **method** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **metric** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z_0-9\]\[A-Za-z0-9\_\]\*\$')\])\]*)

- **suffixes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

method*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the method by which the metric was measured.

metric*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z_0-9\]\[A-Za-z0-9\_\]\*\$')\])\]*  
Measured metric.

suffixes*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= FieldInfo(annotation=NoneType, required=False, default_factory=dict)*  
Suffixes defining the metric further (if any).

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Return the QON domain for metrics.

*property* suffix_str*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Return the all the suffixes encoded into a dut_field fragment.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONMetric](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-b1ed388b7c7428f4087a503c439b6d78b1fad0b8.png)
