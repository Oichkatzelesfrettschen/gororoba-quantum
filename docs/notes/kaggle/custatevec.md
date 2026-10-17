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

The full Aer GPU configuration probe carries the cuStateVec row:

```sh
"$PYTHON" scripts/kaggle_run.py push scripts/aer_gpu_probe.py \
    --slug gororoba-aer-gpu-config --machine NvidiaTeslaT4 --timeout 10800 \
    --include docs/evidence/calibration/history/ibm_fez/20261016T1212520700.json \
    --include docs/evidence/calibration/ibm_kingston.json \
    -- --out /kaggle/working/output/aer_gpu_probe.json
```

The probe rewrites `--out` after every row, and a session Kaggle ends at
the timeout returns `/kaggle/working/output`, so the record keeps every
row finished before the cut. A T4 host has four CPUs: the probe reruns each
row whose load exceeded them at its start or end and waits up to `IDLE_WAIT_SECONDS`
before each of its rows, so the full probe outlasts 5400 s there.

`--workloads n21 --configurations
cpu_statevector,gpu_statevector_unbatched,gpu_statevector_custatevec`
after `--` runs only the three statevector paths.

Read `kaggle quota` before and after, then `status` and `collect` retain the
output under results/kaggle/.

## Reading the result

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
