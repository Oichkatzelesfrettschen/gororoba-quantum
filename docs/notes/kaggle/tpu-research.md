# Kaggle TPU access: sources, measured routes and root-cause analysis

Every Kaggle batch session this account requested with a TPU accelerator ran
in a container on Kaggle's CPU image on a 4-core machine. Kaggle's server
recorded the TPU accelerator on each of them, so the request reached the
server intact through every route (CLI, kagglesdk, MCP, editor commit) and
the session lost its TPU at allocation. The TPU quota's `time_used` stayed at
zero throughout. Kaggle staff name one documented cause, an image pin, and it
explains one of the five recorded versions; the four unpinned versions carry
no image pin and ran on the same CPU image. The interactive editor route is
unverified (section 5).

## 1. How a session is judged

A session is a TPU VM only when its own output shows it. Each of these
markers comes from a source or a measurement named beside it:

| Marker | TPU VM | CPU session | Authority |
|---|---|---|---|
| `os.cpu_count()`, MemTotal | 96 cores, 330 GB | 4 cores, 30 GB | [site/notebooks.md](site/notebooks.md) |
| `/dev/accel*` or numbered `/dev/vfio/N` | present | absent | Google Cloud TPU VM layout; general knowledge, unsourced here |
| PCI functions of vendor `1ae0` (Google) | present | absent | PCI vendor registry |
| `ISTPUVM`, `TPU_PROCESS_ADDRESSES` | `1`, `local` | unset | Kaggle docker-python `tpu/Dockerfile` |
| `libtpu` distribution | installed (`0.0.17`) | absent | Kaggle docker-python `tpu/Dockerfile` |
| `jax.devices()` | 8 TPU devices | `cpu` only | JAX AI Stack tutorial |
| server `isolatorResults` image | none (staff: TPU VM sessions have a null dockerImage) | `gcr.io/kaggle-images/python` | kaggle-api issue 1197; ListKernelVersions |
| quota `tpu_quota.time_used` | grows | unchanged | MCP `get_accelerator_quota` |

`scripts/tpu_probe.py` records the first six markers in its `hardware`
block (schema `tpu-probe-v2`). The server record comes from
`kernels.KernelsService/ListKernelVersions`, which `scripts/kaggle_sessions.py
versions` calls; each version's `run.commit.settings.accelerator` holds the
accelerator the server accepted and `run.isolatorResults` the image the
session ran.

## 2. Measured routes

Account `probablyeric`, 2026-10-16. Every row ran on a 4-core Intel Xeon
2.20 GHz machine with about 31 GiB RAM, JAX reported only the `cpu` backend,
and `tpu_quota.time_used` stayed at 0. "Server record" is the version's
ListKernelVersions entry.

| Route | Request | Session software | Server record |
|---|---|---|---|
| CLI push, script (`gororoba-substrate-probe-tpu`, `-tpuv5e8`, `-tpuv6e8`) | `machine_shape` TpuV5E8 or TpuV6E8, `--accelerator`, default image | Python 3.13.15 | not read |
| CLI push, script (`gororoba-tpu-probe` v1) | `machine_shape` TpuV6E8, `enable_tpu`, `--accelerator`, no image | Python 3.13.15, jax 0.11.1, torch 2.11.0+cpu, glibc 2.39, `libtpu.so` missing | accelerator `TPU_V6E_8`; image `81b1e7c4` |
| CLI push, notebook (`gororoba-tpu-probe` v2) | `machine_shape` TpuV5E8, `--accelerator`, `docker_image` pinned to digest `dafd4ce5` | Python 3.12.13, jax 0.7.2, torch 2.10.0+cpu, glibc 2.35, `libtpu.so` missing | accelerator `TPU_V5E_8`, `dockerImageVersionId` 31429; image `dafd4ce5` |
| kagglesdk `create_kernel_session` | `TpuV5E8` | returned a session id; no observable execution | not read |
| MCP `save_notebook` (`gororoba-tpu-mcp-probe` v1) | `machineShape` TpuV5E8, `enableTpu`, `SaveAndRunAll`, every presence flag | Python 3.13.15, jax 0.11.1, no libtpu | accelerator `TPU_V5E_8`; image `81b1e7c4` |
| Editor "Save & Run All (Commit)" (`gororoba-tpu-mcp-probe` v2) | Settings -> Accelerator TPU v5e-8, "Run with TPU for this session" | Python 3.13.15, jax 0.11.1, no libtpu | accelerator `TPU_V5E_8`; image `81b1e7c4` |
| MCP `save_notebook` (`gororoba-tpu-probe-latest` v1) | `machineShape` TpuV5E8, `enableTpu`, `dockerImagePinningType latest`, no image, no `kaggle` notebook block | Python 3.13.15, jax 0.11.1, torch 2.11.0+cpu, no libtpu, no `/dev/accel*`, no vendor-1ae0 PCI function, `ISTPUVM` unset | not read; the run's `KAGGLE_DOCKER_IMAGE` is `81b1e7c4` |
| CLI push, staff recipe (`gororoba-tpu-probe-cli` v1) | notebook, `enable_tpu`, `machine_shape` TpuV5E8, `docker_image_pinning_type latest`, no image, no `kaggle` block, no `--accelerator` | identical to the row above | accelerator `TPU_V5E_8`; image `81b1e7c4` |

