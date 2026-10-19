> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Chirp.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Chirp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6bdbd15df6bbff29f1fd26643f013e095962bdea2a30d10de6d9a034c6cfcaac.

# Chirp

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.Chirp(*n_samples*, *freq_start*, *freq_stop*, *alpha=0.05*, *phase=0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Linear chirp.

> \\f(t) = A \\ \omega\[\alpha, N\] \\ \cos(2\pi \int (f\_{0} + (f\_{1} - f\_{0}) t) \\ \mathrm{d}t),\\

where \\\omega\[\alpha, N\]\\ is a cosine-tapered window. For \\\alpha = 1\\ it becomes rectangular, and for \\\alpha = 0\\ it becomes a Hann (or raised cosine) window.

The chirp pulse is valued inside the Nyquist zone, such that \\f\_{0}\\ and \\f\_{1}\\ are constrained in the range \\\[-0.5, 0.5\]\\.

Parameters:  
- **freq_start** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Initial frequency of the chirp waveform in the Nyquist zone.

- **freq_stop** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Final frequency of the chirp waveform in the Nyquist zone.

- **alpha** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Alpha parameter of the cosine-tapered window. Defaults to 0.05.

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Phase of the waveform. Defaults to 0

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Attributes

|              |                                               |
|--------------|-----------------------------------------------|
| `alpha`      |                                               |
| `phase`      |                                               |
| `freq_start` |                                               |
| `freq_stop`  |                                               |
| `n_samples`  | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.waveforms.Chirp.non_timelike_attributes "iqm.pulse.playlist.waveforms.Chirp.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.Chirp](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-981727b472146a2c20b74c23817cae7e79677b6e.png)
