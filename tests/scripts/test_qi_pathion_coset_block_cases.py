"""Analysis of the Tuna coset-block series: the shared reader, the sign-selected pattern bins, deterministic bins.

analyze binds each run to the committed case byte for byte; the bounded fixture rewrites the manifest at SHOTS shots,
so these tests pass case_root=None; analyze applies the shared qi_records rules to every batch.

The fixture is the committed case (eight batches, 24 circuits) with a bounded shot count: each batch directory is
copied, its manifest is rewritten at SHOTS shots, and a v2 receipt and a qi-collection-v1 collection (every job
metadata nested under `job`, as scripts/qi_platform.py collects) are written around expected-count raw shots.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_block_cases as cb

import qi_records

CASE = Path(__file__).resolve().parents[2] / "results/quantum_inspire/cases/pathion_coset_block_tuna_17"
SHOTS = 2048


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _text(value: Any) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def _write_run(case_batch: Path, run_dir: Path, retention: float, status: str = "completed") -> None:
    manifest = json.loads((case_batch / "cases.json").read_text(encoding="utf-8"))
    manifest["shots"] = SHOTS
    shutil.copytree(case_batch, run_dir)
    cases_text = _text(manifest)
    (run_dir / "cases.json").write_text(cases_text, encoding="utf-8")
    batch_number = int(manifest["batch"].split("-")[1])
    (run_dir / "raw").mkdir()
    submitted, collected = [], []
    for index, row in enumerate(manifest["circuits"]):
        job_id = 1000 * batch_number + index
        submitted.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
        if row["kind"] == "readout":
            strings = [("0" if "readout-0" in row["file"] else "1") * cb.NQUBITS] * SHOTS
        else:
            template = manifest["templates"][row["template"]]
            law = retention * np.array(row["ideal"]) + (1 - retention) / 16
            strings = cb.law_shots(law, template["roles"], SHOTS)
        histogram = {key: strings.count(key) for key in sorted(set(strings))}
        (run_dir / "raw" / f"{row['file']}.json").write_text(_text(strings), encoding="utf-8")
        job = {
            "id": job_id,
            "created_on": f"2026-11-07T00:{batch_number:02d}:00.000000Z",
            "status": status,
            "batch_job_id": 77 + batch_number,
            "queued_at": f"2026-11-07T01:{batch_number:02d}:{index:02d}.000000Z",
            "finished_at": f"2026-11-07T02:{batch_number:02d}:{index:02d}.000000Z",
            "number_of_shots": SHOTS,
        }
        results = [{"job_id": job_id, "shots_requested": SHOTS, "shots_done": SHOTS, "results": histogram}]
        collected.append({"file": row["file"], "job": job, "results": results, "logs": ""})
    receipt = {
        "schema": "qi-submission-v2",
        "state": "enqueued",
        "approval": "fixture",
        "backend": manifest["backend"],
        "backend_type_id": manifest["backend_type_id"],
        "cases_sha256": qi_records.digest(cases_text.encode()),
        "batch_job": 77 + batch_number,
        "shots": SHOTS,
        "jobs": submitted,
    }
    (run_dir / "submission.json").write_text(_text(receipt), encoding="utf-8")
    (run_dir / "results.json").write_text(
        _text({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
    )


def _series(root: Path, retention: float) -> list[Path]:
    runs = []
    for batch in sorted(CASE.glob("batch-*")):
        run_dir = root / f"2026-11-07T00000{batch.name[-1]}Z-{cb.TUNA_SERIES}-{batch.name}"
        _write_run(batch, run_dir, retention)
        runs.append(run_dir)
    return runs


def _manifest() -> dict[str, Any]:
    return json.loads((CASE / "batch-00/cases.json").read_text(encoding="utf-8"))


def test_analyze_reads_the_nested_job_metadata_through_the_shared_reader(tmp_path: Path) -> None:
    runs = _series(tmp_path, 0.9)
    report = cb.analyze(runs, case_root=None)
    _check(report["schema"] == cb.ANALYSIS_SCHEMA and report["complete"], "schema")
    order = report["executed_order"]
    _check(sorted(order) == [f"batch-{n:02d}" for n in range(8)], f"executed batches {sorted(order)}")
    _check(order["batch-00"] == "+-" and order["batch-04"] == "-+", f"arm order of the replicates {order}")
    json.dumps(report, allow_nan=False)


def test_analyze_rejects_a_batch_the_shared_reader_rejects(tmp_path: Path) -> None:
    runs = _series(tmp_path, 0.9)
    raw = runs[2] / "raw" / "b0-plus-r0.cq.json"
    shots = json.loads(raw.read_text(encoding="utf-8"))
    shots[0] = "0" * cb.NQUBITS if shots[0] != "0" * cb.NQUBITS else "1" * cb.NQUBITS
    raw.write_text(_text(shots), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the recorded outcome histogram"):
        cb.analyze(runs, case_root=None)


def test_analyze_rejects_a_job_that_did_not_complete(tmp_path: Path) -> None:
    runs = _series(tmp_path, 0.9)
    collection = json.loads((runs[1] / "results.json").read_text(encoding="utf-8"))
    row = collection["jobs"][0]
    row["job"]["status"] = "cancelled"
    row["results"] = []
    (runs[1] / "results.json").write_text(_text(collection), encoding="utf-8")
    (runs[1] / "raw" / f"{row['file']}.json").unlink()
    with pytest.raises(ValueError, match="did not complete"):
        cb.analyze(runs, case_root=None)


def test_analyze_reports_a_series_short_of_a_batch_without_decisions(tmp_path: Path) -> None:
    report = cb.analyze(_series(tmp_path, 0.9)[:-1], case_root=None)
    _check(report["complete"] is False and len(report["batches"]) == 7, f"batches {report.get('batches')}")
    _check("decisions" not in report, "a partial series reports no decisions")


def test_analyze_rejects_a_batch_listed_twice(tmp_path: Path) -> None:
    runs = _series(tmp_path, 0.9)
    twin = tmp_path / f"2026-11-08T000000Z-{cb.TUNA_SERIES}-batch-00"
    shutil.copytree(runs[0], twin)
    with pytest.raises(ValueError, match="appears twice"):
        cb.analyze([*runs, twin], case_root=None)


def test_pattern_bins_follow_the_ideal_signs_not_the_rounded_values() -> None:
    ideal = {name: np.array(t["ideal_c"]) for name, t in _manifest()["templates"].items()}
    _check(cb.pattern_bins(ideal["ba"], ideal["bb"]) == [2, 6], "the committed ba and bb differ in sign at 2 and 6")
    _check(not np.array_equal(ideal["ba"], ideal["bb"]), "grid rounding makes every bin numerically unequal")
    _check(
        sum(a != b for a, b in zip(ideal["ba"], ideal["bb"], strict=True)) == 8,
        "the committed contrasts are unequal in all eight bins",
    )
    _check(cb.pattern_bins(ideal["ba"], ideal["ba"] * 0.5) == [], "a same-sign pair has no pattern bin")
    _check(cb.pattern_bins(ideal["ba"], -ideal["ba"]) == list(range(8)), "opposite everywhere")


def test_pattern_decision_requires_only_the_opposite_sign_bins() -> None:
    """Both templates resolve every bin except a shared same-sign bin: the pattern decision holds.

    The old selection (exact inequality of the rounded ideal contrasts) takes all eight bins as pattern bins and
    fails on the unresolved one."""
    manifest = _manifest()
    shots = _device(manifest, 0.9)  # retention 0.9 keeps every standard error above zero: only the bin selection acts
    # Bin 0 is a same-sign bin of ba and bb; scramble the selector there in both templates so it is unresolved.
    for name in ("ba", "bb"):
        for key in [k for k in shots if k.split("/")[1].startswith(f"{name}-")]:
            shots[key] = _scramble_bin(shots[key], manifest["templates"][name]["roles"], bin_index=0)
    report = cb.evaluate(shots, manifest)
    for name in ("ba", "bb"):
        _check(report["templates"][name]["bins_with_ideal_sign"] == 7, f"{name} resolves seven bins")
    _check(report["decisions"]["pattern"]["bins"] == [2, 6], "pattern bins")
    _check(report["decisions"]["pattern"]["resolved"], "the opposite-sign bins resolve the pattern")
    _check(all(report["decisions"]["resolution"].values()), "seven of eight bins meet the resolution decision")


def test_signed_z_decides_a_deterministic_bin_by_an_exact_sign_match() -> None:
    _check(cb.signed_z(1.0, 0.0, 1.0) == math.inf, "match on a deterministic bin")
    _check(cb.signed_z(-1.0, 0.0, -1.0) == math.inf, "match with a negative ideal sign")
    _check(cb.signed_z(-1.0, 0.0, 1.0) == -math.inf, "mismatch on a deterministic bin")
    _check(cb.signed_z(0.0, 0.0, 1.0) == 0.0, "a zero contrast decides nothing")
    _check(cb.signed_z(0.5, 0.0, 0.0) == 0.0, "a zero ideal sign decides nothing")
    _check(abs(cb.signed_z(0.3, 0.1, 1.0) - 3.0) < 1e-12, "a sampled bin keeps c * sign / se")
    _check(cb.ratio_or_none(1.0, 0.0) is None and cb.ratio_or_none(1.0, 0.5) == 2.0, "ratio_or_none")


def test_a_deterministic_bin_counts_only_with_enough_shots_in_each_arm() -> None:
    least = cb.DETERMINISTIC_MIN_COUNT
    tail = 0.5 * math.erfc(cb.Z_RESOLVE / math.sqrt(2.0))
    _check(4.0**-least <= tail < 4.0 ** -(least - 1), f"{least} is the least count with 4^-n below the normal tail")
    _check(cb.signed_z(1.0, 0.0, 1.0, n_min=least) == math.inf, "a deterministic bin at the minimum count decides")
    _check(cb.signed_z(1.0, 0.0, 1.0, n_min=least - 1) == 0.0, "a chance-deterministic bin decides nothing")
    _check(cb.signed_z(-1.0, 0.0, 1.0, n_min=least - 1) == 0.0, "a short bin never reads as a contrary result")
    _check(abs(cb.signed_z(0.3, 0.1, 1.0, n_min=1) - 3.0) < 1e-12, "a sampled bin ignores the count rule")


def test_a_zero_contrast_does_not_resolve_the_cocycle_free_decision() -> None:
    """Selectors that never fire give a zero contrast with zero standard error in ba and xor_ba."""
    manifest = _manifest()
    shots = _device(manifest, 1.0)
    for key in shots:
        name = key.split("/")[1].split("-")[0]
        if name in ("ba", "xor_ba"):
            shots[key] = ["0" * cb.NQUBITS] * SHOTS
    with np.errstate(all="ignore"):  # a zero visibility makes the per-bin ratios undefined; the decision ignores them
        report = cb.evaluate(shots, manifest)
    for name in ("ba", "xor_ba"):
        row = report["templates"][name]
        _check(row["selector_contrast"] == 0.0 and row["selector_se"] == 0.0, f"{name} selector is deterministic")
    _check(not report["decisions"]["cocycle_free"]["resolved"], "a zero contrast carries no sign")


def test_noiseless_data_evaluates_with_zero_standard_error_bins() -> None:
    manifest = _manifest()
    report = cb.evaluate(_device(manifest, 1.0), manifest)
    deterministic = {name: row["deterministic_bins"] for name, row in report["templates"].items()}
    _check(any(deterministic["bb"][2:6]), f"bb bins 2 to 5 are deterministic: {deterministic['bb']}")
    _check(report["decisions"]["pattern"]["resolved"], "the noiseless pattern resolves")
    _check(report["all_decisions_met"], f"noiseless decisions {report['decisions']}")
    json.dumps(report, allow_nan=False)


def test_a_deterministic_bin_with_the_wrong_sign_is_unresolved() -> None:
    manifest = _manifest()
    shots = _device(manifest, 1.0)
    swapped = {k: v for k, v in shots.items()}
    for key in list(shots):
        fname = key.split("/")[1]
        if fname.startswith("bb-plus"):
            swapped[key] = shots[key.replace("bb-plus", "bb-minus")]
        elif fname.startswith("bb-minus"):
            swapped[key] = shots[key.replace("bb-minus", "bb-plus")]
    report = cb.evaluate(swapped, manifest)
    _check(report["templates"]["bb"]["bins_with_ideal_sign"] < 6, "an inverted contrast resolves no bin")
    _check(not report["decisions"]["pattern"]["resolved"], "an inverted bb leaves the pattern unresolved")


def _device(manifest: dict[str, Any], retention: float) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for batch in sorted(CASE.glob("batch-*")):
        cases = json.loads((batch / "cases.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]:
            key = f"{cases['batch']}/{row['file']}"
            if row["kind"] == "readout":
                out[key] = [("0" if "readout-0" in row["file"] else "1") * cb.NQUBITS] * SHOTS
                continue
            law = retention * np.array(row["ideal"]) + (1 - retention) / 16
            out[key] = cb.law_shots(law, manifest["templates"][row["template"]]["roles"], SHOTS)
    return out


def _scramble_bin(strings: list[str], roles: dict[str, int], bin_index: int) -> list[str]:
    """Flip the selector of every other shot whose data bits equal bin_index, so both arms read p = 1/2 there."""
    out = []
    seen = 0
    for shot in strings:
        data = sum((int(shot[-1 - roles[k]]) << n) for n, k in enumerate(("d0", "d1", "d2")))
        if data == bin_index:
            seen += 1
            if seen % 2:
                position = len(shot) - 1 - roles["selector"]
                shot = shot[:position] + str(1 - int(shot[position])) + shot[position + 1 :]
        out.append(shot)
    return out
