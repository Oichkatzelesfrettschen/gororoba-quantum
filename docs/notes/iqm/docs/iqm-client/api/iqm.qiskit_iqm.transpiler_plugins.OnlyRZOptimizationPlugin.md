> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.OnlyRZOptimizationPlugin.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.OnlyRZOptimizationPlugin.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fb06db3a71ff2e1bf0bb9ea06fdde2c2718eb5546464cb560b64c4289bc094dc.

# OnlyRZOptimizationPlugin

Module: [`iqm.qiskit_iqm.transpiler_plugins`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.html#module-iqm.qiskit_iqm.transpiler_plugins "iqm.qiskit_iqm.transpiler_plugins")

*class* iqm.qiskit_iqm.transpiler_plugins.OnlyRZOptimizationPlugin(*drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *ignore_barriers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*)  
Bases: [`IQMSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin")

Single qubit gate optimization without MOVE gate routing.

Methods

Parameters:  
- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.transpiler_plugins.OnlyRZOptimizationPlugin](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-44b690edb40ab7d5056ff9c059dcf3762d9eb35f.png)
