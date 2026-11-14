"""The Ascella mesh-persistence case: retained bytes, verbatim replays, and the reading on synthetic runs.

The unmarked tests build their synthetic runs from the small verbatim cut under
tests/data/ascella_pathion_mesh_persistence/, a miniature repository root: five designs of the original QPU job and
the original simulator run (the anchor, the dark, a-h-CC, a-h-NN and b-i-NN, 12 settings and result entries each),
the frozen sim-00 and job-00 manifests restricted to those designs and their fresh counterparts (28 settings), the
two failing items they hold, the case's draw, the frozen c1_static maps and the topology cache mesh_pairs.npz of the
original QPU job. Running this file as a script, with gororoba_quantum/ and scripts/ on PYTHONPATH, rewrites the cut
from the retained records; the audit test compares the cut with them.
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import perceval as pcvl
import pytest
from perceval.serialization import deserialize, serialize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import ascella_pathion_mesh_persistence as case  # noqa: E402
import ascella_pathion_mesh_persistence_analysis as reading  # noqa: E402
import ascella_pathion_mesh_persistence_plan as printer  # noqa: E402

CASES = ROOT / "results/quandela/cases/ascella_pathion_mesh_persistence"
DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-11-07T162910Z.json"
ORIGINAL = ROOT / case.ORIGINAL_RUN


def check(condition: object, statement: str) -> None:
    if not condition:
        raise AssertionError(statement)


RUNS = {
    "sim-00": ROOT / "results/quandela/runs/2026-11-07T181127Z-sim_ascella-ascella_pathion_mesh_persistence-sim-00",
    "job-00": ROOT / "results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00",
}

EXCHANGED = ("a-h-NN-o0-i21", "b-i-NN-o0-i43")
FIXTURE = ROOT / "tests/data/ascella_pathion_mesh_persistence"
CASE_DIRECTORY = "results/quandela/cases/ascella_pathion_mesh_persistence"
DRAW_FILE = "docs/evidence/anu_qrng/draw-2026-11-07T162910Z.json"
MAPS_FILE = "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz"
MESH_FILE = "docs/evidence/pathion-kernel-map/conjectures/mesh_pairs.npz"
# Designs the cut keeps from the original job, and from the frozen manifests their replays and fresh counterparts.
FIXTURE_DESIGNS = ("anchor", "dark", "a-h-CC", "a-h-NN", "b-i-NN")
FIXTURE_FAILING_ITEMS = [["a-h-NN", 1], ["b-i-NN", 1]]
FIXTURE_ANCHOR_DRAW_INDICES = (0, 1)
ORIGINAL_KEYS = ("schema", "family", "job", "iterations", "max_samples", "max_shots", "preregistered", "settings")
FIXTURE_FILES = (
    f"{case.ORIGINAL_RUN}/cases.json",
    f"{case.ORIGINAL_RUN}/results.json",
    f"{case.ORIGINAL_SIM_RUN}/cases.json",
    f"{case.ORIGINAL_SIM_RUN}/results.json",
    f"{CASE_DIRECTORY}/sim-00/cases.json",
    f"{CASE_DIRECTORY}/job-00/cases.json",
    DRAW_FILE,
    MAPS_FILE,
    MESH_FILE,
)


def _dump(document: object, indent: int | None = None) -> bytes:
    return (json.dumps(document, indent=indent, separators=(",", ":") if indent is None else None) + "\n").encode()


def cut_documents(root: Path) -> dict[str, bytes]:
    """The fixture's files, cut from the retained records under `root`."""
    documents: dict[str, bytes] = {}
    kept_names: set[str] = set()
    for run in (case.ORIGINAL_RUN, case.ORIGINAL_SIM_RUN):
        manifest = json.loads((root / run / "cases.json").read_bytes())
        results = json.loads((root / run / "results.json").read_bytes())["iterations"]
        picked = [i for i, s in enumerate(manifest["settings"]) if s["setting"] in FIXTURE_DESIGNS]
        names = {manifest["settings"][i]["name"] for i in picked}
        if kept_names and names != kept_names:
            raise ValueError("the original QPU job and simulator run name different settings")
        kept_names = names
        cut = {key: manifest[key] for key in ORIGINAL_KEYS if key != "settings"}
        cut["settings"] = [manifest["settings"][i] for i in picked]
        documents[f"{run}/cases.json"] = _dump(cut, indent=1)
        documents[f"{run}/results.json"] = _dump({"iterations": [results[i] for i in picked]})
    for directory in ("sim-00", "job-00"):
        manifest = json.loads((root / CASE_DIRECTORY / directory / "cases.json").read_bytes())
        seeds = {s["seed_index"] for s in manifest["settings"] if s["kind"] == "fresh-anchor"}
        failing = {tuple(item) for item in FIXTURE_FAILING_ITEMS}
        picked = [
            s
            for s in manifest["settings"]
            if (s["kind"] == "replay" and s["original_name"] in kept_names)
            or (s["kind"] == "fresh-failing" and any(s["setting"] == name for name, _ in failing))
            or (s["kind"] == "fresh-anchor" and s["seed_index"] in FIXTURE_ANCHOR_DRAW_INDICES)
            or s["kind"] == "fresh-dark"
        ]
        if not set(FIXTURE_ANCHOR_DRAW_INDICES) <= seeds:
            raise ValueError("the manifest lacks a fixture fresh-anchor seed")
        manifest["settings"] = picked
        manifest["preregistered"]["failing_items"] = FIXTURE_FAILING_ITEMS
        documents[f"{CASE_DIRECTORY}/{directory}/cases.json"] = _dump(manifest, indent=1)
    for name in (DRAW_FILE, MAPS_FILE, MESH_FILE):
        documents[name] = (root / name).read_bytes()
    return documents


