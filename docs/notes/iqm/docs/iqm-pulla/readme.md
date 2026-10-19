> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/readme.html](https://docs.iqm.tech/4.7/iqm-pulla/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 acc58272d7f631e93ef1e2d9f1c72a114062aab6db22f4021fda00802aec320f.

# iqm-pulla

Pulla (pulse-level access) is a client-side Python library which enables the generation and execution of pulse-level jobs on an [IQM](https://iqm.tech/) quantum computer. Within the existing IQM QCCSW stack, Pulla is somewhere between circuit-level execution and EXA experiments.

An interactive user guide is available as a Jupyter notebook in the `docs` folder.

## Testing

If you want to run a particular notebook and see the output cells printed in the terminal, you can use `nbconvert` with [`jq`](https://jqlang.github.io/jq/download/) like so:

``` bash
jupyter nbconvert --to notebook --execute  "docs/Quick Start.ipynb" --stdout |
  jq -r '.cells[] | select(.outputs) | .outputs[] | select(.output_type == "stream") | .text[]'
```

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-pulla
```

### Optional extras

The following optional extras are available:

- `notebook`: Jupyter notebook support for running example notebooks

- `qir`: QIR (Quantum Intermediate Representation) support

All extras are inter-compatible and each adds more dependencies on top of the base install. To install all of them:

``` bash
uv pip install "iqm-pulla[notebook,qir]"
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

These can be combined with other extras. The following combined extras are available:

- `notebook-pin-iqm`

- `qir-pin-iqm`

- `notebook-pin-all`

- `qir-pin-all`

For example:

``` bash
uv pip install "iqm-pulla[notebook-pin-all]"
```

All extras are inter-compatible, so you can combine multiple extras with pinning as needed.

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
