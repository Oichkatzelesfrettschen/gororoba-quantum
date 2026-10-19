> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c2fe7470983fc5e66bda3783a96c70d30f07288c8331a9650a3b67e747a7054b.

# Schedule

Module: [`iqm.pulse.playlist.schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.html#module-iqm.pulse.playlist.schedule "iqm.pulse.playlist.schedule")

*class* iqm.pulse.playlist.schedule.Schedule(*contents=None*, *\**, *duration=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Set of synchronously executed AWG/readout programs that start on a single trigger.

Consists of a number of *channels*, each containing a [`Segment`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Segment.html#iqm.pulse.playlist.schedule.Segment "iqm.pulse.playlist.schedule.Segment") of [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction") s for a specific controller. For each channel, maps the channel name to its Segment of Instructions.

Mutable. To make an independent copy, use [`copy()`](#iqm.pulse.playlist.schedule.Schedule.copy "iqm.pulse.playlist.schedule.Schedule.copy").

Parameters:  
- **contents** (*Mapping\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Iterable\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\]\]* *\|* *None*) – mapping from channel name to a list of Instructions for that channel

- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Optional precomputed duration (in samples). In cases where the duration is known and performance is critical, the duration can be given in the constructor, allowing one to skip computing it.

Attributes

|  |  |
|----|----|
| [`duration`](#iqm.pulse.playlist.schedule.Schedule.duration "iqm.pulse.playlist.schedule.Schedule.duration") | The maximum duration of the Schedule's channels, in samples. |

Methods

|  |  |
|----|----|
| [`add_channels`](#iqm.pulse.playlist.schedule.Schedule.add_channels "iqm.pulse.playlist.schedule.Schedule.add_channels") | Add new empty channels to the schedule. |
| [`append`](#iqm.pulse.playlist.schedule.Schedule.append "iqm.pulse.playlist.schedule.Schedule.append") | Append a single Instruction to a specific channel in the Schedule. |
| [`channels`](#iqm.pulse.playlist.schedule.Schedule.channels "iqm.pulse.playlist.schedule.Schedule.channels") | The channels occupied in `self`. |
| [`cleanup`](#iqm.pulse.playlist.schedule.Schedule.cleanup "iqm.pulse.playlist.schedule.Schedule.cleanup") | Cleans up the schedule by removing things that do not affect the execution. |
| [`copy`](#iqm.pulse.playlist.schedule.Schedule.copy "iqm.pulse.playlist.schedule.Schedule.copy") | Make an independent copy of the schedule. |
| [`duration_in_seconds`](#iqm.pulse.playlist.schedule.Schedule.duration_in_seconds "iqm.pulse.playlist.schedule.Schedule.duration_in_seconds") | Schedule duration in seconds, taking into account the sample rates of the channels. |
| [`extend`](#iqm.pulse.playlist.schedule.Schedule.extend "iqm.pulse.playlist.schedule.Schedule.extend") | Append given Instruction to a specific channel in the Schedule. |
| [`front_pad`](#iqm.pulse.playlist.schedule.Schedule.front_pad "iqm.pulse.playlist.schedule.Schedule.front_pad") | Modify the schedule in place by front-padding it with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions. |
| [`front_pad_in_seconds`](#iqm.pulse.playlist.schedule.Schedule.front_pad_in_seconds "iqm.pulse.playlist.schedule.Schedule.front_pad_in_seconds") | Modifies the schedule in place by front-padding it with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions. |
| [`has_content_in`](#iqm.pulse.playlist.schedule.Schedule.has_content_in "iqm.pulse.playlist.schedule.Schedule.has_content_in") | Returns `True` if `self` has content in any of the given channels, otherwise `False`. |
| [`items`](#iqm.pulse.playlist.schedule.Schedule.items "iqm.pulse.playlist.schedule.Schedule.items") | Iterator over the schedule channel names and segments. |
| [`pad_to_hard_box`](#iqm.pulse.playlist.schedule.Schedule.pad_to_hard_box "iqm.pulse.playlist.schedule.Schedule.pad_to_hard_box") | Pad channels in `self` to the maximum channel length found within with `Wait` instructions. |
| [`pad_to_hard_box_in_seconds`](#iqm.pulse.playlist.schedule.Schedule.pad_to_hard_box_in_seconds "iqm.pulse.playlist.schedule.Schedule.pad_to_hard_box_in_seconds") | Pad channels in `self` to the maximum channel length (seconds) found within with Wait instructions. |
| [`pprint`](#iqm.pulse.playlist.schedule.Schedule.pprint "iqm.pulse.playlist.schedule.Schedule.pprint") | Fixed-width character graphics representation of the Schedule. |
| [`reverse`](#iqm.pulse.playlist.schedule.Schedule.reverse "iqm.pulse.playlist.schedule.Schedule.reverse") | Copy of the schedule with the order of the instructions in each channel reversed. |
| [`reverse_hard_box`](#iqm.pulse.playlist.schedule.Schedule.reverse_hard_box "iqm.pulse.playlist.schedule.Schedule.reverse_hard_box") | Copy of the schedule with the order of the instructions in each channel reversed. |
| [`validate`](#iqm.pulse.playlist.schedule.Schedule.validate "iqm.pulse.playlist.schedule.Schedule.validate") | Validate the contents of the schedule. |

*property* duration*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The maximum duration of the Schedule’s channels, in samples.

Computed only when needed and cached for performance.

duration_in_seconds(*channel_properties*)  
Schedule duration in seconds, taking into account the sample rates of the channels.

Parameters:  
**channel_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – channel properties.

Returns:  
schedule duration (in seconds)

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

pprint(*time_unit=16*)  
Fixed-width character graphics representation of the Schedule.

Assumes the `Instruction.duration` s are in samples.

Parameters:  
**time_unit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – unit of time represented by a single symbol (in samples)

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

items()  
Iterator over the schedule channel names and segments.

channels()  
The channels occupied in `self`.

Return type:  
[*KeysView*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.KeysView "(in Python v3.11)")

copy()  
Make an independent copy of the schedule.

Mutating the original must not affect the copy, or vice versa. Instructions are immutable, so they need not be copied.

Returns:  
copy of the schedule

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

add_channels(*channel_names*)  
Add new empty channels to the schedule.

If a given channel (identified by its controller name) already exist in the schedule, it is unchanged.

Modifies `self`.

Parameters:  
**channel_names** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – names of the controllers for which empty channels are added

Return type:  
*None*

append(*channel*, *instruction*)  
Append a single Instruction to a specific channel in the Schedule.

Parameters:  
- **channel** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the channel to append the instruction to

- **instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")) – instruction to append

Return type:  
*None*

extend(*channel*, *instructions*)  
Append given Instruction to a specific channel in the Schedule.

Parameters:  
- **channel** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the channel to append the instructions to

- **instructions** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\]*) – instructions to append

Return type:  
*None*

front_pad(*to_duration*)  
Modify the schedule in place by front-padding it with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions.

NOTE: this method cannot be used when there are variable sampling rates present in the schedule. In that case, use the method `front_pad_in_seconds`.

Parameters:  
**to_duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Duration of the resulting schedule, in samples.

Returns:  
`self`, with the padding

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

front_pad_in_seconds(*to_duration*, *channel_properties*)  
Modifies the schedule in place by front-padding it with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions.

The new duration is given in seconds, and this method works also with variable sample rates.

Parameters:  
- **to_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the resulting schedule, in seconds.

- **channel_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – Station channel properties.

Returns:  
`self`, with the padding

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

pad_to_hard_box()  
Pad channels in `self` to the maximum channel length found within with `Wait` instructions.

The ``` Wait``s are appended to the end of the segments. NOTE: this method cannot be used when there are variable sampling rates present in the schedule. In that case, use the method ``pad_to_hard_box_in_seconds ```.

Return type:  
*None*

pad_to_hard_box_in_seconds(*channel_properties*)  
Pad channels in `self` to the maximum channel length (seconds) found within with Wait instructions.

The Waits are appended to the end of the segments. The segment durations are compared in seconds, so this method works in the case of variable sampling rates as well. The padding is added to a channel only if the difference between the channel’s duration and the maximum duration is larger than the smallest possible instruction duration for that channel.

Parameters:  
**channel_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – channel properties (containing the sampling rates and granularities).

Return type:  
*None*

reverse()  
Copy of the schedule with the order of the instructions in each channel reversed.

NOTE: this method cannot be used when there are variable sampling rates present in the schedule.

To preserve synchronization of the channels, the channels are first rear-padded with [`Nothing`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html#iqm.pulse.playlist.instructions.Nothing "iqm.pulse.playlist.instructions.Nothing") instructions.

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

reverse_hard_box()  
Copy of the schedule with the order of the instructions in each channel reversed.

No additional time-synchronisation logic is implemented, so this method will break the synchronisation if `self` is not a schedule with matching durations in all segments.

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

cleanup()  
Cleans up the schedule by removing things that do not affect the execution.

Removes

- empty channels, and

- channels that only have idling instructions.

Modifies `self`.

Return type:  
[*Schedule*](#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

validate(*path=()*)  
Validate the contents of the schedule.

Parameters:  
**path** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
*None*

has_content_in(*channel_names*)  
Returns `True` if `self` has content in any of the given channels, otherwise `False`.

Parameters:  
**channel_names** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.playlist.schedule.Schedule](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-52f70797ef24ca927f5f0f8db962c2f3426d3172.png)
