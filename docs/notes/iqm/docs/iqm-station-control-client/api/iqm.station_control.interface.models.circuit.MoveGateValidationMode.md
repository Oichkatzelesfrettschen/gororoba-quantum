> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateValidationMode.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateValidationMode.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 01624924cb12c9b74109ec2ac942f85387e2247d834abb4b6d695bf571ee7dd8.

# MoveGateValidationMode

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* MoveGateValidationMode(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

MOVE gate validation mode for circuit compilation. This options is meant for advanced users.

Attributes

|  |  |
|----|----|
| [`STRICT`](#iqm.station_control.interface.models.circuit.MoveGateValidationMode.STRICT "iqm.station_control.interface.models.circuit.MoveGateValidationMode.STRICT") | MOVE(qubit, resonator) gates must only appear in sandwiches (pairs). |
| [`ALLOW_PRX`](#iqm.station_control.interface.models.circuit.MoveGateValidationMode.ALLOW_PRX "iqm.station_control.interface.models.circuit.MoveGateValidationMode.ALLOW_PRX") | Allow PRX gates on the MOVE qubit inside MOVE sandwiches during validation. |
| [`NONE`](#iqm.station_control.interface.models.circuit.MoveGateValidationMode.NONE "iqm.station_control.interface.models.circuit.MoveGateValidationMode.NONE") | Do not perform any MOVE gate validation. |

Methods

STRICT *= 'strict'*  
MOVE(qubit, resonator) gates must only appear in sandwiches (pairs). Inside a sandwich there must be no gates acting on the MOVE qubit, and no other MOVE gates acting on the resonator.

Type:  
Perform standard MOVE gate validation

ALLOW_PRX *= 'allow_prx'*  
Allow PRX gates on the MOVE qubit inside MOVE sandwiches during validation.

NONE *= 'none'*  
Do not perform any MOVE gate validation.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.MoveGateValidationMode](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a81db379e98789db0f241cfcc4de6529b518738f.png)
