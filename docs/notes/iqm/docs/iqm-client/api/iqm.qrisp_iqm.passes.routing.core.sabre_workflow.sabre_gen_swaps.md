> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9bf2f1397d0926f22f162a43f04cb66b0dcabe3b7b92881ad9379a0bd4334926.

# iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps

iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps(*topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *circuit_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *greediness: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *max_instruction: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = inf*, *seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*, *initial_phys_depth: np.ndarray = array(\[\], dtype=int32)*, *congestion_penalty: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *backward_mode: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *scaling_threshold: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[InstructionRef\], np.ndarray\]  
Core SABRE routing loop.

Iteratively moves through the DAG front layer, compiling gates that are already placed on adjacent physical qubits and inserting SWAPs to bring non-adjacent operands together.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")) – Hardware topology.

- **circuit_dag** ([*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")) – Circuit DAG in CSR format.

- **greediness** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Controls swap selection randomness. Higher = more deterministic.

- **max_instruction** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Only compile DAG nodes with index \< max_instruction (for sectionized routing).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – RNG seed for stochastic swap selection.

- **initial_phys_depth** (*np.ndarray*) – Starting per-physical-qubit depth. The dtype is inherited from the topology (int16 on NISQ-scale devices). Non-empty when routing a section that follows a previously routed section, so depth accounting is continuous across sections.

- **congestion_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Strength of the congestion penalty applied to swap candidate scores. When \> 0, swaps touching high-depth physical qubits receive a score penalty proportional to their local depth, encouraging the router to spread work across idle qubits and reduce critical-path depth. 0.0 disables the penalty (pure gate-count optimization).

- **backward_mode** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, operate in backward mode (layout refinement).

- **scaling_threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Instructions whose exp_depth_array weight falls below this threshold are skipped during cost-change evaluation. For deep circuits this prunes near-zero contributions from the hot loop, avoiding expensive lookups on instructions whose weight has decayed to insignificance. Default 0.0 (no skipping) for backward compatibility.

Returns:  
- Compiled instructions. SWAPs have instr_index = -1.

- Final logical-to-physical qubit mapping. The dtype is inherited from the topology (int16 on NISQ-scale devices).

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[InstructionRef\], np.ndarray\]
