> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.process_backend.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.process_backend.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 88b70014984fa319c19f30989bd1bed9c5d765323d5a17a033dc31bec99fa4a0.

# iqm.benchmarks.utils.process_backend

iqm.benchmarks.utils.process_backend(*backend: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]  
Process the backend input to ensure it is an IQMBackendBase instance and extract the station name.

Parameters:  
**backend** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to process, either as a string name or an IQMBackendBase

Returns:  
A tuple containing the processed backend and the station name.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
