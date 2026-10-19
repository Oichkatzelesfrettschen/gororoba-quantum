> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.HeraldingMode.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.HeraldingMode.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 523efa09c4f46bda5db556592a1106347a3b20170661e481cbd27346d7174b64.

# HeraldingMode

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* HeraldingMode(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Heralding mode for circuit execution.

Heralding is the practice of generating data about the state of qubits prior to execution of a circuit. This can be achieved by measuring the qubits immediately before executing each shot for a circuit.

Attributes

|  |  |
|----|----|
| [`NONE`](#iqm.station_control.interface.models.circuit.HeraldingMode.NONE "iqm.station_control.interface.models.circuit.HeraldingMode.NONE") | Do not do any heralding. |
| [`ZEROS`](#iqm.station_control.interface.models.circuit.HeraldingMode.ZEROS "iqm.station_control.interface.models.circuit.HeraldingMode.ZEROS") | For each circuit, perform a heralding measurement after the initial reset on all the QPU components used in the circuit that have the "measure" operation available in the calset. |

Methods

NONE *= 'none'*  
Do not do any heralding.

ZEROS *= 'zeros'*  
For each circuit, perform a heralding measurement after the initial reset on all the QPU components used in the circuit that have the “measure” operation available in the calset. Only retain shots where all the components are measured to be in the zero state.

Note: in this mode, the number of shots returned after execution will be \<= the requested amount due to the post-selection based on heralding data. If zero shots would be returned, the job will have the FAILED status.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.HeraldingMode](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-c9eba429b970f9133564bf845f1cfd83a027bfdb.png)
