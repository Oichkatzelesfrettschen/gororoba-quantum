> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a2da7ed3ca3c1a6a6f7fcad948c8e6f99b4acfe7e1abbeabade3a6ba58bbdc69.

# QUBOInstance

Module: [`iqm.applications.qubo`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.html#module-iqm.applications.qubo "iqm.applications.qubo")

*class* iqm.applications.qubo.QUBOInstance(*qubo_object*, *vartype='BINARY'*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L63-L294)  
Bases: [`ProblemInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance")

A problem instance class for generic QUBO problems.

This problem instance class should only be used for problems without any structure beyond having a QUBO cost function. Problems with constraints or more structure (such as maxcut, MIS, …) should use sub-classes (children) of [`QUBOInstance`](#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance").

The class is initialized with a `qubo_object` variable, which stores the QUBO parameters. Valid `qubo_object` is either a 2D square [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") or `BinaryQuadraticModel`. In the case of a [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)"), the interactions need to be represented as attributes of nodes / edges. The initialization method looks for the edge/node attributes in the order specified by the tuples [`EDGE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html#iqm.applications.graph_utils.EDGE_ATTR_PRIORITY "iqm.applications.graph_utils.EDGE_ATTR_PRIORITY") and [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY") respectively. Regardless of the type of `qubo_object`, the `__init__()` method internally saves the problem description as [`bqm`](#iqm.applications.qubo.QUBOInstance.bqm "iqm.applications.qubo.QUBOInstance.bqm"), which is a `BinaryQuadraticModel`.

Parameters:  
- **qubo_object** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") *\|* [*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – Either a square [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), a [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") or a `BinaryQuadraticModel` describing the QUBO problem.

- **vartype** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\[Vartype.SPIN,* *'SPIN',* *Vartype.BINARY,* *'BINARY',* *Vartype.INTEGER,* *'INTEGER',* *Vartype.REAL,* *'REAL'\]*) – An optional variable type for interpreting the input [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") or [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") as `BinaryQuadraticModel`. The default value is ‘BINARY’.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the provided `qubo_object` is a graph with a node or an edge without any attribute from [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY") or [`EDGE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html#iqm.applications.graph_utils.EDGE_ATTR_PRIORITY "iqm.applications.graph_utils.EDGE_ATTR_PRIORITY") respectively.

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the provided `qubo_object` is a graph with a node or an edge with a correct attribute name, but containing a value of incorrect type.

- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the input `qubo_object` is neither of the expected types.

Attributes

|  |  |
|----|----|
| [`average_quality`](#iqm.applications.qubo.QUBOInstance.average_quality "iqm.applications.qubo.QUBOInstance.average_quality") | The average quality value over all possible bitstrings. |
| [`bqm`](#iqm.applications.qubo.QUBOInstance.bqm "iqm.applications.qubo.QUBOInstance.bqm") | The `BinaryQuadraticModel` representation of the problem instance. |
| [`dim`](#iqm.applications.qubo.QUBOInstance.dim "iqm.applications.qubo.QUBOInstance.dim") | The dimension of the problem (i.e., the number of binary variables). |
| [`qubo_graph`](#iqm.applications.qubo.QUBOInstance.qubo_graph "iqm.applications.qubo.QUBOInstance.qubo_graph") | The QUBO graph of the problem instance. |
| [`qubo_matrix`](#iqm.applications.qubo.QUBOInstance.qubo_matrix "iqm.applications.qubo.QUBOInstance.qubo_matrix") | The QUBO matrix of the problem instance. |

Methods

|  |  |
|----|----|
| [`draw_problem`](#iqm.applications.qubo.QUBOInstance.draw_problem "iqm.applications.qubo.QUBOInstance.draw_problem") | The method to draw a graph corresponding to an instance of a QUBO problem, with the solution highlighted. |
| [`fix_variables`](#iqm.applications.qubo.QUBOInstance.fix_variables "iqm.applications.qubo.QUBOInstance.fix_variables") | Fixes (assigns) some of the problem variables. |
| [`quality`](#iqm.applications.qubo.QUBOInstance.quality "iqm.applications.qubo.QUBOInstance.quality") | Accepts a bitstring (representing a solution) and returns that solution's quality / energy. |

*property* dim*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
The dimension of the problem (i.e., the number of binary variables).

*property* qubo_matrix*: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*  
The QUBO matrix of the problem instance.

The matrix is obtained from the internal variable [`bqm`](#iqm.applications.qubo.QUBOInstance.bqm "iqm.applications.qubo.QUBOInstance.bqm"). If the QUBO cost function of the problem variables \\x_i \in \\0, 1\\\\ is described as:

\\C = \sum\_{i\<j} x_i Q\_{ij} x_j + \sum\_{i} x_i Q\_{ii} x_i\\

Then the output of this method is the square matrix \\Q\_{ij}\\ as [`ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)").

- The diagonal entries corresponds to the local fields acting on the variables.

- The entries above the diagonal correspond to the interactions between variables.

- The entries below the diagonal are empty.

*property* qubo_graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The QUBO graph of the problem instance.

The nodes / edges of the graph have a `bias` parameter containing the local field / interaction strength of the corresponding variable(s). Variable pairs without interaction aren’t connected by edges in the graph.

*property* bqm*: [BinaryQuadraticModel](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")*  
The `BinaryQuadraticModel` representation of the problem instance.

This variable is defined in `__init__()` and is used throughout the class to calculate such quantities as [`dim`](#iqm.applications.qubo.QUBOInstance.dim "iqm.applications.qubo.QUBOInstance.dim") or [`qubo_matrix`](#iqm.applications.qubo.QUBOInstance.qubo_matrix "iqm.applications.qubo.QUBOInstance.qubo_matrix") lazily.

*property* average_quality*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The average quality value over all possible bitstrings.

For QUBO problems, this is equal to the constant term in the spin/Hamiltonian formulation of the cost function.

fix_variables(*variables*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L207-L234)  
Fixes (assigns) some of the problem variables.

Warning: For problems that come from a graph (such as maxcut), this doesn’t change the original graph, only the derived QUBO formulation (i.e., the BQM variable)!

Parameters:  
**variables** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Hashable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Hashable "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Either an iterable of variables (which get all fixed to the value 1) or a dictionary with keys equal to the variables to fix and whose values are equal to the values to fix them to (either 1 or 0).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If one of the variables has already been fixed previously to a different value.

Return type:  
None

quality(*bit_str*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L236-L257)  
Accepts a bitstring (representing a solution) and returns that solution’s quality / energy.

Parameters:  
**bit_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The bitstring whose quality is being calculated.

Returns:  
The energy of the input bitstring.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the length of the input bitstring does not match the number of variables of the problem.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

draw_problem(*solution_bitstring=None*, *seed=None*, *highlight_edge_by_node_count=frozenset({2})*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/qubo.py#L259-L294)  
The method to draw a graph corresponding to an instance of a QUBO problem, with the solution highlighted.

Parameters:  
- **solution_bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – A bitstring representing a solution to the problem. Selected nodes are represented as 1’s, the other nodes are represented as 0’s. This skips nodes that have been fixed. The full bitstring including the fixed nodes is restored internally by calling [`restore_fixed_variables_bitstring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring").

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The seed to derandomize the layout of the graph.

- **highlight_edge_by_node_count** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Contains the numbers of highlighted nodes that an edge has to be connected to, in order to be highlighted itself. In other words, if `highlight_edge_by_node_count` is `frozenset({1})`, then edges connected to 1 highlighted node will be themselves highlighted. Edges connecting 2 highlighted nodes (or 2 non-highlighted nodes) will not be highlighted.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.applications.qubo.QUBOInstance](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-4911c82b69c1f697954db0d07be94e163f094751.png)
