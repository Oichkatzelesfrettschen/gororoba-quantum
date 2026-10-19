> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f0b4d4840885e41f60dc8e22d3c4de4291b076a85ee0eb93685c33d451379841.

# AcquisitionMethod

*class* iqm.models.playlist.instructions.AcquisitionMethod(*label*, *delay_samples*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Describes a way to acquire readout data.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`label`](#iqm.models.playlist.instructions.AcquisitionMethod.label "iqm.models.playlist.instructions.AcquisitionMethod.label") | Identifier for the returned data, like `QB1__readout.time_trace`. |
| [`delay_samples`](#iqm.models.playlist.instructions.AcquisitionMethod.delay_samples "iqm.models.playlist.instructions.AcquisitionMethod.delay_samples") | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Identifier for the returned data, like `QB1__readout.time_trace`.

delay_samples*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Delay from beginning of probe pulse to beginning of acquisition window, in samples.
