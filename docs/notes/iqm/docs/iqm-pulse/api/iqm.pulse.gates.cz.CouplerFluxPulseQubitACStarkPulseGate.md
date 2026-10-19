> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 90264ab8c8f5881cd1a4980947aca0b2f26e82b43cad64b3b51d4507e547d568.

# CouplerFluxPulseQubitACStarkPulseGate

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Base class for CZ gates with coupler flux pulse and a qubit AC Stark pulse.

Analogous to the fast qubit flux pulse, the AC Stark pulse can tune the frequency of the qubit. Together with the coupler flux pulse, this can implement a fast qubit pulsed CZ gate.

Attributes

|  |  |
|----|----|
| [`excluded_parameters`](#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.excluded_parameters "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.excluded_parameters") | Parameters names to be excluded from `self.parameters`. |
| `root_parameters` |  |
| [`coupler_wave`](#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.coupler_wave "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.coupler_wave") | Flux pulse Waveform to be played in the coupler flux AWG. |
| [`qubit_drive_wave`](#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.qubit_drive_wave "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.qubit_drive_wave") | Qubit drive pulse waveform to be played in the qubit drive AWG. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.duration_in_seconds "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Flux pulse Waveform to be played in the coupler flux AWG.

qubit_drive_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Qubit drive pulse waveform to be played in the qubit drive AWG.

excluded_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= \[\]*  
Parameters names to be excluded from `self.parameters`. Inheriting classes may override this if certain parameters are not wanted in that class (also parameters defined by the waveforms can be excluded).

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-cf4551f3db6720ced2181cc908e94cc81608ce6b.png)
