> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f3163dd6437d727329300b2b6b3300b3b26cff9abac0c5f04d205f433160e12b.

# PrxGateImplementation

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PrxGateImplementation(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

ABC for different implementations of the PRX gate.

Attributes

|  |  |
|----|----|
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`clifford`](#iqm.pulse.gates.prx.PrxGateImplementation.clifford "iqm.pulse.gates.prx.PrxGateImplementation.clifford") | One-qubit XY Clifford gates. |
| [`locus_mapping_function`](#iqm.pulse.gates.prx.PrxGateImplementation.locus_mapping_function "iqm.pulse.gates.prx.PrxGateImplementation.locus_mapping_function") | One-component loci with drive. |
| [`rx`](#iqm.pulse.gates.prx.PrxGateImplementation.rx "iqm.pulse.gates.prx.PrxGateImplementation.rx") | X rotation gate. |
| [`ry`](#iqm.pulse.gates.prx.PrxGateImplementation.ry "iqm.pulse.gates.prx.PrxGateImplementation.ry") | Y rotation gate. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

locus_mapping_function()  
One-component loci with drive.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

rx(*angle*)  
X rotation gate.

Parameters:  
**angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rotation angle (in radians)

Returns:  
boxed instruction schedule implementing the x rotation gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

ry(*angle*)  
Y rotation gate.

Parameters:  
**angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rotation angle (in radians)

Returns:  
boxed instruction schedule implementing the y rotation gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

clifford(*xy_gate*)  
One-qubit XY Clifford gates.

Parameters:  
**xy_gate** ([*XYGate*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.XYGate.html#iqm.pulse.gates.enums.XYGate "iqm.pulse.gates.enums.XYGate")) – Clifford gate

Returns:  
boxed instruction schedule implementing the requested Clifford gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PrxGateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-eaa8a4a7ee225dfb59922e6021a9c99632a4590e.png)
