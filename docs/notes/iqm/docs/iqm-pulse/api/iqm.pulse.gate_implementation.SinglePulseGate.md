> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 72df2a26b8aed487c248a91c241519a5d5c9106c3e213d84da8e297fe889b9f7.

# SinglePulseGate

Module: [`iqm.pulse.gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html#module-iqm.pulse.gate_implementation "iqm.pulse.gate_implementation")

*class* iqm.pulse.gate_implementation.SinglePulseGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Base class for GateImplementations that play a single pulse on a single channel.

The pulse is created in `_get_pulse()` and the channel is specified in `_get_pulse_channel()`. The base class also implements a basic `_call()` method that just inserts the specified pulse into the specified channel, and a method for computing the pulse’s duration. All of these methods can be overridden in subclasses.

Attributes

|  |  |
|----|----|
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gate_implementation.SinglePulseGate.duration_in_seconds "iqm.pulse.gate_implementation.SinglePulseGate.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation.SinglePulseGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-85ac9f55c2930ee9e3940847529958b84c8c4196.png)
