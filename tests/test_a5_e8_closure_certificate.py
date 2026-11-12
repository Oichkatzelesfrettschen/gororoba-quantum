"""The E8-bar closure certificate over Q(i): rational reconstruction, the verdict predicate, the Nakayama rank, the
mutation-detection rule and the record-digest gate of `--check`, on constructed data that needs neither Singular nor
the retained records."""

from __future__ import annotations

import copy
import json
import lzma
import math
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAR0 = ROOT / "docs/evidence/a5-char0-transfer"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(CHAR0))

import e8_closure_certificate as cert  # noqa: E402

MODULUS = 32009 * 32029 * 32749


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _closed_row() -> dict[str, Any]:
    """A parsed result in which every premise of the closure holds."""
    return {
        "status": "completed",
        "j_nonzero": 0,
        "generators": 21,
        "colength_of_n": 2,
        "am_outside_n": 0,
        "n_outside_am": 0,
        "bad_identities": 0,
        "qw_relation_rank": 21,
    }


def _residue(fraction: Fraction, modulus: int = MODULUS) -> int:
    return fraction.numerator * pow(fraction.denominator, -1, modulus) % modulus


def test_a_value_without_a_small_fraction_is_not_reconstructed_as_zero() -> None:
    # 32009 * 32029 is neither 0 nor the residue of a fraction inside the bound modulo the three primes.
    _check(cert._ratrec(32009 * 32029, MODULUS) is None)


def test_every_reconstructed_fraction_satisfies_its_congruence() -> None:
    for value in (32009 * 32029, 123456789012, 7, MODULUS - 1, 10**9 + 7):
        fraction = cert._ratrec(value, MODULUS)
        if fraction is not None:
            _check((fraction.numerator - value * fraction.denominator) % MODULUS == 0)


@pytest.mark.parametrize(
    "fraction", [Fraction(0), Fraction(1), Fraction(-1), Fraction(3, 7), Fraction(-5, 11), Fraction(12345, 6789)]
)
def test_a_small_fraction_is_reconstructed_from_its_residue(fraction: Fraction) -> None:
    _check(cert._ratrec(_residue(fraction), MODULUS) == fraction)


