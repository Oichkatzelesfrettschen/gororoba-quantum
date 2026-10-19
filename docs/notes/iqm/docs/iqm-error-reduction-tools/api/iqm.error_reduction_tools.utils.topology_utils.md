> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b5c1eca8bc9ad9e4eae914d802e1a4da1b07d8219058c26dfb96f22ca02dc7da.

# iqm.error_reduction_tools.utils.topology_utils

Utility functions for resolving QPU topology from remote quantum computer.

Provides helpers that convert chip topology objects into the [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology") used by readout-twirling string generation, and detection of IQM Star QPUs where circuit twirling is not supported because those QPUs use MOVE gates and computational resonators rather than direct qubit-qubit CZ gates, which are not handled by the PMPT implementation.

Functions

|  |  |
|----|----|
| [`compute_crystal_layout`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout.html#iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout "iqm.error_reduction_tools.utils.topology_utils.compute_crystal_layout")(couplers, qubits) | Compute a square-grid layout for IQM Crystal architecture QPUs. |
| [`operational_qubits_from_qc`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc "iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc")(client) | Operational qubit names on the remote quantum computer. |
| [`topology_from_qc`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.topology_from_qc "iqm.error_reduction_tools.utils.topology_utils.topology_from_qc")(client) | QPU topology representing a remote quantum computer. |
| [`uses_move_gates`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.uses_move_gates.html#iqm.error_reduction_tools.utils.topology_utils.uses_move_gates "iqm.error_reduction_tools.utils.topology_utils.uses_move_gates")(client) | Detect whether a QPU uses MOVE gates, which makes circuit twirling unsupported. |
