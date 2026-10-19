> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.Serializable.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.Serializable.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7abbb6ba47bb92c0a53e0b0dfc807d1afe199e0a13b5202d51fbb6b2aa6e9ac7.

# Serializable

Module: [`iqm.station_control.interface.serializable`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.serializable.html#module-iqm.station_control.interface.serializable "iqm.station_control.interface.serializable")

*class* Serializable  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

A mixin class adding uniform dictionary serialization capabilities to subclasses.

Methods

|  |  |
|----|----|
| [`deserialize`](#iqm.station_control.interface.serializable.Serializable.deserialize "iqm.station_control.interface.serializable.Serializable.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`serialize`](#iqm.station_control.interface.serializable.Serializable.serialize "iqm.station_control.interface.serializable.Serializable.serialize") | Serialize the object instance into a dictionary payload. |

*abstractmethod* serialize()  
Serialize the object instance into a dictionary payload.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*abstractmethod classmethod* deserialize(*data*)  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
*T*

Inheritance

![Inheritance diagram of iqm.station_control.interface.serializable.Serializable](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-dd344e49acc07144dee41e4a6a483ba9710a47bf.png)
