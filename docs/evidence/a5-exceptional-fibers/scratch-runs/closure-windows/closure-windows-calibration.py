"""Calibrate one registered modular root from a manifest-verified closure snapshot."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import lzma
import os
import platform
import re
import subprocess
import sys
import sysconfig
import time
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", required=True)
    parser.parse_args()
    manifest_bytes = (ROOT / "transport-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    for entry in manifest["files"]:
        relative = PurePosixPath(entry["path"])
        require(
            not relative.is_absolute() and ".." not in relative.parts and str(relative) == entry["path"],
            "manifest input path is unsafe",
        )
        path = ROOT / entry["path"]
        require(path.is_file() and not path.is_symlink(), "manifest input is absent or is a symlink")
        payload = path.read_bytes()
        require(
            len(payload) == entry["bytes"] and hashlib.sha256(payload).hexdigest() == entry["sha256"],
            "manifest input bytes differ: " + entry["path"],
        )
    versions = {name: importlib.metadata.version(name) for name in ("python-flint", "sympy", "passagemath-singular")}
    require(versions == manifest["expected_runtime"]["packages"], "runtime package versions differ")
    require(platform.python_version() == manifest["expected_runtime"]["python"], "Python version differs")
    solver = Path(sysconfig.get_paths()["purelib"]) / "sage_wheels/bin/Singular"
    require(solver.is_file(), "the preflighted Singular binary is absent")
    solver_version = subprocess.run(
        [str(solver), "--version"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout
    require(
        re.search(r"Singular for .* version " + re.escape(manifest["expected_runtime"]["singular"]), solver_version)
        is not None,
        "the Singular binary version differs",
    )
    os.environ["PATH"] = str(solver.parent) + os.pathsep + os.environ["PATH"]
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    sys.path.insert(0, str(ROOT / "docs/evidence/a5-char0-transfer"))
    import e8_closure_certificate as certificate

    slug, prime, root = "e8-nm", 32009, 10754
    retained = json.loads(certificate._record_path(slug).read_text())
    started = time.monotonic()
    with certificate._execution_scope(1, 8) as execution:
        for checked_slug in ("e8-nm", "e8-np"):
            body = certificate.rc._script(checked_slug, None, certificate.rc.rees.MODULAR_PRIME, extra=False)
            require(
                hashlib.sha256(body.encode()).hexdigest()
                == manifest["expected_retained_bindings"][checked_slug]["producer_script"],
                "the copied sources/caches generate a different producer script: " + checked_slug,
            )
        with certificate._check_workspace(slug):
            inputs = certificate.producer(slug)
            require(
                certificate._input_digest(inputs) == retained["sha256"]["header_j_and_g"],
                "producer J/G differ from the registered input",
            )
            modular_started = time.monotonic()
            modular = certificate.modular_run((slug, inputs, prime, root))
            modular_wall = time.monotonic() - modular_started
            reference_modular = next(
                row for row in retained["stages"]["modular"] if row["prime"] == prime and row["root"] == root
            )
            require(
                all(modular[key] == reference_modular[key] for key in ("rows", "columns", "rank")),
                "the calibration matrix dimensions or rank differ from the registered root",
            )
            cofactors = json.loads(lzma.decompress(certificate._cofactor_path(slug).read_bytes()))
            exact = certificate.verify(slug, inputs, cofactors)
            require(
                exact["status"] == "completed" and exact["verdict"] == "i_equals_is",
                "the exact calibration check fails",
            )
        solution = modular.pop("solution")
        modular["solution_entries"] = [[target, column, value] for (target, column), value in sorted(solution.items())]
        result: dict[str, Any] = {
            "schema": "a5-e8-closure-modular-calibration/1",
            "slug": slug,
            "prime": prime,
            "root": root,
            "source_commit": manifest["source_commit"],
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "certificate_producer_sha256": certificate._sha256_file(Path(certificate.__file__)),
            "producer_script_sha256": inputs["script_sha256"],
            "header_j_and_g_sha256": certificate._input_digest(inputs),
            "execution": execution,
            "producer_wall_seconds": inputs["wall_seconds"],
            "modular_wall_seconds": round(modular_wall, 3),
            "modular": modular,
            "exact": exact,
            "total_wall_seconds": round(time.monotonic() - started, 3),
        }
        destination = ROOT / "docs/local/windows-closure-calibration.json"
        destination.write_text(json.dumps(result, indent=1) + "\n")
        print(
            json.dumps(
                {
                    key: result[key]
                    for key in (
                        "slug",
                        "prime",
                        "root",
                        "producer_wall_seconds",
                        "modular_wall_seconds",
                        "total_wall_seconds",
                    )
                }
            )
        )


if __name__ == "__main__":
    main()
