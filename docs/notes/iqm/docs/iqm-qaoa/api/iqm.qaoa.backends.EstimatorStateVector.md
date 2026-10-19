> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorStateVector.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorStateVector.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e36bc057d7579e2d5cfec45daba7a7da786852dfd7f708f1deb822210a4a23b3.

# EstimatorStateVector

Module: [`iqm.qaoa.backends`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.html#module-iqm.qaoa.backends "iqm.qaoa.backends")

*class* iqm.qaoa.backends.EstimatorStateVector[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/backends.py#L466-L594)  
Bases: [`EstimatorBackend`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.backends.EstimatorBackend.html#iqm.qaoa.backends.EstimatorBackend "iqm.qaoa.backends.EstimatorBackend")

Exact estimator using Qiskit statevector simulation.

Supports both QUBOQAOA and HUBOQAOA with arbitrary number of layers, but scales exponentially with the number of qubits.

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.backends.EstimatorStateVector](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-db138850c4f159e8f493b3da0c8e15543c909792.png)
