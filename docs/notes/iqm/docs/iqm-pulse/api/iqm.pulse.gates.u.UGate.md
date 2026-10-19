> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.UGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.UGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a41dffcf508f8bbd212196d0b22b0513e4c15657106468bf545ab729e14dcd8.

# UGate

Module: [`iqm.pulse.gates.u`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html#module-iqm.pulse.gates.u "iqm.pulse.gates.u")

*class* iqm.pulse.gates.u.UGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

SU(2) gate implemented using PRX.

Assumes the chosen PRX implementation uses resonant driving, and that the virtual RZ technique can be used.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.u.UGate.customizable_gates "iqm.pulse.gates.u.UGate.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`registered_gates`](#iqm.pulse.gates.u.UGate.registered_gates "iqm.pulse.gates.u.UGate.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`from_unitary`](#iqm.pulse.gates.u.UGate.from_unitary "iqm.pulse.gates.u.UGate.from_unitary") | Make a box directly from a single qubit unitary matrix. |
| [`rx`](#iqm.pulse.gates.u.UGate.rx "iqm.pulse.gates.u.UGate.rx") | X rotation gate. |
| [`ry`](#iqm.pulse.gates.u.UGate.ry "iqm.pulse.gates.u.UGate.ry") | Y rotation gate. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('prx',)*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

rx(*angle*)  
X rotation gate.

Parameters:  
**angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rotation angle (in radians)

Returns:  
boxed instruction schedule implementing the x rotation gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('prx',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.u.UGate.registered_gates "iqm.pulse.gates.u.UGate.registered_gates"). By default all member operations are customizable.

ry(*angle*)  
Y rotation gate.

Parameters:  
**angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rotation angle (in radians)

Returns:  
boxed instruction schedule implementing the y rotation gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

from_unitary(*unitary*)  
Make a box directly from a single qubit unitary matrix.

Parameters:  
**unitary** (*np.ndarray*) – 2x2 unitary matrix

Returns:  
boxed instruction schedule implementing the unitary as a gate

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

Inheritance

![Inheritance diagram of iqm.pulse.gates.u.UGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8f5ebff1da6e9e8792fa0cc0baf0c0a67be20d23.png)
