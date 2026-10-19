> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.relabel_qubits_array_from_zero.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.relabel_qubits_array_from_zero.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 25e78ab2985e8bec40165bcfc916a7df8e81a8418c080f08d40f011d0144534c.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.relabel_qubits_array_from_zero

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.relabel_qubits_array_from_zero(*arr: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *separate_registers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *reversed_arr: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Helper function to relabel an array of qubits to an increasingly ordered one starting from zero.

E.g., \[\[2,3\], \[5\], \[7,8\]\] -\> \[\[0,1\], \[2\], \[3,4\]\]

Note: This assumes the input array is sorted in increasing order!

Parameters:  
- **arr** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – Array of qubits to relabel.

- **separate_registers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the clbits were generated in separate registers. This has the effect of skipping one value in between each sublist, e.g., \[\[2,3\], \[5\], \[7,8\]\] -\> \[\[0,1\], \[3\], \[5,6\]\]. Default is False.

- **reversed_arr** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the input array is reversed. This has the effect of reversing the output array, e.g., \[\[2,3\], \[5,7\], \[8\]\] -\> \[\[0\], \[1,2\], \[3,4\]\]. Default is False.

Returns:  
Relabeled array of qubits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
