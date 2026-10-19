> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bfbe88edd6f32ea99181bd9ae785bdc93736b82221bd546a632514726e98336b.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag(*topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *instruction_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *c2a: np.ndarray*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute the SABRE cost from a given instruction DAG.

Evaluates under a given initial layout for a given topology.

Parameters:  
- **topology** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – A topology tuple (see graph_processing_tools for more details).

- **instruction_dag** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – An instruction DAG tuple (see graph_processing_tools for more details).

- **c2a** (*np.ndarray*) – An array describing the initial layout permutation.

Returns:  
The SABRE metric.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
