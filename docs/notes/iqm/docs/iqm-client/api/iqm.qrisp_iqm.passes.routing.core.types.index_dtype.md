> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.index_dtype.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.index_dtype.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 230581d5df597a6c8375ec0b27dbc1b0983e851470a8637afa5a371fc9fd1f87.

# iqm.qrisp_iqm.passes.routing.core.types.index_dtype

iqm.qrisp_iqm.passes.routing.core.types.index_dtype(*max_value: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [dtype](https://numpy.org/doc/stable/reference/generated/numpy.dtype.html#numpy.dtype "(in NumPy v2.5)")  
Return the narrowest numpy signed-integer dtype for the given range.

Can represent every value from `0` to `max_value` (inclusive).

Parameters:  
**max_value** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Largest expected index value.

Returns:  
`np.int16` when `max_value <= 32767`, otherwise `np.int32`.

Return type:  
np.dtype
