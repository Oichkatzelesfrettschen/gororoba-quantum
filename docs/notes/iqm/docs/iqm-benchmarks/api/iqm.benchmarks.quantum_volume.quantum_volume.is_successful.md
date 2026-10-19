> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.is_successful.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.is_successful.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0d545c16959133652d90535ee5cc69ade3761b4bbec5c176124910b2c1642cde.

# iqm.benchmarks.quantum_volume.quantum_volume.is_successful

iqm.benchmarks.quantum_volume.quantum_volume.is_successful(*heavy_output_probabilities: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *num_sigmas: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 2*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Check whether a QV benchmark returned heavy output results over the threshold, therefore being successful.

This condition checks that the average of HOP is above the 2/3 threshold within the number of sigmas given in the configuration.

Parameters:  
- **heavy_output_probabilities** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The HOP of all quantum circuits.

- **num_sigmas** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of sigmas to check

Returns:  
Whether the QV benchmark was successful.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")
