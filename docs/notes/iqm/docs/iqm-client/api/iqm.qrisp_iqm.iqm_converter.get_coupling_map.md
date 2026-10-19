> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.get_coupling_map.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.get_coupling_map.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 677228e7438b72f2c72ed97d6da3febe61306a436a98e0e992abbf2ec46266e6.

# iqm.qrisp_iqm.iqm_converter.get_coupling_map

iqm.qrisp_iqm.iqm_converter.get_coupling_map(*dqa: DynamicQuantumArchitecture*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Extract the coupling map from DQA.

Parameters:  
**dqa** (*DynamicQuantumArchitecture*) – Describes the gates and loci available with a given calibration set.

Returns:  
The coupling map as a list of pairs of `dqa.qubits` indices that have the CZ gate available.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the device uses computational resonators, which are not yet supported by the Qrisp-IQM connector.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
