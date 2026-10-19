> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateCharacterization.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateCharacterization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e0f96f44c9214461c08c1b54cd1ef50a0eac8ed843daee88540200e7c767c137.

# QONGateCharacterization

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONGateCharacterization(*gate*, *implementation*, *quantity*, *\**, *locus_str*)  
Bases: [`LocusQON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html#iqm.station_control.client.qon.LocusQON "iqm.station_control.client.qon.LocusQON")

QON representing an auxiliary gate property, used e.g. during calibration or preprocessing.

Has the form `characterization.gate_properties.{gate}.{implementation}.{locus_str}.{quantity}`.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONGateCharacterization.domain "iqm.station_control.client.qon.QONGateCharacterization.domain") | Type/purpose of the observation. |
| [`gate`](#iqm.station_control.client.qon.QONGateCharacterization.gate "iqm.station_control.client.qon.QONGateCharacterization.gate") | Name of the gate/quantum operation. |
| [`implementation`](#iqm.station_control.client.qon.QONGateCharacterization.implementation "iqm.station_control.client.qon.QONGateCharacterization.implementation") | Name of the gate implementation. |
| [`quantity`](#iqm.station_control.client.qon.QONGateCharacterization.quantity "iqm.station_control.client.qon.QONGateCharacterization.quantity") | Name of the property. |
| `locus_str` | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
- **gate** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **implementation** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **quantity** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

gate*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate/quantum operation.

implementation*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate implementation.

quantity*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the property. May have further dotted structure.

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONGateCharacterization](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-5e379e4186e610b610e115359cb11322ad2f0cf9.png)
