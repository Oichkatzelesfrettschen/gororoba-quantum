> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.rx_to_nx.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.rx_to_nx.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bcfd5a4de1cf9edce135c25fcdbf2c786adbfe4e620b6394c063591fed0c9ca7.

# rx_to_nx

Full path: iqm.qaoa.transpiler.rx_to_nx

Module to carry a helpful function to transform a `rustworkx` graph into a [`networkx.Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)").

This function isn’t included in `rustworkx` or [networkx](https://networkx.org/documentation/stable/reference/index.html) because these two packages don’t want to have the other as a dependency.

Functions

|  |  |
|----|----|
| [`rustworkx_to_networkx`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx.html#iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx "iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx")(graph) | Convert a `rustworkx` graph to a [`networkx.Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)"). |
