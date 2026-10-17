# Kaggle TPU access: sources, measured routes and root-cause analysis

The leading cause, rated high, is Kaggle's identity verification: this
account has phone verification only, and the editor's session panel states "Some
accelerators, such as TPUs, require identity verification" beside a "Verify
identity" link, and the account settings page reads "Phone verification:
Verified" and "You have not verified your identity using Persona". Without
it, as observed here, Kaggle accepts a TPU request, records the TPU accelerator on the
version, and runs the session on a 4-core CPU worker on the CPU image with
no error; every route measured here (CLI, MCP, the editor's commit and the
editor's interactive session) did exactly that, and the TPU quota's
`time_used` stayed at zero. Phone verification is the gate for GPUs, which
is why GPU sessions run. An image pin is a second, independent cause of a
CPU image (kaggle-api issue 1197) and explains one recorded version. After
the owner completed Persona verification the server began classifying the
same request as a TPU session: the version carries `isTpuEnabled`, holds
the account's single TPU batch slot and waits in the queue (section 3,
"After verification"). No TPU VM has executed yet, so the hardware marker
of section 1 is still the outstanding confirmation.

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

Account `probablyeric`, 2026-10-16. `tpu_quota.time_used` stayed at 0 after
every row, and every row that recorded a JAX backend recorded only `cpu`.
Rows whose output carries `environment.json` (the CLI rows) or the
hardware probe (the `-latest` and `-cli` rows) record 4 cores and about 31
GiB; `environment.json` names an Intel Xeon at 2.20 GHz. The two
`gororoba-tpu-mcp-probe` rows recorded Python and the JAX state only.
"Server record" is the version's ListKernelVersions entry.

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

Leading cause, rated high: the account lacks Persona identity
verification, which the editor's session panel names as a TPU requirement
(section 5). The settings page's own Persona text names competitions, not
TPUs, and no Kaggle page captured here states the TPU rule; Kaggle's
benchmarks documentation requires "additional identity verification" of
accounts registered after December 15, 2025 to execute task notebooks
([site/benchmarks.md](site/benchmarks.md)), and this account registered on
2026-10-15. One push after verification decides it: a `kaggle_run.py push
--machine TpuV5E8` session whose `tpu_probe.py` hardware block reports 96
cores and 8 TPU devices confirms it, and 4 cores with no TPU devices refutes
it. The panel string appearing unchanged on an identity-verified account
would also lower it. The analysis that led there:

The request is complete on every route. All five versions whose server
record was read store the TPU accelerator in `commit.settings`; the CLI,
the MCP and the editor's commit button all deliver it.

The image pin is the cause for one version. `gororoba-tpu-probe` v2 pinned
`dafd4ce5`, the server stored it as `dockerImageVersionId` 31429, and the
session ran that image; this is the override issue 1197 documents.
`scripts/kaggle_run.py` pins no image for a TPU push.

The image pin does not explain the other four. They named no image, the
server chose the CPU image itself, and the staff recipe (no image, latest
pinning, no notebook `kaggle` block) ran on it as well, so the loss happens
at allocation; the unpinned pushes `gororoba-tpu-probe-latest` v1 and
`gororoba-tpu-probe-cli` v1 rule out the image pin as the general cause.
The editor's interactive session, which takes no batch path, lost the TPU
the same way (section 5), which rules out request shape; it ran under the
editor's "Pin to original environment" setting, so it does not by itself
rule out a pin. The batch-session limit is ruled out because no push
returned "Maximum batch TPU session count of 1 reached", and phone
verification because GPU sessions run. That leaves the account gate the
editor names.

### After verification

`gororoba-tpu-probe-verified` v1 (session 359130889), pushed at 20:07:39
UTC on 2026-10-16 with `kaggle_run.py push --machine TpuV5E8` from the
committed tree, differs from every earlier version on four server-side
counts:

