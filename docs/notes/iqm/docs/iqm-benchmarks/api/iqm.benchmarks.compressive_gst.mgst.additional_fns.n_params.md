> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.n_params.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.n_params.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 af44ebd8c547aff301bf3726de15fb2add48f419cb4eb11ff891d025b71915a0.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.n_params

iqm.benchmarks.compressive_gst.mgst.additional_fns.n_params(*pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Returns the number of free parameters in a gate set.

Unitary gauge parameters and unitary freedom in representing the Kraus operators and the POVM elements are subtracted. For details, see [https://docserv.uni-duesseldorf.de/servlets/DerivateServlet/Derivate-71735/dissertation_brieger-2%281%29.pdf](https://docserv.uni-duesseldorf.de/servlets/DerivateServlet/Derivate-71735/dissertation_brieger-2%281%29.pdf)

Parameters:  
- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The physical dimension, i.e. 2^(#qubits)

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of gates in the gate set

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The Kraus rank of the gates

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of POVM elements; For computational basis measurements n_povm = pdim

Returns:  
The number of free parameters.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
