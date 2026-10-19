> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f26d08f9bb56089d06351ea80b4750d2c77aa9552cc8257fdea1bdfcecb4c18b.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix

iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix(*input_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *num_circ_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *num_pauli_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]  
Convert a flat list to a matrix of shape (num_circ_samples, num_pauli_samples).

Parameters:  
- **input_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – the input flat list

- **num_circ_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the number of sets of Pauli-dressed circuit samples

- **num_pauli_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the number of Pauli samples per circuit

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Length of passed list is not (num_circ_samples \* num_pauli_samples).

Returns:  
The output matrix

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]
