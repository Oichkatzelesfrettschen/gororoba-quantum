> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PiecewiseConstant.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PiecewiseConstant.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9dc06fc6a060a187798c3546c1cb0669fe08dc4f275c39f0aef326fda70aa655.

# PiecewiseConstant

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.PiecewiseConstant(*n_samples*, *changepoints*, *values*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Piecewise constant waveform.

The values are assumed to be in the range \\\[-1, 1\]\\, and the changepoints are assumed to be in the Nyquist-zone of the duration, i.e. in the range \[-duration/2, duration/2\]

Parameters:  
- **changepoints** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of the changepoints of the piecewise constant function.

- **values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of the values of the piecewise constant function.

- **changepoints.** (*Must have one more element than*)

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Attributes

|                |                                               |
|----------------|-----------------------------------------------|
| `changepoints` |                                               |
| `values`       |                                               |
| `n_samples`    | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.waveforms.PiecewiseConstant.non_timelike_attributes "iqm.pulse.playlist.waveforms.PiecewiseConstant.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.PiecewiseConstant](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6cc26007978c9235094094b31b450b209faace68.png)
