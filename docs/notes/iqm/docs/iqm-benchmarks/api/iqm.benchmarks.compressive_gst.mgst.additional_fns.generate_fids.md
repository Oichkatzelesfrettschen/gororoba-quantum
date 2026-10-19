> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.generate_fids.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.generate_fids.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d853ae634bbe7eb4c7a221b8c77d872ad4f656d8794cf38216ca6b55d9702ee6.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.generate_fids

iqm.benchmarks.compressive_gst.mgst.additional_fns.generate_fids(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *m_f: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Generate random fiducial sequencecs.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total sequence length

- **m_f** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of random fiducial sequences

Returns:  
- Sequence list of only the fiducial sequences

- Sequence list for all combinations of two concatenated fiducial sequences

- Sequence list for all combinations of fiducials seuqneces with a gate in between: fiducial1 – gate – fiducial2

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]
