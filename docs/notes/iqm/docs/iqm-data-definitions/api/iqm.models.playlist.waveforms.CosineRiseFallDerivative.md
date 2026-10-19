> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFallDerivative.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFallDerivative.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fcd58baf90a5787554f4af77c01e71e13cc9b5bb1c9f3efd60a25e0030e4d294.

# CosineRiseFallDerivative

*class* iqm.models.playlist.waveforms.CosineRiseFallDerivative(*n_samples*, *full_width*, *rise_time*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Derivative of a waveform that has a sinusoidal rise and fall, and a constant part in between.

\\\begin{split}f(t) = \begin{cases} -\sin(\pi (t - c + p / 2) / r) & t - (c - p / 2) \in \[-r, 0\]\\ -\sin(\pi (t - c - p / 2) / r) & t - (c + p / 2) \in \[0, r\]\\ 0 & \text{otherwise} \end{cases}\end{split}\\

where \\c\\ is `center_offset`, \\r\\ is `rise_time`, and \\p\\ is the plateau width, calculated via \\p :=\\ `full_width` - 2 \* `rise_time`.

Its values are in \\\[-1, 1\]\\.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the support of the pulse, \>= 2 \* `rise_time`.

- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the sinusoidal rise (and fall) part of the waveform, \>= 0.

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The waveform is centered at this offset from the midpoint of the sampling window.

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|                 |                                               |
|-----------------|-----------------------------------------------|
| `center_offset` |                                               |
| `full_width`    |                                               |
| `rise_time`     |                                               |
| `n_samples`     | Requested number of samples for the waveform. |

Methods
