> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.local_basis.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.local_basis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c0179435cf8283dfea4204349a8e6d7e5656296f6adb63b5f5540528a525e81c.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.local_basis

iqm.benchmarks.compressive_gst.mgst.low_level_jit.local_basis(*x: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *b: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Convert a base-10 integer to an integer in a specified base with a fixed number of digits.

This function takes an integer x in base-10 and converts it to base b. The result is returned as an array of length length with leading zeros.

Parameters:  
- **x** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The input number in base-10 to be converted.

- **b** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The target base to convert the input number to.

- **length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of output digits in the target base representation.

Returns:  
A numpy array of integers representing the base-b digits of the converted number, with leading zeros if necessary. The length of the array is length.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
