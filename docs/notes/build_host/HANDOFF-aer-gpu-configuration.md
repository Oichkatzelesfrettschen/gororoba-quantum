# Handoff: Aer GPU configuration (branch sim/aer-gpu-configuration)

Branch base 2df388e; the branch is unpushed and not yet merged with
origin/main (5b756e1 at the last fetch).

## Done and verified

- `calibration_snapshot.noise_simulator`: on a GPU, `batched_shots_gpu` is on
  by default up to `BATCHED_SHOTS_MAX_QUBITS = 10` (`batched_shots=False`
  opts out); `SnapshotSimulator.run` turns batching off for any circuit with
  control flow; shot branching is never enabled. The CPU path is Aer's
  default.
- CPU count-comparing gates on the branch, `GOROROBA_AER_DEVICE=CPU`:
  core-279, core-288, core-287, core-311, core-313, core-304 and core-273
  each printed `PASS`.
- core-366 (`ruff check scripts/aer_gpu_probe.py && ruff format --check
  scripts/aer_gpu_probe.py && MYPYPATH=gororoba_quantum mypy
  scripts/aer_gpu_probe.py`): `All checks passed!`, `1 file already
  formatted`, `Success: no issues found in 1 source file` (2.5 s).
- core-367 (`--check docs/evidence/aer_gpu_configuration/result.json`,
  normal and `-O`): `53 timed rows and 11 readout-toy rows reproduce their
  derived values; readout law kept by cpu_density_matrix, cpu_statevector,
  gpu_density_matrix_unbatched, gpu_statevector_default,
  gpu_statevector_unbatched; the CPU default keeps it on replay; lowered
  counts equal the if_else counts; ...` (about 11 s per mode; 22.6 s in
  gates.json is an estimate from those two runs).
- `python3 ci/check_run_gates.py`: `run_gates: unique gate names, ...`.
- `python3 ci/check_agents_sections.py`: `identical sections: ...`.
- Evidence and mechanism: docs/evidence/aer_gpu_configuration/README.md.

## Unfinished, with the next command

1. Merge main: `git -C ~/worktrees/IBMQuantum/sim/aer-gpu-configuration merge
   origin/main`, then rerun core-366, core-367, `python3 ci/check_run_gates.py`
   and `python3 ci/check_agents_sections.py`.
2. `python3 -W error docs/verify_sources.py` (not run).
3. Docs not yet updated: docs/notes/kaggle/substrates.md ("Small dynamic
   circuits" section and a configuration table from the evidence README),
   the root AGENTS.md "Simulation on Kaggle" bullet "Batched GPU shots"
   (now: default on up to 10 qubits for circuits without control flow;
   feed-forward unbatched; shot branching excluded), and
   kaggle_kernel/AGENTS.md "Aer on the GPU". Kaggle quota: the
   docs/notes/kaggle/site capture names P100, T4 x2 and TPU v3-8, a 30 h
   weekly GPU quota and 20 h weekly TPU, gives no per-tier charge rate and
   does not mention L4, so the cheapest tier per GPU-hour is not stated by
   the capture.
4. The ten-round batched row stopped after 32 shots (342 ms per shot, fixed
   cost host-CPU bound); it is moot for the default since feed-forward runs
   unbatched.
5. T4 rerun (orchestrator):
   `"$PYTHON" scripts/kaggle_run.py push scripts/aer_gpu_probe.py --slug
   gororoba-aer-gpu-config --machine NvidiaTeslaT4 --timeout 5400 --include
   docs/evidence/calibration/history/ibm_fez/20261016T1212520700.json
   --include docs/evidence/calibration/ibm_kingston.json -- --out
   results/kaggle_out/aer_gpu_probe.json`
6. Split into the requested three commits (probe and evidence, configuration,
   docs) if the reviewer wants that shape; the branch now carries one commit
   for code and evidence plus this handoff.

## Outside the worktree

Scratch files only, under the session scratchpad
(/tmp/claude-1000/.../scratchpad: explore.py, one.py, cond.py, toy.py,
host_run.json). Nothing else on the host changed.
