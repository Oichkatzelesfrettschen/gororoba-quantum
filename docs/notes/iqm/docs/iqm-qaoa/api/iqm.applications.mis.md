> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9517fead10ddcfb0fbdfad6e59710a6c803eb67bae65f82f5aa5a63a0545cd6f.

# mis

Full path: iqm.applications.mis

Module containing the MIS problem instance class.

Two solvers for MIS problems are also provided:

- A simple and fast greedy solver.

- Exact solver based on *Bron-Kerbosch* algorithm to find a graph’s cliques.

Example

``` python
from iqm.applications.mis import MISInstance
from iqm.applications.mis import greedy_mis
from iqm.applications.mis import bron_kerbosch

my_mis_instance = MISInstance(my_graph, penalty = 2)  # Problem instance from a graph.
my_mis_instance.constraints_checker("101011000")  # Check if this corresponds to an independent set.

greedy_solution = greedy_mis(my_instance)  # Solution bitstring obtained from greedy.
bk_solution = bron_kerbosch(my_instance)  # Solution bitstring obtained from BK.
```

Functions

|  |  |
|----|----|
| [`bron_kerbosch`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.bron_kerbosch.html#iqm.applications.mis.bron_kerbosch "iqm.applications.mis.bron_kerbosch")(mis_problem\[, all_solutions\]) | Bron-Kerbosch algorithm for finding the maximum independent set. |
| [`greedy_mis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mis.html#iqm.applications.mis.greedy_mis "iqm.applications.mis.greedy_mis")(mis_problem\[, seed\]) | Standard greedy algorithm for maximum independent set problem class. |
| [`greedy_mwis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mwis.html#iqm.applications.mis.greedy_mwis "iqm.applications.mis.greedy_mwis")(mwis_problem\[, seed\]) | Compute an approximation to the maximum-weight independent set using a greedy heuristic. |
| [`mis_generator`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.mis_generator.html#iqm.applications.mis.mis_generator "iqm.applications.mis.mis_generator")(n, n_instances, \*\[, ...\]) | The generator function for generating random MIS problem instances. |

Classes

|  |  |
|----|----|
| [`ISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance") | The instance class for independent set problems on a graph with a custom cost function. |
| [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance") | The instance class for maximum independent set problems. |
| [`MaximumWeightISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html#iqm.applications.mis.MaximumWeightISInstance "iqm.applications.mis.MaximumWeightISInstance") | The instance class for maximum-weight independent set problems. |

Inheritance

![Inheritance diagram of iqm.applications.mis](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-743b1691f1155574533f79cc18fcd48c29acdd43.png)
