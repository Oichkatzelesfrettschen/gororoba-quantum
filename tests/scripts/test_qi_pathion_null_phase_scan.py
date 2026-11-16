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


# Fast decisions fit the contraction shares alone; the damped noise models need tables that take minutes to build,
# and the audit tests run the full fit.
FAST = "contraction"
# Decisions that test the label logic hold the readout flip at 0 (one fit instead of one per flip of FLIP_GRID); the
# flip tests offer the planted flip beside 0.
NO_FLIP = (0.0,)


def test_the_plain_arm_is_the_predecessors_center_arm() -> None:
    ps.center_check()
    _expect(np.array_equal(ps.forward_law(ps.PLAIN), rs.forward_law(rs.CENTER)), "the plain laws differ")
    _expect(np.abs(ps.forward_law(ps.CENTER) - rs.forward_law(rs.CENTER)).max() < 1e-12, "the padding changes a law")


def _added(lines: list[str], plain: list[str]) -> list[int]:
    """Positions of the lines a padded arm holds beyond the plain arm, by a greedy in-order alignment."""
    added, j = [], 0
    for n, line in enumerate(lines):
        if j < len(plain) and line == plain[j]:
            j += 1
        else:
            added.append(n)
    if j != len(plain):
        raise AssertionError("the padded arm drops a line of the plain arm")
    return added


def test_every_padded_arm_holds_nine_rz_at_the_same_places() -> None:
    plain = ps.arm_lines(ps.PLAIN, _place())
    center = ps.arm_lines(ps.CENTER, _place())
    places = _added(center, plain)
    _expect(len(places) == 9 and len(center) == len(plain) + 9, f"the center adds {len(places)} lines")
    for n in places:
        line = center[n]
        _expect(line in ("Rz(0.0) q[12]", "Rz(0.0) q[8]"), f"the padding adds {line}")
        if line.endswith("q[12]"):
            _expect(center[n + 1].startswith("Rx(") and center[n + 1].endswith("q[12]"), "a q12 Rz precedes no pulse")
        else:
            _expect(center[n - 1] in ("CZ q[8], q[12]", "CZ q[12], q[8]"), "a q8 Rz follows no CZ of coupler 8-12")
    _expect(sum(center[n].endswith("q[12]") for n in places) == 5, "the q12 padding is not one Rz per pulse")
    for arm in ps.ARM_NAMES:
        if arm != ps.PLAIN:
            lines = ps.arm_lines(arm, _place())
            _expect(len(lines) == len(center), f"{arm} holds {len(lines)} lines")
            _expect(all(lines[n].startswith("Rz(") for n in places), f"{arm} moves its Rz")


@pytest.mark.parametrize("arm", [a for a in ps.ARM_NAMES if a not in (ps.CENTER, ps.PLAIN)])
def test_an_arm_rewrites_one_quantity(arm: str) -> None:
    center = ps.arm_lines(ps.CENTER, _place())
    lines = ps.arm_lines(arm, _place())
    q4_steps, z12_steps, z8c_steps = ps.ARMS[arm]
    _expect(sum(bool(x) for x in ps.ARMS[arm]) == 1, f"{arm} rewrites more than one quantity")
    changed = [(a, b) for a, b in zip(center, lines, strict=True) if a != b]
    if z12_steps:
        _expect(changed == [("Rz(0.0) q[12]", f"Rz({z12_steps * ps.STEP!r}) q[12]")] * 5, f"{arm} changes {changed}")
    elif z8c_steps:
        _expect(changed == [("Rz(0.0) q[8]", f"Rz({z8c_steps * ps.STEP!r}) q[8]")] * 4, f"{arm} changes {changed}")
    else:
        _expect(len(changed) == 8, f"{arm} changes {len(changed)} lines, not q4's 8 pulses")
        _expect(all(b == f"{rs.rx_text(q4_steps)} q[4]" for _, b in changed), f"{arm} changes a line off q4")


