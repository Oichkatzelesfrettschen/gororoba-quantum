> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 573f342f5f4bce93dc18f56aaab84fc8047562e71d7f0b012c0b0bfe84f7db6d.

# Playlist

*class* iqm.models.playlist.playlist.Playlist(*channel_descriptions=\<factory\>*, *segments=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Information required to build a batch of programs for AWGs and readout instruments.

Consists of a number of [`Segment`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.segment.Segment.html#iqm.models.playlist.segment.Segment "iqm.models.playlist.segment.Segment") s, executed in a sequence, and information about the properties of the control and readout channels used in the Segments, as well as [`Instruction`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction") and [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform") tables.

This class implements the new data structure that contains all the data necessary for an experiment to execute. Playlist contains information of all the channels used as well as the instruction execution schedule.

Parameters:  
- **channel_descriptions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelDescription*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html#iqm.models.playlist.channel_descriptions.ChannelDescription "iqm.models.playlist.channel_descriptions.ChannelDescription")*\]*) – Controller name mapped to channel and channel specific instruction and waveform data.

- **segments** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Segment*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.segment.Segment.html#iqm.models.playlist.segment.Segment "iqm.models.playlist.segment.Segment")*\]*) – Contains all the segments in the order of execution.

Module: [`iqm.models.playlist.playlist`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.html#module-iqm.models.playlist.playlist "iqm.models.playlist.playlist")

Attributes

|                        |     |
|------------------------|-----|
| `channel_descriptions` |     |
| `segments`             |     |

Methods

|  |  |
|----|----|
| [`add_channel`](#iqm.models.playlist.playlist.Playlist.add_channel "iqm.models.playlist.playlist.Playlist.add_channel") | Adds a new channel to the Playlist. |
| [`view`](#iqm.models.playlist.playlist.Playlist.view "iqm.models.playlist.playlist.Playlist.view") | Return operations of the playlist grouped by segments and channel names for easy inspection. |

add_channel(*new_channel*)  
Adds a new channel to the Playlist.

Parameters:  
**new_channel** ([*ChannelDescription*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html#iqm.models.playlist.channel_descriptions.ChannelDescription "iqm.models.playlist.channel_descriptions.ChannelDescription")) – channel to add

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – channel with that name already exists, and has different properties

Return type:  
None

view(*\**, *filter_segments=None*, *filter_channels=None*, *kind='operations'*)  
Return operations of the playlist grouped by segments and channel names for easy inspection. This method is not meant to be used for integration purposes, but rather for hands-on inspection and debugging.

Parameters:  
- **filter_segments** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – List of segment indexes to filter by. If None, all segments are included.

- **filter_channels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of channel names to filter by. If None, all channels are included.

- **kind** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Type of data to return in the inner dict, either “strings”, “operations” or “instructions”.

Returns:  
keys are channels, values are lists of operations or instructions, or string representations of the operations.

Return type:  
Dict of segments, where values are dicts

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If kind is not “strings”, “operations” or “instructions”.
