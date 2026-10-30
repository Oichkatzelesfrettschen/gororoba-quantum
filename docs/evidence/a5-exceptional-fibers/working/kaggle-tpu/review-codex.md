The cancellation cause remains unresolved. The retained evidence also corrects two central assumptions: **sampled RSS reached 209 GB, and msolve requested 224 threads**. The TPU VM merits a bounded parallel Singular test; another unrestricted msolve graph elimination has weak expected value.

The findings concern retained launchers, logs, metadata and documentation. Reported provider status and quota readings remain historical observations.

**1. Cancellation: the evidence does not identify the initiator or policy.**

The launcher sets a **31,500-second solver timeout**. Its normal cleanup writes `result.json`, but the downloaded artifacts omit that receipt. A cutoff around 7,380 seconds therefore requires an explanation outside the configured solver deadline. [Launcher:52,84,99–120](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/src/a5-e8vb-msolve-tpu.py:52), [download inventory:1–17](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/download.log:1).

The memory narrative needs correction. At elapsed 7,166 seconds, the sampler records **203,942,860 KiB RSS: 208.84 GB, or 194.50 GiB**, alongside 190.45 GB available. The final sample records 46.80 GB RSS and 352.83 GB available. The brief combines a later low-memory observation with an incorrect peak. Thirty-second sampling still leaves transient spikes and unmeasured container limits unresolved. [Samples:239,246](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/out/samples.tsv:239), [sampling mechanism:89–95](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/src/a5-e8vb-msolve-tpu.py:89).

| Explanation | Assessment | Evidence that would decide it |
|---|---|---|
| Push-time timeout | Plausible; independent of `SOLVER_SECONDS` | Original save/push request and its `session_timeout_seconds`, bound to the exact version/session |
| Kaggle preemption or policy | Plausible; attribution remains open | Provider terminal reason and cancellation event identifying actor or policy |
| Interactive idle rule | Weak explanation for a batch script | Evidence that the session was interactive, or a documented batch-idle termination event |
| Output-size limit | Weak: retrieved artifacts total about 19.5 KB; `gb.out` is empty | Provider output-limit event or evidence of substantial omitted output |
| Weekly quota exhaustion | Weak against the reported 7,390/72,000-second reading | Raw before/after quota responses, including reservations and other sessions |
| OOM | Endpoint samples provide little support; spikes remain possible | Container/kernel OOM event or provider resource-limit reason |

Saved-version timeouts belong to the push request, rather than pulled metadata. Kaggle documents the 20-minute idle rule for interactive sessions. [Interfaces:55–66](~/Projects/IBMQuantum/docs/notes/kaggle/interfaces.md:55), [captured notebook documentation:448–454](~/Projects/IBMQuantum/docs/notes/kaggle/site/notebooks.md:448).

`CANCEL_ACKNOWLEDGED`, 15:03 UTC and the local cancellation-search result appear in the decision record. The referenced watcher receipt was absent from the reviewed evidence. Even a complete local search would leave another client or actor possible; “the cancel came from Kaggle’s side” overstates the inference. [Decision record:221–226](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:221).

The next authorized run should retain its push request, session identity, timeout, quota reading and hardware inventory **before computation**. Independent tasks should write completed receipts immediately. Stage files improve recoverability, but the current msolve wrapper exports neither its live basis nor pending-pair frontier.

**2. Complexity: degree 17–18 looks plausible within nine hours; full completion remains unbounded.**

The retained input matches the source’s embedded input byte-for-byte and describes the **19-variable E8-bar→VB Rees graph**. The solver uses exact linear-algebra option 2 and requests 224 threads through `os.cpu_count()`. Those observations establish exposed logical CPUs, rather than physical-core count or effective utilization. [Input:1–2](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/out/input.ms:1), [solver configuration:4–16](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/out/msolve.log:4), [launcher:80–82](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/src/a5-e8vb-msolve-tpu.py:80).

| Completed F4 degree | Round wall time |
|---|---:|
| 13 | 586.70 s |
| 14 | 956.54 s |
| 15 | 1,826.23 s |
| 16 | 2,983.58 s |

Degree 16 constructs the **86,010,243 × 87,648,606 sparse matrix**. Degree 17 begins, but its matrix and completed duration remain unrecorded. The rounded `0.00%` density cannot support a dense-memory estimate. [F4 log:106–110](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/out/msolve.log:106).

Completed rounds total **7,325 seconds**. Extrapolating the final 1.63× round-growth factor gives cumulative times of approximately **3.39 hours through degree 17, 5.60 hours through degree 18, and 9.22 hours through degree 19**, before installation and final reduction/export. Applying the observed 1.91× factor instead puts degree 19 around 12.4 hours. These are sensitivity calculations; the logs supply no terminating-degree bound.

