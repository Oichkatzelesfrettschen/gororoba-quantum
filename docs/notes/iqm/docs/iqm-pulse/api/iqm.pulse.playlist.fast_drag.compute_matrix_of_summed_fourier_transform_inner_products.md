> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7cfde74597396c148ad4c020721a814dc4a45a0da4b0b14e1a0e1880618b43c0.

# iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products

iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products(*n_arr*, *weights*, *suppressed_freq_ranges_2darr*, *pulse_duration*, *time_scaling_factor*, *n_points_for_integration=60*)  
Evaluate matrix \\A\\ defined in Eq. (5) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\].

The matrix element \\A\_{nm}\\ is defined as

\\A\_{nm} = \sum\_{j=1}^k w_j \int\_{f\_{l,j}}^{f\_{h,j}} \hat{g}\_n(f) \hat{g}\_m(f)^\* \mathrm{d} f,\\

where n,m are the row and column indices starting from 1 and extending to \\N\\ denoting the number of basis functions, \\f\_{l,j}\\ and \\f\_{h,j}\\ denote the starting and ending frequency of the j’th frequency range to suppress, \\\hat{g}\_n(f)\\ denotes the Fourier transform of \\g_n(f) = 1 - \cos(2 \pi n t/t_p)\\ with \\t_p\\ being the pulse duration.

Importantly, the computations are fully vectorized for fast evaluation.

Parameters:  
- **n_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 1d array containing indices of basis functions used in the series expansion, typically ranging from 1 to N

- **weights** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 1d array of weights corresponding to the suppressed frequency ranges

- **suppressed_freq_ranges_2darr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2d array describing the frequency ranges (in Hz), over which we want to suppress the Fourier transform. The array should have two columns, the first giving the starting frequency for each range and the second giving the ending frequency for each range. Note that frequencies will be symmetrically suppressed around the center frequency.

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration (in s) without zero padding.

- **time_scaling_factor** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Scaling factor for time to avoid excessively large or small values in the matrix. Scaling factor of frequency is obtained as the inverse.

- **n_points_for_integration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of points at which the integrand is evaluated for each interval. At least 50 points are recommended for the numerical approximation error to be low.

Returns:  
2d array representing the `A` matrix with dimensions `(len(n_arr), len(n_arr))`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
