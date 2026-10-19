> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.uses_move_gates.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.uses_move_gates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c80c55eaf40b707b2b28be3846703ca7783bafd4343291fafc2a8c4091c4dacc.

# iqm.error_reduction_tools.utils.topology_utils.uses_move_gates

iqm.error_reduction_tools.utils.topology_utils.uses_move_gates(*client*)  
Detect whether a QPU uses MOVE gates, which makes circuit twirling unsupported.

IQM QPUs that include computational resonators use MOVE gates rather than direct CZ gates between qubits. The PMPT implementation only handles `prx` and `cz` operations and will raise a `ValueError` if it encounters a `move` instruction, so twirling cannot be applied to circuits compiled for these QPUs.

This function detects such QPUs directly by checking whether the chip topology reports any computational resonators, which is the authoritative indicator that MOVE gates are present.

Parameters:  
**client** (*IQMClient*) – Client instance for connecting to the quantum computer.

Returns:  
`True` if the QPU has computational resonators (and therefore uses MOVE gates), `False` otherwise or if the topology cannot be retrieved.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")