def main() -> int:
    for name, data in cut_documents(ROOT).items():
        path = FIXTURE / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return 0


@pytest.mark.audit
@pytest.mark.parametrize("directory", ["sim-00", "job-00"])
def test_the_submitted_cases_keep_their_bytes(directory: str) -> None:
    import hashlib

    submitted = json.loads((RUNS[directory] / "submission-state.json").read_bytes())
    for data in ((CASES / directory / "cases.json").read_bytes(), (RUNS[directory] / "cases.json").read_bytes()):
        check(submitted["cases_sha256"] == hashlib.sha256(data).hexdigest(), f"{directory} is the submitted request")


@pytest.mark.audit
def test_replays_send_the_retained_requests_and_fresh_seeds_are_new() -> None:
    manifest = json.loads((CASES / "job-00" / "cases.json").read_bytes())
    retained = {s["name"]: s for s in json.loads((ORIGINAL / "cases.json").read_bytes())["settings"]}
    replays = [s for s in manifest["settings"] if s["kind"] == "replay"]
    check(len(replays) == 52, "52 replay settings")
    for setting in replays:
        before = retained[setting["original_name"]]
        check(setting["compilation_seed"] == before["compilation_seed"], f"{setting['name']} seed")
        check(setting["circuit_params"] == before["circuit_params"], f"{setting['name']} circuit parameters")
    old = {s["compilation_seed"] for s in retained.values()}
    fresh = {s["compilation_seed"] for s in manifest["settings"] if s["kind"] != "replay"}
    check(len(fresh) == case.FRESH_ANCHOR_SEEDS + len(case.FAILING) + 1, "one fresh seed per fresh design")
    check(not fresh & old, "fresh seeds are unused by the original job")
    check(len(manifest["settings"]) == case.ITERATIONS, "iteration count")
    check(manifest["expected_seconds"] <= case.BUDGET_FRACTION * case.MAX_DURATION, "packing margin")


@pytest.mark.audit
def test_the_persistence_cutoff_is_the_frozen_plans() -> None:
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    check(record["persistence_cutoff"] == case.PERSISTENCE_CUTOFF, "cutoff equals the frozen plan")
    check(
        record["persistence_cutoff_without_platform_differing"] == case.PERSISTENCE_CUTOFF_REDUCED,
        "reduced cutoff equals the frozen plan",
    )
    check(case.PREREGISTERED["persistence_cutoff"] == case.PERSISTENCE_CUTOFF, "manifest carries the cutoff")


def test_the_aligned_mean_holds_its_error_rates() -> None:
    power = reading.aligned_power()
    check(power["design_reads_follows_mesh"] < 0.02 and power["mesh_reads_follows_design"] < 0.02, "aligned errors")


