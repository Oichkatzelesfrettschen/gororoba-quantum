> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 34cc044e8abee53a40f24c03260b132494544f70ab1e67878cac7d6bfa6c2b90.

# MaximumWeightISInstance

Module: [`iqm.applications.mis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.html#module-iqm.applications.mis "iqm.applications.mis")

*class* iqm.applications.mis.MaximumWeightISInstance(*graph*, *penalty*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L321-L410)  
Bases: [`ISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance")

The instance class for maximum-weight independent set problems.

The maximum-weight independent set problem refers to finding a subset of nodes of a graph, such that no nodes in the subset are connected by an edge and sum of the weights of the nodes in the subset is maximized. The class is initialized by initializing its parent class [`ISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance") with a custom objective function (carrying the weights of the graph nodes).

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") describing the maximum-weight independent set problem. Each node of the graph needs to have an attribute (something like “weight”) storing a number. Specifically, the initialization method looks fornode attributes from the tuple [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY") (in order) and takes the first one as the node weight.

- **penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The penalty to be incurred per each edge present in the solution, sometimes referred to as \\\lambda\\ in the literature. The higher it is, the less likely the algorithm is to include an edge in the solution. This is needed when the problem formulation is transformed into QUBO.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If any of the input graph’s nodes doesn’t have any attribute from the tuple of attributes [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY").

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the weight of any node is a wrong data type (neither [`float`](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") nor [`int`](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")).

Attributes

|  |  |
|----|----|
| [`highest_quality_bitstrings`](#iqm.applications.mis.MaximumWeightISInstance.highest_quality_bitstrings "iqm.applications.mis.MaximumWeightISInstance.highest_quality_bitstrings") | The worst bitstring(s) for the MWIS problem, determined trivially if all weights are non-negative. |

Methods

|  |  |
|----|----|
| [`fix_constraint_violation_bitstring`](#iqm.applications.mis.MaximumWeightISInstance.fix_constraint_violation_bitstring "iqm.applications.mis.MaximumWeightISInstance.fix_constraint_violation_bitstring") | Postprocessing function that fixes a single bitstring, making it satisfy the constraints. |

*property* highest_quality_bitstrings*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The worst bitstring(s) for the MWIS problem, determined trivially if all weights are non-negative.

fix_constraint_violation_bitstring(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L380-L410)  
Postprocessing function that fixes a single bitstring, making it satisfy the constraints.

It works in the following way:

1.  Get the subgraph induced by the bitstring `bit_str`.

2.  Find the approximate minimum-weight vertex cover of the graph with a greedy algorithm, breaking ties at random.

3.  Remove those nodes from the induced subgraph.

4.  Return the bitstring corresponding to the remaining subgraph (which is an independent subset of the original graph).

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring to be modified to satisfy the independence constraint.

Returns:  
A bitstring corresponding to greedily pruned `bit_str`.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.applications.mis.MaximumWeightISInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-f81c60263ad5776cc9814fbad773a2fed20d6edb.png)
