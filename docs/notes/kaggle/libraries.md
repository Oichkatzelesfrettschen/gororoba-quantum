# Kaggle Python packages

Three Kaggle packages serve this repository from the build host: the
`kaggle` CLI, the generated `kagglesdk` client underneath it, and
`kagglehub`. Each is an Arch package at the version below, and the CLI
pulls in jupytext and python-dotenv. Three more Kaggle packages exist on
PyPI and stay uninstalled because none of their functions is a job here.
[interfaces.md](interfaces.md) maps the operations each one exposes.

## Installed on the build host

| PyPI distribution | Import | Version | Arch package | Recipe | Role here |
| --- | --- | --- | --- | --- | --- |
| kaggle | `kaggle` (command `kaggle`) | 2.2.4 | kaggle-api 2.2.4-2 | `~/Github/PKGBUILDs/kaggle-api` | `scripts/kaggle_run.py` push, status, collect and dataset; `scripts/kaggle_sessions.py` kernel id lookup |
| kagglesdk | `kagglesdk` | 0.1.37 | python-kagglesdk 0.1.37-1 | AUR | the HTTP client the CLI and kagglehub call; direct use for version-labeled reads, quota and session calls |
| kagglehub | `kagglehub` | 1.0.2 | python-kagglehub 1.0.2-1 | `~/Github/PKGBUILDs/python-kagglehub` | identity checks, cached dataset and model downloads, version-pinned notebook output |
| jupytext | `jupytext` | 1.19.6 | python-jupytext 1.19.6-1 | `~/Github/PKGBUILDs/python-jupytext` | CLI dependency |
| python-dotenv | `dotenv` | 1.2.4 | python-dotenv 1.2.4-1 | Arch extra | CLI dependency |

Why the local recipes exist:

- **kaggle-api.** kaggle 2.2.4 declares `jupytext` and `python-dotenv` in
  its `Requires-Dist`, and the AUR recipe (2.2.4-1) omits both. The local
  recipe is pkgrel 2 with the two added. `kaggle.api.kaggle_api_extended`
  imports `dotenv` at module load, so without it every CLI command fails;
  it imports jupytext inside `_convert_py_to_notebook`, which `benchmarks
  tasks push` uses to turn a percent-format script into a notebook, and its
  YAML settings loader for `competitions settings update` relies on PyYAML
  arriving through jupytext.
- **python-jupytext.** The AUR recipe builds the JupyterLab extension from
  source with corepack, which fetches an unpinned yarn at build time. The
  local recipe installs the released `jupytext-1.19.6-py3-none-any.whl`,
  which already carries the prebuilt extension, under a pinned sha256.
- **python-kagglehub.** The AUR has no kagglehub package; the local recipe
  builds the PyPI sdist under a pinned sha256 with the pandas and polars
  adapters as optional dependencies.
- **python-kagglesdk** builds from the AUR recipe unchanged: the PyPI sdist
  under a pinned sha256, depending on python-requests and python-protobuf.

A broken or missing package is rebuilt the way docs/notes/build_host/python-stack.md
prescribes for the Python stack: python-kagglesdk first, from the AUR
through paru, since `~/Github/PKGBUILDs` holds no recipe for it; then
`makepkg -si --nocheck` in `~/Github/PKGBUILDs/python-jupytext`,
`kaggle-api` and `python-kagglehub`, in that order.

## kaggle: the CLI

`scripts/kaggle_run.py` runs every Kaggle job through the CLI, and
`kaggle quota` reads the weekly accelerator quota:

```sh
kaggle quota
```

```text
resource  used    remaining  total   refreshAt
GPU       16.80h  13.20h     30.00h  2026-10-17T00:00:00
TPU       0.00h   20.00h     20.00h  2026-10-17T00:00:00
```

