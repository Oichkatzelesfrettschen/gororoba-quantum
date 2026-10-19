> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_len_seq.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_len_seq.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0cd5cecf0fbce949d92aca16bc284d7046f1a96d6312ed66e22c3c5829cef63b.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.random_len_seq

iqm.benchmarks.compressive_gst.mgst.additional_fns.random_len_seq(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *min_l: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *max_l: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *N: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate random gate sequence instructions.

These contain sequences of different lengths, the lengths are drawn uniformly at random from (min_l, …, max_l).

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **min_l** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Minimum sequence length

- **max_l** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Maximum sequence length

- **N** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of random sequences

Returns:  
2D array where each row contains the gate indices of a gate sequence

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
