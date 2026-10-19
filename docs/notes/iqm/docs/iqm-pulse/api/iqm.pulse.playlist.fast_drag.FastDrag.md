> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDrag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDrag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6f1ed50523614316176cedca45505c24b93ff865fb6869945708a44ab3194d52.

# FastDrag

Module: [`iqm.pulse.playlist.fast_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.html#module-iqm.pulse.playlist.fast_drag "iqm.pulse.playlist.fast_drag")

*class* iqm.pulse.playlist.fast_drag.FastDrag(*n_samples*, *full_width*, *coefficients*, *suppressed_frequencies*, *compute_coefs_from_frequencies*, *number_of_cos_terms*, *suppressed_interval_widths*, *weights*, *center_offset=0*)  
Bases: [`SuppressedPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.SuppressedPulse.html#iqm.pulse.playlist.fast_drag.SuppressedPulse "iqm.pulse.playlist.fast_drag.SuppressedPulse")

Base class for IQ components of the Fourier Ansatz Spectrum Tuning (FAST) DRAG pulse.

The FAST DRAG pulse shapes the I-envelope in the frequency domain to suppress specified frequency intervals according to given weights. Furthermore, the Q-envelope is obtained as a derivative of the I-envelope similarly to ordinary DRAG. This class represents a base class for an implementation using cosine functions as the I-envelope basis functions. See \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\] for more details on FAST DRAG.

Parameters:  
- **number_of_cos_terms** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of cosine terms in the Fourier series expression of the I-component

- **suppressed_interval_widths** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Widths of the suppressed frequency intervals (in Hz). The last element corresponds to the width of a potential cutoff interval.

- **weights** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Weights corresponding to the suppressed frequency intervals

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **suppressed_frequencies** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **compute_coefs_from_frequencies** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Attributes

|  |  |
|----|----|
| `center_offset` |  |
| `number_of_cos_terms` |  |
| `suppressed_interval_widths` |  |
| `weights` |  |
| `full_width` |  |
| `coefficients` |  |
| `suppressed_frequencies` |  |
| `compute_coefs_from_frequencies` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.pulse.playlist.fast_drag.FastDrag.non_timelike_attributes "iqm.pulse.playlist.fast_drag.FastDrag.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.fast_drag.FastDrag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6ffd49e9e84e6403d241a6c1dfef9e3a656bdbff.png)
