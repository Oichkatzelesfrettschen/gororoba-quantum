> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Conditional.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Conditional.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 522a41ffc66ea01489bc93c2c86c60686146cd5bea651a51fcc6ab1a75fdaa06.

# Reset_Conditional

Module: [`iqm.pulse.gates.reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "iqm.pulse.gates.reset")

*class* iqm.pulse.gates.reset.Reset_Conditional(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

Conditional reset operation.

Uses a measurement followed by a conditional PRX gate with angle \\\pi\\. It is assumed the measurement projects the state into the computational basis.

The conditional PRX implementation handles any necessary waits to accommodate for the feedback result propagation delay.

This reset implementation is factorizable. It can act upon any set of locus components, and the measurement used in the conditional reset will be multiplexed to those components. However, only locus components that have readout and drive can be reset via conditional reset. Otherwise, locus components will just have their channels blocked.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.reset.Reset_Conditional.customizable_gates "iqm.pulse.gates.reset.Reset_Conditional.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`registered_gates`](#iqm.pulse.gates.reset.Reset_Conditional.registered_gates "iqm.pulse.gates.reset.Reset_Conditional.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.reset.Reset_Conditional.locus_mapping_function "iqm.pulse.gates.reset.Reset_Conditional.locus_mapping_function") | One-qubit loci with physical drive and readout. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('measure', 'cc_prx')*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

locus_mapping_function()  
One-qubit loci with physical drive and readout.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('measure', 'cc_prx')*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.reset.Reset_Conditional.registered_gates "iqm.pulse.gates.reset.Reset_Conditional.registered_gates"). By default all member operations are customizable.

Inheritance

![Inheritance diagram of iqm.pulse.gates.reset.Reset_Conditional](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-340b29281008ae78de6621f392e537b1af935eb8.png)
