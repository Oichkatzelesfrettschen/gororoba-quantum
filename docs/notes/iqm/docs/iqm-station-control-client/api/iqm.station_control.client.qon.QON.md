> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3e44dc97e13ba69f9d148c0a254009dc3569633fcc043b40df0f0744e7880b91.

# QON

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QON  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

ABC for qualified observation names.

Used for representing, creating and parsing observation names that conform to the current convention. When the convention changes, the first thing you should do is to update the classes in this module.

Note

This class provides a somewhat reliable way to encode more than one data item in `ObservationBase.dut_field`, aka “observation name”. Eventually a more viable solution could be to give each of these items their own fields in the observation structure.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QON.domain "iqm.station_control.client.qon.QON.domain") | Type/purpose of the observation. |

Methods

|  |  |
|----|----|
| [`from_str`](#iqm.station_control.client.qon.QON.from_str "iqm.station_control.client.qon.QON.from_str") | Parse an observation name into a QON object. |

&nbsp;

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

&nbsp;

*classmethod* from_str(*name*)  
Parse an observation name into a QON object.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Observation name (aka dut_field) to parse.

Returns:  
Corresponding qualified observation name object.

Raises:  
- **ValidationError** – Failed to parse `name` because it was syntactically incorrect.

- **UnknownObservationError** – Failed to parse `name` because it contains unknown elements.

Return type:  
[*QON*](#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QON](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-9c26fbff33a118282f2c3a0cab2242399e7fb53d.png)
