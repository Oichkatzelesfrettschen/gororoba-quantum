> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ReadoutTrigger.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ReadoutTrigger.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b5ca53a681e9d4674f93dbfea9ee5ac48c7b13686f1fd4fc7bf3077449a215af.

# ReadoutTrigger

*class* iqm.models.playlist.instructions.ReadoutTrigger(*probe_pulse*, *acquisitions*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Instruction for playing a probe pulse and acquiring the associated readout results.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`probe_pulse`](#iqm.models.playlist.instructions.ReadoutTrigger.probe_pulse "iqm.models.playlist.instructions.ReadoutTrigger.probe_pulse") | Index pointing to a probe pulse, usually a MultiplexedIQPulse. |
| [`acquisitions`](#iqm.models.playlist.instructions.ReadoutTrigger.acquisitions "iqm.models.playlist.instructions.ReadoutTrigger.acquisitions") | Active readout acquisition methods associated with this trigger instance. |

Methods

Parameters:  
- **probe_pulse** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction"))

- **acquisitions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*AcquisitionMethod*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod")*,* *...\]*)

probe_pulse*: [Instruction](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")*  
Index pointing to a probe pulse, usually a MultiplexedIQPulse.

acquisitions*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[AcquisitionMethod](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod"), ...\]*  
Active readout acquisition methods associated with this trigger instance.
