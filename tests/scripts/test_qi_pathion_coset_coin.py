"""Contracts of the coin-arm coset-block series on Quantum Inspire: scoring, the IBM comparison, the drift covariate.

Each fixture builds run directories from the retained case files with largest-remainder expected counts of the
ideal laws of record (no random draw), in the layout qi_platform.collect writes (a qi-submission-v2 receipt, a
qi-collection-v1 results.json with a job record and outcome histogram per file, raw/<file>.json shot lists), which
analyze reads through qi_records. The IBM side is the retained measured ibm_fez and ibm_marrakesh
coset-map records. A drift between readout brackets is recorded in the analysis and in the gate receipt and
refuses nothing.
"""

from __future__ import annotations

import json
import math
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_block_cases as blk
import qi_pathion_coset_block_series as old_series
import qi_pathion_coset_coin_cases as gen
import qi_pathion_coset_coin_series as gate

import qi_records

CASES = gate.CASES_ROOT
TUNA = gate.TUNA_SERIES
QX = gate.QX_SERIES
REGISTER = (2, 4, 8, 11, 12)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _readout_shots(
    width: int, total: int, excited: bool, assignment: dict[int, tuple[float, float]], register: list[int]
) -> list[str]:
    law = np.ones(1)
    for q in reversed(register):
        e01, e10 = assignment[q]
        p1 = 1.0 - e10 if excited else e01
        law = np.kron(law, np.array([1.0 - p1, p1]))
    roles = {f"q{n}": q for n, q in enumerate(register)}
    return gen.place_counts(gen.largest_remainder(law, total), tuple(roles), roles, width)


