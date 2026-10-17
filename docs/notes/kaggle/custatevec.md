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
IDLE_WAIT_SECONDS and ran again, which is how the first T4 push overran
5400 s without one finished row.

Read `kaggle quota` before and after, then `status` and `collect` retain the
output under results/kaggle/.

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
