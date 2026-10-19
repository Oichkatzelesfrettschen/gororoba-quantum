> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.exponential_rb.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.exponential_rb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0645f2fe10dce168789c40ebe11cf1d4a3b2d85b5d503a4468054a87efe6b2a9.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.exponential_rb

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.exponential_rb(*depths: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *depolarization_probability: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *offset: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *amplitude: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Fit function for interleaved/non-interleaved RB.

Parameters:  
- **depths** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – the depths of the RB experiment

- **depolarization_probability** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – the depolarization value (1-p) of the RB decay

- **offset** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – the offset of the RB decay

- **amplitude** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – the amplitude of the RB decay

Returns:  
The exponential fit function

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
