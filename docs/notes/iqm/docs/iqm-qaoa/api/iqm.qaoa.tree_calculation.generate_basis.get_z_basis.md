> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.generate_basis.get_z_basis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 644582b84291c7e64e916c67b42a91b92e64f900e5a10cfdc4a382be716e3ee5.

# get_z_basis

iqm.qaoa.tree_calculation.generate_basis.get_z_basis(*p*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/tree_calculation/generate_basis.py#L33-L47)  
Generate an array containing the Z basis on a qubit.

The Z basis basically means “all possible combinations of +1 and -1”, multiple times. In the calcultion, this comes from resolutions of identity between the QAOA layers, which is why the Z basis has \\2^{2p+1}\\ elements.

Parameters:  
**p** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers.

Returns:  
A [`numpy`](https://numpy.org/doc/stable/reference/index.html#module-numpy "(in NumPy v2.5)") array of size \\2^{2p+1}\\ containing the basis on the RCC.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), …\], [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")\[*int8*\]\]
