> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f1a410e235c15857e217956b3b12db1862d95e75cd541cec85eed37c1d842f8b.

# MeasureBoxes

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.MeasureBoxes(*measure_boxes*, *measure_components*, *additional_components=None*)  
Bases: [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")

Multiplexable list of TimeBoxes associated with a measure implementation.

All `measure` implementations’ `__call__` method should return a `MeasureBoxes` instance. The measurements can be multiplexed together via [`multiplex()`](#iqm.pulse.timebox.MeasureBoxes.multiplex "iqm.pulse.timebox.MeasureBoxes.multiplex"), allowing parallel measurements within a single probe line.

A `MeasureBoxes` instance has the following structure: `[A] + [P, B, A] * n`, where `P` is a [`MultiplexedProbeTimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MultiplexedProbeTimeBox.html#iqm.pulse.timebox.MultiplexedProbeTimeBox "iqm.pulse.timebox.MultiplexedProbeTimeBox") instance (the actual readout triggers), `B` is a MeasureBox containing extra blocking (if any) on the probe channel after the measurement, and `A` is an auxiliary MeasureBox associated with a measure implementation (e.g. the `prx_12` shelving operation in shelved measurements). So, there is an initial auxiliary box and then any number of triplets `P, B, A`. The auxiliary boxes `A` and the extra probe block boxes `B` can be empty.\`\`.

Parameters:  
- **measure_boxes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*MeasureBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox")*\]*) – The measure boxes.

- **measure_components** (*Iterable\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Primary component names this measure `MeasureBoxes` instance is associated with. Note that this may be different from the `TimeBox.locus_components` attributes if its member boxes. Typically, this is the same as the measured qubits, but in some measure implementations, additional components may also be pinned in the operation (see [`MeasureBoxes.multiplex()`](#iqm.pulse.timebox.MeasureBoxes.multiplex "iqm.pulse.timebox.MeasureBoxes.multiplex")).

- **additional_components** (*Iterable\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Additional component names this measure `MeasureBoxes` instance is associated with (see [`MeasureBoxes.multiplex()`](#iqm.pulse.timebox.MeasureBoxes.multiplex "iqm.pulse.timebox.MeasureBoxes.multiplex")). By default, initiated as an empty set. The attribute can be used e.g. If the multiplexing should be blocked in some neighborhood of the `measure_components` (next neighbor qubits).

Methods

|  |  |
|----|----|
| [`append`](#iqm.pulse.timebox.MeasureBoxes.append "iqm.pulse.timebox.MeasureBoxes.append") | Append object to the end of the list. |
| [`extend`](#iqm.pulse.timebox.MeasureBoxes.extend "iqm.pulse.timebox.MeasureBoxes.extend") | Extend list by appending elements from the iterable. |
| [`from_readout_trigger`](#iqm.pulse.timebox.MeasureBoxes.from_readout_trigger "iqm.pulse.timebox.MeasureBoxes.from_readout_trigger") | Shortcut method for creating a `MeasureBoxes` instance from `ReadoutTrigger instance`. |
| [`is_multiplexable_with`](#iqm.pulse.timebox.MeasureBoxes.is_multiplexable_with "iqm.pulse.timebox.MeasureBoxes.is_multiplexable_with") | Whether `self` can be multiplexed with `other`. |
| [`multiplex`](#iqm.pulse.timebox.MeasureBoxes.multiplex "iqm.pulse.timebox.MeasureBoxes.multiplex") | Multiplex two `MeasureBoxes` instances together. |

is_multiplexable_with(*other*)  
Whether `self` can be multiplexed with `other`.

Parameters:  
**other** ([*MeasureBoxes*](#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

multiplex(*other*)  
Multiplex two `MeasureBoxes` instances together.

The multiplexing works such that the lists are aligned ASAP (as soon as possible) to the left. The auxiliary boxes `A` in the overlapping parts of the lists are summed together ([`MeasureBox.multiplex()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox.multiplex "iqm.pulse.timebox.MeasureBox.multiplex") resolves to just the normal `TimeBox.__add__()` method), the probe boxes `P` are multiplexed with `MultiplexedProbeTimeBox.multiplex`. The durations of the `P` boxes and their subsequent `B` boxes are adjusted so that 1) the duration of the `P` is the maximum of multiplexed boxes durations 2) the duration of the new `B` box is `<multiplexed block duration> = max((P1 + B1).duration, P2 + B2).duration) - max(P1.duration, P2.duration)`.

If the multiplexed `MeasureBoxes` lists are of a different length, the tail of the longer one is copied as it is into the multiplexed result.

If the `MeasureBoxes.measure_components` of `self` and `other` have an overlap, an error is raised. The error is raised also if `MeasureBoxes.additional_components` of `self` have an overlap with the `measure_components` of `other` (or vice versa). NOTE: the `additional_components` of `self` and `other` may still overlap.

Parameters:  
**other** ([*MeasureBoxes*](#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")) – MeasureBoxes instance to multiplex with `self`.

Returns:  
The multiplexed `MeasureBoxes` instance.

Raises:  
[**MeasureMultiplexingError**](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureMultiplexingError.html#iqm.pulse.timebox.MeasureMultiplexingError "iqm.pulse.timebox.MeasureMultiplexingError") – If `MeasureBoxes.measure_components` of `self` and `other` are overlapping or if `MeasureBoxes.additional_components` of `self` overlaps with the `MeasureBoxes.measure_components` of `other` (or vice versa). Note that `MeasureBoxes.additional_components` may still overlap with that of `other`.

Return type:  
[*MeasureBoxes*](#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")

*static* from_readout_trigger(*readout_trigger*, *probe_channel*, *measure_components*, *\**, *additional_components=None*, *extra_probe_block_duration=0*, *probe_box_segments=None*)  
Shortcut method for creating a `MeasureBoxes` instance from `ReadoutTrigger instance`.

The created `MeasureBoxes` instance will have a single probe box `P` with an optional extra probe block box `B` superseding it. The auxiliary box slots are occupied with empty boxes.

Parameters:  
- **readout_trigger** ([*ReadoutTrigger*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger")) – `ReadoutTrigger` instance.

- **probe_channel** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – channel name of the probe.

- **measure_components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The measure_components for the created `MeasureBoxes` instance.

- **additional_components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – The additional_components for the created `MeasureBoxes` instance (by default initialized as an empty set).

- **extra_probe_block_duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The duration of the extra probe block, in seconds. If not given, the extra probe block box will be empty.

- **probe_box_segments** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Segment*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Segment.html#iqm.pulse.playlist.schedule.Segment "iqm.pulse.playlist.schedule.Segment")*\]* *\|* *None*) – Optional contents for the drive/flux channels of the probe box.

Returns:  
`MeasureBoxes` instance with a single probe box.

Return type:  
[*MeasureBoxes*](#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")

append(*\_MeasureBoxes\_\_object*)  
Append object to the end of the list.

Parameters:  
**\_MeasureBoxes\_\_object** ([*object*](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)"))

Return type:  
*None*

extend(*other*)  
Extend list by appending elements from the iterable.

Parameters:  
**other** ([*object*](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)"))

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.timebox.MeasureBoxes](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-7a2eb11fa528b6809229c6235d0e9b64f7090af2.png)
