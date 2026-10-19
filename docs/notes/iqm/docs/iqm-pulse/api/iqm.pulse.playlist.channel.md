> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6450706016ebe6d9933e86c8dde79a28a407ac56d1419a3eca5901b3bcd0ae7c.

# channel

Full path: iqm.pulse.playlist.channel

Control channel properties.

Functions

|  |  |
|----|----|
| [`round_duration_to_granularity_samples`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.round_duration_to_granularity_samples.html#iqm.pulse.playlist.channel.round_duration_to_granularity_samples "iqm.pulse.playlist.channel.round_duration_to_granularity_samples")(...\[, ...\]) | Round a time duration to the least common multiple of the granularities of the given channels. |

Classes

|  |  |
|----|----|
| [`ChannelConfiguration`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelConfiguration.html#iqm.pulse.playlist.channel.ChannelConfiguration "iqm.pulse.playlist.channel.ChannelConfiguration") | Base class for configuring channels. |
| [`ChannelDescription`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelDescription.html#iqm.pulse.playlist.channel.ChannelDescription "iqm.pulse.playlist.channel.ChannelDescription") | Channel specific data, including tables for the instructions and waveforms used. |
| [`ChannelProperties`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties") | Defines the properties of a control or measurement channel. |
| [`IQChannelConfig`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.IQChannelConfig.html#iqm.pulse.playlist.channel.IQChannelConfig "iqm.pulse.playlist.channel.IQChannelConfig") | Requested configuration of an IQ channel. |
| [`ProbeChannelProperties`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ProbeChannelProperties.html#iqm.pulse.playlist.channel.ProbeChannelProperties "iqm.pulse.playlist.channel.ProbeChannelProperties") | `ChannelProperties` for probe line channels. |
| [`RealChannelConfig`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.RealChannelConfig.html#iqm.pulse.playlist.channel.RealChannelConfig "iqm.pulse.playlist.channel.RealChannelConfig") | Requested configuration of a real channel. |

Inheritance

![Inheritance diagram of iqm.pulse.playlist.channel](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-69a70890408429bc6c6e8d64bedfcaf0cef83800.png)
