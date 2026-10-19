> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ProbeChannelProperties.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ProbeChannelProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c1ee74a31dcde483537c41ac7af31c9779841d6da80d96fb5d48eded00dced9a.

# ProbeChannelProperties

Module: [`iqm.pulse.playlist.channel`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html#module-iqm.pulse.playlist.channel "iqm.pulse.playlist.channel")

*class* iqm.pulse.playlist.channel.ProbeChannelProperties(*sample_rate*, *instruction_duration_granularity*, *instruction_duration_min*, *compatible_instructions=\<factory\>*, *is_iq=False*, *is_virtual=False*, *blocks_component=True*, *center_frequency=0.0*, *integration_start_dead_time=0*, *integration_stop_dead_time=0*)  
Bases: [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")

`ChannelProperties` for probe line channels.

Attributes

|  |  |
|----|----|
| [`center_frequency`](#iqm.pulse.playlist.channel.ProbeChannelProperties.center_frequency "iqm.pulse.playlist.channel.ProbeChannelProperties.center_frequency") | Center frequency for the channel. |
| [`integration_start_dead_time`](#iqm.pulse.playlist.channel.ProbeChannelProperties.integration_start_dead_time "iqm.pulse.playlist.channel.ProbeChannelProperties.integration_start_dead_time") | Dead time samples before integration. |
| [`integration_stop_dead_time`](#iqm.pulse.playlist.channel.ProbeChannelProperties.integration_stop_dead_time "iqm.pulse.playlist.channel.ProbeChannelProperties.integration_stop_dead_time") | Dead time samples after integration. |
| `sample_rate` | sample rate of the instrument responsible for the channel (in Hz) |
| `instruction_duration_granularity` | all instruction durations on this channel must be multiples of this granularity (in samples) |
| `instruction_duration_min` | all instruction durations on this channel must at least this long (in samples) |
| `compatible_instructions` | instruction types that are allowed on this channel |

Methods

Parameters:  
- **sample_rate** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **instruction_duration_granularity** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **instruction_duration_min** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **compatible_instructions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\],* *...\]*)

- **is_iq** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **is_virtual** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **blocks_component** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **center_frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **integration_start_dead_time** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **integration_stop_dead_time** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

center_frequency*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Center frequency for the channel.

integration_start_dead_time*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
Dead time samples before integration.

integration_stop_dead_time*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
Dead time samples after integration.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.channel.ProbeChannelProperties](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8ea9c89aa524ad05b8a3b65da733ef8928227ce4.png)
