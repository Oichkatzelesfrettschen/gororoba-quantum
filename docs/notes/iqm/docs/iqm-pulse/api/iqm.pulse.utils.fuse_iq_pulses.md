> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.fuse_iq_pulses.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.fuse_iq_pulses.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0412431347c5257de0122dfbe2aeccb3a2bf38388cc9b5f5a46e44135afcd4b4.

# iqm.pulse.utils.fuse_iq_pulses

iqm.pulse.utils.fuse_iq_pulses(*iq_pulses*)  
Fuse multiple IQPulses into one by concatenating the sampled waveforms.

Works by flushing `IQPulse.phase_increment` s to the front, updating the `IQPulse.phase` s, sampling the pulses, concatenating, normalizing the amplitudes, and putting the result into a new IQPulse instruction with a `phase_increment` that is a sum of the individual `phase_increment` s.

Additionally, to conserve waveform memory on the AWGs, we normalize the waveform phase by setting `IQPulse.phase` of the fused pulse to the flushed phase of the first pulse.

Parameters:  
**iq_pulses** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse")*\]*) – IQPulse instructions to fuse.

Returns:  
Fused IQPulse that behaves indentically to the sequence `iq_pulses` on an AWG.

Return type:  
[*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse")
