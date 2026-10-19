> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7d0320aafe316b03cf2fb4c60710326490c3539e58faeec333d1d7570c8bca0b.

# iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT

iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT *= {0: array(\[1\]), 1: array(\[ 1.33333333, -0.33333333\]), 2: array(\[ 1.5, -0.6,  0.1\]), 3: array(\[ 1.6       , -0.8       ,  0.22857143, -0.02857143\]), 4: array(\[ 1.66666667, -0.95238095,  0.35714286, -0.07936508,  0.00793651\]), 5: array(\[ 1.71428571, -1.07142857,  0.47619048, -0.14285714,  0.02597403,        -0.0021645 \]), 6: array(\[ 1.75000000e+00, -1.16666667e+00,  5.83333333e-01, -2.12121212e-01,         5.30303030e-02, -8.15850816e-03,  5.82750583e-04\]), 7: array(\[ 1.77777778e+00, -1.24444444e+00,  6.78787879e-01, -2.82828283e-01,         8.70240870e-02, -1.86480186e-02,  2.48640249e-03, -1.55400155e-04\])}*  
Pre-computed coefficients of the cosine terms in the basis envelope (0th derivative). This dictionary contains a mapping from the number of suppressed frequencies to the coefficients of the cosine terms computed using the function `solve_cosine_coefs_for_hd_drag`.
