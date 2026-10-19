> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ed0ff4b79951901661f45f90f80adc44237532b2de9ba0c4be54b99122afb918.

# sabre_meta_functions

Full path: iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions

Meta-functions for SABRE routing with parallel tempering and sectionizing.

Functions

|  |  |
|----|----|
| [`instruction_tuples_to_qc`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc.html#iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc "iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc")(...\[, ...\]) | Turn a list of compiled instruction tuples back into a QuantumCircuit. |
| [`sabre_gen_swaps_parallel`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel.html#iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel "iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sabre_gen_swaps_parallel")(topology, ...\[, ...\]) | Execute sabre_gen_swaps in parallel with different seeds and greediness values. |
| [`sectionized_sabre`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre.html#iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre "iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.sectionized_sabre")(topology, instruction_dag, ...) | Execute the SABRE algorithm with "sectionizing" strategy. |
| [`update_depth_array`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array.html#iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array "iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array")(instruction_list, depth_array) | Update the per-physical-qubit depth array from a compiled instruction list. |
