> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Slepian.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Slepian.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e2186b8f00927e316c57157c0899765dbb03f37e3cf4599fa1fce177d1395482.

# Slepian

*class* iqm.models.playlist.waveforms.Slepian(*n_samples*, *full_width*, *lambda_1*, *lambda_2*, *frequency_initial_normalized*, *frequency_to_minimize_normalized*, *coupling_strength_normalized*, *center_offset=0*, *squid_asymmetry=0*, *flat_width=0.0*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Slepian waveform, which minimizes non-adiabatic errors during a gate.

It is assumed that the user has done the minimization in a prior step, such that the optimal \\\lambda_n\\ for a specific length \\\tau\_\text{pulse}\\ (in the accelerated frame) is known. This class then reconstructs the waveform with the following steps:

1.  Calculate \\\theta(\tau)\\ (Slepian in the accelerated frame and in \\\theta\\ space)

2.  Calculate \\t(\tau)\\ (mapping time in the accelerated frame to time in the lab frame)

3.  Interpolate \\\theta(t)\\ (Slepian in the lab frame and in \\\theta\\ space)

4.  Calculate \\f(t)\\ (Slepian in the lab frame and in frequency space)

5.  Calculate \\V(t)\\ (Slepian in the lab frame and in voltage space)

Since the waveform is normalized, any voltage pre-factor should go into the pulse amplitude.

The user is advised to look up \[[1](https://docs.iqm.tech/4.7/iqm-data-definitions/references.html#id2 "John M. Martinis and Michael R. Geller. Fast adiabatic qubit gates using only $\sigma _z$ control. Phys. Rev. A, 90:022307, Aug 2014. arXiv:1402.5467, doi:10.1103/PhysRevA.90.022307.")\] for further details, since the derivation is mathematically heavy.

Parameters:  
- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the support of the waveform.

- **lambda_1** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – First coefficient of Slepian waveform.

- **lambda_2** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Second coefficient of Slepian waveform.

- **frequency_initial_normalized** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Initial frequency of the pulsed component (usually coupler), normalized by the maximum frequency of the pulsed component.

- **frequency_to_minimize_normalized** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Frequency of the static component (usually qubit) which to minimize the leakage from/to, normalized by the maximum frequency of the pulsed component.

- **coupling_strength_normalized** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Coupling strength between pulsed component and static component, normalized by the maximum frequency of the pulsed component.

- **center_offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The waveform is centered at this offset from the midpoint of the sampling window.

- **squid_asymmetry** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Squid asymmetry.

- **flat_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Duration of the flat part in the middle of the waveform. The rise and fall parts together have duration `full_width - flat_width`. Defaults to 0.0 (standard Slepian).

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|  |  |
|----|----|
| `center_offset` |  |
| `flat_width` |  |
| `squid_asymmetry` |  |
| `full_width` |  |
| `lambda_1` |  |
| `lambda_2` |  |
| `frequency_initial_normalized` |  |
| `frequency_to_minimize_normalized` |  |
| `coupling_strength_normalized` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.models.playlist.waveforms.Slepian.non_timelike_attributes "iqm.models.playlist.waveforms.Slepian.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
