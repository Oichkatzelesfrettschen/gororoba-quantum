> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd732456f3c367551c232d5eda4678730ac3653b878beb4e3416b07445f80330.

# maxcut

Full path: iqm.applications.maxcut

Module containing the maxcut problem instance class and related functions.

Contains the iterator function [`maxcut_generator()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.maxcut_generator.html#iqm.applications.maxcut.maxcut_generator "iqm.applications.maxcut.maxcut_generator") which yields random instances of [`MaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance"), useful for applications such as calculating the Q-score. Also contains two classical solvers for maxcut problems:

- A simple and fast greedy algorithm.

- A solver based on the standard *Goemans-Williamson* \[[1](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id5 "Michel X. Goemans and David P. Williamson. Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming. J. ACM, 42(6):1115–1145, November 1995. URL: https://doi.org/10.1145/227683.227684, doi:10.1145/227683.227684.")\], fast and with a performance guarantee.

Example

``` python
from iqm.applications.maxcut import MaxCutInstance
from iqm.applications.maxcut import maxcut_generator
from iqm.applications.maxcut import goemans_williamson
from iqm.applications.maxcut import greedy_max_cut

for my_instance in maxcut_generator(graph_size, n_instances):  # Generates problem instances.
    gw_solution = goemans_williamson(my_instance)  # Solution bitstring obtained from GW.
    greedy_solution = greedy_max_cut(my_instance)  # Solution bitstring obtained from greedy.
    my_instance.cut_size(gw_solution)  # Check the GW solution cut size.

my_maxcut_instance = MaxCutInstance(my_graph)  # Problem instance from a graph.
```

Functions

|  |  |
|----|----|
| [`goemans_williamson`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.goemans_williamson.html#iqm.applications.maxcut.goemans_williamson "iqm.applications.maxcut.goemans_williamson")(max_cut_problem\[, seed\]) | Runs the Goemans-Williamson algorithm for maxcut, returning a solution bitstring. |
| [`greedy_max_cut`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.greedy_max_cut.html#iqm.applications.maxcut.greedy_max_cut "iqm.applications.maxcut.greedy_max_cut")(max_cut_problem\[, seed\]) | Standard greedy algorithm for maxcut problem class. |
| [`max_cut_exact`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.max_cut_exact.html#iqm.applications.maxcut.max_cut_exact "iqm.applications.maxcut.max_cut_exact")(problem) | Runs an exact solver for the (weighted) maxcut problem, using branch-and-bound. |
| [`maxcut_generator`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.maxcut_generator.html#iqm.applications.maxcut.maxcut_generator "iqm.applications.maxcut.maxcut_generator")(n, n_instances, \*\[, ...\]) | The generator function for generating random maxcut problem instances. |

Classes

|  |  |
|----|----|
| [`MaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance") | The maxcut instance class. |
| [`WeightedMaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance") | The weighted maxcut instance class. |

Inheritance

![Inheritance diagram of iqm.applications.maxcut](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-e2f12b3644d43f25eab99688bda97376224e6fe7.png)
