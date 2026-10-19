> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 14de6edd2f9854dd70e595554caa362d0ff12e82824ed9a40e74b1b715c80970.

# IQMSchedulingPlugin

Module: [`iqm.qiskit_iqm.transpiler_plugins`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.html#module-iqm.qiskit_iqm.transpiler_plugins "iqm.qiskit_iqm.transpiler_plugins")

*class* iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin(*move_gate_routing: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*, *optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*, *drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*, *ignore_barriers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*, *existing_move_handling: [ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*)  
Bases: [`PassManagerStagePlugin`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.preset_passmanagers.plugin.PassManagerStagePlugin "(in Qiskit v2.5)")

Basic plugin for scheduling stage of IQM devices.

Parameters:  
- **move_gate_routing** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to include MoveGate routing in the scheduling stage.

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to include single qubit gate optimization in the scheduling stage.

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to drop trailing RZ gates in the circuit during single qubit gate optimization. Dropping them does not change the measurement outcomes, but does change the unitary propagator of the circuit.

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to ignore barriers during single qubit gate optimization.

- **existing_move_handling** ([*ExistingMoveHandlingOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") *\|* *None*) – How to handle existing MoveGates in the circuit during MoveGate routing.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – When incompatible options are set.

Methods

|  |  |
|----|----|
| [`pass_manager`](#iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.pass_manager "iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.pass_manager") | Build scheduling stage PassManager. |

pass_manager(*pass_manager_config: [PassManagerConfig](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManagerConfig "(in Qiskit v2.5)")*, *optimization_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [PassManager](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManager "(in Qiskit v2.5)")  
Build scheduling stage PassManager.

Parameters:  
- **pass_manager_config** ([*PassManagerConfig*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManagerConfig "(in Qiskit v2.5)"))

- **optimization_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

Return type:  
[*PassManager*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManager "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-7fa28674d49a3719e8811fb6259df96c8c133b6d.png)
