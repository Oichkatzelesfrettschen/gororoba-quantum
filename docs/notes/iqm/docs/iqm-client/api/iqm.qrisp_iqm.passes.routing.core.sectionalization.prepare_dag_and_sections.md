> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5cdcbfd211510b3f73645d37e27ce75589a924372361d770138eb0e0c5e6234e.

# iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections

iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections(*qc: QuantumCircuit*, *\**, *sections: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Instruction \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\], np.ndarray\]  
Convert a quantum circuit into a CSR instruction DAG.

Computes sectionalization information for the router.

This is the single entry point that combines DAG construction (via `convert_qc_to_sparse_dag()`) with section-boundary computation. The returned `section_lengths` array tells the router how to split the compilation into sections.

Parameters:  
- **qc** (*QuantumCircuit*) – The circuit to prepare.

- **sections** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – `0` (default) for automatic CP-based sections (`floor(cp_2qb / 15) + 1`), `1` for no sectionalization, `N > 1` for exactly *N* terminator-based sections.

Returns:  
- **forward_dag** (*tuple*) – CSR instruction DAG for the forward circuit.

- **forward_instruction_list** (*list*) – Instruction list (entries are `Instruction` or `None`).

- **section_lengths** (*np.ndarray*) – Int32 array of per-section node counts. When sectionalization is inactive (`sections=1` or no terminators found), this is a single-element array covering the entire DAG.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Instruction \| None\], np.ndarray\]
