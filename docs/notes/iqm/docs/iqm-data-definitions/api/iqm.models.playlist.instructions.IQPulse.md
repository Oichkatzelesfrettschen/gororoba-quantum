> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b673bb1ff2a5abf88ab00dbae5edd8bd9c608b82d70e0d9c5cafefd9677115f0.

# IQPulse

*class* iqm.models.playlist.instructions.IQPulse(*wave_i*, *wave_q*, *scale_i*, *scale_q*, *phase=0.0*, *modulation_frequency=0.0*, *phase_increment=0.0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Class for IQ Pulses. Contains waveforms for both in-phase and quadrature waveforms.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|                        |     |
|------------------------|-----|
| `modulation_frequency` |     |
| `phase`                |     |
| `phase_increment`      |     |
| `wave_i`               |     |
| `wave_q`               |     |
| `scale_i`              |     |
| `scale_q`              |     |

Methods

Parameters:  
- **wave_i** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform"))

- **wave_q** ([*Waveform*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform"))

- **scale_i** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **scale_q** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **modulation_frequency** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **phase_increment** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))
