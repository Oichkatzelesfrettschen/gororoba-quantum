> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.plasma_layout.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.plasma_layout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 42888fdbfddc93681e34b8bd191630007b2085ac096ccda631f34523e87a87e7.

# plasma_layout

Full path: iqm.qrisp_iqm.passes.routing.plasma_layout

SABRE layout pass.

Finds an initial qubit mapping (logical → physical) that minimizes the SABRE routing cost. Chain with `plasma_route()` for a full transpiler pipeline.

## Forward/backward layout refinement

Finding a good initial layout is essential: the routing pass greedily inserts SWAPs to satisfy 2-qubit gate connectivity, and a poor starting mapping forces many unnecessary SWAPs early on that cascade through the rest of the circuit.

The layout search generates many random candidate mappings and scores each one. Scoring uses SABRE’s **forward/backward refinement loop**:

1.  Route the circuit *forward* starting from the candidate mapping. The forward pass’s final permutation favours the circuit’s *last* gates.

2.  Use that permutation as the starting layout and route *backward* (reversed gate order). The backward pass ends with a permutation that places the circuit’s *first* gates’ qubits close together.

3.  Repeat for several iterations. Each round improves the layout for both ends of the circuit.

Because the loop ends with a backward pass, the final mapping is already optimised for the circuit’s *first* gates — exactly what the downstream forward routing needs. No extra backward pass is required.

The parallel evaluation function returns both scores and refined mappings. The best refined mapping is used directly, avoiding a redundant re-refinement from the original seed.

## Section-aware evaluation

When sectionalized routing is active (`sections != 1`), the layout search must mirror what the downstream `plasma_route()` pass will actually do. If the layout pass evaluates candidates on an *unsectioned* DAG while routing later uses sectioned SABRE, the proxy cost diverges from the true objective. In particular, the unsectioned evaluation ignores the fact that each section is compiled independently — a layout that looks good globally may be poor for the first section, and that mistake cascades.

To fix this, the layout evaluation performs **sectionized** forward and backward passes: the circuit DAG is split at the same terminator-based boundaries that `plasma_route()` will use, each section is compiled independently, and the total swap count across all sections is the scoring metric.

## Section-aligned backward passes

During layout refinement the backward pass must use the forward section lengths in reversed order (`section_lengths[::-1]`), **not** independently computed backward sections. The backward pass processes gates in the opposite order: if forward sections are `[S_1, S_2, ..., S_N]`, the backward pass routes them as `[S_N, S_{N-1}, ..., S_1]`. By using reversed forward section lengths, backward section *k* processes exactly the gates of forward section *N − k*. The backward pass’s last section therefore covers exactly the gates in forward section `S_1`, so the resulting permutation places those qubits close together — which is exactly what the forward pass needs for its first section.

If independently computed backward sections were used instead, the backward pass’s last section would cover arbitrary gates (determined by the reversed circuit’s commutation structure, which differs due to TerminatorNode placement). The resulting permutation would be optimised for those arbitrary gates rather than for `S_1`, producing a starting layout misaligned with the forward pass’s first section.

## Backward DAG construction

The backward DAG is built by reversing the forward CSR adjacency matrix (see [`reverse_dag()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag")). This reverses all dependency edges *and* flips the node ordering so that the last forward nodes become the first backward nodes. Building a PermeabilityGraph from the reversed circuit is *not* suitable because it would place TerminatorNodes at different positions, producing a structurally different DAG.

## Impact

Circuits with no sectionalization (C=1) are unaffected — both changes are no-ops. Circuits with deep conjugate structure (e.g. Grover with C=6/20, ripple-carry adders, random circuits with many sections) see 10–28 % reductions in routed 2-qubit gate count compared to unsectioned layout evaluation.
