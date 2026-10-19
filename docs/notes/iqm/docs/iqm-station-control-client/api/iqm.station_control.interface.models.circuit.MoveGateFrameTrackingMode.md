> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 835aa8f59a6256b3d5efdf670af780c4f0ca669c9a8f926b06ae9b5ddb75a3bc.

# MoveGateFrameTrackingMode

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* MoveGateFrameTrackingMode(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

MOVE gate reference frame tracking mode for circuit compilation. This option is meant for advanced users.

Attributes

|  |  |
|----|----|
| [`FULL`](#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.FULL "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.FULL") | Apply both explicit z rotations on the resonator, and a dynamic phase correction due to qubit-resonator detuning, to the qubit at the end of a MOVE sandwich. |
| [`NO_DETUNING_CORRECTION`](#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.NO_DETUNING_CORRECTION "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.NO_DETUNING_CORRECTION") | Only apply explicit z rotations on the resonator to the qubit at the end of the sandwich. |
| [`NONE`](#iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.NONE "iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode.NONE") | Do not perform any MOVE gate frame tracking. |

Methods

FULL *= 'full'*  
Apply both explicit z rotations on the resonator, and a dynamic phase correction due to qubit-resonator detuning, to the qubit at the end of a MOVE sandwich.

NO_DETUNING_CORRECTION *= 'no_detuning_correction'*  
Only apply explicit z rotations on the resonator to the qubit at the end of the sandwich. Do not apply a detuning correction, the user is expected to do this manually.

NONE *= 'none'*  
Do not perform any MOVE gate frame tracking. The user is expected to do this manually.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.MoveGateFrameTrackingMode](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-2c7e4339ab6b194f2b86025a20eebb43ebd94ff9.png)
