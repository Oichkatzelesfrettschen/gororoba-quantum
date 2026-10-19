> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c3b77ec0945c07cfa547cdf18dc6ddbfd02bc12eb0db968bcac7f713c508f8ce.

# MaxCutInstance

Module: [`iqm.applications.maxcut`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.html#module-iqm.applications.maxcut "iqm.applications.maxcut")

*class* iqm.applications.maxcut.MaxCutInstance(*graph*, *break_z2=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L65-L177)  
Bases: [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance")

The maxcut instance class.

This class is initialized with a graph whose maxcut we try to find. A maxcut is a division of the graph nodes into two groups, such that the number of edges connecting nodes from different groups is maximized. The optional `break_z2` variable indicates whether the \\\mathbb{Z}\_2\\ symmetry of the problem is to be broken by pre-assigning one of the nodes to one of the groups.

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") describing the maxcut problem.

- **break_z2** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean variable indicating whether the \\\mathbb{Z}\_2\\ symmetry of the problem should be artificially broken, reducing the number of problem variables by 1.

Attributes

|  |  |
|----|----|
| [`graph`](#iqm.applications.maxcut.MaxCutInstance.graph "iqm.applications.maxcut.MaxCutInstance.graph") | The graph of the problem. |

Methods

|  |  |
|----|----|
| [`cut_size`](#iqm.applications.maxcut.MaxCutInstance.cut_size "iqm.applications.maxcut.MaxCutInstance.cut_size") | Calculates the cut size of a solution represented by a bitstring. |
| [`draw_problem`](#iqm.applications.maxcut.MaxCutInstance.draw_problem "iqm.applications.maxcut.MaxCutInstance.draw_problem") | The method to draw an instance of maxcut, with the solution highlighted. |

*property* graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The graph of the problem.

Equals the graph that was given on initialization of [`MaxCutInstance`](#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance") and shouldn’t be modified. Instead of modifying the graph, the user should instantiate a new object of [`MaxCutInstance`](#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance").

cut_size(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L112-L146)  
Calculates the cut size of a solution represented by a bitstring.

The calculation simply iterates over edges of the graph and adds +1 for each edge cut according to the bitstring. Since it uses the original graph, the input bitstring needs to have the same length as the graph has nodes.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A string of 0’s and 1’s (or any two distinct characters) representing the division of the graph into two sets.

Returns:  
The number of edges cut.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the length of the input bitstring isn’t equal to the number of nodes of `_graph`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the bitstring contains more than 2 different characters (it doesn’t have to be 0’s and 1’s).

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

draw_problem(*solution_bitstring=None*, *seed=None*, *highlight_edge_by_node_count=frozenset({1})*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L148-L177)  
The method to draw an instance of maxcut, with the solution highlighted.

Parameters:  
- **solution_bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – A bitstring representing a solution to the problem. Selected nodes are represented as 1’s, the other nodes are represented as 0’s. This skips nodes that have been fixed, e.g., by breaking the Z2 symmetry. The full bitstring including the fixed nodes is restored internally by calling [`restore_fixed_variables_bitstring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring").

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed to derandomize the layout of the graph.

- **highlight_edge_by_node_count** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – How many of the endnodes of an edge need to be highlighted to also make the edge highlighted. For maxcut, this should be `frozenset({1})` so that cut edges are highlighted.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.applications.maxcut.MaxCutInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-88832d0a4d669b0fa965e23d414ce96e75ccba35.png)
