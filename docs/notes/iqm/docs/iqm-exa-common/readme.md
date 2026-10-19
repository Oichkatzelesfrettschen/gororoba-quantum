> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/readme.html](https://docs.iqm.tech/4.7/iqm-exa-common/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a7c57dab684576d3fbbf272672bf04c29e0455e8ebef748efcddb01949c973b.

# iqm-exa-common

A Python library containing shared types, classes, helper functions etc. that are used in other IQM OS packages.

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-exa-common
```

### Optional extras

The following optional extras are available:

- `notebook`: Interactive Jupyter notebook integration support

All extras are inter-compatible and each adds more dependencies on top of the base install. To install all of them:

``` bash
uv pip install "iqm-exa-common[notebook]"
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
uv pip install "iqm-exa-common[notebook-pin-all]"
```

All extras are inter-compatible, so you can combine multiple extras with pinning as needed.

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
