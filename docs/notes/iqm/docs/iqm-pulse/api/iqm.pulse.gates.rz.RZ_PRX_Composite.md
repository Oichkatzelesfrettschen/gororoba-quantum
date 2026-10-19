> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_PRX_Composite.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_PRX_Composite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c69bc45b5ab1e66bcf9f66f490b7a48852ad4b56db8ea419833042938761140a.

# RZ_PRX_Composite

Module: [`iqm.pulse.gates.rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html#module-iqm.pulse.gates.rz "iqm.pulse.gates.rz")

*class* iqm.pulse.gates.rz.RZ_PRX_Composite(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

RZ gate implemented as a sequence of PRX gates.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.rz.RZ_PRX_Composite.customizable_gates "iqm.pulse.gates.rz.RZ_PRX_Composite.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`registered_gates`](#iqm.pulse.gates.rz.RZ_PRX_Composite.registered_gates "iqm.pulse.gates.rz.RZ_PRX_Composite.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.rz.RZ_PRX_Composite.locus_mapping_function "iqm.pulse.gates.rz.RZ_PRX_Composite.locus_mapping_function") | One-component loci with drive. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('prx',)*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

locus_mapping_function()  
One-component loci with drive.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('prx',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.rz.RZ_PRX_Composite.registered_gates "iqm.pulse.gates.rz.RZ_PRX_Composite.registered_gates"). By default all member operations are customizable.

Inheritance

![Inheritance diagram of iqm.pulse.gates.rz.RZ_PRX_Composite](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-621789aff176ec5192605cb132c1f8cf961e45d3.png)
