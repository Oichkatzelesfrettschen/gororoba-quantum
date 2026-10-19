> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.format_stages.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.format_stages.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 474a41431460ab9af2d3f295a6ae9325c2d2c9b930045b6456921b59d100685f.

# iqm.cpc.compiler.compilation_stage.format_stages

iqm.cpc.compiler.compilation_stage.format_stages(*stages*, *idempotent=True*)  
Format user inputted stages and their passes to their final runnable form (see [`compiler_pass()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.compiler_pass.html#iqm.cpc.compiler.compilation_stage.compiler_pass "iqm.cpc.compiler.compilation_stage.compiler_pass")).

Parameters:  
- **stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]*) – The compilation stages containing function passes that should be formatted.

- **idempotent** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Optionally make the stages also idempotent (they deepcopy both the context and the circuits at each pass). NOTE: if performance is prioritized, this option should not be turned on.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")\]
