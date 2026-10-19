> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 64c15c2ae5ef84873405c03505482596aaf46d1630c5603a58ba5fcaf4a409bd.

# iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope

iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope(*t_arr*, *pulse_duration*, *coefficients*)  
Evaluate I-envelope of a FAST DRAG pulse for given coefficients.

The I-envelope is defined as \\I(t) = \sum\_{n=1}^{N} c_n \[1 - (-1)^n \cos(2\pi n t/t_p)\]\\, where \\N\\ is the number of cosine terms in the series, \\\\c_n\\\\ are the coefficients, and the pulse is defined on the interval \\t \in \[-t_p/2, t_p/2\]\\.

Parameters:  
- **t_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of time points, at which the function is to be evaluated

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration in the same units as t_arr

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Coefficients of a FAST DRAG pulse

Returns:  
I-envelope of a FAST DRAG pulse evaluated at `t_arr`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
