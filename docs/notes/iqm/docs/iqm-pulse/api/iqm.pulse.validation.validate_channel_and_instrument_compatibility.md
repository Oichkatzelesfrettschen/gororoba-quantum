> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_channel_and_instrument_compatibility.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.validate_channel_and_instrument_compatibility.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcbcd88040ac3cd3949f67fb0023bfc9c9a10613c5ac12e78afecb480acc2b39.

# iqm.pulse.validation.validate_channel_and_instrument_compatibility

iqm.pulse.validation.validate_channel_and_instrument_compatibility(*channel_description*, *device_constraints*)  
Validate that the given control channel and its contents are compatible with the instrument.

Checks the channel configuration and its contents against the controller/instrument hardware constraints.

The following requirements are validated:

1.  Channel sampling rate vs. instrument sampling rate.

2.  Only supported instructions are used.

3.  ConditionalInstruction has the same duration in every outcome.

4.  ReadoutTrigger duration is longer than the probe pulse in it.

5.  Instruction durations match instrument granularity.

6.  Instructions durations are at least the minimum number of samples for the instrument.

7.  Instruction durations match waveform lengths in IQ and RealPulses.

Parameters:  
- **channel_description** ([*ChannelDescription*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.channel_descriptions.ChannelDescription.html#iqm.models.playlist.channel_descriptions.ChannelDescription "(in IQM data definitions v3.1.0)")) – Channel config and its instruction table from a Playlist.

- **device_constraints** ([*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.channel_properties.channel_properties.ChannelProperties.html#iqm.models.channel_properties.channel_properties.ChannelProperties "(in IQM data definitions v3.1.0)")) – Hardware limitations of the control instrument.

Raises:  
**ValidationError** – Not compatible.

Return type:  
*None*
