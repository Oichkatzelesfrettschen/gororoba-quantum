> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragI.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragI.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6e8cd16a90d6099f51055ede1e7545a1cf5dde628c72d985d301e6debcf53130.

# FastDragI

Module: [`iqm.pulse.playlist.fast_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.html#module-iqm.pulse.playlist.fast_drag "iqm.pulse.playlist.fast_drag")

*class* iqm.pulse.playlist.fast_drag.FastDragI(*n_samples*, *full_width*, *coefficients*, *suppressed_frequencies*, *compute_coefs_from_frequencies*, *number_of_cos_terms*, *suppressed_interval_widths*, *weights*, *center_offset=0*)  
Bases: [`FastDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDrag.html#iqm.pulse.playlist.fast_drag.FastDrag "iqm.pulse.playlist.fast_drag.FastDrag")

I-component of the Fourier Ansatz Spectrum Tuning (FAST) drag pulse.

The I-envelope is defined as

\\I(t) = \sum\_{n=1}^{N} c_n \[1 - \cos(2\pi n t/t_p + n\pi)\],\\

where \\N\\ is the number of cosine terms in the series, \\\\c_n\\\\ are the coefficients, and the pulse is defined on the interval \\t \in \[-t_p/2, t_p/2\]\\.

Attributes

|  |  |
|----|----|
| `number_of_cos_terms` |  |
| `suppressed_interval_widths` |  |
| `weights` |  |
| `full_width` |  |
| `coefficients` |  |
| `suppressed_frequencies` |  |
| `compute_coefs_from_frequencies` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

Parameters:  
- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **suppressed_frequencies** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **compute_coefs_from_frequencies** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **number_of_cos_terms** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **suppressed_interval_widths** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **weights** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.fast_drag.FastDragI](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d84edfac2decd2fb915a6c1cf958ed13a23b779a.png)
