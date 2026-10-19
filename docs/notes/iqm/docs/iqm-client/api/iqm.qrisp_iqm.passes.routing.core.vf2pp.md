> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8915ac010085b56d4457f102169b2879ffa0c4e224dca2b84f72f992b4928bde.

# vf2pp

Full path: iqm.qrisp_iqm.passes.routing.core.vf2pp

VF2++ subgraph isomorphism for quantum circuit layout.

This module implements a Numba-accelerated VF2++-style subgraph isomorphism search for placing quantum circuits onto hardware topologies. The search uses BFS-based node ordering, T-set candidate narrowing, and parallel exploration of first-node candidates across CPU cores.

Functions

|  |  |
|----|----|
| [`is_identity_embedding`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding.html#iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding "iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding")(pattern_indices, ...) | Check whether the pattern graph is a subgraph of the target graph. |
| [`qc_to_interaction_graph`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph.html#iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph "iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph")(qc) | Extract the qubit-interaction graph of a quantum circuit. |
| [`vf2pp_layout_and_route`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route.html#iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route "iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route")(qc, topology\[, ...\]) | Attempt to place *qc* onto *topology* via subgraph isomorphism. |
| [`vf2pp_subgraph_isomorphism`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism.html#iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism "iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism")(pattern_indices, ...) | Find one subgraph isomorphism mapping from pattern graph to target. |
