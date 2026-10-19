> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 140739b18dc00bfe64b00decb59d668e846d2f264409a2c42ac642e84da06f25.

# iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope

iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope(*t_arr*, *pulse_duration*, *derivative_coefs_arr*, *cosine_coefs_arr*)  
Evaluate Q-envelope of HD DRAG given the coefficients of the derivative terms and the cosine terms.

The Q-envelope is defined as \\Q(t) = \sum\_{n=0}^{K} \beta\_{2n} g^{(2n+1)}(t)\\, where \\K\\ is the number of suppressed frequency ranges, \\\\beta\_{2n}\\\\ are the coefficients of the derivative terms, and \\g(t)\\ is the basis envelope. The pulse is assumed to start at time `-pulse_duration/2`, and end at time `pulse_duration/2`.

Parameters:  
- **t_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of time points, at which the function is to be evaluated

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration in the same units as t_arr

- **derivative_coefs_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Coefficients of the derivatives

- **cosine_coefs_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Coefficients of the cosine terms in the basis envelope

Returns:  
Q-envelope of a HD DRAG pulse evaluated at `t_arr`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
