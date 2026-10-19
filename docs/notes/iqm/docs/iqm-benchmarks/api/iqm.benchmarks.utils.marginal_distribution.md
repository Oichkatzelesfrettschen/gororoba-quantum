> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.marginal_distribution.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.marginal_distribution.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19e3976f2b08d36b202dda0704df729982beb9f9ee3e21f9b3b4d72b0a16f5a8.

# iqm.benchmarks.utils.marginal_distribution

iqm.benchmarks.utils.marginal_distribution(*prob_dist_or_counts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *indices: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Compute the marginal distribution over specified bits (indices).

Parameters:  
- **prob_dist_or_counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A dictionary with keys being bitstrings, and values are either probabilities or counts.

- **indices** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of bit indices to marginalize over.

Returns:  
A dictionary representing the marginal distribution over the specified bits.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
