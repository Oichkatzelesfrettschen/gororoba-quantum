> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7455e377f1f9814daae3eed53027e9ae821d45ba90ecb4dfc76928dfcdea2974.

# AcquisitionMethod

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.AcquisitionMethod(*label*, *delay_samples*, *implementation*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Describes a way to acquire readout data.

Attributes

|  |  |
|----|----|
| [`label`](#iqm.pulse.playlist.instructions.AcquisitionMethod.label "iqm.pulse.playlist.instructions.AcquisitionMethod.label") | Identifier for the returned data, like `QB1__readout.time_trace`. |
| [`delay_samples`](#iqm.pulse.playlist.instructions.AcquisitionMethod.delay_samples "iqm.pulse.playlist.instructions.AcquisitionMethod.delay_samples") | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |
| [`implementation`](#iqm.pulse.playlist.instructions.AcquisitionMethod.implementation "iqm.pulse.playlist.instructions.AcquisitionMethod.implementation") | Measure operation and implementation that created this AcquisitionMethod, in the format `<operation name>.<implementation name>`. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Identifier for the returned data, like `QB1__readout.time_trace`.

delay_samples*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Delay from beginning of probe pulse to beginning of acquisition window, in samples.

implementation*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Measure operation and implementation that created this AcquisitionMethod, in the format `<operation name>.<implementation name>`. If the acquisition is not originated from a gate implementation, this should be `None`.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.AcquisitionMethod](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-2f3e8b08e6d8792f6d493598b2e54f8566596244.png)
