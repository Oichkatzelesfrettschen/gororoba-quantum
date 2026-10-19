> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ConditionalInstruction.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ConditionalInstruction.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 410b79e22c5ee789056825a481dc4a52f81d091e562c863b73e9cff5505b1d69.

# ConditionalInstruction

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.ConditionalInstruction(*duration*, *condition*, *outcomes*)  
Bases: [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")

Choice between multiple Instructions, depending on a condition.

Attributes

|  |  |
|----|----|
| [`condition`](#iqm.pulse.playlist.instructions.ConditionalInstruction.condition "iqm.pulse.playlist.instructions.ConditionalInstruction.condition") | Can be evaluated to an integer \>= 0 representing an outcome. |
| [`outcomes`](#iqm.pulse.playlist.instructions.ConditionalInstruction.outcomes "iqm.pulse.playlist.instructions.ConditionalInstruction.outcomes") | Maps possible outcomes of the condition to the corresponding instructions. |
| `duration` | Time duration of the instruction. |
| `id` | Unique id for caching purposes, which can be used if the instruction is not hashable. |

Methods

|  |  |
|----|----|
| [`get_child_instructions`](#iqm.pulse.playlist.instructions.ConditionalInstruction.get_child_instructions "iqm.pulse.playlist.instructions.ConditionalInstruction.get_child_instructions") | Returns all the child Instructions the Instruction contains. |
| [`validate`](#iqm.pulse.playlist.instructions.ConditionalInstruction.validate "iqm.pulse.playlist.instructions.ConditionalInstruction.validate") | Validate the instruction attributes. |

Parameters:  
- **duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **condition** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **outcomes** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")*,* *...\]*)

condition*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Can be evaluated to an integer \>= 0 representing an outcome.

outcomes*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Instruction](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction"), ...\]*  
Maps possible outcomes of the condition to the corresponding instructions.

validate()  
Validate the instruction attributes.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – something about the instruction is not ok

Return type:  
*None*

get_child_instructions()  
Returns all the child Instructions the Instruction contains.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction"), …\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.ConditionalInstruction](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e025c5f0b5b11d9fe4e236e8a3b41f6d3f76fdc1.png)
