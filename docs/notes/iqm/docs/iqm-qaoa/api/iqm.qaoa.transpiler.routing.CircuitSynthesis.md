> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.CircuitSynthesis.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.CircuitSynthesis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b35ead7fe6470cab3c90a2dcde80ef8e4c2ab85ababcce7f6dba9a55f7f4f771.

# CircuitSynthesis

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.CircuitSynthesis(*mapping*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L800-L1168)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Synthesize a quantum circuit using parity-based interaction mapping.

The hardware-to-parity mapping is saved in an internal [`ParityMapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.ParityMapping.html#iqm.qaoa.transpiler.routing.ParityMapping "iqm.qaoa.transpiler.routing.ParityMapping").

There are two main regimes to use the class:

1.  If a diagonal Hamiltonian is known beforehand, only the method [`cnot()`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot "iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot") is used for constructing the circuit. When a Qiskit [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") is created with [`build_qiskit()`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit "iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit"), RZ gates are included automatically based on the provided diagonal Hamiltonian (as a [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") object).

2.  Alternatively, one may manually insert CNOT and RZ gates. The attribute `possible_ints` contains a set of all possible interactions that could be implemented given the CNOT gates (so it can be used to construct a Hamiltonian). The attribute `constructed_hamiltonian_bp` contains the Hamiltonian that has been implicitly constructed by manually applying the RZ gates.

An external algorithm might be needed to determine the optimal placement of the CNOT gates.

Parameters:  
**mapping** ([*ParityMapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.ParityMapping.html#iqm.qaoa.transpiler.routing.ParityMapping "iqm.qaoa.transpiler.routing.ParityMapping")) – Initial parity mapping used to construct the circuit.

Attributes

|  |  |
|----|----|
| [`cnot_list`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot_list "iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot_list") | Returns the list of all CNOT gates applied throughout the circuit synthesis process. |
| [`computing`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.computing "iqm.qaoa.transpiler.routing.CircuitSynthesis.computing") | A flag signalling that the circuit synthesis is currently in the 'computing' mode. |

Methods

|  |  |
|----|----|
| [`begin_uncompute`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.begin_uncompute "iqm.qaoa.transpiler.routing.CircuitSynthesis.begin_uncompute") | Calling this ends the computing phase of the circuit synthesis and begins the uncomputing phase. |
| [`build_qiskit`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit "iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit") | Build a full QAOA circuit from the synthesized parity-based circuit construction. |
| [`build_qiskit_phase_separator`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit_phase_separator "iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit_phase_separator") | Builds the synthesized quantum circuit. |
| [`cnot`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot "iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot") | Adds a CNOT gate to the synthesized circuit. |
| [`cnot_depth`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot_depth "iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot_depth") | CNOT depth of the synthesized phase separator. |
| [`rz`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.rz "iqm.qaoa.transpiler.routing.CircuitSynthesis.rz") | Adds an RZ rotation gate associated with a parity interaction. |
| [`uncompute_parities`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.uncompute_parities "iqm.qaoa.transpiler.routing.CircuitSynthesis.uncompute_parities") | Adds CNOT gates to the circuit synthesis to uncompute the parity mapping back to `self.initial_mapping`. |

*class* CNOTStep(*control*, *target*, *allow_interactions=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L823-L837)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A custom dataclass representing one CNOT step in the circuit synthesis.

Parameters:  
- **control** (*HardQubit*)

- **target** (*HardQubit*)

- **allow_interactions** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

control  
The control qubit of the CNOT gate.

Type:  
HardQubit

target  
The target qubit of the CNOT gate.

Type:  
HardQubit

allow_interactions  
True iff we permit the circuit synthesis algorithm to add RZ gates directly after this CNOT gate. This is useful for better control over the structure of the quantum circuit.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

*property* computing*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
A flag signalling that the circuit synthesis is currently in the ‘computing’ mode.

*property* cnot_list*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[CNOTStep](#iqm.qaoa.transpiler.routing.CircuitSynthesis.CNOTStep "iqm.qaoa.transpiler.routing.CircuitSynthesis.CNOTStep")\]*  
Returns the list of all CNOT gates applied throughout the circuit synthesis process.

cnot_depth(*include_uncompute=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L885-L897)  
CNOT depth of the synthesized phase separator.

Parameters:  
**include_uncompute** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, counts compute + uncompute CNOTs. If `False`, counts only the compute half.

Returns:  
The CNOT-only depth of the synthesized phase separator.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

begin_uncompute()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L899-L908)  
Calling this ends the computing phase of the circuit synthesis and begins the uncomputing phase.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If uncomputation has already begun previously.

Return type:  
None

cnot(*control*, *target*, *allow_int_after=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L910-L927)  
Adds a CNOT gate to the synthesized circuit.

Updates the internal parity mapping and records the interaction.

Parameters:  
- **control** (*HardQubit*) – Control hardware qubit.

- **target** (*HardQubit*) – Target hardware qubit.

- **allow_int_after** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – True iff interactions are allowed to take place immediately after the CNOT gate.

Return type:  
None

rz(*interaction*, *qubit*, *allow_overwrite=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L929-L962)  
Adds an RZ rotation gate associated with a parity interaction.

Also, adds an interaction term to the internal [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") implied by applying the RZ gate. This internal [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") may be accessed by the attribute `self.constructed_hamiltonian_bp`.

Parameters:  
- **interaction** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) –

  The interaction strength corresponding to the RZ gate.

  Warning

  The input is the **interaction strength** corresponding to the RZ gate, i.e., the term that will be added to the Hamiltonian. The rotation angle of the RZ gate is this value times the γ QAOA angle.

- **qubit** (*HardQubit*) – Hardware qubit on which the RZ gate is applied.

- **allow_overwrite** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, allows overwriting an existing interaction term in the internal [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)").

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the interaction term already exists in the internal [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") and overwrite is disabled

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the qubit on which the RZ rotation acts carries no parity information.

- [**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If attempted to place an RZ gate during uncomputation.

Return type:  
None

uncompute_parities()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L964-L972)  
Adds CNOT gates to the circuit synthesis to uncompute the parity mapping back to `self.initial_mapping`.

Currently, the uncomputing is very primitive. It just mirrors the CNOTs that were added in the first half of the circuit.

Return type:  
None

build_qiskit_phase_separator(*gamma*, *interactions=None*, *show_parities=False*, *remove_cnots=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L974-L1084)  
Builds the synthesized quantum circuit.

This only builds the synthesized part of the quantum circuit. For constructing the entire QAOA circuit, use [`build_qiskit()`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit "iqm.qaoa.transpiler.routing.CircuitSynthesis.build_qiskit").

The circuit is constructed using CNOT gates in the order in which the method [`cnot()`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot "iqm.qaoa.transpiler.routing.CircuitSynthesis.cnot") was called, acting on the respective qubits.

- If `interactions` is not provided, the circuit inserts an RZ gate wherever it was placed using the [`rz()`](#iqm.qaoa.transpiler.routing.CircuitSynthesis.rz "iqm.qaoa.transpiler.routing.CircuitSynthesis.rz") method.

- If `interactions` is provided, the circuit **ignores** the manually placed RZ gates (and raises a warning if some were manually placed). It then places RZ gates automatically whenever a qubit carries one of the parities from `interactions`. A warning is raised if not all `interactions` are executed.

Parameters:  
- **gamma** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Global scaling factor for interaction strengths (e.g., a parameter of the QAOA ansatz).

- **interactions** ([*BinaryPolynomial*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") *\|* *None*) – Optional Hamiltonian of interactions. If `None`, uses internally constructed interactions. The `varytpe` of the interactions has to be `"SPIN"` and it is assumed that the quantum state \\\|1\rangle\\ corresponds to the value -1 in the polynomial (and \\\|0\rangle\\ corresponds to 1). This comes from seeing the [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") as describing a Hamiltonian made up of sums of products of the Z Pauli gate. The reason we don’t accept the input with `vartype` `"BINARY"` is that the conversion from `"BINARY"` to `"SPIN"` by default uses the opposite convention (where \\\|1\rangle\\ corresponds to the value 1 in the polynomial and \\\|0\rangle\\ to -1). This could lead to silent errors.

- **show_parities** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff set to `True`, adds identity gates throughout the circuit whose labels show the parity encoded in the qubits.

- **remove_cnots** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff set to `True`, the uncomputation is skipped and the computation happens in the opposite order. This saves 2-qubit gates, if this is the first phase seprator applied onto the initial state (which is presumably the \\\|+\rangle\\ state).

Returns:  
A Qiskit [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") implementing the synthesized quantum circuit.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the input `interactions` has `vartype` set to `"BINARY"`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `remove_cnots` is set to `True`, but the circuit synthesis contains no uncomputation.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

build_qiskit(*betas*, *gammas*, *interactions=None*, *measurement=True*, *remove_cnots_first_layer=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L1086-L1168)  
Build a full QAOA circuit from the synthesized parity-based circuit construction.

This method assembles the complete QAOA circuit by repeatedly composing the parity-based phase separator (constructed via CNOT and RZ operations) with the mixer (RX rotations). It assumes that all parity transformations have been properly uncomputed before execution, i.e., the parity mapping has returned to the initial configuration up to a permutation of hardware qubits.

Parameters:  
- **betas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – List of QAOA mixer angles (RX rotations).

- **gammas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – List of QAOA phase separator angles.

- **interactions** ([*BinaryPolynomial*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") *\|* *None*) – The problem Hamiltonian as a [`BinaryPolynomial`](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)") in SPIN representation.

- **measurement** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, adds a measurement step.

- **remove_cnots_first_layer** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, the first layer of QAOA swaps its computation and uncomputation. Then, the uncomputation step is completely removed, since it consists purely of CNOT gates applied directly onto the \\\|+\rangle\\ state, which has no effect.

Returns:  
A [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") implementing the full synthesized QAOA circuit.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `betas` and `gammas` do not have the same length.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the parity mapping has not been fully uncomputed back to the initial state (up to permutation of hardware qubits).

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.CircuitSynthesis](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-d0e32f138af974210b2f5b42c31603170ecc599f.png)