`81b1e7c4` is `gcr.io/kaggle-images/python@sha256:81b1e7c4b4f0...`, the
image built from docker-python's `Dockerfile.tmpl` (the CPU image);
`kaggle kernels pull -m` reports it as `docker_image` seconds after a push.
`dafd4ce5` is an older CPU image: it carries torch's `+cpu` build and no
libtpu, the combination the reporter of issue 1197 saw on the CPU image.

## 3. Root-cause analysis

The request is complete on every route. All five versions whose server
record was read store the TPU accelerator in `commit.settings`; the CLI,
kagglesdk, MCP and the editor's commit button all deliver it.

The image pin is the cause for one version. `gororoba-tpu-probe` v2 pinned
`dafd4ce5`, the server stored it as `dockerImageVersionId` 31429, and the
session ran that image; this is the override issue 1197 documents.
`scripts/kaggle_run.py` pins no image for a TPU push.

The image pin does not explain the other four. They named no image, the
server chose the CPU image itself, and the staff recipe (no image, latest
pinning, no notebook `kaggle` block) ran on it as well. Remaining
explanations, with what would decide each:

- **TPU allocation is unavailable to this account's batch sessions.** Staff
  describe pushed TPU runs as batch sessions limited to one per user; no
  push returned "Maximum batch TPU session count of 1 reached", so the
  limit was never the obstacle. The account's phone verification is in
  place, since GPU batch sessions run. An editor session that attaches a
  TPU VM (section 5) while batch sessions do not would confirm this.
- **The scheduler falls back to a CPU worker when no TPU capacity is free.**
  No source states this; a fallback that keeps the TPU accelerator in the
  record and runs on a CPU image would be indistinguishable from the rows
  above. Repeating one push at a different time of day and reading its
  `isolatorResults` would bound it.
- **A Kaggle server defect.** Issue 1197 is open, and its fix PR 1219
  changes only the client (it drops both image pins). A push whose request
  matches 1219's output and still runs on the CPU image places the fault on
  the server; `gororoba-tpu-probe-cli` v1 is such a push.

## 4. Sources

Stated items carry their source; inferences are marked.

