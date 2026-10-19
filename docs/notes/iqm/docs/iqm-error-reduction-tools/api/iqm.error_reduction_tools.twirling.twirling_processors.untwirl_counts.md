> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8e1813e04f64caa84719681aaab126741c5d241d0b58b771203a88b165bc989a.

# iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts

iqm.error_reduction_tools.twirling.twirling_processors.untwirl_counts(*counts*, *rot_string*)  
Apply untwirling to measurement counts.

Flips bits in measurement bitstrings according to a readout twirling string. For each qubit where the twirling operation was ‘X’, the corresponding measurement bit is flipped (0 ↔ 1).

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Dictionary of measurement counts.

- **rot_string** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – List of readout twirling Pauli strings or a string (BIG endian, so the opposite of Qiskit’s little endian).

Returns:  
Dictionary of untwirled counts.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If rot_string length doesn’t match number of qubits.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

Example

```
>>> counts = {'000': 10, '001': 5, '010': 3}
>>> rot_string = "XII"
>>> untwirl_counts(counts, rot_string)
{'001': 10, '000': 5, '011': 3}
```
