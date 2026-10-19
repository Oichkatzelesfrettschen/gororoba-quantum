> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.calculate_t.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.calculate_t.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 993a7e29bbbe3484e2f516f904084ccfb97f70f344f99576be413c8423fa1219.

# calculate_t

iqm.qaoa.tree_calculation.generate_basis.calculate_t(*v1*)  
Given a vector `v1`, calculate its symmetry sector.

For an input vector `v1` of length \\2m\\, the symmetry sector \\t\\ is the smallest integer, such that removing \\t\\ elements from the beginning and the end of `v1` makes the array symmetric with respect to flip, i.e., a palindrome. In other words, it’s the smallest integer, such that starting from the middle of `v1`, the first \\m-t\\ elements to the left equal the first \\m-t\\ elements to the right. By definition \\t\\ lies between 0 and \\m\\ (included). Some examples:

| Input array                     | Half of input length \\m\\ | Output \\t\\ |
|---------------------------------|----------------------------|--------------|
| \[-1, **1, 1, 1, 1**, 1\]       | 3                          | 1            |
| \[-1, 1, **-1, -1**, -1, 1\]    | 3                          | 2            |
| \[**-1, 1, -1, -1, 1, -1**\]    | 3                          | 0            |
| \[-1, 1, -1, 1, 1, 1\]          | 3                          | 3            |
| \[-1, **1, 1**, 1\]             | 2                          | 1            |
| \[-1, **1, 1, 1, 1, 1, 1**, 1\] | 4                          | 1            |

Parameters:  
**v1** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The array whose symmetry sector we want to calculate.

Returns:  
The symmetry sector of the input array.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `v1` does not have the proper shape (1D array of even length).

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `v1` contains other entries than +1 and -1

Return type:  
*int64*
