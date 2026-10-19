> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/readme.html](https://docs.iqm.tech/4.7/iqm-data-definitions/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 742131df4d176f41964d8e2f81c3bd607149010800a0a588a4e595eb91ba0e15.

# iqm-data-definitions

A common place for data definitions shared inside IQM. The package is meant to stay independent of any other IQM project, so that everything in the control software stack can depend on it. Concretely it contains:

- The Protobuf message formats (`protos/`) used by the quantum computer control software stack, and the serialization code generated from them (`src/iqm/data_definitions/`).

- Hand-written Python-native representations of some of those messages (`src/iqm/models/`).

## Protocol versioning

Breaking changes to data definitions require a major version update. Major versions are described in the directory paths inside `protos/`. For instance, version 1.x Protobuf definitions live in `protos/iqm/data_definitions/<subpackage>/v1/*.proto`, and there can be several subpackages per version.

Backwards-compatible changes are handled as minor version upgrades. Minor versions are not part of the path, only of the package version: version 1.2 Protobuf definitions live in the same place as version 1.1 ones, but the distributable packages differ. The generated Python code is importable as `iqm.data_definitions.<subpackage>.v1.*_pb2`.

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-data-definitions
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

For example:

``` bash
uv pip install "iqm-data-definitions[pin-all]"
```

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
