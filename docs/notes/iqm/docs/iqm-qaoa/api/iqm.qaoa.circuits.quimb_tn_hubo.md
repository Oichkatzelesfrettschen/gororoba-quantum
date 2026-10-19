> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn_hubo.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn_hubo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dc5c935340a9a3b3cf667f5128d052f52215dc3a7323d06d73958a858494450c.

# quimb_tn_hubo

iqm.qaoa.circuits.quimb_tn_hubo(*qaoa*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L459-L495)  
Constructs a [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the quantum circuit.

The object is constructed just like any other quantum circuit by applying quantum gates. [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") transforms those into tensors.

Parameters:  
**qaoa** ([*HUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html#iqm.qaoa.hubo_qaoa.HUBOQAOA "iqm.qaoa.hubo_qaoa.HUBOQAOA")) – A [`HUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html#iqm.qaoa.hubo_qaoa.HUBOQAOA "iqm.qaoa.hubo_qaoa.HUBOQAOA") object whose angles and interaction strengths are used in the construction of the tensor network.

Returns:  
[`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the QAOA circuit (without measurements).

Return type:  
qtn.Circuit
