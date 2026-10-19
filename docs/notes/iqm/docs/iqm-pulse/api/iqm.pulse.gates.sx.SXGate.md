> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.SXGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.SXGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 59d50147dd91f86c225517698e9e4bb7de6c43418ff22e19c57dd646de07a4dd.

# SXGate

Module: [`iqm.pulse.gates.sx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.html#module-iqm.pulse.gates.sx "iqm.pulse.gates.sx")

*class* iqm.pulse.gates.sx.SXGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

SX gate implementation based on PRX gate, by limiting the angle to pi / 2.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.sx.SXGate.customizable_gates "iqm.pulse.gates.sx.SXGate.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`registered_gates`](#iqm.pulse.gates.sx.SXGate.registered_gates "iqm.pulse.gates.sx.SXGate.registered_gates") | Names of the member operations used by the composite gate. |
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

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('prx',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.sx.SXGate.registered_gates "iqm.pulse.gates.sx.SXGate.registered_gates"). By default all member operations are customizable.

Inheritance

![Inheritance diagram of iqm.pulse.gates.sx.SXGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-3dd8d9987be20f2591930cd653f23a76194fece7.png)
