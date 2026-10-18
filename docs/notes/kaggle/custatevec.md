# cuStateVec on the Kaggle GPU kernel

`calibration_snapshot.noise_simulator(..., custatevec=True)` sets Aer's
`cuStateVec_enable`, which routes a GPU statevector run's gate application
and sampling through libcustatevec. On a Kaggle T4 the library comes from
pip wheels; the host build is in `docs/notes/build_host/custatevec.md`.

## Library chain

PyPI metadata (`https://pypi.org/pypi/NAME/VERSION/json`):

| Wheel | Version | Requires-Dist | Supplies |
| --- | --- | --- | --- |
| qiskit-aer-gpu-cu11 | 0.17.2 (cp313 manylinux2014, sha256 2684a4bf8dc7...f2892) | nvidia-cuda-runtime-cu11>=11.8.89, nvidia-cublas-cu11>=11.11.3.6, nvidia-cusolver-cu11>=11.4.1.48, nvidia-cusparse-cu11>=11.7.5.86, cuquantum-cu11>=23.3.0,<24.11.0 | `qiskit_aer`, whose controller_wrappers module lists libcustatevec.so.1 and libcutensornet.so.2 as NEEDED with RPATH `$ORIGIN/../../cuquantum/lib`; cubins for sm_70 through sm_87, which include the T4's sm_75 |
| cuquantum-cu11 | 24.8.0, the newest release inside Aer's range | custatevec-cu11==1.6.0.post1, cutensornet-cu11==2.5.0 | a metapackage |
| custatevec-cu11 | 1.6.0.post1 | none | `site-packages/cuquantum/lib/libcustatevec.so.1`, the directory the Aer RPATH names |
| cutensornet-cu11 | 2.5.0 | cutensor-cu11>=2.0.1,<3 | libcutensornet.so.2 |
| cutensor-cu11 | 2.2.0, the newest release inside that range | none | libcutensor |

The cuQuantum wheels are `py3-none-manylinux2014_x86_64`, so they install
under the image's Python 3.13. `KERNEL_PINS` in `scripts/kaggle_run.py`
pins cuquantum-cu11 24.8.0 and cutensor-cu11 2.2.0, and the bootstrap
installs every pin with its dependencies under a constraints file that holds
the pins and the image's numpy and scipy fixed, so a GPU kernel loads one
version of every library on the cuStateVec path. `environment.json` records
qiskit-aer-gpu-cu11, cuquantum-cu11, custatevec-cu11, cutensornet-cu11 and
cutensor-cu11. A CPU or TPU kernel installs `CPU_KERNEL_PINS`, which carry
the CPU Aer build and no cuQuantum wheel.

Every GPU kernel that installed the Aer wheel with its dependencies already
held the libraries: the probe at
`results/kaggle/2026-10-16T204620Z-gororoba-aer-gpu-probe` imported the wheel
and ran GPU trajectories, which the NEEDED entries require to resolve. Aer
leaves `cuStateVec_enable` off by default and no retained GPU run sets it,
so no retained record exercises the library.

## Keeping the run on the GPU

Aer falls back to the CPU in silence: an AerSimulator on a host without a
usable CUDA build or device still constructs, and `available_devices()`
still lists GPU. A kernel can leave the GPU by six routes. `--gpu-env` closes
each one before the entry starts, and `--require-gpu` closes the last one
while the entry runs:

