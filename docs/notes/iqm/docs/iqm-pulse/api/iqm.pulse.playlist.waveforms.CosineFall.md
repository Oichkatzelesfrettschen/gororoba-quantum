> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFall.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7f0d3dbee2d5cf919a56bf5c039d63e7a3008d6a1d9274e437854162044f5c71.

# CosineFall

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.CosineFall(*n_samples*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Cosine fall waveform.

This waveform assumes that during its duration, the only thing occurring is signal falling to 0. The waveform is made for pairing with ‘Constant’ waveform to enable arbitrarily long pulses with smooth fall part. The fall time is equal to pulse duration.

Attributes

|             |                                               |
|-------------|-----------------------------------------------|
| `n_samples` | Requested number of samples for the waveform. |

Methods

Parameters:  
**n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.CosineFall](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-38c82377c5b1e94dc4b2f0eb23d180ef36897e14.png)
