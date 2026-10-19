> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianDerivative.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianDerivative.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d81b216ab9f78bc37f554f0c36fd24be0a1c97846c9c62b1b21b2ae9ae6b9ec6.

# GaussianDerivative

*class* iqm.models.playlist.waveforms.GaussianDerivative(*n_samples*, *sigma*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Derivative of a gaussian pulse.

Normalized so that values are in \\\[-1, 1\]\\. The normalization factor is \\\sigma \\ \sqrt{e}\\.

\\f(t) = - \sqrt{e} \frac{t - c}{\sigma} e^{-\frac{(t - c)^2}{2 \sigma^2}},\\

where \\c\\ is `center_offset`, and \\\sigma\\ is `sigma`.

Parameters:  
- **sigma** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – gaussian standard deviation

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – center offset

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|                 |                                               |
|-----------------|-----------------------------------------------|
| `center_offset` |                                               |
| `sigma`         |                                               |
| `n_samples`     | Requested number of samples for the waveform. |

Methods
