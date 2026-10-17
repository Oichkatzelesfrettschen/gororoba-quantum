# rustworkx

## NAME

rustworkx 0.18.1 -- graph library in Rust: VF2 subgraph isomorphism, shortest
paths, coloring, bipartiteness.

## SYNOPSIS

```python
import rustworkx as rx
g = rx.PyGraph(); g.add_nodes_from(range(n)); g.add_edges_from_no_data(edges)
rx.vf2_mapping(host, pattern, subgraph=True, induced=False, id_order=True)
```

| Substrate | Status |
| --- | --- |
| Build host | python-rustworkx 0.18.1 (Arch), the pin in `requirements.txt` |
| Kaggle | hard dependency of qiskit (`rustworkx>=0.15.0` in the host's qiskit 2.5.2 metadata), so pip installs it with `qiskit==2.5.2`; the resolved version is not recorded in the repository's probes |

## CAPABILITIES IN THIS REPOSITORY

- Replica placement and layouts. `gororoba_quantum/packing.py` and
  `qpu_planning.py` map a pattern graph onto the CZ coupling graph with
  `rx.vf2_mapping(graph, pattern, subgraph=True, induced=False, id_order=True)`;
  `heron_multiprogramming.py` and `live_run.py` import the package too.
- The Kingston coupling graph from the retained snapshot: 156 nodes, 176
  edges, maximum degree 3, bipartite (example). It contains no 4-cycle, so a
  square pattern has no embedding; a 5-path does.
- Graph distance for routing estimates (`dijkstra_shortest_paths`).
- Parallelism: `parallel.py` states that forking a process that already runs
  Aer or rustworkx thread pools can deadlock a child, which is why it starts
  workers with spawn.

## API ENTRY POINTS

`rustworkx` public names (320), by introspection:

functions:

```text
  adjacency_matrix, all_pairs_all_simple_paths,
  all_pairs_bellman_ford_path_lengths,
  all_pairs_bellman_ford_shortest_paths, all_pairs_dijkstra_path_lengths,
  all_pairs_dijkstra_shortest_paths, all_shortest_paths, all_simple_paths,
  ancestors, articulation_points, astar_shortest_path,
  barabasi_albert_graph, bellman_ford_shortest_path_lengths,
  bellman_ford_shortest_paths, betweenness_centrality, bfs_layers,
  bfs_predecessors, bfs_search, bfs_successors, biconnected_components,
  bipartite_layout, bridges, cartesian_product, chain_decomposition,
  circular_layout, closeness_centrality, collect_bicolor_runs, collect_runs,
  complement, condensation, connected_components, connected_subgraphs,
  core_number, cycle_basis, dag_longest_path, dag_longest_path_length,
  dag_weighted_longest_path, dag_weighted_longest_path_length,
  degree_centrality, descendants, dfs_edges, dfs_search,
  digraph_adjacency_matrix, digraph_all_pairs_all_simple_paths,
  digraph_all_pairs_bellman_ford_path_lengths,
  digraph_all_pairs_bellman_ford_shortest_paths,
  digraph_all_pairs_dijkstra_path_lengths,
  digraph_all_pairs_dijkstra_shortest_paths, digraph_all_shortest_paths,
  digraph_all_simple_paths, digraph_astar_shortest_path,
  digraph_bellman_ford_shortest_path_lengths,
  digraph_bellman_ford_shortest_paths, digraph_betweenness_centrality,
  digraph_bfs_layers, digraph_bfs_search, digraph_bipartite_layout,
  digraph_cartesian_product, digraph_circular_layout,
  digraph_closeness_centrality, digraph_complement, digraph_condensation,
  digraph_core_number, digraph_degree_centrality, digraph_dfs_edges,
  digraph_dfs_search, digraph_dijkstra_search,
  digraph_dijkstra_shortest_path_lengths, digraph_dijkstra_shortest_paths,
  digraph_distance_matrix, digraph_edge_betweenness_centrality,
  digraph_eigenvector_centrality, digraph_find_cycle,
  digraph_floyd_warshall, digraph_floyd_warshall_numpy,
  digraph_floyd_warshall_successor_and_distance,
  digraph_generate_random_path, digraph_group_betweenness_centrality,
  digraph_group_closeness_centrality, digraph_group_degree_centrality,
  digraph_has_path, digraph_is_bipartite, digraph_is_isomorphic,
  digraph_is_subgraph_isomorphic, digraph_isolates,
  digraph_k_shortest_path_lengths, digraph_kamada_kawai_layout,
  digraph_katz_centrality, digraph_longest_simple_path,
  digraph_maximum_bisimulation,
  digraph_newman_weighted_closeness_centrality, digraph_node_link_json,
  digraph_num_shortest_paths_unweighted, digraph_random_layout,
  digraph_shell_layout, digraph_single_source_all_shortest_paths,
  digraph_spiral_layout, digraph_spring_layout, digraph_tensor_product,
  digraph_transitivity, digraph_two_color, digraph_union,
  digraph_unweighted_average_shortest_path_length, digraph_vf2_mapping,
  digraph_write_graphml, digraph_write_matrix_market, dijkstra_search,
  dijkstra_shortest_path_lengths, dijkstra_shortest_paths,
  directed_barabasi_albert_graph, directed_gnm_random_graph,
  directed_gnp_random_graph, directed_random_bipartite_graph,
  directed_sbm_random_graph, distance_matrix, dominance_frontiers,
  edge_betweenness_centrality, eigenvector_centrality, find_negative_cycle,
  floyd_warshall, floyd_warshall_numpy,
  floyd_warshall_successor_and_distance, from_dot, from_node_link_json_file,
  generate_random_path, graph_adjacency_matrix,
  graph_all_pairs_all_simple_paths,
  graph_all_pairs_bellman_ford_path_lengths,
  graph_all_pairs_bellman_ford_shortest_paths,
  graph_all_pairs_dijkstra_path_lengths,
  graph_all_pairs_dijkstra_shortest_paths, graph_all_shortest_paths,
  graph_all_simple_paths, graph_astar_shortest_path,
  graph_bellman_ford_shortest_path_lengths,
  graph_bellman_ford_shortest_paths, graph_betweenness_centrality,
  graph_bfs_layers, graph_bfs_search, graph_bipartite_edge_color,
  graph_bipartite_layout, graph_cartesian_product, graph_circular_layout,
  graph_closeness_centrality, graph_complement, graph_condensation,
  graph_core_number, graph_degree_centrality, graph_dfs_edges,
  graph_dfs_search, graph_dijkstra_search,
  graph_dijkstra_shortest_path_lengths, graph_dijkstra_shortest_paths,
  graph_distance_matrix, graph_edge_betweenness_centrality,
  graph_eigenvector_centrality, graph_floyd_warshall,
  graph_floyd_warshall_numpy, graph_floyd_warshall_successor_and_distance,
  graph_generate_random_path, graph_greedy_color, graph_greedy_edge_color,
  graph_group_betweenness_centrality, graph_group_closeness_centrality,
  graph_group_degree_centrality, graph_has_path, graph_is_bipartite,
  graph_is_isomorphic, graph_is_subgraph_isomorphic, graph_isolates,
  graph_k_shortest_path_lengths, graph_kamada_kawai_layout,
  graph_katz_centrality, graph_line_graph, graph_longest_simple_path,
  graph_misra_gries_edge_color, graph_newman_weighted_closeness_centrality,
  graph_node_link_json, graph_num_shortest_paths_unweighted,
  graph_random_layout, graph_shell_layout,
  graph_single_source_all_shortest_paths, graph_spiral_layout,
  graph_spring_layout, graph_tensor_product, graph_token_swapper,
  graph_transitivity, graph_two_color, graph_union,
  graph_unweighted_average_shortest_path_length, graph_vf2_mapping,
  graph_write_graphml, graph_write_matrix_market,
  group_betweenness_centrality, group_closeness_centrality,
  group_degree_centrality, has_path, hits, hyperbolic_greedy_routing,
  hyperbolic_greedy_success_rate, hyperbolic_random_graph,
  immediate_dominators, in_degree_centrality, is_bipartite, is_connected,
  is_directed_acyclic_graph, is_isomorphic, is_isomorphic_node_match,
  is_matching, is_maximal_matching, is_planar, is_semi_connected,
  is_strongly_connected, is_subgraph_isomorphic, is_weakly_connected,
  isolates, k_shortest_path_lengths, kamada_kawai_layout, katz_centrality,
  layers, lexicographical_topological_sort, local_complement,
  longest_simple_path, max_weight_matching, metric_closure,
  minimum_spanning_edges, minimum_spanning_tree, negative_edge_cycle,
  networkx_converter, newman_weighted_closeness_centrality,
  node_connected_component, node_link_json, num_shortest_paths_unweighted,
  number_connected_components, number_strongly_connected_components,
  number_weakly_connected_components, out_degree_centrality, pagerank,
  parse_node_link_json, random_geometric_graph, random_layout,
  random_regular_graph, read_graphml, read_matrix_market,
  read_matrix_market_file, shell_layout, simple_cycles,
  single_source_all_shortest_paths, spiral_layout, spring_layout,
  steiner_tree, stoer_wagner_min_cut, strongly_connected_components,
  tensor_product, topological_generations, topological_sort,
  transitive_reduction, transitivity, two_color,
  undirected_gnm_random_graph, undirected_gnp_random_graph,
  undirected_random_bipartite_graph, undirected_sbm_random_graph, union,
  unweighted_average_shortest_path_length, vf2_mapping,
  weakly_connected_components, write_graphml, write_matrix_market
```

## EXAMPLES

```python
import json
import rustworkx as rx

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
edges = sorted({tuple(sorted(r["qargs"])) for r in snap["instructions"]["cz"]})
g = rx.PyGraph()
g.add_nodes_from(range(snap["num_qubits"]))
g.add_edges_from_no_data(edges)
print("rustworkx", rx.__version__, "| coupling graph:", g.num_nodes(), "qubits,", g.num_edges(), "couplers")
print("max degree:", max(g.degree(i) for i in g.node_indices()), " bipartite:", rx.is_bipartite(g))

pattern = rx.PyGraph()
pattern.add_nodes_from(range(4))
pattern.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (3, 0)])        # a 4-cycle
count = sum(1 for _ in rx.vf2_mapping(g, pattern, subgraph=True, induced=False, id_order=True))
print("embeddings of a 4-cycle (heavy-hex has none):", count)
path = rx.PyGraph(); path.add_nodes_from(range(5)); path.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (3, 4)])
first = next(iter(rx.vf2_mapping(g, path, subgraph=True, induced=False, id_order=True)))
print("first 5-qubit path embedding:", dict(sorted(first.items())))
print("shortest path 0 -> 155 length:", len(rx.dijkstra_shortest_paths(g, 0, 155)[155]))
```

Output:

```text
rustworkx 0.18.1 | coupling graph: 156 qubits, 176 couplers
max degree: 3  bipartite: True
embeddings of a 4-cycle (heavy-hex has none): 0
first 5-qubit path embedding: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
shortest path 0 -> 155 length: 30
```

## INTEROP WITH QISKIT

The example builds the graph from the retained snapshot, not from a `CouplingMap`.
`CouplingMap` conversion was not run.

## CPU AND GPU

CPU (Rust; some algorithms use threads). No GPU path.

## TRAPS

- `vf2_mapping` returns an iterator of node-index dicts; `id_order=True` fixes
  the matching order for replay (the repository passes it).
- `induced=False` allows extra host edges among mapped nodes; `induced=True`
  would reject a mapping whose images share an additional coupler.
- Counting all embeddings of a symmetric pattern enumerates every automorphism.

## LICENSE

Apache-2.0.
