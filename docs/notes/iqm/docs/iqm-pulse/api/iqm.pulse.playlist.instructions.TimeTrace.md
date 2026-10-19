> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.TimeTrace.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.TimeTrace.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf9c631b6ef7ac70057d5173e3a66b98f612ac760d700e9877a87ed4791273eb.

# TimeTrace

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.TimeTrace(*label*, *delay_samples*, *implementation*, *duration_samples*)  
Bases: [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html#iqm.pulse.playlist.instructions.AcquisitionMethod "iqm.pulse.playlist.instructions.AcquisitionMethod")

Capture the raw IQ signal without integration.

Attributes

|  |  |
|----|----|
| [`duration_samples`](#iqm.pulse.playlist.instructions.TimeTrace.duration_samples "iqm.pulse.playlist.instructions.TimeTrace.duration_samples") | Length of the capture window, in samples. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |
| `implementation` | Measure operation and implementation that created this AcquisitionMethod, in the format `<operation name>.<implementation name>`. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **duration_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

duration_samples*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Length of the capture window, in samples.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.TimeTrace](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e8e80b04251c79384b51b895efbc486c75944f7c.png)
