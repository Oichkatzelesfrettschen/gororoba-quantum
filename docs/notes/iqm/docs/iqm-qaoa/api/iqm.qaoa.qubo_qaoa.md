> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4204faa18b7fdf65d459553e22ed80444a34ca16d6e102fd62b518f09ea42dd3.

# qubo_qaoa

Full path: iqm.qaoa.qubo_qaoa

A module for the QUBOQAOA class.

The class [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA") mostly serves to store the parameters (angles) of the QAOA circuit and to facilitate various operations on it. The training of the QAOA circuit is done here. For constructing circuits representing the QAOA, use functions from the module [`circuits`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.html#module-iqm.qaoa.circuits "iqm.qaoa.circuits"). For sampling from the QAOA and calculating expectation values, use the backend classes from the module [`backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends").

Classes

|  |  |
|----|----|
| [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA") | The class for QAOA with quadratic unconstrained binary (QUBO) cost function. |

Inheritance

![Inheritance diagram of iqm.qaoa.qubo_qaoa](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-cc7ad7d53cfc53af7e62aeaa0e5889e34875fa87.png)