| Route to the CPU | Mechanism | What closes it |
| --- | --- | --- |
| Interpreter ABI | qiskit-aer-gpu-cu11 0.17.2 publishes cp313 wheels only, and the CUDA 12 qiskit-aer-gpu stops at 0.15.1, so the CI venv's Python 3.14.7 can take only CPU Aer | `gpu_interpreter` builds the venv from the image's own `sys.executable` (Python 3.13), for which every pin has a manylinux wheel |
| Image packages | the image ships its own numpy, scipy and Aer | `uv venv --seed` starts the venv empty, so the image's packages stay out of the entry |
| Shared module directory | qiskit-aer and qiskit-aer-gpu-cu11 both install `qiskit_aer/`, so the CPU wheel that requirements.txt pins overwrites the CUDA controller module when both install | `ci/install_pins.sh` with `AER_PINS` drops the `qiskit-aer==` line and installs the GPU wheels in the same resolve; `gpu_env_failures` requires the GPU distribution to be the only owner of `qiskit_aer/__init__.py` |
| Missing device | a CPU machine, or a GPU session that attached no device | nvidia-smi must list `MACHINE_GPUS` devices (two on NvidiaTeslaT4), and a seeded Bell run with `device="GPU"` must succeed with result metadata `device` GPU |
| cuStateVec off | Aer reports `cuStateVec_enable` false when `batched_shots_gpu` is also set, and false when libcustatevec fails to load | the cuStateVec Bell run sets `batched_shots_gpu` False and must report `cuStateVec_enable` true; `noise_simulator` raises ValueError on `custatevec=True` with `batched_shots=True` |
| One row leaves the GPU | a configuration the build rejects, or a child that runs on another device | `aer_gpu_probe.py --require-gpu` reads each GPU row's metadata through `gpu_fallback` and exits on the first row that reports another device or leaves cuStateVec off; `--check` enforces the same rule on the retained record |

`gpu_env.json` keeps the evidence for each row of the table: the installed
version of every pin, the owners of `qiskit_aer/__init__.py`, Aer's devices,
numpy's build configuration, and both Bell runs with their metadata. A
nonempty `failures` list exits 4 and names the route. The one exemption is
`gpu_statevector_batched_jump`, the batched configuration the cu11 build
aborts on control flow (`KNOWN_GPU_ABORTS`); a row that aborts is still
recorded with its exit code.

The venv holds the build host's numerical stack at the pinned versions:
numpy 2.5.4 and scipy 1.18.1 on scipy-openblas 0.3.34 with DYNAMIC_ARCH, so
OpenBLAS selects the host CPU's kernels at load time. `report.numpy` in
`gpu_env.json` records both choices. On the Kaggle CPU kernel it read
"OpenBLAS 0.3.34.106.0 USE64BITINT DYNAMIC_ARCH NO_AFFINITY SkylakeX
MAX_THREADS=64", and it reported numpy's X86_V2 baseline with X86_V3 (AVX2)
found and the AVX-512 groups absent.

## T4 check

The kernel runs the probe under `--gpu-env`. The venv uses the image's
Python 3.13 and installs requirements.txt and ci/requirements-ci.txt, with
the wheels above taking qiskit-aer's place. Before the entry starts, the
kernel requires all of the following and otherwise exits 4:

- every pin at its version;
- qiskit-aer-gpu-cu11 as the only owner of `qiskit_aer/__init__.py`;
- both T4s listed by nvidia-smi;
- GPU Bell runs that report device GPU, and `cuStateVec_enable` true on the
  cuStateVec run.

The probe's `--require-gpu` then stops at the first row that leaves the
GPU. The push carries the two calibration snapshots the probe reads:

```sh
"$PYTHON" scripts/kaggle_run.py push scripts/aer_gpu_probe.py \
    --slug gororoba-aer-gpu-config --machine NvidiaTeslaT4 --gpu-env --timeout 3600 \
    --include docs/evidence/calibration/history/ibm_fez/20261016T1212520700.json \
    --include docs/evidence/calibration/ibm_kingston.json \
    -- --out /kaggle/working/output/aer_gpu_probe.json --workloads toy,width --widths 7,10 --require-gpu
```

The same push with `--machine cpu` stops at the preflight, which tests the
fallback error on Kaggle at no GPU cost.

The CPU kernel
(`results/kaggle/2026-10-17T211857Z-gororoba-aer-gpu-env-preflight`) did
exactly that. It held all 13 pins under Python 3.13.15, with numpy on
scipy-openblas 0.3.34 and qiskit-aer-gpu-cu11 as the only owner of
`qiskit_aer`, then exited 4 with three failures:

- nvidia-smi listed no GPU;
- both Bell runs raised "No CUDA device available!".

