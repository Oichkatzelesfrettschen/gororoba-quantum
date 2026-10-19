> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 38f97aa603f88910732e81ab7dc0fd52e28be14076de9794ca5e0db4b97d6f1c.

# iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel

iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel(*topology: [QPUTopology](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")*, *instruction_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *greediness: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *max_instruction: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *threads: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *tempering_range: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 3*, *congestion_penalty: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *selection_exponent: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[int16, int16, int16\]\], [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Execute sabre_gen_swaps in parallel with different seeds and greediness values.

Uses parallel tempering across threads, then selects the trial with the lowest score. The score is a weighted geometric mean of swap count and 2-qubit depth:

```
score = swaps^(1 - e) * depth^e
```

When `selection_exponent` is 0 (default) the selection is purely by swap count; when 1.0 it is purely by depth.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.QPUTopology")) – Available gates.

- **instruction_dag** ([*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")) – Quantum circuit in DAG format.

- **greediness** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Controls swap selection randomness. The algorithm will skip the best swap candidate with probability 1/greediness. Higher values mean more greedy (deterministic) behavior.

- **max_instruction** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The sabre_gen_swaps will only compile until this threshold is reached.

- **threads** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The amount of instances that should be executed in parallel (recommended to be an integer multiple of the CPU count).

- **depth_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Per-physical-qubit depth array. Carried across sections so that depth accounting is continuous. Each parallel trial receives a copy.

- **tempering_range** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Controls parallel tempering. When \> 0, each thread uses a different greediness value spread across \[max(2, greediness - tempering_range), greediness + tempering_range\]. This gives different threads different exploration/exploitation tradeoffs (analogous to running replicas at different temperatures in simulated annealing). When 0, all threads use the same greediness.

- **congestion_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Strength of the per-physical-qubit congestion penalty in swap scoring. Forwarded to sabre_gen_swaps. 0.0 disables.

- **selection_exponent** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Blending weight for the geometric-mean selection metric (0.0–1.0). 0.0 selects purely by swap count, 1.0 purely by depth.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Base seed for the random number generation. Each parallel thread derives its own seed as `seed + i*173 + 1`.

Returns:  
- Compiled instructions from the trial with the lowest score. SWAPs have instr_index = -1.

- Final logical-to-physical qubit mapping of the best solution. The dtype is inherited from the topology (int16 on NISQ-scale devices).

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*int16*, *int16*, *int16*\]\], [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]
