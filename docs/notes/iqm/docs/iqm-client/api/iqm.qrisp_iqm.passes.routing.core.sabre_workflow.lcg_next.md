> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 10a15dee50f465eb77b5d36336424d76c92919d11e0ea74e15d18f4ab09679ef.

# iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next

iqm.qrisp_iqm.passes.routing.core.sabre_workflow.lcg_next(*seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Linear Congruential Generator for stochastic swap selection.

Returns a value in \[0, 65536\] with approximately uniform distribution. Used with threshold comparison: skip candidate when `seed < 65537 / greediness`.

The parameters a=75, c=74, m=65537 are chosen for good distribution properties; m=65537 is a prime modulus (2^16 + 1) ensuring full period.

Parameters:  
**seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Current RNG seed value.

Returns:  
Next value in the LCG sequence.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
