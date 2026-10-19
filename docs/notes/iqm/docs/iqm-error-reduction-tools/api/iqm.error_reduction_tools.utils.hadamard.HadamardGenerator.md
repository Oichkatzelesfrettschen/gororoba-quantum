> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.hadamard.HadamardGenerator.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.hadamard.HadamardGenerator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0a75d1833a9827faabf58024d8ee5e50177ecc7b71c28e8a8b8762fb645d35c8.

# iqm.error_reduction_tools.utils.hadamard.HadamardGenerator

*class* iqm.error_reduction_tools.utils.hadamard.HadamardGenerator(*num_qubits*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Hadamard calibration generator.

Methods

|  |  |
|----|----|
| `__iter__`() | Return an iterator over the bit arrays (the class itself is also the iterator). |
| `__next__`() | Next bit array in the iteration. |
| `_generate_array`(index) | Return the bit array corresponding to `index`. |

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
