> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fe611eea510edf040e5a58ef512c154e34b103cc550743e23c99d77541bdee6d.

# iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc

iqm.error_reduction_tools.utils.topology_utils.operational_qubits_from_qc(*client*)  
Operational qubit names on the remote quantum computer.

A qubit is considered operational if the current default calibration set contains a calibrated `measure` gate for it, i.e. it can be read out. This is the relevant notion of “operational” for readout error characterization and mitigation: qubits without readout calibration cannot be meaningfully characterized.

The information is taken from the dynamic quantum architecture (DQA), which describes exactly the operations for which calibration data exists.

Parameters:  
**client** (*IQMClient*) – Client instance for connecting to the quantum computer.

Returns:  
Operational qubit names, sorted as reported by the DQA, or `None` if the information cannot be retrieved from the server.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| None