| Observation | Before verification (ten versions above) | After verification |
|---|---|---|
| `run.isTpuEnabled` in ListKernelVersions | absent | `true` |
| `docker_image` in `kaggle kernels pull -m` seconds after the push | `gcr.io/kaggle-images/python@sha256:81b1e7c4...` | empty |
| a second TPU push while the first is live | accepted: `-tpuv5e8` and `-tpuv6e8` went in 1.8 s apart and both ran | refused: "Maximum batch TPU session count of 1 reached" (a TpuV6E8 probe at 21:31 UTC) |
| status | ran on the CPU worker | `QUEUED`, with an empty session log, for at least 1 h 40 min |

`tpu_quota.time_used` and `time_reserved` stay at 0 while the version
queues. The web method `kernels.KernelsService/GetKernelSessionLog` takes
`{"sessionId": N}` and answers 200 with an empty body for the queued
session; `kernelSessionId`, `kernelRunId` and `kernelVersionId` are
refused with "Permission 'kernelSessions.get' was denied". The version page
reads "Queued..." with accelerator "TPU v5e-8" and shows no queue position.
The four rows together move the identity gate from the leading cause to
the measured one for allocation; a TPU VM's hardware block, when the
session starts, closes it.

### Queue behavior

A QUEUED TPU version is the documented normal state of a busy pool. Kaggle's
notebooks documentation says "Free TPU availability is limited: in busy
times, you might be placed in a queue" (the sentence predates v5e-8 and
names the v3-8). Forum reports of the same condition: "TPU session queued
for 14+ hours" (topic 745817, v5e-8, 2026-10-04), "TPU queue times are
getting really long" (743783), "Very long TPU queues" (664302) and "Long
TPU task waiting time (~ 2hrs)" (271777); in a search summary of the last,
Kaggle staff call it a demand and supply issue, with T4 almost never
queued and TPUs queued now and again, and other threads report positions
such as #323 and a 13 h wait. These pages render client-side, so only the
titles and search summaries were readable; no thread body was fetched. The
5.5 h queue here sits inside the reported range of 2 h to more than 14 h.
Inferred: the queue is a shared FIFO-like pool whose drain rate is set by
the 9 h session cap of the sessions ahead, so waits of hours persist while
public GLM-serving notebooks hold slots (the claim of topic 745817).

Queue position appears in one place. The older interactive editor message
"You are #n in the queue. You can wait, try connecting again later" is the
title of product-feedback thread 318562, so an interactive request can show
a position. A batch version shows "Queued..." with no position, and the
session-log method returns an empty body, as measured above (batch row).
No Kaggle page states whether queued time counts against the 20 h weekly
quota; the measured `time_used` and `time_reserved` of 0 after 5.5 h of
queueing show that a queued batch session neither consumes nor reserves
quota here. The slot cap is separate from quota: the queued version holds
the account's one TPU batch slot (kaggle-api issue 1197 and the
refused second push above), so a queued session blocks later TPU pushes
until it starts or is cancelled.

### Whether libtpu is in the TPU image

