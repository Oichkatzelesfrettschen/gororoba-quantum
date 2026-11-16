"""Contract for scripts/qi_tuna17_characterization_cases.py: the series obeys the provider's batch and shot
limits, the files regenerate byte for byte, the analysis recovers a T1 and a readout pair it was given and survives
a dead qubit and a partial ladder, and the sanity check stops a batch whose fixed outcome is wrong.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import qi_tuna17_characterization_cases as cases


def test_series_respects_batch_and_measurement_limits() -> None:
    series = cases.batches()
    if max(len(batch) for batch in series) > cases.BATCH_LIMIT or sum(len(batch) for batch in series) != 14:
        raise AssertionError(series)
    if series[0] != series[-1] or series[0] != ["readout-0.cq", "readout-1.cq"]:
        raise AssertionError("the series does not open and close on a readout pair")
    profile = cases.PROFILES["tuna_17"]
    # One measurement per qubit per shot: the largest count per qubit per job is the shot count.
    if max(profile["readout_shots"], profile["shots"]) > 131072:
        raise AssertionError(profile)
    texts = cases.circuits(17)
    if texts["x90-64.cq"][0].count("X90 q[16]") != 256 or texts["t1-4000.cq"][0].count("wait(4000) q[") != 17:
        raise AssertionError("a circuit does not hold its stated pulses or waits")
    if any(text.count("measure") != 1 or "qubit[17] q" not in text for text, _, _ in texts.values()):
        raise AssertionError("a circuit measures more than once or declares another register")
    longest = max(cases.job_seconds(profile, name) for batch in series for name in batch)
    if longest >= 300 or abs(longest - 11.28) > 0.01 or cases.expected_seconds(profile) != 115.8:
        raise AssertionError(f"largest job {longest} s, series {cases.expected_seconds(profile)} s")
    if cases.PROFILES["qx"]["nqubits"] > 10 or cases.PROFILES["qx"]["shots"] > 2048:
        raise AssertionError("the QX twin exceeds the emulator's limits")


def test_written_files_regenerate_and_a_changed_file_is_named(tmp_path: Path) -> None:
    cases.write(tmp_path)
    if cases.check(tmp_path):
        raise AssertionError(cases.check(tmp_path))
    directory = cases.case_directory(tmp_path, "tuna_17")
    (directory / "CASE.md").write_text("handwritten\n", encoding="utf-8")
    (directory / "batch-01" / "t1-250.cq").write_text("changed\n", encoding="utf-8")
    (directory / "stray.cq").write_text("stray\n", encoding="utf-8")
    problems = cases.check(tmp_path)
    if len(problems) != 2 or "t1-250.cq differs" not in problems[0] or "stray.cq is not generated" not in problems[1]:
        raise AssertionError(problems)
    manifest = json.loads((directory / "batch-00" / "cases.json").read_text(encoding="utf-8"))
    if manifest["backend_type_id"] != 7 or manifest["shots"] != 16384 or len(manifest["circuits"]) != 2:
        raise AssertionError(manifest)


def shots_with(probability: list[float], count: int) -> list[str]:
    """COUNT shots in which qubit q reads 1 in exactly round(probability[q] * COUNT) of them; no random draw."""
    width = len(probability)
    ones = [round(p * count) for p in probability]
    return ["".join("1" if shot < ones[width - 1 - place] else "0" for place in range(width)) for shot in range(count)]


def write_run(
    run: Path, nqubits: int, raw: dict[str, list[str]], rows: list[dict[str, Any]], backend: str = "tuna_17"
) -> None:
    """A run directory in the layout gororoba_quantum/qi_records.py validates, with RAW as the completed shots."""
    (run / "raw").mkdir(parents=True)
    shots = max(len(values) for values in raw.values())
    identity = sum(run.name.encode()) * 100
    circuits = []
    for row in rows:
        text = f"circuit {row['file']}\n"
        (run / row["file"]).write_text(text, encoding="utf-8")
        circuits.append({**row, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    manifest = {"backend": backend, "backend_type_id": 7, "nqubits": nqubits, "shots": shots, "circuits": circuits}
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    jobs = [{"file": row["file"], "job": identity + index} for index, row in enumerate(rows)]
    receipt = {
        "schema": "qi-submission-v1",
        "approval": "test fixture",
        "backend": backend,
        "backend_type_id": 7,
        "shots": shots,
        "batch_job": identity,
        "jobs": jobs,
    }
    (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    collected = []
    for entry in jobs:
        values = raw[entry["file"]]
        (run / "raw" / f"{entry['file']}.json").write_text(json.dumps(values), encoding="utf-8")
        job = {
            "id": entry["job"],
            "batch_job_id": identity,
            "number_of_shots": shots,
            "status": "completed",
            "created_on": "2026-11-15T00:00:00Z",
        }
        result = {
            "job_id": entry["job"],
            "shots_requested": shots,
            "shots_done": len(values),
            "results": dict(Counter(values)),
        }
        collected.append({"file": entry["file"], "job": job, "results": [result]})
    (run / "results.json").write_text(json.dumps({"schema": "qi-collection-v1", "jobs": collected}), encoding="utf-8")


def synthetic(tmp_path: Path, ladder: tuple[int, ...], readout_shots: int = 20000) -> list[Path]:
    """Three batches of a three-qubit series: T1 of 20 and 40 us on qubits 0 and 1, qubit 2 stuck at one value."""
    nqubits, shots, zero, one, t1_us = 3, 20000, 0.02, 0.96, [20.0, 40.0]
    readout = tmp_path / "batch-00"
    write_run(
        readout,
        nqubits,
        {
            "readout-0.cq": shots_with([zero, zero, 0.5], readout_shots),
            "readout-1.cq": shots_with([one, one, 0.5], readout_shots),
        },
        [
            {"file": "readout-0.cq", "kind": "readout", "prepared": 0},
            {"file": "readout-1.cq", "kind": "readout", "prepared": 1},
        ],
    )
    rows: list[dict[str, Any]] = []
    raw = {}
    for cycles in cases.T1_CYCLES:
        delay = cycles * cases.CYCLE_SECONDS * 1e6
        rows.append({"file": f"t1-{cycles}.cq", "kind": "t1", "wait_cycles": cycles})
        raw[f"t1-{cycles}.cq"] = shots_with(
            [zero + (one - zero) * math.exp(-delay / t1) for t1 in t1_us] + [0.5], shots
        )
    write_run(tmp_path / "batch-01", nqubits, raw, rows)
    rows, raw = [], {}
    for pulses in ladder:
        rows.append({"file": f"x90-{pulses}.cq", "kind": "x90", "pulses": pulses})
        raw[f"x90-{pulses}.cq"] = shots_with([zero + (one - zero) * 0.1 * (pulses > 0)] * 2 + [0.5], shots)
    write_run(tmp_path / "batch-03", nqubits, raw, rows)
    return [readout, tmp_path / "batch-01", tmp_path / "batch-03"]


def replace_shots(run: Path, name: str, values: list[str]) -> None:
    """Overwrite one circuit's raw shots and its recorded histogram together."""
    (run / "raw" / f"{name}.json").write_text(json.dumps(values), encoding="utf-8")
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    for row in collected["jobs"]:
        if row["file"] == name:
            row["results"][0]["results"] = dict(Counter(values))
    (run / "results.json").write_text(json.dumps(collected), encoding="utf-8")


