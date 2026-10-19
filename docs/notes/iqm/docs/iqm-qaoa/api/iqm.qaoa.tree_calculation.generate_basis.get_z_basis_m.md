> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2aef9b3beb2a5dd59dd7ccea56caf77229be42528c06022992c427af25b8c3f2.

# get_z_basis_m

iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m(*m*)  
Generate an array containing the Z basis on a qubit.

Basically, this function is the same as [`get_z_basis()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis.html#iqm.qaoa.tree_calculation.generate_basis.get_z_basis "iqm.qaoa.tree_calculation.generate_basis.get_z_basis"), but instead of specifying `p`, here one specifies the length of the basis elements directly. Effectively, the function implements the following line of code, but in a Numba-compatible way.

``` python
return np.array(list(itertools.product([-1, 1], repeat=2 * m)), dtype=np.int8)
```

Parameters:  
**m** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The length of the basis elements to be generated. There will be \\4^m\\ total elements generated.

Returns:  
A [`numpy`](https://numpy.org/doc/stable/reference/index.html#module-numpy "(in NumPy v2.5)") array of size \\4^m \times 2m\\ containing the Z basis.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), …\], [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[*int8*\]\]
