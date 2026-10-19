> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 de20abba3d7511568cdae1be77cfb57d6686fd6b026c6921336362cbe7c87ea4.

# IQMTarget

Module: [`iqm.qiskit_iqm.iqm_target`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.html#module-iqm.qiskit_iqm.iqm_target "iqm.qiskit_iqm.iqm_target")

*class* iqm.qiskit_iqm.iqm_target.IQMTarget(*description: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*, *dt: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *granularity: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *min_length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *pulse_alignment: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *acquire_alignment: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *qubit_properties: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *concurrent_measurements: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\*args*, *\*\*kwargs*)  
Bases: [`Target`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target "(in Qiskit v2.5)")

Transpilation target for an IQM architecture.

Contains the mapping of physical qubit name on the device to qubit index in the Target.

Parameters:  
- **architecture** (*DynamicQuantumArchitecture*) – Quantum architecture that defines the target.

- **component_to_idx** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Mapping from QPU component names to integer indices used by Qiskit to refer to them.

- **include_resonators** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to include computational resonators (and MOVE gates) in the target, if present in `architecture`.

- **include_fictional_czs** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to include “fictional” CZs that are not natively supported, but could be routed using MOVE.

- **metrics** (*ObservationFinder* *\|* *None*) – Optional calibration data and related quality metrics to improve the transpilation.

Attributes

|  |  |
|----|----|
| [`physical_qubits`](#iqm.qiskit_iqm.iqm_target.IQMTarget.physical_qubits "iqm.qiskit_iqm.iqm_target.IQMTarget.physical_qubits") | Return the ordered list of physical qubits in the target. |

Methods

|  |  |
|----|----|
| [`locus_to_idx`](#iqm.qiskit_iqm.iqm_target.IQMTarget.locus_to_idx "iqm.qiskit_iqm.iqm_target.IQMTarget.locus_to_idx") | Map the given locus to use component indices instead of component names. |
| [`restrict_to_qubits`](#iqm.qiskit_iqm.iqm_target.IQMTarget.restrict_to_qubits "iqm.qiskit_iqm.iqm_target.IQMTarget.restrict_to_qubits") | Generate a restricted transpilation target from this Target that only contains the given QPU components. |

locus_to_idx(*locus: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\]  
Map the given locus to use component indices instead of component names.

Parameters:  
**locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), …\]

*property* physical_qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Return the ordered list of physical qubits in the target.

restrict_to_qubits(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*) → [IQMTarget](#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget")  
Generate a restricted transpilation target from this Target that only contains the given QPU components.

Parameters:  
**qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – QPU components (qubits and computational resonators) to restrict the target to. Can be given either as component indices or component names.

Returns:  
Restricted target.

Return type:  
[*IQMTarget*](#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_target.IQMTarget](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-41807d3ab22f0942b269b1c07d14c114025fff9c.png)
