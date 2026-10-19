> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec5021b036bb8342914863449bed154cc811f5bd10b5608d478b30116e7b7fda.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations

iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *noisy_counts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *ideal_counts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *num_circ_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *num_pauli_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Estimates the polarization for a list of noisy counts with respect to corresponding ideal counts.

The polarization here is a rescaling of the average fidelity, that corrects for few-qubit effects

Parameters:  
- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits being benchmarked

- **noisy_counts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The list of counts coming from real execution

- **ideal_counts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The list of counts coming from simulated, ideal execution

- **num_circ_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number circuit of samples used to estimate the polarization

- **num_pauli_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of pauli samples per circuit sample used to estimate the polarization

Returns:  
The polarizations for each circuit sample of the given sequence length

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
