> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1c0c5613ca10125f97f1eee9654bcd409635ac7e27d85ba01182b4dd80e8f966.

# MOVE_CustomWaveforms

Module: [`iqm.pulse.gates.move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html#module-iqm.pulse.gates.move "iqm.pulse.gates.move")

*class* iqm.pulse.gates.move.MOVE_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`FluxPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate.html#iqm.pulse.gates.cz.FluxPulseGate "iqm.pulse.gates.cz.FluxPulseGate")

Qubit-resonator or qubit-qubit MOVE gate using flux pulses both on a qubit and the coupler.

This class implements the extra phase bookkeeping logic required to make the MOVE gates work as intended. Due to the unknown phase in the MOVE gate definition, the MOVEs need to be applied in pairs, i.e. the state is always moved back to the qubit it came from. Between a pair of MOVE gates, you can apply any number of other two-component gates (CZs for example) to entangle the component where the state was moved to with other qubits. This sequence of gates enclosed by two MOVE operations is called a *MOVE sandwich*. At the end of a sandwich we have to apply a local phase correction (z rotation) on the state that was moved back to the qubit.

The `__call__()` method of this class uses the [`MoveMarker`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MoveMarker.html#iqm.pulse.gates.move.MoveMarker "iqm.pulse.gates.move.MoveMarker") annotation instruction to mark the beginning and end of each MOVE sandwich, in order to enable the calculation of the angle of the z rotation to be applied on the moved qubit at the end of the sandwich to counteract the phase accumulation during the sandwich relative to the computational frame of the qubit. The phase accumulation has two sources:

- Phase due to the frequency detuning between the two MOVE components, proportional to the time duration of the MOVE sandwich.

- Phase due to the virtual z rotations applied on the central components as gates are applied between it and another qubit, which need to be summed up. By convention the central component VirtualRZ angle of the MOVE implementation itself is currently always zero (since only the sum of the central component and qubit z rotation angles matters for MOVE), but we also include it in the sum for completeness.

The phases are calculated and applied on the qubits using [`apply_move_gate_phase_corrections()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.apply_move_gate_phase_corrections.html#iqm.pulse.gates.move.apply_move_gate_phase_corrections "iqm.pulse.gates.move.apply_move_gate_phase_corrections").

Attributes

|  |  |
|----|----|
| [`root_parameters`](#iqm.pulse.gates.move.MOVE_CustomWaveforms.root_parameters "iqm.pulse.gates.move.MOVE_CustomWaveforms.root_parameters") | Include the detuning between the two MOVE components in the gate parameters for phase tracking. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]* *= {'detuning': Parameter(name='', label='Detuning of the computational components at parking', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Include the detuning between the two MOVE components in the gate parameters for phase tracking.

Inheritance

![Inheritance diagram of iqm.pulse.gates.move.MOVE_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-0dbcc9826843b325a07806fcbacca15c4da10f60.png)
