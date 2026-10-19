> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f81eb1324e21191d510f475b7d84b8837398e36726023b7a1ea6e9845898c998.

# iqm_converter

Full path: iqm.qrisp_iqm.iqm_converter

Circuit converter for mapping Qrisp QuantumCircuits to IQM Circuits.

This module provides the conversion function that maps Qrisp circuits to IQM format. For transpilation (layout, routing, gate conversion), use the PassManager from [`create_iqm_pass_manager()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html#iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager"), or [`transpile_to_iqm()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html#iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm "iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm").

Functions

|  |  |
|----|----|
| [`get_coupling_map`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.get_coupling_map.html#iqm.qrisp_iqm.iqm_converter.get_coupling_map "iqm.qrisp_iqm.iqm_converter.get_coupling_map")(dqa) | Extract the coupling map from DQA. |
| [`qrisp_to_iqm_converter`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html#iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter "iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter")(qc, dqa\[, circuit_name\]) | Converts a Qrisp QuantumCircuit to an IQM `Circuit`. |
