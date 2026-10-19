> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f2ab8b982fc3a35447e2fff34962c001c662037707d97c50d582706b495bd38e.

# iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit

iqm.qiskit_iqm.pulse_level_utils.sweep_job_to_qiskit(*job_tracker: RunJobTracker*, *\**, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [Result](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.result.Result "(in Qiskit v2.5)")  
Query the results of a completed pulse-level job and convert it to a Qiskit Result.

Parameters:  
- **job_tracker** (*RunJobTracker*) – Tracker for the completed job.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of shots that was requested. Only used for validating the result.

Returns:  
The equivalent Qiskit Result.

Raises:  
**NotFoundError** – Job has not finished yet.

Return type:  
[*Result*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.result.Result "(in Qiskit v2.5)")
