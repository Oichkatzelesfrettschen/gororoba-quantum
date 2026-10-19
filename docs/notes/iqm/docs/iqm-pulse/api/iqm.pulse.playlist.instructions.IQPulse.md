> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5e9a54deb261585bfcd30da376829bfe96175f8113ff7919d7d2dd83b6b80c31.

# IQPulse

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.IQPulse(*duration*, *wave_i*, *wave_q*, *scale_i=1.0*, *scale_q=0.0*, *phase=0.0*, *modulation_frequency=0.0*, *phase_increment=0.0*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Play an upconverted pulse that contains real in-phase and quadrature waveforms.

Attributes

|  |  |
|----|----|
| [`modulation_frequency`](#iqm.pulse.playlist.instructions.IQPulse.modulation_frequency "iqm.pulse.playlist.instructions.IQPulse.modulation_frequency") | Modulation frequency of the waveforms, in units of the sampling rate. |
| [`phase`](#iqm.pulse.playlist.instructions.IQPulse.phase "iqm.pulse.playlist.instructions.IQPulse.phase") | Phase of the pulse relative to the channel upconversion oscillator ("carrier wave"), in radians. |
| [`phase_increment`](#iqm.pulse.playlist.instructions.IQPulse.phase_increment "iqm.pulse.playlist.instructions.IQPulse.phase_increment") | Phase increment for the channel upconversion oscillator ("carrier wave"), affecting this pulse and all pulses that are played after it on the channel, in radians. |
| [`scale_i`](#iqm.pulse.playlist.instructions.IQPulse.scale_i "iqm.pulse.playlist.instructions.IQPulse.scale_i") | Scaling factor for the I quadrature. |
| [`scale_q`](#iqm.pulse.playlist.instructions.IQPulse.scale_q "iqm.pulse.playlist.instructions.IQPulse.scale_q") | Scaling factor for the Q quadrature. |
| [`wave_i`](#iqm.pulse.playlist.instructions.IQPulse.wave_i "iqm.pulse.playlist.instructions.IQPulse.wave_i") | I quadrature envelope. |
| [`wave_q`](#iqm.pulse.playlist.instructions.IQPulse.wave_q "iqm.pulse.playlist.instructions.IQPulse.wave_q") | Q quadrature envelope. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

|  |  |
|----|----|
| [`get_waveforms`](#iqm.pulse.playlist.instructions.IQPulse.get_waveforms "iqm.pulse.playlist.instructions.IQPulse.get_waveforms") | Returns all the waveforms the Instruction contains. |
| [`validate`](#iqm.pulse.playlist.instructions.IQPulse.validate "iqm.pulse.playlist.instructions.IQPulse.validate") | Validate the instruction attributes. |

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **wave_i** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"))

- **wave_q** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"))

- **scale_i** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **scale_q** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **modulation_frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **phase_increment** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

wave_i*: [Waveform](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")*  
I quadrature envelope.

wave_q*: [Waveform](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")*  
Q quadrature envelope.

scale_i*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 1.0*  
Scaling factor for the I quadrature.

scale_q*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Scaling factor for the Q quadrature.

phase*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Phase of the pulse relative to the channel upconversion oscillator (“carrier wave”), in radians.

modulation_frequency*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Modulation frequency of the waveforms, in units of the sampling rate. This modulation is additional to the channel upconversion frequency. The default value of 0.0 does not modulate. Note that the phase of this modulation resets for every instruction, that is, successive instances of the same modulated pulse are not phase coherent.

phase_increment*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Phase increment for the channel upconversion oscillator (“carrier wave”), affecting this pulse and all pulses that are played after it on the channel, in radians.

validate()  
Validate the instruction attributes.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – something about the instruction is not ok

Return type:  
*None*

get_waveforms()  
Returns all the waveforms the Instruction contains.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"), …\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.IQPulse](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e1f5436e9dec4b2b91c87dfabb5dc0b6d4e8b190.png)
