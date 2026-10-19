> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.segment.Segment.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.segment.Segment.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d90c314c3616bab7371d3b4de66d9469dcfb5223df92b6d75c1388e6b92515ff.

# Segment

*class* iqm.models.playlist.segment.Segment(*instructions=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Contains the instructions to be executed in one segment for each channel.

Parameters:  
- **instructions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – dict containing controller name as the key and the list of Instruction indices to be executed

- **value.** (*as the*)

Module: [`iqm.models.playlist.segment`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.segment.html#module-iqm.models.playlist.segment "iqm.models.playlist.segment")

Attributes

|                |     |
|----------------|-----|
| `instructions` |     |

Methods

|  |  |
|----|----|
| [`add_to_segment`](#iqm.models.playlist.segment.Segment.add_to_segment "iqm.models.playlist.segment.Segment.add_to_segment") | Add an instruction to the segment on a specific channel. |

add_to_segment(*channel_description*, *instruction*)  
Add an instruction to the segment on a specific channel.

Also adds the instruction to the channel’s instruction and waveform tables.

Parameters:  
- **channel_description** ([*ChannelDescription*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html#iqm.models.playlist.channel_descriptions.ChannelDescription "iqm.models.playlist.channel_descriptions.ChannelDescription")) – Channel on which to add the instruction.

- **instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")) – The instruction to be added

Return type:  
None
