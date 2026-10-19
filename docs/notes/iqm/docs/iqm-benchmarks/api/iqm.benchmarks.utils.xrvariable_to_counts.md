> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.xrvariable_to_counts.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.xrvariable_to_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6b075738f054966b56a83d805674ece43613c34cd7595cc761c3d4c82ae3070b.

# iqm.benchmarks.utils.xrvariable_to_counts

iqm.benchmarks.utils.xrvariable_to_counts(*dataset: Dataset*, *identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *counts_range: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Retrieve counts from xarray dataset.

Parameters:  
- **dataset** (*Dataset*) – the dataset to extract counts from.

- **identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – the identifier for the dataset counts.

- **counts_range** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the range of counts to extract (e.g., the amount of circuits that were executed).

Returns:  
A list of counts dictionaries from the dataset.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
