> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 11bd2967680062282f0f4e42ec2004a2bdd21e2027067e7eec902dd50bf82fdb.

# iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route

iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_layout_and_route(*qc: QuantumCircuit*, *topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *max_attempts: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1000000000*) → QuantumCircuit \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Attempt to place *qc* onto *topology* via subgraph isomorphism.

Parameters:  
- **qc** (*QuantumCircuit*) – The circuit to place.

- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")) – Target topology in CSR form.

- **max_attempts** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total budget of feasible candidate assignments the VF2++ search may explore (split across parallel threads) before giving up and returning None. 0 means unlimited. Default is 1 000 000 000. Because the search is parallelised over first-node candidates, wall-clock time scales as `max_attempts / n_target_nodes`.

Returns:  
The placed circuit, or None if no isomorphism was found within the attempt budget.

Return type:  
QuantumCircuit \| None
