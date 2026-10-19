> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PolynomialCosine.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.PolynomialCosine.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5991dfe0576fe906213560f665fb7a7c8872ba0f3cf1534f925ee61892b2a412.

# PolynomialCosine

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.PolynomialCosine(*n_samples*, *frequency*, *coefficients*, *phase=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Polynomial of a periodic sinusoidal waveform which defaults to cosine.

\\f(t) = P(\cos(2\pi \\ f \\ t + \phi))\\

where \\P(x)\\ is a polynomial, \\f\\ is the frequency, and \\\phi\\ the phase of the wave.

Parameters:  
- **frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – frequency of the wave, in units of inverse sampling window duration

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – phase of the wave, in radians

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

Attributes

|                |                                               |
|----------------|-----------------------------------------------|
| `phase`        |                                               |
| `frequency`    |                                               |
| `coefficients` |                                               |
| `n_samples`    | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.waveforms.PolynomialCosine.non_timelike_attributes "iqm.pulse.playlist.waveforms.PolynomialCosine.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.PolynomialCosine](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e615cfe188dd0eb21a41984e1318be738a5c83ff.png)
