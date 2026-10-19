> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 886c0e422a8bc244cb0a69b9604c09ae60d68cded8c03c03dff32e51257379ef.

# ChannelDescription

*class* iqm.models.playlist.channel_descriptions.ChannelDescription(*channel_config*, *controller_name*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

ChannelDescription class contains all channel specific data and the suitable instructions and waveforms  
for a channel.

Parameters:  
- **channel_config** ([*ChannelConfiguration*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelConfiguration.html#iqm.models.playlist.channel_descriptions.ChannelConfiguration "iqm.models.playlist.channel_descriptions.ChannelConfiguration")) – ChannelConfiguration object which contains data related to the channel

- **controller_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the controller

- **instruction_table** – Contains mapping of the instructions to be executed on this channel. Each instruction should be unique.

- **waveform_table** – Contains mapping of the waveforms to be executed on this channel. Each waveform should be unique.

- **acquisition_table** – Table of acquisition configs. Each ReadoutTrigger instruction may ask to perform an arbitrary combination of these. In practice, possible combinations are limited by device capabilities.

Module: [`iqm.models.playlist.channel_descriptions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.html#module-iqm.models.playlist.channel_descriptions "iqm.models.playlist.channel_descriptions")

Attributes

|                     |     |
|---------------------|-----|
| `channel_config`    |     |
| `controller_name`   |     |
| `instruction_table` |     |
| `waveform_table`    |     |
| `acquisition_table` |     |

Methods

|  |  |
|----|----|
| [`add_acquisition`](#iqm.models.playlist.channel_descriptions.ChannelDescription.add_acquisition "iqm.models.playlist.channel_descriptions.ChannelDescription.add_acquisition") | Add an acquisition method to the table map if the configuration is unique. |
| [`add_instruction`](#iqm.models.playlist.channel_descriptions.ChannelDescription.add_instruction "iqm.models.playlist.channel_descriptions.ChannelDescription.add_instruction") | Add an instruction to the instruction table if the instruction is unique. |

add_instruction(*instruction*)  
Add an instruction to the instruction table if the instruction is unique.

If the instruction contains other instructions, those are also added if they are unique. If any of the instructions contain unique waveforms, those are also added to the waveform table.

Parameters:  
**instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")) – Instruction to be added

Returns:  
corresponding index to the instruction table

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

add_acquisition(*acquisition*)  
Add an acquisition method to the table map if the configuration is unique.

If it contains unique waveforms, those are added to the waveform table.

Parameters:  
**acquisition** ([*AcquisitionMethod*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod")) – Configuration to be added.

Returns:  
Corresponding index to the acquisition table.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
