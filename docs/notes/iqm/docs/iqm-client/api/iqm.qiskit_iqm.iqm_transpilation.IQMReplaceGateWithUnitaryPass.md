> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 478fbcf9e4189ec8524abbbec8c600a4390fc159e429d355c819acf30a56c864.

# IQMReplaceGateWithUnitaryPass

Module: [`iqm.qiskit_iqm.iqm_transpilation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.html#module-iqm.qiskit_iqm.iqm_transpilation "iqm.qiskit_iqm.iqm_transpilation")

*class* iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass(*\*args*, *\*\*kwargs*)  
Bases: [`TransformationPass`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.TransformationPass "(in Qiskit v2.5)")

Transpiler pass that replaces all gates with given name in a circuit with a UnitaryGate.

Parameters:  
- **gate** – The name of the gate to replace.

- **unitary** – The unitary matrix to replace the gate with.

Attributes

Methods

|  |  |
|----|----|
| [`run`](#iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass.run "iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass.run") | Run the pass on the given circuit. |

run(*dag: [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")*) → [DAGCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")  
Run the pass on the given circuit.

Parameters:  
**dag** ([*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)"))

Return type:  
[*DAGCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.dagcircuit.DAGCircuit "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-7446cff5aa0e2322b4e4698e0476fcf3fa12752b.png)
