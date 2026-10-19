> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.InstructionType.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.channel_property_serializer.InstructionType.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4bc0916818f3a8242401de375fe41d9c2c222ed6839c691062efab3a2bd1bbb6.

# InstructionType

InstructionType*: [TypeAlias](https://docs.python.org/3.11/library/typing.html#typing.TypeAlias "(in Python v3.11)")* *= type\[iqm.models.playlist.instructions.VirtualRZ\] \| type\[iqm.models.playlist.instructions.ConditionalInstruction\] \| type\[iqm.models.playlist.instructions.Wait\] \| type\[iqm.models.playlist.instructions.RealPulse\] \| type\[iqm.models.playlist.instructions.IQPulse\] \| type\[iqm.models.playlist.instructions.ReadoutTrigger\] \| type\[iqm.models.playlist.instructions.MultiplexedIQPulse\]*  
One of the instruction classes that can appear in `ChannelProperties.compatible_instructions`.
