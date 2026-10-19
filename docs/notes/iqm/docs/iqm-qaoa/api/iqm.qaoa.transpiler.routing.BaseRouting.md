> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseRouting.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseRouting.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f18e767913c940e7e97f4a219f359e0a144b28e2a8a43de34157962cf7c328b8.

# BaseRouting

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.BaseRouting(*problem_bqm*, *qpu*, *initial_mapping=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L389-L432)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

The abstract base class for various routing sub-classes.

Generally speaking, routing refers to the process of ‘moving’ the problem qubits around the QPU to allow the execution of the interactions between the problem qubits. The standard way to do this is with *swap* gates, but there are special variations e.g., if using *move* gates on a computational resonator.

Attributes

|  |  |
|----|----|
| [`layers`](#iqm.qaoa.transpiler.routing.BaseRouting.layers "iqm.qaoa.transpiler.routing.BaseRouting.layers") | The list of layers of the routing object. |

Methods

|  |  |
|----|----|
| [`build_qiskit`](#iqm.qaoa.transpiler.routing.BaseRouting.build_qiskit "iqm.qaoa.transpiler.routing.BaseRouting.build_qiskit") | The method to construct a qiskit circuit out of the routing, given a list of `gammas` and `betas` angles. |

Parameters:  
- **problem_bqm** (*BinaryQuadraticModel*)

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU"))

- **initial_mapping** ([*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") *\|* *None*)

*abstract property* layers*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
The list of layers of the routing object.

Different subclasses of [`BaseRouting`](#iqm.qaoa.transpiler.routing.BaseRouting "iqm.qaoa.transpiler.routing.BaseRouting") represent the individual layers differently, which is why the type of the layers here is the generic `Any`.

*abstractmethod* build_qiskit(*betas*, *gammas*, *measurement=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L419-L432)  
The method to construct a qiskit circuit out of the routing, given a list of `gammas` and `betas` angles.

Parameters:  
- **betas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters (angles) to be used in the mixer.

- **gammas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters (angles) to be used in the phase separator.

- **measurement** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should the quantum circuit end with a measurement of all qubits?

Returns:  
A qiskit circuit implementing the QAOA.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.BaseRouting](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-fa29b87623b8e0884d62e25a62bb2f04409fd81a.png)
