# Brief: portable least-squares precision sweep across hosts

Read first: `<workspace>/gororoba-infrastructure/workspace/AGENTS.md`, then
`AGENTS.md` and `scripts/AGENTS.md` in this worktree, then `docs/evidence/least-squares-precision/README.md`
and `fp_sweep.py`, `fp_backends.py`, `fp_export.py` beside it.

Work only in this worktree (`<worktree>`, branch
`least-squares-precision/portable-sweep`). Spawn no subagents. Commit nothing, push nothing; leave the diff for review.
Submit no provider job. Write your report to `docs/local/report-portable-sweep.md` in this worktree.

## Goal

`fp_sweep.py` times every least-squares backend on one host (the build host, Zen 3, under load 2 to 22). Make it run
unchanged on every host below and record enough per row to compare hosts:

- Memory cap per OS: `systemd-run --user --scope -p MemoryMax=... -p MemorySwapMax=0` where a user systemd manager
  answers (probe it, WSL may lack one); otherwise a `resource.setrlimit(RLIMIT_AS)` child on Linux and macOS, and a
  documented uncapped run on native Windows. The cap scales with host memory (`min(8G, 0.6 x MemTotal)`).
- Thread counts taken from the host's CPU count (1, 2, 4, ..., up to `os.cpu_count()`), never above it.
- Configurations that need hardware the host lacks are skipped with a recorded reason: the x87 rows on non-x86 or
  where `numpy.longdouble` is not 80-bit (`numpy.finfo(numpy.longdouble).nmant != 63`); quaddtype rows where the
  wheel is absent.
- Each row also records: hostname-free host label passed by `--host-label`, `platform.machine()`, OS, CPU model, the
  CPU flag subset {avx2, avx512f, avx512dq, avx512vl, fma, neon/asimd, sse3}, numpy version and
  `numpy.show_config()` SIMD baseline/dispatch lists, OpenBLAS core (`threadpoolctl` if installed), python-flint
  version, the five `arithmetic.inputs_sha256` digests the ensemble producer records (see README "Finding"), and
  load average before each run (Windows: record null).
- An `--idle-wait` option polls the 1-minute load average and starts only when it is below 0.5 x CPU count.
- A `--quick` subset (one thread count per backend family, one repeat) for 1 GiB hosts.

Keep the existing `sweep.jsonl` rows readable: new fields are additions. Keep `python3` literals out of docs and
scripts (`$PYTHON`). ruff, black, isort, flake8 and mypy clean on the touched files; no `assert` outside tests.

## Acceptance

Run the full sweep on the build host here under `--idle-wait` (it shares CPUs with other sessions; record the load) and
`--quick` once, both writing to `docs/evidence/least-squares-precision/hosts/build-host-*.jsonl`. Report the exact
commands, tool versions, any configuration that failed and why, and the command line each remote host needs
(Linux x86, Linux aarch64, macOS arm64, Windows native) including the pip packages to install into a venv.
