> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.maxcut_generator.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.maxcut_generator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c8972586f474678ba9bf4a1a3a8912b11e7fb7a879454b8fc33230a333e37ada.

# maxcut_generator

iqm.applications.maxcut.maxcut_generator(*n*, *n_instances*, *\**, *graph_family='erdos-renyi'*, *p=0.5*, *d=3*, *break_z2=False*, *seed=None*, *enforce_connected=False*, *max_iterations=1000*, *weighted=False*, *distribution_of_weights='uniform'*, *maximum=1.0*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L310-L376)  
The generator function for generating random maxcut problem instances.

The generator yields maxcut problem instances using random graphs, created according to the input parameters. If `enforce_connected` is set to `True`, then the resulting graphs are checked for connectivity and regenerated if the check fails. In that case, the output graphs are not strictly speaking Erdős–Rényi or uniformly random regular graphs anymore.

Parameters:  
- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of nodes of the graph.

- **n_instances** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of maxcut instances to generate.

- **graph_family** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['regular',* *'erdos-renyi'\]*) – A string describing the random graph family to generate. Possible graph families include ‘erdos-renyi’ and ‘regular’.

- **p** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – For the Erdős–Rényi graph, this is the edge probability. For other graph families, it’s ignored.

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – For the random regular graph, this is the degree of each node in the graph. For other graph families, it’s ignored.

- **break_z2** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Optional bool indicating whether the \\\mathbb{Z}\_2\\ symmetry should be explicitly broken in the problem instances.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None* *\|* [*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – Optional random seed for generating the problem instances.

- **enforce_connected** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – `True` iff it is required that the random graphs are connected.

- **max_iterations** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – In case `enforce_connected` is `True`, the function generates random graphs in a `while` loop until it finds a connected one. If it doesn’t find a connected one after `max_iterations`, it raises an error.

- **weighted** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – `True` iff we want to generate weighted maxcut instances (as opposed to unweighted maxcut).

- **distribution_of_weights** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['uniform',* *'integers'\]*) – A string describing the distribution of the random weights in case weighted maxcu is generated. Otherwise ignored.

- **maximum** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – A parameter of the distribution used if the distribution is “uniform” or “integers”, otherwise it’s ignored.

Yields:  
Problem instances of [`MaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance") randomly constructed in accordance to the input parameters. Or instances of [`WeightedMaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance") if `weighted` is `True`.

Return type:  
[*Iterator*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterator "(in Python v3.11)")\[[*MaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance") \| [*WeightedMaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance")\]
