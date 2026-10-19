> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d135351bc54802a01e5062449a3149056e9f72488f452acfa5e9f5da7b2f5fc6.

# iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences

iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *num_circuits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Estimates the GHZ state fidelity based on the multiple quantum coherences method based on \[Mooney, 2021\].

Parameters:  
- **dataset** (*Dataset*) – An xarray dataset containing the measurement data

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol

- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of circuits executed for the given qubit layout to estimate the fidelity

Returns:  
The ghz fidelity or, if rem=True, fidelity and readout error mitigated fidelity

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]
