> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad34686d711003734196d6b0f3e5b4a76932501d312a50a0eaeca4f41b204322.

# Instruction

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.Instruction(*duration*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Command that can be executed by the quantum computer on a control channel.

Has a well-specified time duration.

Attributes

|  |  |
|----|----|
| [`duration`](#iqm.pulse.playlist.instructions.Instruction.duration "iqm.pulse.playlist.instructions.Instruction.duration") | Time duration of the instruction. |
| [`id`](#iqm.pulse.playlist.instructions.Instruction.id "iqm.pulse.playlist.instructions.Instruction.id") | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

|  |  |
|----|----|
| [`copy`](#iqm.pulse.playlist.instructions.Instruction.copy "iqm.pulse.playlist.instructions.Instruction.copy") | Make a copy of the Instruction with the given changes applied to its contents. |
| [`get_child_instructions`](#iqm.pulse.playlist.instructions.Instruction.get_child_instructions "iqm.pulse.playlist.instructions.Instruction.get_child_instructions") | Returns all the child Instructions the Instruction contains. |
| [`get_waveforms`](#iqm.pulse.playlist.instructions.Instruction.get_waveforms "iqm.pulse.playlist.instructions.Instruction.get_waveforms") | Returns all the waveforms the Instruction contains. |
| [`validate`](#iqm.pulse.playlist.instructions.Instruction.validate "iqm.pulse.playlist.instructions.Instruction.validate") | Validate the instruction attributes. |

Parameters:  
**duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

duration*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Time duration of the instruction. In samples at the channel sample rate.

id*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Unique id for caching purposes, which can be used if the instruction is not hashable.

validate()  
Validate the instruction attributes.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – something about the instruction is not ok

Return type:  
*None*

copy(*\*\*changes*)  
Make a copy of the Instruction with the given changes applied to its contents.

Return type:  
[*Instruction*](#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

get_child_instructions()  
Returns all the child Instructions the Instruction contains.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Instruction*](#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction"), …\]

get_waveforms()  
Returns all the waveforms the Instruction contains.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"), …\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.Instruction](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6e509df8845ca1e23b17946f87ff1d7d2a3781f3.png)
