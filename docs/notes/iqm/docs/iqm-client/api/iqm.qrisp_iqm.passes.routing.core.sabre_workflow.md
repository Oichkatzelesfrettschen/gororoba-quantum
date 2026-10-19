> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6ff30d658359f7281091afcf38e2f1972f2b2478716d3abbd61f0c702d66b894.

# sabre_workflow

Full path: iqm.qrisp_iqm.passes.routing.core.sabre_workflow

SABRE routing workflow.

This module implements the SABRE workflow, described in \[[1](https://docs.iqm.tech/4.7/iqm-client/references.html#id2 "Gushu Li, Yufei Ding, and Yuan Xie. Tackling the qubit mapping problem for NISQ-era quantum devices. In Proceedings of the Twenty-Fourth International Conference on Architectural Support for Programming Languages and Operating Systems, ASPLOS '19, 1001–1014. New York, NY, USA, 2019. Association for Computing Machinery. arXiv:1809.02573, doi:10.1145/3297858.3304023.")\].

Extended with: - Per-physical-qubit depth tracking for depth-aware swap selection - Descendant-count weighting for DAG-criticality-aware gate prioritization - A congestion penalty mechanism that steers swaps towards idle physical qubits

Module Attributes

|  |  |
|----|----|
| [`InstructionRef`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.InstructionRef.html#iqm.qrisp_iqm.passes.routing.core.sabre_workflow.InstructionRef "iqm.qrisp_iqm.passes.routing.core.sabre_workflow.InstructionRef") | Represents an instruction in a quantum circuit as a (locus_qubit_0_index, locus_qubit_1_index, instr_index) tuple. |

Functions

|  |  |
|----|----|
| [`lcg_next`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next.html#iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next "iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next")(seed) | Linear Congruential Generator for stochastic swap selection. |
| [`sabre_gen_swaps`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps.html#iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps "iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps")(topology, circuit_dag, ...) | Core SABRE routing loop. |
