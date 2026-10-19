> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f902979b82523a51162c212ab1f1dcba452222950d1f2d901d46b4a631b28211.

# compiler

Full path: iqm.cpc.compiler.compiler

Convert quantum circuits into instruction schedules.

This is the core module of `CPC`. It contains the functionality to define a compiler, whose job is to convert quantum circuits and calibration data into configuration settings and instruction schedules that can be executed by the IQM server on quantum hardware.

Module Attributes

|  |  |
|----|----|
| [`Components`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Components.html#iqm.cpc.compiler.compiler.Components "iqm.cpc.compiler.compiler.Components") | Same as `ComponentGrouping` but using a normal [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)"). |

Classes

|  |  |
|----|----|
| [`Compiler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html#iqm.cpc.compiler.compiler.Compiler "iqm.cpc.compiler.compiler.Compiler") | Compile quantum circuits into jobs that can be submitted to a quantum computer. |
| [`CompilerOptions`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerOptions.html#iqm.cpc.compiler.compiler.CompilerOptions "iqm.cpc.compiler.compiler.CompilerOptions") | Options for Compiler. |
| [`CompilerStages`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerStages.html#iqm.cpc.compiler.compiler.CompilerStages "iqm.cpc.compiler.compiler.CompilerStages") | Combines all compilation stages under a single object for easy access. |

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compiler](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-8118fabb5fcf3d2538d2d57dbd578098e704d46a.png)
