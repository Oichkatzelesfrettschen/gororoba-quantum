> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bc1850f6d348b5ce293ef583dac1ff7361aeb5c7eed0909b8c53debd1459aa35.

# iqm.error_reduction_tools.utils.topology_utils.topology_from_qc

iqm.error_reduction_tools.utils.topology_utils.topology_from_qc(*client*)  
QPU topology representing a remote quantum computer.

Retrieves the QPU topology information from the remote quantum computer and converts it into a `QPUTopology` suitable for twirling-string generation.

Parameters:  
**client** (*IQMClient*) – Client instance for connecting to the quantum computer.

Returns:  
A `QPUTopology`, or `None` if the topology cannot be retrieved from the server.

Return type:  
[QPUTopology](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology") \| None
