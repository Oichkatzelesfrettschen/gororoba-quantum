"""Contracts of the coset-block series on Quantum Inspire: scoring, the IBM comparison, the drift stop, the gate.

Each fixture builds run directories from the retained case files with largest-remainder expected counts of the
ideal laws of record (no random draw), at a chosen retention, in the layout qi_platform.collect writes
(a qi-submission-v2 receipt with its approval, a qi-collection-v1 results.json with a job record and outcome histogram
per file, raw/<file>.json shot lists), so every fixture passes the shared qi_records rules that analyze applies.
The IBM side is the retained measured ibm_fez and ibm_marrakesh coset-map records.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_block_cases as gen
import qi_pathion_coset_block_series as pcs

import qi_records

CASES = pcs.CASES_ROOT
TUNA = pcs.TUNA_SERIES
QX = pcs.QX_SERIES


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _shots(law: np.ndarray, roles: dict[str, int], width: int, total: int) -> list[str]:
    """Expected counts of `law` by largest remainder, as shot strings with the roles on their physical qubits."""
    expected = law / law.sum() * total
    counts = np.floor(expected).astype(int)
    for v in np.argsort(counts - expected)[: total - counts.sum()]:
        counts[v] += 1
    strings: list[str] = []
    for v, count in enumerate(counts):
        value = 0
        for k, key in enumerate(("d0", "d1", "d2", "selector")):
            value |= (v >> k & 1) << roles[key]
        strings += [format(value, f"0{width}b")] * int(count)
    return strings


def _readout(width: int, total: int, kind: str, flip: tuple[int, float] | None = None) -> list[str]:
    base = ("0" if kind == "readout-0.cq" else "1") * width
    if flip is None:
        return [base] * total
    qubit, fraction = flip
    moved = format(int(base, 2) ^ (1 << qubit), f"0{width}b")
    n = int(fraction * total)
    return [moved] * n + [base] * (total - n)


def build_series(
    root: Path,
    series: str,
    batches: range,
    retention: float,
    *,
    flip: tuple[str, int, float] | None = None,
    swap: tuple[str, str] | None = None,
    short: str | None = None,
) -> Path:
    """Collected run directories `<stamp>-<series>-batch-NN` under root/runs for the listed batches."""
    runs = root / "runs"
    for n in batches:
        case_batch = CASES / series / f"batch-{n:02d}"
        cases = json.loads((case_batch / "cases.json").read_text(encoding="utf-8"))
        run = runs / f"2026-11-07T000000Z-{series}-batch-{n:02d}"
        shutil.copytree(case_batch, run)
        (run / "raw").mkdir()
        submitted, collected = [], []
        for k, row in enumerate(cases["circuits"]):
            width, total = cases["nqubits"], cases["shots"]
            if row["kind"] == "readout":
                listed = _readout(width, total, row["file"])
                if flip is not None and flip[0] == f"batch-{n:02d}/{row['file']}":
                    listed = _readout(width, total, row["file"], (flip[1], flip[2]))
            else:
                source = swap[1] if swap and row["template"] == swap[0] else row["template"]
                ideal = _ideal_of(series, source, row["arm"])
                law = retention * ideal + (1 - retention) / ideal.size
                listed = _shots(law, cases["templates"][row["template"]]["roles"], width, total)
            if short == f"batch-{n:02d}/{row['file']}":
                listed = listed[:-1]
            (run / "raw" / f"{row['file']}.json").write_text(json.dumps(listed), encoding="utf-8")
            job_id = 100 * n + k
            submitted.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
            job = {
                "id": job_id,
                "created_on": f"2026-11-07T00:{n:02d}:00Z",
                "status": "completed",
                "batch_job_id": 77 + n,
                "queued_at": f"2026-11-07T00:{n:02d}:{k:02d}Z",
                "number_of_shots": cases["shots"],
            }
            result = {
                "job_id": job_id,
                "shots_requested": cases["shots"],
                "shots_done": len(listed),
                "results": dict(sorted(Counter(listed).items())),
            }
            collected.append({"file": row["file"], "job": job, "results": [result], "logs": ""})
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "approval": "fixture",
            "backend": cases["backend"],
            "backend_type_id": cases["backend_type_id"],
            "cases_sha256": qi_records.digest((run / "cases.json").read_bytes()),
            "batch_job": 77 + n,
            "shots": cases["shots"],
            "jobs": submitted,
        }
        (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
        (run / "results.json").write_text(
            json.dumps({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
        )
    return runs


def _ideal_of(series: str, template: str, arm: str) -> np.ndarray:
    for case in sorted((CASES / series).glob("batch-*/cases.json")):
        for row in json.loads(case.read_text(encoding="utf-8"))["circuits"]:
            if row["kind"] == "arm" and row["template"] == template and row["arm"] == arm:
                return np.array(row["ideal"])
    raise AssertionError(f"no {template} {arm} arm in {series}")


def _dirs(runs: Path) -> list[Path]:
    return sorted(runs.glob("*-batch-*"))


@pytest.fixture(scope="module")
def contracted(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    root = tmp_path_factory.mktemp("contracted")
    runs = build_series(root, TUNA, range(8), 0.5)
    return {"runs": runs, "analysis": gen.analyze(_dirs(runs))}


def test_a_contracted_series_meets_every_decision_and_recovers_the_block_statistics(
    contracted: dict[str, Any],
) -> None:
    analysis = contracted["analysis"]
    _expect(isinstance(analysis, dict) and analysis["complete"], "the full series reads as incomplete")
    json.dumps(analysis, allow_nan=False)
    _expect(analysis["all_decisions_met"], f"a decision failed: {analysis['decisions']}")
    _expect(analysis["claim_kind"] == "hardware acquisition" and not analysis["stopped"], "claim kind or stop wrong")
    for name, nullity in (("ba", 2.0), ("bb", 2.0), ("b0", 0.0)):
        stats = analysis["templates"][name]["statistics"]
        for kind in ("raw", "readout_corrected"):
            got = stats[kind]["nullity_estimate"]
            _expect(abs(got - nullity) < 1e-2, f"{name} {kind}: N_hat {got}, ideal {nullity}")
            # Retention 0.5 over the 16 outcomes reads a conditional contrast of 0.5, to the grid rounding.
            _expect(abs(stats[kind]["visibility"] - 0.5) < 1e-2, f"{name} {kind}: V {stats[kind]['visibility']}")
        _expect(abs(analysis["templates"][name]["nullity_ideal"] - nullity) < 0.02, f"{name}: nullity_ideal")
    for device in gen.IBM_RECORDS:
        block = analysis["decisions"]["cross_platform"]["devices"][device]
        _expect(block["holds"], f"{device}: {block}")
        for name in gen.PRIMARY:
            cell = block["templates"][name]["readout_corrected"]
            _expect(cell["bins_within"] == 8 and len(cell["labels"]) == 8, f"{device} {name}: {cell['z']}")
    order = analysis["executed_order"]
    _expect(order["batch-00"] == "+-" and order["batch-04"] == "-+", f"executed order {order}")


def test_delta_method_error_of_a_raw_contrast_is_the_binomial_error(contracted: dict[str, Any]) -> None:
    analysis = contracted["analysis"]
    row = analysis["templates"]["ba"]
    raw = row["statistics"]["raw"]
    _expect(np.allclose(raw["c_se"], row["se"], rtol=2e-3), f"{raw['c_se']} against {row['se']}")


def test_ibm_reference_reproduces_the_stored_block_visibilities() -> None:
    for device, spec in gen.IBM_RECORDS.items():
        records = json.loads((gen.ROOT / spec["collect"]).read_text(encoding="utf-8"))
        group = next(g for g in records if isinstance(g, dict) and g.get("group") == gen.IBM_GROUP)
        summary = group["measured_statistics"]["summary"]
        reference = gen.ibm_reference(device)
        for tag, entry in reference.items():
            for k0, block in entry["blocks"].items():
                stored = summary[f"cmap_{tag}_k{k0}_visibility"]
                _expect(
                    abs(block["visibility"] - stored) < 2e-6, f"{device} {tag} k{k0}: {block['visibility']} {stored}"
                )
            _expect(sorted(entry["labels"]) == list(range(32)), f"{device} {tag}: labels do not cover 32 outputs")


def test_a_template_with_the_other_cocycle_fails_the_cross_platform_rule(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(8), 0.5, swap=("bb", "ba"))
    analysis = gen.analyze(_dirs(runs))
    cross = analysis["decisions"]["cross_platform"]
    _expect(not cross["holds"], "a bb slot carrying the ba laws left the cross-platform rule standing")
    for device in gen.IBM_RECORDS:
        within = cross["devices"][device]["templates"]["bb"][gen.CROSS_STATISTIC]["bins_within"]
        _expect(within < gen.CROSS_BINS_MIN, f"{device}: {within} bins within")
    _expect(not analysis["all_decisions_met"], "decisions met with the wrong cocycle")


def test_a_drifting_readout_bracket_stops_the_series_and_fails_the_rule(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(8), 0.5, flip=("batch-02/readout-0.cq", 8, 0.05))
    analysis = gen.analyze(_dirs(runs))
    drift = analysis["decisions"]["drift"]
    _expect(not drift["holds"] and analysis["stopped"] and not analysis["all_decisions_met"], f"{drift}")
    flagged = {(p["kind"], p["from"], p["to"], p["qubit"]) for p in drift["flagged"]}
    _expect(flagged == {("e01", "batch-00", "batch-02", 8), ("e01", "batch-02", "batch-05", 8)}, f"{flagged}")
    report = pcs.sanity(_dirs(runs))
    _expect(report["stopped"], "--sanity did not stop on the drift")


def test_drift_at_the_threshold_does_not_stop(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(8), 0.5, flip=("batch-02/readout-0.cq", 8, 0.015))
    _expect(not pcs.sanity(_dirs(runs))["stopped"], "a 0.015 change tripped the 0.02 stop")


def test_a_partial_series_reports_batches_and_drift_without_decisions(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(3), 0.5)
    analysis = gen.analyze(_dirs(runs))
    _expect(
        analysis["complete"] is False and analysis["batches"] == ["batch-00", "batch-01", "batch-02"], f"{analysis}"
    )
    _expect("decisions" not in analysis and analysis["references"]["max_abs_delta"] == 0.0, "partial analysis shape")


def test_a_short_shot_list_or_unbound_case_stops_the_load(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(1), 0.5, short="batch-00/readout-0.cq")
    with pytest.raises(SystemExit, match="shots of the"):
        pcs.sanity(_dirs(runs))
    runs = build_series(tmp_path / "b", TUNA, range(1), 0.5)
    run = _dirs(runs)[0]
    receipt = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    receipt["cases_sha256"] = "0" * 64
    (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(SystemExit, match="receipt binds"):
        pcs.sanity([run])


def test_the_qx_control_passes_on_the_ideal_laws_and_fails_on_a_wrong_circuit(tmp_path: Path) -> None:
    runs = build_series(tmp_path, QX, range(8), 1.0)
    analysis = gen.analyze(_dirs(runs))
    _expect(analysis["claim_kind"] == pcs.CONTROL_KIND and analysis["qx_control"]["pass"], f"{analysis['qx_control']}")
    wrong = build_series(tmp_path / "w", QX, range(8), 1.0, swap=("ba", "xor_ba"))
    _expect(not gen.analyze(_dirs(wrong))["qx_control"]["pass"], "a cocycle-free circuit in the ba slot passed")


def test_submit_next_gates_on_order_drift_and_the_qx_control(tmp_path: Path) -> None:
    series_dir = CASES / QX
    runs = build_series(tmp_path, QX, range(2), 1.0)
    run_dir, receipt = pcs.submit_next(series_dir, runs, "approval", dry=True)
    _expect(
        run_dir.name.endswith("-batch-02") and receipt["stops"]["batches_checked"] == ["batch-00", "batch-01"],
        f"{receipt}",
    )
    shutil.rmtree(runs / "2026-11-07T000000Z-pathion_coset_block_qx-batch-00")
    with pytest.raises(SystemExit, match="before batch-00"):
        pcs.submit_next(series_dir, runs, "approval", dry=True)
    tuna = CASES / TUNA
    drifting = build_series(tmp_path / "d", TUNA, range(3), 0.5, flip=("batch-02/readout-0.cq", 8, 0.05))
    with pytest.raises(SystemExit, match="drift stop fired"):
        pcs.submit_next(tuna, drifting, "approval", dry=True)
    clean = build_series(tmp_path / "c", TUNA, range(2), 0.5)
    with pytest.raises(SystemExit, match="needs --control"):
        pcs.submit_next(tuna, clean, "approval", dry=True, client=object())
    qx = build_series(tmp_path / "q", QX, range(8), 1.0)
    control = tmp_path / "control.json"
    control.write_text(json.dumps(gen.analyze(_dirs(qx))), encoding="utf-8")
    with pytest.raises(SystemExit, match="outside the repository"):
        pcs.submit_next(tuna, clean, "approval", control, dry=True, client=object())


def test_submit_next_binds_a_passing_control_into_the_gate_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pcs, "ROOT", tmp_path)
    clean = build_series(tmp_path / "c", TUNA, range(2), 0.5)
    qx = build_series(tmp_path / "q", QX, range(8), 1.0)
    control = tmp_path / "control.json"
    control.write_text(json.dumps(gen.analyze(_dirs(qx))), encoding="utf-8")
    run_dir, receipt = pcs.submit_next(CASES / TUNA, clean, "approval", control, dry=True, client=object())
    _expect(run_dir.name.endswith(f"-{TUNA}-batch-02"), f"{run_dir}")
    _expect(
        receipt["control"]["file"] == "control.json" and receipt["stops"]["bracket_drift_flagged"] == [], f"{receipt}"
    )
    _expect(receipt["pause_seconds"] > 0, "a hardware batch carries its pause step")
    failed = json.loads(control.read_text(encoding="utf-8"))
    failed["qx_control"]["pass"] = False
    control.write_text(json.dumps(failed), encoding="utf-8")
    with pytest.raises(SystemExit, match="QX control missed"):
        pcs.submit_next(CASES / TUNA, clean, "approval", control, dry=True, client=object())
