> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9698768fe5a6c9bcccd1b6a9d75d627aefde8140d1534c32ec7dc0a6bac22ab2.

# StagesList

Module: [`iqm.cpc.compiler.compilation_stage`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.html#module-iqm.cpc.compiler.compilation_stage "iqm.cpc.compiler.compilation_stage")

*class* iqm.cpc.compiler.compilation_stage.StagesList(*stages*)  
Bases: [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[`CompilationStage`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")\]

Extend `list[CompilationStage]` to allow accessing the stages via their names and to include validation.

Methods

|  |  |
|----|----|
| [`append`](#iqm.cpc.compiler.compilation_stage.StagesList.append "iqm.cpc.compiler.compilation_stage.StagesList.append") | Append `stage` into the list. |
| [`extend`](#iqm.cpc.compiler.compilation_stage.StagesList.extend "iqm.cpc.compiler.compilation_stage.StagesList.extend") | Extend the list by `stages`. |
| [`insert`](#iqm.cpc.compiler.compilation_stage.StagesList.insert "iqm.cpc.compiler.compilation_stage.StagesList.insert") | Insert `stage` into the list. |

Parameters:  
**stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]*)

append(*stage*)  
Append `stage` into the list.

Parameters:  
**stage** ([*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage"))

Return type:  
None

insert(*index*, *stage*)  
Insert `stage` into the list.

Parameters:  
- **index** ([*SupportsIndex*](https://docs.python.org/3.11/library/typing.html#typing.SupportsIndex "(in Python v3.11)"))

- **stage** ([*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage"))

Return type:  
None

extend(*stages*)  
Extend the list by `stages`.

Parameters:  
**stages** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]*)

Return type:  
None

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compilation_stage.StagesList](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-7696e38a2cf5d3e34c0ff12d83037d0ac72507c0.png)
