# Verified Aer CPU rollback package

The retained `python-qiskit-aer 0.17.2-3` archive contains the tested CPU
implementation. Its package metadata requires `blas-openblas`, while the
workstation's `openblas` package owns `libopenblas.so.0` and supplies no
`blas-openblas` alias. The rollback package corrects that dependency and
sets package release 4. Its conflict with `python-qiskit-aer-cuda` lets
pacman replace the CUDA variant during a rollback transaction.

The PKGBUILD extracts the checksum-pinned original package directly. It
preserves installed files, bytecode, extension binaries, permissions, links,
and timestamps. makepkg regenerates `.PKGINFO`, `.BUILDINFO`, and `.MTREE`.
Stripping and payload-removal options stay disabled. The operation compiles
zero sources and installs zero packages. The original archive remains
untouched. Binary archives belong in local build storage, outside Git.

From the repository root, set `CPU_ARCHIVE` to the retained package archive.
The commands below create an isolated build directory under temporary
storage, build the corrected package, verify payload equality, and confirm
that its dependencies resolve against the installed package database:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  : "${CPU_ARCHIVE:?set CPU_ARCHIVE to the retained 0.17.2-3 CPU package archive}"
  CPU_ARCHIVE="$(realpath "$CPU_ARCHIVE")"
  rollback_build="$(mktemp -d /tmp/qiskit-aer-cpu-rollback.XXXXXX)"
  cp packaging/qiskit-aer-cuda/rollback/PKGBUILD "$rollback_build/PKGBUILD"
  ln -s "$CPU_ARCHIVE" "$rollback_build/python-qiskit-aer-0.17.2-3-x86_64.pkg.tar.zst"
  (
    cd "$rollback_build"
    SOURCE_DATE_EPOCH=1791618281 SRCDEST="$PWD" PKGDEST="$PWD" \
      SRCPKGDEST="$PWD" LOGDEST="$PWD" BUILDDIR="$PWD" makepkg --cleanbuild
  )
  rollback_package="$rollback_build/python-qiskit-aer-0.17.2-4-x86_64.pkg.tar.zst"
  "$PYTHON" packaging/qiskit-aer-cuda/rollback/verify_payload.py \
    "$CPU_ARCHIVE" "$rollback_package" --installed-root / --check \
    >"$rollback_build/payload-verification.json"
  pacman -T openblas python-dateutil python-numpy python-psutil python-qiskit python-sympy
  printf '%s\n' "$rollback_package"
)
```

`SOURCE_DATE_EPOCH` preserves the original payload timestamp. makepkg also
uses that value in generated archive metadata; the timestamp describes
source reproducibility, rather than the wall-clock repackaging date.
`--installed-root /` additionally compares the retained extension with the
installed CPU extension before CUDA installation. Omit that option after
CUDA installation; the two package archives remain the payload authority.
The `--check` option exercises six rejection cases in temporary storage.
The verifier requires Python 3.14's standard-library Zstandard support.

The installation owner retains the artifact path and its verification report.
A later rollback uses a normal pacman package transaction, with the exact
verified package path:

```sh
SUDO_ASKPASS=/usr/bin/unified-askpass sudo -A pacman -U "$ROLLBACK_PACKAGE"
```

The transaction restores the CPU package and resolves the explicit CUDA
package conflict. The installation owner confirms `pacman -Qkk
python-qiskit-aer`, the import path, the extension digest, and
`AerSimulator().available_devices()` afterward. The expected CPU extension
SHA-256 is
`758db4f3d2d81902f938d15605bd63e206e3fa3404fea8564c71b81100457a32`.
The verifier checks every payload entry and rejects changed source archives,
changed payload bytes, missing entries, and incorrect dependency metadata.

The verifier's type gate names its required Python version explicitly:

```sh
mypy --python-version 3.14 --strict packaging/qiskit-aer-cuda/rollback/verify_payload.py
```

The repository's simulator modules retain their separate Python target.