@pytest.mark.audit
def test_the_persistence_plan_rebuilds() -> None:
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    check(reading.persistence_plan() == record, "persistence_plan.json rebuilds from its draw")


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A writable copy of the fixture root that the reading module treats as the repository root."""
    root = tmp_path / "root"
    shutil.copytree(FIXTURE, root)
    manifest = json.loads((root / CASE_DIRECTORY / "sim-00" / "cases.json").read_bytes())
    monkeypatch.setattr(reading, "ROOT", root)
    monkeypatch.setattr(case, "ITERATIONS", len(manifest["settings"]))
    return root


def synthetic_run(root: Path, directory: str = "job-00", mutate: str = "") -> Path:
    """A run whose every iteration reuses the original job's entry for the same setting and orientation."""
    manifest = json.loads((root / CASE_DIRECTORY / directory / "cases.json").read_bytes())
    # A synthetic simulator run reuses the original simulator run's entries, a QPU run the original QPU job's.
    source = root / (case.ORIGINAL_SIM_RUN if directory == "sim-00" else case.ORIGINAL_RUN)
    original = json.loads((source / "results.json").read_bytes())["iterations"]
    settings = json.loads((source / "cases.json").read_bytes())["settings"]
    by_name = {s["name"]: e for s, e in zip(settings, original, strict=True)}
    by_design = {(s["setting"], s["orientation"]): e for s, e in zip(settings, original, strict=True)}
    entries = []
    for setting in manifest["settings"]:
        if setting["kind"] == "replay":
            entry = copy.deepcopy(by_name[setting["original_name"]])
        else:
            # The original job read its dark in orientation 0 only.
            key = (setting["setting"], setting["orientation"])
            entry = copy.deepcopy(by_design.get(key, by_design[(setting["setting"], 0)]))
        entry["iteration"]["compilation_seed"] = setting["compilation_seed"]
        entry["iteration"]["circuit_params"] = setting["circuit_params"]
        entries.append(entry)
    data = (root / CASE_DIRECTORY / directory / "cases.json").read_bytes()
    if mutate == "mesh":
        replay = next(i for i, s in enumerate(manifest["settings"]) if s["kind"] == "replay")
        # The palindrome ends on the same anchor mesh it starts with, so take a sign setting's mesh instead.
        sign = next(i for i, s in enumerate(manifest["settings"]) if s["role"] == "sign")
        entries[replay]["result_fields"]["computed_circuit"] = entries[sign]["result_fields"]["computed_circuit"]
    elif mutate == "platform":
        # The QPU serves a-h-CC o1 a different mesh, as the original QPU job did against the simulator.
        target = next(i for i, s in enumerate(manifest["settings"]) if s.get("original_name") == "a-h-CC-o1-i20")
        other = next(i for i, s in enumerate(manifest["settings"]) if s["role"] == "sign" and s["setting"] != "a-h-CC")
        entries[target]["result_fields"]["computed_circuit"] = entries[other]["result_fields"]["computed_circuit"]
    elif mutate == "missing":
        entries = entries[:-1]
    elif mutate == "echo-seed":
        entries[0]["iteration"]["compilation_seed"] += 1
    elif mutate == "echo-params":
        entries[0]["iteration"]["circuit_params"] = {**entries[0]["iteration"]["circuit_params"], "changed": 1}
    elif mutate == "exchange":
        # Two replays of different designs exchange their click counts; both entries stay valid observations.
        first, second = (i for i, s in enumerate(manifest["settings"]) if s.get("original_name") in EXCHANGED)
        entries[first]["counts"], entries[second]["counts"] = entries[second]["counts"], entries[first]["counts"]
    elif mutate == "duplicate":
        replays = [s for s in manifest["settings"] if s["kind"] == "replay"]
        replays[1]["original_name"] = replays[0]["original_name"]
        data = (json.dumps(manifest, indent=1) + "\n").encode()
    run = root / "run"
    run.mkdir()
    (run / "cases.json").write_bytes(data)
    (run / "results.json").write_text(json.dumps({"iterations": entries}))
    return run


def test_the_fixture_holds_exactly_its_cut_documents() -> None:
    present = sorted(p.relative_to(FIXTURE).as_posix() for p in FIXTURE.rglob("*") if p.is_file())
    check(present == sorted(FIXTURE_FILES), f"fixture files {present}")