def test_analysis_recovers_a_given_t1_and_readout_pair(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, (0, 32, 128, 256))
    retained_file = tmp_path / "retained.json"
    retained_file.write_text(
        json.dumps(
            {
                "qubits": [
                    {"qubit": 0, "readout": {"p1_given_0": 0.02, "p1_given_1": 0.96}},
                    {"qubit": 1, "readout": {"p1_given_0": 0.12, "p1_given_1": 0.96}},
                    {"qubit": 2},
                ]
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "analysis.json"
    if cases.main(["--analyze", str(out), *map(str, runs), "--retained", str(retained_file)]) != 0:
        raise AssertionError("--analyze failed")
    first, second, dead = json.loads(out.read_text(encoding="utf-8"))["qubits"]
    for row, want in ((first, 20.0), (second, 40.0)):
        if abs(row["t1"]["us"] - want) > 4 * row["t1"]["us_se"] or not row["t1_single_exponential"]:
            raise AssertionError(row["t1"])
        if abs(row["ladder_p0_at_longest"] - 0.9) > 0.02 or not row["ladder_clears"] or row["t1_beyond_window"]:
            raise AssertionError(row)
    if not first["readout_within_tolerance"] or second["readout_within_tolerance"]:
        raise AssertionError("the command-line analysis ignores the retained row")
    if not dead.get("readout_unusable") or "t1" in dead or "ladder_clears" in dead:
        raise AssertionError(f"a qubit without readout contrast received a fit: {dead}")
    if cases.retained_rows(retained_file, 17) or cases.retained_rows(tmp_path / "absent.json", 3):
        raise AssertionError("retained rows of another register or a missing file were used")
    if (
        abs(cases.chi_square_probability(3.84, 1) - 0.05) > 0.001
        or abs(cases.chi_square_probability(18.31, 10) - 0.05) > 0.001
    ):
        raise AssertionError("the chi-square tail differs from its tabulated 5% points")


def test_ladder_verdict_needs_the_256_pulse_point_and_every_point_above_the_minimum(tmp_path: Path) -> None:
    partial = cases.analyze(synthetic(tmp_path, (0, 32)))["qubits"][0]
    if "ladder_clears" in partial or "ladder_p0_at_longest" in partial or "32" not in partial["ladder_p0"]:
        raise AssertionError(f"a ladder without its 256-pulse circuit received a verdict: {partial}")
    ends = cases.analyze(synthetic(tmp_path / "ends", (0, 256)))["qubits"][0]
    if "ladder_clears" in ends or abs(ends["ladder_p0_at_longest"] - 0.9) > 0.02:
        raise AssertionError(f"a ladder without its 32 and 128 pulse circuits received a verdict: {ends}")
    runs = synthetic(tmp_path / "aliased", (0, 32, 128, 256))
    # An over-rotation that returns to P(0) = 1 at 256 pulses passes through P(0) = 0 at 128.
    replace_shots(runs[2], "x90-128.cq", shots_with([0.96, 0.96, 0.5], 20000))
    replace_shots(runs[2], "x90-256.cq", shots_with([0.02, 0.02, 0.5], 20000))
    aliased = cases.analyze(runs)["qubits"][0]
    if aliased["ladder_clears"] or aliased["ladder_p0_at_longest"] < 0.99:
        raise AssertionError(f"an aliased over-rotation cleared the ladder: {aliased}")
    # P(0) of 0.9, 0.4 and 0.7: the middle contrast is negative, and the two that remain would fit a decay.
    for pulses, value in ((32, 0.114), (128, 0.584), (256, 0.302)):
        replace_shots(runs[2], f"x90-{pulses}.cq", shots_with([value, value, 0.5], 20000))
    dipped = cases.analyze(runs)["qubits"][0]
    if dipped["ladder_clears"] or "ladder" in dipped or abs(dipped["ladder_p0"]["128"] - 0.4) > 0.01:
        raise AssertionError(f"a ladder with a negative contrast received a decay length: {dipped}")


def test_t1_error_grows_with_the_uncertainty_of_the_readout_pair(tmp_path: Path) -> None:
    wide = synthetic(tmp_path / "wide", (0,), readout_shots=200)
    tight = synthetic(tmp_path / "tight", (0,))
    few, many = cases.analyze(wide)["qubits"][0]["t1"], cases.analyze(tight)["qubits"][0]["t1"]
    if few["us_se"] < 1.5 * many["us_se"]:
        raise AssertionError(f"a readout pair of 200 shots left the T1 error at {few['us_se']} against {many['us_se']}")


def test_sanity_stops_a_batch_whose_fixed_outcome_is_wrong(tmp_path: Path) -> None:
    nqubits, shots = 17, 64
    healthy = [0.97] * nqubits
    healthy[6] = 0.16  # one weak qubit, as on 2026-10-17, stops nothing
    rows = [
        {"file": "t1-0.cq", "kind": "t1", "wait_cycles": 0},
        {"file": "t1-250.cq", "kind": "t1", "wait_cycles": 250},
    ]
    dark, lit = shots_with([0.0] * nqubits, shots), shots_with(healthy, shots)
    write_run(tmp_path / "good", nqubits, {"t1-0.cq": lit, "t1-250.cq": dark}, rows)
    if cases.sanity(tmp_path / "good"):
        raise AssertionError(cases.sanity(tmp_path / "good"))
    write_run(tmp_path / "bad", nqubits, {"t1-0.cq": dark, "t1-250.cq": lit}, rows)
    problems = cases.sanity(tmp_path / "bad")
    if len(problems) != 1 or "t1-0.cq" not in problems[0] or "want all 1" not in problems[0]:
        raise AssertionError(problems)
    write_run(tmp_path / "short", nqubits, {"t1-0.cq": lit, "t1-250.cq": lit[:-1]}, rows)
    problems = cases.sanity(tmp_path / "short")
    if len(problems) != 1 or "t1-250.cq: 63 shots done of 64" not in problems[0]:
        raise AssertionError(problems)


def test_a_run_of_another_width_backend_or_histogram_is_refused(tmp_path: Path) -> None:
    rows = [{"file": "t1-0.cq", "kind": "t1", "wait_cycles": 0}]
    # Ten-character shots under a 17-qubit manifest: bit() would read the low bits again for qubits 10 to 16.
    write_run(tmp_path / "narrow", 17, {"t1-0.cq": ["1" * 10] * 8}, rows)
    problems = cases.sanity(tmp_path / "narrow")
    if len(problems) != 1 or "want 17-bit strings" not in problems[0]:
        raise AssertionError(problems)
    write_run(tmp_path / "empty", 17, {"t1-0.cq": []}, rows)
    problems = cases.sanity(tmp_path / "empty")
    if len(problems) != 1 or "holds no shot" not in problems[0]:
        raise AssertionError(problems)
    write_run(tmp_path / "edited", 17, {"t1-0.cq": ["1" * 17] * 8}, rows)
    (tmp_path / "edited" / "raw" / "t1-0.cq.json").write_text(json.dumps(["0" * 17] * 8), encoding="utf-8")
    problems = cases.sanity(tmp_path / "edited")
    if len(problems) != 1 or "differs from the recorded outcome histogram" not in problems[0]:
        raise AssertionError(problems)
    runs = synthetic(tmp_path / "tuna", (0,))
    twin = synthetic(tmp_path / "qx", (0,))
    receipt = json.loads((twin[1] / "submission.json").read_text(encoding="utf-8"))
    manifest = json.loads((twin[1] / "cases.json").read_text(encoding="utf-8"))
    receipt["backend"] = manifest["backend"] = "QXsinglenodesimulator"
    (twin[1] / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    (twin[1] / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    again = synthetic(tmp_path / "again", (0,))
    for mixed, want in (([runs[0], twin[1]], "QXsinglenodesimulator on 3 qubits"), ([*runs, again[1]], "repeats")):
        try:
            cases.analyze(mixed)
        except SystemExit as stop:
            if want not in str(stop):
                raise AssertionError(str(stop)) from stop
        else:
            raise AssertionError(f"runs {[run.parent.name for run in mixed]} were analyzed together")


def test_retained_rows_read_the_baseline_a_newer_series_left_behind(tmp_path: Path) -> None:
    document = tmp_path / "retained.json"
    document.write_text(
        json.dumps(
            {
                "qubits": [
                    {
                        "qubit": 0,
                        "readout": {"p1_given_0": 0.01, "p1_given_1": 0.99},
                        "baseline_readout": {"p1_given_0": 0.02, "p1_given_1": 0.96},
                    },
                    {"qubit": 1, "readout": {"p1_given_0": 0.03, "p1_given_1": 0.95}},
                ]
            }
        ),
        encoding="utf-8",
    )
    found = cases.retained_rows(document, 2)
    if found != {0: {"p1_given_0": 0.02, "p1_given_1": 0.96}, 1: {"p1_given_0": 0.03, "p1_given_1": 0.95}}:
        raise AssertionError(found)
