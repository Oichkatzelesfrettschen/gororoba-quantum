> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.SegmentPointer.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.SegmentPointer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcdd7e43309f8661814045ce8382e7a666de91d2b3ea46a61989a4bcac338130.

# SegmentPointer

Module: [`iqm.pulse.scheduler`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.html#module-iqm.pulse.scheduler "iqm.pulse.scheduler")

*class* iqm.pulse.scheduler.SegmentPointer(*source*, *idx*, *TOL*, *frac=0.0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Tool for working with Segments.

Serves as a time pointer inside the Segment.

Attributes

|  |  |
|----|----|
| [`frac`](#iqm.pulse.scheduler.SegmentPointer.frac "iqm.pulse.scheduler.SegmentPointer.frac") | time, in seconds, after the start of the current instruction |
| [`remainder`](#iqm.pulse.scheduler.SegmentPointer.remainder "iqm.pulse.scheduler.SegmentPointer.remainder") | Remaining duration of the current instruction (in seconds). |
| [`source`](#iqm.pulse.scheduler.SegmentPointer.source "iqm.pulse.scheduler.SegmentPointer.source") | contents of the Segment |
| [`idx`](#iqm.pulse.scheduler.SegmentPointer.idx "iqm.pulse.scheduler.SegmentPointer.idx") | index of the current instruction |
| [`TOL`](#iqm.pulse.scheduler.SegmentPointer.TOL "iqm.pulse.scheduler.SegmentPointer.TOL") | time durations equal or smaller than this tolerance are considered zero (in seconds) |

Methods

|  |  |
|----|----|
| [`cut_tail`](#iqm.pulse.scheduler.SegmentPointer.cut_tail "iqm.pulse.scheduler.SegmentPointer.cut_tail") | Cut the source of the pointer at the current index. |
| [`fastforward`](#iqm.pulse.scheduler.SegmentPointer.fastforward "iqm.pulse.scheduler.SegmentPointer.fastforward") | Move the pointer forward by `duration` seconds. |
| [`get`](#iqm.pulse.scheduler.SegmentPointer.get "iqm.pulse.scheduler.SegmentPointer.get") | Current instruction. |
| [`next`](#iqm.pulse.scheduler.SegmentPointer.next "iqm.pulse.scheduler.SegmentPointer.next") | Move to the beginning of the next instruction. |
| [`rewind`](#iqm.pulse.scheduler.SegmentPointer.rewind "iqm.pulse.scheduler.SegmentPointer.rewind") | Move the pointer back by `duration` seconds. |
| [`tail`](#iqm.pulse.scheduler.SegmentPointer.tail "iqm.pulse.scheduler.SegmentPointer.tail") | Instructions from the current index onwards. |

Parameters:  
- **source** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\]*)

- **idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **TOL** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **frac** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

source*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")\]*  
contents of the Segment

idx*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
index of the current instruction

TOL*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
time durations equal or smaller than this tolerance are considered zero (in seconds)

frac*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
time, in seconds, after the start of the current instruction

get()  
Current instruction.

Return type:  
[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

*property* remainder*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Remaining duration of the current instruction (in seconds).

next()  
Move to the beginning of the next instruction.

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

cut_tail()  
Cut the source of the pointer at the current index.

Truncate [`source`](#iqm.pulse.scheduler.SegmentPointer.source "iqm.pulse.scheduler.SegmentPointer.source") at [`idx`](#iqm.pulse.scheduler.SegmentPointer.idx "iqm.pulse.scheduler.SegmentPointer.idx"), make `self` point to the cut tail part only. [`frac`](#iqm.pulse.scheduler.SegmentPointer.frac "iqm.pulse.scheduler.SegmentPointer.frac") is not changed.

Note: modifies [`source`](#iqm.pulse.scheduler.SegmentPointer.source "iqm.pulse.scheduler.SegmentPointer.source").

Return type:  
*None*

tail()  
Instructions from the current index onwards.

Return type:  
[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")\]

rewind(*duration*)  
Move the pointer back by `duration` seconds.

Parameters:  
**duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
*None*

fastforward(*duration*)  
Move the pointer forward by `duration` seconds.

Parameters:  
**duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.scheduler.SegmentPointer](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d0645bfac70baa0de450a382868dfd46e953ce67.png)
