> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.outcome_probs_from_files.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.outcome_probs_from_files.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 177285e957e4783cbdb9e45e1cac6042d084174f821a1ae55f765cb5a2410904.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.outcome_probs_from_files

iqm.benchmarks.compressive_gst.mgst.additional_fns.outcome_probs_from_files(*folder_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *basis_dict: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *N: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Searches a specified folder for .txt files containing circuit outcomes and combines the results.

Each text file needs to have line in the following format: 1: 1,0,1,0,1,1,0,0,0 2: 1,1,1,1,0,1,1,1,1 Here the first number specifies the circuit and basis outcome of each shot is written to the right.

Parameters:  
- **folder_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The relative or absolute name of the data folder

- **basis_dict** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Translation between label for each shot in the .txt files and the numbering of the POVM element. Example (two qubits): {“00”: 0, “01”: 1, “10”: 2, “11”: 3,}

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of POVM elements in the data set

- **N** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of circuits in the data set

Returns:  
- 2D array of measurement outcomes for all measured sequences; Each column contains the outcome probabilities for a fixed sequence

- The average number of shots per circuit after combining data sets

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]
