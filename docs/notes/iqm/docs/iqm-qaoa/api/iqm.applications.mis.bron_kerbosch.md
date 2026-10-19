> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.bron_kerbosch.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.bron_kerbosch.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 144a3b3a3e50d744e866d760c8f36b7e6aa4369616d0ac2d5412e5c338aea345.

# bron_kerbosch

iqm.applications.mis.bron_kerbosch(*mis_problem*, *all_solutions=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L539-L581)  
Bron-Kerbosch algorithm for finding the maximum independent set.

The algorithm finds all maximal cliques in a graph recursively. Cliques in complement graph correspond to independent sets in the problem graph. For details see [find_cliques — NetworkX documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.clique.find_cliques.html) (and the references therein). If `all_solutions` is False (default), return one maximum independent set as a bitstring. If `all_solutions` is True, return a set of bitstrings corresponding to all maximum independent sets found (not all **maximal** independent sets).

Parameters:  
- **mis_problem** ([*MISInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance")) – A problem instance of maximum independent set to be solved.

- **all_solutions** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should the algorithm return all solutions?

Returns:  
A bitstring solution.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
