> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CustomIQWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CustomIQWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d075c7c9820eacfcdaa3c7c3d3854c315155918ab4e5c8941f81836646210f6f.

# CustomIQWaveforms

Module: [`iqm.pulse.gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html#module-iqm.pulse.gate_implementation "iqm.pulse.gate_implementation")

*class* iqm.pulse.gate_implementation.CustomIQWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Base class for GateImplementations using custom waveform definition with IQPulses.

The class contains logic for automatic gate calibration parameters handling for such gates (see the class attributes for more info). With given `Waveform` waveform definitions `Something` and `SomethingElse`, an inheriting class may define the waveforms for the I and Q channels like this: `class MyGate(CustomIQWaveforms, i_wave=Something, q_wave=SomethingElse)`.

Attributes

|  |  |
|----|----|
| [`excluded_parameters`](#iqm.pulse.gate_implementation.CustomIQWaveforms.excluded_parameters "iqm.pulse.gate_implementation.CustomIQWaveforms.excluded_parameters") | Parameters names to be excluded from `self.parameters`. |
| [`root_parameters`](#iqm.pulse.gate_implementation.CustomIQWaveforms.root_parameters "iqm.pulse.gate_implementation.CustomIQWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
| [`wave_i`](#iqm.pulse.gate_implementation.CustomIQWaveforms.wave_i "iqm.pulse.gate_implementation.CustomIQWaveforms.wave_i") | Waveform for the I channel. |
| [`wave_q`](#iqm.pulse.gate_implementation.CustomIQWaveforms.wave_q "iqm.pulse.gate_implementation.CustomIQWaveforms.wave_q") | Waveform for the Q channel. |
| [`dependent_waves`](#iqm.pulse.gate_implementation.CustomIQWaveforms.dependent_waves "iqm.pulse.gate_implementation.CustomIQWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

wave_i*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\]*  
Waveform for the I channel.

wave_q*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\]*  
Waveform for the Q channel.

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

excluded_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= \[\]*  
Parameters names to be excluded from `self.parameters`. Inheriting classes may override this if certain parameters are not wanted in that class (also parameters defined by the waveforms can be excluded).

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation.CustomIQWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ce599b5bc854420bafb9f6b0af23e0b5db52a274.png)
