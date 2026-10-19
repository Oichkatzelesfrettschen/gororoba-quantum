> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragI.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragI.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 24f5447effff9bab5cbb8c53613ef51feef7111d8893183dc6f11a8d6fcc084b.

# HdDragI

Module: [`iqm.pulse.playlist.hd_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.html#module-iqm.pulse.playlist.hd_drag "iqm.pulse.playlist.hd_drag")

*class* iqm.pulse.playlist.hd_drag.HdDragI(*n_samples*, *full_width*, *coefficients*, *suppressed_frequencies*, *compute_coefs_from_frequencies*, *center_offset=0*)  
Bases: [`HdDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDrag.html#iqm.pulse.playlist.hd_drag.HdDrag "iqm.pulse.playlist.hd_drag.HdDrag")

I-component of the higher derivative (HD) drag pulse.

The I-component is defined according to Eq. (B1) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\] ,

\\I(t) = \sum\_{n=0}^{K} \beta\_{2n} g^{(2n)}(t),\\

where \\\\\beta\_{2n}\\\_{n=0}^K\\ are the coefficients of the derivative terms, \\K\\ is the number of suppressed frequencies, and \\g(t)\\ is the basis envelope given by

\\g(t) = \sum\_{k=1}^K d_k (1 - \cos(2 \pi k t/t_p + k\pi)),\\

where \\d_k\\ are pre-computed to ensure continuous derivatives up to order \\2K + 1\\, \\t_p\\ denotes the pulse duration, and the pulse is defined across \\t \in (-t_p/2, t_p/2)\\.

The sampled pulse is always normalized to have a maximum value slightly below 1.0.

Attributes

|  |  |
|----|----|
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

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.pulse.playlist.hd_drag.HdDragI](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-602cdef878bbeb1c2a4e682262c2397d8a729cae.png)
