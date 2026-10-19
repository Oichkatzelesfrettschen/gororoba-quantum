> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6021d4d27087e26a441545a9ad24cbc30030493ee49ed0a459b5dfc4afe56909.

# hd_drag

Full path: iqm.pulse.playlist.hd_drag

Waveform definitions for a higher-derivative (HD) DRAG pulse based on Appendix B of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\].

Module Attributes

|  |  |
|----|----|
| [`COSINE_COEFFICIENTS_DICT`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT.html#iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT "iqm.pulse.playlist.hd_drag.COSINE_COEFFICIENTS_DICT") | Pre-computed coefficients of the cosine terms in the basis envelope (0th derivative). |

Functions

|  |  |
|----|----|
| [`evaluate_hd_drag_i_envelope`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_hd_drag_i_envelope.html#iqm.pulse.playlist.hd_drag.evaluate_hd_drag_i_envelope "iqm.pulse.playlist.hd_drag.evaluate_hd_drag_i_envelope")(t_arr, ...) | Evaluate I-envelope of HD DRAG given the coefficients of the derivative terms and the cosine terms. |
| [`evaluate_hd_drag_q_envelope`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope.html#iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope "iqm.pulse.playlist.hd_drag.evaluate_hd_drag_q_envelope")(t_arr, ...) | Evaluate Q-envelope of HD DRAG given the coefficients of the derivative terms and the cosine terms. |
| [`evaluate_nth_derivative_of_basis_envelope`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope.html#iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope "iqm.pulse.playlist.hd_drag.evaluate_nth_derivative_of_basis_envelope")(...) | Evaluate nth derivative of the basis envelope for HD DRAG based on a cosine series. |
| [`solve_cosine_coefs_for_hd_drag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag.html#iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag "iqm.pulse.playlist.hd_drag.solve_cosine_coefs_for_hd_drag")(...) | Solve cosine coefficients of the basis envelope given the number of suppressed frequencies. |
| [`solve_hd_drag_coefficients_from_suppressed_frequencies`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies.html#iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies "iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies")(...) | Solve coefficients of the derivative terms in a HD DRAG pulse given pulse duration and frequencies to suppress. |

Classes

|  |  |
|----|----|
| [`HdDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDrag.html#iqm.pulse.playlist.hd_drag.HdDrag "iqm.pulse.playlist.hd_drag.HdDrag") | Base class for higher-derivative DRAG based on Eqs. |
| [`HdDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragI.html#iqm.pulse.playlist.hd_drag.HdDragI "iqm.pulse.playlist.hd_drag.HdDragI") | I-component of the higher derivative (HD) drag pulse. |
| [`HdDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragQ.html#iqm.pulse.playlist.hd_drag.HdDragQ "iqm.pulse.playlist.hd_drag.HdDragQ") | Q-component of the higher derivative (HD) drag pulse. |

Inheritance

![Inheritance diagram of iqm.pulse.playlist.hd_drag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-a73aa57a357f56ce60a2e9220a37c6bb8b1073ae.png)
