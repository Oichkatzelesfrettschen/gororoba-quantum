> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.ChirpImag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.ChirpImag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3047d84ad35b1c78d3d299cf248b276adb5b5ea1fea0f70380a296aa16511aa8.

# ChirpImag

Module: [`iqm.pulse.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.html#module-iqm.pulse.playlist.waveforms "iqm.pulse.playlist.waveforms")

*class* iqm.pulse.playlist.waveforms.ChirpImag(*n_samples*, *freq_start*, *freq_stop*, *alpha=0.05*, *phase=-1.5707963267948966*)  
Bases: [`Chirp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.Chirp.html#iqm.pulse.playlist.waveforms.Chirp "iqm.pulse.playlist.waveforms.Chirp")

Imaginary part of the linear chirp, which sets the phase to \$-pi/2\$.

Parameters:  
- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **freq_start** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **freq_stop** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **alpha** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

phase  
Phase of the pulse. Defaults to \$pi/2\$

Type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`phase`](#iqm.pulse.playlist.waveforms.ChirpImag.phase "iqm.pulse.playlist.waveforms.ChirpImag.phase") |  |
| `freq_start` |  |
| `freq_stop` |  |
| `n_samples` | Requested number of samples for the waveform. |

Methods

Inheritance

![Inheritance diagram of iqm.pulse.playlist.waveforms.ChirpImag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-b0469dcc670e1cecb134f2c7bd693f454b8fd6ba.png)
