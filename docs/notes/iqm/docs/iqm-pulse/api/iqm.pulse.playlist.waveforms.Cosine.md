> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Cosine.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Cosine.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ebe67699524b07cdc2a80d08ac529b3aeeb8b1cf887772a1432e5a2b3543f9d6.

# Cosine

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.Cosine(*n_samples*, *frequency*, *phase=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Periodic sinusoidal waveform which defaults to cosine.

The use case for this waveform is to do manual modulation of other waveforms.

\\f(t) = \cos(2\pi \\ f \\ t + \phi)\\

where \\f\\ is the frequency, and \\\phi\\ the phase of the wave.

Parameters:  
- **frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – frequency of the wave, in units of inverse sampling window duration

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – phase of the wave, in radians

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Attributes

|             |                                               |
|-------------|-----------------------------------------------|
| `phase`     |                                               |
| `frequency` |                                               |
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.waveforms.Cosine.non_timelike_attributes "iqm.pulse.playlist.waveforms.Cosine.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.Cosine](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-3900676d076eefb54302ccbc74c0a7af76a14821.png)
