"""The Garnet follow-up case: fused generic compile, sedenion sign-row oracles, the mutation and null arms.

Tests that read the retained case carry audit; the others build their input here. The analyzer tests run on a
synthetic case written below: the arm names of the retained case, a model device of per-qubit readout flips and
geometric Grover retention, and run directories laid out by synthetic_run."""

import json
import re
import shutil
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import iqm_garnet_followup as followup
import iqm_grover_line as grover
import numpy as np
import pytest
from iqm_jobs import CASE_SCHEMA, dump

import garnet_followup_analysis as analysis
import iqm_records
import sedenion_sign_oracle as sed


def test_fusion_keeps_the_cz_sequence_and_the_distribution() -> None:
    path = ["QA", "QB", "QC"]
    generic = grover.generic("101", path, "g")
    merged = followup.fused(generic, path, "f")
    cz = [op["locus"] for op in generic["instructions"] if op["name"] == "cz"]
    if [op["locus"] for op in merged["instructions"] if op["name"] == "cz"] != cz:
        raise AssertionError("fusion moved a CZ")
    if followup.count(merged, "prx") != 38 or followup.count(generic, "prx") != 68:
        raise AssertionError("prx counts changed")
    if np.max(np.abs(followup.ideal(merged, path) - followup.ideal(generic, path))) > 1e-9:
        raise AssertionError("fusion changed the outcome distribution")


def test_every_row_carries_the_parities_of_odd_overlap() -> None:
    for m in range(1, 16):
        eighths = sed.phase_eighths(sed.row_bits(m))
        if set(eighths) != {s for s in range(1, 16) if sed.parity(s & m)}:
            raise AssertionError(f"m={m}: parities {sorted(eighths)}")


def test_a_flipped_sign_moves_the_walsh_distribution() -> None:
    # The mutation test: the observable must change when the sign table changes.
    bits = sed.row_bits(5)
    flipped = list(bits)
    flipped[3] ^= 1
    if np.array_equal(sed.walsh_distribution(bits), sed.walsh_distribution(flipped)):
        raise AssertionError("one flipped sign leaves the Walsh distribution unchanged")


@pytest.mark.parametrize("m", followup.ROWS)  # type: ignore[untyped-decorator, unused-ignore]
def test_row_truncation_and_identity_share_one_cz_sequence(m: int) -> None:
    square = ["QA", "QB", "QC", "QD"]
    circuits = {kind: followup.sedenion_circuit(m, kind, square, kind) for kind in ("row", "trunc", "id")}
    loci = {kind: [op["locus"] for op in c[0]["instructions"] if op["name"] == "cz"] for kind, c in circuits.items()}
    if not loci["row"] == loci["trunc"] == loci["id"] or len(loci["row"]) != 8:
        raise AssertionError(f"e_{m}: CZ sequences {loci}")
    row = followup.ideal(circuits["row"][0], square)
    top = int(np.argmax(row))
    if abs(row[top] - 9 / 16) > 1e-9 or abs(followup.ideal(circuits["trunc"][0], square)[top] - 0.25) > 1e-9:
        raise AssertionError(f"e_{m}: row peak {row[top]}")
    if followup.ideal(circuits["id"][0], square)[0] < 1 - 1e-9:
        raise AssertionError(f"e_{m}: the identity oracle leaves |0000>")


@pytest.mark.audit
def test_retained_case_mirrors_its_contrasts() -> None:
    case = json.loads((followup.ROOT / "results/iqm/cases" / followup.CASE / "cases.json").read_text())
    for job in case["jobs"]:
        names = [c["file"].split("/")[-1].removesuffix(".json").rsplit("-c", 1)[0] for c in job["circuits"]]
        for stem in {n for n in names if n.startswith(("m101-k1", "r-m", "s5-", "s10-"))}:
            positions = [i for i, n in enumerate(names) if n == stem]
            if sum(positions) * 2 != (len(names) - 1) * len(positions):
                raise AssertionError(f"{job['job']}: {stem} positions {positions} are not mirrored")


@pytest.mark.audit
def test_each_row_null_shares_the_row_cz_list() -> None:
    case_dir = followup.ROOT / "results/iqm/cases" / followup.CASE

    def loci(name: str) -> list[list[str]]:
        circuit = json.loads((case_dir / "circuits" / f"{name}.json").read_text())
        return [op["locus"] for op in circuit["instructions"] if op["name"] == "cz"]

    for m in followup.ROWS:
        if not loci(f"s{m}-row-c0") == loci(f"s{m}-trunc-c0") == loci(f"s{m}-id-c0") == loci(f"s{m}-id-c1"):
            raise AssertionError(f"e_{m}: the null or truncation runs another CZ list")


