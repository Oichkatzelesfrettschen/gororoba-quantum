> Full piece: [https://docs.qbraid.com/v2/cli/user-guide/environments.md](https://docs.qbraid.com/v2/cli/user-guide/environments.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 33529cc77de4f8a83de3d627d09e35786c436865adee532ea28d2b7f9daedb42.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# Environments

qBraid environments are simply [Python virtual environments](https://docs.python.org/3/library/venv.html) in disguise.
The qBraid CLI provides convenient short-cuts to activate and install packages into your qBraid environments, however all
of the traditional commands to activate and manipulate Python venvs still apply. For example, you can activate an
environment using the [source command](https://docs.python.org/3/library/venv.html#how-venvs-work):

```bash
$ source ~/.qbraid/environments/<slug>/pyenv/bin/activate
```

If you're working in terminal, you don't specifically need to activate a qBraid environment, as you can just specify the full path
to that environment's Python interpreter when invoking Python, e.g. `/<path-to-venv>/bin/python`. The same is true for `pip` commands.
So if you are attempting to install new packages into a qBraid environment from terminal or inside a notebook, make sure to use the full
pip path.

Simply running `pip install ...` will default to `/opt/conda/bin/pip`, which will cause dependency conflicts, and the installed packages
will be overridden the next time you launch lab.

### Install package

From Launcher, under “Other”, click on Terminal. By default, your qBraid terminal opens using Python (and pip) from
`/opt/conda/bin`. Packages that are installed directly at this top-level will _not_ persist between sessions. Instead,
use the qBraid CLI to list your environments,

```bash
$ qbraid envs list
# qbraid environments:
#

default                        /opt/.qbraid/environments/qbraid_000000
qsharp                         /opt/.qbraid/environments/qsharp_b54crn
qbraid_sdk                     /home/jovyan/.qbraid/environments/qbraid_sdk_9j9sjy
qiskit                         /home/jovyan/.qbraid/environments/qiskit_9y9siy
```

activate an environment, and perform your pip installs from there. For example, installing pytket into the qiskit environment:

```bash
$ qbraid envs activate qiskit
$ python -m pip install pytket
$ deactivate
```
