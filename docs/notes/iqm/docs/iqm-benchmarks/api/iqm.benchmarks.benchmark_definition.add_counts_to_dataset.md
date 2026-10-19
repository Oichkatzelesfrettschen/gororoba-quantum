> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.add_counts_to_dataset.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.add_counts_to_dataset.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ed1547b0c96c488a62b50960d6130db68e4e2486a8fe26f630c8f7ffeeaf736b.

# iqm.benchmarks.benchmark_definition.add_counts_to_dataset

iqm.benchmarks.benchmark_definition.add_counts_to_dataset(*counts: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *dataset: Dataset*) → Dataset  
Adds the counts from a cortex job result to the given dataset.

If counts with the same identifier are already present in the old dataset, then both counts are added together.

Parameters:  
- **counts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – A list of dictionaries with counts of bitstrings.

- **identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A string to identify the current data, for instance the qubit layout.

- **dataset** (*Dataset*) – Dataset to add results to.

Returns:  
A merged dataset where the new counts are added the input dataset

Return type:  
*Dataset*
