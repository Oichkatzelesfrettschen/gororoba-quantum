> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d8aa0919d4568da6040087da9c396fa08d9d188efa21143b7d794cc0fa42c59b.

# applications

Full path: iqm.applications.applications

Module containing the abstract base class providing a template for defining problem instances.

Example

``` python
from iqm.applications.applications import ProblemInstance

class MyProblemInstance(ProblemInstance):
    @property
    def dim(self):
        # Implementation (mandatory)

    def quality(self):
        # Implementation (mandatory)

    @property
    def best_quality(self)
        # Implementation if there is a more efficient problem-instance-specific way to calculate this.
```

Classes

|  |  |
|----|----|
| [`ProblemInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance "iqm.applications.applications.ProblemInstance") | The abstract base class for defining problem instances. |

Inheritance

![Inheritance diagram of iqm.applications.applications](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-d8c16c849775d0e4417098819d34f50959ca3d7e.png)
