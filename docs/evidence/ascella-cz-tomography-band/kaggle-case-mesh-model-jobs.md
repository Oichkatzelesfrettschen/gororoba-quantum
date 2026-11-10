# Kaggle case: the per-job component model of the Ascella CZ tomography pairs

Written before the push, under the standing approval of Kaggle CPU and GPU sessions inside the 12-hour limit (root
AGENTS.md, "Hardware services").

- **What it computes.** `mesh_model_jobs.py --input mesh-model-jobs-input.json mesh-model-jobs.json`: the chip-level
  component model of the four retained tomography jobs with output weights per job, under the two-photon and the
  g2 pattern laws, over the four hold-outs of `mesh_model.py`. 36 component fits (six fitting sets, two laws,
  three starts) and 816 fits of an overlap and per-job weights at fixed components (per law and hold-out: a
  baseline, a transfer and 100 null draws).
- **Falsifier.** The rule in the script's docstring, fixed before any fit to measured counts: a hold-out survives
  when Gain >= 0.3, Gain over the null median >= 0.3 and the rank p <= 0.05.
- **Why a kernel.** The fits are retained-count analysis, not a simulation of a device; the run needs 2 to 5
  core-hours, which the build host's routing rule sends to Kaggle.
- **Substrate.** Kaggle `NvidiaTeslaT4` machine, private, pushed by `scripts/kaggle_run.py push`. The fits run on
  its 4 CPU cores and leave the GPUs idle: the CPU push of 2026-11-10 was refused ("Maximum batch CPU session
  count of 5 reached", five kernels of other sessions), the GPU pool held a free session, and the owner chose it
  over waiting for a CPU slot, at 1 to 2 h of the weekly GPU quota (28.64 h remaining before the push). The
  image's numpy and torch are recorded in the output's `versions`. Inputs: the bundled extract (the phases, counts and plan reads
  of the retained records, and three seed values), `mesh_model.py` and `gororoba_quantum/parallel.py`.
- **Runtime estimate.** Measured on the build host at one thread: 0.11 s per L-BFGS iteration of a 144-setting
  component fit, 1,443 CPU-seconds for the self-test's 6 component fits and 66 fixed-component fits. Scaled: 2 to
  5 core-hours, 0.5 to 1.3 h on 4 cores, 2 h if every component fit runs its ten rounds on slower cores.
  `--timeout 14400`.
- **Memory.** 0.98 GB peak resident in the self-test with three workers; under 2 GB with four, against 30 GB.
- **Admission of the output.** `mesh_model_jobs.py --check` refits every baseline and transfer on the build host
  from the recorded components and requires each deviance within 1e-5 of the kernel's.
