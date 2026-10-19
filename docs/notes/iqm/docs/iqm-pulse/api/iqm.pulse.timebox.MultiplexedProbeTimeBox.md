> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MultiplexedProbeTimeBox.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MultiplexedProbeTimeBox.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cbb797306fb8a09a9b14294e7438358654f8b27fe0dd0d5d20d6ed6332d55669.

# MultiplexedProbeTimeBox

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.MultiplexedProbeTimeBox(*label*, *locus_components*, *atom*, *children=\<factory\>*, *scheduling=SchedulingStrategy.ASAP*, *scheduling_algorithm=SchedulingAlgorithm.HARD_BOUNDARY*, *neighborhood_components=\<factory\>*, *boxes_length=0*, *measure_components=\<factory\>*, *additional_components=\<factory\>*)  
Bases: [`MeasureBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox")

A `MeasureBox` for multiplexing IQ pulses in probe channels.

A MultiplexedProbeTimeBox’s atom contains exactly one `ReadoutTrigger` for each probe channel. This class implements [`multiplex()`](#iqm.pulse.timebox.MultiplexedProbeTimeBox.multiplex "iqm.pulse.timebox.MultiplexedProbeTimeBox.multiplex") between MultiplexedProbeTimeBox instances such that every `ReadoutTrigger` on overlapping probe channels is multiplexed with `ReadoutTrigger.__add__()` (non-overlapping probe channel contents are just combined).

Attributes

|  |  |
|----|----|
| `measure_components` | The `MeasureBoxes.measure_components` of the MeasureBoxes `self` belongs to. |
| `additional_components` | The `MeasureBoxes.additional_components` of the MeasureBoxes `self` belongs to. |
| `label` | Description the contents of the box for users' convenience. |
| `locus_components` | Names of the QPU components on which this timebox operates. |
| `atom` | Resolved contents of the TimeBox, or None if not resolved. |
| `children` | Further Timeboxes inside this TimeBox. |
| `neighborhood_components` | Dict of neighborhood range integers mapped to sets of components neighboring the locus of this `TimeBox`. |

Methods

|  |  |
|----|----|
| [`from_readout_trigger`](#iqm.pulse.timebox.MultiplexedProbeTimeBox.from_readout_trigger "iqm.pulse.timebox.MultiplexedProbeTimeBox.from_readout_trigger") | Build an atomic MultiplexedProbeTimeBox from a single ReadoutTrigger instruction. |
| [`multiplex`](#iqm.pulse.timebox.MultiplexedProbeTimeBox.multiplex "iqm.pulse.timebox.MultiplexedProbeTimeBox.multiplex") | Multiplex two atomic `MultiplexedProbeTimeBox` instances together. |

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **atom** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") *\|* *None*)

- **children** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*,* *...\]*)

- **scheduling** ([*SchedulingStrategy*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy"))

- **scheduling_algorithm** ([*SchedulingAlgorithm*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm"))

- **neighborhood_components** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

- **boxes_length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **measure_components** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **additional_components** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

multiplex(*other*)  
Multiplex two atomic `MultiplexedProbeTimeBox` instances together.

The multiplexing is done such that every `ReadoutTrigger` belonging to the same probe channel are multiplexed together. Otherwise, behaves like `MeasureBox.__add__`, returning a normal `MeasureBox`.

Parameters:  
**other** ([*MeasureBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox"))

Return type:  
[*MeasureBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox")

*static* from_readout_trigger(*readout_trigger*, *probe_channel*, *locus_components*, *\**, *label=''*, *block_channels=()*, *block_duration=0*)  
Build an atomic MultiplexedProbeTimeBox from a single ReadoutTrigger instruction.

Parameters:  
- **readout_trigger** ([*ReadoutTrigger*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger")) – Readout trigger instruction.

- **probe_channel** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the probe channel to play `readout_trigger` in.

- **locus_components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Locus components.

- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Label of the new timebox.

- **block_channels** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Names of channels to block.

- **block_duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Duration of the required blocking (in samples).

Returns:  
Atomic timebox containing `readout_trigger` in the channel `probe_channel`.

Return type:  
[*MultiplexedProbeTimeBox*](#iqm.pulse.timebox.MultiplexedProbeTimeBox "iqm.pulse.timebox.MultiplexedProbeTimeBox")

Inheritance

![Inheritance diagram of iqm.pulse.timebox.MultiplexedProbeTimeBox](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-5e7c6cd0c1e4a98d03c634ddedec4b9c52aa0133.png)
