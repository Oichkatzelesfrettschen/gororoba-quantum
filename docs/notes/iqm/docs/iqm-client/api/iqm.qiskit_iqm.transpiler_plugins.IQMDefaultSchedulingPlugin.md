> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 443292936adf2e35db5d648fade287435ddf5b6afa46cb5ab87dc58f608fe617.

# IQMDefaultSchedulingPlugin

Module: [`iqm.qiskit_iqm.transpiler_plugins`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.html#module-iqm.qiskit_iqm.transpiler_plugins "iqm.qiskit_iqm.transpiler_plugins")

*class* iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin  
Bases: [`IQMSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin")

IQM single qubit gate optimization and MoveGate routing as a scheduling stage.

Methods

|  |  |
|----|----|
| [`pass_manager`](#iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.pass_manager "iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.pass_manager") | Build scheduling stage PassManager. |

&nbsp;

pass_manager(*pass_manager_config: [PassManagerConfig](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManagerConfig "(in Qiskit v2.5)")*, *optimization_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [PassManager](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManager "(in Qiskit v2.5)")  
Build scheduling stage PassManager.

Parameters:  
- **pass_manager_config** ([*PassManagerConfig*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManagerConfig "(in Qiskit v2.5)"))

- **optimization_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

Return type:  
[*PassManager*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManager "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-eb00a1fd99b468c0a4e162e4699fa2a889ee7f91.png)
