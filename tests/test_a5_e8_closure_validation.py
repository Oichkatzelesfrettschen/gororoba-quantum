"""Bounded mutations for the retained exact-check receipt's cross-file bindings."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "docs/evidence/a5-char0-transfer"
specification = importlib.util.spec_from_file_location(
    "e8_closure_validation", ROOT / PREFIX / "e8_closure_validation.py"
)
if specification is None or specification.loader is None:
    raise RuntimeError("the closure validation reader is unavailable")
reader = importlib.util.module_from_spec(specification)
specification.loader.exec_module(reader)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def bundle(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    directory = tmp_path / PREFIX
    (directory / "logs").mkdir(parents=True)
    (directory / "cofactors").mkdir()
    sources = {
        "certificate_producer": "e8_closure_certificate.py",
        "slice_rings_qi": "slice_rings_qi.py",
        "reduction_check": "reduction_check.py",
    }
    for filename in sources.values():
        (directory / filename).write_text("source fixture\n")
    checks = []
    for slug in ("e8-nm", "e8-np"):
        cofactor = directory / f"cofactors/e8-closure-{slug}.json.xz"
        cofactor.write_bytes(b"retained cofactor fixture")
        record_path = directory / f"e8-closure-certificate-{slug}.json"
        record = {
            "slug": slug,
            "verdict": "i_equals_is",
            "sha256": {
                **{key: _digest(directory / name) for key, name in sources.items()},
                "cofactor_file": _digest(cofactor),
            },
        }
        record_path.write_text(json.dumps(record))
        log = directory / f"logs/e8-closure-producer-{slug}.log"
        log.write_text("retained generation diagnostic\n")
        checks.append(
            {
                "slug": slug,
                "certificate": str(record_path.relative_to(tmp_path)),
                "certificate_sha256": _digest(record_path),
                "cofactor_sha256": _digest(cofactor),
                "result": {
                    "slug": slug,
                    "verdict": "i_equals_is",
                    "mutations": {
                        kind: {"status": "completed", "verdict": "failed", "bad_identities": count}
                        for kind, count in (("cofactor", 1), ("generator", 42))
                    },
                },
                "retained_generation_diagnostics_equal_before_and_after": True,
                "retained_generation_diagnostic_sha256": {str(log.relative_to(tmp_path)): _digest(log)},
            }
        )
    return tmp_path, {
        "schema": "a5-e8-closure-exact-check-validation/1",
        "certificate_producer_sha256": _digest(directory / "e8_closure_certificate.py"),
        "checks": checks,
    }


def _check(root: Path, document: dict[str, Any]) -> dict[str, int]:
    path = root / PREFIX / "e8-closure-check-validation.json"
    path.write_text(json.dumps(document))
    result: dict[str, int] = reader.check(path, root)
    return result


def test_complete_binding_chain(bundle: tuple[Path, dict[str, Any]]) -> None:
    root, document = bundle
    if _check(root, document) != {"checks": 2, "generation_diagnostics": 2}:
        raise AssertionError("the constructed two-sign receipt differs")


@pytest.mark.parametrize("surface", ("certificate", "cofactor", "source", "diagnostic"))
def test_changed_bound_bytes_fail(bundle: tuple[Path, dict[str, Any]], surface: str) -> None:
    root, document = bundle
    names = {
        "certificate": "e8-closure-certificate-e8-nm.json",
        "cofactor": "cofactors/e8-closure-e8-nm.json.xz",
        "source": "slice_rings_qi.py",
        "diagnostic": "logs/e8-closure-producer-e8-nm.log",
    }
    with (root / PREFIX / names[surface]).open("ab") as output:
        output.write(b"changed")
    with pytest.raises(ValueError, match="binding differs"):
        _check(root, document)


@pytest.mark.parametrize("kind", ("cofactor", "generator"))
def test_incomplete_mutation_fails(bundle: tuple[Path, dict[str, Any]], kind: str) -> None:
    root, document = bundle
    document["checks"][0]["result"]["mutations"][kind]["status"] = "timeout"
    with pytest.raises(ValueError, match="mutation outcome"):
        _check(root, document)


@pytest.mark.parametrize("kind,count", (("cofactor", 0), ("generator", 41)))
def test_wrong_mutation_denominator_fails(bundle: tuple[Path, dict[str, Any]], kind: str, count: int) -> None:
    root, document = bundle
    document["checks"][0]["result"]["mutations"][kind]["bad_identities"] = count
    with pytest.raises(ValueError, match="mutation outcome"):
        _check(root, document)


def test_diagnostic_path_leaves_sign(bundle: tuple[Path, dict[str, Any]]) -> None:
    root, document = bundle
    hashes = document["checks"][0]["retained_generation_diagnostic_sha256"]
    document["checks"][0]["retained_generation_diagnostic_sha256"] = {"../outside.log": next(iter(hashes.values()))}
    with pytest.raises(ValueError, match="path leaves"):
        _check(root, document)
