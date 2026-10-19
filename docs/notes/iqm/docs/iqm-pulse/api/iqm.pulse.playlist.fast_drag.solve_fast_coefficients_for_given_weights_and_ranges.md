> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a3c63aa044f8f4802029cd0b5baf96faa22a04e94909095f63adceb011de8d1d.

# iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges

iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges(*number_of_cosines*, *pulse_duration*, *weights_tuple*, *suppressed_freq_ranges_2d_tuple*, *n_points_for_integration=60*)  
Solve for optimal coefficients of the basis functions in a FAST DRAG pulse.

Computes the optimal coefficients \\\\c_n\\\_{n=1}^N\\ for a FAST DRAG pulse with \\N\\ basis functions such that the pulse spectrum is suppressed across the given frequency ranges according to the provided weights. The computation is based on Eqs. (A5), (A7), (A12) and (A13) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\].

Note that this function essentially computes the mapping from frequency-domain parameters of a FAST DRAG pulse to time-domain parameters.

The results must be cached to allow efficient generation of playlists containing a large number of pulses with same parameters, as in RB.

Parameters:  
- **number_of_cosines** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of cosine basis functions used in the FAST DRAG pulse

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration (in s) without zero padding.

- **weights_tuple** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *...\]*) – 1d tuple of weights for each suppressed frequency interval used in the objective function

- **suppressed_freq_ranges_2d_tuple** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *...\],* *...\]*) – 2d tuple describing the frequency ranges (in Hz), over which we want to suppress the Fourier transform. Each element of the outer tuple should be a tuple of two floats, the first setting the starting frequency for the given range and the second setting the ending frequency for the given range.

- **n_points_for_integration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of points at which the integrand is evaluated for each interval. At least 50 points are recommended for the numerical approximation error to be low.

Returns:  
Coefficients of the basis functions as a 1d array.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
