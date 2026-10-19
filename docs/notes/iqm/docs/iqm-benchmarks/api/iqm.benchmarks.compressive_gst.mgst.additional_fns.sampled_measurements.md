> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.sampled_measurements.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.sampled_measurements.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 35b68753afd2462d678852f4622863b32a00600ec0d83b74b6d5a4bb1aeaa051.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.sampled_measurements

iqm.benchmarks.compressive_gst.mgst.additional_fns.sampled_measurements(*y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *n_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute finite sample estimates of input probabilities.

Parameters:  
- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of measurement outcomes for different sequences, Each column contains the outcome probabilities for a fixed sequence

- **n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of samples for each experiment

Returns:  
2D array of sampled measurement outcomes for different sequences; Each column contains the sampled outcome probabilities for a fixed sequence

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The entries of each column of y form a probability distribution. From this distribution n random samples are drawn which give estimates for the initial probabilities. This simulates finite sample size data.
