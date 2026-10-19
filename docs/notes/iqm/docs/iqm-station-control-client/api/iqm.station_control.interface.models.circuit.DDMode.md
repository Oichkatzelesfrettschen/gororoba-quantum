> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDMode.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDMode.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ee91e9a8af351167ca33e951100f05b446dda1cd778b23fb8c1b8b65340f0d7e.

# DDMode

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* DDMode(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Dynamical Decoupling (DD) mode for circuit execution.

Attributes

|  |  |
|----|----|
| [`DISABLED`](#iqm.station_control.interface.models.circuit.DDMode.DISABLED "iqm.station_control.interface.models.circuit.DDMode.DISABLED") | Do not apply dynamical decoupling. |
| [`ENABLED`](#iqm.station_control.interface.models.circuit.DDMode.ENABLED "iqm.station_control.interface.models.circuit.DDMode.ENABLED") | Apply dynamical decoupling. |

Methods

DISABLED *= 'disabled'*  
Do not apply dynamical decoupling.

ENABLED *= 'enabled'*  
Apply dynamical decoupling.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.DDMode](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a01b3856d8b62542ff53c98d5d6c7a77ce77c255.png)
