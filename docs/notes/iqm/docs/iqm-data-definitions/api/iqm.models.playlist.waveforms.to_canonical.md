> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.to_canonical.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.to_canonical.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 459263501f6f60ba1621397ddb78f8026d1b282b7ece44e992265807260503be.

# iqm.models.playlist.waveforms.to_canonical

iqm.models.playlist.waveforms.to_canonical(*waveform*)  
Convert the waveform into a canonical version of itself, e.g. for serialization.

Canonical waveforms are returned as is, non-canonical waveforms are sampled.

Returns:  
canonical version of the waveform

Parameters:  
**waveform** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform"))

Return type:  
[*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")
