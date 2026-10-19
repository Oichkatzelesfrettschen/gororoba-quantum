> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.a24_a25.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.tree_calculation.tree_calculation.a24_a25.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b64c3aaec91d2e56a8319f8879d56e4d57b539dc91ad7c4e8f64b19686cf4f2d.

# a24_a25

iqm.qaoa.tree_calculation.tree_calculation.a24_a25(*a_m*, *a_minus_m*, *b_m_minus_1*, *b_1_minus_m*, *beta_m_1*, *gamma_m*, *big_d*)  
Calculates the term surrounded in the big parentheses in equations A24 and A25.

Parameters:  
- **a_m** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The variable \\a\_{m}\\.

- **a_minus_m** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The variable \\a\_{-m}\\.

- **b_m_minus_1** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The \\b\_{m-1}\\ variable.

- **b_1_minus_m** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The \\b\_{-m+1}\\ variable.

- **beta_m_1** (*float64*) – The beta angle \\\beta\_{m-1}\\.

- **gamma_m** (*float64*) – The gamma angle \\\gamma_m\\.

- **big_d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The regularity of the problem graph minus one.

Return type:  
*complex128*
