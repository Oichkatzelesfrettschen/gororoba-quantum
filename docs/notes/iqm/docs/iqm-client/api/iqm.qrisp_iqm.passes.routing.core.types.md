> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 904748f2b5592f27c50ab9cd7fa6dab72ad6e0dcbc485506261cfd7692f09106.

# types

Full path: iqm.qrisp_iqm.passes.routing.core.types

Dynamic index-type selection for plasma-sabre routing passes.

Provides a single source of truth for choosing the narrowest numpy integer dtype that can safely represent a given index range. All data structures (coupling topology, instruction DAGs, layout permutations, depth trackers, etc.) should derive their dtype from the functions in this module rather than hard-coding `np.int32`.

## Rationale

Plasma-sabre targets NISQ devices (\< 32 768 qubits). Quantum circuits are expected to contain fewer than 32 768 two-qubit gates before decoherence destroys any meaningful entanglement. Under these assumptions **all** index values fit into `np.int16`, which doubles cache-line density compared to `np.int32` and substantially improves ALU throughput in the hot SABRE metric loop.

Functions

|  |  |
|----|----|
| [`data_dtype`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.data_dtype.html#iqm.qrisp_iqm.passes.routing.core.types.data_dtype "iqm.qrisp_iqm.passes.routing.core.types.data_dtype")(n_physical, n_nodes) | Return dtype for `instruction_data` (Mx3) arrays. |
| [`index_dtype`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.index_dtype.html#iqm.qrisp_iqm.passes.routing.core.types.index_dtype "iqm.qrisp_iqm.passes.routing.core.types.index_dtype")(max_value) | Return the narrowest numpy signed-integer dtype for the given range. |
| [`node_dtype`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.node_dtype.html#iqm.qrisp_iqm.passes.routing.core.types.node_dtype "iqm.qrisp_iqm.passes.routing.core.types.node_dtype")(n_nodes) | Return dtype suitable for per-DAG-node data structures. |
| [`qubit_dtype`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.types.qubit_dtype.html#iqm.qrisp_iqm.passes.routing.core.types.qubit_dtype "iqm.qrisp_iqm.passes.routing.core.types.qubit_dtype")(n_physical) | Return dtype suitable for per-qubit data structures. |
