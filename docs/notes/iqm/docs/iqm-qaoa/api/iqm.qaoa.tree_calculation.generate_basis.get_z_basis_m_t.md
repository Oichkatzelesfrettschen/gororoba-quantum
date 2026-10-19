> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m_t.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m_t.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 848f3316d9f7345854dfd7a2f8af5618e36d24b8b9aec7673ab061e7409302ca.

# get_z_basis_m_t

iqm.qaoa.tree_calculation.generate_basis.get_z_basis_m_t(*basis*)  
Takes an array containing (all) basis vectors and sorts them into a list based on their symmetry sector.

The input is assumed to be a (full) array of basis vectors.

Parameters:  
**basis** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The array containing the basis vectors to be sorted.

Returns:  
A list of [`numpy`](https://numpy.org/doc/stable/reference/index.html#module-numpy "(in NumPy v2.5)") arrays, each of which contains the basis vectors belonging to the corresponding symmetry sector.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), …\], [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[*int8*\]\]\]
