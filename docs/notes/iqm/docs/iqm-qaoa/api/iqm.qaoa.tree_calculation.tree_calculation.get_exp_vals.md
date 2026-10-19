> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_exp_vals.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_exp_vals.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c4024447b8acc99c29905ee634629f92d9841d5d56a91f86c08271525fe780d4.

# get_exp_vals

iqm.qaoa.tree_calculation.tree_calculation.get_exp_vals(*p*, *big_d*, *h*, *big_gamma*, *big_beta*, *basis_list_t=None*)  
Calculates the expectation values of \<Z\> and \<ZZ\> terms.

Basically, this reproduces the full calculation in equations A41-A44 and A49. The sum in equation A43 over \\t_a\>t_b\\ is split in two cases, \\t_b = 0\\ and \\t_b \> 0\\.

Parameters:  
- **p** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers, corresponding to the largest order of the fixed points that we want to calculate.

- **big_d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Graph regularity minus one. Note that in expressions with \\\gamma\\, we use \\\sqrt{D}\\ in the denominator instead of \\\sqrt{d} = \sqrt{D+1}\\, but this just introduces a small factor to the gamma angles.

- **h** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The local field of the problem.

- **big_gamma** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The array of the \\\gamma\\ angles of the QAOA. The full array, with a 0 in the middle (see A8).

- **big_beta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The array of the \\\beta\\ angles of the QAOA. The full array, with a 0 in the middle (see A8).

- **basis_list_t** (*None* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]\]*) – For some compatibility, the basis list sorted by the symmetry sectors can be pregenerated and given as an input. Otherwise it’s generated internally.

Returns:  
A tuple of two floats representing the expectation values of \<Z\> and \<ZZ\> respectively. The output values are typed as np.complex128, but they are in fact real values (so their imaginary component is minimal).

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*complex128*, *complex128*\]
