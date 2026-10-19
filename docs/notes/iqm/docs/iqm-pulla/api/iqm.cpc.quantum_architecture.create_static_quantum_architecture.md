> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.quantum_architecture.create_static_quantum_architecture.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.quantum_architecture.create_static_quantum_architecture.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4e920f1682a4eef5236c7e8d1157948ee0d5260ae299294c49e76e122191c3d5.

# iqm.cpc.quantum_architecture.create_static_quantum_architecture

iqm.cpc.quantum_architecture.create_static_quantum_architecture(*dut_label*, *chip_topology*)  
Create a static quantum architecture (SQA) for the given chip topology.

Parameters:  
- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Identifies the QPU that `chip_topology` describes.

- **chip_topology** ([*ChipTopology*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)")) – The chip topology.

Returns:  
Static quantum architecture containing information about qubits, computational resonators, and connectivity.

Return type:  
[*StaticQuantumArchitecture*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.html#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture "(in iqm-station-control-client v14.0.0)")
