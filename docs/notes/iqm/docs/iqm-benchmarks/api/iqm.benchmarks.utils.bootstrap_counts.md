> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.bootstrap_counts.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.bootstrap_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b8fd9b7f00871f03d234dd961d9dc224d3a730f0467a6789e872c633caaee8f4.

# iqm.benchmarks.utils.bootstrap_counts

iqm.benchmarks.utils.bootstrap_counts(*original_counts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *num_bootstrap_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 100*, *rgen: [Generator](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *include_original_counts: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Returns num_bootstrap_samples resampled copies of the original_counts.

Parameters:  
- **original_counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The original counts to bootstrap from.

- **num_bootstrap_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of bootstrapping samples to generate.

- **rgen** ([*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)") *\|* *None*) – Random number generator to use. If None, use Numpy’s `default_rng()`.

- **include_original_counts** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to include the original counts in the returned bootstrapped count samples.

Returns:  
Bootstrapped counts.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
