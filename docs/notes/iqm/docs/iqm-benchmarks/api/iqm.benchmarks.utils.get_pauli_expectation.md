> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_pauli_expectation.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_pauli_expectation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dab3d1a0522b1faa5ec22b7f1c388e56fa95700aa96eaf6c43c5776bcec4e423.

# iqm.benchmarks.utils.get_pauli_expectation

iqm.benchmarks.utils.get_pauli_expectation(*counts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *pauli_label: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Gets an estimate of a Pauli expectation value for a given set of counts and a Pauli measurement label.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary of counts. \* NB: keys are assumed to have a single bitstring, i.e., coming from a single classical register.

- **pauli_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A Pauli measurement label, specified as a string of I, X, Y, Z characters.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If Pauli labels are not specified in terms of I, X, Y, Z characters.

Returns:  
The estimate of the Pauli expectation value.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
