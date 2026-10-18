# Kaggle guides

Kaggle kernels run every simulation of 14 qubits or fewer (root AGENTS.md,
"QPU time and calibration"). These guides play the role
`docs/notes/ibm_quantum/` plays for IBM hardware:

| Guide | Content |
| --- | --- |
| [workflow.md](workflow.md) | `scripts/kaggle_run.py` push, status and collect; authentication; how a result enters the research state |
| [substrates.md](substrates.md) | measured CPU, RAM, disk, GPU, TPU and qubit limits of each machine shape, and what runs on which substrate |
| [gpu-runbook.md](gpu-runbook.md) | how to run a GPU kernel without wasting quota: the procedure, the failures that shaped it, Aer and numpy practice, the quota ledger and the 15-qubit routing gate |
| [custatevec.md](custatevec.md) | the cuQuantum libraries the cu11 Aer wheel loads, their pins, the cuStateVec T4 check and how to read it |
| [hypercomplex-stack.md](hypercomplex-stack.md) | the eight hypercomplex packages built and proved identically on the host and in every kernel |
| [interfaces.md](interfaces.md) | every CLI command, kagglesdk method and MCP tool, mapped onto shared operations; which call addresses which kernel version, where a session id comes from, how a session is cancelled; accelerator fields, authentication and the host's MCP permission policy |
| [tpu-research.md](tpu-research.md) | every TPU request route measured on this account, the server record of each version, the markers that decide whether a session is a TPU VM, the root-cause analysis and its sources, and the push procedure |
| [libraries.md](libraries.md) | the Kaggle PyPI packages: kaggle, kagglesdk and kagglehub as installed Arch packages with their recipes and run examples, the packages left out and why, and what a kernel image carries |

## Captured Kaggle documentation

`scripts/capture_kaggle_docs.py` keeps Kaggle's own documentation here
byte for byte, with `MANIFEST.json` in each directory naming every file's
source URL and sha256 (gate core-283 rechecks the bytes):

| Directory | Source | Content |
| --- | --- | --- |
| [site/](site/) | kaggle.com/docs, each page's Markdown source at `https://www.kaggle.com/docs/<page>.md`, for every page the docs navigation lists; root-relative links are relative to kaggle.com | [notebooks](site/notebooks.md) (session resources and limits), [efficient-gpu-usage](site/efficient-gpu-usage.md), [tpu](site/tpu.md), [api](site/api.md) (auth, OAuth scopes, rate limits), [mcp](site/mcp.md) (56 MCP tools with request and response), [models](site/models.md), [datasets](site/datasets.md), [packages](site/packages.md), [benchmarks](site/benchmarks.md), [competitions](site/competitions.md), [competitions-setup](site/competitions-setup.md), [organizations](site/organizations.md), [groups](site/groups.md) |
| [cli/](cli/) | github.com/Kaggle/kaggle-cli `docs/` at commit 931014d, verbatim | [kernels](cli/kernels.md) (push, `--accelerator`, the accelerator list), [kernels_metadata](cli/kernels_metadata.md), [configuration](cli/configuration.md), models, datasets, output format, search |

Facts the guides above rest on, with their source:

- Session resources: 12 h per CPU or GPU session and 9 h per TPU session;
  20 GB saved in `/kaggle/working` plus unsaved scratch; CPU sessions 4
  cores and 30 GB RAM; GPU sessions 4 cores and 29 GB RAM; the TPU VM 96
  cores and 330 GB RAM; interactive sessions end after 20 idle minutes
  ([site/notebooks.md](site/notebooks.md)).
- TPU use: up to 20 hours per week and 9 hours per session
  ([site/tpu.md](site/tpu.md)).
- Accelerator IDs as of September 2026: NvidiaTeslaT4 (2 x T4),
  NvidiaTeslaA100, NvidiaL4, NvidiaL4X1, NvidiaH100, NvidiaRtxPro6000,
  TpuV5E8, TpuV6E8, some restricted to competitions or admins; the push's
  `--accelerator` selects one ([cli/kernels.md](cli/kernels.md)), and
  `enable_gpu` and `enable_tpu` are deprecated in favor of `machine_shape`
  ([site/mcp.md](site/mcp.md)).

The pages lag the service, and the service decides. Where they disagree,
the guides follow what a kernel measured:

| Page statement | Service behavior | Authority |
| --- | --- | --- |
| The TPU is a TPU v3-8 with 8 cores and 128 GB of TPU memory ([site/tpu.md](site/tpu.md), [site/notebooks.md](site/notebooks.md)) | the accelerator list offers TpuV5E8 and TpuV6E8 only | [cli/kernels.md](cli/kernels.md), [tpu-research.md](tpu-research.md) |
| No page names an identity requirement for TPUs | the notebook editor's session panel reads "Some accelerators, such as TPUs, require identity verification"; every TPU request from an account without Persona verification ran on the 4-core CPU image | [tpu-research.md](tpu-research.md) |
| The free GPU is one Tesla P100 ([site/efficient-gpu-usage.md](site/efficient-gpu-usage.md), [site/notebooks.md](site/notebooks.md) "Using a GPU") | `NvidiaTeslaT4` gives 2 x T4; the same notebooks page also specifies the T4 x2 shape | [substrates.md](substrates.md) |
| Interactive sessions stay alive until a 60-minute idle timeout ([site/efficient-gpu-usage.md](site/efficient-gpu-usage.md)) | 20 idle minutes end an interactive session ([site/notebooks.md](site/notebooks.md) "Idle time") | the shorter limit binds a plan |
| A GPU session waits only when a queue forms (notebooks "Using a GPU") | a third concurrent GPU batch push is refused with "Maximum batch GPU session count of 2 reached", whatever weekly quota is left; quota and concurrency are separate limits | [workflow.md](workflow.md) |

`kaggle_kernel/AGENTS.md` is the instruction file that travels inside each
kernel, and `kaggle_kernel/kernel_main.py` is the program every kernel runs.
