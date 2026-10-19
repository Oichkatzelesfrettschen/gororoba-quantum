> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 562ac8645cbada34d1ea3ffa4cfb8023afc537edb0d663dd348c579e1223dd11.

# IQMOptimizeSingleQubitGates

Module: [`iqm.qiskit_iqm.iqm_transpilation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.html#module-iqm.qiskit_iqm.iqm_transpilation "iqm.qiskit_iqm.iqm_transpilation")

*class* iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates(*\*args*, *\*\*kwargs*)  
Bases: [`TransformationPass`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.TransformationPass "(in Qiskit v2.5)")

Optimize the decomposition of single-qubit gates for the IQM gate set.

This optimization pass expects the circuit to be correctly layouted and translated to the IQM architecture and raises an error otherwise. The optimization logic follows the steps:

1.  Convert single-qubit gates to \\U\\ gates and combine all neighboring \\U\\ gates.

2.  Convert \\U\\ gates according to \\U(\theta , \phi , \lambda) = ~ RZ(\phi + \lambda) R(\theta, \pi / 2 - \lambda)\\.

3.  Commute RZ gates to the end of the circuit using the fact that RZ and CZ gates commute, and \\R(\theta , \phi) RZ(\lambda) = RZ(\lambda) R(\theta, \phi - \lambda)\\.

4.  Drop RZ gates immediately before measurements, and otherwise replace them according to \\RZ(\lambda) = R(\pi, \lambda / 2) R(- \pi, 0)\\.

Parameters:  
- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Drop terminal RZ gates even if there are no measurements following them (since they do not affect the measurement results). Note that this will change the unitary propagator of the circuit. Defaults to False.

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Remove the barriers from the circuit before optimization. Defaults to False.

Attributes

Methods

|  |  |
|----|----|
| [`run`](#iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.run "iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.run") | Run the single-qubit gate optimization pass. |

run(*dag: [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")*, *decompose_rz_to_r: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")  
Run the single-qubit gate optimization pass.

Parameters:  
- **dag** ([*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")) – The input DAG circuit to optimize.

- **decompose_rz_to_r** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to decompose RZ gates into R gates, or add the to the DAG as RZ gates. This is used in recursive calls to communicate the accumulated RZ angles in `rz_angles`.

Returns:  
The optimized DAG circuit.

Return type:  
[*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-a86787857b6a4dc215c85e0b47e1bf127334e0be.png)