Reported CPU time divided by wall time averages about **23 effective cores**, rising to about 31 in degree 16. Requesting 224 threads therefore did not establish corresponding utilization.

The run demonstrated substantial large-memory progress. It produced an empty basis output and an unfinished elimination. Method A already computes useful graded pieces cheaply, while method B targets full completion through pivot saturation. The decision record correctly deprioritizes msolve. [Decision record:20–26](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:20). Parallel Singular jobs offer more independent opportunities for useful results; their comparative completion rate still requires measurement.

**3. TPU requirements and documentation corrections.**

A TPU-VM batch should declare `machine_shape: "TpuV5E8"`. The smoke metadata also sets `enable_tpu: true`, `enable_gpu: false` and `enable_internet: true`; internet supports its online pip installation. The accelerator booleans are deprecated compatibility fields—the documented selector is `machine_shape`. [Smoke metadata:8–14](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/test/src/kernel-metadata.json:8), [interface fields:103–111](~/Projects/IBMQuantum/docs/notes/kaggle/interfaces.md:103).

**Image pinning requires care.** The documented recipe removes stale CPU/GPU `docker_image` and notebook `dockerImageVersionId` fields, optionally requesting `docker_image_pinning_type: "latest"`. The failed run’s pulled metadata contains a TPU-specific image digest, but pulled metadata does not establish what the original push explicitly pinned. Preserve the resolved image identity; establish explicit digest reuse with a successful allocation check before making it the recipe. [Image procedure:264–273](~/Projects/IBMQuantum/docs/notes/kaggle/tpu-research.md:264), [pulled metadata:17–18](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/src/kernel-metadata.json:17).

Documented limits are **nine hours per TPU session, 20 TPU hours weekly, 20 GB saved working output, and one active or queued TPU batch session**. A retained queue observation exceeded seven hours while used/reserved quota remained zero; that queued session still occupied the batch slot. [Limits:31–43](~/Projects/IBMQuantum/docs/notes/kaggle/README.md:31), [queue accounting:170–176](~/Projects/IBMQuantum/docs/notes/kaggle/tpu-research.md:170).

The nominal **96 cores/330 GB** comes from captured documentation. This run exposed 224 logical CPUs and initially reported about **400.6 GB available memory**. Record CPU topology, affinity, `MemTotal` and applicable limits at startup; neither nominal specifications nor host-wide availability establishes a guaranteed process allocation. [Documented specifications:438–442](~/Projects/IBMQuantum/docs/notes/kaggle/site/notebooks.md:438), [initial sample:2](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/out/samples.tsv:2).

CPU algebra gains RAM and independent-process capacity. TPU-device acceleration remains unmeasured. Queue latency, accelerator wall-time consumption and the single batch slot are the costs.

Maintained guides needing updates are:

- [substrates.md:36,54](~/Projects/IBMQuantum/docs/notes/kaggle/substrates.md:36): replace the present-tense “unreachable” account conclusion.
- [tpu-research.md:18,190](~/Projects/IBMQuantum/docs/notes/kaggle/tpu-research.md:18): distinguish historical CPU fallbacks, the observed large-host allocation and unresolved TPU-device execution; qualify image generalizations.
- [workflow.md:131,241](~/Projects/IBMQuantum/docs/notes/kaggle/workflow.md:131): revise historical account/routing conclusions and generic session limits.
- [interfaces.md:65,76](~/Projects/IBMQuantum/docs/notes/kaggle/interfaces.md:65): add the nine-hour TPU exception and revise “editor … the only route.”
- [README.md:31–43](~/Projects/IBMQuantum/docs/notes/kaggle/README.md:31): distinguish documented specifications from measured allocation and link concurrency constraints.

Preserve captured upstream `site/` and `cli/` records.

**4. Rank remaining jobs by evidence value per TPU-hour.**

Method A certifies individual graded pieces. Method B can supply the complete fiber ideal. Each arrow denotes an orbit closure and its boundary orbit at the recorded point.

