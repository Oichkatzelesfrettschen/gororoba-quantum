> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.CUE.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.CUE.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ab18f237dc89af25757cd6eea774fbcb07696ba50b7c38eb98c060eb2abfc152.

# iqm.benchmarks.utils_shadows.CUE

iqm.benchmarks.utils_shadows.CUE(*random_gen: [RandomState](https://numpy.org/doc/stable/reference/random/legacy.html#numpy.random.RandomState "(in NumPy v2.5)")*, *n: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Prepares single qubit Haar-random unitary (drawn from Circuilar Unitary Ensemble - CUE).

Parameters:  
- **random_gen** ([*RandomState*](https://numpy.org/doc/stable/reference/random/legacy.html#numpy.random.RandomState "(in NumPy v2.5)")) – A random generator.

- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The size of the matrix.

Returns:  
An n x n CUE matrix

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
