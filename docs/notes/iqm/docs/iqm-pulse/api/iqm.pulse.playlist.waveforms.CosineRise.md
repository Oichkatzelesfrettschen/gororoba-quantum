> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRise.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRise.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 baca7b2b72b46c3d2dcb9756a8d1bd69d105209819ef1e1f7ba413e2fc065967.

# CosineRise

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.CosineRise(*n_samples*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Cosine rise waveform.

This waveform assumes that during its duration, the only thing happening is signal rising to the required amplitude. The waveform is made for pairing with ‘Constant’ waveform to enable arbitrarily long pulses with smooth rise part. The rise time is equal to pulse duration.

Attributes

|             |                                               |
|-------------|-----------------------------------------------|
| `n_samples` | Requested number of samples for the waveform. |

Methods

Parameters:  
**n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.CosineRise](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8aabd4e7f1635758050e499a3af02618f4a35c8f.png)