def build_series(
    root: Path,
    series: str,
    batches: range,
    retention: float,
    *,
    assignment: dict[str, dict[int, tuple[float, float]]] | None = None,
    swap: tuple[str, str] | None = None,
    short: str | None = None,
    laws: dict[str, np.ndarray] | None = None,
) -> Path:
    """Collected run directories `<stamp>-<series>-batch-NN` under root/runs for the listed batches.

    `laws` maps a template to the 32-outcome law its circuit reads in place of the contracted ideal law."""
    runs = root / "runs"
    for n in batches:
        case_batch = CASES / series / f"batch-{n:02d}"
        cases = json.loads((case_batch / "cases.json").read_text(encoding="utf-8"))
        run = runs / f"2026-11-07T000000Z-{series}-batch-{n:02d}"
        shutil.copytree(case_batch, run)
        (run / "raw").mkdir()
        submitted: list[dict[str, Any]] = []
        collected: list[dict[str, Any]] = []
        width, total = cases["nqubits"], cases["shots"]
        asg = (assignment or {}).get(f"batch-{n:02d}", {q: (0.0, 0.0) for q in cases["register"]})
        for k, row in enumerate(cases["circuits"]):
            if row["kind"] == "readout":
                listed = _readout_shots(width, total, row["file"] == "readout-1.cq", asg, cases["register"])
            else:
                source = swap[1] if swap and row["template"] == swap[0] else row["template"]
                ideal = _ideal_of(series, source)
                law = retention * ideal + (1 - retention) / ideal.size
                if laws and row["template"] in laws:
                    law = laws[row["template"]]
                roles = cases["templates"][row["template"]]["roles"]
                matrix = gen.confusion([asg[roles[key]] for key in gen.KEYS])
                listed = gen.place_counts(gen.largest_remainder(matrix @ law, total), gen.KEYS, roles, width)
            histogram = dict(sorted(Counter(listed).items()))
            if short == f"batch-{n:02d}/{row['file']}":
                listed = listed[:-1]
            (run / "raw" / f"{row['file']}.json").write_text(json.dumps(listed), encoding="utf-8")
            job_id = 100 * n + k
            submitted.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
            job = {
                "id": job_id,
                "created_on": f"2026-11-07T00:{n:02d}:00.000000Z",
                "status": "completed",
                "batch_job_id": 77 + n,
                "queued_at": f"2026-11-07T00:{n:02d}:{k:02d}.000000Z",
                "finished_at": f"2026-11-07T01:{n:02d}:{k:02d}.000000Z",
                "number_of_shots": total,
            }
            results = [{"job_id": job_id, "shots_requested": total, "shots_done": total, "results": histogram}]
            collected.append({"file": row["file"], "job": job, "results": results, "logs": ""})
        cases_text = (run / "cases.json").read_text(encoding="utf-8")
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "approval": "fixture",
            "backend": cases["backend"],
            "backend_type_id": cases["backend_type_id"],
            "cases_sha256": qi_records.digest(cases_text.encode()),
            "batch_job": 77 + n,
            "shots": total,
            "jobs": submitted,
        }
        (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
        (run / "results.json").write_text(
            json.dumps({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
        )
    return runs


def _ideal_of(series: str, template: str) -> np.ndarray:
    for case in sorted((CASES / series).glob("batch-*/cases.json")):
        for row in json.loads(case.read_text(encoding="utf-8"))["circuits"]:
            if row["kind"] == "data" and row["template"] == template:
                return np.array(row["ideal"])
    raise AssertionError(f"no {template} circuit in {series}")


def _dirs(runs: Path) -> list[Path]:
    return sorted(runs.glob("*-batch-*"))


def _moved(extra: float, qubit: int = 11, batch: str = "batch-01") -> dict[str, dict[int, tuple[float, float]]]:
    base = {q: (0.02 + 0.01 * n, 0.04 + 0.01 * n) for n, q in enumerate(REGISTER)}
    out = {f"batch-0{n}": dict(base) for n in range(4)}
    e01, e10 = base[qubit]
    out[batch][qubit] = (e01, e10 + extra)
    return out


@pytest.fixture(scope="module")
def contracted(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    root = tmp_path_factory.mktemp("contracted")
    runs = build_series(root, TUNA, range(4), 0.5, assignment=_moved(0.0))
    return {"runs": runs, "analysis": gen.analyze(_dirs(runs))}


def test_the_series_holds_ten_jobs_in_four_batches_within_the_platform_limits() -> None:
    series = json.loads((CASES / TUNA / "cases.json").read_text(encoding="utf-8"))
    sizes = [len(b["files"]) for b in series["batches"]]
    _expect(sizes == [3, 3, 3, 1], f"batch sizes {sizes}")
    shots = []
    for b in series["batches"]:
        manifest = json.loads((CASES / TUNA / b["batch"] / "cases.json").read_text(encoding="utf-8"))
        _expect(manifest["shots"] <= 131072, "shots exceed the platform maximum")
        shots.append(manifest["shots"])
        _expect(manifest["register"] == list(REGISTER), "the register is the five-qubit region")
    _expect(shots == [65536, 65536, 65536, 16384], f"shots {shots}")
    qx = json.loads((CASES / QX / "cases.json").read_text(encoding="utf-8"))
    _expect([len(b["files"]) for b in qx["batches"]] == [4], "the QX twin holds the four circuits in one batch")


def test_a_contracted_series_meets_every_decision_and_recovers_the_block_statistics(
    contracted: dict[str, Any],
) -> None:
    analysis = contracted["analysis"]
    _expect(analysis["complete"], "the full series reads as incomplete")
    json.dumps(analysis, allow_nan=False)
    _expect(analysis["all_decisions_met"], f"a decision failed: {analysis['decisions']}")
    _expect(analysis["claim_kind"] == "hardware acquisition", "claim kind")
    for name, nullity in (("ba", 2.0), ("bb", 2.0), ("b0", 0.0)):
        stats = analysis["templates"][name]["statistics"]
        got = stats["readout_corrected"]["nullity_estimate"]
        _expect(abs(got - nullity) < 1e-2, f"{name}: corrected N_hat {got}, ideal {nullity}")
        # Retention 0.5 over the 32 outcomes reads a conditional contrast of 0.5, to the grid rounding.
        _expect(abs(stats["readout_corrected"]["visibility"] - 0.5) < 1e-2, f"{name}: corrected V")
        _expect(abs(analysis["templates"][name]["coin_read_fraction"] - 0.5) < 0.05, f"{name}: coin balance")
    for device in gen.IBM_RECORDS:
        block = analysis["decisions"]["cross_platform"]["devices"][device]
        _expect(block["holds"], f"{device}: {block}")
        for name in gen.PRIMARY:
            cell = block["templates"][name]["readout_corrected"]
            _expect(cell["bins_within"] == 8 and len(cell["labels"]) == 8, f"{device} {name}: {cell['z']}")
    _expect(not analysis["drift_covariate"]["references"]["flagged"] and analysis["drift_covariate"]["stable"], "drift")


def test_a_coin_misread_scales_every_contrast_by_one_factor() -> None:
    roles = {"d0": 0, "d1": 1, "d2": 2, "selector": 3, "coin": 4}
    name = "ba"
    ideal = _ideal_of(TUNA, name)
    plus_ideal, minus_ideal = gen.arm_laws(ideal)
    sign = np.sign(gen.pcb.output_contrast(plus_ideal, minus_ideal))
    clean = gen.coin_statistics(ideal * 65536, sign)
    # A coin that reads 1 for a true 0 with probability 0.05 and 0 for a true 1 with probability 0.08.
    matrix = gen.confusion([(0.0, 0.0)] * 4 + [(0.05, 0.08)])
    blurred = gen.coin_statistics(matrix @ ideal * 65536, sign)
    ratio = np.array(blurred["c"]) / np.array(clean["c"])
    # The plus pile keeps 0.92 of its own weight against 0.05 of the minus weight, and the minus pile the mirror.
    factor = 0.92 / (0.92 + 0.05) - 0.08 / (0.08 + 0.95)
    _expect(bool(np.allclose(ratio, factor, atol=1e-9)), f"c scales by {ratio}, expected {factor}")
    _expect(bool(np.allclose(blurred["ratio"], clean["ratio"], atol=1e-9)), "c / V moved with the coin misread")
    _expect(abs(blurred["nullity_estimate"] - clean["nullity_estimate"]) < 1e-9, "N_hat moved with the coin misread")
    _expect(roles["coin"] == 4, "the coin is the fifth bit")


def test_delta_method_error_of_a_raw_contrast_is_the_binomial_error(contracted: dict[str, Any]) -> None:
    row = contracted["analysis"]["templates"]["ba"]
    raw = row["statistics"]["raw"]
    _expect(np.allclose(raw["c_se"], row["se"], rtol=2e-2), f"{raw['c_se']} against {row['se']}")


def test_a_template_with_the_other_cocycle_fails_the_cross_platform_rule(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(4), 0.5, assignment=_moved(0.0), swap=("bb", "ba"))
    analysis = gen.analyze(_dirs(runs))
    cross = analysis["decisions"]["cross_platform"]
    _expect(not cross["holds"] and not analysis["all_decisions_met"], "a bb slot carrying the ba laws passed")
    for device in gen.IBM_RECORDS:
        within = cross["devices"][device]["templates"]["bb"][gen.CROSS_STATISTIC]["bins_within"]
        _expect(within < gen.CROSS_BINS_MIN, f"{device}: {within} bins within")


def test_a_bracket_drift_is_a_stratum_and_never_a_stop(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(4), 0.5, assignment=_moved(0.17))
    analysis = gen.analyze(_dirs(runs))
    cover = analysis["drift_covariate"]
    flagged = {(p["kind"], p["from"], p["to"], p["qubit"]) for p in cover["references"]["flagged"]}
    _expect(("e10", "batch-00", "batch-01", 11) in flagged, f"{flagged}")
    _expect(analysis["all_decisions_met"], f"own-batch assignment left a decision failing: {analysis['decisions']}")
    _expect(not cover["stable"], "the cross-platform statistic did not move under the drifted bracket")
    shifts = cover["cross_platform_under_each_bracket"]["batch-01"]["max_ratio_shift_over_se"]
    _expect(max(shifts.values()) > gen.Z_RESOLVE, f"shift over se {shifts}")
    report = gate.sanity(_dirs(runs))
    _expect(bool(report["drift"]["flagged"]), "--sanity dropped the drift record")


def test_a_partial_series_reports_batches_and_drift_without_decisions(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(2), 0.5, assignment=_moved(0.0))
    analysis = gen.analyze(_dirs(runs))
    _expect(analysis["complete"] is False and analysis["batches"] == ["batch-00", "batch-01"], f"{analysis}")
    _expect("decisions" not in analysis, "a partial series carries decisions")


def test_a_short_shot_list_or_unbound_case_stops_the_load(tmp_path: Path) -> None:
    runs = build_series(tmp_path, TUNA, range(1), 0.5, short="batch-00/readout-0.cq")
    with pytest.raises(SystemExit, match="shots of the"):
        gate.sanity(_dirs(runs))
    runs = build_series(tmp_path / "b", TUNA, range(1), 0.5)
    run = _dirs(runs)[0]
    receipt = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    receipt["cases_sha256"] = "0" * 64
    (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(SystemExit, match="receipt binds"):
        gate.sanity([run])


def test_run_directories_of_the_stopped_series_are_not_read_as_this_series(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is not a run directory"):
        gate.series_of(tmp_path / "2026-11-06T221626Z-pathion_coset_block_tuna_17-batch-00")
    _expect(gate.series_of(tmp_path / f"2026-11-07T000000Z-{TUNA}-batch-00") == TUNA, "the new series name is not read")


def test_the_qx_control_passes_on_the_ideal_laws_and_fails_on_a_wrong_circuit(tmp_path: Path) -> None:
    runs = build_series(tmp_path, QX, range(1), 1.0)
    analysis = gen.analyze(_dirs(runs))
    _expect(
        analysis["claim_kind"] == old_series.CONTROL_KIND and analysis["qx_control"]["pass"],
        f"{analysis['qx_control']}",
    )
    wrong = build_series(tmp_path / "w", QX, range(1), 1.0, swap=("ba", "xor_ba"))
    _expect(not gen.analyze(_dirs(wrong))["qx_control"]["pass"], "a cocycle-free circuit in the ba slot passed")


def test_submit_next_gates_on_order_the_control_and_records_drift_without_stopping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tuna = CASES / TUNA
    runs = build_series(tmp_path / "o", TUNA, range(2), 0.5, assignment=_moved(0.17))
    shutil.rmtree(runs / f"2026-11-07T000000Z-{TUNA}-batch-00")
    qx = build_series(tmp_path / "q", QX, range(1), 1.0)
    control = tmp_path / "control.json"
    control.write_text(json.dumps(gen.analyze(_dirs(qx))), encoding="utf-8")
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="before batch-00"):
        gate.submit_next(tuna, runs, "approval", control, dry=True, client=object())
    drifting = build_series(tmp_path / "d", TUNA, range(2), 0.5, assignment=_moved(0.17))
    run_dir, receipt = gate.submit_next(tuna, drifting, "approval", control, dry=True, client=object())
    _expect(run_dir.name.endswith(f"-{TUNA}-batch-02"), f"{run_dir}")
    drift = receipt["stops"]["drift"]
    _expect(drift is not None and len(drift["flagged"]) == 1 and drift["max_abs_delta"] > 0.16, f"{receipt['stops']}")
    _expect(receipt["control"]["file"] == "control.json" and receipt["pause_seconds"] > 0, f"{receipt}")
    with pytest.raises(SystemExit, match="needs --control"):
        gate.submit_next(tuna, drifting, "approval", dry=True, client=object())
    failed = json.loads(control.read_text(encoding="utf-8"))
    failed["qx_control"]["pass"] = False
    control.write_text(json.dumps(failed), encoding="utf-8")
    with pytest.raises(SystemExit, match="QX control missed"):
        gate.submit_next(tuna, drifting, "approval", control, dry=True, client=object())
    short = build_series(tmp_path / "s", TUNA, range(1), 0.5, short="batch-00/ba.cq")
    with pytest.raises(SystemExit, match="shots of the"):
        gate.submit_next(tuna, short, "approval", control, dry=True, client=object())


def test_a_changed_or_missing_stopped_series_file_refuses_the_build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gen.verify_stopped_files.__wrapped__()
    monkeypatch.setitem(gen.STOPPED_FILES, "batch-00/raw/readout-0.cq.json", "0" * 64)
    with pytest.raises(ValueError, match="differs from the retained record"):
        gen.verify_stopped_files.__wrapped__()
    monkeypatch.setattr(gen, "STOPPED_RUN", (tmp_path / "absent").as_posix().removeprefix(gen.ROOT.as_posix() + "/"))
    with pytest.raises(ValueError, match="missing"):
        gen.verify_stopped_files.__wrapped__()


def _first_run(tmp_path: Path, **kwargs: Any) -> Path:
    return _dirs(build_series(tmp_path, TUNA, range(1), 0.5, **kwargs))[0]


def test_analyze_rejects_a_raw_bitstring_that_contradicts_the_recorded_histogram(tmp_path: Path) -> None:
    run = _first_run(tmp_path)
    raw = run / "raw" / "ba.cq.json"
    listed = json.loads(raw.read_text(encoding="utf-8"))
    listed[0] = "0" * len(listed[0]) if set(listed[0]) != {"0"} else "1" * len(listed[0])
    raw.write_text(json.dumps(listed), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the recorded outcome histogram"):
        gen.analyze([run])


def test_analyze_rejects_a_batch_listed_twice(tmp_path: Path) -> None:
    run = _first_run(tmp_path)
    twin = run.parent / f"2026-11-08T000000Z-{TUNA}-batch-00"
    shutil.copytree(run, twin)
    with pytest.raises(ValueError, match="appears twice"):
        gen.analyze([run, twin])


@pytest.mark.parametrize("remove_raw", [False, True])
def test_analyze_rejects_a_collection_that_is_not_a_qi_record(tmp_path: Path, remove_raw: bool) -> None:
    """A results.json of schema "test" (the layout an unvalidated reader accepted) and a run with no raw files both
    fail the qi_records reading before any statistic is computed."""
    run = _first_run(tmp_path)
    collection = json.loads((run / "results.json").read_text(encoding="utf-8"))
    collection["schema"] = "test"
    (run / "results.json").write_text(json.dumps(collection), encoding="utf-8")
    if remove_raw:
        shutil.rmtree(run / "raw")
    with pytest.raises(ValueError):
        gen.analyze([run])


def test_a_one_shot_deterministic_bin_resolves_nothing() -> None:
    manifest = json.loads((CASES / TUNA / "batch-00/cases.json").read_text(encoding="utf-8"))
    template = manifest["templates"]["ba"]
    ideal_c = np.array(template["ideal_c"])
    y = int(np.argmax(np.abs(ideal_c)))
    counts = np.zeros(gen.NOUT)
    # One shot per pile whose selector reads the ideal sign: a bin with zero variance and a contrast of 1.
    if ideal_c[y] > 0:
        counts[gen.HALF + y], counts[y + 8] = 1, 1
    else:
        counts[gen.HALF + y + 8], counts[y] = 1, 1
    row = gen.template_row("ba", template, counts, None, ideal_c)
    _expect(row["deterministic_bins"][y] and row["c"][y] * np.sign(ideal_c[y]) == 1.0, "the bin is deterministic")
    _expect(row["z_signed"][y] == 0.0, f"a one-shot deterministic bin decides {row['z_signed'][y]}")
    _expect(row["bins_with_ideal_sign"] == 0, "a chance run of one outcome per arm counted as a resolved bin")


def test_a_zero_contrast_resolves_neither_the_cocycle_free_rule_nor_a_finite_ratio(tmp_path: Path) -> None:
    """Selectors that never fire with the coin balanced give a zero contrast at zero standard error in ba and xor_ba,
    and a zero visibility that leaves c / V undefined: the record writes null, never nan."""
    law = np.zeros(gen.NOUT)
    law[0] = law[gen.HALF] = 0.5
    runs = build_series(tmp_path, TUNA, range(4), 0.5, laws={"ba": law, "xor_ba": law})
    analysis = gen.analyze(_dirs(runs))
    _expect(not analysis["decisions"]["cocycle_free"]["resolved"], "a zero contrast carries no sign")
    raw = analysis["templates"]["ba"]["statistics"]["raw"]
    _expect(raw["visibility"] == 0.0 and all(r is None for r in raw["ratio"]), f"{raw}")
    _expect(raw["nullity_estimate"] is None, "N_hat is undefined at zero visibility")
    json.dumps(analysis, allow_nan=False)


def test_the_out_file_refuses_a_non_finite_number(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gen, "analyze", lambda dirs: {"x": math.nan})
    monkeypatch.setattr("sys.argv", ["coin", "--analyze", str(tmp_path), "--out", str(tmp_path / "out.json")])
    with pytest.raises(ValueError, match="not JSON compliant"):
        gen.main()


def _noise_reference() -> dict[str, Any]:
    entry = {"ratio": 0.0, "se": 0.0, "se_mean": 0.0, "coset": 0}
    return {"labels": {label: entry for label in range(32)}}


def test_a_high_uncertainty_run_does_not_count_eight_of_eight_bins() -> None:
    """IBM ratios 0 against Tuna ratios 1 at a standard error of 1: every z is 1, the old rule counted 8 of 8."""
    statistics = {"ratio": [1.0] * 8, "ratio_se": [1.0] * 8}
    labels = list(range(8))
    old = blk.cross_platform(statistics, labels, _noise_reference())
    _expect(old["bins_within"] == 8, "without a design the ratio of 1 at se 1 reads as agreement")
    floored = blk.cross_platform(statistics, labels, _noise_reference(), design_se=[0.05] * 8)
    _expect(floored["bins_within"] == 0 and floored["bins_within_unfloored"] == 8, f"{floored}")
    _expect(not any(floored["precise"]), "no bin reaches the design precision")
    manifest = json.loads((CASES / TUNA / "batch-00/cases.json").read_text(encoding="utf-8"))
    design = blk.load_design(None, TUNA)
    scale = {name: 1.0 for name in manifest["templates"]}
    ibm = {device: {tag: _noise_reference() for tag in _tags(manifest)} for device in gen.IBM_RECORDS}
    decision = blk.cross_decision(
        manifest["templates"],
        manifest["labels"],
        ibm,
        lambda name: {gen.CROSS_STATISTIC: statistics},
        design,
        scale,
    )
    _expect(not decision["holds"], "eight imprecise bins held the cross-platform rule")
    _expect(decision["outcome"] == "uninformative", f"imprecise bins read {decision['outcome']}, not uninformative")


def _tags(manifest: dict[str, Any]) -> list[str]:
    return [blk.pkm.operand_tag(tuple(manifest["templates"][n]["operand"])) for n in gen.PRIMARY]


def test_a_run_coarser_than_the_design_leaves_the_null_and_the_decisions_unmet(
    contracted: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    _expect(contracted["analysis"]["decisions"]["null"]["outcome"] == "holds", "the contracted run holds the null")
    original = blk.load_design
    monkeypatch.setattr(blk, "load_design", lambda root, series: blk.scale_design(original(root, series), 1 / 3))
    coarse = gen.analyze(_dirs(contracted["runs"]))
    null = coarse["decisions"]["null"]
    _expect(null["outcome"] == "uninformative" and not null["holds"], f"{null}")
    _expect(not coarse["all_decisions_met"], "a run three times coarser than the design met every decision")
    cross = coarse["decisions"]["cross_platform"]
    _expect(cross["outcome"] == "uninformative", f"coarse cross-platform outcome {cross['outcome']}")
    _expect(contracted["analysis"]["decisions"]["cross_platform"]["outcome"] == "holds", "the contracted run holds")
    for entry in coarse["decisions"]["cross_platform"]["devices"].values():
        for cell in entry["templates"].values():
            ratio = cell[gen.CROSS_STATISTIC]
            _expect(ratio["bins_within"] == 0 and ratio["bins_within_unfloored"] > 0, f"{ratio}")
