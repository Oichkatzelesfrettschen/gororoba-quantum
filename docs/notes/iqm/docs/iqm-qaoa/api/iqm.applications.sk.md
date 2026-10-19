> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 556b955cbe5cc9d712cb8e4b9c5caab64842daf461e69a5f7011335e803df6cc.

# sk

Full path: iqm.applications.sk

Module containing the SK model problem instance class.

Example

``` python
from iqm.applications.sk import sk_iterator

for my_instance in sk_generator(n, n_instances):  # Generates problem instances.
    my_instance.quality("111111111")
```

Functions

|  |  |
|----|----|
| [`sk_generator`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.sk_generator.html#iqm.applications.sk.sk_generator "iqm.applications.sk.sk_generator")(n, n_instances\[, distribution, ...\]) | The generator function for generating random SK model problem instances. |

Classes

|  |  |
|----|----|
| [`SherringtonKirkpatrick`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html#iqm.applications.sk.SherringtonKirkpatrick "iqm.applications.sk.SherringtonKirkpatrick") | The problem class for Sherrington Kirkpatrick model. |

Inheritance

![Inheritance diagram of iqm.applications.sk](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-8834c94b2591fc6bb50efefa3ca84e11d1771ad0.png)
