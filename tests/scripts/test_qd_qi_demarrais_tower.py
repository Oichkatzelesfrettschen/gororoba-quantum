"""Unit tests for the Quandela and Quantum Inspire 16D-to-8192D De Marrais tower scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "gororoba_quantum") not in sys.path:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import qd_demarrais_tower  # noqa: E402
import qi_demarrais_tower  # noqa: E402


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_qd_demarrais_tower_self_test_and_check() -> None:
    summary = qd_demarrais_tower.run_self_test()
    _check(summary["tower_levels"] == 14, "expected 14 tower levels")
    _check(summary["max_dimension"] == 8192, "expected 8192 max dimension")
    _check(summary["max_name"] == "DekatrisVoudon", "expected DekatrisVoudon")
    _check(abs(summary["slos_8192d_midden_contrast"] - 1.0) < 1e-9, "SLOS 8192D midden contrast != 1.0")
    qd_demarrais_tower.check_all_cases()


def test_qd_demarrais_tower_synthetic_analysis(tmp_path: Path) -> None:
    case_dir = qd_demarrais_tower.CASE_ROOT / "ascella" / "job-dm3"
    cases = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    run_dir = tmp_path / "run-dm3"
    run_dir.mkdir(parents=True)
    (run_dir / "cases.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")

    iterations = []
    for s in cases["settings"]:
        if "null" not in s["arm"]:
            counts = {"|0,0,1,0,0,0,0,0,0,0,0,0>": 1000}
        else:
            counts = {"|1,0,0,0,0,0,0,0,0,0,0,0>": 1000}
        iterations.append({"name": s["name"], "counts": counts})
    (run_dir / "results.json").write_text(json.dumps({"iterations": iterations}, indent=2) + "\n", encoding="utf-8")

    report = qd_demarrais_tower.analyze_run(run_dir)
    _check(report["job_id"] == "job-dm3", "unexpected job_id")
    _check(abs(report["mean_active_d"] - 1.0) < 1e-9, "expected active D_midden == +1.0")
    _check(abs(report["mean_null_d"] + 1.0) < 1e-9, "expected null D_midden == -1.0")
    _check(abs(report["measured_contrast_delta"] - 2.0) < 1e-9, "expected Delta_midden == +2.0")
    _check(report["verdict"] == "CONFORMANT", f"verdict {report['verdict']}")

    for plat in ("sim:ascella", "qpu:ascella", "sim:belenos", "qpu:belenos"):
        twin = qd_demarrais_tower.simulate_local_twin("job-dm3", plat, out_dir=tmp_path / f"twin-{plat}")
        _check(twin["verdict"] == "CONFORMANT", f"{plat} local twin not CONFORMANT")
        _check(twin["measured_contrast_delta"] > 1.95, f"{plat} delta {twin['measured_contrast_delta']} <= 1.95")

    twin_dm4 = qd_demarrais_tower.simulate_local_twin("job-dm4", "sim:belenos", out_dir=tmp_path / "twin-dm4-belenos")
    _check(twin_dm4["verdict"] == "CONFORMANT", "job-dm4 sim:belenos not CONFORMANT")
    _check(twin_dm4["iterations"] == 24, f"expected 24 settings on job-dm4 belenos, got {twin_dm4['iterations']}")
    ctrl_row = next(r for r in twin_dm4["settings"] if r["name"].endswith("ctrl_n12_4096d_dodekavoudon"))
    act_row = next(r for r in twin_dm4["settings"] if r["name"].endswith("explore_8192d_midden_s1"))
    _check(ctrl_row["c_upper_8192d_shell"] == 0, "expected 0 upper 24-mode counts on 4096D control")
    _check(act_row["c_upper_8192d_shell"] > 0, "expected >0 upper 24-mode counts on 8192D active setting")


@pytest.mark.audit
def test_qi_demarrais_tower_check_and_synthetic_analysis(tmp_path: Path) -> None:
    qi_demarrais_tower.check_suite()
    tuna_case = qi_demarrais_tower.CASES_ROOT / "demarrais_tuna17_8192d" / "batch-00"
    cases = json.loads((tuna_case / "cases.json").read_text(encoding="utf-8"))
    _check(cases["shots"] == 75536, f"expected 75536 shots on Tuna-17, got {cases['shots']}")
    _check(cases["nqubits"] == 17, f"expected 17 qubits on Tuna-17, got {cases['nqubits']}")
    _check(cases["cayley_dickson_target_dim"] == 8192, "expected 8192D target dim")

    run_dir = tmp_path / "tuna17-run"
    (run_dir / "raw").mkdir(parents=True)
    # Use a small synthetic shot count for unit-test speed
    small_cases = dict(cases)
    small_cases["shots"] = 64
    (run_dir / "cases.json").write_text(json.dumps(small_cases, indent=1) + "\n", encoding="utf-8")
    for row in small_cases["circuits"]:
        shots = [row["ideal_shot_string"]] * 64
        (run_dir / "raw" / f"{row['file']}.json").write_text(json.dumps(shots) + "\n", encoding="utf-8")

    analysis = qi_demarrais_tower.analyze_batch_run(run_dir)
    _check(analysis["cayley_dickson_target_dim"] == 8192, "expected 8192D in analysis")
    _check(
        abs(analysis["voudon_switching_contrast_cowbird_minus_midden"] - 1.0) < 1e-9, "expected switching contrast 1"
    )
    for kind in ("midden", "cowbird", "dmz"):
        c_rep = analysis["circuits"][kind]
        _check(abs(c_rep["exact_17q_or_10q_match_probability"] - 1.0) < 1e-9, f"{kind} exact match != 1.0")
        _check(abs(c_rep["interference_contrast_one_minus_two_path"] - 1.0) < 1e-9, f"{kind} contrast != 1.0")
        _check(abs(c_rep["sentinel_all_zero_herald_rate"] - 1.0) < 1e-9, f"{kind} herald rate != 1.0")

    for batch_name, expected_key in (
        ("batch-01", "shell_8192d_or_1024d_vs_32d_control_contrast"),
        ("batch-02", "catamaran_vs_sleeper_null_contrast"),
    ):
        b_case = qi_demarrais_tower.CASES_ROOT / "demarrais_tuna17_8192d" / batch_name
        b_cases = json.loads((b_case / "cases.json").read_text(encoding="utf-8"))
        b_run = tmp_path / f"tuna17-{batch_name}"
        (b_run / "raw").mkdir(parents=True)
        b_small = dict(b_cases)
        b_small["shots"] = 64
        (b_run / "cases.json").write_text(json.dumps(b_small, indent=1) + "\n", encoding="utf-8")
        for row in b_small["circuits"]:
            (b_run / "raw" / f"{row['file']}.json").write_text(
                json.dumps([row["ideal_shot_string"]] * 64) + "\n", encoding="utf-8"
            )
        b_analysis = qi_demarrais_tower.analyze_batch_run(b_run)
        _check(expected_key in b_analysis, f"missing {expected_key} in {batch_name} analysis")
        _check(abs(b_analysis[expected_key] - 1.0) < 1e-9, f"{batch_name} {expected_key} != 1.0")


def test_qd_demarrais_tower_withholds_a_verdict_without_null_or_counts(tmp_path: Path) -> None:
    cases = json.loads(
        (qd_demarrais_tower.CASE_ROOT / "ascella" / "job-dm1" / "cases.json").read_text(encoding="utf-8")
    )
    run_dir = tmp_path / "run-dm1"
    run_dir.mkdir()
    (run_dir / "cases.json").write_text(json.dumps(cases) + "\n", encoding="utf-8")
    wrong = [{"counts": {"|1,0,0,0,0,0,0,0,0,0,0,0>": 1000}} for _ in cases["settings"]]
    (run_dir / "results.json").write_text(json.dumps({"iterations": wrong}) + "\n", encoding="utf-8")
    report = qd_demarrais_tower.analyze_run(run_dir)
    _check(report["verdict"] == "UNADJUDICATED: no null arm", f"null-free verdict {report['verdict']}")

    partial: list[dict[str, object]] = [{"missing": True} for _ in cases["settings"]]
    partial[0] = {"iteration": 0, "error": "Circuit optimizer: No trial converged", "result_fields": {}}
    (run_dir / "results.json").write_text(json.dumps({"iterations": partial}) + "\n", encoding="utf-8")
    report = qd_demarrais_tower.analyze_run(run_dir)
    _check(report["verdict"] == "UNADJUDICATED: settings without counts", f"partial verdict {report['verdict']}")
    _check(len(report["unavailable_settings"]) == len(cases["settings"]), "every unavailable setting is reported")
