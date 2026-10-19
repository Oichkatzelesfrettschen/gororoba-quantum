> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5d51664c1bfc992966f421cfaa223b6103f52474213b8d91265ee4384587a8e6.

# default_pass_manager

Full path: iqm.qrisp_iqm.passes.default_pass_manager

Default plasma-sabre PassManager for IQM-targeted transpilation.

This module provides [`create_iqm_pass_manager()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html#iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager"), a factory that builds a fully configured `PassManager` implementing the complete plasma-sabre transpilation pipeline (predicates, decomposition, layout, routing, SWAP optimization, and gate conversion to the CZ + PRX native gate set). The high-level convenience function [`transpile_to_iqm()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html#iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm "iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm") calls the factory and immediately runs the resulting PassManager on a circuit.

Functions

|  |  |
|----|----|
| [`create_iqm_pass_manager`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html#iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager")(connectivity\[, ...\]) | Create a `PassManager` pre-configured for IQM transpilation. |
| [`shift_graph_edges`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges.html#iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges "iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges")(edges, removed_nodes\[, ...\]) | Removes specified edges and nodes from a graph, then shifts the indices of the remaining nodes. |
| [`transpile_to_iqm`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html#iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm "iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm")(qc, connectivity\[, ...\]) | Transpile a Qrisp QuantumCircuit for execution on IQM hardware. |
