> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.MultiplexedIQPulse.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.MultiplexedIQPulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b8db6cbdb54adcfc55384bc84407089b62f247a80b666dd511ded4878d67973e.

# MultiplexedIQPulse

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.MultiplexedIQPulse(*duration*, *entries*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Play the sum of multiple IQ pulses.

Each component pulse can have an arbitrary delay from the beginning of this instruction. Outside the interval of the MultiplexedIQPulse, the component pulses are truncated. Where overlapping, samples of component pulse entries are summed. Where the interval of a MultiplexedIQPulse does not overlap with any of its component pulses, its samples are zeroes.

Attributes

|  |  |
|----|----|
| [`entries`](#iqm.pulse.playlist.instructions.MultiplexedIQPulse.entries "iqm.pulse.playlist.instructions.MultiplexedIQPulse.entries") | (`pulse`, `offset`) pairs. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **entries** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* *...\]*)

entries*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[IQPulse](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], ...\]*  
(`pulse`, `offset`) pairs. `offset` is the number of samples `pulse` is delayed from the beginning of the instruction. It has no granularity constraints. Negative values are allowed, but beginning will be truncated.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.MultiplexedIQPulse](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6a32c5043da3a60c18e428988a0cfbf0aadc3a17.png)
