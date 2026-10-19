> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1070bd44842cce2afb264552d23ea01f105eca477e12caed5a5ea20b1cd828d4.

# IQMNaiveResonatorMoving

Module: [`iqm.qiskit_iqm.iqm_naive_move_pass`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.html#module-iqm.qiskit_iqm.iqm_naive_move_pass "iqm.qiskit_iqm.iqm_naive_move_pass")

*class* iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving(*\*args*, *\*\*kwargs*)  
Bases: [`TransformationPass`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.TransformationPass "(in Qiskit v2.5)")

Naive transpilation pass for resonator moving.

The logic of this pass is deferred to [`transpile_insert_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html#iqm.iqm_client.transpile.transpile_insert_moves "iqm.iqm_client.transpile.transpile_insert_moves"). This pass is a wrapper that converts the circuit into the IQM circuit format, runs the `transpile_insert_moves` function, and then converts the result back to a Qiskit circuit.

Parameters:  
- **target** – Transpilation target.

- **existing_moves_handling** – How to handle existing MOVE gates in the circuit.

Attributes

Methods

|  |  |
|----|----|
| [`run`](#iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving.run "iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving.run") | Run the pass on a circuit. |

run(*dag: [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")*) → [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")  
Run the pass on a circuit.

Parameters:  
**dag** ([*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")) – DAG to insert MOVE gates into.

Returns:  
The new `dag` now including MOVE gates as needed.

Raises:  
**TranspilerError** – The layout is not compatible with the DAG, or if something goes wrong during transpilation.

Return type:  
[*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-da821924bdbdcf87fe77955755d20079ca65500a.png)
