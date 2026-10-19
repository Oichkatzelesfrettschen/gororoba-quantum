> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.perturbed_target_init.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.perturbed_target_init.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ceceb597f7810996942c67c2118ac733b1ed0ed84369185fc921ea18f3062c96.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.perturbed_target_init

iqm.benchmarks.compressive_gst.mgst.additional_fns.perturbed_target_init(*X_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generates a small random noise gate around the identity and applies it to the target gate.

The reason for using this gate as an initialization as opposed the target gate itself, is that the non-dominant Kraus operators we start with are now not zero, but small random matrices. Observations show that with this start, the non-dominant Kraus operators converge faster.

Parameters:  
- **X_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current gate estimate

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of Kraus operators per gate (“Kraus rank”) for the initialization

Returns:  
Each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
