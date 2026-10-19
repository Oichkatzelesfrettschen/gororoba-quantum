> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9e573bf1f979ac1b9763a858478a07c81d7ffcd77db0278ffbc6d2fde6599f85.

# IQMPulseJob

Module: [`iqm.qrisp_iqm.backends.iqm_pulse_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.html#module-iqm.qrisp_iqm.backends.iqm_pulse_job "iqm.qrisp_iqm.backends.iqm_pulse_job")

*class* iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob(*job: T_JobTracker*, *\**, *backend: [iqm.qrisp_iqm.backends.backend.IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend")*)  
Bases: [`IQMJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.IQMJob.html#iqm.qrisp_iqm.backends.iqm_job.IQMJob "iqm.qrisp_iqm.backends.iqm_job.IQMJob")\[`RunJobTracker`\]

Job handle for pulse-level circuit execution.

Returned by `run_async()` when the submitted circuit contains [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instructions. The circuit is compiled locally to a pulse schedule and submitted as a pulse-level job.

Example:

```
>>> from qrisp import QuantumCircuit
>>> from iqm.qrisp_iqm import IQMBackend, IQMPulseOperation, IQMPulseJob
>>> from iqm.qrisp_iqm.custom_pulse_operations import delay_quantum_op
>>> backend = IQMBackend(device_instance="garnet", token="...")
>>> qc = QuantumCircuit(2)
>>> qc.h(0); qc.cx(0, 1)
>>> qc.append(IQMPulseOperation(delay_quantum_op, {"duration": 100e-9}), [qc.qubits[0]])
>>> qc.measure(qc.qubits)
>>> job = backend.run_async(qc, shots=1000)
>>> isinstance(job, IQMPulseJob)
True
>>> result = job.result()  # waits for completion, returns JobResult
```

Attributes

Methods

Parameters:  
- **job** (*T_JobTracker*)

- **backend** (*qrisp_IQMBackend*)

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-cf76b2df393b601cc12401094ab6913664a7af3e.png)
