> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianDerivative.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianDerivative.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0073c7072c735613472760a040f30ae7cda647848bf0dbfa624f14c56c93928f.

# TruncatedGaussianDerivative

*class* iqm.models.playlist.waveforms.TruncatedGaussianDerivative(*n_samples*, *full_width*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Derivative of a gaussian pulse, where the decaying tails are removed by offsetting, truncating, and then rescaling the pulse slightly, so that the resulting waveform is zero where the original waveform reaches the threshold level, and beyond, while still reaching the same maximal pulse amplitude. Currently, the threshold is fixed at \\g_0 = 0.003\\.

Normalized so that values are in \\\[-1, 1\]\\. The normalization factor is \\\sigma \\ \sqrt{e}\\.

\\f(t) = - \sqrt{e} \frac{t - c}{\sigma} e^{-\frac{(t - c)^2}{2 \sigma^2}},\\

where \\c\\ is `center_offset`, and \\\sigma\\ is calculated via \\\sigma :=\\ `full_width` \\/ \sqrt{8 \text{ln}(1/g_0)}\\.

The waveform after offsetting, truncating and rescaling is given by

\\f(t) = \text{max}(g(t) - g_0, 0) / (1 - g_0).\\

where \\g_0\\ is the threshold level for the truncation.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the support of the pulse, \>= 0.

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The waveform is centered at this offset from the midpoint of the sampling window.

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|                 |                                               |
|-----------------|-----------------------------------------------|
| `center_offset` |                                               |
| `full_width`    |                                               |
| `n_samples`     | Requested number of samples for the waveform. |

Methods
