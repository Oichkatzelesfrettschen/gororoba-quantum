> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d9ebafb1c900fac0e982cb984dc681b6014f93d452126bf3598c27936959ddbe.

# Wait

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.Wait(*duration*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Behave as if outputting zero-valued samples for the duration of the instruction.

Used to idle QPU components. However, may be replaced with a dynamical decoupling sequence after the scheduling step. If you want to make sure that this does not happen, use [`Block`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html#iqm.pulse.playlist.instructions.Block "iqm.pulse.playlist.instructions.Block") instead.

Attributes

|  |  |
|----|----|
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
**duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.Wait](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e796dd6347ac752540855c5741f206acce98062b.png)
