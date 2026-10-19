> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVEGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVEGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 27097e31506529481a6e0458da04b1a424a491375d95d0d39a1d3dbd06201d43.

# CouplerMOVEGate

Module: [`iqm.pulse.gates.coupler_move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.html#module-iqm.pulse.gates.coupler_move "iqm.pulse.gates.coupler_move")

*class* iqm.pulse.gates.coupler_move.CouplerMOVEGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Two component coupler_move gate implemented using flux pulse and the interaction mediated by the coupler.

Implements a population exchange with single qubit phases on the invariant subspace. The two components should be a qubit and a coupler. Consists of a flux pulse on the coupler, and possibly another flux pulse on the qubit.

Attributes

|  |  |
|----|----|
| `excluded_parameters` |  |
| `root_parameters` |  |
| [`coupler_wave`](#iqm.pulse.gates.coupler_move.CouplerMOVEGate.coupler_wave "iqm.pulse.gates.coupler_move.CouplerMOVEGate.coupler_wave") | Coupler flux pulse Waveform |
| [`qubit_wave`](#iqm.pulse.gates.coupler_move.CouplerMOVEGate.qubit_wave "iqm.pulse.gates.coupler_move.CouplerMOVEGate.qubit_wave") | Coupler flux pulse Waveform |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.coupler_move.CouplerMOVEGate.duration_in_seconds "iqm.pulse.gates.coupler_move.CouplerMOVEGate.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Coupler flux pulse Waveform

qubit_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Coupler flux pulse Waveform

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.coupler_move.CouplerMOVEGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-90510922b0fd63bccb84000df72a31e2a0fe9a46.png)
