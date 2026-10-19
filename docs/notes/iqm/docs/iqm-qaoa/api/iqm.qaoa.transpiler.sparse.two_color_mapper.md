> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 63fa0fa9e91f049008cbe020b3482720f2c1a44e55e4a2f03a891fdc9a4387b3.

# two_color_mapper

Full path: iqm.qaoa.transpiler.sparse.two_color_mapper

Module containing the [`two_color_mapper()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper.html#iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper "iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper") function, which creates the initial mapping.

The created [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") is based on the edge coloring of the graph created by the [`find_edge_coloring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring") function.

Functions

|  |  |
|----|----|
| [`two_color_mapper`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper.html#iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper "iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper")(problem_bqm, qpu, color_sets) | Finds an initial mapping between logical and hardware qubits. |
