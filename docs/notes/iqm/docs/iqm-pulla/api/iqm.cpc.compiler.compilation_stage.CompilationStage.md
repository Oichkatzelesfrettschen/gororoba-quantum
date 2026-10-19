> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6077838bd50075d3886c182e852a7228f052fddda368147acfbe609f7d1bc365.

# CompilationStage

Module: [`iqm.cpc.compiler.compilation_stage`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.html#module-iqm.cpc.compiler.compilation_stage "iqm.cpc.compiler.compilation_stage")

*class* iqm.cpc.compiler.compilation_stage.CompilationStage(*name*, *info=''*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Sequence of compiler passes that are applied to the data.

The data and context are returned after all passes have been applied. A pass is a function that takes the data, context and pass options as arguments and returns the modified data. The context is a dictionary that can contain any information that needs to be passed between the passes and accumulates stateful side effects.

Methods

|  |  |
|----|----|
| [`add_passes`](#iqm.cpc.compiler.compilation_stage.CompilationStage.add_passes "iqm.cpc.compiler.compilation_stage.CompilationStage.add_passes") | Add multiple passes to the stage. |
| [`get_pass_args`](#iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_args "iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_args") | Get pass function argument names. |
| [`get_pass_metadata`](#iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_metadata "iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_metadata") | Returns all signature metadata in a single call. |
| [`get_pass_names`](#iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_names "iqm.cpc.compiler.compilation_stage.CompilationStage.get_pass_names") | Get pass function names. |
| [`run`](#iqm.cpc.compiler.compilation_stage.CompilationStage.run "iqm.cpc.compiler.compilation_stage.CompilationStage.run") | Run all the passes in the stage on the data and context. |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **info** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

add_passes(*\*passes*, *index=None*)  
Add multiple passes to the stage.

Parameters:  
- **passes** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – One or more passes to be added to the stage.

- **index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Index where to add `passes`. None means end of the stage.

Return type:  
None

get_pass_names()  
Get pass function names.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_pass_args()  
Get pass function argument names.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

run(*data*, *context*, *options*)  
Run all the passes in the stage on the data and context.

The data and context are returned after all passes have been applied.

Parameters:  
- **data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The data to be processed.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – A dictionary containing any additional information that needs to be passed between the passes.

- **options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]\]*) – A dictionary of stage’s pass function arguments and their values (mapped to the pass function name)

Returns:  
The processed data, context.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

*static* get_pass_metadata(*pass_fn*)  
Returns all signature metadata in a single call.

Parameters:  
**pass_fn** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compilation_stage.CompilationStage](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-d944ccef024137db982e9ecf69620f2a0d6dbb0a.png)