@pytest.mark.parametrize("sign", [1, -1])
def test_the_eight_prime_reconstruction_boundary_uses_integer_arithmetic(sign: int) -> None:
    modulus = math.prod(prime for prime, _root in cert.PRIMES[:8])
    boundary = math.isqrt(modulus // 2)
    _check(cert._ratrec(sign * boundary, modulus) == Fraction(sign * boundary))


def test_a_verdict_needs_every_premise() -> None:
    _check(cert.verdict(_closed_row()) == "i_equals_is")
    violations: dict[str, Any] = {
        "j_nonzero": 3,
        "colength_of_n": 3,
        "am_outside_n": 1,
        "n_outside_am": 1,
        "bad_identities": 1,
        "qw_relation_rank": 20,
    }
    for key, value in violations.items():
        row = _closed_row()
        row[key] = value
        _check(cert.verdict(row) == "failed")


def test_a_rank_deficit_is_measured_against_the_generator_count() -> None:
    row = dict(_closed_row(), generators=22)
    _check(cert.verdict(row) == "failed")
    row = dict(_closed_row(), generators=22, qw_relation_rank=22)
    _check(cert.verdict(row) == "i_equals_is")


def _cofactors(rows: list[list[list[Any]]], n: int) -> dict[str, Any]:
    """Cofactor data with n columns of kind u (one per generator) and one column of kind g; 2n target rows."""
    labels = [["u", k, "", 0, [0, 0, 0, 0, 0, 0]] for k in range(n)] + [["g", 0, "", 0, [0, 0, 0, 0, 0, 0]]]
    return {"labels": labels, "targets": copy.deepcopy(rows)}


def test_the_nakayama_rank_of_independent_relations_is_full() -> None:
    # No beta part: the rows are +-e_j, of rank n.
    data = _cofactors([[[2, "5", "0"]], [[2, "1", "1"]], [], []], 2)
    _check(cert.nakayama_rank(data, 2) == {"qw_relation_rank": 2, "size": 2})


def test_the_nakayama_rank_of_dependent_relations_is_deficient() -> None:
    # The beta parts turn every row into a multiple of (1, 1).
    rows = [[[1, "1", "0"]], [[0, "1", "0"]], [[1, "-1", "0"]], [[0, "-1", "0"]]]
    _check(cert.nakayama_rank(_cofactors(rows, 2), 2) == {"qw_relation_rank": 1, "size": 2})


def test_the_nakayama_rank_reads_the_imaginary_part_of_beta() -> None:
    # n = 1: the two rows are 1 + beta_0 and -1 + beta_1; a beta with an imaginary part keeps the row nonzero.
    partial = _cofactors([[[0, "-1", "0"]], [[0, "-1", "0"]]], 1)
    _check(cert.nakayama_rank(partial, 1)["qw_relation_rank"] == 1)
    both = _cofactors([[[0, "-1", "0"]], [[0, "1", "0"]]], 1)
    _check(cert.nakayama_rank(both, 1)["qw_relation_rank"] == 0)
    imaginary = _cofactors([[[0, "-1", "1"]], [[0, "1", "1"]]], 1)
    _check(cert.nakayama_rank(imaginary, 1)["qw_relation_rank"] == 1)


def test_a_column_that_is_not_a_u_column_does_not_enter_the_rank() -> None:
    data = _cofactors([[[1, "9", "9"]], [[1, "9", "9"]]], 1)
    _check(cert.nakayama_rank(data, 1)["qw_relation_rank"] == 1)


def test_a_mutation_counts_as_detected_only_when_it_ran_and_broke_an_identity() -> None:
    detected = {"status": "completed", "bad_identities": 1, "verdict": "failed"}
    _check(cert.mutation_detected(detected))
    _check(not cert.mutation_detected({**detected, "status": "blocked_timeout"}))
    _check(not cert.mutation_detected({**detected, "status": "blocked_error"}))
    _check(not cert.mutation_detected({**detected, "bad_identities": 0}))
    _check(not cert.mutation_detected({"status": "completed", "verdict": "failed"}))
    _check(not cert.mutation_detected({**detected, "verdict": "i_equals_is"}))


def _record_setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, digests: dict[str, str]) -> None:
    cofactor = tmp_path / "cofactor.json.xz"
    cofactor.write_bytes(lzma.compress(json.dumps({"labels": [], "targets": []}).encode()))
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"sha256": {**digests, "cofactor_file": cert._sha256_file(cofactor)}}))
    monkeypatch.setattr(cert, "_record_path", lambda _slug: record)
    monkeypatch.setattr(cert, "_cofactor_path", lambda _slug: cofactor)


def _source_digests() -> dict[str, str]:
    return {
        "certificate_producer": cert._sha256_file(CHAR0 / "e8_closure_certificate.py"),
        "slice_rings_qi": cert._sha256_file(CHAR0 / "slice_rings_qi.py"),
        "reduction_check": cert._sha256_file(CHAR0 / "reduction_check.py"),
        "producer_script": "script",
        "header_j_and_g": "jg",
    }


