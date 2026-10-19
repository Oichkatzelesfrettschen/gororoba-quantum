> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Segment.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Segment.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9681416be5a0f2605c63c5919c9b903662f6ed3143fc8bce85af39378965641f.

# Segment

Module: [`iqm.pulse.playlist.schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.html#module-iqm.pulse.playlist.schedule "iqm.pulse.playlist.schedule")

*class* iqm.pulse.playlist.schedule.Segment(*instructions*, *\**, *duration=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Sequence of instructions, for a single channel.

Basically a list\[Instruction\] that keeps track of the time duration of its contents.

Parameters:  
- **instructions** (*Iterable\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\]*) – contents of the segment

- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – If None, compute the sum of the durations of `instructions`. Otherwise, the time duration (in samples) of the segment, which must match the aforementioned sum if the Segment is still to be modified.

Attributes

|  |  |
|----|----|
| [`duration`](#iqm.pulse.playlist.schedule.Segment.duration "iqm.pulse.playlist.schedule.Segment.duration") | Sum of the durations of the instructions in the segment, in samples. |

Methods

|  |  |
|----|----|
| [`append`](#iqm.pulse.playlist.schedule.Segment.append "iqm.pulse.playlist.schedule.Segment.append") | Append an instruction to the end of the segment. |
| [`copy`](#iqm.pulse.playlist.schedule.Segment.copy "iqm.pulse.playlist.schedule.Segment.copy") | Make an independent copy of the segment. |
| [`extend`](#iqm.pulse.playlist.schedule.Segment.extend "iqm.pulse.playlist.schedule.Segment.extend") | Append all instructions from an iterable to the end of the segment. |
| [`pop`](#iqm.pulse.playlist.schedule.Segment.pop "iqm.pulse.playlist.schedule.Segment.pop") | Remove and return the instruction at the given index of the segment. |
| [`prepend`](#iqm.pulse.playlist.schedule.Segment.prepend "iqm.pulse.playlist.schedule.Segment.prepend") | Prepend an instruction to the beginning of the segment. |

copy()  
Make an independent copy of the segment.

Mutating the original must not affect the copy, or vice versa. Instructions are immutable, so they need not be copied.

Returns:  
copy of the segment

Return type:  
[*Segment*](#iqm.pulse.playlist.schedule.Segment "iqm.pulse.playlist.schedule.Segment")

append(*instruction*)  
Append an instruction to the end of the segment.

Parameters:  
**instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction"))

Return type:  
*None*

prepend(*instruction*)  
Prepend an instruction to the beginning of the segment.

Parameters:  
**instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction"))

Return type:  
*None*

extend(*instructions*)  
Append all instructions from an iterable to the end of the segment.

Parameters:  
**instructions** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\]*)

Return type:  
*None*

pop(*idx=-1*)  
Remove and return the instruction at the given index of the segment.

Parameters:  
**idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

*property* duration*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Sum of the durations of the instructions in the segment, in samples.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.schedule.Segment](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-3b303832367d4b204a43554b1d98ca9c24be2089.png)
