> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4adb64868fe27e992b69dc21ddfea6bed531216ceb17dafa6875cff7aeb8dd41.

# Nothing

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.Nothing(*duration*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Used to extend a control channel in time, without blocking it, during scheduling.

Can overlap with any other Instruction. Converted to a [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instruction at the end of scheduling.

Attributes

|  |  |
|----|----|
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
**duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.Nothing](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-f51ca33a2bb69750c66e9c2bdbef909850965e02.png)
