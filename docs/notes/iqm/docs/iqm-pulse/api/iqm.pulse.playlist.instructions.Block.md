> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 48f50b988a208810113dcec183fb2debc3d2eb3f34c471a897317a032d93168f.

# Block

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.Block(*duration*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Behave strictly as if outputting zero-valued samples for the duration of the instruction.

Used to block a control channel during compilation. A more strict version of [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait"), cannot be replaced with DD sequences during compilation. Converted to a [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instruction at the end of compilation process.

In “Tetris” scheduling, several Block instructions can overlap in time, whereas Waits cannot.

Attributes

|  |  |
|----|----|
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
**duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.Block](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-11728591e8025e8bb9ba5512b5b1142c68ab3260.png)