@pytest.mark.parametrize("arm", [a for a, (_, z12, z8c) in ps.ARMS.items() if z12 or z8c])
def test_an_injected_rz_cancels_the_opposite_phase(arm: str) -> None:
    _, z12, z8c = ps.ARMS[arm]
    world, steps = ("q12_phase", z12) if z12 else (ps.Q8_PHASE, z8c)
    gap = np.abs(ps.forward_law(arm, world, -steps * ps.STEP) - ps.forward_law(ps.CENTER)).max()
    _expect(gap < 1e-12, f"{arm} under the opposite phase differs from the exact center by {gap}")


def test_the_noisy_model_reduces_to_the_pure_one() -> None:
    for arm in ("b0-rxz-z12-m30", "b0-rxz-z8c-p10", "b0-rxz-q4-m5"):
        pure = ps.forward_law(arm, "coupler_phase", 0.2)
        mixed = ps.forward_law(arm, "coupler_phase", 0.2, (0.0, 0.0, 1e-15, 0.0))
        _expect(np.abs(pure - mixed).max() < 1e-12, f"{arm}: the density matrix differs from the state vector")
    damped = ps.forward_law(ps.CENTER, "exact", 0.0, ps.CZ_DAMPING)
    _expect(abs(damped.sum() - 1) < 1e-12, "a damped law does not sum to one")
    _expect(np.abs(damped - ps.forward_law(ps.CENTER)).max() > 1e-3, "CZ damping leaves the law in place")


def test_exact_gates_give_an_even_curve_with_no_offset() -> None:
    matrix = ps.predecessor_matrix()
    row = ps.truth_row("exact", 0.0, matrix)
    _expect(abs(row[ps.CENTER]["contrast"]) < 1e-9, "exact gates read an offset at the center")
    for kind in ("z12-m10", "z12-m30"):
        minus = row[f"b0-rxz-{kind}"]["contrast"]
        plus = row[f"b0-rxz-{kind.replace('-m', '-p')}"]["contrast"]
        _expect(abs(minus - plus) < 0.5 * max(abs(minus), 1e-3), f"the exact {kind} arms read {minus} and {plus}")


@pytest.mark.parametrize("series_name", [ps.TUNA_SERIES, ps.QX_SERIES])
def test_no_batch_exceeds_the_hardware_batch_size(series_name: str) -> None:
    rows = ps.batch_rows(series_name)
    _expect(all(len(r["circuits"]) <= qi_platform.HARDWARE_BATCH_CIRCUITS for r in rows), "a batch is too large")
    files = [c["file"] for r in rows for c in r["circuits"] if c["kind"] == "data"]
    _expect({ps.arm_of(f) for f in files} == set(ps.ARM_NAMES), "the series misses an arm")
    for row in rows:
        names = [c["file"] for c in row["circuits"]]
        _expect(len(set(names)) == len(names), f"{row['batch']} repeats a file name")


def test_the_series_has_its_size_and_brackets() -> None:
    rows = ps.batch_rows(ps.TUNA_SERIES)
    design = ps.design()
    _expect((design["batches"], design["jobs"], design["shots_total"]) == (29, 72, 6_488_064), f"design {design}")
    for n, row in enumerate(rows):
        if row["kind"] == "readout":
            continue
        _expect(
            rows[n - 1]["kind"] == "readout" and rows[n + 1]["kind"] == "readout", f"{row['batch']} lacks a bracket"
        )
        _expect(ps.CENTER in [ps.arm_of(c["file"]) for c in row["circuits"]], f"{row['batch']} holds no center")
    kinds = [(r["kind"], r["replicate"]) for r in rows if r["kind"] != "readout"]
    half = len(kinds) // 2
    _expect(kinds[half:] == [(k, r + 1) for k, r in reversed(kinds[:half])], "the mirror round is not reversed")
    counts = {k: sum(1 for kind, _ in kinds if kind == k) for k in ps.SCANS}
    _expect(counts == {"bridge": 2, "z12-10": 2, "z12-30": 2, "z8c-10": 4, "q4-near": 2, "q4-far": 2}, f"{counts}")


