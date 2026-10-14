# IBM Quantum Runtime execution guides

Tag convention: [P] marks documentation statements; [I] marks repository interpretation.

## Pages and retrieval

Retrieved 2026-10-13T18:49:33Z (execution-modes at 2026-10-13T23:27:30Z). The SHA-256 identifies the HTML bytes served at retrieval; the documentation changes without versioned URLs, so a later reading checks the live page against its stated use.

| Page | URL | SHA-256 of retrieved HTML | Cited for |
|---|---|---|---|
| estimate-job-run-time | https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time | `6be62aa6fb10342688cfe124df6097894428a5c84fe4c741208135cdd5f0613a` | [I] Workload usage: billed QPU usage against scheduler circuit timing, job and sub-job overhead, sessions holding the QPU, repetition delay against preparation error. |
| stretch | https://quantum.cloud.ibm.com/docs/en/guides/stretch | `c777d3cb28f63808231d92f25177e0091b486b0e4c70b0130df0dde755539825` | [I] Deferred timing resolution with stretch: relative timing constraints, paired barriers, explicit echo placement, resolved durations and remainders. |
| sampler-options | https://quantum.cloud.ibm.com/docs/en/guides/sampler-options | `e49adeba87cf8d7f5082aea15af5f01e836a9b0591794eeeaf1e4e8538aaf2f5` | [I] Sampler options: per-PUB shot precedence and execution settings. |
| sampler-input-output | https://quantum.cloud.ibm.com/docs/en/guides/sampler-input-output | `e0d943d29632975965e87a0d33cab277f4c57a805c0a60eaa50397bc085a1290` | [I] Sampler inputs and outputs: parameterized workloads, per-PUB shots, result structure. |
| minimize-time | https://quantum.cloud.ibm.com/docs/en/guides/minimize-time | `920e2e2d6356ef1dcee75d4adccd29f57836fa36680d3e668ec8355c3c8c1470` | [I] Minimize job run time: shot allocation, execution limits, mitigation overhead. |
| executor-sampler-sampler | https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/executor-sampler-sampler | `79ebba9527eecbe413914cdd8dd4aea331e08d4f733f3f7cfb18bcb60b183958` | [I] Client-side Sampler API: dry_run=True usage estimates with randomized mock results, and automatic dynamical decoupling unavailable for dynamic circuits. |
| refresh-backend-properties-with-real-time-benchmarking | https://quantum.cloud.ibm.com/docs/en/tutorials/refresh-backend-properties-with-real-time-benchmarking | `99f70c4c4febcd0329d276a482de94af837496677544836f1a182a731c583fbb` | [I] Reported properties against contemporaneous measurement: drift on timescales shorter than daily calibration, transient two-level-system defects, and differences that reflect measurement methodology rather than drift. Retrieved 2026-10-13. |
| qiskit-runtime-circuit-timing | https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-circuit-timing | `dff635a3dbbf53f3ae49153dde44eb41bda030619e7cbb0c761190a5e19d9a82` | [I] Returned scheduler timing: the experimental scheduler_timing flag, the raw timing table per channel, and circuit time that differs from billed QPU time. Retrieved 2026-10-13. |
| execution-modes | https://quantum.cloud.ibm.com/docs/en/guides/execution-modes | `c074a1e488274bd98170784bc8d5501afd14d0ec50d222a3e789979292b7f142` | [P] Batched jobs are not guaranteed to run in submission order, and QPU calibration jobs can run between batched jobs; session mode excludes calibration jobs during its window. |

## Reading scope

[I] Each page is cited for the use in its row, as summarized in the staged patch-window plan's source review; this note records retrieval identity and does not certify a full reading of each page.

## Mapping to this repository

- [I] live_run.py sends dynamic circuits with twirling and automatic dynamical decoupling off; explicit echo sequences replace them in the window arms.
- [I] The staged plan keeps per-PUB shots (40 x 1,024 plus 6 x 4,096), a fixed repetition delay, separate jobs rather than a session, and a native dry run that excludes mock outcomes from analysis.
- [I] Charge estimates remain predictions; the collected job metrics carry the billed seconds.
- [I] The execution-modes guide is why the patch-window record checks each job's start-time calibration stamp rather than assuming one calibration across jobs submitted together.