@pytest.mark.audit
def test_an_altered_prediction_fails_the_case_binding(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    shutil.copytree(followup.ROOT / "results/iqm/cases" / followup.CASE, case_dir)
    iqm_records.load_job(case_dir, "grover")
    prediction = case_dir / "prediction.json"
    prediction.write_text(prediction.read_text().replace('"z_resolve": 3.0', '"z_resolve": 2.0'))
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(case_dir, "grover")


def test_a_bound_prediction_is_checked_on_a_synthetic_case(tmp_path: Path) -> None:
    circuit = json.dumps({"name": "c", "instructions": []}).encode()
    prediction = b'{"decisions": {}}\n'
    case = {
        "schema": iqm_records.CASE_SCHEMA,
        "case": "synthetic",
        "prediction_sha256": iqm_records.sha256(prediction),
        "jobs": [{"job": "j", "circuits": [{"file": "circuits/c.json", "sha256": iqm_records.sha256(circuit)}]}],
    }
    (tmp_path / "circuits").mkdir()
    (tmp_path / "circuits" / "c.json").write_bytes(circuit)
    (tmp_path / "cases.json").write_text(json.dumps(case))
    (tmp_path / "prediction.json").write_bytes(prediction)
    iqm_records.load_job(tmp_path, "j")
    (tmp_path / "prediction.json").write_bytes(b'{"decisions": {"z": 2}}\n')
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(tmp_path, "j")
    (tmp_path / "prediction.json").unlink()
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(tmp_path, "j")


def test_a_verdict_resolves_at_three_standard_errors() -> None:
    if [analysis.verdict_of(z) for z in (3.0, 2.99, -3.0, -2.99)] != [
        "positive",
        "unresolved",
        "negative",
        "unresolved",
    ]:
        raise AssertionError("verdict_of misreads the resolution threshold")
    if analysis.verdict_of(3.0, strict=True) != "unresolved" or analysis.verdict_of(3.01, strict=True) != "positive":
        raise AssertionError("the role rule is strict")
    with pytest.raises(analysis.AnalysisError, match="zero variance"):
        analysis.z_of(0.1, 0.0)


def test_outcome_strings_read_character_q_as_bit_q() -> None:
    if (
        analysis.outcome_index("1001") != 9
        or analysis.outcome_key(9, 4) != "1001"
        or analysis.outcome_index("110") != 3
    ):
        raise AssertionError("outcome strings are not little-endian")
    with pytest.raises(analysis.AnalysisError, match="bit string"):
        analysis.outcome_index("10a")


def test_synthetic_shots_keep_their_total_without_a_generator() -> None:
    counts = followup.largest_remainder([0.5, 0.3, 0.2 - 1e-12, 1e-12], 3424)
    if sum(counts) != 3424 or counts != followup.largest_remainder([0.5, 0.3, 0.2 - 1e-12, 1e-12], 3424):
        raise AssertionError(f"largest remainder gave {counts}")
    moved = followup.shifted({"a": 0.5, "b": 0.5}, "a", "b", 0.1)
    if abs(moved["a"] - 0.4) > 1e-12 or abs(sum(moved.values()) - 1.0) > 1e-12:
        raise AssertionError(f"shifted gave {moved}")


@pytest.mark.audit
def test_analysis_decides_synthetic_acquisitions() -> None:
    followup.analysis_checks()


@pytest.mark.audit
def test_analyze_writes_one_record_from_both_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    case_dir = followup.RETAINED_CASE.parent / followup.CASE
    runs = [followup.synthetic_run(case_dir, tmp_path / job, job) for job in ("sedenion", "grover")]
    out = tmp_path / "analysis.json"
    monkeypatch.setattr(sys, "argv", ["iqm_garnet_followup.py", "analyze", *map(str, runs), "--out", str(out)])
    if followup.main() != 0:
        raise AssertionError("analyze failed")
    record = json.loads(out.read_text())
    if record["schema"] != analysis.SCHEMA or record["not_run"] or "exploratory" not in record:
        raise AssertionError(f"record keys {sorted(record)}")
    required = {"prx_load_generic", "prx_load_line", "cz_sequence", "depth_law_101", "depth_law_011"}
    if not required | {"role_or_qubit", "sedenion_5", "sedenion_10"} <= set(record["decisions"]):
        raise AssertionError(f"decisions {sorted(record['decisions'])}")
    single = analysis.analyze(runs[:1], case_dir)
    if single["not_run"] != ["grover"] or "sedenion_5" not in single["decisions"]:
        raise AssertionError("a single sedenion run does not analyze alone")


# The synthetic case: every arm of the retained case, with a prediction the test writes from its own model device.
FLIP = {"QB20": 0.02, "QB16": 0.03, "QB17": 0.01, "QB11": 0.015, "QB12": 0.025}
FORWARD = ["QB20", "QB16", "QB17"]
REVERSED = FORWARD[::-1]
SQUARE = ["QB11", "QB12", "QB17", "QB16"]
GROVER_SHOTS = 2000
SEDENION_SHOTS = 1000
PEAKS = {5: "1001", 10: "0101"}
RETENTION = 0.95
DECAY = 0.9
LOAD = {"fused": 1.02, "padded": 1.0, "generic": 0.985}
SEDENION_RETENTION = 0.85


def flipped(p: np.ndarray, locus: list[str]) -> np.ndarray:
    """The distribution after an independent symmetric readout flip on each measured qubit."""
    for q, name in enumerate(locus):
        e = FLIP[name]
        moved = (1 - e) * p
        for index in range(len(p)):
            moved[index ^ (1 << q)] += e * p[index]
        p = moved
    return p


def as_dict(p: np.ndarray, width: int) -> dict[str, float]:
    return {analysis.outcome_key(i, width): float(v) for i, v in enumerate(p)}


def grover_vector(name: str) -> tuple[np.ndarray, list[str], str | None]:
    locus = REVERSED if name.startswith("r-") else FORWARD
    if name.startswith("ro-"):
        basis = np.zeros(8)
        basis[analysis.outcome_index(name[3:])] = 1.0
        return flipped(basis, locus), locus, None
    marked = "000" if name == "k0" else re.match(r"r?-?m(\d{3})", name).group(1)  # type: ignore[union-attr]
    k = 0 if name == "k0" else int(re.search(r"-k(\d)", name).group(1))  # type: ignore[union-attr]
    load = next((v for kind, v in LOAD.items() if kind in name), 1.0)
    ideal = grover.ideal_probability(k)
    peak = 1 / 8 + RETENTION * DECAY**k * load * (ideal - 1 / 8)
    p = np.full(8, (1 - peak) / 7)
    p[analysis.outcome_index(marked)] = peak
    return flipped(p, locus), locus, marked


def sedenion_vector(name: str) -> tuple[np.ndarray, list[str]]:
    if name.startswith("ro4-"):
        basis = np.zeros(16)
        basis[analysis.outcome_index(name[4:])] = 1.0
        return flipped(basis, SQUARE), SQUARE
    m, kind = re.match(r"s(\d+)-(row|trunc|id)", name).groups()  # type: ignore[union-attr]
    peak = analysis.outcome_index(PEAKS[int(m)])
    ideal = np.zeros(16)
    if kind == "row":
        ideal[peak] = 9 / 16
        for t in range(1, 8):
            ideal[peak ^ t] = 1 / 16
    elif kind == "trunc":
        for t in range(4):
            ideal[peak ^ t] = 1 / 4
    else:
        ideal[0] = 1.0
    return flipped(SEDENION_RETENTION * ideal + (1 - SEDENION_RETENTION) / 16, SQUARE), SQUARE


def arm_names() -> dict[str, list[str]]:
    grover_arms = ["k0", *(f"m011-k{k}" for k in (1, 2, 3)), "m101-k2", "m101-k3"]
    for stem, copies in (("m101-k1", 4), ("m101-k1-fused", 4), ("m101-k1-generic", 4), ("m101-k1-padded", 4)):
        grover_arms += [f"{stem}-c{c}" for c in range(copies)]
    grover_arms += [f"r-m011-k1-c{c}" for c in range(2)] + [f"r-m101-k1-c{c}" for c in range(4)]
    grover_arms += [f"ro-{analysis.outcome_key(c, 3)}" for c in range(8)]
    sedenion_arms = [f"ro4-{analysis.outcome_key(c, 4)}" for c in range(16)]
    sedenion_arms += [f"s{m}-{kind}-c{c}" for m in PEAKS for kind in ("row", "trunc", "id") for c in range(2)]
    return {"grover": grover_arms, "sedenion": sedenion_arms}


def wrong(p: np.ndarray, locus: list[str], marked: str, qubit: str) -> float:
    position = locus.index(qubit)
    return float(sum(v for i, v in enumerate(p) if analysis.outcome_key(i, 3)[position] != marked[position]))


def model_difference(name: str) -> float:
    """D = w(QB17) - w(QB20) of one model arm, computed from its distribution."""
    p, locus, marked = grover_vector(name)
    if marked is None:
        raise AssertionError(name)
    return wrong(p, locus, marked, "QB17") - wrong(p, locus, marked, "QB20")


def write_case(case_dir: Path) -> dict[str, Any]:
    (case_dir / "circuits").mkdir(parents=True)
    names = arm_names()
    arms: dict[str, Any] = {}
    rows = []
    for job, stems in names.items():
        circuits = []
        for name in stems:
            if job == "grover":
                p, locus, marked = grover_vector(name)
                arm: dict[str, Any] = {"job": job, "locus": locus, "predicted": as_dict(p, 3)}
                if marked is not None:
                    arm |= {"marked": marked, "predicted_marked": float(p[analysis.outcome_index(marked)])}
            else:
                p, locus = sedenion_vector(name)
                arm = {"job": job, "locus": locus, "predicted": as_dict(p, 4)}
                if name.startswith("s"):
                    m = int(name[1 : name.index("-")])
                    arm |= {"m": m, "row_peak": PEAKS[m]}
            arms[name] = arm
            circuit = {"name": name, "instructions": [{"name": "measure", "locus": locus, "args": {"key": "m"}}]}
            data = dump(circuit)
            (case_dir / "circuits" / f"{name}.json").write_text(data, encoding="utf-8")
            circuits.append({"file": f"circuits/{name}.json", "sha256": iqm_records.sha256(data.encode())})
        shots = GROVER_SHOTS if job == "grover" else SEDENION_SHOTS
        rows.append({"job": job, "shots": shots, "options": {"heralding_mode": "zeros"}, "circuits": circuits})
    for m, peak in PEAKS.items():
        ideal = {analysis.outcome_key(analysis.outcome_index(peak) ^ t, 4): 1 / 16 for t in range(1, 8)}
        arms[f"s{m}-row-c0"]["ideal"] = ideal | {peak: 9 / 16}

    def depth(marked: str) -> dict[str, Any]:
        lam = {}
        for k in (1, 2, 3):
            stem = f"m{marked}-k{k}"
            name = stem + "-c0" if stem == "m101-k1" else stem
            lam[k] = (arms[name]["predicted_marked"] - 1 / 8) / (grover.ideal_probability(k) - 1 / 8)
        f = lam[3] - lam[2] ** 2 / lam[1]
        return {
            "predicted": f,
            "predicted_lambda": {str(k): v for k, v in lam.items()},
            "resolvable_deviation": 0.12,
            "se_at_planned_shots": 0.04,
        }

    contrast = {"predicted": 0.0, "predicted_z": 0.0, "se_at_planned_shots": 0.006}
    decisions: dict[str, Any] = {
        "prx_load_generic": contrast,
        "prx_load_line": contrast,
        "cz_sequence": contrast,
        "depth_law_101": depth("101"),
        "depth_law_011": depth("011"),
        "role_or_qubit": {
            "model": {
                "forward": {"D": model_difference("m101-k1-c0")},
                "reversed": {"D": model_difference("r-m101-k1-c0")},
            }
        },
        "k0_reference": "the corrected uniformity Wald statistic of k0",
        "z_resolve": 3.0,
    }
    for m in PEAKS:
        decisions[f"sedenion_{m}"] = {**contrast, "null_floor": 0.002, "row_minus_null_z": 40.0}
    prediction = {"arms": arms, "calibration_set": "model-calibration-set", "decisions": decisions}
    prediction_bytes = dump(prediction)
    (case_dir / "prediction.json").write_text(prediction_bytes, encoding="utf-8")
    case = {
        "schema": CASE_SCHEMA,
        "case": analysis.CASE,
        "prediction_sha256": iqm_records.sha256(prediction_bytes.encode()),
        "jobs": rows,
    }
    (case_dir / "cases.json").write_text(dump(case), encoding="utf-8")
    return prediction


class World:
    """The synthetic case, a counter for run directories and the analysis of its model device."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.case_dir = base / "case"
        self.prediction = write_case(self.case_dir)
        self.count = 0

    def run(self, job: str, plant: followup.Plant | None = None, **extra: Any) -> Path:
        self.count += 1
        return followup.synthetic_run(self.case_dir, self.base / f"run{self.count}", job, plant, **extra)

    def decisions(self, job: str, plant: followup.Plant | None = None) -> dict[str, Any]:
        result: dict[str, Any] = analysis.analyze([self.run(job, plant)], self.case_dir)["decisions"]
        return result


@pytest.fixture(scope="module")  # type: ignore[untyped-decorator, unused-ignore]
def world(tmp_path_factory: pytest.TempPathFactory) -> Iterator[World]:
    yield World(tmp_path_factory.mktemp("garnet-followup-case"))


@pytest.fixture(scope="module")  # type: ignore[untyped-decorator, unused-ignore]
def model(world: World) -> dict[str, Any]:
    record: dict[str, Any] = analysis.analyze([world.run("grover"), world.run("sedenion")], world.case_dir)
    return record


def test_model_device_resolves_only_what_the_model_resolves(world: World, model: dict[str, Any]) -> None:
    decisions = model["decisions"]
    if model["schema"] != analysis.SCHEMA or model["not_run"]:
        raise AssertionError(f"the model record lacks a job: {model['not_run']}")
    for key, (first, second) in {
        "prx_load_generic": ("m101-k1-fused-c0", "m101-k1-generic-c0"),
        "prx_load_line": ("m101-k1-c0", "m101-k1-padded-c0"),
        "cz_sequence": ("m101-k1-padded-c0", "m101-k1-fused-c0"),
    }.items():
        expected = (
            world.prediction["arms"][first]["predicted_marked"] - world.prediction["arms"][second]["predicted_marked"]
        )
        if abs(decisions[key]["raw"] - expected) > 0.002 or decisions[key]["verdict"] != "unresolved":
            raise AssertionError(f"model device, {key}: {decisions[key]} against {expected}")
    for marked in ("101", "011"):
        depth = decisions[f"depth_law_{marked}"]
        if abs(depth["f_raw"] - depth["model_f"]) > 0.003 or depth["verdict"] != "inside":
            raise AssertionError(f"model device, depth {marked}: {depth}")
        if abs(depth["corrected_f"]) > 0.01:
            raise AssertionError(f"model device, corrected f of a geometric law {marked}: {depth['corrected_f']}")
    role = decisions["role_or_qubit"]
    if abs(role["forward"]["D"] - model_difference("m101-k1-c0")) > 0.002 or not role["reading"].startswith("open"):
        raise AssertionError(f"model device, role {role}")
    if not decisions["bit_order"]["holds"]:
        raise AssertionError(f"model device, bit order {decisions['bit_order']}")
    for m in PEAKS:
        row = decisions[f"sedenion_{m}"]
        if row["verdict"] != "resolved" or row["row_minus_truncation_z"] < 10 or row["row_minus_null_z"] < 20:
            raise AssertionError(f"model device, sedenion {m}: {row}")
        if row["most_frequent_row_string"] != PEAKS[m] or not row["row_peak_is_unique_mode"]:
            raise AssertionError(f"model device, sedenion {m} mode: {row}")


def test_a_generic_gain_resolves_positive_and_leaves_the_line_contrast(world: World) -> None:
    def gain(name: str, p: dict[str, float]) -> dict[str, float]:
        return followup.shifted(p, "101", "000", 0.06) if name.startswith("m101-k1-generic") else p

    planted = world.decisions("grover", gain)
    if planted["prx_load_generic"]["verdict"] != "positive" or planted["prx_load_line"]["verdict"] != "unresolved":
        raise AssertionError(f"planted gain: {planted['prx_load_generic']} {planted['prx_load_line']}")


def test_a_fused_loss_resolves_negative(world: World) -> None:
    def loss(name: str, p: dict[str, float]) -> dict[str, float]:
        return followup.shifted(p, "101", "000", 0.06) if name.startswith("m101-k1-fused") else p

    planted = world.decisions("grover", loss)["prx_load_generic"]
    if planted["verdict"] != "negative" or "falsified" not in planted["reading"]:
        raise AssertionError(f"planted loss: {planted}")


def test_a_bent_depth_law_leaves_the_model_for_its_own_mark(world: World) -> None:
    def bent(name: str, p: dict[str, float]) -> dict[str, float]:
        return followup.shifted(p, "101", "000", 0.2) if name == "m101-k3" else p

    planted = world.decisions("grover", bent)
    if not planted["depth_law_101"]["verdict"].startswith("outside") or planted["depth_law_011"]["verdict"] != "inside":
        raise AssertionError(f"planted depth: {planted['depth_law_101']} {planted['depth_law_011']}")


def test_a_reversed_bit_order_fails_the_bit_order_check(world: World) -> None:
    def swapped(name: str, p: dict[str, float]) -> dict[str, float]:
        if name.startswith("m011-k"):
            return followup.shifted(p, "011", "110", 0.8 * p["011"])
        return p

    check = world.decisions("grover", swapped)["bit_order"]
    if check["holds"]:
        raise AssertionError(f"planted bit order: {check}")


def role_reading(world: World, forward: tuple[str, str], reverse: tuple[str, str], amount: float) -> dict[str, Any]:
    def plant(name: str, p: dict[str, float]) -> dict[str, float]:
        if name.startswith("m101-k1-c"):
            return followup.shifted(p, forward[0], forward[1], amount)
        if name.startswith("r-m101-k1"):
            return followup.shifted(p, reverse[0], reverse[1], amount)
        return p

    decision, _ = analysis.role_decision(analysis.read_job(world.run("grover", plant), world.case_dir))
    return decision


def test_a_role_reading_follows_the_qubit_or_the_role(world: World) -> None:
    # Forward arms: character 2 is QB17 and character 0 is QB20. Reversed arms: character 0 is QB17.
    moved = role_reading(world, ("101", "100"), ("101", "100"), 0.05)
    if not moved["forward"]["D"] > 0 > moved["reversed"]["D"] or not moved["reading"].startswith("moves with"):
        raise AssertionError(f"planted roles: {moved}")
    kept = role_reading(world, ("101", "100"), ("101", "001"), 0.05)
    if not kept["reading"].startswith("with the qubits"):
        raise AssertionError(f"planted qubits: {kept['reading']}")
    open_reversed = role_reading(world, ("101", "100"), ("101", "111"), 0.05)
    if not open_reversed["reading"].startswith("open") or not open_reversed["forward_resolved"]:
        raise AssertionError(f"a reversed D that does not resolve: {open_reversed}")


def test_a_row_equal_to_its_truncation_or_null_stays_unresolved(world: World) -> None:
    def peakless(name: str, p: dict[str, float]) -> dict[str, float]:
        if name.startswith("s5-row"):
            return dict(world.prediction["arms"][name.replace("row", "trunc")]["predicted"])
        if name.startswith("s10-row"):
            return dict(world.prediction["arms"][name.replace("row", "id")]["predicted"])
        return p

    rows = world.decisions("sedenion", peakless)
    if rows["sedenion_5"]["verdict"] != "unresolved" or abs(rows["sedenion_5"]["row_minus_truncation"]) > 0.01:
        raise AssertionError(f"a row equal to its truncation: {rows['sedenion_5']}")
    if rows["sedenion_10"]["verdict"] != "unresolved" or abs(rows["sedenion_10"]["row_minus_null"]) > 0.01:
        raise AssertionError(f"a row equal to its null: {rows['sedenion_10']}")


def test_sedenion_rows_assemble_in_row_order(world: World, model: dict[str, Any]) -> None:
    job = analysis.read_job(world.run("sedenion"), world.case_dir)
    decisions, exploratory = analysis.sedenion_analysis(job)
    if list(decisions) != [f"sedenion_{m}" for m in analysis.ROWS] or list(exploratory)[:2] != list(decisions):
        raise AssertionError(f"rows assembled as {list(decisions)} and {list(exploratory)}")
    if decisions != {k: model["decisions"][k] for k in decisions}:
        raise AssertionError("the same run analyzed twice decides differently")


def test_the_analyzer_refuses_runs_it_cannot_decide_from(world: World) -> None:
    refusals = {
        "not a": lambda: world.run("grover", qc="garnet:mock"),
        "prediction.json": lambda: world.run("grover", prediction_edit="unbound"),
        "another prediction digest": lambda: world.run("grover", prediction_edit="rebound"),
        "another calibration set": lambda: world.run("grover", calibration="another-calibration-set"),
    }
    for fragment, make in refusals.items():
        directory = make()
        with pytest.raises((analysis.AnalysisError, iqm_records.RecordError), match=fragment):
            analysis.analyze([directory], world.case_dir)
    with pytest.raises(analysis.AnalysisError, match="second run of job grover"):
        analysis.analyze([world.run("grover"), world.run("grover")], world.case_dir)
    with pytest.raises(analysis.AnalysisError, match="no run to analyze"):
        analysis.analyze([], world.case_dir)
