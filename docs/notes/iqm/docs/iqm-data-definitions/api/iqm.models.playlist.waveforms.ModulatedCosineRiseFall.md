> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.ModulatedCosineRiseFall.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.ModulatedCosineRiseFall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5d8bd2ccefdbb3ea6a2df912761231fef2e90653e9ca3288404f154c5bb51a71.

# ModulatedCosineRiseFall

*class* iqm.models.playlist.waveforms.ModulatedCosineRiseFall(*n_samples*, *full_width*, *rise_time*, *modulation_frequency=0.0*, *phase=0*, *center_offset=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Modulated Cosine Rise Fall waveform.

This waveform takes the waveform [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "iqm.models.playlist.waveforms.CosineRiseFall") and modulates it with a cosine signal which then has parameters `frequency` and `phase`, additional to the parameters `full_width`, `rise_time`, and `center_offset`, see description of [`TruncatedGaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare.html#iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare "iqm.models.playlist.waveforms.TruncatedGaussianSmoothedSquare") for further details.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Full width of the pulse, \>= 2 \* `rise_time`.

- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the sinusoidal rise (and fall) part of the waveform, \>= 0.

- **modulation_frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Modulation frequency.

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase of the modulation.

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The waveform is centered around this sampling window coordinate. If zero, the pulse is placed in the middle of the sampling window.

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|                        |                                               |
|------------------------|-----------------------------------------------|
| `center_offset`        |                                               |
| `modulation_frequency` |                                               |
| `phase`                |                                               |
| `full_width`           |                                               |
| `rise_time`            |                                               |
| `n_samples`            | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.models.playlist.waveforms.ModulatedCosineRiseFall.non_timelike_attributes "iqm.models.playlist.waveforms.ModulatedCosineRiseFall.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
