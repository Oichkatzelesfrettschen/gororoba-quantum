> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7dd78eea241b46c1ff97e3925048f9fba03b273c65d66944e8596d3387c6ec36.

# SherringtonKirkpatrick

Module: [`iqm.applications.sk`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.html#module-iqm.applications.sk "iqm.applications.sk")

*class* iqm.applications.sk.SherringtonKirkpatrick(*interaction_matrix*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/sk.py#L42-L55)  
Bases: [`QUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance")

The problem class for Sherrington Kirkpatrick model.

In this model, all qubits interact with randomly distributed interactions. The model takes an interaction matrix on input. The suggested usage is to generate SK problem instances using [`sk_generator()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.sk_generator.html#iqm.applications.sk.sk_generator "iqm.applications.sk.sk_generator").

Parameters:  
**interaction_matrix** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The matrix of interactions between the spins in the SK model.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.applications.sk.SherringtonKirkpatrick](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-3070c74131aa4282a2c8f9f6dbadcf7e1299c6f3.png)
