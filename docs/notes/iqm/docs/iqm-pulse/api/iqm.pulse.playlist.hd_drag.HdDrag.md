> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDrag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDrag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 682b424a16212690bb67c4c9827698130a71f7c704e7b4ebe17cbe3569e1d00c.

# HdDrag

Module: [`iqm.pulse.playlist.hd_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.html#module-iqm.pulse.playlist.hd_drag "iqm.pulse.playlist.hd_drag")

*class* iqm.pulse.playlist.hd_drag.HdDrag(*n_samples*, *full_width*, *coefficients*, *suppressed_frequencies*, *compute_coefs_from_frequencies*, *center_offset=0*)  
Bases: [`SuppressedPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.SuppressedPulse.html#iqm.pulse.playlist.fast_drag.SuppressedPulse "iqm.pulse.playlist.fast_drag.SuppressedPulse")

Base class for higher-derivative DRAG based on Eqs. (B1) and (B2) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\].

Base class for IQ components of the higher derivative (HD) drag pulse. Depending on the value of `compute_coefs_from_frequencies`, we compute the coefficients from the suppressed frequencies during the post-initialization or use pre-computed coefficients of the derivative terms (neglecting the suppressed frequencies). See `SuppressedPulse`.

Attributes

|  |  |
|----|----|
| `center_offset` |  |
| `full_width` |  |
| `coefficients` |  |
| `suppressed_frequencies` |  |
| `compute_coefs_from_frequencies` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.hd_drag.HdDrag.non_timelike_attributes "iqm.pulse.playlist.hd_drag.HdDrag.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

Parameters:  
- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **suppressed_frequencies** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **compute_coefs_from_frequencies** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.hd_drag.HdDrag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-bdd8b883fa2d6f009ef74e38abe8656c0bfb028f.png)
