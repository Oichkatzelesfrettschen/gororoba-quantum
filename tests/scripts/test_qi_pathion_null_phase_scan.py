"""Contracts of the q12 phase and q4 angle scan of the null block: the arms against the predecessor's center, the
forward model, the series shape, the decision on planted worlds and the analysis path on expected counts.

Fixtures hold expected counts (largest remainder, no random draw). The tests marked `audit` compare the committed
case with the build or run the whole analysis path; pull requests deselect them.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_null_phase_scan_cases as ps
import qi_pathion_null_rotation_scan_cases as rs
import qi_platform

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _place() -> dict[int, int]:
    return {q: q for q in rs.retained()["region"]}


def test_the_center_arm_is_the_predecessors_center_arm() -> None:
    ps.center_check()
    _expect(np.array_equal(ps.forward_law(ps.CENTER), rs.forward_law(rs.CENTER)), "the center laws differ")


@pytest.mark.parametrize("arm", [a for a in ps.ARM_NAMES if a != ps.CENTER])
def test_an_arm_rewrites_one_qubit(arm: str) -> None:
    center = ps.arm_lines(ps.CENTER, _place())
    lines = ps.arm_lines(arm, _place())
    q4_steps, z12_steps = ps.ARMS[arm]
    _expect((q4_steps == 0) != (z12_steps == 0), f"{arm} rewrites both qubits or neither")
    if z12_steps:
        frame = f"Rz({z12_steps * ps.STEP!r}) q[12]"
        _expect([line for line in lines if line != frame] == center, f"{arm} changes a line beside its Rz")
        _expect(lines.count(frame) == 5, f"{arm} holds {lines.count(frame)} injected Rz, not one per q12 pulse")
        for n, line in enumerate(lines):
            if line == frame:
                _expect(lines[n + 1].startswith("Rx(") and lines[n + 1].endswith("q[12]"), "an Rz precedes no pulse")
    else:
        changed = [(a, b) for a, b in zip(center, lines, strict=True) if a != b]
        _expect(len(changed) == 8, f"{arm} changes {len(changed)} lines, not q4's 8 pulses")
        _expect(all(b == f"{rs.rx_text(q4_steps)} q[4]" for _, b in changed), f"{arm} changes a line off q4")


def test_the_q4_plus_ten_arm_repeats_the_predecessors_arm() -> None:
    place = _place()
    _expect(
        ps.arm_lines("b0-rx-q4-p10", place) == rs.arm_lines("b0-rx-q4-p10", place),
        "the +10 degree q4 arm differs from the retained arm",
    )


@pytest.mark.parametrize("steps", [-6, -2, 2, 6])
def test_an_injected_frame_cancels_the_opposite_q12_phase(steps: int) -> None:
    arm = next(a for a, (_, z12) in ps.ARMS.items() if z12 == steps)
    gap = np.abs(ps.forward_law(arm, "q12_phase", -steps * ps.STEP) - ps.forward_law(ps.CENTER)).max()
    _expect(gap < 1e-12, f"{arm} under the opposite phase differs from the exact center by {gap}")


def test_exact_gates_give_an_even_curve_with_no_offset() -> None:
    matrix = ps.predecessor_matrix()
    row = ps.truth_row("exact", 0.0, matrix)
    _expect(abs(row[ps.CENTER]["contrast"]) < 1e-9, "exact gates read an offset at the center")
    for size in ("10", "30"):
        minus, plus = row[f"b0-rx-z12-m{size}"]["contrast"], row[f"b0-rx-z12-p{size}"]["contrast"]
        _expect(
            abs(minus - plus) < 0.05 * minus and minus > 0.01, f"the exact +-{size} degree arms read {minus} and {plus}"
        )


@pytest.mark.parametrize("series_name", [ps.TUNA_SERIES, ps.QX_SERIES])
def test_no_batch_exceeds_the_hardware_batch_size(series_name: str) -> None:
    rows = ps.batch_rows(series_name)
    _expect(all(len(r["circuits"]) <= qi_platform.HARDWARE_BATCH_CIRCUITS for r in rows), "a batch is too large")
    files = [c["file"] for r in rows for c in r["circuits"] if c["kind"] == "data"]
    _expect({ps.arm_of(f) for f in files} == set(ps.ARM_NAMES), "the series misses an arm")


def test_the_series_has_the_drafted_size_and_brackets() -> None:
    rows = ps.batch_rows(ps.TUNA_SERIES)
    design = ps.design()
    _expect((design["batches"], design["jobs"], design["shots_total"]) == (17, 42, 3_735_552), f"design {design}")
    for n, row in enumerate(rows):
        if row["kind"] == "readout":
            continue
        _expect(
            rows[n - 1]["kind"] == "readout" and rows[n + 1]["kind"] == "readout", f"{row['batch']} lacks a bracket"
        )
        _expect(ps.CENTER in [ps.arm_of(c["file"]) for c in row["circuits"]], f"{row['batch']} holds no center")
    kinds = [(r["kind"], r["replicate"]) for r in rows if r["kind"] != "readout"]
    _expect(kinds[4:] == [(k, 1) for k, _ in reversed(kinds[:4])], "the mirror round is not the forward round reversed")


@pytest.mark.parametrize("truth", list(ps.TRUTHS))
def test_a_planted_truth_reads_its_label(truth: str) -> None:
    matrix = ps.predecessor_matrix()
    world, theta, flip, label = ps.TRUTHS[truth]
    decision = ps.decide(ps.planted_batches(ps.truth_row(world, theta, matrix, flip)), lambda b: matrix)
    _expect(decision["label"] == label, f"{truth} reads {decision['label']}")
    if world != "exact":
        fitted = decision["numbers"]["parameters"][world].values()
        _expect(max(abs(v - theta) for v in fitted) < 0.004, f"the fitted {list(fitted)} miss the planted {theta}")


def test_a_readout_offset_beside_exact_gates_is_not_read_as_a_phase() -> None:
    labels = {label for world, _, flip, label in ps.TRUTHS.values() if world == "exact" and flip}
    _expect(len(labels) > 0, "no readout truth is planted")
    _expect(not labels & {"q12_phase", "coupler_phase", "phase_mixed"}, f"readout truths read {labels}")


def test_a_phase_after_each_q12_pulse_gives_the_laws_of_one_before() -> None:
    for arm in ps.ARM_NAMES:
        gap = np.abs(ps.forward_law(arm, ps.AFTER_PULSE, -0.18) - ps.forward_law(arm, "q12_phase", -0.18)).max()
        _expect(gap < 1e-12, f"{arm}: the two placements differ by {gap}")


@pytest.mark.parametrize(("near", "far"), [("q12_phase", "coupler_phase"), ("coupler_phase", "q12_phase")])
def test_z12_batches_of_two_mechanisms_read_no_deciding_label(near: str, far: str) -> None:
    matrix = ps.predecessor_matrix()
    size = {"q12_phase": -0.18, "coupler_phase": -0.25}
    first = ps.planted_batches(ps.truth_row(near, size[near], matrix))
    second = ps.planted_batches(ps.truth_row(far, size[far], matrix))
    mixed = [b if a["kind"] == "z12-30" else a for a, b in zip(first, second, strict=True)]
    label = ps.decide(mixed, lambda b: matrix)["label"]
    _expect(label not in ("q12_phase", "coupler_phase"), f"two mechanisms read {label}")


def test_a_missing_z12_kind_reads_unresolved_guard() -> None:
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row("q12_phase", -0.18, matrix))
    for batch in batches:
        if batch["kind"] == "z12-30":
            batch["admitted"] = False
    _expect(ps.decide(batches, lambda b: matrix)["label"] == "unresolved_guard", "a lost z12 kind is not refused")


def test_the_parabola_finds_the_injected_phase_of_least_contrast() -> None:
    matrix = ps.predecessor_matrix()
    row = ps.truth_row("q12_phase", -0.18, matrix)
    error = 1.0 / math.sqrt(ps.SCAN_SHOTS)
    points = [(5.0 * ps.ARMS[a][1], row[a]["contrast"], error) for a in ps.ARM_NAMES if ps.ARMS[a][0] == 0]
    least = ps.parabola_minimum(points)
    _expect(least is not None, "the parabola has no least point")
    if least is not None:
        _expect(abs(least["phi_degrees"] - math.degrees(0.18)) < 1.5, f"the least point is {least['phi_degrees']}")


def _strings(law: np.ndarray, shots: int, roles: dict[str, int]) -> list[str]:
    """`shots` strings whose logical-outcome counts are the largest-remainder rounding of shots * law."""
    exact = law * shots
    counts = np.floor(exact).astype(int)
    for index in np.argsort(exact - counts)[::-1][: shots - int(counts.sum())]:
        counts[index] += 1
    listed: list[str] = []
    for outcome, count in enumerate(counts):
        bits = ["0"] * cc.NQUBITS
        for position, key in enumerate(ps.KEYS):
            if (outcome >> position) & 1:
                bits[cc.NQUBITS - 1 - roles[key]] = "1"
        listed += ["".join(bits)] * int(count)
    return listed


def _series_shots(world: str, theta: float, shots: int, jump: tuple[str, ...] = ()) -> dict[str, list[str]]:
    """Expected-count shot lists of the whole Tuna-17 series under a planted world at retention 0.5 with exact
    assignment readout; the readout-1 circuit of each batch named in `jump` reads q11 as 0 in a quarter of its
    shots."""
    roles = rs.retained()["roles"]
    register = rs.retained()["region"]
    out: dict[str, list[str]] = {}
    ones = "".join("1" if cc.NQUBITS - 1 - i in register else "0" for i in range(cc.NQUBITS))
    dropped = "".join("0" if cc.NQUBITS - 1 - i == 11 else c for i, c in enumerate(ones))
    for row in ps.batch_rows(ps.TUNA_SERIES):
        for circuit in row["circuits"]:
            key = f"{row['batch']}/{circuit['file']}"
            if circuit["file"] == "readout-0.cq":
                out[key] = ["0" * cc.NQUBITS] * shots
            elif circuit["file"] == "readout-1.cq":
                lost = shots // 4 if row["batch"] in jump else 0
                out[key] = [dropped] * lost + [ones] * (shots - lost)
            else:
                law = 0.5 * ps.forward_law(ps.arm_of(circuit["file"]), world, theta) + 0.5 / ps.NOUT
                out[key] = _strings(law, shots, roles)
    return out


def _manifest() -> dict[str, object]:
    return dict(json.loads((CASES / ps.TUNA_SERIES / "batch-01" / "cases.json").read_text(encoding="utf-8")))


@pytest.mark.audit
def test_evaluate_reads_a_planted_q12_phase_through_the_analysis_path() -> None:
    report = ps.evaluate(_series_shots("q12_phase", -0.18, 131072), _manifest())
    decision = report["decision"]
    _expect(decision["label"] == "q12_phase", f"the planted phase reads {decision['label']}")
    fitted = decision["numbers"]["parameters"]["q12_phase"].values()
    _expect(max(abs(v + 0.18) for v in fitted) < 0.006, f"the fitted phases {list(fitted)} miss -0.18")
    least = report["reported"]["z12_parabola"]
    _expect(abs(least["phi_degrees"] - math.degrees(0.18)) < 2.0, f"the least point is {least['phi_degrees']} degrees")
    _expect(report["reported"]["q4_line"]["slope_per_degree"] < 0, "the q4 line of a negative q12 phase rises")
    _expect(decision["a5_186"].startswith("changes"), "a deciding label leaves the ledger row unchanged")
    ratios = report["reported"]["visibility_ratio"]
    _expect(set(ratios) == set(ps.ARM_NAMES) - {ps.CENTER}, "a visibility ratio is missing")
    _expect(all(len(r["measured"]) == 2 and 0 < r["exact"] <= 1 for r in ratios.values()), f"ratios {ratios}")


@pytest.mark.audit
def test_evaluate_refuses_a_z12_kind_whose_d2_readout_jumps() -> None:
    rows = ps.batch_rows(ps.TUNA_SERIES)
    # The two z12-30 batches share the bracket between them, so a jump in that one bracket fails both.
    shared = next(rows[n + 1]["batch"] for n, r in enumerate(rows) if r["kind"] == "z12-30")
    report = ps.evaluate(_series_shots("q12_phase", -0.18, 32768, (shared,)), _manifest())
    lost = [b for b, r in report["batch_rows"].items() if not r["guard"]["admitted"]]
    _expect([report["batch_rows"][b]["kind"] for b in lost] == ["z12-30", "z12-30"], f"the jump fails {lost}")
    _expect(report["decision"]["label"] == "unresolved_guard", f"the jump reads {report['decision']['label']}")


@pytest.mark.audit
def test_the_committed_case_matches_the_build() -> None:
    ps.check(CASES)