@pytest.mark.audit
def test_the_fixture_is_the_cut_of_the_retained_records() -> None:
    cut = cut_documents(ROOT)
    for name in FIXTURE_FILES:
        check(cut[name] == (FIXTURE / name).read_bytes(), f"{name} is the cut of its retained record")


@pytest.mark.parametrize("mutate", ["", "mesh", "missing", "duplicate"])
def test_mesh_gate_refuses_a_changed_missing_or_duplicated_replay(tree: Path, mutate: str) -> None:
    gate = reading.mesh_gate(synthetic_run(tree, "sim-00", mutate))
    check(gate["passed"] == (mutate == ""), f"mesh gate with mutation {mutate!r}: {gate['problems'] or gate['misses']}")
    if mutate == "":
        check(gate["replay_compared"] == 12, "12 replay meshes compared, one per original setting")


@pytest.mark.parametrize("mutate", ["echo-seed", "echo-params"])
def test_mesh_gate_refuses_an_echoed_request_that_differs(tree: Path, mutate: str) -> None:
    gate = reading.mesh_gate(synthetic_run(tree, "sim-00", mutate))
    check(not gate["passed"], "a changed echoed request fails the gate")
    check(any("the echoed request differs" in problem for problem in gate["problems"]), f"problems {gate['problems']}")
    check(gate["replay_compared"] == 0, "no mesh is compared once the request differs")


def test_the_qpu_manifest_fails_the_simulator_gate(tree: Path) -> None:
    gate = reading.mesh_gate(synthetic_run(tree, "job-00"))
    check(not gate["passed"] and gate["problems"], "a manifest other than the frozen sim-00 case is refused")


def test_constant_or_non_finite_inputs_are_not_read() -> None:
    check(reading.finite_r(np.ones(9), np.arange(9.0)) is None, "constant input")
    check(reading.finite_r(np.array([0.1, np.nan, 0.3]), np.arange(3.0)) is None, "non-finite input")
    check(reading.finite_r(np.arange(9.0), np.arange(9.0)) == pytest.approx(1.0), "finite input reads")


def test_a_replay_of_the_original_counts_reads_fixed_per_mesh(tree: Path) -> None:
    report = reading.analyze(synthetic_run(tree))
    persistence = report["persistence"]
    check(persistence["r"] == pytest.approx(1.0), "replay r")
    check(persistence["pairs"] == 6, "three sign designs, two items each")
    check(persistence["reading"] == "fixed per mesh", "persistence reading")
    check(persistence["replay_failing"] == 2, "the two fixture failing items replay as failures")
    check(report["anchor_replay"]["ba"] == pytest.approx(case.ORIGINAL_BA, abs=1e-3), "replayed B/A")
    check(report["correction"]["failing_after"] == 0, "correction")
    # The synthetic fresh items copy the original meshes' counts, so their error follows the design by construction.
    fresh = report["fresh_failing"]
    check(fresh["fresh_raw_d"] == fresh["original_raw_d"], "fresh items copy the original items")
    check(fresh["aligned_mean"] == pytest.approx(np.mean(np.abs(fresh["original_raw_d"]))), "aligned mean")
    check(fresh["reading"] == "follows the design", "fresh failing reading")
    check(
        fresh["carried_fraction"]
        == pytest.approx(fresh["aligned_mean"] / case.PREREGISTERED["original_failing_raw_mean"]),
        "carried fraction",
    )
    control = report["within_job_control"]
    check(not control["drift_within_job"], "no drift within the job")
    for half in ("early_half_r", "late_half_r"):
        check(control[half] == pytest.approx(1.0), f"{half} reads the replay of the original counts")
    for model in ("gain", "offset"):
        check(report["frozen_maps"][model]["n_seed_blocks"] == 5, f"{model}: two failing, two anchor, one dark block")


