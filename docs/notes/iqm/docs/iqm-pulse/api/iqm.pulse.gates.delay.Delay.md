> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.Delay.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.Delay.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e1802d6978257b16b166f080c7e7a04cdd2b6f2ffc6d73dcb150e0db5c94232f.

# Delay

Module: [`iqm.pulse.gates.delay`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.html#module-iqm.pulse.gates.delay "iqm.pulse.gates.delay")

*class* iqm.pulse.gates.delay.Delay(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Applies a delay on the control channels of its locus components.

This operation applies [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions on all the control channels of all its locus components. The duration of all the Waits is the same, and it is given as a parameter for the operation, rounded up to the nearest possible duration the hardware can handle.

Note

We can only guarantee that the delay is *at least* of the requested duration. Also, when Delay is used in a quantum circuit, the delay between the preceding and following operations is again *at least* the requested duration, but could be much more depending on the other operations in the circuit. To see why, consider e.g. the circuit `[CZ(a, b), Delay(1, a), Delay(10, b), CZ(a, b)]` where a and b are qubits. In this case the actual delay between the two CZ gates will be 10 time units rounded up to hardware granularity.

Attributes

|  |  |
|----|----|
| [`symmetric`](#iqm.pulse.gates.delay.Delay.symmetric "iqm.pulse.gates.delay.Delay.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.delay.Delay](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ef5b3eb442e7d868e8f4b39548ff812e5d96a7f6.png)
