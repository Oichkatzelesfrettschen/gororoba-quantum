> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 84c6fd00ca8ca871486d432e592e542b6f4e6af6f8ed34d718950c30ef0c516b.

# ReadoutTrigger

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.ReadoutTrigger(*duration*, *probe_pulse*, *acquisitions*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Instruction for playing a probe pulse and acquiring the associated readout results.

Attributes

|  |  |
|----|----|
| [`probe_pulse`](#iqm.pulse.playlist.instructions.ReadoutTrigger.probe_pulse "iqm.pulse.playlist.instructions.ReadoutTrigger.probe_pulse") | Probe pulse to play, usually a MultiplexedIQPulse. |
| [`acquisitions`](#iqm.pulse.playlist.instructions.ReadoutTrigger.acquisitions "iqm.pulse.playlist.instructions.ReadoutTrigger.acquisitions") | Active readout acquisition methods associated with this trigger instance. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **probe_pulse** ([*MultiplexedIQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.MultiplexedIQPulse.html#iqm.pulse.playlist.instructions.MultiplexedIQPulse "iqm.pulse.playlist.instructions.MultiplexedIQPulse"))

- **acquisitions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*AcquisitionMethod*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html#iqm.pulse.playlist.instructions.AcquisitionMethod "iqm.pulse.playlist.instructions.AcquisitionMethod")*,* *...\]*)

probe_pulse*: [MultiplexedIQPulse](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.MultiplexedIQPulse.html#iqm.pulse.playlist.instructions.MultiplexedIQPulse "iqm.pulse.playlist.instructions.MultiplexedIQPulse")*  
Probe pulse to play, usually a MultiplexedIQPulse.

acquisitions*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[AcquisitionMethod](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html#iqm.pulse.playlist.instructions.AcquisitionMethod "iqm.pulse.playlist.instructions.AcquisitionMethod"), ...\]*  
Active readout acquisition methods associated with this trigger instance.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.ReadoutTrigger](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8c279373a6594b3672338d892dd41d4cbdbf4b62.png)
