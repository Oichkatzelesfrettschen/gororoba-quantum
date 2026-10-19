> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f79c15d701910a2e4301616516effb4e6d2806cdfad0d788658e592893bf10d.

# ChannelProperties

*class* iqm.models.channel_properties.channel_properties.ChannelProperties(*sampling_rate*, *instruction_duration_granularity*, *instruction_duration_min*, *compatible_instructions=\<factory\>*, *is_virtual=False*, *blocks_component=True*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Parent class of AWG and QA Channel properties that contains common attributes and methods.

Module: [`iqm.models.channel_properties.channel_properties`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.html#module-iqm.models.channel_properties.channel_properties "iqm.models.channel_properties.channel_properties")

Attributes

|  |  |
|----|----|
| [`blocks_component`](#iqm.models.channel_properties.channel_properties.ChannelProperties.blocks_component "iqm.models.channel_properties.channel_properties.ChannelProperties.blocks_component") | Whether content in this channel should block the entire component that it is associated with in the scheduling. |
| [`is_virtual`](#iqm.models.channel_properties.channel_properties.ChannelProperties.is_virtual "iqm.models.channel_properties.channel_properties.ChannelProperties.is_virtual") | Virtual channels are only used on the frontend side during compilation and scheduling. |
| [`sampling_rate`](#iqm.models.channel_properties.channel_properties.ChannelProperties.sampling_rate "iqm.models.channel_properties.channel_properties.ChannelProperties.sampling_rate") | Sample rate of the instrument responsible for the channel (in Hz). |
| [`instruction_duration_granularity`](#iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_granularity "iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_granularity") | All instruction durations on this channel must be multiples of this granularity (in samples). |
| [`instruction_duration_min`](#iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_min "iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_min") | All instruction durations on this channel must at least this long (in samples). |
| [`compatible_instructions`](#iqm.models.channel_properties.channel_properties.ChannelProperties.compatible_instructions "iqm.models.channel_properties.channel_properties.ChannelProperties.compatible_instructions") | Instruction types that are allowed on this channel. |

Methods

|  |  |
|----|----|
| [`duration_to_int_samples`](#iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_int_samples "iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_int_samples") | Convert a time duration to an integer number of samples at the channel sample rate. |
| [`duration_to_samples`](#iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_samples "iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_samples") | Convert a time duration to number of samples at the channel sample rate. |
| [`duration_to_seconds`](#iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_seconds "iqm.models.channel_properties.channel_properties.ChannelProperties.duration_to_seconds") | Convert a time duration in samples at the channel sample rate to seconds. |
| [`round_duration_to_granularity`](#iqm.models.channel_properties.channel_properties.ChannelProperties.round_duration_to_granularity "iqm.models.channel_properties.channel_properties.ChannelProperties.round_duration_to_granularity") | Round a time duration to the channel granularity. |

Parameters:  
- **sampling_rate** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **instruction_duration_granularity** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **instruction_duration_min** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **compatible_instructions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")*\],* *...\]*)

- **is_virtual** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **blocks_component** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

sampling_rate*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Sample rate of the instrument responsible for the channel (in Hz).

instruction_duration_granularity*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
All instruction durations on this channel must be multiples of this granularity (in samples).

instruction_duration_min*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
All instruction durations on this channel must at least this long (in samples).

compatible_instructions*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")\], ...\]*  
Instruction types that are allowed on this channel.

is_virtual*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
Virtual channels are only used on the frontend side during compilation and scheduling. They are removed from the `Schedule` before it is sent to Station Control. For example, virtual drive channels of computational resonators.

blocks_component*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
Whether content in this channel should block the entire component that it is associated with in the scheduling. Typically all physical channels should block their components, but certain virtual channels might not require this.

duration_to_samples(*duration*)  
Convert a time duration to number of samples at the channel sample rate.

Parameters:  
**duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

Returns:  
`duration` in samples

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

duration_to_seconds(*duration*)  
Convert a time duration in samples at the channel sample rate to seconds.

Parameters:  
**duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in samples

Returns:  
`duration` in seconds

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

duration_to_int_samples(*duration*, *message='Given duration'*, *check_min_samples=True*)  
Convert a time duration to an integer number of samples at the channel sample rate.

`duration` must be sufficiently close to an integer number of samples, and that number must be something the channel can handle.

Parameters:  
- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – message identifying the duration we are testing

- **check_min_samples** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, check that the output is at least [`instruction_duration_min`](#iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_min "iqm.models.channel_properties.channel_properties.ChannelProperties.instruction_duration_min").

Returns:  
`duration` as an integer number of samples

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `duration` is not close to an integer number of samples, or is otherwise unacceptable to the channel

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

round_duration_to_granularity(*duration*, *round_up=False*, *force_min_duration=False*)  
Round a time duration to the channel granularity.

Parameters:  
- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

- **round_up** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to round the durations up to the closest granularity

- **force_min_duration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to force the duration to be at least `self.instruction_duration_min` in seconds

Returns:  
`duration` rounded to channel granularity, in seconds

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
