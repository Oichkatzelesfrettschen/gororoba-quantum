# Folded-QPE timing and service access

The network-enabled CPU preparation exits 0 and produces an admitted plan.
The initial sandbox attempt fails DNS resolution for `iam.cloud.ibm.com`;
Qiskit wraps that failure in `InvalidAccountError`. Successful authenticated
backend and quota reads establish access after the network-enabled retry.

Runtime 0.50 documents `Sampler.run(..., dry_run=True)` as server-side mock
validation. The installed service resolves that request through
`mock_kingston`. The account returns `QiskitBackendNotFoundError` before a job
ID exists. `native-validation.json` records the access failure. Native mock
validation therefore supplies neither measurements nor a server cost estimate.

The fresh Target reports reset duration 2.212 microseconds on all 156 qubits.
Adding one such initialization duration per execution across 131072 PUB-shots
adds 0.289931264 seconds. That separate sensitivity gives nominal
39.922331136 seconds and stress 45.833051136 seconds. The original model predicts
39.632399872 and 45.543119872 seconds. The historical residual overhead can
already contain initialization contributions, so the additive sensitivity
does not claim an independently calibrated charge prediction.

IBM documents approximately two seconds of overhead per internal subjob.
The unknown internal subdivision and scheduler latency limit forecast accuracy.
Each primitive job retains its 60-second QPU-usage ceiling; two jobs reserve
120 seconds plus the 60-second quota reserve. The fresh usage response reports
591 seconds remaining. Actual completed-job metrics determine final charge.

Sources checked for the execution:

- [Sampler native dry-run API](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/executor-sampler-sampler#run)
- [Estimate job run time](https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time)
- [Maximum execution time](https://quantum.cloud.ibm.com/docs/en/guides/max-execution-time)
