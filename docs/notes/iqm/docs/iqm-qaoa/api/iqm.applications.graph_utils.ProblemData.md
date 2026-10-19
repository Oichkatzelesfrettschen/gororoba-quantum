> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.ProblemData.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.ProblemData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d0ff420d89463ee1609b6704511671c2cb2a12fcb91e397388064c4aa3ff9a82.

# ProblemData

Module: [`iqm.applications.graph_utils`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.html#module-iqm.applications.graph_utils "iqm.applications.graph_utils")

*class* iqm.applications.graph_utils.ProblemData(*graph*, *fixed_vars*, *bitstring*, *highlight_edge_by_node_count*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L171-L182)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Normalized problem information extracted and validated before plotting.

Attributes

|  |  |
|----|----|
| [`graph`](#iqm.applications.graph_utils.ProblemData.graph "iqm.applications.graph_utils.ProblemData.graph") | The problem graph to be visualized. |
| [`fixed_vars`](#iqm.applications.graph_utils.ProblemData.fixed_vars "iqm.applications.graph_utils.ProblemData.fixed_vars") | Set of variables that were fixed in the optimization problem instance. |
| [`bitstring`](#iqm.applications.graph_utils.ProblemData.bitstring "iqm.applications.graph_utils.ProblemData.bitstring") | Bitstring representing highlighted (active) nodes in the solution. |
| [`highlight_edge_by_node_count`](#iqm.applications.graph_utils.ProblemData.highlight_edge_by_node_count "iqm.applications.graph_utils.ProblemData.highlight_edge_by_node_count") | Rule describing which edges to highlight based on how many connected nodes are highlighted. |

Methods

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)"))

- **fixed_vars** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **highlight_edge_by_node_count** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The problem graph to be visualized.

fixed_vars*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Set of variables that were fixed in the optimization problem instance.

bitstring*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Bitstring representing highlighted (active) nodes in the solution.

highlight_edge_by_node_count*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Rule describing which edges to highlight based on how many connected nodes are highlighted.

Inheritance

![Inheritance diagram of iqm.applications.graph_utils.ProblemData](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-534424ed5e04590df6a89eeb5db2ad540a287a69.png)
