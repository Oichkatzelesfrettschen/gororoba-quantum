> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.big_g_tilde.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.big_g_tilde.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9a197df05e4373657bef7bace3aa926248baf4d3c4671d4bfedc86d86e00b129.

# big_g_tilde

iqm.qaoa.tree_calculation.tree_calculation.big_g_tilde(*a_t*, *beta_t*)  
Calculates the function \\\tilde{G}(a_t)\\ from equations (A47) and (A48) from \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

Parameters:  
- **a_t** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The variable \\a_t\\.

- **beta_t** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – An array containing the QAOA beta angles from \\\beta_t\\ to \\\beta_p\\, where \\p\\ is the number of QAOA layers.

Returns:  
The result of the calculation.

Return type:  
*complex128*
