> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6023010b88cf13dc1727f0b5559d9c8d7a1274c207f62a2e002ffac256588854.

# IQMCircuitJob

Module: [`iqm.qrisp_iqm.backends.iqm_circuit_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.html#module-iqm.qrisp_iqm.backends.iqm_circuit_job "iqm.qrisp_iqm.backends.iqm_circuit_job")

*class* iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob(*job: T_JobTracker*, *\**, *backend: [iqm.qrisp_iqm.backends.backend.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend")*)  
Bases: [`IQMJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")\[`CircuitJobTracker`\]

Job handle for gate-level circuit execution.

Returned by `run_async()` when the submitted circuit contains no [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instructions.

Example:

```
>>> from qrisp import QuantumCircuit
>>> from iqm.qrisp_iqm import IQMBackend, IQMCircuitJob
>>> backend = IQMBackend(device_instance="garnet", token="...")
>>> qc = QuantumCircuit(2)
>>> qc.h(0); qc.cx(0, 1); qc.measure(qc.qubits)
>>> job = backend.run_async(qc, shots=1000)
>>> isinstance(job, IQMCircuitJob)
True
>>> result = job.result()  # waits for completion, returns JobResult
```

Attributes

Methods

Parameters:  
- **job** (*T_JobTracker*)

- **backend** (*qrisp_IQMBackend*)

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-3bd64d89df2339e20f9dd5242235a63a1cb71459.png)
