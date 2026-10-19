> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerOptions.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ede38a2b91b7d8ab5cce80439ef516a3725bf6dc7b1aac9e332b95a55b518321.

# CompilerOptions

Module: [`iqm.cpc.compiler.compiler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.html#module-iqm.cpc.compiler.compiler "iqm.cpc.compiler.compiler")

*class* iqm.cpc.compiler.compiler.CompilerOptions(*idempotent_stages=False*, *update_settings=False*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Options for Compiler.

Attributes

|  |  |
|----|----|
| [`idempotent_stages`](#iqm.cpc.compiler.compiler.CompilerOptions.idempotent_stages "iqm.cpc.compiler.compiler.CompilerOptions.idempotent_stages") | Set to `True` for idempotent stages (the context and the circuits are deepcopied between each stage pass). |
| [`update_settings`](#iqm.cpc.compiler.compiler.CompilerOptions.update_settings "iqm.cpc.compiler.compiler.CompilerOptions.update_settings") | If True, the settings tree will be updated with the sweep spot values. |

Methods

Parameters:  
- **idempotent_stages** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **update_settings** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

idempotent_stages*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
Set to `True` for idempotent stages (the context and the circuits are deepcopied between each stage pass).

update_settings*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
If True, the settings tree will be updated with the sweep spot values.

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compiler.CompilerOptions](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-18dbd19f0a21bfde0b13694a3e0b9cc6535fa8c5.png)
