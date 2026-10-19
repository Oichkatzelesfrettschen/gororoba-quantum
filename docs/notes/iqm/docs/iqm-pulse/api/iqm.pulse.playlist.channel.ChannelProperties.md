> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d3ac43d241e2ebbdfcfe108610e9f9e8736793e312fcaa4c1f88c23685a67af3.

# ChannelProperties

Module: [`iqm.pulse.playlist.channel`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html#module-iqm.pulse.playlist.channel "iqm.pulse.playlist.channel")

*class* iqm.pulse.playlist.channel.ChannelProperties(*sample_rate*, *instruction_duration_granularity*, *instruction_duration_min*, *compatible_instructions=\<factory\>*, *is_iq=False*, *is_virtual=False*, *blocks_component=True*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Defines the properties of a control or measurement channel.

All ZI instruments (HDAWG, UHFQA, SHFSG, SHFQA) can handle control pulses and waits where the number of samples is `32 + n * 16`, where `n in {0, 1, 2, ...}`.

Each programmable controller in Station Control has an associated channel.

Attributes

|  |  |
|----|----|
| [`blocks_component`](#iqm.pulse.playlist.channel.ChannelProperties.blocks_component "iqm.pulse.playlist.channel.ChannelProperties.blocks_component") | Whether content in this channel should block the entire component that it is associated with in the scheduling. |
| [`is_iq`](#iqm.pulse.playlist.channel.ChannelProperties.is_iq "iqm.pulse.playlist.channel.ChannelProperties.is_iq") | HACK, True iff this is an IQ channel. |
| [`is_virtual`](#iqm.pulse.playlist.channel.ChannelProperties.is_virtual "iqm.pulse.playlist.channel.ChannelProperties.is_virtual") | Virtual channels are only used on the frontend side during compilation and scheduling. |
| [`sample_rate`](#iqm.pulse.playlist.channel.ChannelProperties.sample_rate "iqm.pulse.playlist.channel.ChannelProperties.sample_rate") | sample rate of the instrument responsible for the channel (in Hz) |
| [`instruction_duration_granularity`](#iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_granularity "iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_granularity") | all instruction durations on this channel must be multiples of this granularity (in samples) |
| [`instruction_duration_min`](#iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min "iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min") | all instruction durations on this channel must at least this long (in samples) |
| [`compatible_instructions`](#iqm.pulse.playlist.channel.ChannelProperties.compatible_instructions "iqm.pulse.playlist.channel.ChannelProperties.compatible_instructions") | instruction types that are allowed on this channel |

Methods

|  |  |
|----|----|
| [`duration_to_int_samples`](#iqm.pulse.playlist.channel.ChannelProperties.duration_to_int_samples "iqm.pulse.playlist.channel.ChannelProperties.duration_to_int_samples") | Convert a time duration to an integer number of samples at the channel sample rate. |
| [`duration_to_samples`](#iqm.pulse.playlist.channel.ChannelProperties.duration_to_samples "iqm.pulse.playlist.channel.ChannelProperties.duration_to_samples") | Convert a time duration to number of samples at the channel sample rate. |
| [`duration_to_seconds`](#iqm.pulse.playlist.channel.ChannelProperties.duration_to_seconds "iqm.pulse.playlist.channel.ChannelProperties.duration_to_seconds") | Convert a time duration in samples at the channel sample rate to seconds. |
| [`round_duration_to_granularity`](#iqm.pulse.playlist.channel.ChannelProperties.round_duration_to_granularity "iqm.pulse.playlist.channel.ChannelProperties.round_duration_to_granularity") | Round a time duration to the channel granularity. |

Parameters:  
- **sample_rate** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **instruction_duration_granularity** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **instruction_duration_min** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **compatible_instructions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*\],* *...\]*)

- **is_iq** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **is_virtual** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **blocks_component** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

sample_rate*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
sample rate of the instrument responsible for the channel (in Hz)

instruction_duration_granularity*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
all instruction durations on this channel must be multiples of this granularity (in samples)

instruction_duration_min*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
all instruction durations on this channel must at least this long (in samples)

compatible_instructions*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")\], ...\]*  
instruction types that are allowed on this channel

is_iq*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
HACK, True iff this is an IQ channel. TODO do better

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
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

duration_to_seconds(*duration*)  
Convert a time duration in samples at the channel sample rate to seconds.

Parameters:  
**duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in samples

Returns:  
`duration` in seconds

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

duration_to_int_samples(*duration*, *message='Given duration'*, *check_min_samples=True*)  
Convert a time duration to an integer number of samples at the channel sample rate.

`duration` must be sufficiently close to an integer number of samples, and that number must be something the channel can handle.

Parameters:  
- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – message identifying the duration we are testing

- **check_min_samples** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, check that the output is at least [`instruction_duration_min`](#iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min "iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min").

Returns:  
`duration` as an integer number of samples

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `duration` is not close to an integer number of samples, or is otherwise unacceptable to the channel

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

round_duration_to_granularity(*duration*, *round_up=False*, *force_min_duration=False*)  
Round a time duration to the channel granularity.

Parameters:  
- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

- **round_up** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to round the durations up, or to the closest granularity

- **force_min_duration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to force the duration to be at least [`instruction_duration_min`](#iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min "iqm.pulse.playlist.channel.ChannelProperties.instruction_duration_min")

Returns:  
`duration` rounded to channel granularity, in s

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.playlist.channel.ChannelProperties](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-4a2548e51c2acced67636dd8907e6e29e7da4934.png)
