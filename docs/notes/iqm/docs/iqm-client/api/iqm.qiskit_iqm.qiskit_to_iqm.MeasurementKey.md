> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 67d3d5685f8036f079a0ed617a1a9291b6f05158c243677c7619b2e88a43fac6.

# MeasurementKey

Module: [`iqm.qiskit_iqm.qiskit_to_iqm`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.html#module-iqm.qiskit_iqm.qiskit_to_iqm "iqm.qiskit_iqm.qiskit_to_iqm")

*class* iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey(*creg_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *creg_len: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *creg_idx: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *clbit_idx: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Unique key associated with a measurement instruction.

Qiskit stores the results of quantum measurements in classical registers consisting of bits. The circuit execution results are presented as bitstrings of a certain structure so that the classical register and the index within that register for each bit is implied from its position in the bitstring.

For example, if you have two classical registers in the circuit with lengths 3 and 2, then the measurement results will look like ‘01 101’ if the classical register of length 3 was added to the circuit first, and ‘101 01’ otherwise. If a bit in a classical register is not used in any measurement operation it will still show up in the results with the default value of ‘0’.

To be able to handle measurement results in a Qiskit-friendly way, we need to keep around some information about how the circuit was constructed. This can, for example, be achieved by keeping around the original Qiskit quantum circuit and using it when constructing the results in `qiskit_IQMJob`. This should be done so that the circuit is saved on the server side and not in `IQMJob`, since otherwise users will not be able to retrieve results from a detached Python environment solely based on the job id. Another option is to use measurement key strings to store the required info. Qiskit does not use measurement keys, so we are free to use them internally in the communication with the IQM Server, and can encode the necessary information in them.

This class encapsulates the necessary info, and provides methods to transform between this representation and the measurement key string representation.

Parameters:  
- **creg_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the classical register

- **creg_len** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – number of bits in the classical register

- **creg_idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Index of the classical register in the circuit. Determines the order in which this register was added to the circuit relative to the others.

- **clbit_idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – index of the classical bit within the classical register

Attributes

|             |     |
|-------------|-----|
| `creg_name` |     |
| `creg_len`  |     |
| `creg_idx`  |     |
| `clbit_idx` |     |

Methods

|  |  |
|----|----|
| [`from_clbit`](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.from_clbit "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.from_clbit") | Create a MeasurementKey for a classical bit in a quantum circuit. |
| [`from_string`](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.from_string "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey.from_string") | Create a MeasurementKey from its string representation. |

*classmethod* from_string(*string: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [MeasurementKey](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey")  
Create a MeasurementKey from its string representation.

Parameters:  
**string** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*MeasurementKey*](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey")

*classmethod* from_clbit(*clbit: [Clbit](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Clbit "(in Qiskit v2.5)")*, *circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*) → [MeasurementKey](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey")  
Create a MeasurementKey for a classical bit in a quantum circuit.

Parameters:  
- **clbit** ([*Clbit*](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Clbit "(in Qiskit v2.5)"))

- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)"))

Return type:  
[*MeasurementKey*](#iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey "iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey")

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.qiskit_to_iqm.MeasurementKey](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-aae2de10339a30c6d7940edc0870e4fa2b001aa1.png)
