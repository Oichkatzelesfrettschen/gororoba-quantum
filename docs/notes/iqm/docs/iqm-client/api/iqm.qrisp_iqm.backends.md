> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c220304650c6c4dbd43a434d7d8494f0559e0f42c521e6547dee8328926d8943.

# backends

Full path: iqm.qrisp_iqm.backends

Backend infrastructure for running Qrisp circuits on IQM hardware.

Provides the central `IQMBackend` class (gate- and pulse-level submission), as well as job handles for tracking execution:

- `IQMCircuitJob` — gate-level circuit execution.

- `IQMPulseJob` — pulse-level schedule execution.

Subpackages and modules

|  |  |
|----|----|
| [`backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.backend.html#module-iqm.qrisp_iqm.backends.backend "iqm.qrisp_iqm.backends.backend") | IQM Backend implementation for Qrisp using plasma-sabre transpilation. |
| [`iqm_circuit_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_circuit_job.html#module-iqm.qrisp_iqm.backends.iqm_circuit_job "iqm.qrisp_iqm.backends.iqm_circuit_job") | Job handle for circuit execution. |
| [`iqm_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_job.html#module-iqm.qrisp_iqm.backends.iqm_job "iqm.qrisp_iqm.backends.iqm_job") | Abstract base class for IQM job handles. |
| [`iqm_pulse_job`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.backends.iqm_pulse_job.html#module-iqm.qrisp_iqm.backends.iqm_pulse_job "iqm.qrisp_iqm.backends.iqm_pulse_job") | Job handle for circuit execution as a pulse-level job. |