| Priority | Work | Reason |
|---|---|---|
| 1 | Parallel method-B completion attempts for **X− and Iso**, with **E8-bar→VB** as a small completion/control task | Full certificates address the main gap; X completion also serves its verified sign partner |
| 2 | Producer-regenerated second-prime replays of completed receipts, once input tooling is verified | Strong reproducibility value when bundled into an existing session |
| 3 | **E8-bar→N− degree two and method B**, alongside **E8-bar→N+ method B** | N− lacks completed counts; the tested sign shortcut failed |
| 4 | **W8→N− method B** | Large-memory candidate; verified symmetry serves N+ too |
| 5 | Targeted **X− degree four**, then E8-bar degree three | Useful finite-degree questions, including survival of embedded structure |
| 6 | W8 degree three and broad degree-four extensions | Expensive finite segments; completion value remains limited |

The adopted ordering prioritizes VB/X/Iso completion and defers expensive cubic extensions. X’s quadratic scheme is nonreduced; VB’s is reducible. Those facts make scheme-completion checks substantive. [Decision record:168–204](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:168).

Second-prime runs must regenerate coefficients from the Gaussian-rational producer. Replacing `32009` in specialized inputs changes the problem. Matching several degrees or primes still leaves characteristic-zero completeness unresolved. [Decision record:174–178](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:174).

The reported quota leaves **64,610 seconds: 17 h 56 min 50 s**, before smoke consumption, reservations and other sessions. That arithmetic is verified; current quota remains unverified.

**5. Next test: a four-hour parallel completion pilot with recoverable receipts.**

First repair the smoke acceptance check. The wrapper records exit codes and `RESULT` strings but never computes the exact ranks required to verify **VB 10,34,80 and X− 15,51**. It also buffers logs until subprocess completion and writes the aggregate receipt after all workers finish. Successful execution alone therefore fails to establish mathematical conformance. [Smoke runner:19–26](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/test/src/a5-fiber-tpu-smoke.py:19).

Use a **14,400-second outer session ceiling**, matching the repository launcher’s four-hour accelerator policy. The service’s nine-hour allowance does not override that policy. [Runner:192,669–671](~/Projects/IBMQuantum/scripts/kaggle_run.py:192).

After numeric smoke validation, the proposed job list is:

| Job | Proposed RSS threshold | Solver deadline |
|---|---:|---:|
| E8-bar→VB, method B | 8 GiB | 3,600 s |
| X−→N−, method B | 16 GiB | 12,600 s |
| Iso, method B | 24 GiB | 12,600 s |
| E8-bar→N+, method B | 48 GiB | 12,600 s |
| E8-bar→N−, method B | 48 GiB | 12,600 s |
| W8→N−, method B | 64 GiB | 12,600 s |
| E8-bar→N−, method A degree two | 24 GiB | 10,800 s |

These are **experimental budgets, rather than completion predictions**. Reconcile completed and active work before submission; remove already-settled tasks instead of duplicating another worker’s acquisition.

The simultaneous thresholds total **232 GiB**. Require at least **296 GiB available at admission**, preserving 64 GiB headroom. Use one thread per Singular process, one-second process-tree RSS sampling, a 256-GiB aggregate threshold and a 64-GiB available-memory floor. Threshold breaches should terminate the responsible process group with TERM, then KILL after ten seconds, recording the reason. RSS polling remains sampled protection; Linux `RLIMIT_RSS` supplies no hard enforcement. [Resource-limit guidance:51–65](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:51).

Bound installation to 600 seconds, solver work to 12,600 seconds and finalization to 600 seconds, leaving 600 seconds below the outer deadline. Verify flags against the installed binaries and retain that review. [Flag checklist:179–196](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:179).

Checkpoint outputs should include:

- Startup identity, versions, input hashes, prime/root, generator order, limits and launch request.
- Streaming per-job logs and RSS samples; immediate termination/completion receipts.
- Method-A ordered monomials, products, normal forms, exact ranks and relation witnesses after each completed stage.
- Method-B Rees ideal immediately after saturation, then the fiber ideal and Hilbert data.
- Compressed diagnostics, output byte counts and checksums, with a proposed **10-GB soft output ceiling**.

An interrupted saturation retains diagnostic progress; its completion remains open. Test partial-output retrieval before treating files inside the VM as durable checkpoints. The existing method-B template first writes its Rees ideal after saturation returns. [Template:13–20](~/Projects/IBMQuantum/docs/local/a5-failed-runs/templates/b_body.sing:13).

**Falsifier:** reject another unchanged TPU batch if controls disagree, resource containment or retrieval fails, or the pilot yields only timeouts and previously known small results. Continued allocation should require a new certified result plus measured throughput advantage over the admitted host workload, or a useful computation whose measured working set exceeds that host budget. Include queue and setup latency in the comparison.

The strongest supported conclusion is that Kaggle supplied a substantially larger CPU-memory execution surface. The next test should establish whether that surface produces more certified fiber evidence per constrained session.