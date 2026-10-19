> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ba1c2147cdba9f73f9d6d6382a09d19ef49acab568cb8f61b2df54113de7225c.

# TruncatedGaussianSmoothedSquare

*class* iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare(*n_samples*, *full_width*, *rise_time*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Convolution of a square pulse and a gaussian pulse, offset and truncated so that it has finite support.

One can think of it as a square pulse smoothed with a gaussian one, or vice versa. The decaying tails are removed by offsetting, truncating, and then rescaling the pulse slightly, so that the resulting waveform is zero where the original waveform reaches the threshold level, and beyond, while still reaching the same maximal pulse amplitude. Currently, the threshold is fixed at \\g_0 = 0.003\\.

\\g(t) = \frac{1}{2} \left\[ \text{erf}\left(\frac{t - (c - w / 2)}{\sqrt{2 \sigma^2}}\right) - \text{erf}\left(\frac{t - (c + w / 2)}{\sqrt{2 \sigma^2}}\right) \right\],\\

where \\\text{erf}\\ is the error function, \\c\\ is `center_offset`, \\w\\ is the square width, and \\\sigma\\ is the gaussian standard deviation.

We set

- \\w :=\\ `full_width` - `rise_time`

- \\\sigma :=\\ `rise_time` \\/ (\sqrt{8} \\ \text{erf}^{-1}(1 - 2 g_0))\\

The cutoff time \\t_c = c - w / 2 -\\ `rise_time` \\/ 2\\ marks the start of the rising segment. The waveform after offsetting, truncating and rescaling is given by

\\f(t) = \text{max}(g(t) - g_0, 0) / (1 - g_0).\\

where \\g_0\\ is the threshold level for the truncation. We have \\f(t_c) \approx 0\\, and the approximation is good if \\g_0 \< 0.1\\.

The values of the waveform are in \\\[0, 1\]\\.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the support of the pulse, from start of the rising to the end of the falling segment.

- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the rising and falling segments.

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
