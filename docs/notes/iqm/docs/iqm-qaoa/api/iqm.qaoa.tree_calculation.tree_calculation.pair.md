> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.pair.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.pair.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5b4068eebbef4fb19e639e0308e136d854889b29f5429154e5be1a4c957ed1c5.

# pair

iqm.qaoa.tree_calculation.tree_calculation.pair(*ai*, *aj*, *beta_i*)  
Represents the equation (A12) in \[[8](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id8 "Elisabeth Wybo and Martin Leib. Missing puzzle pieces in the performance landscape of the quantum approximate optimization algorithm. 2024. URL: https://arxiv.org/abs/2406.14618, arXiv:2406.14618.")\].

Returns the expectation value of \\\langle z^{\[m\]}\_k \| e^{i\beta_i X_k} \| z^{\[n\]}\_k \rangle}\\ where the ket and the bra are basis states and the operator is the exponentiation of the mixer.

Parameters:  
- **ai** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The basis state of the bra vector, must be either +1 or -1.

- **aj** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The basis state of the ket vector, must be either +1 or -1.

- **beta_i** (*float64*) – The angle by which the \\X_k\\ operator gets exponentiated.

Returns:  
The right-hand side of the equation (A12). In other words, the cosine of `beta_i` if `aj` and `ai` are equal and the imaginary sine of `beta_i` otherwise.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the input variables `ai` or `aj` aren’t either +1 or -1.

Return type:  
*complex128*
