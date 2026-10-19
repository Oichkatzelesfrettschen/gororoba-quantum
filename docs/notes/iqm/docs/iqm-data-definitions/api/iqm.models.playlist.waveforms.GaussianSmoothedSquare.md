> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianSmoothedSquare.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianSmoothedSquare.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b6ea6244905ec32cb8bc33fba31e6b1d37964ff096b3294ac62598cb247a8213.

# GaussianSmoothedSquare

*class* iqm.models.playlist.waveforms.GaussianSmoothedSquare(*n_samples*, *square_width*, *gaussian_sigma*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Convolution of a square pulse and a gaussian pulse.

One can think of it as a square pulse smoothed with a gaussian one, or vice versa.

\\f(t) = \frac{1}{2} \left\[ \text{erf}\left(\frac{t - (c - s / 2)}{\sqrt{2 \sigma^2}}\right) - \text{erf}\left(\frac{t - (c + s / 2)}{\sqrt{2 \sigma^2}}\right) \right\],\\

where \\\text{erf}\\ is the error function, \\c\\ is `center_offset`, \\s\\ is `square_width`, and \\\sigma\\ is `gaussian_sigma`.

Its values are in \\(0, 1)\\.

Parameters:  
- **square_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – square pulse width

- **gaussian_sigma** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – gaussian pulse standard deviation

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The waveform is centered at this offset from the midpoint of the sampling window.

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|                  |                                               |
|------------------|-----------------------------------------------|
| `center_offset`  |                                               |
| `square_width`   |                                               |
| `gaussian_sigma` |                                               |
| `n_samples`      | Requested number of samples for the waveform. |

Methods
