> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/readme.html](https://docs.iqm.tech/4.7/iqm-pulse/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e47475b92a36f9159f786e30e9d96366a8d036b399d334897a3eb5fa6cf17777.

# iqm-pulse

A Python library for building pulse-level instruction schedules for quantum computers, and for compiling quantum circuits into instruction schedules.

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-pulse
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

For example:

``` bash
uv pip install "iqm-pulse[pin-all]"
```

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
