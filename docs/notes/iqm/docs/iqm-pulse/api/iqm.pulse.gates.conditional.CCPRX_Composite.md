> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bc1999e66e86854b7fc46ba2863c09a7a64765827e223d78eae73fec5813ffc5.

# CCPRX_Composite

Module: [`iqm.pulse.gates.conditional`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.html#module-iqm.pulse.gates.conditional "iqm.pulse.gates.conditional")

*class* iqm.pulse.gates.conditional.CCPRX_Composite(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

Classically controlled PRX gate.

Applies a PRX gate conditioned on a discriminated readout result obtained in the same segment (active feedback). Applies a PRX gate if the result is 1, and a Wait of equal duration if the result is 0. Uses the default implementation of PRX underneath, so no extra calibration is needed.

Note

Assumes that the PRX gate implementation used only consists of IQPulse instructions on the drive channel of its locus qubit.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.conditional.CCPRX_Composite.customizable_gates "iqm.pulse.gates.conditional.CCPRX_Composite.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`parameters`](#iqm.pulse.gates.conditional.CCPRX_Composite.parameters "iqm.pulse.gates.conditional.CCPRX_Composite.parameters") | `control_delays` contains the times it takes for the classical control signal from each probe line (readout instrument) to become usable for the drive AWG implementing the PRX gate. |
| [`registered_gates`](#iqm.pulse.gates.conditional.CCPRX_Composite.registered_gates "iqm.pulse.gates.conditional.CCPRX_Composite.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('prx',)*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

parameters*: NestedParams* *= {'control_delays': Parameter(name='', label='Control delays', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}*  
`control_delays` contains the times it takes for the classical control signal from each probe line (readout instrument) to become usable for the drive AWG implementing the PRX gate. The delays must be in the same order as the probe lines are listed in the `{drive_controller}.awg.feedback_sources` station setting.

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('prx',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.conditional.CCPRX_Composite.registered_gates "iqm.pulse.gates.conditional.CCPRX_Composite.registered_gates"). By default all member operations are customizable.

Inheritance

![Inheritance diagram of iqm.pulse.gates.conditional.CCPRX_Composite](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e976b499538fa97b86a7fef2a52da5a51e82a9fe.png)