- kaggle-api issue 1197 (Kaggle staff reply, 2026-09-17): a `docker_image`
  pinned to the CPU/GPU image in kernel-metadata.json, and a
  `dockerImageVersionId` in the notebook metadata (typical of `kaggle kernels
  pull -m`), override the TPU VM environment; TPU VM sessions have a null
  dockerImage on the backend; workaround: drop `docker_image` (or use
  `docker_image_pinning_type: "latest"` without it) and drop
  `dockerImageVersionId` or the notebook's `kaggle` block. Pushed TPU runs
  are batch sessions limited to one active or queued per user ("Maximum batch
  TPU session count of 1 reached") that can queue and start more slowly than
  interactive ones. No reporter confirmed the workaround.
  https://github.com/Kaggle/kaggle-api/issues/1197
- kaggle-api PR 1219, open: drops `docker_image` and `dockerImageVersionId`
  on TPU pushes. https://github.com/Kaggle/kaggle-api/pull/1219
- kaggle-api PR 1198: TPU v5e-8 is accelerator id `TpuV5E8`.
  https://github.com/Kaggle/kaggle-api/pull/1198
- Kaggle docker-python `tpu/Dockerfile`: sets `ISTPUVM=1` and
  `TPU_PROCESS_ADDRESSES=local` and force-installs `libtpu==0.0.17`, matched
  to jax 0.7.2 and torch 2.8.0; `tpu/requirements.in` carries torch_xla.
  https://github.com/Kaggle/docker-python/tree/main/tpu
- Kaggle notebooks documentation: TPU VM 96 cores and 330 GB RAM; 9 h per
  TPU session. [site/notebooks.md](site/notebooks.md). Kaggle TPU
  documentation: 20 hours per week. [site/tpu.md](site/tpu.md); the page's
  code targets the retired v3-8 and TensorFlow.
- JAX installation guide: stable Cloud TPU support is `pip install
  "jax[tpu]"` with no extra index; the `libtpu_releases.html` find-links
  index serves nightlies. https://docs.jax.dev/en/latest/installation.html
- JAX AI Stack tutorial: on a Kaggle v5e-8 the image needs no TPU install and
  `jax.devices()` lists 8 TPU devices.
  https://docs.jaxstack.ai/en/latest/JAX_for_LLM_pretraining.html
- Community projects (third party): select "TPU VM v5e-8" under the editor's
  session options; a successful upload does not prove a TPU was allocated;
  libtpu's metrics port 8471 never starts on Kaggle; chips stay claimed 10 to
  30 s after a process dies; `--xla_tpu_use_dynamic_smem_negotiation` is
  rejected by the v5litepod runtime. https://github.com/Kitkitkittt/kaggle-tpu-lab ,
  https://github.com/YLiu95/kaggle-tpu-inference
- Inferred: on a TPU VM, reinstalling jax or libtpu replaces the image's
  matched pair; `pip install "jax[tpu]"` is a repair for a TPU VM whose
  libtpu is missing, a state no source describes. On a CPU session it
  installs a library with no device to open.

## 5. Interactive editor route

An editor draft session with Settings -> Accelerator set to TPU v5e-8 showed
a TPU resource meter; a JAX probe run in it reported Python 3.13.15, jax
0.11.1, no libtpu and the `cpu` backend, and the quota's TPU `time_used`
stayed at 0. The probe's position relative to the session restart that an
accelerator change causes is unrecorded, so this result does not decide the
route. The deciding run loads the probe notebook (MCP `save_notebook` with
`QuickSave`), opens it in the editor with the page's `fetch` and
`XMLHttpRequest` wrapped to record request bodies, selects TPU v5e-8,
accepts the restart, waits for the session panel's "TPU VM" section, runs
`scripts/tpu_probe.py`'s hardware block, and reads the quota. A TPU VM there
makes the captured session-start request the reference to diff against the
batch requests; a CPU session there places the cause on the account or on
Kaggle's allocation.

## 6. Push procedure

1. `scripts/kaggle_run.py push --machine TpuV5E8 --timeout SECONDS` writes a
   notebook kernel with `enable_tpu`, `machine_shape`, latest image pinning,
   no `docker_image` and no notebook `kaggle` block, and pushes it with
   `--accelerator TpuV5E8`. Push only from a committed tree, never from a
   `kaggle kernels pull -m` copy, and check `kaggle quota` and that no TPU
   session is queued or running first.
2. Seconds after the push, `kaggle kernels pull -m OWNER/SLUG` shows the image
   the server assigned. A `docker_image` of `gcr.io/kaggle-images/python...`
   means a CPU session: cancel it (`scripts/kaggle_sessions.py
   cancel-running OWNER/SLUG`) instead of waiting for its output.
3. The kernel's first output, `scripts/tpu_probe.py`'s `hardware` block,
   decides the session: 96 cores, `/dev/accel*` or vfio groups, a vendor
   1ae0 function and `ISTPUVM=1` mark a TPU VM, and success is exactly 8 TPU
   devices from `jax.devices()`.
