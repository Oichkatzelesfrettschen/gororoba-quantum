> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.MoveGateRoutingPlugin.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.MoveGateRoutingPlugin.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f58da6fd2974afb5e396c0ac0f841782c0b8bcd4a8cb0ff6f5345accd4c61d3.

# MoveGateRoutingPlugin

Module: [`iqm.qiskit_iqm.transpiler_plugins`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.html#module-iqm.qiskit_iqm.transpiler_plugins "iqm.qiskit_iqm.transpiler_plugins")

*class* iqm.qiskit_iqm.transpiler_plugins.MoveGateRoutingPlugin(*optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *ignore_barriers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *existing_move_handling: [ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`IQMSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMSchedulingPlugin")

IQM single qubit gate optimization and MoveGate routing as a scheduling stage.

Methods

Parameters:  
- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **existing_move_handling** ([*ExistingMoveHandlingOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") *\|* *None*)

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.transpiler_plugins.MoveGateRoutingPlugin](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-648a384a3dd9fd020565cba7ac646737c2ecf44a.png)
