> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2454c1a606cc1dbec05d5f186ec4202f22085c3d793113dc1bae380a104d19d0.

# iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor

iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor(*n_arr*, *frequencies*, *pulse_duration*)  
Evaluate Fourier transforms of cosine basis functions for given basis function indices and frequencies.

The nth cosine basis function is given by \\g_n(t) = 1 - \cos(2 \pi n t/t_p)\\ defined on the interval \\\[0, t_p\]\\, where \\t_p\\ is the pulse duration. The Fourier transform can be analytically evaluated, see Eq. (A7) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\]. We evaluate the Fourier transform for the basis function indices given by `n_arr` and for the frequencies given by `frequency_arr`. We store the Fourier transforms as a tensor of dimension `1+dim(frequency_arr)`, such that the first dimension corresponds to the basis function indices, and the following dimensions to those of `frequency_arr`. Thus, the Fourier transform is evaluated essentially for the cartesian product of `n_arr` and `frequency_arr`.

Parameters:  
- **n_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 1d array of basis function indices, running typically from 1 to N, where N is the number of considered basis functions

- **frequencies** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – N-dimensional array of frequencies (in Hz), at which the Fourier transform is evaluated. For the computation of FAST DRAG coefficients, `N=2`.

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration (in s), without zero padding.

Returns:  
Array containing the Fourier transform as a tensor with a shape `(len(n_arr), *frequency_arr.shape)`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
