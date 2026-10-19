> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c0a63cf00d98ca6eb19f635ba4cae2b5cba6520949ffb3859ed7de6ec4f67ec.

# iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std

iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std(*hops: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Computes the cumulative standard deviation heavy output probabilities of a QV experiment.

Parameters:  
**hops** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The individual heavy output probabilities for each trial.

Returns:  
Cumulative standard deviation heavy output probabilities for all trials.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
