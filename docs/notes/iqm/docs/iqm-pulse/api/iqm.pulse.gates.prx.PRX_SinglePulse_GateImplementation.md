> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f9b2f3968e94358d61e9957d2ab9b0112878c98e1bad8883272d59495d2a3155.

# PRX_SinglePulse_GateImplementation

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`SinglePulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html#iqm.pulse.gate_implementation.SinglePulseGate "iqm.pulse.gate_implementation.SinglePulseGate"), [`PrxGateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html#iqm.pulse.gates.prx.PrxGateImplementation "iqm.pulse.gates.prx.PrxGateImplementation")

Base class for PRX gates implemented using a single IQ pulse.

This class implements phased x rotation gates on a specific qubit using an [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") instance, derived from the pulse calibration data provided at construction by the static method `_single_iq_pulse()`. The pulse is used to resonantly drive the qubit to effect the required rotation.

The pulse calibration data consists of the parameters of an \\x\_\pi\\ [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") only. It is assumed that

- the transfer function from the AWG to the qubit is linear, i.e., other rotation angles can be obtained by linearly scaling the pulse amplitude, and

- other phase angles can be obtained by adjusting the IQ modulation phase.

The generated pulses all have the same time duration, also for identity rotations. In the special case of the duration being zero, the gate implementation will apply a `Block(0)` instruction to the qubit’s drive channel.

Attributes

|  |  |
|----|----|
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e7f8a01440ca6e1df2af471d5304cdc8ebd167e7.png)
