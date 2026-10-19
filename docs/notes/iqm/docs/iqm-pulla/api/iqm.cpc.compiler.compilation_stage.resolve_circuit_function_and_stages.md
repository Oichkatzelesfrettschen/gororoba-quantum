> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cbb1456418b46da9f3dfa79726970d75dfacce391726260a92c729c23dd535b0.

# iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages

iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages(*stages*, *input*)  
Insert the circuit generation as the first stage in the provided `stages`.

Parameters:  
- **stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]*) – The stages into which the circuit should be inserted.

- **input** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The circuit generation function or a static circuit object. If a static circuit object is inputted, it will be wrapped into a trivial circuit generation function.

Returns:  
The compilation stages such that the first stage is now the circuit generation.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")\]
