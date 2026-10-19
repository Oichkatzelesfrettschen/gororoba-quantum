> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bf8b68eaad39d4cfb89de4a5af3211b0368758e15bfee9d1e3433641e2cf4fcb.

# fast_drag

Full path: iqm.pulse.playlist.fast_drag

Waveform definitions for Fourier Ansatz Spectrum Tuning (FAST) DRAG pulse based on \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\].

Functions

|  |  |
|----|----|
| [`compute_matrix_of_summed_fourier_transform_inner_products`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products.html#iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products "iqm.pulse.playlist.fast_drag.compute_matrix_of_summed_fourier_transform_inner_products")(...) | Evaluate matrix \\A\\ defined in Eq. |
| [`evaluate_fast_drag_i_envelope`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope.html#iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope "iqm.pulse.playlist.fast_drag.evaluate_fast_drag_i_envelope")(t_arr, ...) | Evaluate I-envelope of a FAST DRAG pulse for given coefficients. |
| [`evaluate_fast_drag_q_envelope`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope.html#iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope "iqm.pulse.playlist.fast_drag.evaluate_fast_drag_q_envelope")(t_arr, ...) | Evaluate Q-envelope of FAST DRAG for given coefficients. |
| [`fourier_transform_of_cos_basis_functions_as_tensor`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor.html#iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor "iqm.pulse.playlist.fast_drag.fourier_transform_of_cos_basis_functions_as_tensor")(...) | Evaluate Fourier transforms of cosine basis functions for given basis function indices and frequencies. |
| [`solve_fast_coefficients_for_given_weights_and_ranges`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges.html#iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges "iqm.pulse.playlist.fast_drag.solve_fast_coefficients_for_given_weights_and_ranges")(...) | Solve for optimal coefficients of the basis functions in a FAST DRAG pulse. |

Classes

|  |  |
|----|----|
| [`FastDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDrag.html#iqm.pulse.playlist.fast_drag.FastDrag "iqm.pulse.playlist.fast_drag.FastDrag") | Base class for IQ components of the Fourier Ansatz Spectrum Tuning (FAST) DRAG pulse. |
| [`FastDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragI.html#iqm.pulse.playlist.fast_drag.FastDragI "iqm.pulse.playlist.fast_drag.FastDragI") | I-component of the Fourier Ansatz Spectrum Tuning (FAST) drag pulse. |
| [`FastDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragQ.html#iqm.pulse.playlist.fast_drag.FastDragQ "iqm.pulse.playlist.fast_drag.FastDragQ") | Q-component of the Fourier Ansatz Spectrum Tuning (FAST) drag pulse. |
| [`SuppressedPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.SuppressedPulse.html#iqm.pulse.playlist.fast_drag.SuppressedPulse "iqm.pulse.playlist.fast_drag.SuppressedPulse") | Base class for control pulses using a series expansion to suppress certain frequencies in its envelope spectrum. |

Inheritance

![Inheritance diagram of iqm.pulse.playlist.fast_drag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-428ed65cf1258eaf1f633543bbc97ca2f0b5585e.png)