def pearson(x: list[float], y: list[float]) -> float:
    """Pearson r from the defining sums, apart from numpy's correlation the reading uses."""
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y, strict=True))
    return sxy / (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5


def reference_mirror(rows: list[dict], settings: list[dict], calibration: dict) -> dict[tuple[str, int], float]:
    """l_hat(orientation 0) - l_hat(orientation 1) per (setting, item), written out per setting and item."""
    out: dict[tuple[str, int], float] = {}
    for name in sorted({s["setting"] for s in settings if s["role"] in ("sign", "null")}):
        by_orientation = {
            s["orientation"]: an_levels(row, calibration)
            for row, s in zip(rows, settings, strict=True)
            if s["setting"] == name and s["role"] in ("sign", "null")
        }
        if set(by_orientation) == {0, 1}:
            out[(name, 0)] = by_orientation[0]["A"] - by_orientation[1]["B"]
            out[(name, 1)] = by_orientation[0]["B"] - by_orientation[1]["A"]
    return out


def an_levels(row: dict, calibration: dict) -> dict[str, float]:
    """Calibrated level of each slot: twice the efficiency-scaled dark-subtracted clicks over all scaled clicks."""
    scaled = {
        slot: (row["slot"][slot] - calibration["dark"][slot] * row["total"]) / calibration["efficiency"][slot]
        for slot in ("A", "B")
    }
    denominator = scaled["A"] + scaled["B"] + row["failure"]
    return {slot: 2 * scaled[slot] / denominator for slot in ("A", "B")}


def test_an_exchange_of_replay_counts_reads_the_correlation_of_the_two_mirrors(tree: Path) -> None:
    report = reading.analyze(synthetic_run(tree, mutate="exchange"))
    _, o_set, o_rows = reading.original()
    _, r_set, r_rows = reading.load(tree / "run")
    r_rows, r_set = zip(*[(r, s) for r, s in zip(r_rows, r_set, strict=True) if s["kind"] == "replay"], strict=True)
    old = reference_mirror(o_rows, o_set, reading.an.calibrate(o_rows, o_set))
    new = reference_mirror(list(r_rows), list(r_set), reading.an.calibrate(list(r_rows), list(r_set)))
    keys = sorted(set(old) & set(new))
    expected = pearson([old[k] for k in keys], [new[k] for k in keys])
    check(expected < 0.99, f"the exchange moves the replay mirrors off the original's (r {expected})")
    check(report["persistence"]["pairs"] == len(keys) == 6, "six mirror pairs")
    check(report["persistence"]["r"] == pytest.approx(expected, abs=1e-9), "persistence r of the two mirrors")
    check(report["persistence"]["r"] < 0.99 and report["persistence"]["reading"] != "fixed per mesh", "reading")


HAND_CALIBRATION = {
    "dark": {"A": 0.0, "B": 0.0},
    "efficiency": {"A": 1.0, "B": 1.0},
    "anchor_raw": {"A": 1.0, "B": 1.0},
}


def hand_row(a_clicks: float, b_clicks: float) -> dict:
    """One returned iteration of 100 labeled clicks, the rest in the failure mode."""
    return {
        "returned": True,
        "slot": {"A": a_clicks, "B": b_clicks},
        "failure": 100 - a_clicks - b_clicks,
        "total": 100.0,
    }


def hand_setting(design: str, orientation: int, role: str = "sign") -> dict:
    return {"setting": design, "orientation": orientation, "role": role}


def hand_job(counts: dict[str, tuple[tuple[int, int], tuple[int, int]]]) -> tuple[list[dict], list[dict]]:
    """Rows and settings for designs given as ((A, B) clicks at orientation 0, (A, B) clicks at orientation 1)."""
    rows, settings = [], []
    for design, pair in counts.items():
        for orientation, clicks in enumerate(pair):
            rows.append(hand_row(*clicks))
            settings.append(hand_setting(design, orientation))
    return rows, settings


def test_the_mirror_is_the_orientation_zero_level_minus_the_orientation_one_level_of_the_item() -> None:
    rows, settings = hand_job({"s": ((30, 10), (25, 40))})
    # Raw level 2 x slot / 100: orientation 0 reads A 0.6 and B 0.2, orientation 1 reads A 0.5 and B 0.8. Item 0 is A
    # at orientation 0 against B at orientation 1, item 1 is B against A.
    found = reading.mirror(rows, settings, None, "a")
    check(found == pytest.approx({("s", 0): -0.2, ("s", 1): -0.3}), f"raw mirror {found}")
    rows += [hand_row(10, 10), hand_row(60, 0), hand_row(1, 1)]
    settings += [hand_setting("s", 0, "anchor"), hand_setting("lone", 0), hand_setting("n", 1, "null")]
    check(set(reading.mirror(rows, settings, None, "a")) == {("s", 0), ("s", 1)}, "anchors and one-sided designs leave")
    rows[2] = {"returned": False}
    check(reading.mirror(rows[:2], settings[:2], None, "a") == found, "the pair is unchanged without the extras")


def test_the_calibrated_mirror_divides_by_the_slot_efficiencies() -> None:
    rows, settings = hand_job({"s": ((30, 10), (20, 30))})
    calibration = {**HAND_CALIBRATION, "efficiency": {"A": 2.0, "B": 1.0}}
    # Orientation 0: scaled clicks A 15, B 10 and 60 in the failure mode, 85 in all; orientation 1: A 10, B 30, 50
    # failure, 90 in all.
    found = reading.mirror(rows, settings, calibration, "l_hat")
    expected = {("s", 0): 2 * 15 / 85 - 2 * 30 / 90, ("s", 1): 2 * 10 / 85 - 2 * 10 / 90}
    check(found == pytest.approx(expected), f"calibrated mirror {found}")


OLD_COUNTS = {"d1": ((30, 10), (25, 40)), "d2": ((20, 20), (10, 35)), "d3": ((45, 5), (40, 20))}
NEW_COUNTS = {"d1": ((28, 12), (25, 40)), "d2": ((22, 18), (10, 35)), "d3": ((42, 8), (40, 20))}
# Mirrors of OLD_COUNTS by hand, 2 x clicks / 100 at each orientation (d1: 0.6 - 0.8, 0.2 - 0.5; d2: 0.4 - 0.7,
# 0.4 - 0.2; d3: 0.9 - 0.4, 0.1 - 0.8), and of NEW_COUNTS (d1: 0.56 - 0.8, 0.24 - 0.5; d2: 0.44 - 0.7, 0.36 - 0.2;
# d3: 0.84 - 0.4, 0.16 - 0.8).
OLD_MIRROR = [-0.2, -0.3, -0.3, 0.2, 0.5, -0.7]
NEW_MIRROR = [-0.24, -0.26, -0.26, 0.16, 0.44, -0.64]


def test_the_persistence_statistic_correlates_the_original_mirror_with_the_replay_mirror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reading.an, "calibrate", lambda rows, settings: HAND_CALIBRATION)
    old_rows, old_set = hand_job(OLD_COUNTS)
    new_rows, new_set = hand_job(NEW_COUNTS)
    r, x, y = reading.persistence_r(old_rows, old_set, new_rows, new_set)
    check(np.allclose(x, OLD_MIRROR) and np.allclose(y, NEW_MIRROR), f"mirrors {x} {y}")
    check(0.9 < pearson(OLD_MIRROR, NEW_MIRROR) < 0.999, "the hand mirrors correlate, short of one")
    check(r == pytest.approx(pearson(OLD_MIRROR, NEW_MIRROR), abs=1e-12), f"r {r}")
    r_out, x_out, y_out = reading.persistence_r(old_rows, old_set, new_rows, new_set, frozenset({"d3"}))
    check(np.allclose(x_out, OLD_MIRROR[:4]) and np.allclose(y_out, NEW_MIRROR[:4]), "an excluded design leaves")
    check(r_out == pytest.approx(pearson(OLD_MIRROR[:4], NEW_MIRROR[:4]), abs=1e-12), f"reduced r {r_out}")


