# Report: portable least-squares precision sweep (subagent hand-back, written by the orchestrator)

- fp_sweep.py rewritten (with new fp_host.py): per-OS memory cap (systemd scope, RLIMIT_AS with a 2 GiB floor, or none on Windows), thread ladder 1,2,4,... up to min(cpu_count, parallel.workers()), --host-label, --quick, --idle-wait, --timeout, skip rows with reasons, host record per row (CPU flags, numpy SIMD lists, BLAS core, versions, inputs_sha256).
- Build host acceptance: full 74 rows and quick 13 rows, 0 errors; precision scores reproduce sweep.jsonl; digests equal the producer's forecast.json digests.
- Open rulings: RLIMIT_AS floor of 2 GiB (OpenBLAS fails at import under 1 GiB address space); ladder capped at parallel.workers().
- Not run: macOS, native Windows and Linux aarch64 code paths; venv install of the pinned wheels.
- Remote hosts need fp_export.py run locally (qiskit, sympy, rustworkx) for independent input digests; a copied npz proves only the transfer.