@pytest.mark.parametrize(
    ("key", "name"),
    [
        ("certificate_producer", "e8_closure_certificate.py"),
        ("slice_rings_qi", "slice_rings_qi.py"),
        ("reduction_check", "reduction_check.py"),
    ],
)
def test_check_rejects_a_source_that_differs_from_the_record_before_any_replay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, key: str, name: str
) -> None:
    _record_setup(monkeypatch, tmp_path, {**_source_digests(), key: "0" * 64})

    def _unreachable(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError

    monkeypatch.setattr(cert, "producer", _unreachable)
    monkeypatch.setattr(cert, "verify", _unreachable)
    with pytest.raises(SystemExit) as raised:
        cert.check("e8-nm")
    message = str(raised.value)
    _check(name in message and "--write" in message)


def _replay(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mutated: dict[str, Any]) -> dict[str, Any]:
    _record_setup(monkeypatch, tmp_path, _source_digests())
    monkeypatch.setattr(cert, "producer", lambda _slug: {"script_sha256": "script"})
    monkeypatch.setattr(cert, "_input_digest", lambda _inputs: "jg")

    def _verify(_slug: str, _inputs: Any, _cofactors: Any, mutate: str | None = None) -> dict[str, Any]:
        if mutate is None:
            return {**_closed_row(), "verdict": "i_equals_is", "wall_seconds": 1.0}
        return mutated

    monkeypatch.setattr(cert, "verify", _verify)
    return cert.check("e8-nm")


def test_check_accepts_matching_sources_and_detected_mutations(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    result = _replay(monkeypatch, tmp_path, {"status": "completed", "bad_identities": 2, "verdict": "failed"})
    _check(result["verdict"] == "i_equals_is" and set(result["mutations"]) == {"cofactor", "generator"})


@pytest.mark.parametrize(
    "mutated",
    [
        {"status": "blocked_timeout", "errors": ["timeout"], "verdict": "failed"},
        {"status": "completed", "bad_identities": 0, "verdict": "failed"},
    ],
    ids=["mutation-run-did-not-complete", "mutation-broke-no-identity"],
)
def test_check_fails_when_a_mutation_goes_undetected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mutated: dict[str, Any]
) -> None:
    with pytest.raises(SystemExit, match="was not detected"):
        _replay(monkeypatch, tmp_path, mutated)


@pytest.mark.parametrize("fail_mutation", [False, True])
def test_check_preserves_retained_diagnostics_on_success_and_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fail_mutation: bool
) -> None:
    _record_setup(monkeypatch, tmp_path, _source_digests())
    retained_logs = tmp_path / "retained"
    retained_logs.mkdir()
    for suffix in ("log", "time"):
        (retained_logs / f"retained.{suffix}").write_text(f"retained {suffix}\n")
    before = {path.name: path.read_bytes() for path in retained_logs.iterdir()}
    scratch = tmp_path / "work"
    monkeypatch.setattr(cert, "LOGS", retained_logs)
    monkeypatch.setattr(cert, "WORK", scratch)
    monkeypatch.setattr(cert, "_input_digest", lambda _inputs: "jg")

    class CompletedCommand:
        def wait(self, timeout: int | None = None) -> int:
            return 0

        def poll(self) -> int:
            return 0

    def command(*_args: Any, **kwargs: Any) -> CompletedCommand:
        kwargs["stdout"].write("RESULT harmless 1\n")
        kwargs["stderr"].write("Maximum resident set size (kbytes): 1024\n")
        return CompletedCommand()

    monkeypatch.setattr(cert.subprocess, "Popen", command)

    def producer(_slug: str) -> dict[str, Any]:
        cert._singular("quit;\n", "retained")
        return {"script_sha256": "script"}

    def verify(_slug: str, _inputs: Any, _cofactors: Any, mutate: str | None = None) -> dict[str, Any]:
        cert._singular("quit;\n", "retained")
        if mutate is not None:
            return {"status": "completed", "bad_identities": 0 if fail_mutation else 1, "verdict": "failed"}
        return {**_closed_row(), "verdict": "i_equals_is", "wall_seconds": 0}

    monkeypatch.setattr(cert, "producer", producer)
    monkeypatch.setattr(cert, "verify", verify)
    if fail_mutation:
        with pytest.raises(SystemExit, match="was not detected"):
            cert.check("e8-nm")
    else:
        _check(cert.check("e8-nm")["verdict"] == "i_equals_is")
    _check({path.name: path.read_bytes() for path in retained_logs.iterdir()} == before)
    _check(bool(list(scratch.rglob("retained.log"))))
    _check(cert.LOGS == retained_logs and cert.WORK == scratch)


def test_default_worker_admission_caps_execution_and_restores_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert.parallel, "available_cpus", lambda: 8)
    monkeypatch.setenv("GOROROBA_WORKERS", "8")
    monkeypatch.setenv("OMP_NUM_THREADS", "6")
    with cert._execution_scope(2, 12) as execution:
        _check(cert.parallel.workers() == 2 and os.environ["OMP_NUM_THREADS"] == "1")
        _check(execution["requested_workers"] == 2 and execution["effective_workers"] == 2)
        _check(execution["memory_budget_gib"] == 12 and execution["required_memory_gib"] == 11)
    _check(os.environ["GOROROBA_WORKERS"] == "8" and os.environ["OMP_NUM_THREADS"] == "6")


def test_four_workers_require_an_explicit_sufficient_memory_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert.parallel, "available_cpus", lambda: 8)
    monkeypatch.setenv("GOROROBA_WORKERS", "8")
    with pytest.raises(ValueError, match="21 GiB"):
        with cert._execution_scope(4, 12):
            pass
    with cert._execution_scope(4, 24) as execution:
        _check(cert.parallel.workers() == 4 and execution["required_memory_gib"] == 21)
    with pytest.raises(ValueError, match="between 1 and 4"):
        with cert._execution_scope(5, 32):
            pass