On that machine `AerSimulator().available_devices()` still listed GPU. The
cu11 build reports GPU whether or not a CUDA device exists, so only a run's
result metadata shows where it executed.

**Sizing the timeout.** The build host ran exactly this entry in the same
pinned venv (Python 3.13.15, numpy 2.5.4 on scipy-openblas 0.3.34, the cu11
wheels on an RTX 4070 Ti):

| Rows | Process seconds |
| --- | --- |
| 11 readout-toy rows | 47 |
| 24 width rows | 1,226 |
| of which the three 10-qubit dynamic density-matrix rows | 769 |

At two to three times the host's GPU time on a T4, plus the venv install,
the work fits 3600 s.

The probe runs every static row before any dynamic row, and the 10-qubit
dynamic density-matrix rows come last. A timeout therefore cuts only those
rows, and the record keeps every row finished before the cut.

**Contention.** A row counts as contended when processes outside the
probe's own process tree held more than FOREIGN_CPU_LIMIT CPUs before or
during it; the probe's own Aer threads never count. On the build host, the
1-minute load-average rule marked every row of a four-CPU probe busy,
because that average still counts the previous row. Each row then waited
IDLE_WAIT_SECONDS and ran again, which is how the first T4 push
(`results/kaggle/2026-10-17T083803Z-gororoba-aer-gpu-config`) overran
5400 s without one finished row.

Read `kaggle quota` before and after, then `status` and `collect` retain the
output under results/kaggle/.

**Result.** The push above ran as
`results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config` in 0.84 h of GPU
quota and exited 0. Its `gpu_env.json` lists no failure, nvidia-smi listed
both T4s, and both Bell runs report device GPU, the cuStateVec run with
`cuStateVec_enable` true. All 35 rows ran uncontended, every GPU row reports
device GPU, and every cuStateVec row reports `cuStateVec_enable` true; gate
core-450 rechecks the record. The timings and the two-GPU metadata are in
`docs/evidence/aer_gpu_configuration/README.md`.

## Reading the result

- `gpu_env.json` comes first. A nonempty `failures` list names each pin,
  owner, GPU or Bell-run difference, and the kernel ran no entry.
  `install-pins.txt` and `gpu-env-report.txt` hold the commands' output.
- The check succeeds when every `gpu_statevector_custatevec` row carries
  `cuStateVec_enable` true in `metadata`, no `failed` field, and a
  `tvd_to_cpu_statevector` inside the row's `sampling_scale`.
- A row's `failed` field holds the child's exit code and `stderr_tail` its
  error. "does not support cuStateVec" there means the library did not load;
  `machine.packages` in the record and `environment.json` name the wheels
  the kernel installed.
- Aer 0.17.2 reports `cuStateVec_enable` false on a run that also sets
  `batched_shots_gpu`, so `noise_simulator` raises ValueError on
  `custatevec=True` with `batched_shots=True`; `custatevec=True` alone turns
  the GPU's batched default off, and the probe's cuStateVec configuration
  runs unbatched. Its plain-GPU comparison row is
  `gpu_statevector_unbatched`.
- Seeded GPU counts differ from CPU counts, so a CI gate re-derives a GPU
  record from its retained counts and never resamples (root AGENTS.md,
  "Simulation on Kaggle").

## CUDA 13 build

`push --gpu-env --gpu-aer cu13` runs the venv on qiskit-aer-gpu-cu13
0.17.2 in place of the cu11 wheels. The default stays cu11.

- **Wheel.** `docs/notes/kaggle/recipes/build_aer_gpu_cu13_wheel.sh` builds
  `qiskit_aer_gpu_cu13-0.17.2-cp313-cp313-manylinux_2_39_x86_64.whl` in
  rootless podman from the CUDA 13.0.3 devel image on Ubuntu 24.04, with
  SASS for sm_75 (T4) and sm_89 and cuStateVec and cuTensorNet linked. Its
  sha256, `3d40fc33...253d5`, is `AER_GPU_WHEELS["cu13"]` in
  `scripts/kaggle_run.py`.
