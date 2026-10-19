> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sectionalization.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sectionalization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d4ee4bff5b789687d094b1310db6696c8983df42ba9a40549383a0f9543c32fb.

# sectionalization

Full path: iqm.qrisp_iqm.passes.routing.core.sectionalization

Sectionalization strategies for SABRE routing.

## Background

The SABRE routing algorithm compiles a quantum circuit by greedily selecting SWAP gates that reduce the distance between operands of upcoming 2-qubit gates. Compiling the entire circuit in one pass with a single random seed is fast but sensitive to the initial random choices. *Sectionalization* mitigates this by splitting the circuit into consecutive sections and compiling each one independently with multiple random seeds (parallel trials). The best trial is kept, its final qubit permutation is forwarded to the next section, and the procedure repeats. This way early mistakes don’t propagate through the whole circuit.

## PermeabilityGraph and TerminatorNodes

Qrisp’s PermeabilityGraph is a DAG representation of the quantum circuit that encodes *commutation relations* between gates. Two gates that commute (e.g. two RZ gates on the same qubit) are not forced into a strict order — they form a “commutation streak”. A **TerminatorNode** is a synthetic node inserted when such a streak ends, i.e. a non-commuting gate arrives at a qubit that was participating in a commutation chain. Concretely:

- Edges labelled “Z” or “X” connect gates that commute via Z- or X-diagonal permeability.

- An “anti_dependency” edge connects streak members to the TerminatorNode that marks the streak’s end.

- A “neutral” edge connects the TerminatorNode to the first non-commuting gate.

TerminatorNodes thus mark *natural breakpoints* in the circuit’s algebraic structure: everything before the terminator commutes freely, everything after does not.

## Why place section boundaries at terminators?

When SABRE compiles a section, it processes DAG nodes in topological order up to a node-count threshold (`prune_dag` removes the first *k* nodes). If a section boundary falls in the middle of a commutation streak, the routing of the first half cannot exploit the freedom that commutation provides — the streak is artificially cut. Placing the boundary *after* a TerminatorNode ensures each section contains complete commutation blocks, giving the router maximum freedom within each section.

## Topological sort strategy — Kahn’s algorithm with terminator deferral

`convert_qc_to_sparse_dag` builds the PermeabilityGraph, topologically sorts its nodes, then converts to a CSR adjacency matrix. The node ordering in this CSR representation is what `prune_dag` uses to determine which nodes belong to which section (it simply slices the first *k* rows). This means the topological sort order directly controls section composition.

A plain `nx.topological_sort` spreads TerminatorNodes evenly throughout the ordering. This is problematic because section boundaries are snapped to terminator positions — if terminators are scattered, cuts can land inside a commutation streak (splitting it across sections) or in regions that don’t reflect the actual routing difficulty.

The custom sort (`_sectionalization_topo_sort`) uses Kahn’s algorithm with a two-queue dequeuing heuristic:

1.  Maintain two ready-queues: one for regular (non-terminator) nodes and one for TerminatorNodes.

2.  **Always dequeue regular nodes first**, as long as any are available. This lets the algorithm “drain” all streak members and ordinary gates before emitting any terminators.

3.  **When only terminators remain** in the ready set, flush all of them in a burst.

The effect is that terminators become *concentrated* into clusters rather than spread out. Each cluster marks a natural breakpoint where several commutation streaks end simultaneously. Section boundaries placed at these clusters are guaranteed to sit between complete commutation blocks, never in the middle of one.

## Section boundary selection algorithm

Given a target of `N` sections (either user-specified or auto-derived via the heuristic in `iqm.qrisp_iqm.passes.core.section_count_heuristic`), we need `N − 1` cut points:

1.  Scan the `instruction_list` for `None` entries — these correspond to TerminatorNodes in the CSR node order.

2.  Compute `N − 1` ideal (uniformly spaced) cut positions in **2-qubit-gate-count space** — i.e. the positions that split the circuit’s 2-qubit workload into equal parts. Only 2-qubit gates matter for routing difficulty; single-qubit gates are essentially free. A circuit whose 2-qubit gates are all in the first half will therefore have its midpoint cut at the ~25 % mark of the total node list, not at 50 %.

3.  Snap each ideal position to the nearest TerminatorNode (without reuse), where “nearest” is measured in the cumulative 2-qubit-gate metric.

4.  Place the section boundary immediately *after* the chosen terminator (so the terminator is the last node of one section, and the next section starts with the first non-commuting gate after it).

This keeps sections balanced in routing workload while respecting the circuit’s commutation structure.

## API

The `sections` parameter controls behavior:

- `0` (auto): Derive the section count from the circuit’s 2-qubit critical path length (`floor(cp_2qb / 15) + 1`) and place boundaries at TerminatorNode positions. The critical path counts only 2-qubit gates on the longest path through the PDAG — single-qubit gates, measurements, and TerminatorNodes are ignored since they don’t create routing constraints.

- `1`: No sectionalization — compile in a single pass.

- `N > 1`: Exactly *N* sections with boundaries at TerminatorNode positions.

Functions

|  |  |
|----|----|
| [`prepare_dag_and_sections`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections.html#iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections "iqm.qrisp_iqm.passes.routing.core.sectionalization.prepare_dag_and_sections")(qc, \*\[, sections\]) | Convert a quantum circuit into a CSR instruction DAG. |
