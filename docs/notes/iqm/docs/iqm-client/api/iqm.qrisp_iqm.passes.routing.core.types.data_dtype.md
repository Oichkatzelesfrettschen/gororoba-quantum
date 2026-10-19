> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.data_dtype.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.data_dtype.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6ab52d774c45b1b52d1756ed5d8449e8be598f0bcef6efa24ff43740aaf23c0e.

# iqm.qrisp_iqm.passes.routing.core.types.data_dtype

iqm.qrisp_iqm.passes.routing.core.types.data_dtype(*n_physical: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_nodes: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [dtype](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")  
Return dtype for `instruction_data` (Mx3) arrays.

Stores both qubit indices (0..N-1) and instruction indices (0..M-1).

Parameters:  
- **n_physical** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **n_nodes** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
[*dtype*](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")
