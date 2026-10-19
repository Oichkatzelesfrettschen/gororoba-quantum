> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRiseFlex.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRiseFlex.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ff1c8d95bfc7fe358df5b96917c4d22c3222b5ed81d4eb4ed9b9867f5bfca72a.

# CosineRiseFlex

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.CosineRiseFlex(*n_samples*, *rise_time*, *full_width*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Cosine Rise waveform with an extra duration buffer.

The waveform is a piecewise function: (buffer, cosine rise, flat plateau), where:

- buffer is a ‘leftover’ constant signal with amplitude = 0, with duration of `duration - full_width`

- cosine rise is a cosine rise pulse with a duration of `rise_time`

- flat plateau is a constant signal with amplitude = 1, with duration of `full_width - rise_time`

Parameters:  
- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rise time of the waveform

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – combined duration of the cosine rise time and the flat plateau

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

![Inheritance diagram of iqm.pulse.playlist.waveforms.CosineRiseFlex](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d4e100efc9fc0d244e489c88b1f4ab460708baf0.png)
