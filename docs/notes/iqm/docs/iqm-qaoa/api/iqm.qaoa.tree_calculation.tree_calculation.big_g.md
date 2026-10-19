> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.big_g.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.big_g.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f20d2fe8456317286caea686a13e58b5e431a47b70495b1db3fe086e6db8e2b6.

# big_g

iqm.qaoa.tree_calculation.tree_calculation.big_g(*a_t*, *beta_t*)  
Calculates the function \\G(a_t)\\ from equations (A45) and (A46) from \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

Parameters:  
- **a_t** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The variable \\a_t\\.

- **beta_t** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – An array containing the QAOA beta angles from \\\beta_t\\ to \\\beta_p\\, where \\p\\ is the number of QAOA layers.

Returns:  
The result of the calculation.

Return type:  
*complex128*
