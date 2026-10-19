> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e4b5f4a249271e5bd5b641c7e2fba312630bfe7bf694f167ea8eda33cda12af3.

# iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout

iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout(*couplers*, *qubits*)  
Compute a square-grid layout for IQM Crystal architecture QPUs.

Uses the coupler connectivity graph to recursively identify 4-qubit plaquettes and assign (x, y) grid coordinates. This algorithm works for any IQM Crystal QPU (Garnet, Emerald, etc.) but will not work with the IQM Star topology.

Parameters:  
- **couplers** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*) – Qubit pairs representing the connectivity.

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Qubit names on the QPU.

Returns:  
Mapping from qubit names to (x, y) integer grid positions. Qubits that could not be placed (e.g. in a Star topology) are omitted.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
