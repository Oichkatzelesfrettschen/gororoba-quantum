# Common rules for the fiber tooling build

- Worktree: ~/worktrees/IBMQuantum/a5-kernel-attachments (branch geometry/a5-kernel-attachments). New code goes in
  docs/evidence/a5-kernel-attachments/ beside the producers. A read-only Codex review session has that directory as
  its cwd; it writes nothing. Do not commit or push; the orchestrator reviews and commits.
- Read AGENTS.md (root), ci/AGENTS.md, docs/runbooks/compute-flags.md, and the tree's existing producers
  (nullity16_rees_fibers.py, nakayama_rees_fibers.py, nullity16_basepoints.py) for conventions: `_require` instead of
  assert, `$PYTHON` (export PYTHON=~/.cache/gororoba-quantum/ci-py3.14.7-qiskit261/bin/python3), parallel.py for pools
  over independent items, ruff format/check and mypy through ci/pinned_tool.py, no absolute home paths in any written
  record (repo-relative only), seeds only from QRNG draws via qrng_seeds (see AGENTS.md "Seeds").
- Mathematical target and methods: read docs/local/a5-failed-runs/purpose.md and decision-record.md (sections 1-8);
  method A template docs/local/a5-failed-runs/templates/a2_body.sing and runs/s1/input.sing (degree 3); method B
  templates/b_body.sing; helpers probes/rank_nf.py, probes/relations_nf.py; reviews review-claude.md,
  review-codex.md, picture-codex.md.
- Host memory is shared with long jobs: run every Singular call under
  `systemd-run --user --scope -p MemoryMax=3G -p MemorySwapMax=0 timeout ...`, one job at a time, nothing over 3G and
  15 minutes during this build. Write long output to log files under docs/local/a5-failed-runs/build/logs/.
- Tool versions on this host (latest packaged): Singular 4.4.1, FLINT 3.6.0, python-flint 0.9.0, Macaulay2
  1.26.06; record them in every receipt.
- Report to docs/local/a5-failed-runs/build/<your-part>-report.md: files, commands, validation results with log
  paths, open limits.
