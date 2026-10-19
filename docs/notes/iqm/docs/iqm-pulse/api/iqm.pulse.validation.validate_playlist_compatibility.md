> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_playlist_compatibility.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_playlist_compatibility.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9b3836a2780e0f065c822103413c86f5389e8f8c29de7cd15d724ba921bf3464.

# iqm.pulse.validation.validate_playlist_compatibility

iqm.pulse.validation.validate_playlist_compatibility(*playlist*, *device_constraints*)  
Validate that the given playlist is compatible with the control instrument constraints.

Checks the channel configuration and its contents against the controller/instrument hardware constraints.

The following requirements are validated:

1.  Channel sampling rate vs. instrument sampling rate.

2.  Only supported instructions are used.

3.  `Instruction.validate()` passes.

4.  Instruction durations match instrument granularity.

5.  Instructions durations are at least the minimum number of samples for the instrument.

Parameters:  
- **playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")) – Instructions used on each channel, as well as the channel configurations.

- **device_constraints** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – Hardware limitations of the control instruments.

Raises:  
**ValidationError** – Not compatible.

Return type:  
*None*
