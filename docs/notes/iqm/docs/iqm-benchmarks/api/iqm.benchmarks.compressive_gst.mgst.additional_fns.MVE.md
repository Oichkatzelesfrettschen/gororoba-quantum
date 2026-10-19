> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.MVE.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.MVE.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0c41b938b24ab4e0f1094f29571d0f1d390d6cc51d484fb332b0e9f2c09c99d7.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.MVE

iqm.benchmarks.compressive_gst.mgst.additional_fns.MVE(*gates_true: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *gates_estimate: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10000*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Mean varation error between the outputs of two gate sets on random sequences.

Parameters:  
- **gates_true** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Target gates, POVM and initial state

- **gates_estimate** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Current gate, POVM and initial state estimate

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of different gates in the gate set

- **length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Length of the test sequences

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of POVM elements

- **samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of random gate sequences over which the mean variation error is computed

Returns:  
Mean variation error

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

Notes

Sequences are drawn without replacement from initally d\*\*l possibilities. For each sequence the total variation error of the two probability distribution over the POVM elements is computed. Afterwards the meean over these total variation errors is returned.
