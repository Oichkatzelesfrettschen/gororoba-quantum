> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.AWGProperties.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.AWGProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 694698b2ace5afc56e6867fd06bd8b1b884bfae79e3bba34a17b4b701cffb1a6.

# AWGProperties

*class* iqm.models.channel_properties.channel_properties.AWGProperties(*sampling_rate*, *instruction_duration_granularity*, *instruction_duration_min*, *compatible_instructions=\<factory\>*, *is_virtual=False*, *blocks_component=True*, *\**, *fast_feedback_sources=\<factory\>*, *local_oscillator=False*, *mixer_correction=False*)  
Bases: [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "iqm.models.channel_properties.channel_properties.ChannelProperties")

Channel properties of an AWG channel.

Module: [`iqm.models.channel_properties.channel_properties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.html#module-iqm.models.channel_properties.channel_properties "iqm.models.channel_properties.channel_properties")

Attributes

|  |  |
|----|----|
| [`local_oscillator`](#iqm.models.channel_properties.channel_properties.AWGProperties.local_oscillator "iqm.models.channel_properties.channel_properties.AWGProperties.local_oscillator") | Whether this AWG contains a local oscillator or not. |
| [`mixer_correction`](#iqm.models.channel_properties.channel_properties.AWGProperties.mixer_correction "iqm.models.channel_properties.channel_properties.AWGProperties.mixer_correction") | Whether this AWG has mixer correction or not. |
| [`fast_feedback_sources`](#iqm.models.channel_properties.channel_properties.AWGProperties.fast_feedback_sources "iqm.models.channel_properties.channel_properties.AWGProperties.fast_feedback_sources") | Defines compatible fast feedback sources |
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

- **fast_feedback_sources** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **local_oscillator** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **mixer_correction** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

fast_feedback_sources*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Defines compatible fast feedback sources

local_oscillator*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
Whether this AWG contains a local oscillator or not.

mixer_correction*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
Whether this AWG has mixer correction or not.
