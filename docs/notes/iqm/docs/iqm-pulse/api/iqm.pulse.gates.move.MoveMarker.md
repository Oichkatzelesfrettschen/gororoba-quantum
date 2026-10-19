> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MoveMarker.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MoveMarker.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 91ade1525da96a734b902cf97deea7958271ddf6f4a589c11c4db533f95eb5fc.

# MoveMarker

Module: [`iqm.pulse.gates.move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html#module-iqm.pulse.gates.move "iqm.pulse.gates.move")

*class* iqm.pulse.gates.move.MoveMarker(*\**, *duration=0*, *first_move_component*, *second_move_component*, *detuning*)  
Bases: [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait")

Special annotation instruction to indicate the beginning and ending of MOVE gates.

The *same instance* of this instruction will be inserted into the drive channels of both MOVE components, right before the beginning MOVE VirtualRZ instructions, to link the channels together (otherwise, there would be nothing explicit in the Schedule indicating that there is a MOVE gate happening between two components).

Another shared instance will be inserted to the aforementioned channels right before the ending MOVE VirtualRZ instruction. The VirtualRZ instructions between the markers on the second MOVE component drive channel will be applied to the first MOVE component instead in a post-compilation pass.

Attributes

|  |  |
|----|----|
| [`duration`](#iqm.pulse.gates.move.MoveMarker.duration "iqm.pulse.gates.move.MoveMarker.duration") | Time duration of the instruction. |
| `first_move_component` |  |
| `second_move_component` |  |
| `detuning` |  |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **first_move_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **second_move_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **detuning** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

duration*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
Time duration of the instruction. In samples at the channel sample rate.

Inheritance

![Inheritance diagram of iqm.pulse.gates.move.MoveMarker](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-0f04f1eb7b339dd659bf05e87fa381d8b660c475.png)
