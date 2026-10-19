> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 00d4f4abd0523212d42c351eb6c5ce809064a7fb64fe8ea223cfea42fad63103.

# iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre

iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre(*topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *instruction_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *greediness: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *threads: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *section_lengths: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *tempering_range: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 3*, *congestion_penalty: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *selection_exponent: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[int16, int16, int16\]\], [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Execute the SABRE algorithm with “sectionizing” strategy.

Sectionizing means dividing the QuantumCircuit into several sections, which are sequentially compiled. Each section is compiled multiple times with different seeds. The best seed is picked and the algorithm proceeds to the next section.

Section boundaries are placed at semantically meaningful positions (e.g. after TerminatorNodes in the PermeabilityGraph) rather than at uniform intervals. The `section_lengths` array specifies how many DAG nodes belong to each section.

The depth_array is carried forward between sections so that per-physical-qubit depth tracking remains continuous, enabling the congestion penalty to account for congestion accumulated in earlier sections.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")) – QPU topology.

- **instruction_dag** ([*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")) – Instruction DAG.

- **greediness** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Controls swap selection randomness.

- **threads** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The amount of instances that should be executed in parallel.

- **section_lengths** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 1-D int32 array where each entry is the number of DAG nodes in that section. The last entry is treated as “compile everything remaining” (i.e. max_instruction=inf). The sum should equal the total DAG size but the last section will consume whatever is left regardless.

- **tempering_range** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Controls parallel tempering.

- **congestion_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Strength of the per-physical-qubit congestion penalty.

- **selection_exponent** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Blending weight for the geometric-mean selection metric (0.0–1.0). Forwarded to `sabre_gen_swaps_parallel`.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Base seed for reproducibility. Each section derives its own seed offset so that different sections use non-overlapping seed ranges.

Returns:  
- Instructions in the compiled QuantumCircuit.

- Final logical to physical qubit index permutation.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*int16*, *int16*, *int16*\]\], [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]
