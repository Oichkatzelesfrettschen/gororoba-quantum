> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.TimeTrace.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.TimeTrace.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b2bd387f340f0fd0f129fd4566295efbceb4ba507301406f55497dc7e7491d59.

# TimeTrace

*class* iqm.models.playlist.instructions.TimeTrace(*label*, *delay_samples*, *duration_samples*)  
Bases: [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod")

Capture the raw IQ signal without integration.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`duration_samples`](#iqm.models.playlist.instructions.TimeTrace.duration_samples "iqm.models.playlist.instructions.TimeTrace.duration_samples") | Length of the capture window, in samples. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **duration_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

duration_samples*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Length of the capture window, in samples.
