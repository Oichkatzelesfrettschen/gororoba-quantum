> Full piece: [https://docs.qbraid.com/v2/cli/user-guide/magic-commands.md](https://docs.qbraid.com/v2/cli/user-guide/magic-commands.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 6e6d80f10c77059b44acf8d85afc38186b5b0f86a74d30e621ace7410531990d.

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

# Magic Commands

You can access the CLI directly from within [Notebooks](https://docs.qbraid.com/v2/lab/user-guide/notebooks)
using IPython [magic commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html). First, configure
the qBraid magic command extension using:

```shell
$ qbraid configure magic
```

The above command can also be executed from within a Jupyter notebook using the `!` operator. Then, from within a
notebook cell, load the qBraid magic IPython extension using:

```python
In [1]: %load_ext qbraid_magic
```

Now you can continue to use the qBraid-CLI as normal from within your Jupyter notebook using the magic `%` operator, e.g.

```python
In [2]: %qbraid

In [3]: %qbraid --version
```
