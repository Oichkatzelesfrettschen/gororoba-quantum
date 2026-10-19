> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateMetric.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateMetric.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0f30722e0444c16c006a5c93445e3939c34a77d34881b945efce3a9d907b2b2f.

# QONGateMetric

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONGateMetric(*\**, *locus_str*, *method*, *metric*, *suffixes=\<factory\>*, *gate*, *implementation*)  
Bases: [`QONMetric`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html#iqm.station_control.client.qon.QONMetric "iqm.station_control.client.qon.QONMetric")

QON representing a gate quality metric.

Has the form `metrics.{method}.{method_specific_part}`.

Can parse/represent e.g. the following metrics:

`metrics.ssro.measure.constant.QB1.fidelity:par=d1:aaa=bbb`

::  
method: ssro gate: measure implementation: constant locus_str: QB1 metric: fidelity suffixes: {“aaa”: “bbb”, “par”: “d1”}

`metrics.ssro.measure.constant.QB1.fidelity`

> method: ssro gate: measure implementation: constant locus_str: QB1 metric: fidelity suffixes: {}

`metrics.rb.prx.drag_crf.QB4.fidelity:par=d2`

> method: rb gate: prx implementation: drag_crf locus_str: QB4 metric: fidelity suffixes: {“par”: “d2”}

`metrics.irb.circuit.random_circuit.QB4.fidelity:par=d2`

> method: irb gate: circuit implementation: random_circuit locus_str: QB4 metric: fidelity suffixes: {“par”: “d2”}

Attributes

|  |  |
|----|----|
| [`gate`](#iqm.station_control.client.qon.QONGateMetric.gate "iqm.station_control.client.qon.QONGateMetric.gate") | Name of the gate/quantum operation. |
| [`implementation`](#iqm.station_control.client.qon.QONGateMetric.implementation "iqm.station_control.client.qon.QONGateMetric.implementation") | Name of the gate implementation. |
| `method` | Name of the method by which the metric was measured. |
| `metric` | Measured metric. |
| `locus_str` | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
- **locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **method** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **metric** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z_0-9\]\[A-Za-z0-9\_\]\*\$')\])\]*)

- **suffixes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **gate** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **implementation** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

gate*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate/quantum operation.

implementation*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate implementation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONGateMetric](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-2081b0151090245369cd947539483a9520c13fc2.png)
