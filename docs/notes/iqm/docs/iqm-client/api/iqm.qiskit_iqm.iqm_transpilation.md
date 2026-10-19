> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0eb0b73be3a26dd12911b558988ae1301b9fde6d8163a2392e31fdf203ce0940.

# iqm_transpilation

Full path: iqm.qiskit_iqm.iqm_transpilation

Transpilation tool to optimize the decomposition of single-qubit gates tailored to IQM hardware.

Functions

|  |  |
|----|----|
| [`optimize_single_qubit_gates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates.html#iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates "iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates")(circuit\[, ...\]) | Optimize number of single-qubit gates in a transpiled circuit exploiting the IQM specific gate set. |

Classes

|  |  |
|----|----|
| [`IQMOptimizeSingleQubitGates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.html#iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates "iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates") | Optimize the decomposition of single-qubit gates for the IQM gate set. |
| [`IQMReplaceGateWithUnitaryPass`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass.html#iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass "iqm.qiskit_iqm.iqm_transpilation.IQMReplaceGateWithUnitaryPass") | Transpiler pass that replaces all gates with given name in a circuit with a UnitaryGate. |

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_transpilation](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-d0b4145cd09db9ab683695e8757f540d462000e6.png)
