"""Check that the Rocq replay job, its pins and the replay bundles name one toolchain and one path set.

The ci.yml job rocq-replay builds the opam switch of ci/rocq_toolchain.pin and
runs scripts/rocq_kaggle_replay.py against it. Each bundle's toolchain.txt is
the banner ``rocq --version`` must print, so the compiler and Rocq versions of
the pin, the constants OCAML, ROCQ_PACKAGES and SWITCH of the replay driver and
those banners agree. The open_gororoba fetch in the workflow covers every
directory a bundle's source_hashes.sha256 lists, and ci/rocq_changed.sh selects
every bundle directory with a replay_rocq.sh. tests/ci/test_rocq_ci_pins.py
mutates a copy of the inputs and requires each mutation to fail the check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEX40 = re.compile(r"[0-9a-f]{40}")
FIXED_FILES = (
    "ci/rocq_toolchain.pin",
    "ci/open_gororoba.pin",
    "ci/rocq_changed.sh",
    "ci/install_rocq.sh",
    "ci/fetch_open_gororoba.sh",
    "scripts/rocq_kaggle_replay.py",
    ".github/workflows/ci.yml",
    "ci/gates.json",
)


def bundles(root: Path) -> list[str]:
    return sorted(path.parent.name for path in (root / "docs/evidence").glob("*/replay_rocq.sh"))


def constant(source: str, name: str) -> str:
    match = re.search(rf"^{name} = (.+)$", source, re.MULTILINE)
    if match is None:
        raise ValueError(f"scripts/rocq_kaggle_replay.py defines no {name}")
    return match.group(1)


def read_pin(root: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in (root / "ci/rocq_toolchain.pin").read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        fields[key] = value
    return fields


def check(root: Path) -> list[str]:
    errors: list[str] = []
    pin = read_pin(root)
    for key in ("switch", "compiler", "packages", "opam_repository"):
        if not pin.get(key):
            errors.append(f"ci/rocq_toolchain.pin lacks {key}")
    if errors:
        return errors
    if not HEX40.fullmatch(pin["opam_repository"]):
        errors.append("opam_repository is not a 40-digit commit")
    driver = (root / "scripts/rocq_kaggle_replay.py").read_text(encoding="utf-8")
    if constant(driver, "OCAML") != f'"{pin["compiler"]}"':
        errors.append("OCAML of the replay driver differs from the pin compiler")
    if constant(driver, "SWITCH") != f'"{pin["switch"]}"':
        errors.append("SWITCH of the replay driver differs from the pin switch")
    packages = tuple(pin["packages"].split())
    if constant(driver, "ROCQ_PACKAGES") != "(" + ", ".join(f'"{p}"' for p in packages) + ")":
        errors.append("ROCQ_PACKAGES of the replay driver differs from the pin packages")
    ocaml_version = pin["compiler"].split(".", 1)[1]
    package_versions = dict(package.split(".", 1) for package in packages)
    if set(package_versions) != {"rocq-core", "rocq-runtime", "rocq-stdlib"}:
        errors.append("the pin must name rocq-core, rocq-runtime and rocq-stdlib")
    elif package_versions["rocq-core"] != package_versions["rocq-runtime"]:
        errors.append("rocq-core and rocq-runtime must carry the same version")
    else:
        # Stdlib releases independently; the prover banner identifies rocq-core.
        expected = f"The Rocq Prover, version {package_versions['rocq-core']}\ncompiled with OCaml {ocaml_version}\n"
        names = bundles(root)
        if not names:
            errors.append("no docs/evidence bundle carries a replay_rocq.sh")
        for name in names:
            banner = (root / f"docs/evidence/{name}/toolchain.txt").read_text(encoding="utf-8")
            if banner != expected:
                errors.append(f"docs/evidence/{name}/toolchain.txt is {banner!r}, the pin implies {expected!r}")
    if not HEX40.fullmatch((root / "ci/open_gororoba.pin").read_text(encoding="utf-8").strip()):
        errors.append("ci/open_gororoba.pin is not a 40-digit commit")
    workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for needle in (
        "ci/install_rocq.sh",
        "hashFiles('ci/rocq_toolchain.pin'",
        "ripgrep",
        "command -v rg",
        "needs.changes.outputs.rocq == 'true'",
        "ci/rocq_changed.sh",
        "--rocq ",
        "ci/open_gororoba.pin",
    ):
        if needle not in workflow:
            errors.append(f"ci.yml lacks {needle!r}")
    fetched = set(re.findall(r"^\s+((?:proofs|crates)[^\s]*)$", workflow, re.MULTILINE))
    for name in bundles(root):
        hashes = root / f"docs/evidence/{name}/source_hashes.sha256"
        script = (root / f"docs/evidence/{name}/replay_rocq.sh").read_text(encoding="utf-8")
        if not hashes.exists() or "GOROROBA_ROOT" not in script:
            continue
        directories = {
            line.split(None, 1)[1].strip().rpartition("/")[0]
            for line in hashes.read_text().splitlines()
            if line.strip()
        }
        for directory in sorted(directories):
            if not any(directory == cone or directory.startswith(cone + "/") for cone in fetched):
                errors.append(f"the ci.yml fetch does not cover {directory}, which {name} hashes")
    selector = (root / "ci/rocq_changed.sh").read_text(encoding="utf-8")
    required = [f"docs/evidence/{name}/*" for name in bundles(root)]
    required += ["proofs/*", "scripts/rocq_kaggle_replay.py", "ci/open_gororoba.pin", "ci/rocq_toolchain.pin"]
    required += [".github/workflows/ci.yml", "docs/evidence/rocq_kaggle_replay/*", "gororoba_quantum/parallel.py"]
    for pattern in required:
        if pattern not in selector:
            errors.append(f"ci/rocq_changed.sh lacks {pattern}")
    excluded = json.loads((root / "ci/gates.json").read_text(encoding="utf-8"))["excluded"]
    for name in ("c881_exhaustive", "stiefel_witness"):
        entries = [e for e in excluded if f"docs/evidence/{name}/replay_rocq.sh" in e["cmd"]]
        if len(entries) != 1:
            errors.append(f"ci/gates.json excludes no {name} replay")
        elif "ci.yml job rocq-replay" not in entries[0]["reason"]:
            errors.append(f"the excluded {name} replay does not name the ci.yml job rocq-replay")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args()
    errors = check(ROOT)
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print(f"rocq ci pins agree across {len(bundles(ROOT))} bundles")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
