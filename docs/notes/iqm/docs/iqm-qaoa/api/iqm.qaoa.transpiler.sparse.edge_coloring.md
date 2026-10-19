> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 35da66403434a814be2e2e791e65d370991711174346690bad5115d95a23474f.

# edge_coloring

Full path: iqm.qaoa.transpiler.sparse.edge_coloring

The module for the edge-coloring of the graph.

This file contains code to find the edge coloring of an arbitrary simple graph according to the program defined in \[[6](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id6 "J. Misra and David Gries. A constructive proof of vizing's theorem. Information Processing Letters, 41(3):131-133, 1992. URL: https://www.sciencedirect.com/science/article/pii/002001909290041S, doi:https://doi.org/10.1016/0020-0190(92)90041-S.")\]. Almost all functions in this file are helper functions. Only [`find_edge_coloring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring") is intended for external use. The function [`plot_edge_coloring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring") may be used for debugging purposes.

Functions

|  |  |
|----|----|
| [`ec_is_complete`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete.html#iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete "iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete")(graph) | Check that a graph's edge coloring is complete. |
| [`ec_is_valid`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid.html#iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid "iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid")(graph) | Check that a graph's edge coloring is valid. |
| [`find_edge_coloring`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring")(input_graph) | Find an edge coloring for the given graph. |
| [`plot_edge_coloring`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring")(graph\[, pos, ...\]) | A method that plots the edge coloring of a graph. |
