> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 db24f31eb8ddef9b8adff697a230d02457253eaaea3376d2fabe92f077164ded.

# waveforms

Waveform definitions.

Full path: iqm.models.playlist.waveforms

Module Attributes

|  |  |
|----|----|
| [`CanonicalWaveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CanonicalWaveform.html#iqm.models.playlist.waveforms.CanonicalWaveform "iqm.models.playlist.waveforms.CanonicalWaveform") | Alias for Waveform to emphasize the fact the waveforms defined in this module have their own serialisation. |

Functions

|  |  |
|----|----|
| [`is_canonical`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.is_canonical.html#iqm.models.playlist.waveforms.is_canonical "iqm.models.playlist.waveforms.is_canonical")(waveform) | Returns `True` if `waveform` is a canonical waveform else `False` |
| [`register_canonical_waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.register_canonical_waveform.html#iqm.models.playlist.waveforms.register_canonical_waveform "iqm.models.playlist.waveforms.register_canonical_waveform")(cls) | Decorator for making a Waveform into a canonical waveform. |
| [`to_canonical`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.to_canonical.html#iqm.models.playlist.waveforms.to_canonical "iqm.models.playlist.waveforms.to_canonical")(waveform) | Convert the waveform into a canonical version of itself, e.g. for serialization. |

Classes

|  |  |
|----|----|
| [`CanonicalWaveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CanonicalWaveform.html#iqm.models.playlist.waveforms.CanonicalWaveform "iqm.models.playlist.waveforms.CanonicalWaveform") | Alias for Waveform to emphasize the fact the waveforms defined in this module have their own serialisation. |
| [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "iqm.models.playlist.waveforms.Constant") | Constant waveform. |
| [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "iqm.models.playlist.waveforms.CosineRiseFall") | Waveform that has a sinusoidal rise and fall, and a constant part in between. |
| [`CosineRiseFallDerivative`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFallDerivative.html#iqm.models.playlist.waveforms.CosineRiseFallDerivative "iqm.models.playlist.waveforms.CosineRiseFallDerivative") | Derivative of a waveform that has a sinusoidal rise and fall, and a constant part in between. |
| [`Gaussian`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Gaussian.html#iqm.models.playlist.waveforms.Gaussian "iqm.models.playlist.waveforms.Gaussian") | Gaussian pulse. |
| [`GaussianDerivative`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianDerivative.html#iqm.models.playlist.waveforms.GaussianDerivative "iqm.models.playlist.waveforms.GaussianDerivative") | Derivative of a gaussian pulse. |
| [`GaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianSmoothedSquare.html#iqm.models.playlist.waveforms.GaussianSmoothedSquare "iqm.models.playlist.waveforms.GaussianSmoothedSquare") | Convolution of a square pulse and a gaussian pulse. |
| [`ModulatedCosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.ModulatedCosineRiseFall.html#iqm.models.playlist.waveforms.ModulatedCosineRiseFall "iqm.models.playlist.waveforms.ModulatedCosineRiseFall") | Modulated Cosine Rise Fall waveform. |
| [`Samples`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Samples.html#iqm.models.playlist.waveforms.Samples "iqm.models.playlist.waveforms.Samples") | Custom pre-sampled waveform. |
| [`Slepian`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Slepian.html#iqm.models.playlist.waveforms.Slepian "iqm.models.playlist.waveforms.Slepian") | Slepian waveform, which minimizes non-adiabatic errors during a gate. |
| [`TruncatedGaussian`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussian.html#iqm.models.playlist.waveforms.TruncatedGaussian "iqm.models.playlist.waveforms.TruncatedGaussian") | Gaussian pulse, where the decaying tails are removed by offsetting, truncating, and then rescaling the pulse slightly, so that the resulting waveform is zero where the original waveform reaches the threshold level, and beyond, while still reaching the same maximal pulse amplitude. |
| [`TruncatedGaussianDerivative`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianDerivative.html#iqm.models.playlist.waveforms.TruncatedGaussianDerivative "iqm.models.playlist.waveforms.TruncatedGaussianDerivative") | Derivative of a gaussian pulse, where the decaying tails are removed by offsetting, truncating, and then rescaling the pulse slightly, so that the resulting waveform is zero where the original waveform reaches the threshold level, and beyond, while still reaching the same maximal pulse amplitude. |
| [`TruncatedGaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare.html#iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare "iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare") | Convolution of a square pulse and a gaussian pulse, offset and truncated so that it has finite support. |
| [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform") | Describes the normalized shape of a real-valued control pulse. |
