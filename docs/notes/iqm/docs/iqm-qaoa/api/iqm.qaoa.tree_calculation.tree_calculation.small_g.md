> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.small_g.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.small_g.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2cee536a31b630f9e7121e0eb1783c0408d27b9f40ac6be9fe882cde5e7960fc.

# small_g

iqm.qaoa.tree_calculation.tree_calculation.small_g(*m_minus_1*, *b*, *big_beta*)  
Represents the function \\g(b^{(m-1)})\\ defined in (A26) in \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

For a given basis state `b` (i.e., an array of +1 and -1), this calculates the function \\g\\. The function is a product of expectation values.

Parameters:  
- **m_minus_1** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The parameter \\m-1\\ from the text.

- **b** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[int8\]\]*) – The array of basis states of the ket and bra vector which appear in the definition of :math\`g(b^{(m-1)})\`. It is expected to have length 2\*m_minus_1, but it can be longer because it’s accessed from left and right.

- **big_beta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\],* [*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")*\[float64\]\]*) – The array containing the beta angles of the QAOA, sorted ascendingly and descendingly in an array like \\(\beta_1, \beta_2, ... , \beta\_{p-1}, -\beta\_{p-1}, -\beta\_{p-2}, ..., -\beta_2, -\beta_1)\\. Here \\p \geq m-1\\ (but not necessarily equal).

Returns:  
math\`g(b^{(m-1)})\` function.

Return type:  
The value of the
