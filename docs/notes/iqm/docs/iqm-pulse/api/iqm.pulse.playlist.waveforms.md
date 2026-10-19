> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a032a9561d7f81d044798b689a4bcf75fcec84b015a6472ecdbe496788fae9ad.

# waveforms

Full path: iqm.pulse.playlist.waveforms

Waveform definitions.

This module defines some waveforms that don’t have special serialization, and reimports waveforms that do from [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "(in IQM data definitions v3.1.0)"). See the link for documentation of waveforms that don’t appear here.

Classes

|  |  |
|----|----|
| [`Chirp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Chirp.html#iqm.pulse.playlist.waveforms.Chirp "iqm.pulse.playlist.waveforms.Chirp") | Linear chirp. |
| [`ChirpImag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.ChirpImag.html#iqm.pulse.playlist.waveforms.ChirpImag "iqm.pulse.playlist.waveforms.ChirpImag") | Imaginary part of the linear chirp, which sets the phase to \$-pi/2\$. |
| [`Cosine`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Cosine.html#iqm.pulse.playlist.waveforms.Cosine "iqm.pulse.playlist.waveforms.Cosine") | Periodic sinusoidal waveform which defaults to cosine. |
| [`CosineFall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFall.html#iqm.pulse.playlist.waveforms.CosineFall "iqm.pulse.playlist.waveforms.CosineFall") | Cosine fall waveform. |
| [`CosineFallFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFallFlex.html#iqm.pulse.playlist.waveforms.CosineFallFlex "iqm.pulse.playlist.waveforms.CosineFallFlex") | Cosine fall waveform with an extra duration buffer. |
| [`CosineRise`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRise.html#iqm.pulse.playlist.waveforms.CosineRise "iqm.pulse.playlist.waveforms.CosineRise") | Cosine rise waveform. |
| [`CosineRiseFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRiseFlex.html#iqm.pulse.playlist.waveforms.CosineRiseFlex "iqm.pulse.playlist.waveforms.CosineRiseFlex") | Cosine Rise waveform with an extra duration buffer. |
| [`PiecewiseConstant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PiecewiseConstant.html#iqm.pulse.playlist.waveforms.PiecewiseConstant "iqm.pulse.playlist.waveforms.PiecewiseConstant") | Piecewise constant waveform. |
| [`PolynomialCosine`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PolynomialCosine.html#iqm.pulse.playlist.waveforms.PolynomialCosine "iqm.pulse.playlist.waveforms.PolynomialCosine") | Polynomial of a periodic sinusoidal waveform which defaults to cosine. |

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-7e8a158b27693c90eff3bde3b92085c3181e6bd3.png)
