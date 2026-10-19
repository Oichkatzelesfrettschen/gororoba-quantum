> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_local_shadow.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_local_shadow.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e706d8fd8e80a8148762f14c23d99a2d32db7a1817896cc284536a616e4af2a3.

# iqm.benchmarks.utils_shadows.get_local_shadow

iqm.benchmarks.utils_shadows.get_local_shadow(*counts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *unitary_arg: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *subsystem_bit_indices: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *clifford_or_haar: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['clifford', 'haar'\] = 'clifford'*, *cliffords_1q: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Constructs shadows for each individual initialisation.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary of bit-string counts.

- **unitary_arg** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Local random unitaries used for a given initialisation, either specified as - A numpy array, or - A Sequence of Clifford labels.

- **subsystem_bit_indices** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Bit indices in the counts of the subsystem to construct the shadow of.

- **clifford_or_haar** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['clifford',* *'haar'\]*) – Whether to use Clifford or Haar random 1Q gates.

- **cliffords_1q** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]* *\|* *None*) – Dictionary of 1-qubit Cliffords in terms of IQM-native r and CZ gates

Returns:  
Shadow of considered subsystem.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
