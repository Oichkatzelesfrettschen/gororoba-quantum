> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.local_shadow_tomography.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.local_shadow_tomography.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1df2ef08d3e174ee575eb383e5181c1de8e3e840cc39e450b0446b8fe3cf3d02.

# iqm.benchmarks.utils_shadows.local_shadow_tomography

iqm.benchmarks.utils_shadows.local_shadow_tomography(*qc: QuantumCircuit*, *n_unitaries: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *active_qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *measure_other: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *measure_other_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *clifford_or_haar: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['clifford', 'haar'\] = 'clifford'*, *cliffords_1q: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), QuantumCircuit\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[QuantumCircuit\]\]  
Prepares the circuits to perform local Haar or Clifford shadow tomography.

Parameters:  
- **qc** (*QuantumCircuit*) – The quantum circuit to which random unitaries are appended.

- **n_unitaries** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of local random unitaries used.

- **active_qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The Sequence of active qubits.

- **measure_other** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Whether to measure other qubits in the qc QuantumCircuit.

- **measure_other_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Name of the classical register to assign measure_other.

- **clifford_or_haar** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['clifford',* *'haar'\]*) – Whether to use Clifford or Haar random 1Q gates.

- **cliffords_1q** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *QuantumCircuit\]* *\|* *None*) – Dictionary of 1-qubit Cliffords in terms of IQM-native r and CZ gates.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If clifford_or_haar is not “clifford” or “haar”.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If cliffords_1q is None and clifford_or_haar is “clifford”.

Returns:  
- Random unitaries, in either format

  - Unitary gate (numpy ndarray), composed of local unitaries for each random initialisation and qubit, if clifford_or_haar == ‘haar’.

  - Dictionary of lists of Clifford labels corresponding to each RM, keys being str(qubit), if clifford_or_haar == ‘clifford’.

- List of tomography circuits.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*QuantumCircuit*\]\]
