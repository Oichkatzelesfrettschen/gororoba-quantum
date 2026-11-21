"""The packed Pauli Garnet case builds, round-trips through check and analyzes bounded synthetic runs."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from fractions import Fraction
from pathlib import Path

import iqm_packed_pauli_case as case
import iqm_sim
import numpy as np
import pytest

CALIBRATION = iqm_sim.EVIDENCE / case.QC / "calibration"


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    """The full 68-circuit build: 36 compiles, 32 buffers and 340 density-matrix cells."""
    directory = tmp_path_factory.mktemp("packed-pauli") / "case"
    case.write(directory, CALIBRATION)
    yield directory


def _task(number: int, name: str, kind: str, **role: object) -> dict[str, object]:
    proposal, texts = case.load_proposal()
    row = (
        next(r for r in proposal["circuits"] if r["file"] == f"{name}.qasm")
        if kind != "buffer"
        else {"file": name, "kind": "buffer", **role}
    )
    text = texts[proposal["circuits"].index(row)] if kind != "buffer" else ""
    item = (number, row, text, proposal["physical_map_to_be_applied_by_native_compiler"], str(CALIBRATION))
    return case.circuit_task(item)


def test_science_circuit_and_buffer_compile_with_the_barrier_in_order() -> None:
    science = _task(1, "circuit-002", "science")
    buffer = _task(0, "buffer-002", "buffer", before="circuit-002")
    ops = science["circuit"]["instructions"]  # type: ignore[index]
    barriers = [n for n, op in enumerate(ops) if op["name"] == "barrier"]
    _check(len(barriers) == 1 and len(ops[barriers[0]]["locus"]) == 20, f"barriers {barriers}")
    _check(ops[-1]["name"] == "measure" and len(ops[-1]["locus"]) == 20, "no joint twenty-qubit measure")
    _check(all(op["name"] in ("prx", "cz") for op in ops[: barriers[0]]), "a non-gate before the barrier")
    only = buffer["circuit"]["instructions"]  # type: ignore[index]
    _check(len(only) == 1 and only[0]["name"] == "measure" and len(only[0]["locus"]) == 20, f"buffer {only}")
    _check(buffer["shot_path_seconds"] == 0.0, "the buffer has a gate path")
    ideal = buffer["record"]["cells"][0]["ideal_distribution"]  # type: ignore[index]
    _check(ideal[0] == 1.0, "the buffer cell is not the ground state")


def test_gate_crossing_the_barrier_is_refused() -> None:
    calibration = iqm_sim.Calibration.from_directory(CALIBRATION)
    proposal, _ = case.load_proposal()
    case.refusal_checks(calibration, proposal["physical_map_to_be_applied_by_native_compiler"])


def test_carryover_contrast_reads_a_planted_predecessor_dependence() -> None:
    shots = 100
    zero = np.zeros(shots, dtype=np.int64)
    hot = np.zeros(shots, dtype=np.int64)
    hot[:10] = 1
    roles: list[dict[str, object]] = [{"name": "ref", "kind": "reference", "reference": 1}]
    for n in range(6):
        roles.append({"name": f"buffer-{n}", "kind": "buffer"})
        roles.append({"name": f"sci-{n}", "kind": "science", "dense": n % 2 == 0, "pair": n // 2})
    cells = [[hot if (n > 0 and roles[n - 1].get("dense")) else zero for _ in range(5)] for n in range(len(roles))]
    out = case.carryover_contrast(roles, cells)
    _check(out["buffers_after_dense"] == 3 and out["buffers_after_sparse"] == 2, f"{out}")
    register = out["difference"]["register"]
    _check(abs(register["difference"] - 0.025) < 1e-12 and register["standard_error"] < 1e-12, f"{register}")
    _check(set(out["after_reference"]) == {"buffer-0"}, f"{out['after_reference']}")


@pytest.mark.audit
def test_build_round_trips_and_binds_the_prediction(built: Path) -> None:
    case.check(built)
    cases = case.json.loads((built / "cases.json").read_text(encoding="utf-8"))
    job = cases["jobs"][0]
    _check(
        len(job["circuits"]) == 68 and job["shots"] == 2000, f"{len(job['circuits'])} circuits, {job['shots']} shots"
    )
    _check(job["options"]["heralding_mode"] == "none" and job["options"]["active_reset_cycles"] == 1, "options")
    ceiling = job["max_credits"]["garnet"]
    _check(job["max_credits"]["garnet:mock"] == 0.0 and 0 < ceiling <= 24, job["max_credits"])
    _check(
        ceiling / 0.5 - 1.0 - 2.0 >= 1.6 + job["expected_seconds"],
        f"no plan headroom under the cancel threshold {ceiling}",
    )
    _check(cases["prediction_sha256"] == case.sha256((built / "prediction.json").read_bytes()), "unbound prediction")
    names = [Path(c["file"]).stem for c in job["circuits"]]
    for n, name in enumerate(names):
        if name.startswith("buffer-"):
            _check(names[n + 1] == f"circuit-{name[7:]}", f"{name} does not precede its science circuit")
        elif 2 <= int(name[8:]) <= 33:
            _check(names[n - 1] == f"buffer-{name[8:]}", f"{name} does not follow its buffer")


@pytest.mark.audit
def test_check_rejects_an_edited_circuit(built: Path, tmp_path: Path) -> None:
    copy = tmp_path / "copy"
    shutil.copytree(built, copy)
    victim = copy / "circuits" / "circuit-002.json"
    victim.write_text(victim.read_text(encoding="utf-8").replace('"prx"', '"prx "', 1), encoding="utf-8")
    with pytest.raises(case.CaseError, match="differs from the build"):
        case.check(copy)


@pytest.mark.audit
def test_null_device_gives_no_rejection_and_no_carryover(built: Path, tmp_path: Path) -> None:
    result = case.analyze(case.synthetic_run(built, tmp_path / "run", "null"))
    primary = result["primary"]
    _check(Fraction(primary["p_value"]) == 1 and not primary["reject_at_0.05"], f"{primary}")
    _check(primary["pairs"] == 16 and set(primary["numerator_2g_dense_minus_sparse"]) == {0}, f"{primary}")
    rows = result["exploratory"]["carryover_after_dense_minus_sparse"]["difference"]
    _check(all(abs(row["difference"]) < 1e-12 for row in rows.values()), f"{rows}")


@pytest.mark.audit
def test_balanced_pair_differences_give_no_rejection(built: Path, tmp_path: Path) -> None:
    primary = case.analyze(case.synthetic_run(built, tmp_path / "run", "alternating"))["primary"]
    _check(any(primary["numerator_2g_dense_minus_sparse"]), "the fixture planted no difference")
    _check(not primary["reject_at_0.05"], f"{primary}")


@pytest.mark.audit
def test_planted_dense_minus_sparse_response_is_rejected(built: Path, tmp_path: Path) -> None:
    primary = case.analyze(case.synthetic_run(built, tmp_path / "run", "planted"))["primary"]
    _check(Fraction(primary["p_value"]) <= Fraction(1, 128), f"p = {primary['p_value']}")
    _check(primary["mean_difference"] < 0, f"mean difference {primary['mean_difference']}")


@pytest.mark.audit
def test_planted_lag_one_carryover_reads_in_the_buffers_and_leaves_the_primary_test(
    built: Path, tmp_path: Path
) -> None:
    null = case.analyze(case.synthetic_run(built, tmp_path / "null", "null"))
    planted = case.analyze(case.synthetic_run(built, tmp_path / "carryover", "carryover"))
    rows = planted["exploratory"]["carryover_after_dense_minus_sparse"]["difference"]
    _check(all(row["difference"] > 0.01 for row in rows.values()), f"{rows}")
    _check(planted["primary"]["p_value"] == null["primary"]["p_value"], "the buffers moved the primary p-value")


@pytest.mark.audit
def test_mock_run_is_refused(built: Path, tmp_path: Path) -> None:
    run = case.synthetic_run(built, tmp_path / "run", "null", qc="garnet:mock")
    with pytest.raises(case.CaseError, match="not a"):
        case.analyze(run)


def test_altered_proposal_circuit_is_refused(tmp_path: Path) -> None:
    copy = tmp_path / "proposal"
    shutil.copytree(case.PROPOSAL, copy)
    (copy / "circuit-007.qasm").write_text("OPENQASM 2.0;\n", encoding="utf-8")
    with pytest.raises(case.CaseError, match="differs from the sha256"):
        case.load_proposal(copy)
