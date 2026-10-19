> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.compiler_pass.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.compiler_pass.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6caaf2f6cc59deff992cdd02d1ff67b0e1840031de20358d120f2b9fbac01eb6.

# iqm.cpc.compiler.compilation_stage.compiler_pass

iqm.cpc.compiler.compilation_stage.compiler_pass(*function*)  
Convenience wrapper to create a valid compiler pass.

When the wrapped function is called, the compilation data (e.g. circuits) is passed as the first argument. If `function` has any other arguments, they are either sweepable stage options or default members of the stateful compiler context. If a compiler pass needs as its input data that is not a sweepable compiler option or one of the default context members, this data must be provided into the context by some other pass function or manually by the user, and the pass function should have `context` as one of its arguments. The final wrapped compiler then have uniform signatures: `(data_, context, options)`.

Parameters:  
**function** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The function to be wrapped into a valid compiler pass. It must return the `data` for the subsequent passes and any stateful side effects can be achieved via manipulation the compiler context.

Returns:  
`function` wrapped into a compiler pass, i.e. the same functionality as originally but with the signature  
`(data_, context, options)`.

Return type:  
[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")
