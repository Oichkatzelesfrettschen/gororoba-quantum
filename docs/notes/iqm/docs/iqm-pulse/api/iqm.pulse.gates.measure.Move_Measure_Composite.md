> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Move_Measure_Composite.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Move_Measure_Composite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 89f5617b47a31ddd78555211247babc93e962b0c530fbb817ac36c73b7931432.

# Move_Measure_Composite

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.Move_Measure_Composite(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate"), [`Measure_Factorizable`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Factorizable.html#iqm.pulse.gates.measure.Measure_Factorizable "iqm.pulse.gates.measure.Measure_Factorizable")

Measure implementation intended for measuring components that have no probe line.

If a component has no attached probe line, it can be measured by moving its state to a connected component that does have a probe line. This requires that the `move` gate is defined between the (non-probeable) locus component and the move qubit that has a probe line. The move qubit’s name is provided as a calibration data parameter to this implementation.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.measure.Move_Measure_Composite.customizable_gates "iqm.pulse.gates.measure.Move_Measure_Composite.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`parameters`](#iqm.pulse.gates.measure.Move_Measure_Composite.parameters "iqm.pulse.gates.measure.Move_Measure_Composite.parameters") | Required calibration data, may be nested |
| [`registered_gates`](#iqm.pulse.gates.measure.Move_Measure_Composite.registered_gates "iqm.pulse.gates.measure.Move_Measure_Composite.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.measure.Move_Measure_Composite.locus_mapping_function "iqm.pulse.gates.measure.Move_Measure_Composite.locus_mapping_function") | Defined for components that have no probe line and that are qubits or resonators. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'acquisition_type': Setting(parameter=Parameter(name='', label='Acquisition type', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value='threshold', read_only=False, path=''), 'integration_threshold': Parameter(name='', label='Integration threshold', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'measure_qubit': Parameter(name='measure_qubit', label='Qubit used for the probe pulse', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('measure', 'measure_fidelity')*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ()*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.measure.Move_Measure_Composite.registered_gates "iqm.pulse.gates.measure.Move_Measure_Composite.registered_gates"). By default all member operations are customizable.

locus_mapping_function()  
Defined for components that have no probe line and that are qubits or resonators.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.Move_Measure_Composite](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-9cdefa4cfe625bffc85d153c2ba14c542df9eb9e.png)
