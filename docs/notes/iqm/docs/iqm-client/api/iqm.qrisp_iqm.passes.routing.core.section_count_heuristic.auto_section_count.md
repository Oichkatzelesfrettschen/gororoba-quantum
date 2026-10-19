> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8b8e4b246bae469842e231121391da3973518379bc870ab30e8dd2fa96113a14.

# iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count

iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count(*forward_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *instruction_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Determine the number of sections automatically.

Derived from the 2-qubit critical path.

Parameters:  
- **forward_dag** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – CSR instruction DAG from `convert_qc_to_sparse_dag()`.

- **instruction_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Corresponding instruction list.

Returns:  
Recommended number of sections (≥ 1).

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