@pytest.mark.parametrize("truth", [t for t, v in ps.TRUTHS.items() if v[4] is not None and not any(v[3])])
def test_a_planted_truth_reads_its_label(truth: str) -> None:
    matrix = ps.predecessor_matrix()
    world, theta, flip, noise, label = ps.TRUTHS[truth]
    batches = ps.planted_batches(ps.truth_row(world, theta, matrix, flip, noise=noise))
    decision = ps.decide(batches, lambda b: matrix, FAST, flips=(0.0, flip) if flip else NO_FLIP)
    _expect(decision["label"] == label, f"{truth} reads {decision['label']}")
    if world in ps.ERROR_WORLDS:
        fitted = decision["numbers"]["parameters"][world].values()
        _expect(max(abs(v - theta) for v in fitted) < 0.004, f"the fitted {list(fitted)} miss the planted {theta}")


def test_the_case_tables_are_the_rendering_of_the_prediction_record() -> None:
    root = CASES / ps.TUNA_SERIES
    record = json.loads((root / "prediction.json").read_text(encoding="utf-8"))
    text = (root / "CASE.md").read_text(encoding="utf-8")
    _expect(ps.render_case(text, record) == text, "a CASE.md table differs from prediction.json")
    stale = text.replace(ps.TABLE_END, "| stale | row |\n" + ps.TABLE_END, 1)
    _expect(stale != text and ps.render_case(stale, record) == text, "a stale table row is not replaced")


def test_a_world_that_misfits_needs_a_wider_separation() -> None:
    """The separation scales with the least error world's chi-square per degree of freedom once that exceeds 1: a
    planted q12 phase whose outer arms move 2 standard errors apart needs the scaled gap, not SEPARATION."""
    matrix = ps.predecessor_matrix()
    world, theta, flip, noise, _ = ps.TRUTHS["q12 phase -0.18 rad"]
    batches = ps.planted_batches(ps.truth_row(world, theta, matrix, flip, noise=noise))
    for batch in batches:
        batch["contrasts"] = [
            c + 2 * s * e for c, e, s in zip(batch["contrasts"], batch["errors"], (1, 0, -1), strict=True)
        ]
    numbers = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)["numbers"]
    chi2 = numbers["chi2"]
    lead = min(ps.ERROR_WORLDS, key=lambda w: chi2[w])
    values = [ps.batch_values(b) for b in batches if b["kind"] in ps.DECIDING_KINDS]
    scale = chi2[lead] / ps.freedom(lead, values, flip_fitted=False)
    _expect(scale > 1, f"the shifted series fits {lead} at {scale} per degree of freedom")
    _expect(
        math.isclose(numbers["separation_needed"], round(ps.SEPARATION * scale, 3), abs_tol=2e-3),
        f"separation {numbers['separation_needed']} against {ps.SEPARATION} x {scale}",
    )


@pytest.mark.parametrize(("world", "theta"), [("exact", 0.0), ("q12_phase", -0.18)])
def test_a_fitted_readout_flip_restores_the_planted_world(world: str, theta: float) -> None:
    """A selector flip of 0.036 beside exact gates or a q12 phase: with the flip held at 0 no world is adequate;
    with 0.036 offered, the planted world reads its label at that flip and the bounds lose one degree of freedom."""
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row(world, theta, matrix, 0.036))
    fixed = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)
    fitted = ps.decide(batches, lambda b: matrix, FAST, flips=(0.0, 0.036))
    label = "exact_parabola" if world == "exact" else world
    _expect(fixed["label"] == "none_adequate", f"the fixed flip reads {fixed['label']}")
    _expect(fitted["label"] == label, f"the fitted flip reads {fitted['label']}")
    _expect(fitted["numbers"]["readout_flip"][world] == 0.036, f"the flip reads {fitted['numbers']['readout_flip']}")
    _expect(fitted["numbers"]["flip_at_grid_end"] != [], "a flip at the grid's end is not reported")
    for w in ps.WORLDS:
        drop = fixed["numbers"]["adequacy_limit"][w] - fitted["numbers"]["adequacy_limit"][w]
        _expect(0 < drop < 5, f"{w}: the bound moves by {drop}")