The table carries no reserved time, which a running accelerator session
holds, and `kernels status`, `kernels output`, `kernels logs` and
`kernels pull` answer for the latest version whatever `/N` suffix they are
given ([interfaces.md](interfaces.md), "Findings for running and stopping
kernels").

## kagglesdk: the generated client

kagglesdk holds one client class per Kaggle service, each method sending
its request type as JSON to `https://api.kaggle.com/v1/<service>/<Rpc>`.
Authenticating through the CLI's `KaggleApi` reuses its credentials:

```python
from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import (
    ApiGetAcceleratorQuotaStatisticsRequest,
    ApiGetKernelRequest,
)

api = KaggleApi()
api.authenticate()
with api.build_kaggle_client() as kaggle:
    kernels = kaggle.kernels.kernels_api_client
    quota = kernels.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
    print(quota.gpu_quota.time_used, quota.gpu_quota.time_reserved, quota.quota_refresh_time)

    request = ApiGetKernelRequest()
    request.user_name = "probablyeric"
    request.kernel_slug = "gororoba-atlas-detuning-map"
    request.version_label = "v3"  # "vN"; a bare "3" answers HTTP 404
    print(kernels.get_kernel(request).metadata.current_version_number)
```

Measured on 2026-10-16: GPU 16.8 h used, 0 h reserved, 30 h allowed, refresh
2026-10-17 00:00 UTC; `get_kernel` with `v3` returned version 3 of a kernel
whose latest version is 8. `kaggle.models.model_api_client.list_model_instances`
for `google/gemma-4` returned 20 variations.

## kagglehub: cached downloads

kagglehub resolves a handle to files in a local cache (or `output_dir`) and
returns the path. Its notebook handles take a version,
`OWNER/SLUG/versions/N`, which `notebook_output_download` sends as the
integer `version_number` of `DownloadKernelOutput`, so it fetches the named
version's output where the CLI fetches the latest.

```python
import kagglehub

print(kagglehub.whoami())  # {'username': 'probablyeric'}
path = kagglehub.dataset_download("uciml/iris", path="Iris.csv", output_dir=SCRATCH)
```

The download wrote `Iris.csv`, 5107 bytes, sha256 prefix
`600ac44f23c2e6e0`. Other entry points: `model_download`,
`competition_download`, `notebook_output_download`, `dataset_load` (pandas,
polars or Hugging Face adapters), `dataset_upload`, `model_upload`,
`package_import` and `utility_script_install`.

## Not installed

| PyPI distribution | Latest | What it is | Why it stays out |
| --- | --- | --- | --- |
| kaggle-environments | 1.33.0 (2026-10-02) | Kaggle's simulation-competition environments and agent runners | game simulation is no job here, and it pulls jax, gymnasium 1.2.0, gymnax, open_spiel 2.0.1, pettingzoo, pygame, Flask, transformers and litellm |
| kaggle-benchmarks | 0.6.1 (2026-06-17) | authoring and running LLM benchmark tasks | LLM benchmarks are no job here; it needs docker, google-genai, openai, playwright, panel and jupyter, and its `protobuf<6.0` pin conflicts with the protobuf 7.36.1 kagglesdk runs on; the CLI's `benchmarks` group already reaches the service |
| kaggle-mcp | 0.1.0 (2025-03-20) | a third-party stdio MCP server wrapping `kaggle>=1.7.4.2` | Kaggle's official server at `https://www.kaggle.com/mcp` supersedes it with 76 tools and token authentication |

## Inside a Kaggle kernel

No retained record states which Kaggle packages a kernel image carries.
`kaggle_kernel/kernel_main.py` writes `environment.json` from
`REPORTED_PACKAGES` (numpy, scipy, sympy, pandas, torch, qiskit, Aer and the
hypercomplex stack), so neither `results/kaggle/*/output/output/environment.json`
nor `docs/evidence/*/kaggle_environment.json` names kaggle, kagglesdk,
kagglehub, kaggle-environments or jupytext. Kaggle's image recipe,
`kaggle_requirements.txt` in github.com/Kaggle/docker-python at commit
e096cbc (read 2026-10-16 for this note), lists `kaggle>=1.8.3`,
`kaggle-environments` and `kagglehub[pandas-datasets,hf-datasets,signing]>=0.4.2`
without pins, and the image digests the runs record are not bound to that
commit, so the versions inside a kernel are unknown until a run records
them. The kernel program needs none of them: it writes to
`/kaggle/working`, and the host's CLI retrieves the output. Inside a
Kaggle notebook kagglesdk and kagglehub read the token file the
`KAGGLE_API_V1_TOKEN` environment variable names before any other
credential (`kagglesdk.kaggle_env.get_access_token_from_env`).
