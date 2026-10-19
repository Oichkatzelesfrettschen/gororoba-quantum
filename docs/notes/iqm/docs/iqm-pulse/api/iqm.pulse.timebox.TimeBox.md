> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 05a36ab54b87f97299095e3cc234c49282338c8708e1cc5039be336797d848ab.

# TimeBox

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.TimeBox(*label*, *locus_components*, *atom*, *children=\<factory\>*, *scheduling=SchedulingStrategy.ASAP*, *scheduling_algorithm=SchedulingAlgorithm.HARD_BOUNDARY*, *neighborhood_components=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Container for one or more instruction schedule fragments, to be scheduled according to a given strategy.

Each TimeBox can be labeled using a human-readable *label* describing it, and operates on a number of *locus components*, using some of their control channels. It can be either *atomic* or *composite*.

- An atomic box only contains a single [`Schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule").

- A composite box contains a sequence of other TimeBoxes as its children. The locus components are the union of the locus components of the children. If two children use the same channel so that they cannot happen simultaneously, they must happen in the order they occur in the sequence.

A box can be made atomic by *resolving* it using `ScheduleBuilder.resolve_timebox`. The time duration of the box is determined by its contents and the way they are scheduled during the resolution.

TimeBoxes can be concatenated with the following rules:

- Addition concatenates the children of the operands into a single TimeBox.

- The pipe operation groups two TimeBoxes together without concatenating.

- Iterables of Boxes are treated as the sum of the elements.

Let `a, b, c, d` be TimeBoxes. Then

``` python
a_then_b = a + b
c_then_d = (c + d).set_alap()
abcd = a_then_b | c_then_d

abb = a + [b, b]
ccd = [c, c] | d

all_together = abcd | abb + ccd

# is equivalent to:
all_together = a + b | (c + d).set_alap() | a + b + b + c + (c | d)
```

Attributes

|  |  |
|----|----|
| [`scheduling`](#iqm.pulse.timebox.TimeBox.scheduling "iqm.pulse.timebox.TimeBox.scheduling") | Determines how the contents of a composite TimeBox are scheduled by ScheduleBuilder. |
| [`scheduling_algorithm`](#iqm.pulse.timebox.TimeBox.scheduling_algorithm "iqm.pulse.timebox.TimeBox.scheduling_algorithm") | Determines the algorithm used in converting the TimeBox to a Schedule. |
| [`label`](#iqm.pulse.timebox.TimeBox.label "iqm.pulse.timebox.TimeBox.label") | Description the contents of the box for users' convenience. |
| [`locus_components`](#iqm.pulse.timebox.TimeBox.locus_components "iqm.pulse.timebox.TimeBox.locus_components") | Names of the QPU components on which this timebox operates. |
| [`atom`](#iqm.pulse.timebox.TimeBox.atom "iqm.pulse.timebox.TimeBox.atom") | Resolved contents of the TimeBox, or None if not resolved. |
| [`children`](#iqm.pulse.timebox.TimeBox.children "iqm.pulse.timebox.TimeBox.children") | Further Timeboxes inside this TimeBox. |
| [`neighborhood_components`](#iqm.pulse.timebox.TimeBox.neighborhood_components "iqm.pulse.timebox.TimeBox.neighborhood_components") | Dict of neighborhood range integers mapped to sets of components neighboring the locus of this `TimeBox`. |

Methods

|  |  |
|----|----|
| [`atomic`](#iqm.pulse.timebox.TimeBox.atomic "iqm.pulse.timebox.TimeBox.atomic") | Build an atomic timebox from a schedule. |
| [`composite`](#iqm.pulse.timebox.TimeBox.composite "iqm.pulse.timebox.TimeBox.composite") | Build a composite timebox from a sequence of timeboxes. |
| [`print`](#iqm.pulse.timebox.TimeBox.print "iqm.pulse.timebox.TimeBox.print") | Print a simple representation of the contents of this box. |
| [`set_alap`](#iqm.pulse.timebox.TimeBox.set_alap "iqm.pulse.timebox.TimeBox.set_alap") | Set the scheduling strategy to As late as possible (ALAP). |
| [`set_asap`](#iqm.pulse.timebox.TimeBox.set_asap "iqm.pulse.timebox.TimeBox.set_asap") | Set the scheduling strategy to As soon as possible (ASAP). |
| [`validate`](#iqm.pulse.timebox.TimeBox.validate "iqm.pulse.timebox.TimeBox.validate") | Validate the contents of the TimeBox. |

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **atom** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") *\|* *None*)

- **children** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*,* *...\]*)

- **scheduling** ([*SchedulingStrategy*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy"))

- **scheduling_algorithm** ([*SchedulingAlgorithm*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm"))

- **neighborhood_components** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Description the contents of the box for users’ convenience. Has no functional effect.

locus_components*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the QPU components on which this timebox operates. These can include additional components to the ones included in one of the channels occupied by this `TimeBox`. The components included in this attribute will be blocked in scheduling, in addition to the ones dictated by the neighborhood range (see [`neighborhood_components`](#iqm.pulse.timebox.TimeBox.neighborhood_components "iqm.pulse.timebox.TimeBox.neighborhood_components")).

atom*: [Schedule](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Resolved contents of the TimeBox, or None if not resolved.

children*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[TimeBox](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox"), ...\]*  
Further Timeboxes inside this TimeBox.

scheduling*: [SchedulingStrategy](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy")* *= 'ASAP'*  
Determines how the contents of a composite TimeBox are scheduled by ScheduleBuilder. Has no meaning for an atomic TimeBox.

scheduling_algorithm*: [SchedulingAlgorithm](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm")* *= 'HARD_BOUNDARY'*  
Determines the algorithm used in converting the TimeBox to a Schedule.

neighborhood_components*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Dict of neighborhood range integers mapped to sets of components neighboring the locus of this `TimeBox`. These are used in the scheduling when the corresponding neighborhood range is used. The scheduling algorithm computes the neighborhood components (unless it has been already precomputed by e.g. the [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")) and caches them under this attribute. Neighborhood range 0 means just the components affected by one of the channels in `self.atom` + `self.locus`, 1 means also neighboring couplers, 2 the components connected to those couplers, and so on. Note: range 0 may differ from `self.locus_components`: it can have additional components that have occupied channels in `self` but are not defined as a part of the locus of this `TimeBox` for any reason.

*classmethod* composite(*boxes*, *\**, *label=''*, *scheduling=SchedulingStrategy.ASAP*, *scheduling_algorithm=SchedulingAlgorithm.HARD_BOUNDARY*)  
Build a composite timebox from a sequence of timeboxes.

Parameters:  
- **boxes** ([*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") *\|* [*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") *\|* [*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*\]\]*) – contents of the new timebox. Any iterables of timeboxes will be flattened (recursively) and extended to the contents in the same order.

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – label of the new timebox

- **scheduling** ([*SchedulingStrategy*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy")) – scheduling strategy to use when resolving the new timebox

- **scheduling_algorithm** ([*SchedulingAlgorithm*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm")) – scheduling algorithm to use when resolving the new timebox

Returns:  
composite timebox containing `boxes` as its children

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

*classmethod* atomic(*schedule*, *\**, *locus_components*, *label*)  
Build an atomic timebox from a schedule.

Parameters:  
- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – contents of the new timebox

- **locus_components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – names QPU components `schedule` operates on

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – label of the new timebox

Returns:  
atomic timebox containing `schedule`

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

validate(*path=()*)  
Validate the contents of the TimeBox.

Parameters:  
**path** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Labels of ancestor boxes, to generate a better error message.

Return type:  
*None*

set_asap()  
Set the scheduling strategy to As soon as possible (ASAP).

Return type:  
[*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

set_alap()  
Set the scheduling strategy to As late as possible (ALAP).

Return type:  
[*TimeBox*](#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

print(*\_idxs=()*)  
Print a simple representation of the contents of this box.

Parameters:  
**\_idxs** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *...\]*)

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.timebox.TimeBox](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-4e7e9564821b66fef2d8c96420edb90095ca5939.png)
