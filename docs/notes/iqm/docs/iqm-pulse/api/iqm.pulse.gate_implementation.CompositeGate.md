> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 037f137df0512115f308830a0fe1d82841c4cd1af0e0d8c7bcf4ac97c6d22331.

# CompositeGate

Module: [`iqm.pulse.gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html#module-iqm.pulse.gate_implementation "iqm.pulse.gate_implementation")

*class* iqm.pulse.gate_implementation.CompositeGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Base class for gate implementations that are defined in terms of other gate implementations.

Composite gates can be implemented using other pre-existing gate implementations (called its *member gates*) by using [`build()`](#iqm.pulse.gate_implementation.CompositeGate.build "iqm.pulse.gate_implementation.CompositeGate.build") in the `_call()` method. You *should not* call `ScheduleBuilder.get_implementation()` directly in composite gate code.

A CompositeGate subclass needs to declare what its member gates are, e.g. to be able to verify that they are calibrated, using the [`registered_gates`](#iqm.pulse.gate_implementation.CompositeGate.registered_gates "iqm.pulse.gate_implementation.CompositeGate.registered_gates") class attribute.

It is possibe to calibrate (some of) the member gates separately from the common calibration, by listing their names in [`customizable_gates`](#iqm.pulse.gate_implementation.CompositeGate.customizable_gates "iqm.pulse.gate_implementation.CompositeGate.customizable_gates") class attribute. However, if no custom calibration data is provided, the composite gate will use the common calibration for the member operations.

Hint

Inheriting this class and defining `registered_gates = ("prx", "cz")`, `customizable_gates = ("prx",)` allows one to use `prx` and `cz` gates as member operations, and calibrate `prx` independently of the common calibration.

Note

`CompositeGate.needs_calibration()` only tells whether the implementation class itself needs calibration data, not whether the member gates need some.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gate_implementation.CompositeGate.customizable_gates "iqm.pulse.gate_implementation.CompositeGate.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding [`OCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OCalibrationData.html#iqm.pulse.gate_implementation.OCalibrationData "iqm.pulse.gate_implementation.OCalibrationData") nodes for them under the [`OILCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OILCalibrationData.html#iqm.pulse.gate_implementation.OILCalibrationData "iqm.pulse.gate_implementation.OILCalibrationData") node of the composite gate. |
| [`default_implementations`](#iqm.pulse.gate_implementation.CompositeGate.default_implementations "iqm.pulse.gate_implementation.CompositeGate.default_implementations") | Mapping from member operation names to the designated default implementation of that operation. |
| [`registered_gates`](#iqm.pulse.gate_implementation.CompositeGate.registered_gates "iqm.pulse.gate_implementation.CompositeGate.registered_gates") | Names of the member operations used by the composite gate. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`build`](#iqm.pulse.gate_implementation.CompositeGate.build "iqm.pulse.gate_implementation.CompositeGate.build") | Construct an implementation for a member (registered) gate. |
| [`optional_calibration_keys`](#iqm.pulse.gate_implementation.CompositeGate.optional_calibration_keys "iqm.pulse.gate_implementation.CompositeGate.optional_calibration_keys") | Optional calibration data keys for this class, in addition to the required items in `parameters`. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ()*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
These member operations can be calibrated separately from their common calibration by adding [`OCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OCalibrationData.html#iqm.pulse.gate_implementation.OCalibrationData "iqm.pulse.gate_implementation.OCalibrationData") nodes for them under the [`OILCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OILCalibrationData.html#iqm.pulse.gate_implementation.OILCalibrationData "iqm.pulse.gate_implementation.OILCalibrationData") node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gate_implementation.CompositeGate.registered_gates "iqm.pulse.gate_implementation.CompositeGate.registered_gates"). By default all member operations are customizable.

default_implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= {}*  
Mapping from member operation names to the designated default implementation of that operation. Filling this attribute allows one to define a different default implementation from the common default in `builder.op_table` to be used in the context of this composite gate. If a member operation is not found in this dict as a key, the CompositeGate will use the common default as its default implementation.

*classmethod* optional_calibration_keys()  
Optional calibration data keys for this class, in addition to the required items in `parameters`.

These keys are not required to be present in [`OILCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OILCalibrationData.html#iqm.pulse.gate_implementation.OILCalibrationData "iqm.pulse.gate_implementation.OILCalibrationData") when validating it. E.g. custom calibration keys for [`CompositeGate`](#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate") member gates.

Returns:  
Optional top-level calibration data keys.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]

build(*op_name*, *locus*, *impl_name=None*, *\**, *strict_locus=False*, *priority_calibration=None*)  
Construct an implementation for a member (registered) gate.

A custom calibration for `op_name` will be sought in `calibration_data`. If any calibration parameters are found, they override the corresponding parameters in the common calibration data.

Parameters:  
- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – member operation name

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – locus the operation acts on

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Implementation name. If not given, uses the default implementation defined in the class instance if any, and otherwise the common default in `builder.op_table`.

- **strict_locus** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff False, for non-symmetric implementations of symmetric ops the locus order may be changed if no calibration data is available for the requested locus order

- **priority_calibration** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – If given, overrides the custom calibration for the member gate. Deprecated, should not be used.

Returns:  
Calibrated member gate implementation.

Return type:  
[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation.CompositeGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-860fb19600fca205bfe3de22774301a6a7cc0146.png)