def test_exact_parabola_misreads_a_phase_and_not_exact_gates() -> None:
    _expect("exact_parabola" in ps.wrong_labels("q12 phase -0.18 rad"), "a phase read as exact gates is not counted")
    _expect("exact_parabola" in ps.wrong_labels(next(iter(ps.MIXED))), "a mixed series read as exact is not counted")
    _expect("exact_parabola" not in ps.wrong_labels("exact gates"), "exact gates read as exact gates is counted")
    _expect("q12_phase" not in ps.wrong_labels("q12 phase -0.18 rad"), "a phase's own label is counted")


def test_clopper_pearson_bounds_a_clean_count() -> None:
    _expect(math.isclose(ps.upper_bound(0, 5000), 1 - 0.05 ** (1 / 5000), rel_tol=1e-9), "the 5,000-series bound")
    _expect(math.isclose(ps.upper_bound(0, 500), 1 - 0.05 ** (1 / 500), rel_tol=1e-9), "the 500-series bound")
    _expect(ps.upper_bound(3, 500) > ps.upper_bound(0, 500), "a count does not raise the bound")
    _expect(ps.upper_bound(5, 5) == 1.0, "a full count is not bounded by 1")


def test_a_readout_offset_beside_exact_gates_is_not_read_as_a_phase() -> None:
    labels = {v[4] for v in ps.TRUTHS.values() if v[0] == "exact" and v[2]}
    _expect(len(labels) > 0, "no readout truth is planted")
    _expect(not labels & {*ps.ERROR_WORLDS, "phase_mixed"}, f"readout truths read {labels}")


def test_a_phase_after_each_q12_pulse_gives_the_laws_of_one_before() -> None:
    for arm in ps.ARM_NAMES:
        gap = np.abs(ps.forward_law(arm, ps.AFTER_PULSE, -0.18) - ps.forward_law(arm, "q12_phase", -0.18)).max()
        _expect(gap < 1e-12, f"{arm}: the two placements differ by {gap}")


@pytest.mark.parametrize("name", list(ps.MIXED))
def test_batches_of_two_mechanisms_read_no_deciding_label(name: str) -> None:
    matrix = ps.predecessor_matrix()
    label = ps.decide(ps.scenario_batches(name), lambda b: matrix, FAST, flips=NO_FLIP)["label"]
    _expect(label not in ps.ERROR_WORLDS, f"{name} reads {label}")


@pytest.mark.parametrize("kind", ps.DECIDING_KINDS)
def test_a_missing_deciding_kind_reads_unresolved_guard(kind: str) -> None:
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row("q12_phase", -0.18, matrix))
    for batch in batches:
        if batch["kind"] == kind:
            batch["admitted"] = False
    _expect(ps.decide(batches, lambda b: matrix, FAST)["label"] == "unresolved_guard", f"a lost {kind} is not refused")


def test_a_series_no_world_reaches_writes_its_decision_with_null_statistics() -> None:
    """A center visibility above every world's reachable range gives infinite chi-squares; the numbers report them as
    null beside the worlds and the reason, and the analysis report serializes under allow_nan=False."""
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row("q12_phase", -0.18, matrix))
    reachable = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)
    _expect("unavailable" not in reachable["numbers"], "a reachable series reports an unavailable statistic")
    for batch in batches:
        batch["center_visibility"] = 1.5
    decision = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)
    numbers = decision["numbers"]
    _expect(decision["label"] == "none_adequate", f"an unreachable series reads {decision['label']}")
    _expect(all(v is None for v in numbers["chi2"].values()), f"chi2 reads {numbers['chi2']}")
    _expect(numbers["separation_needed"] is None, f"separation_needed reads {numbers['separation_needed']}")
    _expect(
        all(v is None for rows in numbers["batch_chi2"].values() for v in rows.values()),
        f"batch_chi2 reads {numbers['batch_chi2']}",
    )
    _expect(numbers["unavailable"]["worlds"] == sorted(ps.WORLDS), f"unavailable reads {numbers['unavailable']}")
    _expect(numbers["unavailable"]["reason"] == ps.UNREACHABLE_REASON, "the reason is missing")
    text = ps.report_text({"decision": decision})
    _expect(json.loads(text, parse_constant=_refuse)["decision"]["label"] == "none_adequate", "the report misreads")


