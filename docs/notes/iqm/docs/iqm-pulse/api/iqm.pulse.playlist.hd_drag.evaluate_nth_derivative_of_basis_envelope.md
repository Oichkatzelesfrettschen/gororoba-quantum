> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a9315b19b3b5c657cecdc72db618602d81903c6a387983228dfabf0d1454175.

# iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope

iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope(*t_arr*, *pulse_duration*, *cosine_coefs_arr*, *n*)  
Evaluate nth derivative of the basis envelope for HD DRAG based on a cosine series.

The basis envelope is given by \\g(t) = \sum\_{k=1}^{K+1} d_k (1 - \cos(2\pi k t/t_p + k\pi))\\, where the pulse is defined on the interval \\t \in \[-t_p/2, t_p/2\]\\. The returned derivatives are normalized via multiplication by \\((t_p/(2\pi))^n\\, where \\n\\ is the order of the derivative.

Parameters:  
- **t_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of time points, at which the function is to be evaluated

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration in the same units as t_arr

- **cosine_coefs_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Coefficients of the cosine terms in the basis envelope

- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – order of derivative

Returns:  
Array containing the nth derivative of the basis envelope evaluated at `t_arr`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
