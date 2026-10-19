> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9cac5e7ec066c8eb48283739339c68f3e417cc7c17e07e2e58cf69a28d949f16.

# WeightedMaxCutInstance

Module: [`iqm.applications.maxcut`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.html#module-iqm.applications.maxcut "iqm.applications.maxcut")

*class* iqm.applications.maxcut.WeightedMaxCutInstance(*graph*, *break_z2=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L180-L307)  
Bases: [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance")

The weighted maxcut instance class.

The weighted maxcut problem is very similar to the standard maxcut, with the only difference being that the edges of the graph now have weights. Each cut edge contributes its weight to the quality of the cut.

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") describing the weighted maxcut problem. Each edge of the graph needs to have an attribute (something like “weight”) storing a number. Specifically, the initialization method looks for edge attributes from the tuple [`EDGE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html#iqm.applications.graph_utils.EDGE_ATTR_PRIORITY "iqm.applications.graph_utils.EDGE_ATTR_PRIORITY") (in order) and takes the first one as the edge weight.

- **break_z2** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean variable indicating whether the \\\mathbb{Z}\_2\\ symmetry of the problem should be artificially broken, reducing the number of problem variables by 1.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If any of the input graph’s edges doesn’t have any attribute from the tuple of attributes [`EDGE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html#iqm.applications.graph_utils.EDGE_ATTR_PRIORITY "iqm.applications.graph_utils.EDGE_ATTR_PRIORITY").

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the weight of any edge is a wrong data type (neither [`float`](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") nor [`int`](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")).

Attributes

|  |  |
|----|----|
| [`graph`](#iqm.applications.maxcut.WeightedMaxCutInstance.graph "iqm.applications.maxcut.WeightedMaxCutInstance.graph") | The graph of the problem. |

Methods

|  |  |
|----|----|
| [`cut_size`](#iqm.applications.maxcut.WeightedMaxCutInstance.cut_size "iqm.applications.maxcut.WeightedMaxCutInstance.cut_size") | Calculates the cut size of a solution represented by a bitstring. |
| [`draw_problem`](#iqm.applications.maxcut.WeightedMaxCutInstance.draw_problem "iqm.applications.maxcut.WeightedMaxCutInstance.draw_problem") | The method to draw an instance of weighted maxcut, with the solution highlighted. |

*property* graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The graph of the problem.

Equals the graph that was given on initialization of [`WeightedMaxCutInstance`](#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance") and shouldn’t be modified. Instead of modifying the graph, the user should instantiate a new object of [`WeightedMaxCutInstance`](#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance").

cut_size(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L241-L275)  
Calculates the cut size of a solution represented by a bitstring.

The calculation simply iterates over edges of the graph and adds the weight of each edge cut according to the bitstring. Since it uses the original graph, the input bitstring needs to have the same length as the graph has nodes.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A string of 0’s and 1’s (or any two distinct characters) representing the division of the graph into two sets.

Returns:  
The weight of edges cut.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the length of the input bitstring isn’t equal to the number of nodes of [`graph`](#iqm.applications.maxcut.WeightedMaxCutInstance.graph "iqm.applications.maxcut.WeightedMaxCutInstance.graph").

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the bitstring contains more than 2 different characters (it doesn’t have to be 0’s and 1’s).

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

draw_problem(*solution_bitstring=None*, *seed=None*, *highlight_edge_by_node_count=frozenset({1})*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L277-L307)  
The method to draw an instance of weighted maxcut, with the solution highlighted.

Parameters:  
- **solution_bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – A bitstring representing a solution to the problem. Selected nodes are represented as 1’s, the other nodes are represented as 0’s. This skips nodes that have been fixed, e.g., by breaking the Z2 symmetry. The full bitstring including the fixed nodes is restored internally by calling [`restore_fixed_variables_bitstring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring").

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed to derandomize the layout of the graph.

- **highlight_edge_by_node_count** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – How many of the endnodes of an edge need to be highlighted to also make the edge highlighted. For weighted maxcut, this should be `frozenset({1})` so that cut edges are highlighted.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.applications.maxcut.WeightedMaxCutInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-dc8bd632bdfe82fc4ae69cf6b5ab0acf6028e13f.png)
