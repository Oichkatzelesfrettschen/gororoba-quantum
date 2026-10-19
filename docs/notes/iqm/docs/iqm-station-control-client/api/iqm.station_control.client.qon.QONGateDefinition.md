> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0ed4cdef235fcfbaf29e3cab17973bab5c38cced60351161a417dd3bd6989b0e.

# QONGateDefinition

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONGateDefinition(*gate*, *implementation*, *quantity*)  
Bases: [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

QON representing a part of a quantum operation definition.

Quantum operation properties have the form `gate_definitions.{gate}.*`.

Implementation properties have the form `gate_definitions.{gate}.{implementation}.*`.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONGateDefinition.domain "iqm.station_control.client.qon.QONGateDefinition.domain") | Type/purpose of the observation. |
| [`gate`](#iqm.station_control.client.qon.QONGateDefinition.gate "iqm.station_control.client.qon.QONGateDefinition.gate") | Name of the gate/quantum operation. |
| [`implementation`](#iqm.station_control.client.qon.QONGateDefinition.implementation "iqm.station_control.client.qon.QONGateDefinition.implementation") | Name of the gate implementation, or None if not an implementation property. |
| [`quantity`](#iqm.station_control.client.qon.QONGateDefinition.quantity "iqm.station_control.client.qon.QONGateDefinition.quantity") | Name of the quantity described by the observation. |

Methods

Parameters:  
- **gate** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*)

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **quantity** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

gate*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z0-9\_\]+\$')\])\]*  
Name of the gate/quantum operation.

implementation*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Name of the gate implementation, or None if not an implementation property.

quantity*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the quantity described by the observation.

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONGateDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-21df3c8b9720e11fdfec8c894bb33aea6101def5.png)
