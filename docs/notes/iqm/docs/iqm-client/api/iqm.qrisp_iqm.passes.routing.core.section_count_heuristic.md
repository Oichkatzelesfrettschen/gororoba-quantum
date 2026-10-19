> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f87a9f3293cf7e31d7ea91dd347feae8840c218da1c7c53fb7d30630477867e8.

# section_count_heuristic

Full path: iqm.qrisp_iqm.passes.routing.core.section_count_heuristic

Automatic section-count heuristic for SABRE routing.

This module determines *how many sections* a circuit should be split into when sectionalized routing is used. The answer is derived from the **2-qubit critical path** (CP₂) of the circuit’s PermeabilityGraph (PDAG).

## Formula

```
n_sections = floor(CP₂ / 15) + 1
```

where CP₂ is the longest path through the PDAG counting only 2-qubit gate nodes (single-qubit gates, measurements, and TerminatorNodes are weighted 0).

## What is the critical path and why does it matter?

The PermeabilityGraph is a DAG that encodes data-dependency and commutation relations between circuit gates. The **critical path** is the longest directed path through this DAG — it represents the maximum number of *sequentially dependent* routing decisions that SABRE must make without any reordering freedom.

Circuits with a short critical path (e.g. QAOA, where almost everything commutes) give SABRE enormous scheduling flexibility: it can reorder gates freely to avoid congestion. Circuits with a long critical path (e.g. Grover, qwalk) force SABRE into a rigid sequence where early mistakes cascade through the whole compilation.

Sectionalization helps precisely when the critical path is long: by resetting the random-seed search at each section boundary, mistakes in one section cannot propagate beyond it. For short-CP circuits, sectionalization adds overhead without benefit.

## Why count only 2-qubit gates?

Only 2-qubit gates create routing constraints — they require their two operand qubits to be physically adjacent. Single-qubit gates, barriers, measurements, and TerminatorNodes (synthetic PDAG nodes marking commutation-streak boundaries) inflate the naive critical path without adding routing difficulty.

For example, `cdkm_ripple_carry_adder@20` has CP_all = 192 when counting all nodes, but CP₂ = 109 when counting only 2-qubit gates. The naive metric suggested this circuit barely benefits from sections (CP \< 200 threshold from naive analysis), while the corrected metric correctly places it well above the “sections help” threshold.

This insight was discovered when early sweep experiments targeting CP-per-section values of 20–50 (using the naive all-node CP) produced optimal section counts that seemed far too aggressive for small circuits. Re-examining the CP calculation revealed that 1-qubit gates, measurements, and terminators were inflating the numbers by ~2×. After switching to the 2-qubit-only metric, the optimal CP₂/section converged to ~10–15 across diverse benchmarks.

## Implementation

The CP₂ computation uses a numba-JIT-compiled Kahn’s-algorithm topological sort with dynamic programming on the CSR adjacency list that `convert_qc_to_sparse_dag` already produces — no redundant graph construction is needed.

Functions

|  |  |
|----|----|
| [`auto_section_count`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count.html#iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count "iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.auto_section_count")(forward_dag, instruction_list) | Determine the number of sections automatically. |
| [`compute_cp_2qb`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb.html#iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb "iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb")(forward_dag, instruction_list) | Compute the routing-relevant critical path length. |