Finding, rated high: the CPU-session reading is correct. The TPU image
installs libtpu itself, so a granted TPU VM has `libtpu` and a CPU session
lacks it for the reason that it is a different image on a different
machine. Stated: Kaggle's docker-python `tpu/Dockerfile` ends with `uv pip
install --system --force-reinstall libtpu==0.0.17` and the comment "We
install a libtpu version compatible with both jax 0.7.2 and torch 2.8.0.
Why? tunix latest -> flax 0.12 -> jax 0.7.2 -> libtpu 0.0.23. However, that
libtpu causes pjrt api errors for torch 2.8.0"; `tpu/config.txt` pins
Python 3.12, torch 2.8.0, torchvision 0.23.0 and TensorFlow 2.20.0, and
`tpu/requirements.in` lists the TPU jax and torch_xla. The build script
tags the image `kaggle/python-tpuvm-build`; no source names a registry path
`gcr.io/kaggle-images/python-tpu`, and staff state that a TPU VM session
carries a null dockerImage on the backend (kaggle-api issue 1197), so the
image is chosen server side from the accelerator rather than pinned by
reference. `TPU_DOCKER_IMAGE` does not occur in this tree's
`scripts/kaggle_run.py`, and the staff recipe pins no image anyway.
https://raw.githubusercontent.com/Kaggle/docker-python/main/tpu/Dockerfile ,
https://raw.githubusercontent.com/Kaggle/docker-python/main/tpu/config.txt ,
https://raw.githubusercontent.com/Kaggle/docker-python/main/tpu/build

Versions the TPU image ships: Python 3.12, jax 0.7.2, libtpu 0.0.17, torch
2.8.0 (CPU build, with torch_xla for the TPU). The measured TPU-image
session (`gororoba-tpu-probe` v2: Python 3.12.13, jax 0.7.2, glibc 2.35)
matches the jax and Python of the TPU image except that it had no libtpu
and 4 cores, and its torch was 2.10.0+cpu, so that run used an older CPU
image (`dafd4ce5`) whose versions overlap the TPU image's (inferred),
which section 3 already attributes to the image pin. The default image
(Python 3.13.15, jax 0.11.1, torch 2.11.0+cpu, no libtpu) is the CPU image.
Neither lacks libtpu through a broken TPU install: libtpu is absent in the
CPU images by design. The kaggle docs give the TPU VM as 96 cores and 330
GB, against 4 cores and 30 GB on the CPU machine measured here.

Does `pip install "jax[tpu]"` help or hurt on a granted TPU VM: it hurts. It
replaces the matched jax 0.7.2 and libtpu 0.0.17 pair with the latest
jax and its libtpu, and the Dockerfile comment records that a newer libtpu
(0.0.23) breaks torch 2.8.0's PJRT plugin; for JAX alone the upgrade
may work but it forfeits the tested pair (inferred). The JAX AI Stack
tutorial runs on the image as shipped (`jax.devices()` lists 8 devices
after installing only `jax-ai-stack[grain]`). The `libtpu_releases.html`
find-links index serves nightlies only. On a CPU session `jax[tpu]` is
inert: it installs libtpu with no device to open. A 96-core host with
`/dev/accel*` and a missing libtpu is the only case where the install is a
repair, and no source reports it.

### Interactive versus batch

No source states that an interactive session gets a TPU faster than a
batch commit, and none describes a separate interactive TPU queue. Stated:
the notebooks documentation applies the same wording ("you might be placed
in a queue", "may take a few moments to several minutes") to the
editor's accelerator switch, and gives interactive and Save & Run All
sessions the same 9 h TPU cap; the Save & Run All session is "a separate
session from your interactive session". Stated (staff, issue 1197):
pushed batch TPU runs "can queue and start more slowly than interactive
ones". Inferred: batch sessions queue behind a per-user cap of one and
carry no position display, interactive sessions can show a position, but
whether they draw from a different pool is unsupported by any source read.
Here the interactive route never reached a TPU for the verification
reason in the summary, so it gives no timing.
https://www.kaggle.com/docs/notebooks.md ,
https://www.kaggle.com/docs/efficient-gpu-usage.md (separate batch and
interactive sessions; interactive sessions idle out)

Measured after verification, 01:50 UTC on 2026-10-17: an interactive
editor session on a second kernel (`gororoba-tpu-mcp-probe`) with
accelerator TPU v5e-8 entered the queue while the batch version above
stayed `QUEUED`, so the batch cap of one TPU session leaves interactive
requests a separate line. The editor reads "TPUs are popular right now.
You are #524 in the queue. You can wait, try connecting again later, or
use another accelerator."; the position moved from 524 to 520 in five
minutes. `tpu_quota.time_used` and `time_reserved` stayed 0 for the
queued request. The editor's Settings -> Accelerator menu lists None,
GPU T4 x2 and TPU v5e-8 only, so TPU v6e-8 exists as an API
`machine_shape` without an editor route. While the status reads
"Draft Session Starting...", the toolbar power button is disabled; Run ->
Stop session withdraws the queued request ("Session stopped."). A queued
interactive request is withdrawn this way before its browser closes,
because a request that starts with no client attached bills until the
idle timeout.

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
- Kaggle forum topic 745817 (2026-10-04): a TPU v5e-8 notebook queued
  for more than 14 hours; a reply attributes the shortage to public
  notebooks that serve GLM-5.3-Flash as an API from the free TPUs, several
  of which the Kaggle search lists. A queue of hours is therefore the
  expected wait for a v5e-8 batch session.
  https://www.kaggle.com/discussions/general/745817
- Kaggle forum threads on TPU queues: https://www.kaggle.com/general/745817 ,
  https://www.kaggle.com/discussions/general/743783 ,
  https://www.kaggle.com/general/664302 ,
  https://www.kaggle.com/product-feedback/271777 ,
  https://www.kaggle.com/product-feedback/318562 (titles and search
  summaries only; bodies unreadable).
- Inferred: on a TPU VM, reinstalling jax or libtpu replaces the image's
  matched pair; `pip install "jax[tpu]"` is a repair for a TPU VM whose
  libtpu is missing, a state no source describes. On a CPU session it
  installs a library with no device to open.

## 5. Interactive editor route

The editor session of `gororoba-tpu-mcp-probe`, started with Settings ->
Accelerator TPU v5e-8, showed "Draft Session" with HDD, CPU, RAM and TPU
meters and "Quota: 00:00 / 20 hrs". The hardware probe of
`scripts/tpu_probe.py`, run in that live session through JupyterLab's
command registry (`window.jupyterapp.commands.execute(
"notebook:run-all-cells")` inside the `notebook-editor-cells` frame),
reported `KAGGLE_KERNEL_RUN_TYPE=Interactive`, 4 cores, 31 GiB, no
`/dev/accel*`, no vfio groups, no vendor-1ae0 PCI function, `ISTPUVM` unset,
image `81b1e7c4`, no libtpu and the `cpu` JAX backend; the TPU meter is the
selection, not an attached device. The same panel carries the identity
requirement quoted in the summary and an environment setting, "Pin to
original environment", which is the editor's form of the image pin.

The editor's notebook frame is JupyterLab 4 served from
`kkb-production.jupyter-proxy.kaggle.net` with `exposeAppInBrowser` on; its
`/api/kernels` lists nothing because the kernel runs behind Kaggle's own
channel, so code reaches the session through the app's command registry
and the cell's shared model (`cell.model.sharedModel.setSource`), and the
output through `cell.model.outputs.toJSON()`.

## 6. Push procedure

0. Identity verification: the account owner completes Persona verification
   from the account settings page ("Verify my account"); it takes a
   government ID and a selfie, so only the owner does it.
1. `scripts/kaggle_run.py push --machine TpuV5E8 --timeout SECONDS` writes a
   notebook kernel with `enable_tpu`, `machine_shape`, latest image pinning,
   no `docker_image` and no notebook `kaggle` block, and pushes it with
   `--accelerator TpuV5E8`. Push only from a committed tree, never from a
   `kaggle kernels pull -m` copy, and check `kaggle quota` and that no TPU
   session is queued or running first: a queued TPU version holds the
   account's one TPU batch slot, so a second TPU push is refused until it
   ends; cancelling a queued version to try the other TPU type presumably
   starts its wait over (inferred: Kaggle shows no queue position).
2. `kaggle kernels pull -m OWNER/SLUG` seconds after the push names an
   image; every CPU session here showed `gcr.io/kaggle-images/python`
   there, and what it shows for a real TPU VM is unobserved, so it is a hint
   and never a reason to cancel.
3. The kernel's first output, `scripts/tpu_probe.py`'s `hardware` block,
   decides the session, and a CPU session is cancelled on it
   (`scripts/kaggle_sessions.py cancel-running OWNER/SLUG`): 96 cores, `/dev/accel*` or vfio groups, a vendor
   1ae0 function and `ISTPUVM=1` mark a TPU VM, and success is exactly 8 TPU
   devices from `jax.devices()`.
