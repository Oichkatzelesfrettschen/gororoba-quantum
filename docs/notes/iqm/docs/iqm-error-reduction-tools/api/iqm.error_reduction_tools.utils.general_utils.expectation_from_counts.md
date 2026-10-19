> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.expectation_from_counts.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.expectation_from_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1e9f7ad873cf7414aefa8d76730576a07b9dc1c349e53068155d1cc080cd99ce.

# iqm.error_reduction_tools.utils.general_utils.expectation_from_counts

iqm.error_reduction_tools.utils.general_utils.expectation_from_counts(*counts*, *pauli_string=None*)  
Calculate expectation value of a Pauli string from measurement counts.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Dictionary mapping bitstrings to their counts (`int` or `float` after mitigation).

- **pauli_string** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – String of Pauli operators (‘I’ or ‘Z’) for each qubit. If `None`, defaults to all ‘Z’ operators.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Note

Bitstrings and Pauli strings both follow the same ordering (typically little-endian). This is consistent with `qiskit.result.sampled_expectation_value`.

Example

```
>>> counts = {"01": 10}
>>> pauli_string = "ZI"
>>> expectation_from_counts(counts, pauli_string)
1.0
```

Returns:  
Expectation value.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **pauli_string** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