MAP_ROWS = [(400, 200), (380, 230), (430, 190), (360, 170), (450, 240)]
MAP_IDEAL = [0.8, 0.4]
MAP_PARTIAL = [[0.82, 0.38], [0.78, 0.41], [0.81, 0.45], [0.77, 0.40], [0.84, 0.39]]
MAP_ALIGNED = [[0.82, 0.42], [0.77, 0.43], [0.83, 0.40], [0.78, 0.41], [0.85, 0.39]]
MAP_OPPOSED = [[0.78, 0.46], [0.82, 0.38], [0.79, 0.43], [0.84, 0.41], [0.77, 0.36]]


def map_case(levels: list[list[float]]):
    rows = [{"slot": {"A": a, "B": b}, "total": 1000.0} for a, b in MAP_ROWS]
    settings = [
        {"ideal_levels": MAP_IDEAL, "kind": "fresh-anchor", "compilation_seed": seed} for seed in range(len(MAP_ROWS))
    ]
    return rows, settings, dict(enumerate(levels))


def reference_map_reading(levels: list[list[float]]) -> dict[str, float]:
    """r, the exact block-permutation p, ceiling and share of a one-kind, five-seed map test, by enumeration."""
    import itertools

    obs = [2 * clicks / 1000 - ideal for pair in MAP_ROWS for clicks, ideal in zip(pair, MAP_IDEAL, strict=True)]
    shares = [clicks / 1000 for pair in MAP_ROWS for clicks in pair]
    variance = [4 * share * (1 - share) / 1000 for share in shares]

    def centered(values: list[float]) -> list[float]:
        return [v - sum(values) / len(values) for v in values]

    o = centered(obs)
    mod = [level - ideal for pair in levels for level, ideal in zip(pair, MAP_IDEAL, strict=True)]
    r = pearson(o, centered(mod))
    count = 0
    for order in itertools.permutations(range(len(levels))):
        shuffled = [level - ideal for k in order for level, ideal in zip(levels[k], MAP_IDEAL, strict=True)]
        count += pearson(o, centered(shuffled)) >= r - 1e-12
    mean_o = sum(obs) / len(obs)
    ceiling = 1 - (sum(variance) / len(variance)) / (sum((v - mean_o) ** 2 for v in obs) / (len(obs) - 1))
    return {"r": r, "p": count / 120, "ceiling": ceiling, "share": r**2 / ceiling if r > 0 and ceiling > 0 else 0.0}


