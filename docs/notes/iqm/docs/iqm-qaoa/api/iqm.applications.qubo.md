> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 abf9b292a60a4f83486e4203cef3edb07978f59c0cb24407e17f4908a2979154.

# qubo

Full path: iqm.applications.qubo

Contains problem instance classes for a generic QUBO problem and a genetic constrained QUBO problem.

While objects of these classes can be instantiated, it’s generally not recommended. For problems with any added structure, it is recommended to use sub-classes (children) of these classes, e.g., [`MaxCutInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance"), [`MISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance") or [`SherringtonKirkpatrick`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html#iqm.applications.sk.SherringtonKirkpatrick "iqm.applications.sk.SherringtonKirkpatrick").

Example

``` python
from iqm.applications.qubo import QUBOInstance
from iqm.applications.qubo import ConstrainedQuadraticInstance

# Defining a QUBO instance from a ``numpy`` array of interactions.
my_qubo_instance = QUBOInstance(my_square_np_array)
my_qubo_instance.fix_variables([0, 2, 4])  # Fixes the variables labelled by 0, 2 and 4 to the value '1'.

# For defining your own custom constrained quadratic binary subclass.
class MyCustomConstrainedInstance(ConstrainedQuadraticInstance):
    def constraints_checker(self):
        # Implementation
```

Classes

|  |  |
|----|----|
| [`ConstrainedQuadraticInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.ConstrainedQuadraticInstance.html#iqm.applications.qubo.ConstrainedQuadraticInstance "iqm.applications.qubo.ConstrainedQuadraticInstance") | A class for constrainted quadratic binary problems. |
| [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") | A problem instance class for generic QUBO problems. |

Inheritance

![Inheritance diagram of iqm.applications.qubo](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-12caacb750c279a3211d3f4b4509af90e45f6092.png)
