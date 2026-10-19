> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.round_duration_to_granularity_samples.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.round_duration_to_granularity_samples.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 07d79f39ff021b7bce772f059863c30686ff9a9438723f5161e8cc1bc0f6209e.

# iqm.pulse.playlist.channel.round_duration_to_granularity_samples

iqm.pulse.playlist.channel.round_duration_to_granularity_samples(*channels*, *duration*, *round_up=False*, *force_min_duration=False*)  
Round a time duration to the least common multiple of the granularities of the given channels.

Note

Assumes that all the given control channels have the same sample rate.

Parameters:  
- **channels** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – all these channels must be able to handle the rounded duration

- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time duration in s

- **round_up** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to round the duration up, or to the closest granularity

- **force_min_duration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to force the duration to be at least the largest `instruction_duration_min` of `channels`

Returns:  
`duration` rounded to common channel granularity, in samples

Return type:  
[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
