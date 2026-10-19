> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ComplexIntegration.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ComplexIntegration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 02b6c343226f2068db95216d903694093b980d51ad09f623a36cfab0fb24773e.

# ComplexIntegration

*class* iqm.models.playlist.instructions.ComplexIntegration(*label*, *delay_samples*, *weights*)  
Bases: [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod")

Perform a weighted integration of the IQ raw signal, resulting in a complex number.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`weights`](#iqm.models.playlist.instructions.ComplexIntegration.weights "iqm.models.playlist.instructions.ComplexIntegration.weights") | Integration weights. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **weights** ([*IQPulse*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html#iqm.models.playlist.instructions.IQPulse "iqm.models.playlist.instructions.IQPulse"))

weights*: [IQPulse](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html#iqm.models.playlist.instructions.IQPulse "iqm.models.playlist.instructions.IQPulse")*  
Integration weights.