def _refuse(constant: str) -> None:
    raise AssertionError(f"the report holds the non-finite constant {constant}")


def test_every_label_is_reachable_and_one_label_is_returned() -> None:
    matrix = ps.predecessor_matrix()
    seen = set()
    for world, theta, flip, noise, _ in ps.TRUTHS.values():
        if not any(noise):
            seen.add(
                ps.decide(
                    ps.planted_batches(ps.truth_row(world, theta, matrix, flip)), lambda b: matrix, FAST, flips=NO_FLIP
                )["label"]
            )
    for name in ps.MIXED:
        seen.add(ps.decide(ps.scenario_batches(name), lambda b: matrix, FAST, flips=NO_FLIP)["label"])
    reversed_batches = ps.planted_batches(ps.truth_row("q12_phase", -0.18, matrix))
    for batch in reversed_batches:
        batch["contrasts"] = [-0.05 for _ in batch["contrasts"]]
    seen.add(ps.decide(reversed_batches, lambda b: matrix, FAST, flips=NO_FLIP)["label"])
    expected = {"offset_absent", "offset_reversed", *ps.ERROR_WORLDS, "phase_mixed", "none_adequate"}
    _expect(expected <= seen, f"unreached labels: {sorted(expected - seen)}")


def test_the_parabola_finds_the_injected_phase_of_least_contrast() -> None:
    matrix = ps.predecessor_matrix()
    row = ps.truth_row("q12_phase", -0.18, matrix)
    error = 1.0 / math.sqrt(ps.SCAN_SHOTS)
    points = [
        (5.0 * ps.ARMS[a][1], row[a]["contrast"], error)
        for a in ps.ARM_NAMES
        if a != ps.PLAIN and ps.ARMS[a][0] == 0 and ps.ARMS[a][2] == 0
    ]
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
    _expect(report["reported"]["bridge"]["within_resolve"], f"the bridge reads {report['reported']['bridge']}")
    _expect(decision["label"] == "q12_phase", f"the planted phase reads {decision['label']}")
    fitted = decision["numbers"]["parameters"]["q12_phase"].values()
    _expect(max(abs(v + 0.18) for v in fitted) < 0.006, f"the fitted phases {list(fitted)} miss -0.18")
    least = report["reported"]["z12_parabola"]
    _expect(abs(least["phi_degrees"] - math.degrees(0.18)) < 2.0, f"the least point is {least['phi_degrees']} degrees")
    _expect(report["reported"]["q4_line"]["slope_per_degree"] < 0, "the q4 line of a negative q12 phase rises")
    slope = report["reported"]["q4_slope_against_retained"]
    _expect(
        ("q4_line_with_retained" in report["reported"]) == slope["within_resolve"],
        f"the retained q4 points join the line against the slope comparison {slope}",
    )
    _expect(decision["a5_186"].startswith("changes"), "a deciding label leaves the ledger row unchanged")
    ratios = report["reported"]["visibility_ratio"]
    _expect(set(ratios) == set(ps.ARM_NAMES) - {ps.CENTER}, "a visibility ratio is missing")
    _expect(all(len(r["measured"]) >= 2 and 0 < r["exact"] <= 1.0 + 1e-12 for r in ratios.values()), f"ratios {ratios}")


