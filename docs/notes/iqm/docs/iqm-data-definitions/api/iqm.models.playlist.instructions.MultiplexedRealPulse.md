> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedRealPulse.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedRealPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4adc225cf396e24df1bea7b3c5c656b6a3a135d58cfafe9bc18331114391e44b.

# MultiplexedRealPulse

*class* iqm.models.playlist.instructions.MultiplexedRealPulse(*entries*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Instruction to simultaneously play multiple real pulses.

Each component pulse entry can be added with arbitrary delay from the beginning of this instruction. Where outside the duration of the MultiplexedRealPulse, the pulse entries are truncated. Where overlapping, samples of multiple pulse entries are summed. Where the interval of a MultiplexedRealPulse does not overlap with any of its entry pulse, its samples will be 0.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`entries`](#iqm.models.playlist.instructions.MultiplexedRealPulse.entries "iqm.models.playlist.instructions.MultiplexedRealPulse.entries") | Pairs of instruction and offset. |

Methods

Parameters:  
**entries** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* *...\]*)

entries*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], ...\]*  
Pairs of instruction and offset. Instruction should be valid a RealPulse. offset is the number of samples the pulse is delayed from the beginning of the instruction. It has no granularity constraints. Negative values are allowed, but beginning will be truncated.
