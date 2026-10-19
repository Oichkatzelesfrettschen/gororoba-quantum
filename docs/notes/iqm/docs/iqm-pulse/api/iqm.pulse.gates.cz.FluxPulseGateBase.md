> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGateBase.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGateBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 880cbddd85a92cca1fbff1545d1614fd64b13d6c4fd19432bd1131f76cc3f997.

# FluxPulseGateBase

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.FluxPulseGateBase(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Discrete arity-2 gate implemented using flux pulses, virtual RZs, and the interaction mediated by the coupler.

Does not have any gate args since it is discrete.

The two locus components of the gate must be connected via a tunable coupler.

Consists of a flux pulse for the coupler with one waveform, optional flux pulses for the locus components with another waveform, and virtual RZs on the locus drive channels.

Inherit from this class and assign waveforms to the `coupler_wave` and `qubit_wave` pulse slots to create a specific implementation.

Can be used as a base class for both CZ and MOVE gate implementations.

Note

The coupler and qubit pulses have the same duration (given in the calibration data), and in the special case of the duration being zero, the gate implementation will apply `Block(0)` instructions to all the channels where it would otherwise apply flux pulses or virtual z rotations.

Attributes

|  |  |
|----|----|
| [`excluded_parameters`](#iqm.pulse.gates.cz.FluxPulseGateBase.excluded_parameters "iqm.pulse.gates.cz.FluxPulseGateBase.excluded_parameters") | Parameters names to be excluded from `self.parameters`. |
| [`root_parameters`](#iqm.pulse.gates.cz.FluxPulseGateBase.root_parameters "iqm.pulse.gates.cz.FluxPulseGateBase.root_parameters") | Parameters shared by all `FluxPulseGateBase` classes. |
| [`coupler_wave`](#iqm.pulse.gates.cz.FluxPulseGateBase.coupler_wave "iqm.pulse.gates.cz.FluxPulseGateBase.coupler_wave") | Flux pulse waveform for the coupler flux AWG. |
| [`qubit_wave`](#iqm.pulse.gates.cz.FluxPulseGateBase.qubit_wave "iqm.pulse.gates.cz.FluxPulseGateBase.qubit_wave") | Flux pulse waveform for the locus component flux AWGs. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.cz.FluxPulseGateBase.duration_in_seconds "iqm.pulse.gates.cz.FluxPulseGateBase.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Flux pulse waveform for the coupler flux AWG.

qubit_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Flux pulse waveform for the locus component flux AWGs.

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]* *= {'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Parameters shared by all `FluxPulseGateBase` classes. Inheriting classes may override this if there’s a need for additional calibration parameters.

excluded_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= \[\]*  
Parameters names to be excluded from `self.parameters`. Inheriting classes may override this if certain parameters are not wanted in that class (also parameters defined by the waveforms can be excluded).

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.FluxPulseGateBase](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-454544abda8797f20fd56870883af73a4a93ae54.png)
