# Brief: Kaggle TPU-VM use for the A_5 fiber program, decomposed

Read only; return findings as your final message. Cite file:line.

Facts gathered (verify each against its file):
- Quota (Kaggle MCP get_accelerator_quota, read 2026-10-29 ~15:10 UTC): TPU 7,390 s used of 72,000 s per week, GPU
  11,920 s of 108,000 s; refresh 2026-10-31T00:00Z.
- TPU limits and shapes: docs/notes/kaggle/README.md lines 31-40, docs/notes/kaggle/tpu-research.md (96 cores, 330 GB
  TPU VM; 9 h per TPU session; one batch TPU session at a time; queue waits of hours), docs/notes/kaggle/substrates.md.
- Cancelled kernel `a5-e8vb-msolve-tpu`: source and metadata `kaggle-tpu/src/` (TpuV5E8, pinned TPU-VM image,
  passagemath-msolve 10.8.13, `-t os.cpu_count()`, SOLVER_SECONDS 31500), outputs `kaggle-tpu/out/` (`msolve.log`
  reaches degree 17 with an 86,010,243 x 87,648,606 matrix at degree 16; `samples.tsv` RSS up to ~51 GB with
  ~340 GB available; ended CANCEL_ACKNOWLEDGED at 15:03 UTC after ~7,380 s). No session on this machine issued a
  cancel (transcript and shell-history search). The input `kaggle-tpu/out/input.ms` is the E8-bar->VB Rees graph.
- Program context: `purpose.md`, `decision-record.md` (sections 2, 6-9: msolve deprioritized, method A/B results,
  host memory incident, tooling build), `review-claude.md`, `review-codex.md`, `picture-codex.md`.
- A TPU-VM smoke test is queued (`kaggle-tpu/test/src/`): installs passagemath-singular 10.8.13 and runs E8-bar->VB
  method A degrees 2-3 and X- degree 2 in parallel threads (expected h: VB 10, 34, 80; X- 15, 51).

Answer:
1. Why was the msolve kernel cancelled at ~2 h, given a 31,500 s solver timeout and 340 GB free? Weigh: Kaggle-side
   TPU preemption or policy, a push-time timeout, an idle/output-size rule, quota accounting; say which evidence
   would decide it, and how to make the next run robust (checkpointing, smaller batches, output size).
2. Was the job too complex for one run? From msolve.log, estimate whether degree 17+ could finish in 9 h at the
   observed growth, and whether msolve is the right use of a 96-core VM at all versus many parallel Singular jobs.
3. TPU requirements, documented: what a TPU-VM kernel must declare (machine_shape, enable_tpu, image pinning,
   internet for pip), the queue behavior, session cap, weekly cap, and what our CPU-only algebra gains (cores, RAM)
   and loses (queue latency, single batch session). Note any doc in docs/notes/kaggle that needs an update.
4. Which remaining fiber jobs belong on the TPU VM: rank by value per TPU-hour, considering ~18 h weekly left, 9 h
   per session, one session at a time: e.g. a batch of method-B saturations (X-, Iso, E8-bar N+/N-, W8) in parallel,
   method A degree 3/4 runs, second-prime replays once Part A of the tooling build lands.
5. Design the next test after the smoke test: exact job list, per-job memory and time caps (cgroups are absent on
   Kaggle; use timeout and RSS watch), checkpoint outputs, and the falsifier for "the TPU VM is the right substrate".
