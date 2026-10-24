> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/notebooks.md](https://docs.qbraid.com/v2/lab/user-guide/notebooks.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 7457d6c587a32a9d030f935bf3bb616461130a6c620785629e1fbebf95434d61.

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

# Notebooks

Jupyter Notebooks (`.ipynb` files) are a community standard for communicating and performing interactive computing. They are documents that combine live runnable code with narrative text (Markdown), equations (LaTeX), images, interactive visualizations and other rich output.

qBraid Lab provides an interface to create and interact with Jupyter Notebooks, and includes a number of additional key features and integrations to enhance the quantum developer's experience.

## Create notebook

Create a notebook by clicking the `+` button in the file browser and then selecting a kernel in the new Launcher tab. In the Launcher tab, under **Notebooks**, clicking on an ipykernel associated with an activated environment will automatically launch a Jupyter notebook (`.ipynb` file) using that kernel.

<Info>
  The notebook document format used in qBraid Lab is the same as in the classic
  Jupyter Notebook. For more on how to use Jupyter Notebooks, see [Jupyter
  Notebooks](https://jupyter-notebook.readthedocs.io/en/stable/) and [Jupyter
  Lab:
  Notebooks](https://jupyterlab.readthedocs.io/en/stable/user/notebook.html).
</Info>

## Switch notebook kernel

In the upper-right of any open notebook, you can see which kernel is in use. Clicking on the name of the current kernel, will open the kernel selector, and allow you switch to any other active kernel.

<Frame>
  <video
    src="https://storage.googleapis.com/qbraid-static-assets/qbraid-docs/lab/switch-kernel.mp4"
    autoPlay
    muted
    loop
    playsInline
    width="100%"
  />
</Frame>

## Pip (magic) commands

From inside a notebook, you must run all pip commands using the “magic” `%` operator.
For example, to install a new package from within a notebook cell, use:

```python
[ ] %pip install <my-package>
```

<Warning>
  WARNING: **Do not** use the `!` operator for pip install commands within
  Jupyter notebooks on qBraid. Doing so will install packages at the
  system-level, where they will _not_ be discoverable by your current notebook
  environment/kernel.
</Warning>

After installing any new packages directly from a notebook, you _must_ restart the kernel to see the changes take effect.
