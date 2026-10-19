> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.permutation_tools.permute_array.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.permutation_tools.permute_array.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 35b8d33ed49c1404a956e2160d92b0a3dd9b4b51986687d33d6e27fc7e6dea2d.

# iqm.qrisp_iqm.passes.routing.core.permutation_tools.permute_array

iqm.qrisp_iqm.passes.routing.core.permutation_tools.permute_array(*address_to_citizen: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *path: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Permute an address-to-citizen array along a given swap path.

Parameters:  
- **address_to_citizen** (*np.ndarray*) – Address-to-citizen mapping.

- **path** (*np.ndarray*) – Swap path.

Returns:  
The permuted array.

Return type:  
np.ndarray