- **Library chain.** `GPU_AER_PINS["cu13"]` adds the nine CUDA 13 wheels of
  `docs/notes/kaggle/recipes/aer-gpu-cu13-runtime-pins.txt`: the CUDA 13.0.3
  toolkit libraries under `site-packages/nvidia/cu13/lib`, custatevec-cu13
  1.15.0 and cutensornet-cu13 2.14.0 under `cuquantum/lib`, and
  cutensor-cu13 2.8.1 under `cutensor/lib`. The module's DT_RPATH names those
  three directories, and every CUDA soname the cuQuantum libraries reach is a
  direct dependency of the module, so an LD_LIBRARY_PATH that holds another
  CUDA toolkit cannot substitute a copy. torch 2.14.1 (`--gpu-env-with
  torch`) requires cuda-toolkit 13.0.3, which resolves to the same nvidia-*
  versions.
- **Dataset.** No index serves the wheel. `kaggle_run.py artifact --slug
  gororoba-aer-gpu-cu13-wheel --file WHEEL --sha256 HEX` uploads it as a
  private dataset holding that one file, after checking its bytes, and writes
  `results/kaggle/datasets/gororoba-aer-gpu-cu13-wheel.json`
  (`kaggle-artifact-v1`).
  - A cu13 push attaches that dataset itself. It refuses unless the record
    names exactly the wheel and sha256 of `AER_GPU_WHEELS`.
  - The kernel finds the file under /kaggle/input by name, verifies its
    sha256, and copies it to /tmp/gororoba/wheelhouse. `ci/install_pins.sh`
    then installs the copy as a direct file reference, with `PIP_FIND_LINKS`
    naming that directory, so no index can supply the distribution.
  - A missing, ambiguous or different file is a `failures` entry in
    gpu_env.json, and the kernel exits 4 before anything is installed.
- **Records.** gpu_env.json's `wheel` holds the dataset path, size and
  sha256. The report names `qiskit-aer-gpu-cu13` as the owner of
  `qiskit_aer/__init__.py`. It also gives the `controller_wrappers` module
  path and `cuda_libraries`, each CUDA library the import mapped. The import
  needs no GPU, so a CPU push shows the wheel installing and its libraries
  resolving at no GPU cost, then exits 4 because nvidia-smi lists no GPU and
  the Bell runs raise.
- **On Kaggle.**
  - `results/kaggle/2026-10-18T072100Z-gororoba-aer-gpu-cu13-preflight` (CPU
    machine): the dataset kept the `.whl` intact, its sha256 verified,
    `qiskit_aer` belongs to qiskit-aer-gpu-cu13 and all nine CUDA libraries
    load from the venv's site-packages; the kernel exited 4 on the missing
    GPU alone.
  - `results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config` (T4 x2,
    0.85 GPU hours): gpu_env.json lists no failure, nvidia-smi lists both
    T4s, and the cuStateVec Bell run reports `cuStateVec_enable` true, so
    the sm_75 code runs under driver 580.178.04. Every one of the 35 rows of
    `aer_gpu_probe.py --workloads toy,width --widths 7,10` ran.
- **Against the cu11 wheel** (the same probe and seed,
  `results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config`; gate core-442,
  `aer_gpu_probe.py --check --compare-counts`):
  - All 15 GPU density-matrix rows draw the cu11 wheel's seeded counts, and
    run 1 to 14 percent faster per shot.
  - 4 of 16 GPU statevector rows draw the same counts. The 12 width rows
    differ, unbatched ones without cuStateVec included, so seeded
    statevector trajectories are build-specific. The width rows retain only
    count hashes, so the record cannot test whether the two builds' count
    distributions agree.
  - Batched statevector runs about 9 percent faster per shot, unbatched
    statevector 1 to 4 percent slower and cuStateVec statevector 7 to 12
    percent slower.
  - A CPU row, `cpu_density_matrix_branching`, also differs; both builds
    miss its exact law, which is Aer 0.17.2's shot-branching readout fault.

