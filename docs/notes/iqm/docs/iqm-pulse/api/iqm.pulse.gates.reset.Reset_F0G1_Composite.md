> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1_Composite.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1_Composite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c35710dd3a26ea505ec31b1c7eac61fc94eaf508a78ec0bb1eecb5973fa8795e.

# Reset_F0G1_Composite

Module: [`iqm.pulse.gates.reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "iqm.pulse.gates.reset")

*class* iqm.pulse.gates.reset.Reset_F0G1_Composite(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

Reset by applying a `prx_12(pi)` gate followed by the `lru.f0g1` operation.

The `prx_12(pi)` swaps the populations of the states \\\|1\rangle\\ and \\\|2\rangle\\, and the `lru.f0g1` moves the \\\|2\rangle\\ state population to \\\|0\rangle\\.

The parameter `number_of_cycles` specifies how many times the sequence of gates (prx_12, lru) will be repeated.

Note that the F0G1 pulse here is take from the LRU gate, since this is a composite gate.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.customizable_gates "iqm.pulse.gates.reset.Reset_F0G1_Composite.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`default_implementations`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.default_implementations "iqm.pulse.gates.reset.Reset_F0G1_Composite.default_implementations") | Mapping from member operation names to the designated default implementation of that operation. |
| [`parameters`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.parameters "iqm.pulse.gates.reset.Reset_F0G1_Composite.parameters") | Required calibration data, may be nested |
| [`registered_gates`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.registered_gates "iqm.pulse.gates.reset.Reset_F0G1_Composite.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.locus_mapping_function "iqm.pulse.gates.reset.Reset_F0G1_Composite.locus_mapping_function") | One-qubit loci with physical drive and readout. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('lru',)*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

default_implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= {'lru': 'f0g1'}*  
Mapping from member operation names to the designated default implementation of that operation. Filling this attribute allows one to define a different default implementation from the common default in `builder.op_table` to be used in the context of this composite gate. If a member operation is not found in this dict as a key, the CompositeGate will use the common default as its default implementation.

parameters*: NestedParams* *= {'number_of_cycles': Setting(parameter=Parameter(name='', label='Number of cycles of the \[prx_12(pi), lru\] sequence', unit='', data_type=\<DataType.INT: 5\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=1, read_only=False, path='')}*  
Required calibration data, may be nested

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('lru',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.reset.Reset_F0G1_Composite.registered_gates "iqm.pulse.gates.reset.Reset_F0G1_Composite.registered_gates"). By default all member operations are customizable.

locus_mapping_function()  
One-qubit loci with physical drive and readout.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.reset.Reset_F0G1_Composite](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-73fa45401d4b55e4491f23dd35ecfd2bb4fa6a39.png)
