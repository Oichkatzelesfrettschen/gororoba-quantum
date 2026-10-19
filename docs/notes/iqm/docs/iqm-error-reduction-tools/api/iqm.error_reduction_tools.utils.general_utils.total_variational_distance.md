> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.total_variational_distance.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.total_variational_distance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0f526c5da07287e0d21d58fe3dfe2fdf43560e52f9accb7260ca2972ff21530c.

# iqm.error_reduction_tools.utils.general_utils.total_variational_distance

iqm.error_reduction_tools.utils.general_utils.total_variational_distance(*dist_a*, *dist_b*)  
Total Variation Distance between two probability distributions.

The Total Variation Distance between the probability distributions P and Q is defined as

\\\text{TVD}(P, Q) = \frac{1}{2} \sum_x \|P(x) - Q(x)\|.\\

TVD is always in \\\[0, 1\]\\.

This function accepts both:

- Proper probability distributions (`dict[str, float]` with values summing to 1)

- Samplings of distributions (`dict[str, int]` with arbitrary sums)

The distributions are automatically normalized before computing the distance, so the input values do not actually need to sum to 1.

Parameters:  
- **dist_a** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – First probability distribution.

- **dist_b** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Second probability distribution.

Returns:  
Total Variation Distance between the two distributions.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
