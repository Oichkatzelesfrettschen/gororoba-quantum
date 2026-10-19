> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ReadoutProperties.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ReadoutProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0154dc8c927260386ac292ba62784931626af844b60a43417537126d691d9ca6.

# ReadoutProperties

*class* iqm.models.channel_properties.channel_properties.ReadoutProperties(*sampling_rate*, *instruction_duration_granularity*, *instruction_duration_min*, *compatible_instructions=\<factory\>*, *is_virtual=False*, *blocks_component=True*, *\**, *integration_start_dead_time*, *integration_stop_dead_time*)  
Bases: [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "iqm.models.channel_properties.channel_properties.ChannelProperties")

Channel properties of a QA channel.

Module: [`iqm.models.channel_properties.channel_properties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.html#module-iqm.models.channel_properties.channel_properties "iqm.models.channel_properties.channel_properties")

Attributes

|  |  |
|----|----|
| [`integration_start_dead_time`](#iqm.models.channel_properties.channel_properties.ReadoutProperties.integration_start_dead_time "iqm.models.channel_properties.channel_properties.ReadoutProperties.integration_start_dead_time") | Minimum delay for probe pulse entries inside a ReadoutTrigger in samples. |
| [`integration_stop_dead_time`](#iqm.models.channel_properties.channel_properties.ReadoutProperties.integration_stop_dead_time "iqm.models.channel_properties.channel_properties.ReadoutProperties.integration_stop_dead_time") | Minimum delay in samples after the last integrator has stopped, before a new ReadoutTrigger can be executed. |
| `sampling_rate` | Sample rate of the instrument responsible for the channel (in Hz). |
| `instruction_duration_granularity` | All instruction durations on this channel must be multiples of this granularity (in samples). |
| `instruction_duration_min` | All instruction durations on this channel must at least this long (in samples). |
| `compatible_instructions` | Instruction types that are allowed on this channel. |

Methods

Parameters:  
- **sampling_rate** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **instruction_duration_granularity** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **instruction_duration_min** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **compatible_instructions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")*\],* *...\]*)

- **is_virtual** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **blocks_component** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **integration_start_dead_time** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **integration_stop_dead_time** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

integration_start_dead_time*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Minimum delay for probe pulse entries inside a ReadoutTrigger in samples.

integration_stop_dead_time*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Minimum delay in samples after the last integrator has stopped, before a new ReadoutTrigger can be executed. This delay must be taken into account when calculating the duration of a ReadoutTrigger. The duration is the sum of:

> - This value,
>
> - The duration of the longest integration among the acquisitions in the ReadoutTrigger instruction,
>
> - The acquisition delay of the above integration.
