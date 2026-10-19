> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf298b225e5c76b8410c52bee431e35f76ecd8721f8e5593b45f490f6cb91f7b.

# compilation_stage

Full path: iqm.cpc.compiler.compilation_stage

Compilation stages and passes.

Module Attributes

|  |  |
|----|----|
| [`DEFAULT_CONTEXT_KEYS`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS.html#iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS "iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS") | Keys that always exist in the Compiler context. |
| [`DEFAULT_STAGE_ARGS`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.DEFAULT_STAGE_ARGS.html#iqm.cpc.compiler.compilation_stage.DEFAULT_STAGE_ARGS "iqm.cpc.compiler.compilation_stage.DEFAULT_STAGE_ARGS") | Default compiler pass function arguments. |
| [`PassFunction`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.PassFunction.html#iqm.cpc.compiler.compilation_stage.PassFunction "iqm.cpc.compiler.compilation_stage.PassFunction") | A function that takes the data, context, and options as arguments and returns the modified data and context. |

Functions

|  |  |
|----|----|
| [`compiler_pass`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.compiler_pass.html#iqm.cpc.compiler.compilation_stage.compiler_pass "iqm.cpc.compiler.compilation_stage.compiler_pass")(function) | Convenience wrapper to create a valid compiler pass. |
| [`format_stages`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.format_stages.html#iqm.cpc.compiler.compilation_stage.format_stages "iqm.cpc.compiler.compilation_stage.format_stages")(stages\[, idempotent\]) | Format user inputted stages and their passes to their final runnable form (see [`compiler_pass()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.compiler_pass.html#iqm.cpc.compiler.compilation_stage.compiler_pass "iqm.cpc.compiler.compilation_stage.compiler_pass")). |
| [`pass_function_idempotent`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.pass_function_idempotent.html#iqm.cpc.compiler.compilation_stage.pass_function_idempotent "iqm.cpc.compiler.compilation_stage.pass_function_idempotent")(function) | Wrap a pass function to make it idempotent. |
| [`resolve_circuit_function_and_stages`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages.html#iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages "iqm.cpc.compiler.compilation_stage.resolve_circuit_function_and_stages")(stages, ...) | Insert the circuit generation as the first stage in the provided `stages`. |

Classes

|  |  |
|----|----|
| [`CompilationStage`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage") | Sequence of compiler passes that are applied to the data. |
| [`StagesList`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList") | Extend `list[CompilationStage]` to allow accessing the stages via their names and to include validation. |

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compilation_stage](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-f192db7e07cc6ae2ae5cade87f184687a0b130ac.png)
