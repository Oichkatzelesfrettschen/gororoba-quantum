> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.mis_generator.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.mis_generator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8e0cd022564805c301b8e617e18b24addaf01c4574f408915f5e642b324d7051.

# mis_generator

iqm.applications.mis.mis_generator(*n*, *n_instances*, *\**, *graph_family='erdos-renyi'*, *p=0.5*, *d=3*, *seed=None*, *enforce_connected=False*, *max_iterations=1000*, *penalty=1*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L584-L625)  
The generator function for generating random MIS problem instances.

The generator yields MIS problem instances using random graphs, created according to the input parameters. If `enforce_connected` is set to `True`, then the resulting graphs are checked for connectivity and regenerated if the check fails. In that case, the output graphs are not strictly speaking Erdős–Rényi or uniformly random regular graphs anymore.

Parameters:  
- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of nodes of the graph.

- **n_instances** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of MIS instances to generate.

- **graph_family** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['regular',* *'erdos-renyi'\]*) – A string describing the random graph family to generate. Possible graph families include ‘erdos-renyi’ and ‘regular’.

- **p** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – For the Erdős–Rényi graph, this is the edge probability. For other graph families, it’s ignored.

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – For the random regular graph, this is the degree of each node in the graph. For other graph families, it’s ignored.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None* *\|* [*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – Optional random seed for generating the problem instances.

- **enforce_connected** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – `True` iff it is required that the random graphs are connected.

- **max_iterations** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – In case `enforce_connected` is `True`, the function generates random graphs in a `while` loop until it finds a connected one. If it doesn’t find a connected one after `max_iterations`, it raises an error.

- **penalty** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The penalty to the energy for violating the independence constraint.

Yields:  
Problem instances of [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance") randomly constructed in accordance to the input parameters.

Return type:  
[*Iterator*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterator "(in Python v3.11)")\[[*MISInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance")\]
