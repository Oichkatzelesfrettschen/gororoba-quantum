"""Contracts of the injected-rotation scan of the null block: the emitter and simulator against the retained b0, the
arms, the series shape, the decision on planted worlds and the analysis path on expected counts.

Fixtures hold expected counts (largest remainder, no random draw). The operating characteristics are replayed by
`--check` on demand and are outside these tests. The tests marked `audit` compare the committed case and the pinned
digest with the build or take more than 3 s of CPU; pull requests deselect them.
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


@pytest.mark.audit
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
    # File level: the header and measurement stay, and the note line and the pulse lines are the only ones that differ.
    retained_text = rs.arm_text(rs.RETAINED, place, cc.NQUBITS).split("\n")
    text = rs.arm_text(arm, place, cc.NQUBITS).split("\n")
    _expect(len(text) == len(retained_text), f"{arm}: the line count changed")
    for before, after in zip(retained_text, text, strict=True):
        if before != after:
            _expect(before.startswith(("X90 ", "//")), f"{arm}: {after} replaces {before}")
    _expect(sum(1 for a, b in zip(retained_text, text, strict=True) if a != b and a.startswith("//")) == 1, arm)


def test_the_after_worlds_repeat_the_before_worlds() -> None:
    thetas = rs.THETA_FINE[::50]
    for scope in rs.SCOPES:
        for arm in rs.ARM_NAMES:
            y = rs.forward_laws(arm, f"pulse_y_before_{scope}", thetas) - rs.forward_laws(
                arm, f"pulse_y_after_{scope}", -thetas
            )
            z = rs.forward_laws(arm, f"pulse_z_before_{scope}", thetas) - rs.forward_laws(
                arm, f"pulse_z_after_{scope}", thetas
            )
            _expect(float(np.abs(y).max()) < 1e-12, f"{arm}, {scope}: y after(-t) differs from y before(t)")
            _expect(float(np.abs(z).max()) < 1e-12, f"{arm}, {scope}: z after differs from z before")


def test_an_x_rotation_on_q4_alone_gives_the_center_arm_no_offset() -> None:
    contrast = rs.selector_contrast(rs.forward_laws(rs.CENTER, "pulse_x_before_q4", rs.THETA_FINE[::20]))
    _expect(float(np.abs(contrast).max()) < 1e-12, "an x rotation on q4's pulses moves the center contrast")


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


def _planted_x() -> list[dict[str, object]]:
    return rs.planted_batches("pulse_x_before_all", rs.truth_parameter("pulse_x_before_all", 1, rs.DESIGN_CONTRAST))


@pytest.mark.parametrize(
    ("bridge", "label"),
    [((0.001, 0.0024), "pulse_x"), ((0.0164, 0.0024), "unresolved_bridge"), (None, "unresolved_bridge")],
)
def test_a_class_label_stands_only_when_the_bridge_holds(bridge: tuple[float, float] | None, label: str) -> None:
    decision = rs.outcome(rs.decide(_planted_x(), bridge, None, transfer=True))
    _expect(decision["label"] == label, f"bridge {bridge} reads {decision['label']}")
    _expect(decision["decided"] is (label == "pulse_x"), f"bridge {bridge}: decided is {decision['decided']}")
    if label == "unresolved_bridge":
        _expect(decision["numbers"]["rx_label"] == "pulse_x", "the class of the Rx circuits is not reported")
        _expect(decision["a5_186"].startswith("unchanged"), "a failed bridge changes the ledger row")


@pytest.mark.parametrize(
    ("world", "branch", "survives"),
    [("pulse_x_before_all", 1, True), ("pulse_x_before_all", 0, False), ("pulse_x_before_q8", 1, False)],
)
def test_only_an_over_rotation_of_every_pulse_keeps_the_ledger_row(world: str, branch: int, survives: bool) -> None:
    value = rs.truth_parameter(world, branch, rs.DESIGN_CONTRAST)
    decision = rs.outcome(rs.decide(rs.planted_batches(world, value), None, None))
    _expect(decision["label"] == "pulse_x", f"planted {world} reads {decision['label']}")
    _expect(decision["x_over_rotation_of_every_pulse"] is survives, f"{world} at {value:+.4f}")
    _expect(decision["a5_186"].startswith("survives" if survives else "amended"), decision["a5_186"])


@pytest.mark.parametrize(
    ("world", "branch", "label"),
    [
        ("pulse_x_before_all", 1, "pulse_x"),
        ("pulse_y_before_all", 1, "pulse_other"),
        ("selector_flip_q12_0", 0, "readout"),
    ],
)
def test_a_world_whose_visibility_loss_spares_the_selector_reads_its_class(world: str, branch: int, label: str) -> None:
    value = rs.truth_parameter(world, branch, rs.DESIGN_CONTRAST, 1.0)
    decision = rs.decide(rs.planted_batches(world, value, mix=1.0), None, None)
    _expect(decision["label"] == label, f"planted {world} at share 1 reads {decision['label']}")
    _expect(decision["numbers"]["contraction_share"][world] == 1.0, "the fitted share is not the planted one")
    _expect(decision["numbers"]["chi2"][world] < 1.0, f"planted {world} does not fit itself")


def test_contraction_at_share_one_keeps_the_selector_and_coin_law() -> None:
    laws = rs.exact_laws()[None]
    kept = rs.contract(laws, 0.5, 1.0).reshape(-1, 4, 8).sum(-1)
    _expect(float(np.abs(kept - laws.reshape(-1, 4, 8).sum(-1)).max()) < 1e-12, "share 1 moves the selector or coin")
    whole = rs.contract(laws, 0.5, 0.0)
    _expect(float(np.abs(whole - (0.5 * laws + 0.5 / rs.NOUT)).max()) < 1e-12, "share 0 is not a uniform contraction")


def test_a_center_contrast_below_zero_reads_reversed() -> None:
    batches = _planted_x()
    for batch in batches:
        batch["contrasts"] = [-float(c) for c in batch["contrasts"]]  # type: ignore[attr-defined]
    decision = rs.outcome(rs.decide(batches, None, None))
    _expect(decision["label"] == "offset_reversed" and not decision["decided"], f"reads {decision['label']}")
    means = np.array([b["contrasts"] for b in batches])
    _expect(rs.simulated_labels(np.zeros((1, 8, 3)), means) == ["offset_reversed"], "the simulation reads otherwise")


def test_a_cz_phase_error_reads_outside_the_x_class() -> None:
    exact = rs.cz_phase_contrasts(0.0)
    _expect(max(abs(exact[a] - v) for a, v in rs.predicted_contrasts(None, 0.0).items()) < 1e-9, "phase 0 differs")
    for row in rs.unmodeled().values():
        _expect(row["label"] != "pulse_x", f"a CZ phase error reads {row['label']}")


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


def _series_shots(
    world: str, value: float, shots: int, jump: tuple[str, ...] = (), lost_qubit: int = 11, mix: float = 0.0
) -> dict[str, list[str]]:
    """Expected-count shot lists of the whole Tuna-17 series under a planted world with exact assignment readout;
    the readout-1 circuit of each batch named in `jump` reads `lost_qubit` as 0 in a quarter of its shots."""
    roles = rs.retained()["roles"]
    register = rs.retained()["region"]
    grid = rs.parameter_grid(world)
    table = rs.world_laws(world, rs.DESIGN_RETENTION, rs.ARM_NAMES, mix)
    laws = table[int(np.argmin(np.abs(grid - value)))]
    out: dict[str, list[str]] = {}
    ones = "".join("1" if cc.NQUBITS - 1 - i in register else "0" for i in range(cc.NQUBITS))
    dropped = "".join("0" if cc.NQUBITS - 1 - i == lost_qubit else c for i, c in enumerate(ones))
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


@pytest.mark.audit
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
    _expect(all(r["guard"]["admitted"] for r in report["batch_rows"].values()), "a steady readout fails the guard")


@pytest.mark.audit
def test_evaluate_reads_an_over_rotation_whose_visibility_loss_spares_the_selector() -> None:
    value = rs.truth_parameter("pulse_x_before_all", 1, rs.DESIGN_CONTRAST, 1.0)
    report = rs.evaluate(_series_shots("pulse_x_before_all", value, 32768, mix=1.0), _manifest())
    decision = report["decision"]
    _expect(decision["label"] == "pulse_x", f"reads {decision['label']}")
    _expect(decision["numbers"]["contraction_share"]["pulse_x_before_all"] >= 0.9, "the fitted share is low")
    _expect(decision["a5_186"].startswith("survives"), decision["a5_186"])


@pytest.mark.parametrize("role", ["d2", "selector", "coin"])
def test_evaluate_refuses_a_scan_kind_whose_batches_fail_the_readout_guard(role: str) -> None:
    value = rs.truth_parameter("pulse_x_before_all", 1, rs.DRIFT_CONTRAST)
    rows = rs.batch_rows(rs.TUNA_SERIES)
    names = [r["batch"] for r in rows]
    # The bracket after each q8 +-5 scan batch reads the role's qubit changed, so both batches leave the admitted set.
    jump = tuple(names[n + 1] for n, r in enumerate(rows) if r["kind"] == "q8-5")
    shots = _series_shots("pulse_x_before_all", value, 32768, jump, rs.retained()["roles"][role])
    report = rs.evaluate(shots, _manifest())
    _expect(report["decision"]["label"] == "unresolved_guard", f"reads {report['decision']['label']}")
    failed = sorted(b for b, r in report["batch_rows"].items() if not r["guard"]["admitted"])
    _expect(len(failed) >= 2, f"the guard flags {failed}")


@pytest.mark.audit
@pytest.mark.parametrize("offset", [1, 3])
def test_evaluate_withholds_the_decision_when_a_bridge_batch_is_not_admitted(offset: int) -> None:
    value = rs.truth_parameter("pulse_x_before_all", 1, rs.DRIFT_CONTRAST)
    rows = rs.batch_rows(rs.TUNA_SERIES)
    names = [r["batch"] for r in rows]
    # Offset 1 is the bracket the two bridge batches share (neither is admitted); offset 3 is the bracket after the
    # second one, which leaves the first admitted and the second not.
    bridges = [n for n, r in enumerate(rows) if r["kind"] == "bridge"]
    _expect(bridges[1] - bridges[0] == 2, "the bridge batches do not share a bracket")
    report = rs.evaluate(_series_shots("pulse_x_before_all", value, 32768, (names[bridges[0] + offset],)), _manifest())
    decision = report["decision"]
    _expect(decision["label"] == "unresolved_bridge", f"reads {decision['label']}")
    _expect(decision["numbers"]["rx_label"] == "pulse_x" and not decision["decided"], "the Rx class is not pulse_x")


@pytest.mark.audit
def test_the_committed_case_matches_the_build() -> None:
    rs.check(CASES, operating=False)
