> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_big_h_fixed_points_from_scratch.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_big_h_fixed_points_from_scratch.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 07124af5dcf139d7aa4b555fbe4801bbe59edffe85554d87b8e5ed5f8a14c0ed.

# get_big_h_fixed_points_from_scratch

iqm.qaoa.tree_calculation.tree_calculation.get_big_h_fixed_points_from_scratch(*p*, *big_d*, *h*, *big_gamma*, *big_beta*, *basis_list_t=None*)  
Recursively implements equations (A23), (A24) and (A25) to obtain the fixed points of the calculation.

Parameters:  
- **p** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers, corresponding to the largest order of the fixed points that we want to calculate.

- **big_d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Graph regularity minus one. Note that in expressions with \\Gamma\\, we use \\\sqrt{D}\\ in the denominator instead of \\\sqrt{d} = \sqrt{D+1}\\, but this just introduces a small factor to the gamma angles.

- **h** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The local field of the problem.

- **big_gamma** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The array of the \\\gamma\\ angles of the QAOA. The full array, with a 0 in the middle (see A8).

- **big_beta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The array of the \\\beta\\ angles of the QAOA. The full array, with a 0 in the middle (see A8).

- **basis_list_t** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[int8\]\]\]\]* *\|* *None*) – For some compatibility, the basis list sorted by the symmetry sectors can be pregenerated and given as an input. Otherwise it’s generated internally.

Returns:  
A list of lists of the fixed points. The outer index labels the order of the fixed point and the inner index labels its input. Therefore taking \[3\]\[0\] of the output returns \\H^{(3)}\_{d-1}(\[-1, -1, -1, 1, -1, -1\])\\ because \[-1, -1, -1, 1, -1, -1\] is presumably the first basis state of 3 variables in symmetry sector 3.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), …\], [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[*complex128*\]\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), …\], [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[*complex128*\]\]\]\]
