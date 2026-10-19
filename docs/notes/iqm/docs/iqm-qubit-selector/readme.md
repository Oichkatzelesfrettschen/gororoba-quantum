> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/readme.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f6d86b05a38c6aaeec9124f5de933e884b5ee543ee629eb8f45c9949474cd315.

# iqm-qubit-selector

Helps in automatically selecting the best layouts for IQM’s quantum computers.

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-qubit-selector
```

### Optional extras

The following optional extras are available:

- `notebook`: Jupyter notebook support for running example notebooks

All extras are inter-compatible and each adds more dependencies on top of the base install. To install all of them:

``` bash
uv pip install "iqm-qubit-selector[notebook]"
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
uv pip install "iqm-qubit-selector[notebook-pin-all]"
```

All extras are inter-compatible, so you can combine multiple extras with pinning as needed.

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
