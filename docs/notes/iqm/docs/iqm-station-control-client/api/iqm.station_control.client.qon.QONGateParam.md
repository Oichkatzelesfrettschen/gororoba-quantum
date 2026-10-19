> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateParam.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateParam.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 16eff328169e66f8bfb9c086079d8f5de1aa2e4a16366ff1d0f6b83d29bceaf7.

# QONGateParam

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONGateParam(*gate*, *implementation*, *parameter*, *\**, *locus_str*)  
Bases: [`LocusQON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html#iqm.station_control.client.qon.LocusQON "iqm.station_control.client.qon.LocusQON")

QON representing a gate parameter observation.

Has the form `gates.{gate}.{implementation}.{locus_str}.{parameter}`.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONGateParam.domain "iqm.station_control.client.qon.QONGateParam.domain") | Type/purpose of the observation. |
| [`gate`](#iqm.station_control.client.qon.QONGateParam.gate "iqm.station_control.client.qon.QONGateParam.gate") | Name of the gate/quantum operation. |
| [`implementation`](#iqm.station_control.client.qon.QONGateParam.implementation "iqm.station_control.client.qon.QONGateParam.implementation") | Name of the gate implementation. |
| [`parameter`](#iqm.station_control.client.qon.QONGateParam.parameter "iqm.station_control.client.qon.QONGateParam.parameter") | Name of the gate parameter. |
| `locus_str` | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
- **gate** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **implementation** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **parameter** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

gate*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate/quantum operation.

implementation*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate implementation.

parameter*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the gate parameter. May have further dotted structure.

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONGateParam](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-32250d420db4d44f39c4142ff92b80cd2a003371.png)
