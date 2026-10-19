> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedIQPulse.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedIQPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 023316991050cb1b0cc2c6368a3df46fc53203cd5496a72947736f727a0dda8c.

# MultiplexedIQPulse

*class* iqm.models.playlist.instructions.MultiplexedIQPulse(*entries*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Instruction to simultaneously play multiple IQ pulses.

Each component pulse entry can be added with arbitrary delay from the beginning of this instruction. Where outside the duration of the MultiplexedIQPulse, the pulse entries are truncated. Where overlapping, samples of multiple pulse entries are summed. Where the interval of a MultiplexedIQPulse does not overlap with any of its entry pulse, its samples will be 0.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`entries`](#iqm.models.playlist.instructions.MultiplexedIQPulse.entries "iqm.models.playlist.instructions.MultiplexedIQPulse.entries") | Pairs of instruction and offset. |

Methods

Parameters:  
**entries** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* *...\]*)

entries*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], ...\]*  
Pairs of instruction and offset. Instruction should be an IQPulse. offset is the number of samples the pulse is delayed from the beginning of the instruction. It has no granularity constraints. Negative values are allowed, but beginning will be truncated.
