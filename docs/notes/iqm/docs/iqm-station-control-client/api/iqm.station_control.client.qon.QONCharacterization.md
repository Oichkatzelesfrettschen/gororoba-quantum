> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONCharacterization.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONCharacterization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 43ed7639144b69f2f97e239e4daa561d91d53014e44b5fa6e9012a756eb3660e.

# QONCharacterization

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONCharacterization(*component*, *quantity*, *suffixes=\<factory\>*)  
Bases: [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

QON representing a QPU property.

Has the form `characterization.model.{component}.{property}`

Can parse e.g.

characterization.model.QB5.t2_time

> component: QB5 quantity: t2_time

characterization.model.QB1.init_error:herald=measure_fidelity.constant:measure=measure.constant

> component: QB1 quantity: init_error suffixes: {“herald”: “measure_fidelity.constant”, “measure”: “measure.constant”}

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONCharacterization.domain "iqm.station_control.client.qon.QONCharacterization.domain") | Type/purpose of the observation. |
| [`suffix_str`](#iqm.station_control.client.qon.QONCharacterization.suffix_str "iqm.station_control.client.qon.QONCharacterization.suffix_str") | Return the all the suffixes encoded into a dut_field fragment. |
| [`suffixes`](#iqm.station_control.client.qon.QONCharacterization.suffixes "iqm.station_control.client.qon.QONCharacterization.suffixes") | Suffixes defining the quantity further (if any). |
| [`component`](#iqm.station_control.client.qon.QONCharacterization.component "iqm.station_control.client.qon.QONCharacterization.component") | Names of QPU component(s) that the observation describes. |
| [`quantity`](#iqm.station_control.client.qon.QONCharacterization.quantity "iqm.station_control.client.qon.QONCharacterization.quantity") | Name of the quantity described by the observation. |

Methods

Parameters:  
- **component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **quantity** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **suffixes** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

component*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Names of QPU component(s) that the observation describes.

quantity*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the quantity described by the observation.

suffixes*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= FieldInfo(annotation=NoneType, required=False, default_factory=dict)*  
Suffixes defining the quantity further (if any).

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

*property* suffix_str*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Return the all the suffixes encoded into a dut_field fragment.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONCharacterization](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-dcc928c0c5d5ca2079edf68875390cda09b5dbe7.png)
