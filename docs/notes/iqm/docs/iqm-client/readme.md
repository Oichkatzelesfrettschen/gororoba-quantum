> Full piece: [https://docs.iqm.tech/4.7/iqm-client/readme.html](https://docs.iqm.tech/4.7/iqm-client/readme.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c34d1ba01d8df9b9992e82c22b0e29f0b91d704236bef5d5d1eb09891db37c19.

# iqm-client

Client-side Python library for connecting to an [IQM](https://iqm.tech/) quantum computer.

Includes as optional features [Qrisp](https://www.qrisp.eu/), [Qiskit](https://qiskit.org/) and [Cirq](https://quantumai.google/cirq) adapters for IQM’s quantum computers, which allow you to:

- Transpile arbitrary quantum circuits for IQM quantum architectures

- Simulate execution on IQM quantum architectures with IQM-specific noise models (currently only the Qiskit adapter contains IQM noise models)

- Run quantum circuits on an IQM quantum computer

## Migration from legacy packages

If you have previously installed the (now obsolete) `qiskit-iqm` or `cirq-iqm` packages in your Python environment, you should first uninstall them:

``` bash
uv pip uninstall qiskit-iqm cirq-iqm
```

Then reinstall `iqm-client` with the `--force-reinstall` option to ensure a clean state:

``` bash
uv pip install --force-reinstall "iqm-client[qiskit,cirq]"
```

## Installation

> **Note:** [uv](https://docs.astral.sh/uv/) is highly recommended for practical Python environment and package management. The supported Python versions are
>
> > =3.11, \<3.15.

``` bash
uv pip install iqm-client
```

### Optional extras

The following optional extras are available:

- `cirq`: Cirq adapter for IQM quantum computers

- `qiskit`: Qiskit adapter for IQM quantum computers

- `qrisp`: Qrisp adapter for IQM quantum computers

All extras are inter-compatible and each adds more dependencies on top of the base install. To install all of them:

``` bash
uv pip install "iqm-client[cirq,qiskit,qrisp]"
```

### Reproducible installations

For reproducible installations, pinned dependency extras are available:

- `pin-iqm`: pins inter-IQM package dependencies to exact co-released versions.

- `pin-all`: like `pin-iqm`, but additionally pins all transitive third-party dependencies.

These can be combined with other extras. The following combined extras are available:

- `cirq-pin-iqm`

- `qiskit-pin-iqm`

- `qrisp-pin-iqm`

- `cirq-pin-all`

- `qiskit-pin-all`

- `qrisp-pin-all`

For example:

``` bash
uv pip install "iqm-client[cirq-pin-all]"
```

All extras are inter-compatible, so you can combine multiple extras with pinning as needed.

> **Note:** This package was tested at release time for clean installation with `uv 0.11.20` and `pip 25.1.1`. Other versions are likely to work but are not verified per release.
