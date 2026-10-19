> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 325942550ed6e67eb8e7a474654ff337455493e2f7bf5d51c4508c2962c76379.

# VirtualRZ

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.VirtualRZ(*duration*, *phase_increment*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Change the upconversion phase reference.

The phase change can be done either by updating the phase of the local oscillator directly using a hardware instruction, or algebraically by incrementing [`IQPulse.phase`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse.phase "iqm.pulse.playlist.instructions.IQPulse.phase") of all the IQPulses following the VirtualRZ instruction in the [`Segment`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Segment.html#iqm.pulse.playlist.schedule.Segment "iqm.pulse.playlist.schedule.Segment").

Attributes

|  |  |
|----|----|
| [`phase_increment`](#iqm.pulse.playlist.instructions.VirtualRZ.phase_increment "iqm.pulse.playlist.instructions.VirtualRZ.phase_increment") | Phase increment for the local oscillator of a drive channel, in radians. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **phase_increment** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

phase_increment*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Phase increment for the local oscillator of a drive channel, in radians.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.VirtualRZ](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ebc78695dcc595d65be14a60648595da56fd02e5.png)
