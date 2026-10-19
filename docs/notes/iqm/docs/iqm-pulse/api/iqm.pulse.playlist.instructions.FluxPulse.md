> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.FluxPulse.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.FluxPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 600867a8a24afb8d4a26d0141b603e2aaec008d3e8ff28b949d250e259750e28.

# FluxPulse

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.FluxPulse(*duration*, *wave*, *scale*, *rzs=\<factory\>*)  
Bases: [`RealPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.RealPulse.html#iqm.pulse.playlist.instructions.RealPulse "iqm.pulse.playlist.instructions.RealPulse")

RealPulse representing a flux pulse.

Can store RZ angles for correcting local phase shifts from the computational frame due to flux crosstalk.

Attributes

|  |  |
|----|----|
| [`rzs`](#iqm.pulse.playlist.instructions.FluxPulse.rzs "iqm.pulse.playlist.instructions.FluxPulse.rzs") | Collection of (drive) channel names and RZ angles. |
| `wave` | Shape of the pulse. |
| `scale` | Scaling factor for the waveform. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **wave** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "(in IQM data definitions v3.1.0)"))

- **scale** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **rzs** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\],* *...\]*)

rzs*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], ...\]*  
Collection of (drive) channel names and RZ angles.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.FluxPulse](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e9fdc4f0467611090418ed33f5f0c211f42807af.png)