@pytest.mark.parametrize(
    ("levels", "label"),
    [(MAP_PARTIAL, "map does not carry"), (MAP_ALIGNED, "map carries"), (MAP_OPPOSED, "map does not carry")],
)
def test_the_map_score_reads_r_p_ceiling_and_share_of_the_seed_block_test(
    levels: list[list[float]], label: str
) -> None:
    expected = reference_map_reading(levels)
    rows, settings, pred = map_case(levels)
    got = reading.map_score(rows, settings, pred, np.random.default_rng(7), 4000, 0.05)
    check(got["n_readings"] == 10 and got["n_seed_blocks"] == 5, "ten readings in five seed blocks")
    check(got["r"] == pytest.approx(expected["r"], abs=1e-9), f"r {got['r']} against {expected['r']}")
    check(got["ceiling"] == pytest.approx(expected["ceiling"], abs=1e-9), "ceiling")
    check(got["share"] == pytest.approx(expected["share"], abs=1e-9), "share")
    check(got["p_one_sided"] == pytest.approx(expected["p"], abs=0.015), f"p {got['p_one_sided']} for {expected['p']}")
    check(got["reading"] == label, f"reading {got['reading']}")


def test_the_map_cases_span_the_decisions() -> None:
    partial, aligned, opposed = (reference_map_reading(m) for m in (MAP_PARTIAL, MAP_ALIGNED, MAP_OPPOSED))
    check(
        0.0 < partial["r"] < 0.9 and partial["p"] > 0.1, f"the partial case sits well short of the threshold: {partial}"
    )
    check(0.0 < aligned["r"] < 0.9 and aligned["p"] < 0.05, f"the aligned case clears it: {aligned}")
    check(
        opposed["r"] < 0.0 and opposed["share"] == 0.0 and opposed["p"] > 0.9, f"the opposed case reads none: {opposed}"
    )


