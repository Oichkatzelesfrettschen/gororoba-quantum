# Kaggle guides

Kaggle kernels run every simulation of 14 qubits or fewer (root AGENTS.md,
"QPU time and calibration"). These guides play the role
`docs/notes/ibm_quantum/` plays for IBM hardware:

| Guide | Content |
| --- | --- |
| [workflow.md](workflow.md) | `scripts/kaggle_run.py` push, status and collect; authentication; how a result enters the research state |
| [substrates.md](substrates.md) | measured CPU, RAM, disk, GPU, TPU and qubit limits of each machine shape, and what runs on which substrate |
| [hypercomplex-stack.md](hypercomplex-stack.md) | the eight hypercomplex packages built and proved identically on the host and in every kernel |
| [interfaces.md](interfaces.md) | every CLI command, kagglesdk method and MCP tool, mapped onto shared operations; which call addresses which kernel version, where a session id comes from, how a session is cancelled; accelerator fields, authentication and the host's MCP permission policy |
| [tpu-research.md](tpu-research.md) | every TPU request route measured on this account, the server record of each version, the markers that decide whether a session is a TPU VM, the root-cause analysis and its sources, and the push procedure |
| [libraries.md](libraries.md) | the Kaggle PyPI packages: kaggle, kagglesdk and kagglehub as installed Arch packages with their recipes and run examples, the packages left out and why, and what a kernel image carries |

## Captured Kaggle documentation

`scripts/capture_kaggle_docs.py` keeps Kaggle's own documentation here, each
file under a header naming its URL, retrieval time and digest, with
`MANIFEST.json` in each directory (gate core-283 rechecks the bytes):

| Directory | Source | Content |
| --- | --- | --- |
| [site/](site/) | kaggle.com/docs, rendered in headless Chromium and converted with pandoc | [notebooks](site/notebooks.md) (session resources and limits), [tpu](site/tpu.md), [api](site/api.md) (auth, OAuth scopes, rate limits), [mcp](site/mcp.md) (every MCP tool's request and response), [models](site/models.md), [datasets](site/datasets.md), [packages](site/packages.md), [benchmarks](site/benchmarks.md) |
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

`kaggle_kernel/AGENTS.md` is the instruction file that travels inside each
kernel, and `kaggle_kernel/kernel_main.py` is the program every kernel runs.
