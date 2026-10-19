> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONControllerSetting.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONControllerSetting.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 de9651c87040825d8dc578928ff4aac99b04c92b84f604109fd2f9898d9e7bfd.

# QONControllerSetting

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONControllerSetting(*component*, *controller_path*, *setting*)  
Bases: [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

QON representing a controller setting observation.

Has the form `controllers.{component}.{controller_path}.{setting}`.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONControllerSetting.domain "iqm.station_control.client.qon.QONControllerSetting.domain") | Type/purpose of the observation. |
| [`component`](#iqm.station_control.client.qon.QONControllerSetting.component "iqm.station_control.client.qon.QONControllerSetting.component") | Name of QPU component that the controller controls. |
| [`controller_path`](#iqm.station_control.client.qon.QONControllerSetting.controller_path "iqm.station_control.client.qon.QONControllerSetting.controller_path") | Names of the controllers and subcontrollers. |
| [`setting`](#iqm.station_control.client.qon.QONControllerSetting.setting "iqm.station_control.client.qon.QONControllerSetting.setting") | Name of the controller setting. |

Methods

Parameters:  
- **component** ([*Annotated*](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *FieldInfo(annotation=NoneType,* *required=True,* *metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z\_\]\[A-Za-z0-9\_-\]\*\$')\])\]*)

- **controller_path** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

- **setting** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

component*: [Annotated](https://docs.python.org/3.11/library/typing.html#typing.Annotated "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), FieldInfo(annotation=NoneType, required=True, metadata=\[\_PydanticGeneralMetadata(pattern='^\[A-Za-z\_\]\[A-Za-z0-9\_-\]\*\$')\])\]*  
Name of QPU component that the controller controls.

controller_path*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Names of the controllers and subcontrollers.

NOTE: The first controller path element is not the same as in Station Control, where it includes [`component`](#iqm.station_control.client.qon.QONControllerSetting.component "iqm.station_control.client.qon.QONControllerSetting.component").

setting*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the controller setting.

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONControllerSetting](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-4f0a08db34972d4ce0e5d7f0cc57b8bdaa962730.png)
