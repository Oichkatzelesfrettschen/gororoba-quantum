> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_seq_design.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_seq_design.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 52335d567b89032e50d8ae3a2934841493687489971f84e1f399ace3bf831310.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.random_seq_design

iqm.benchmarks.compressive_gst.mgst.additional_fns.random_seq_design(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *l_min: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *l_cut: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *l_max: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *N_short: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *N_long: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate a set of random sequences ith given lengths.

Disclaimer: Draws without replacement but inefficiently (not working for sequence length \> 24) This sequence lengths (circuit depths) are chosen for a mix of very short sequences (better convergence) and some slightly longer sequences to reduce the generalization error. This sequence design is heuristic and intended for coarse and fast estimates. For very accurate estimates at the cost of higher measurement effort it is recommended to use pyGSTi with long sequence GST.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of gates in the gate set

- **l_min** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Minimum sequence lenght

- **l_cut** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Cutoff sequence lenght: N_short sequences are equally distributed among lengths l_min \< l \< l_cut

- **l_max** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – N_long sequences are equally distributed among lengths l_cut + 1 \< l \< l_max. Currently l_max \< 24 only.

- **N_short** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of short sequences

- **N_long** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of long sequences

Returns:  
2D array where each row contains the gate indices of a gate sequence

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
