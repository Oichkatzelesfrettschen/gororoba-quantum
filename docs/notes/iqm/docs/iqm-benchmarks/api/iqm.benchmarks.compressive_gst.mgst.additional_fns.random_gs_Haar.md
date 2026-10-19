> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs_Haar.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs_Haar.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8865d3606751e72a1053044d20f8f48023a3d1d38324c59b3d2ee2eb9e82d3e1.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs_Haar

iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs_Haar(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *r: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Generates a random gate set with gates from Haar random unitaries, initial state and POVM.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **r** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Superoperator dimension of the gates given by the square of the physical dimension

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of Kraus operators per gate (“Kraus rank”)

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of POVM-Elements

Returns:  
- Each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

- Array where random CPT superoperators are stacked along the first axis.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

Notes

The Kraus operators are generated from Haar random unitaries, see function randKrausSet_Haar
