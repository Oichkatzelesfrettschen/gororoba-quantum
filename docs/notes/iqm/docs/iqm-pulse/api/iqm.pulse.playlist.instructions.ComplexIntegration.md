> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ComplexIntegration.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ComplexIntegration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 963bb2b71940422fb713a92ad0259e437db54e826f20b267081b5fa26050a1fe.

# ComplexIntegration

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.ComplexIntegration(*label*, *delay_samples*, *implementation*, *weights*)  
Bases: [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html#iqm.pulse.playlist.instructions.AcquisitionMethod "iqm.pulse.playlist.instructions.AcquisitionMethod")

Perform a weighted integration of the IQ raw signal, resulting in a complex number.

Attributes

|  |  |
|----|----|
| [`weights`](#iqm.pulse.playlist.instructions.ComplexIntegration.weights "iqm.pulse.playlist.instructions.ComplexIntegration.weights") | Integration weights. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |
| `implementation` | Measure operation and implementation that created this AcquisitionMethod, in the format `<operation name>.<implementation name>`. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **weights** ([*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse"))

weights*: [IQPulse](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse")*  
Integration weights.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.ComplexIntegration](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-cb0f2b42917e7f58e58d89c8cad9cb4ca40aa478.png)
