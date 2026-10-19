> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.SuppressedPulse.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.SuppressedPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c2db831c055d8b3126d24a8ecf57643f2d49cc6a5084d0c378d8d91ea6d3a8b.

# SuppressedPulse

Module: [`iqm.pulse.playlist.fast_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.html#module-iqm.pulse.playlist.fast_drag "iqm.pulse.playlist.fast_drag")

*class* iqm.pulse.playlist.fast_drag.SuppressedPulse(*n_samples*, *full_width*, *coefficients*, *suppressed_frequencies*, *compute_coefs_from_frequencies*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)")

Base class for control pulses using a series expansion to suppress certain frequencies in its envelope spectrum.

The base class describes control pulses, in which the coefficients of the basis functions are chosen to suppress specific frequencies or frequency ranges in the frequency spectrum of the pulse envelope. Examples include FAST DRAG and HD DRAG.

The pulse argument `compute_coefs_from_frequencies` allows the user to choose whether the basis function coefficients are computed from `suppressed_frequencies` during the post-initialization of the pulse (thus, overriding any pre-computed values in `coefficients`), or if the (pre-computed) values in `coefficients` are directly used and `suppressed_frequencies` are neglected. The classes deriving from this base class should implement the post-initialization logic specific to the given pulse.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Full width of the pulse corresponding to the pulse duration with non-zero amplitude (in s).

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Pre-computed coefficients of the series expansion.

- **suppressed_frequencies** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Frequencies to be suppressed or center frequencies of intervals to be suppressed (in Hz).

- **compute_coefs_from_frequencies** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean value indicating whether we compute the coefficients from the suppressed frequencies or whether we use the pre-computed coefficients. If True, `suppressed_frequencies` are used to compute and override `coefficients` in the post-initialization. If False, pre-computed `coefficients` are used, and `suppressed_frequencies` are ignored.

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Attributes

|  |  |
|----|----|
| `full_width` |  |
| `coefficients` |  |
| `suppressed_frequencies` |  |
| `compute_coefs_from_frequencies` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

Inheritance

![Inheritance diagram of iqm.pulse.playlist.fast_drag.SuppressedPulse](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-4ab7af0cd4994971190bfdec21385a9b466bd568.png)
