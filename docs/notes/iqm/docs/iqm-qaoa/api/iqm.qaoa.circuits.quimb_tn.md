> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 91a8a9cf8deb44c151a4636cca388c360086727e5ec0b824b75b4edecdf0427b.

# quimb_tn

iqm.qaoa.circuits.quimb_tn(*qaoa*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L169-L199)  
Constructs a [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the quantum circuit.

The object is constructed just like any other quantum circuit by applying quantum gates. [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") transforms those into tensors.

Parameters:  
**qaoa** ([*QUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA")) – A [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA") object whose angles and interaction strengths are used in the construction of the tensor network.

Returns:  
[`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the QAOA circuit (without measurements).

Return type:  
qtn.Circuit
