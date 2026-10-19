> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_f.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.get_f.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ba09ddc1c46fcce9ccc79a4154656692b13c23b177607ff587b1a5680d211942.

# get_f

iqm.qaoa.tree_calculation.tree_calculation.get_f(*p*, *a*, *big_beta*)  
Represents the function \\f(\mathbb{a})\\ defined in (9) and (10) in \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

For a given basis state \\\mathbb{a}\\ (i.e., an array of +1 and -1), this calculates the function \\f\\. The function is one half of a product of expectation values of the form \\\langle a_k \| e^{i\beta_k X} \| a\_{k+1} \rangle}\\ for variable \\k\\.

Parameters:  
- **p** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of QAOA layers.

- **a** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[int8\]\]*) – The array of basis states of the ket and bra vector which appear in the definition of :math\`f(mathbb{a})\`.

- **big_beta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The array containing the beta angles of the QAOA, sorted ascendingly and descendingly as \\(\beta_1, \beta_2, ... , \beta_p, -\beta_p, -\beta\_{p-1}, ..., -\beta_2, -\beta_1)\\.

Returns:  
The value of the \\f(\mathbb{a})\\ function.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `a` is not a 1D array.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `a` does not have length `2*p+1`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `big_beta` is not a 1D array.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `big_beta` does not have length `2*p`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `a` contains other entries than +1 or -1.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `big_beta` is not antisymmetric.

Return type:  
*complex128*
