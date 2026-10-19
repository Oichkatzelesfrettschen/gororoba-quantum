> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFallFlex.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFallFlex.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e65794dd130e31fbe552a4e4a760519f6c6d160fa19715c8dc64911d8606a74b.

# CosineFallFlex

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.CosineFallFlex(*n_samples*, *rise_time*, *full_width*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Cosine fall waveform with an extra duration buffer.

The waveform is a piecewise function: (flat plateau, cosine fall, buffer), where:

- buffer is a ‘leftover’ constant signal with amplitude = 0, generally with duration of `duration - full_width`

- cosine fall is a cosine fall pulse with a duration of `rise_time`

- flat plateau is a constant signal with amplitude = 1, generally with duration of `full_width - rise_time`

Parameters:  
- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rise time of the waveform

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – combined duration of the cosine fall time and the flat plateau

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Error is raised if full_width or rise_time is more than duration

Attributes

|              |                                               |
|--------------|-----------------------------------------------|
| `rise_time`  |                                               |
| `full_width` |                                               |
| `n_samples`  | Requested number of samples for the waveform. |

Methods

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.CosineFallFlex](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-be52da342414bd942a8b227f490199bffd4f4347.png)
