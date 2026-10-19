> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 15db4dcb675e83742b16656d34a5a71a36e91afc8539733ce2fcbaaf859a2280.

# iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope

iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope(*t_arr*, *pulse_duration*, *coefficients*)  
Evaluate Q-envelope of FAST DRAG for given coefficients.

The Q-envelope is defined as \\Q(t) = \sum\_{n=1}^{N} c_n n (-1)^n \sin(2\pi n t/t_p)\]\\, where \\N\\ is the number of cosine terms in the series, \\\\c_n\\\\ are the coefficients, and the pulse is defined on the interval \\t \in \[-t_p/2, t_p/2\]\\.

Parameters:  
- **t_arr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of time points, at which the function is to be evaluated

- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration in the same units as t_arr

- **coefficients** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Coefficients of a FAST DRAG pulse

Returns:  
Q-envelope of a FAST DRAG pulse evaluated at `t_arr`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
