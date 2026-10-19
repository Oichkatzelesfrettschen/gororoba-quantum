> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.rx_to_nx_graph.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.rx_to_nx_graph.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f081c3e21cd791b3f04d39f212dd88f7a2ea7f22d23a112e3a78a71e2b472fa0.

# iqm.benchmarks.utils_plots.rx_to_nx_graph

iqm.benchmarks.utils_plots.rx_to_nx_graph(*backend_coupling_map: CouplingMap*) → Graph  
Convert the Rustworkx graph returned by a backend to a Networkx graph.

Parameters:  
**backend_coupling_map** (*CouplingMap*) – The coupling map of the backend.

Returns:  
The Networkx Graph corresponding to the backend graph.

Return type:  
*Graph*
