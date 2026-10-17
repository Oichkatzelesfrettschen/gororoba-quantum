# The hypercomplex package stack on every substrate

`gororoba_quantum/cd_core.py` is the algebra's specification. Sixteen
external packages are measured against it (`docs/notes/packages/README.md`):
the Cayley-Dickson packages, three quaternion classes, three Clifford
algebra packages read through Cl(0,2), and two further octonion and sedenion
implementations. The same sixteen run identically on the build host and in
every Kaggle kernel.
IBM jobs run circuits only; the algebra that builds those circuits runs on
the host, so the host stack is the one that shapes an IBM run.

## One authority, three builds

`scripts/algebra_package_tables.py` holds the pins: `RELEASES` (version and
sha256 of each PyPI sdist or GitHub archive), `ARCHIVE_URLS`,
`BUILD_RECIPES` (the `prepare()` step of the cayley-dickson, SplitOct and
pyquaternion PKGBUILDs, transcribed byte for byte) and `RUNTIME_PINS`
(numpy-quaternion 2024.0.13 as its compiled wheel, and numba 0.68.0,
sparse 0.17.0 and anywidget 0.11.0 for quaternionic, clifford and kingdon,
each at the build host's Arch package version). Octonion-Sedenion is
published only as a wheel, which `--install` installs as it is.

| Substrate | How the stack is built | How it is proved |
| --- | --- | --- |
| Build host (Arch) | Arch packages from `~/Github/PKGBUILDs`, `makepkg -si --nocheck` | `--fetch DIR` then `--extract DIR`: the regenerated `docs/evidence/algebra_packages/tables.json` must equal the retained bytes |
| Kaggle kernel | `--fetch` and `--install` in `kaggle_kernel/kernel_main.py`: sha256-checked archives, recipes applied, `pip install --no-deps` | the same `--extract` byte comparison; the kernel exits with code 3 before its entry on any difference (`hypercomplex.json`) |
| GitHub Actions | no package installed | `--check` (gates sources-216 and sources-217) re-derives every retained table's relation to `cd_core` |

`--extract` binds each installed distribution to its archive: exactly one
archive carries the pinned sha256, the installed version equals the pin,
and every installed `.py` file is byte-identical to an archive member
except the declared `cayley_dickson/__init__.py` shim. The tables it then
reads, and the seeded product samples up to dimension 4096, are what the
byte comparison covers, so two substrates that pass ran the same algebra
code with the same results.

## What does not travel

- **SageMath 10.10** is a build-host package. Its octonion table is a
  retained export (`docs/notes/packages/sagemath.md`); a computation that
  needs Sage runs on the host.
- **numpy, scipy, sympy, pandas and torch** come from the Kaggle image, at
  the versions each run records in `environment.json`. The extracted tables
  are exact signs and indices, so these versions do not enter the byte
  comparison; a design whose floating-point results depend on them states
  that and replays on the CPU under the repository pins.

## When a pin changes

A new release or commit changes `RELEASES` and, where the PKGBUILD's
`prepare()` changes, `BUILD_RECIPES`; the PKGBUILD in `~/Github/PKGBUILDs`
changes with it. The host rebuilds the Arch package, `--extract` regenerates
`tables.json`, and the next kernel proves the new stack against those bytes.
