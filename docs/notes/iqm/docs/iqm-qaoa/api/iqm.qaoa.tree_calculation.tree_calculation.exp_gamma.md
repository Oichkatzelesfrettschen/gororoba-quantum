> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.exp_gamma.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.exp_gamma.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 136279f478da41de951d7225c789135c39f43f4793f25c33c6037bf6236318c3.

# exp_gamma

iqm.qaoa.tree_calculation.tree_calculation.exp_gamma(*big_d*, *h*, *big_gamma_pruned*, *a*, *b*)  
Calculates the complex exponential in the 2nd half of (A23).

Parameters:  
- **big_d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Graph regularity minus one. It appears in denominators as \\\sqrt{D}\\ instead of \\\sqrt{D+1} = \sqrt{d}\\ which appears in the formula in the paper.

- **h** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The local field of the problem.

- **big_gamma_pruned** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The array of gamma angles \\\mathbb{\Gamma}^{(m-1)}\\. sorted ascendingly and descendingly in an array like \\(\gamma_1, \gamma_2, ... , \gamma\_{p-1}, -\gamma\_{p-1}, ..., -\gamma_2, -\gamma_1)\\.

- **a** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The vector \\\mathbb{a}^{(m-1)}\\.

- **b** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The vector \\\mathbb{b}^{(m-1)}\\

Returns:  
The product of the two exponential terms in (A23).

Return type:  
*complex128*
