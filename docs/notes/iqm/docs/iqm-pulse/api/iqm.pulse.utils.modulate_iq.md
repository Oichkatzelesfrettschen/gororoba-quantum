> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.modulate_iq.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.modulate_iq.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7d6b67b20878c6c0f440798ef6280269b5758e40fa95ee72183ac59387df4a3e.

# iqm.pulse.utils.modulate_iq

iqm.pulse.utils.modulate_iq(*pulse*, *assert_ranges=False*)  
Sampled baseband waveform of an IQ pulse.

Note that `IQPulse.phase_increment` has no effect on the sampled waveform. The upconversion oscillator phase incrementation is a separate action performed by the AWG that also affects future IQPulses, and thus cannot be represented by an array of waveform samples. To replicate the effect of `pulse` on an AWG, one should first perform the increment and then play the returned samples.

Parameters:  
- **pulse** ([*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse")) – IQ pulse.

- **assert_ranges** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, check that the resulting waveform is in the range \[-1, 1\]. Small floating point artifacts are tolerated and clipped to the range.

Returns:  
The waveform of `pulse` as an array of complex-valued samples.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
