> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b94d5344fc18a1353170ce9d6eec17da30d7f6cc58c0bc5a9000c6215aeb60cf.

# iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies

iqm.pulse.playlist.hd_drag.solve_hd_drag_coefficients_from_suppressed_frequencies(*pulse_duration*, *suppressed_freq_arr*)  
Solve coefficients of the derivative terms in a HD DRAG pulse given pulse duration and frequencies to suppress.

The coefficients \\\\\beta\_{2n}}\_{n=0}^{K}\\ of the derivative terms are solved using Eq. (B5) of \[[3](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id6 "Eric Hyyppä, Antti Vepsäläinen, Miha Papič, Chun Fai Chan, Sinan Inel, Alessandro Landra, Wei Liu, Jürgen Luus, Fabian Marxer, Caspar Ockeloen-Korppi, and others. Reducing leakage of single-qubit gates for superconducting quantum processors using analytical control pulse envelopes. PRX Quantum, 5(3):030353, 2024. doi:10.1103/PRXQuantum.5.030353.")\] assuming that \\\beta_0 = 1\\. Here, \\K\\ is the number of suppressed frequencies.

Note that the duration and frequencies must have matching units, e.g., s and Hz, or ns and GHz.

Parameters:  
- **pulse_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Pulse duration (in s).

- **suppressed_freq_arr** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *...\]*) – Frequencies to be suppressed relative to the center drive frequency (in Hz).

Returns:  
Coefficient array of length `len(suppressed_freq_arr) + 1`

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
