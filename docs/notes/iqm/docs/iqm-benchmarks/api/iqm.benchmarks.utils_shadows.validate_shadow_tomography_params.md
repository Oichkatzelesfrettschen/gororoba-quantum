> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.validate_shadow_tomography_params.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.validate_shadow_tomography_params.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f507a68705f46917c8207586d71f2e52e89984bb919cfd89423f3003adb68325.

# iqm.benchmarks.utils_shadows.validate_shadow_tomography_params

iqm.benchmarks.utils_shadows.validate_shadow_tomography_params(*clifford_or_haar: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['clifford', 'haar'\]*, *cliffords_1q: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validates the parameters for shadow tomography functions.

Parameters:  
- **clifford_or_haar** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['clifford',* *'haar'\]*) – Whether to use Clifford or Haar random 1Q gates.

- **cliffords_1q** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]* *\|* *None*) – Dictionary of 1-qubit Cliffords in terms of IQM-native r and CZ gates.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If clifford_or_haar is not “clifford” or “haar”.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If cliffords_1q is None and clifford_or_haar is “clifford”.

Return type:  
None
