> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.RealPulse.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.RealPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0be1e04820517a8acb9cb102308169e9371ec302db54d3254ca659eb388a6536.

# RealPulse

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.RealPulse(*duration*, *wave*, *scale*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Play a real-valued pulse.

Attributes

|  |  |
|----|----|
| [`wave`](#iqm.pulse.playlist.instructions.RealPulse.wave "iqm.pulse.playlist.instructions.RealPulse.wave") | Shape of the pulse. |
| [`scale`](#iqm.pulse.playlist.instructions.RealPulse.scale "iqm.pulse.playlist.instructions.RealPulse.scale") | Scaling factor for the waveform. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

|  |  |
|----|----|
| [`get_waveforms`](#iqm.pulse.playlist.instructions.RealPulse.get_waveforms "iqm.pulse.playlist.instructions.RealPulse.get_waveforms") | Returns all the waveforms the Instruction contains. |
| [`validate`](#iqm.pulse.playlist.instructions.RealPulse.validate "iqm.pulse.playlist.instructions.RealPulse.validate") | Validate the instruction attributes. |

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **wave** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"))

- **scale** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

wave*: [Waveform](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")*  
Shape of the pulse.

scale*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Scaling factor for the waveform.

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

![Inheritance diagram of iqm.pulse.playlist.instructions.RealPulse](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-7f3e07bc228d696b6f18d2ad98f71a17dc994ee9.png)
