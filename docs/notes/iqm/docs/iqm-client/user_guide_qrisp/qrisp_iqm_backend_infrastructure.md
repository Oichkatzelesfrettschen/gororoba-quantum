> Full piece: [https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/qrisp_iqm_backend_infrastructure.html](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/qrisp_iqm_backend_infrastructure.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ef56adbdc374023a0e86671e72ae82ac0b870d05d2c140558081067b27b659a6.

# Backend infrastructure

The central entry point for running Qrisp circuits on IQM hardware. [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.IQMBackend.html#iqm.qrisp_iqm.backends.backend.IQMBackend "iqm.qrisp_iqm.backends.backend.IQMBackend") manages authentication, job submission, and result retrieval. Before submission, circuits are transpiled through a `PassManager` that you control: accept the pre-configured default pipeline, customize it with your own passes, or pass a fully hand-tuned pipeline via the `pass_manager` argument. The backend automatically routes circuits to either gate-level or pulse-level execution depending on whether the circuits contain [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instructions.

Various Job classes are used to track execution progress and retrieve results:

- [`IQMCircuitJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob.html#iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob "iqm.qrisp_iqm.backends.iqm_circuit_job.IQMCircuitJob") — gate-level circuit submissions.

- [`IQMPulseJob`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob.html#iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob "iqm.qrisp_iqm.backends.iqm_pulse_job.IQMPulseJob") — pulse-level playlist submissions.

|  |  |
|----|----|
| `IQMBackend` | Qrisp backend for executing circuits on IQM quantum hardware. |
| `IQMCircuitJob` | Job handle for gate-level circuit execution. |
| `IQMPulseJob` | Job handle for pulse-level circuit execution. |