def test_the_retained_q4_points_join_only_an_agreeing_bridge_and_slope() -> None:
    retained = ps.retained_q4_points()
    slope = ps.line_fit(retained, 0.0)["slope_per_degree"]
    same = [(x, slope * x, 0.002) for x in (-10.0, -5.0, 5.0, 10.0)]
    doubled = [(x, 2 * slope * x, 0.002) for x in (-10.0, -5.0, 5.0, 10.0)]
    _expect("q4_line_with_retained" in ps.q4_reports(same, 0.01, True, retained), "an equal slope stays apart")
    _expect("q4_line_with_retained" not in ps.q4_reports(same, 0.01, False, retained), "a failed bridge pools")
    report = ps.q4_reports(doubled, 0.01, True, retained)
    _expect("q4_line_with_retained" not in report, "a doubled slope joins the retained points")
    _expect(not report["q4_slope_against_retained"]["within_resolve"], f"the comparison reads {report}")


def test_a_jump_of_d2s_qubit_drops_the_splits_and_keeps_the_batch() -> None:
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row("q12_phase", -0.18, matrix))
    whole = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)
    for batch in batches:
        batch["split_admitted"] = False
        batch["splits"] = [9.0, -9.0, 9.0]
    partial = ps.decide(batches, lambda b: matrix, FAST, flips=NO_FLIP)
    _expect(partial["numbers"]["split_admitted"] == [], "a batch without its splits is listed as holding them")
    _expect(partial["numbers"]["chi2"]["q12_phase"] < 1e-6, "dropped splits still enter the chi-square")
    limits = (whole["numbers"]["adequacy_limit"]["q12_phase"], partial["numbers"]["adequacy_limit"]["q12_phase"])
    _expect(limits[1] < limits[0], f"the bound ignores the dropped values: {limits}")


@pytest.mark.audit
def test_evaluate_keeps_a_batch_whose_d2_readout_jumps_and_drops_its_splits() -> None:
    rows = ps.batch_rows(ps.TUNA_SERIES)
    # The readout batch between the two rounds brackets the last forward and the first mirror z8c batch.
    shared = next(rows[n + 1]["batch"] for n, r in enumerate(rows) if r["kind"] == "z8c-10" and r["replicate"] == 2)
    report = ps.evaluate(_series_shots("q12_phase", -0.18, 131072, (shared,)), _manifest())
    guards = {b: r["guard"] for b, r in report["batch_rows"].items()}
    _expect(all(g["admitted"] for g in guards.values()), "a jump of d2's qubit fails the contrast guard")
    dropped = [report["batch_rows"][b]["kind"] for b, g in guards.items() if not g["split_admitted"]]
    _expect(dropped == ["z8c-10", "z8c-10"], f"the jump drops the splits of {dropped}")
    _expect(report["decision"]["label"] == "q12_phase", f"the series reads {report['decision']['label']}")


@pytest.mark.audit
@pytest.mark.parametrize("truth", [t for t, v in ps.TRUTHS.items() if v[4] is not None and any(v[3])])
def test_a_planted_truth_with_cz_damping_reads_its_label(truth: str) -> None:
    matrix = ps.predecessor_matrix()
    world, theta, flip, noise, label = ps.TRUTHS[truth]
    batches = ps.planted_batches(ps.truth_row(world, theta, matrix, flip, noise=noise))
    _expect(ps.decide(batches, lambda b: matrix)["label"] == label, f"{truth} misreads")


@pytest.mark.audit
def test_the_recorded_operating_characteristics_read_no_wrong_deciding_label() -> None:
    record = json.loads((CASES / ps.TUNA_SERIES / "prediction.json").read_text(encoding="utf-8"))
    counts = record["operating_characteristics"]["label_counts"]
    for name, (world, _, _, _, _) in ps.TRUTHS.items():
        wrong = set(ps.ERROR_WORLDS) - {world}
        _expect(not wrong & set(counts[name]), f"{name} reads {counts[name]}")


@pytest.mark.audit
def test_the_committed_case_matches_the_build() -> None:
    ps.check(CASES)