def test_the_frozen_map_reads_the_topology_cache_of_its_root(tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    loaded: list[Path] = []
    load = np.load

    def recording(path: Path, *args: object, **kwargs: object):
        loaded.append(Path(str(path)))
        return load(path, *args, **kwargs)

    monkeypatch.setattr(np, "load", recording)
    run = synthetic_run(tree)
    settings = json.loads((run / "cases.json").read_bytes())["settings"]
    predicted = reading.frozen_map_prediction(run, settings, ("fresh-anchor", "fresh-failing", "fresh-dark"))
    check(len(predicted["gain"]) == len(predicted["offset"]) > 0, "both maps predict the fresh iterations")
    check(
        len(loaded) == 2 and all(tree in path.parents for path in loaded),
        f"arrays read from outside the root: {loaded}",
    )


def test_the_topology_cache_is_the_public_iteration_of_the_original_job() -> None:
    import c1_mesh

    topology, theta, phi, _ = c1_mesh.extract(FIXTURE / case.ORIGINAL_RUN)
    kinds, lo, cached_theta, cached_phi, _ = c1_mesh.cached(ORIGINAL, "pairs", (FIXTURE / MESH_FILE).parent)
    check([k for k, _ in topology] == list(kinds) and [m for _, m in topology] == list(lo), "cached topology")
    check(theta.shape[0] == phi.shape[0] == 12, "the cut holds twelve served meshes")
    for angles, cached in ((theta, cached_theta), (phi, cached_phi)):
        check(all(any(np.array_equal(row, c) for c in cached) for row in angles), "every cut mesh is a cached mesh")


def test_a_foreign_manifest_is_not_read(tree: Path) -> None:
    check(reading.analyze(synthetic_run(tree, "sim-00"))["reading"].startswith("not read"), "foreign manifest")


def test_a_qpu_mesh_differing_on_a_known_design_is_left_out(tree: Path) -> None:
    report = reading.analyze(synthetic_run(tree, mutate="platform"))
    check(report["replay_mesh_identity"]["differing_designs"] == ["a-h-CC"], "a-h-CC differs")
    check(report["persistence"]["pairs"] == 4, "the design's two mirror items leave")
    check(report["persistence"]["cutoff"] == case.PERSISTENCE_CUTOFF_REDUCED, "reduced cutoff applies")


def test_spec_check_bounds_published_imperfections() -> None:
    spec = case.spec_check(limit=2)
    check(spec["worst_level_shift_from_g2_and_indistinguishability"] < 0.005, "g2 and indistinguishability shift")
    check(spec["dark_level_shift_bound"] < 0.005, "dark count bound")


def served_circuit(convention: pcvl.BSConvention) -> pcvl.Circuit:
    """Three modes: a beam splitter and a phase shifter at the top level, then a nested two-mode block on modes 1, 2."""
    nested = pcvl.Circuit(2).add(0, pcvl.BS(convention=convention, theta=0.7)).add(1, pcvl.PS(0.9))
    circuit = pcvl.Circuit(3).add(0, pcvl.BS(convention=convention, theta=0.4)).add(0, pcvl.PS(0.2))
    return circuit.add(1, nested, merge=False)


def test_served_mesh_reads_topology_and_angles_through_the_public_iteration() -> None:
    circuit = deserialize(serialize(served_circuit(pcvl.BSConvention.Rx)))
    topology, theta, phi = reading.served_mesh(circuit, "fixture")
    check(topology == [("BS", 0), ("PS", 0), ("BS", 1), ("PS", 2)], f"topology {topology}")
    check(np.allclose(theta, [0.4, 0.7]) and np.allclose(phi, [0.2, 0.9]), f"angles {theta} {phi}")


@pytest.mark.parametrize("convention", [pcvl.BSConvention.Ry, pcvl.BSConvention.H])
def test_served_mesh_refuses_a_beam_splitter_that_is_not_rx(convention: pcvl.BSConvention) -> None:
    with pytest.raises(ValueError, match="not BS.Rx"):
        reading.served_mesh(deserialize(serialize(served_circuit(convention))), "fixture")


def test_the_successor_plan_prints_the_median_of_the_scenario_that_sets_the_cutoff(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["ascella_pathion_mesh_persistence_plan.py", "--plan"])
    check(printer.main() == 0, "--plan exits 0")
    printed = json.loads(capsys.readouterr().out)
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    median = record["r_quantiles"][printer.CUTOFF_SCENARIO]["0.5"]
    check(printed["persistence_plan"] == record, "the printed plan carries the frozen record")
    check(
        printed["predictions"]["per_mesh_fixed"]["persistence_r"]
        == f">= {case.PERSISTENCE_CUTOFF} (fixed-mesh median {median:.4f})",
        "the printed median is the random-drift scenario's",
    )
    check(printed["iterations"] == case.ITERATIONS, "iteration count")


def test_the_successor_plan_refuses_a_cutoff_that_the_scenario_does_not_set() -> None:
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    check(printer.cutoff_scenario_median(record) == record["r_quantiles"]["random"]["0.5"], "frozen record reads")
    record["persistence_cutoff"] = round(record["persistence_cutoff"] + 0.0001, 4)
    with pytest.raises(ValueError, match="first percentile"):
        printer.cutoff_scenario_median(record)
    with pytest.raises(KeyError):
        printer.cutoff_scenario_median({"r_quantiles": {"none": {"0.5": 0.99}}, "persistence_cutoff": 0.9})


if __name__ == "__main__":
    raise SystemExit(main())
