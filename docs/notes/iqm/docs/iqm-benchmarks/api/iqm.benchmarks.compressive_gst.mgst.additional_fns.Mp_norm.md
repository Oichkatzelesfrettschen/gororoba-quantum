> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.Mp_norm.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.Mp_norm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c1f5b11cc7f758aa59ded8d1eff3ed13e90895fc7099c8d6b5d9bd910114e5e7.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.Mp_norm

iqm.benchmarks.compressive_gst.mgst.additional_fns.Mp_norm(*gates_true: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *gates_estimate: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *p: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10000*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Mean of the p-norm deviation between the outputs of two gate sets on random sequences.

Parameters:  
- **gates_true** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Target gates, POVM and initial state

- **gates_estimate** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Current gate, POVM and initial state estimate

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of different gates in the gate set

- **length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Length of the test sequences

- **p** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Defines the l_p - norm that is used to compare probability distributions

- **samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of random gate sequences over which the mean variation error is computed

Returns:  
Mean l_p - norm error

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

Notes

Sequences are drawn without replacement from initally d\*\*l possibilities. For each sequence the l_p - norm error of the two probability distribution over the POVM elements is computed. Afterward the meean over these total variation errors is returned.
