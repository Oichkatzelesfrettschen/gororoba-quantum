> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.readout_error_m3.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.readout_error_m3.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4bed1b1f614d698fd09c6d171a408a3c42a5ad7370eb18696c2ee4ae625bf351.

# iqm.benchmarks.readout_mitigation.readout_error_m3

iqm.benchmarks.readout_mitigation.readout_error_m3(*counts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *mit: [M3IQM](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.M3IQM.html#iqm.benchmarks.readout_mitigation.M3IQM "iqm.benchmarks.readout_mitigation.M3IQM")*, *qubits: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Counts processor using M3IQM for readout error mitigation.

The qubits argument can be either a dictionary coming from mthree.utils.final_measurement_mapping or an array like the initial layout coming from \[backend.qubit_name_to_index(name)\]

returns a dictionary of quasiprobabilties.

NOTE: we could also pass a list of input counts and then this would return a list of quasiprobabilities. This would not work out of the box for us since we need the annotations of either Dict or List (not Union).

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **mit** ([*M3IQM*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.M3IQM.html#iqm.benchmarks.readout_mitigation.M3IQM "iqm.benchmarks.readout_mitigation.M3IQM"))

- **qubits** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
