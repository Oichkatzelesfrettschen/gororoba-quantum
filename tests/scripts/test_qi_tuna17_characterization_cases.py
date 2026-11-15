"""Contract for scripts/qi_tuna17_characterization_cases.py: the series obeys the provider's batch and shot
limits, the files regenerate byte for byte, and the analysis recovers a T1 and a readout pair it was given.
"""

from __future__ import annotations

import json
import math
import random
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
    if max(profile["readout_shots"], profile["shots"]) > 131072 or profile["readout_shots"] > 500000:
        raise AssertionError(profile)
    texts = cases.circuits(17)
    if texts["x90-64.cq"][0].count("X90 q[16]") != 256 or texts["t1-4000.cq"][0].count("wait(4000) q[") != 17:
        raise AssertionError("a circuit does not hold its stated pulses or waits")
    if any(text.count("measure") != 1 or "qubit[17] q" not in text for text, _, _ in texts.values()):
        raise AssertionError("a circuit measures more than once or declares another register")
    if cases.expected_seconds(profile) >= 300 or cases.expected_seconds(cases.PROFILES["qx"]) >= 300:
        raise AssertionError("the series estimate exceeds one job limit")
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


def shots_with(probability: list[float], count: int, rng: random.Random) -> list[str]:
    width = len(probability)
    return [
        "".join("1" if rng.random() < probability[width - 1 - place] else "0" for place in range(width))
        for _ in range(count)
    ]


def test_analysis_recovers_a_given_t1_and_readout_pair(tmp_path: Path) -> None:
    rng = random.Random(20261115)
    nqubits, shots, zero, one, t1_us = 2, 20000, 0.02, 0.96, [20.0, 40.0]
    run = tmp_path / "run"
    (run / "raw").mkdir(parents=True)
    rows: list[dict[str, Any]] = [
        {"file": "readout-0.cq", "kind": "readout"},
        {"file": "readout-1.cq", "kind": "readout"},
    ]
    raw = {
        "readout-0.cq": shots_with([zero] * nqubits, shots, rng),
        "readout-1.cq": shots_with([one] * nqubits, shots, rng),
    }
    for cycles in cases.T1_CYCLES:
        delay = cycles * cases.CYCLE_SECONDS * 1e6
        rows.append({"file": f"t1-{cycles}.cq", "kind": "t1", "wait_cycles": cycles})
        raw[f"t1-{cycles}.cq"] = shots_with([zero + (one - zero) * math.exp(-delay / t1) for t1 in t1_us], shots, rng)
    for pulses in (0, 256):
        rows.append({"file": f"x90-{pulses}.cq", "kind": "x90", "pulses": pulses})
        raw[f"x90-{pulses}.cq"] = shots_with([zero + (one - zero) * 0.1 * (pulses > 0)] * nqubits, shots, rng)
    (run / "cases.json").write_text(
        json.dumps({"nqubits": nqubits, "shots": shots, "circuits": rows}), encoding="utf-8"
    )
    for name, values in raw.items():
        (run / "raw" / f"{name}.json").write_text(json.dumps(values), encoding="utf-8")
    retained = {0: {"p1_given_0": zero, "p1_given_1": one}, 1: {"p1_given_0": zero + 0.1, "p1_given_1": one}}
    found = cases.analyze([run], retained)
    first, second = found["qubits"]
    for row, want in ((first, 20.0), (second, 40.0)):
        if abs(row["t1"]["us"] - want) > 4 * row["t1"]["us_se"] or not row["t1_single_exponential"]:
            raise AssertionError(row["t1"])
        if abs(row["ladder_p0_at_longest"] - 0.9) > 0.02 or not row["ladder_clears"]:
            raise AssertionError(row)
    if not first["readout_within_tolerance"] or second["readout_within_tolerance"]:
        raise AssertionError("the readout tolerance verdict ignores the retained row")
    if (
        abs(cases.chi_square_probability(3.84, 1) - 0.05) > 0.001
        or abs(cases.chi_square_probability(18.31, 10) - 0.05) > 0.001
    ):
        raise AssertionError("the chi-square tail differs from its tabulated 5% points")
