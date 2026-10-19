> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b125e77e12335f1f37ad814216a3ceaa84d58ac0b7f0c231508a0c9763b46118.

# iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag

iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag(*number_of_suppressed_freqs*)  
Solve cosine coefficients of the basis envelope given the number of suppressed frequencies.

The cosine coefficients \\\\d_k\\\_{k=1}^{K+1}\\ define the basis envelope as \\g(t) = \sum\_{k=1}^{K+1} d_k (1 - \cos(2\pi k t/t_p + k\pi))\\, where the pulse is defined on the interval \\t \in \[-t_p/2, t_p/2\]\\.

Parameters:  
**number_of_suppressed_freqs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of suppressed frequencies

Returns:  
Coefficient array of length `number_of_suppressed_freqs + 1`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
