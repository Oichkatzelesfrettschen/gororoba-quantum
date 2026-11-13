"""Contracts of the injected-rotation scan of the null block: the emitter and simulator against the retained b0, the
arms, the series shape, the decision on planted worlds and the analysis path on expected counts.

Fixtures hold expected counts (largest remainder, no random draw). The operating characteristics are replayed by
`--check` on demand and are outside these tests.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_null_rotation_scan_cases as rs
import qi_pathion_one_cz_null_cases as oc
import qi_platform

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_emitter_reproduces_the_retained_circuit() -> None:
    _expect(rs.replay_check() == oc.COIN_PINS["b0.cq"], "the emitted b0 does not carry the pinned digest")


def test_simulator_reproduces_the_retained_ideal_law() -> None:
    gap = float(np.abs(rs.forward_law(rs.RETAINED) - np.array(rs.retained()["ideal"])).max())
    _expect(gap < 1e-9, f"the simulated b0 differs from its retained ideal law by {gap}")
    same = float(np.abs(rs.forward_law(rs.CENTER) - rs.forward_law(rs.RETAINED)).max())
    _expect(same < 1e-12, "Rx(pi/2) and X90 give different exact laws")


@pytest.mark.parametrize("arm", [a for a in rs.ARM_NAMES if a != rs.RETAINED])
def test_an_arm_changes_only_the_pulse_lines(arm: str) -> None:
    region = rs.retained()["region"]
    place = {q: q for q in region}
    base, lines = rs.arm_lines(rs.RETAINED, place), rs.arm_lines(arm, place)
    _, scope, steps = rs.ARMS[arm]
    injected = () if scope is None else rs.SCOPES[scope]
    _expect(len(base) == len(lines), f"{arm}: the instruction count changed")
    for before, after in zip(base, lines, strict=True):
        if not before.startswith("X90 "):
            _expect(before == after, f"{arm}: a line other than a pulse changed: {after}")
            continue
        match = re.fullmatch(r"Rx\(([0-9.]+)\) q\[(\d+)\]", after)
        if match is None:
            raise AssertionError(f"{arm}: {after} is not an Rx pulse")
        offset = (float(match.group(1)) - math.pi / 2) / rs.STEP
        expected = steps if int(match.group(2)) in injected else 0
        _expect(abs(offset - expected) < 1e-9, f"{arm}: {after} is not {expected} grid steps from pi/2")


@pytest.mark.parametrize("series_name", [rs.TUNA_SERIES, rs.QX_SERIES])
def test_no_batch_exceeds_the_hardware_batch_size(series_name: str) -> None:
    for row in rs.batch_rows(series_name):
        _expect(
            len(row["circuits"]) <= qi_platform.HARDWARE_BATCH_CIRCUITS,
            f"{series_name}/{row['batch']} holds {len(row['circuits'])} circuits",
        )
        files = [c["file"] for c in row["circuits"]]
        _expect(len(set(files)) == len(files), f"{series_name}/{row['batch']} names a file twice")


def test_every_data_batch_sits_between_two_readout_batches() -> None:
    rows = rs.batch_rows(rs.TUNA_SERIES)
    kinds = [r["kind"] for r in rows]
    _expect(kinds[0] == "readout" and kinds[-1] == "readout", "the series does not start and end on a bracket")
    for n, kind in enumerate(kinds):
        if kind != "readout":
            _expect(kinds[n - 1] == "readout" and kinds[n + 1] == "readout", f"{rows[n]['batch']} lacks a bracket")
    scans = [(r["kind"], r["replicate"]) for r in rows if r["kind"] in rs.SCANS]
    _expect(sorted(scans) == sorted((k, r) for k in rs.SCANS for r in range(rs.REPLICATES)), "a scan batch is missing")
    for row in rows:
        if row["kind"] in rs.SCANS:
            _expect(rs.arm_of(row["circuits"][1]["file"]) == rs.CENTER, f"{row['batch']} is not centered on b0-rx")
    _expect(max(rs.row_shots(r) for r in rows) <= 131072, "a job exceeds the Tuna-17 shot limit")


@pytest.mark.parametrize(
    ("world", "branch", "guard_fails", "label"),
    [
        ("pulse_x_before_all", 1, (), "pulse_x"),
        ("pulse_x_before_all", 0, (), "pulse_x"),
        ("pulse_x_before_q8", 1, (), "pulse_x"),
        ("pulse_y_before_all", 1, (), "pulse_other"),
        ("selector_flip_q12_0", 0, (), "readout"),
        ("selector_dropout_coin_1", 0, (), "readout"),
        (None, None, (), "offset_absent"),
        ("pulse_x_before_all", 1, ("all10",), "unresolved_guard"),
    ],
)
def test_a_planted_world_reads_its_own_class(
    world: str | None, branch: int | None, guard_fails: tuple[str, ...], label: str
) -> None:
    value = rs.truth_parameter(world, branch, rs.DESIGN_CONTRAST)
    decision = rs.decide(rs.planted_batches(world, value, guard_fails), None, None)
    _expect(decision["label"] == label, f"planted {world} reads {decision['label']}")
    if world is not None and not guard_fails:
        _expect(decision["numbers"]["chi2"][world] < 1.0, f"planted {world} does not fit itself")


@pytest.mark.parametrize(
    ("best", "label"),
    [
        ({"x": 5.0, "other": 40.0, "readout": 60.0}, "pulse_x"),
        ({"x": 60.0, "other": 40.0, "readout": 5.0}, "readout"),
        ({"x": 60.0, "other": 12.0, "readout": 5.0}, "x_excluded"),
        ({"x": 20.0, "other": 40.0, "readout": 5.0}, "unresolved_both"),
        ({"x": 50.0, "other": 90.0, "readout": 95.0}, "unresolved_none"),
    ],
)
def test_classify_applies_the_separation_and_the_adequacy_bound(best: dict[str, float], label: str) -> None:
    _expect(rs.classify(best, rs.adequacy_limit(8)) == label, f"{best} does not read {label}")


def test_the_simulated_decision_equals_decide_on_the_same_contrasts() -> None:
    scans = [(k, r) for k, r in rs.batch_order() if k != "bridge"]
    value = rs.truth_parameter("selector_dropout_coin_1", 0, rs.DESIGN_CONTRAST)
    row = rs.predicted_contrasts("selector_dropout_coin_1", value)
    means = np.array([[row[a] for a in rs.scan_arms(k, r)] for k, r in scans])
    # Fixed offsets in units of the standard error, three per batch; no random draw.
    noise = np.array([[[((7 * i + 3 * n + 5 * j) % 11 - 5) / 4 for j in range(3)] for n in range(8)] for i in range(6)])
    error = 1.0 / math.sqrt(rs.SCAN_SHOTS)
    labels = rs.simulated_labels(noise, means)
    for i, label in enumerate(labels):
        batches = rs.planted_batches("selector_dropout_coin_1", value)
        for n, batch in enumerate(batches):
            batch["contrasts"] = list(means[n] + error * noise[i, n])
        _expect(rs.decide(batches, None, None)["label"] == label, f"series {i}: decide() and the simulation differ")


def _strings(law: np.ndarray, shots: int, roles: dict[str, int]) -> list[str]:
    """`shots` strings whose logical-outcome counts are the largest-remainder rounding of shots * law."""
    exact = law * shots
    counts = np.floor(exact).astype(int)
    for index in np.argsort(exact - counts)[::-1][: shots - int(counts.sum())]:
        counts[index] += 1
    listed: list[str] = []
    for outcome, count in enumerate(counts):
        bits = ["0"] * cc.NQUBITS
        for position, key in enumerate(rs.KEYS):
            if (outcome >> position) & 1:
                bits[cc.NQUBITS - 1 - roles[key]] = "1"
        listed += ["".join(bits)] * int(count)
    return listed


def _series_shots(world: str, value: float, shots: int, jump: tuple[str, ...] = ()) -> dict[str, list[str]]:
    """Expected-count shot lists of the whole Tuna-17 series under a planted world with exact assignment readout;
    the readout-1 circuit of each batch named in `jump` reads q11 as 0 in a quarter of its shots."""
    roles = rs.retained()["roles"]
    register = rs.retained()["region"]
    grid = rs.parameter_grid(world)
    table = rs.world_laws(world, rs.DESIGN_RETENTION, rs.ARM_NAMES)
    laws = table[int(np.argmin(np.abs(grid - value)))]
    out: dict[str, list[str]] = {}
    ones = "".join("1" if cc.NQUBITS - 1 - i in register else "0" for i in range(cc.NQUBITS))
    dropped = "".join("0" if cc.NQUBITS - 1 - i == rs.GUARD_QUBIT else c for i, c in enumerate(ones))
    for row in rs.batch_rows(rs.TUNA_SERIES):
        for circuit in row["circuits"]:
            key = f"{row['batch']}/{circuit['file']}"
            if circuit["file"] == "readout-0.cq":
                out[key] = ["0" * cc.NQUBITS] * shots
            elif circuit["file"] == "readout-1.cq":
                lost = shots // 4 if row["batch"] in jump else 0
                out[key] = [dropped] * lost + [ones] * (shots - lost)
            else:
                out[key] = _strings(laws[rs.ARM_NAMES.index(rs.arm_of(circuit["file"]))], shots, roles)
    return out


def _manifest() -> dict[str, object]:
    import json

    return dict(json.loads((CASES / rs.TUNA_SERIES / "batch-01" / "cases.json").read_text(encoding="utf-8")))


def test_evaluate_reads_a_planted_over_rotation_through_the_analysis_path() -> None:
    value = rs.truth_parameter("pulse_x_before_all", 1, rs.DRIFT_CONTRAST)
    report = rs.evaluate(_series_shots("pulse_x_before_all", value, 32768), _manifest())
    decision = report["decision"]
    _expect(decision["label"] == "pulse_x", f"the planted over-rotation reads {decision['label']}")
    _expect(decision["numbers"]["best_world"]["x"] == "pulse_x_before_all", "the fitted scope is not all pulses")
    _expect(decision["numbers"]["bridge_holds"] is True, "identical bridge arms read different contrasts")
    fits = decision["numbers"]["fits"]
    angles = [fits[b]["pulse_x_before_all"]["parameter"] for b in fits]
    _expect(max(abs(a - value) for a in angles) < 0.004, f"the fitted angles {angles} miss the planted {value}")
    _expect(all(r["guard"]["admitted"] for r in report["batch_rows"].values()), "a steady q11 fails the guard")


def test_evaluate_refuses_a_scan_kind_whose_batches_fail_the_q11_guard() -> None:
    value = rs.truth_parameter("pulse_x_before_all", 1, rs.DRIFT_CONTRAST)
    rows = rs.batch_rows(rs.TUNA_SERIES)
    names = [r["batch"] for r in rows]
    # The bracket after each q8 scan batch reads q11 changed, so both q8 batches leave the admitted set.
    jump = tuple(names[n + 1] for n, r in enumerate(rows) if r["kind"] == "q8")
    report = rs.evaluate(_series_shots("pulse_x_before_all", value, 32768, jump), _manifest())
    _expect(report["decision"]["label"] == "unresolved_guard", f"reads {report['decision']['label']}")
    failed = sorted(b for b, r in report["batch_rows"].items() if not r["guard"]["admitted"])
    _expect(len(failed) >= 2, f"the guard flags {failed}")


def test_the_committed_case_matches_the_build() -> None:
    rs.check(CASES, operating=False)
