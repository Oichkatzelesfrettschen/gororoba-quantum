> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelDescription.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelDescription.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 079cd1c00f73a9b4807398f300cf89d7d852eae054dc0daefeee617e4a39950b.

# ChannelDescription

Module: [`iqm.pulse.playlist.channel`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html#module-iqm.pulse.playlist.channel "iqm.pulse.playlist.channel")

*class* iqm.pulse.playlist.channel.ChannelDescription(*name*, *config*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Channel specific data, including tables for the instructions and waveforms used.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the controller handling the channel, also the name of the channel

- **config** ([*RealChannelConfig*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.RealChannelConfig.html#iqm.pulse.playlist.channel.RealChannelConfig "iqm.pulse.playlist.channel.RealChannelConfig")) – properties of the channel

- **instruction_table** – mapping of the instructions to be executed on this channel. Each instruction should be unique.

- **waveform_table** – Contains mapping of the waveforms to be executed on this channel. Each waveform should be unique.

Attributes

|                     |     |
|---------------------|-----|
| `name`              |     |
| `config`            |     |
| `instruction_table` |     |
| `waveform_table`    |     |

Methods

|  |  |
|----|----|
| [`add_instruction`](#iqm.pulse.playlist.channel.ChannelDescription.add_instruction "iqm.pulse.playlist.channel.ChannelDescription.add_instruction") | Add an instruction to the channel. |

add_instruction(*instruction*)  
Add an instruction to the channel.

Each unique instruction in a channel gets assigned an integer index that can be used to refer to it. If the instruction has associated `Waveform` s, they are indexed in a similar manner.

Parameters:  
**instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")) – instruction to be added

Returns:  
index of the instruction

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.playlist.channel.ChannelDescription](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-80c9faffab603beec0f745a44588bcf9dfdb60be.png)
