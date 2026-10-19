> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/readme.html](https://docs.iqm.tech/4.7/iqm-qaoa/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6d46cbcee9b367ef4a2d016bbfcfe2a8cf6c4d74def3c6d5c5e7fa8ae59d7d65.

# iqm-qaoa

A Python library for setting up and running QAOA (Quantum Approximate Optimization Algorithm) experiments on [IQM](https://iqm.tech/) quantum computers.

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-qaoa
```

### Optional extras

The following optional extras are available:

- `notebook`: Jupyter notebook support for running example notebooks

All extras are inter-compatible and each adds more dependencies on top of the base install. To install all of them:

``` bash
uv pip install "iqm-qaoa[notebook]"
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

These can be combined with other extras. The following combined extras are available:

- `notebook-pin-iqm`

- `notebook-pin-all`

For example:

``` bash
uv pip install "iqm-qaoa[notebook-pin-all]"
```

All extras are inter-compatible, so you can combine multiple extras with pinning as needed.

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
