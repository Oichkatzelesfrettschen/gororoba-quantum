> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 df9d779b2f0cbb9ef8d096d9edad29b2bf9513bed3078d9b416a7f42f3a7ba74.

# quantum_hardware

Full path: iqm.qaoa.transpiler.quantum_hardware

The module for classes representing various QPU architectures.

The module also contains four type aliases, which are imported by other modules for more clear type hinting.

Module Attributes

|  |  |
|----|----|
| [`LogQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogQubit.html#iqm.qaoa.transpiler.quantum_hardware.LogQubit "iqm.qaoa.transpiler.quantum_hardware.LogQubit") | A custom type alias for `Variable` to refer to logical / problem qubits. |
| [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") | A custom type alias for [`int`](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") to refer to hardware qubits. |
| [`LogEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogEdge.html#iqm.qaoa.transpiler.quantum_hardware.LogEdge "iqm.qaoa.transpiler.quantum_hardware.LogEdge") | A custom type alias for [`frozenset`](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)") of [`LogQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogQubit.html#iqm.qaoa.transpiler.quantum_hardware.LogQubit "iqm.qaoa.transpiler.quantum_hardware.LogQubit") to refer to interactions between logical qubits. |
| [`HardEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardEdge.html#iqm.qaoa.transpiler.quantum_hardware.HardEdge "iqm.qaoa.transpiler.quantum_hardware.HardEdge") | A custom type alias of [`frozenset`](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)") of [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") to refer to interactions between hardware qubits. |

Classes

|  |  |
|----|----|
| [`CrystalQPUFromBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend.html#iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend "iqm.qaoa.transpiler.quantum_hardware.CrystalQPUFromBackend") | Class for a QPU with square lattice topology, initialited from a Qiskit backend object. |
| [`Grid2DQPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.html#iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU "iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU") | Class for 2D rectangular QPU. |
| [`LineQPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LineQPU.html#iqm.qaoa.transpiler.quantum_hardware.LineQPU "iqm.qaoa.transpiler.quantum_hardware.LineQPU") | A linear QPU (qubits on a line). |
| [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU") | A parent class for all QPU architectures. |
| [`StarQPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.StarQPU.html#iqm.qaoa.transpiler.quantum_hardware.StarQPU "iqm.qaoa.transpiler.quantum_hardware.StarQPU") | A star-shaped QPU (Daneb, Sirius, ...). |

Exceptions

|  |  |
|----|----|
| [`NonCrystalSQAError`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.NonCrystalSQAError.html#iqm.qaoa.transpiler.quantum_hardware.NonCrystalSQAError "iqm.qaoa.transpiler.quantum_hardware.NonCrystalSQAError") | Custom error class for errors coming from the QPU topology not matching the Crystal architecture. |

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-84ddf6aa5bc6469aebc7c903eb2e0029a10deb26.png)
