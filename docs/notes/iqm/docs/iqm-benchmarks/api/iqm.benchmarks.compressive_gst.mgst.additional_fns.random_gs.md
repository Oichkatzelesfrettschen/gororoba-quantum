> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e5242821de66c856274817fd8e55bc8f146311c96286c5f94cb041bbbe4b43d3.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs

iqm.benchmarks.compressive_gst.mgst.additional_fns.random_gs(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *r: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Generates a random gate using the Gaussian unitary ensemble, initial state and POVM.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **r** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Superoperator dimension of the gates given by the square of the physical dimension

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of Kraus operators per gate (“Kraus rank”)

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of POVM-Elements

Returns:  
- K, each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

- X, array where random CPT superoperators are stacked along the first axis.

- E, randomly generated POVM elements stacked along the first axis.

- rho, random initial state vector.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

Notes

The Kraus operators are generated from random unitaries, see function randKrausSet
