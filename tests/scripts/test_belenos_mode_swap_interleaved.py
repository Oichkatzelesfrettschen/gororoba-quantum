"""Contracts of the Belenos interleaved mode-swap request: frozen cases, seeds, timing, binding, validity, mesh
variance, placement, the pooled slot reading and the comparison with the earlier deltas."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import belenos_mode_swap_interleaved as case
import pytest

ROOT = Path(__file__).resolve().parents[2]
Key = tuple[str, int]
Model = Callable[[dict[str, Any], dict[str, Any]], float]
# A chip-mode effect on the algebra share of a block, by slot.
GAIN = {0: 0.02, 1: -0.05, 2: 0.09, 3: -0.12, 4: 0.15, 5: -0.03}
ARMS = (
    (case.SEED_DRAW, case.COMPILATION_SEEDS),
    (case.REPLICATE_SEED_DRAW, case.REPLICATE_COMPILATION_SEEDS),
)


def unit(*parts: object) -> float:
    """A deterministic number in [-0.5, 0.5) from the parts."""
    digest = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64 - 0.5


def slot_of(block: dict[str, Any]) -> int:
    return int(block["offset"]) // case.SLOT_WIDTH


def test_retained_requests_rebuild_and_bind_to_the_packed_and_swapped_unitaries() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen requests do not check")


def test_seeds_are_the_registered_draws_in_index_order_and_each_is_used_once() -> None:
    for draw, seeds in ARMS:
        values = json.loads((ROOT / draw).read_text(encoding="utf-8"))["values"]
        if list(seeds) != values:
            raise AssertionError(f"{draw} is not the draw in index order")
    every = case.COMPILATION_SEEDS + case.REPLICATE_COMPILATION_SEEDS
    if len(set(every)) != len(every):
        raise AssertionError("a compilation seed repeats across the arms")
    ledger = json.loads((ROOT / "docs/evidence/qrng_seeds/allocations.json").read_text(encoding="utf-8"))
    rows = {
        (r["record"], r["index"]): r["value"]
        for r in ledger["allocations"]
        if r["path"] == "scripts/belenos_mode_swap_interleaved.py"
    }
    for draw, seeds in ARMS:
        if [rows.get((draw, i)) for i in range(len(seeds))] != list(seeds):
            raise AssertionError(f"allocations.json does not register {draw} indices 0 to {len(seeds) - 1}")


def test_each_set_runs_abba_then_a_replicate_pair_with_one_seed_per_layout_and_arm() -> None:
    for job, sets in case.JOBS.items():
        manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
        settings = manifest["settings"]
        if len(settings) != case.ITERATIONS_PER_SET * len(sets):
            raise AssertionError(f"{job}: {len(settings)} iterations")
        for position, block_set in enumerate(sets):
            mine = settings[position * 6 : (position + 1) * 6]
            if {s["block_set"] for s in mine} != {block_set}:
                raise AssertionError(f"{job}: set {block_set} does not run contiguously")
            if [s["layout"] for s in mine[:4]] != list(case.ORDER) or {s["arm"] for s in mine[:4]} != {"primary"}:
                raise AssertionError(f"{job}: set {block_set} does not open with ABBA")
            tail = [s["layout"] for s in mine[4:]]
            expected_tail = ["packed", "swapped"] if block_set % 2 == 0 else ["swapped", "packed"]
            if {s["arm"] for s in mine[4:]} != {"replicate"} or tail != expected_tail:
                raise AssertionError(f"{job}: set {block_set} replicate tail {tail}")
            by_cell: dict[tuple[str, str], set[int]] = {}
            for s in mine:
                by_cell.setdefault((s["layout"], s["arm"]), set()).add(s["compilation_seed"])
            if any(len(seeds) != 1 for seeds in by_cell.values()) or len(by_cell) != 4:
                raise AssertionError(f"{job}: set {block_set} takes one seed per layout and arm")
            keys = {json.dumps([s["circuit_params"], s["compilation_seed"]], sort_keys=True) for s in mine}
            if len(keys) != 4:
                raise AssertionError(f"{job}: set {block_set} binds {len(keys)} distinct keys, not 4")


def test_duration_bound_leaves_margin_and_credits_follow_the_largest_iteration() -> None:
    for job in case.JOBS:
        manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
        stressed = case.bound_seconds(job, case.STRESS_FACTOR)
        if stressed > case.DURATION_MARGIN * case.MAX_DURATION or manifest["max_duration"] != case.MAX_DURATION:
            raise AssertionError(f"{job}: stressed bound {stressed} s")
        if not case.bound_seconds(job) <= case.expected_seconds(job) < stressed:
            raise AssertionError(f"{job}: expected seconds {case.expected_seconds(job)}")
        if manifest["max_shots"] != case.SHOTS_PER_ITERATION * manifest["iterations"]:
            raise AssertionError(f"{job}: max_shots")


def test_the_frozen_interpretation_is_the_design_document_reading() -> None:
    doc = " ".join((ROOT / case.DESIGN).read_text(encoding="utf-8").split())
    if case.READING not in doc:
        raise AssertionError("the design document does not carry the preregistered reading word for word")
    for job in case.JOBS:
        manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
        prereg = manifest["preregistered"]
        if prereg["interpretation"] != case.READING:
            raise AssertionError(f"{job}: interpretation differs from READING")
        for text in prereg["reading_table"].values():
            if text not in doc:
                raise AssertionError(f"the design document lacks the table reading {text!r}")


def synthetic(
    tmp_path: Path,
    model: Model,
    primary_same_mesh: bool = True,
    replicate_distinct: bool = True,
    reverse: bool = False,
) -> list[Path]:
    """Three runs whose block shares follow model(setting, block), 20000 one-click samples per block."""
    runs = []
    for job in case.JOBS:
        raw = (case.CASES / job / "cases.json").read_bytes()
        manifest = json.loads(raw)
        iterations = []
        for setting in manifest["settings"]:
            counts: dict[str, int] = {}
            for block in setting["blocks"]:
                a = model(setting, block)
                algebra = next(k for k, role in enumerate(block["roles"]) if role != "dilation")
                dilation = next(k for k, role in enumerate(block["roles"]) if role == "dilation")
                for port, n in ((algebra, round(20000 * a)), (dilation, 20000 - round(20000 * a))):
                    state = [0] * case.MODES
                    state[block["offset"] + port] = 1
                    counts[",".join(map(str, state))] = n
            mesh = f"{setting['layout']}-{setting['block_set']}-{setting['arm']}"
            if setting["arm"] == "primary" and not primary_same_mesh:
                mesh += f"-{setting['repeat']}"
            if setting["arm"] == "replicate" and not replicate_distinct:
                mesh = f"{setting['layout']}-{setting['block_set']}-primary"
            iterations.append(
                {
                    "iteration": {
                        "circuit_params": setting["circuit_params"],
                        "compilation_seed": setting["compilation_seed"],
                    },
                    "counts": counts,
                    "result_fields": {"computed_circuit": mesh},
                }
            )
        run = tmp_path / job
        run.mkdir()
        (run / "cases.json").write_bytes(raw)
        (run / "results.json").write_text(
            json.dumps({"iterations": iterations[::-1] if reverse else iterations}), encoding="utf-8"
        )
        runs.append(run)
    return runs


def chip_mode(sign: float) -> Model:
    """Every block's share is 1/2 plus sign x the gain of the slot it sits on: a pure chip-mode effect."""
    return lambda setting, block: 0.5 + sign * GAIN[slot_of(block)]


def flat(setting: dict[str, Any], block: dict[str, Any]) -> float:
    return 0.5 + 0.001 * slot_of(block)


def zero_deltas(runs: list[Path]) -> dict[Key, float]:
    keys: set[Key] = set()
    for run in runs:
        for setting in json.loads((run / "cases.json").read_text(encoding="utf-8"))["settings"]:
            keys.update((json.dumps(b["m"]), b["t"]) for b in setting["blocks"])
    return dict.fromkeys(keys, 0.0)


def earlier_from(record: dict[str, Any], scale: float = 1.0) -> dict[Key, float]:
    return {(row["block"][0], row["block"][1]): scale * row["new"] for row in record["comparison"]["rows"]}


def test_a_chip_mode_effect_reads_as_a_positive_sign_slot_reading_and_reproduces_the_earlier_deltas(
    tmp_path: Path,
) -> None:
    runs = synthetic(tmp_path, chip_mode(+1.0), reverse=True)
    first = case.analyze(runs, earlier=zero_deltas(runs))
    record = case.analyze(runs, earlier=earlier_from(first, 1.1))
    if record["iterations_bound"] != 30 or record["withheld"]:
        raise AssertionError(record["withheld"])
    slot = record["slot_predictor"]
    if slot["verdict"] != "slot" or slot["reading"] != "positive-sign chip-mode effect":
        raise AssertionError(slot)
    if record["validity"]["detected"] is not False or record["mesh_variance"]["sigma2"] > 1e-6:
        raise AssertionError(record["validity"])
    if record["comparison"]["verdict"] != "reproduce" or record["comparison"]["sign_agreement"] != 30:
        raise AssertionError(record["comparison"])
    if record["reading"] != case.READING_TABLE[("beyond", "reproduce")]:
        raise AssertionError(record["reading"])


def test_a_reversed_chip_mode_effect_reads_as_the_reversed_sign(tmp_path: Path) -> None:
    def model(setting: dict[str, Any], block: dict[str, Any]) -> float:
        sign = 1.0 if setting["layout"] == "packed" else -1.0
        return 0.5 + sign * GAIN[slot_of(block)]

    runs = synthetic(tmp_path, model)
    record = case.analyze(runs, earlier=zero_deltas(runs))
    slot = record["slot_predictor"]
    r, _, upper = slot["slot_predictor"]
    if r > -0.9 or upper >= -case.SLOT_SIGN_BOUND or slot["reading"] != "reversed-sign chip-mode effect":
        raise AssertionError(slot)
    if slot["verdict"] != "mixed":
        raise AssertionError("decide() returns mixed for a negative correlation; the reading is the sign rule")


def test_mesh_variance_absorbs_moves_that_binomial_error_alone_would_call_and_reads_mesh_specific(
    tmp_path: Path,
) -> None:
    def mesh_only(setting: dict[str, Any], block: dict[str, Any]) -> float:
        return 0.5 + 0.08 * unit(
            "mesh", setting["block_set"], setting["layout"], setting["arm"], block["t"], block["m"]
        )

    runs = synthetic(tmp_path, mesh_only)
    unrelated = {key: 0.2 * unit("earlier", key) for key in zero_deltas(runs)}
    record = case.analyze(runs, earlier=unrelated)
    if record["moved_binomial"] < 10:
        raise AssertionError("the mesh offsets should move many blocks against binomial error alone")
    mesh = record["mesh_variance"]
    if not 0.02 < mesh["sigma"] < 0.06 or mesh["excess_ratio"] < 50:
        raise AssertionError(mesh["sigma"])
    if record["placement"]["beyond_mesh_variance"]:
        raise AssertionError(record["placement"]["moved_beyond_mesh"])
    if record["comparison"]["verdict"] != "uncorrelated":
        raise AssertionError(record["comparison"])
    if record["reading"] != case.READING_TABLE[("within", "uncorrelated")]:
        raise AssertionError(record["reading"])


def test_no_placement_effect_reads_no_moves(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, lambda setting, block: 0.5)
    record = case.analyze(runs, earlier=zero_deltas(runs))
    if record["moved_binomial"] != 0 or record["reading"] != case.READING_TABLE[("none", "any")]:
        raise AssertionError(record["reading"])


def test_drift_is_a_validity_finding_that_scales_the_binomial_variances(tmp_path: Path) -> None:
    def drifting(setting: dict[str, Any], block: dict[str, Any]) -> float:
        step = 0.05 if (setting["arm"], setting["repeat"]) == ("primary", 1) else 0.0
        return 0.5 + step * (1 + unit("drift", block["t"]))

    runs = synthetic(tmp_path, drifting)
    record = case.analyze(runs, earlier=zero_deltas(runs))
    jobs = record["validity"]["jobs"]
    if not all(j["detected"] is True and j["inflation"] > 1 and j["dof"] > 0 for j in jobs.values()):
        raise AssertionError(jobs)
    if record["validity"]["dof"] != 60:
        raise AssertionError(record["validity"]["dof"])


def test_repeats_on_different_meshes_withhold_the_reading(tmp_path: Path) -> None:
    record = case.analyze(synthetic(tmp_path, flat, primary_same_mesh=False), earlier={})
    if record["validity"]["dof"] != 0 or record["validity"]["detected"] is not None:
        raise AssertionError(record["validity"])
    if not record["reading"].startswith("withheld") or "placement" in record:
        raise AssertionError(record["reading"])


def test_a_replicate_on_the_primary_mesh_withholds_the_reading(tmp_path: Path) -> None:
    record = case.analyze(synthetic(tmp_path, flat, replicate_distinct=False), earlier={})
    if not record["reading"].startswith("withheld") or "replicate" not in record["reading"]:
        raise AssertionError(record["reading"])


def test_a_cut_short_job_keeps_its_counted_iterations_and_withholds_the_pooled_reading(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, flat)
    path = runs[2] / "results.json"
    results = json.loads(path.read_text(encoding="utf-8"))
    results["iterations"][0] = {"missing": True}
    path.write_text(json.dumps(results), encoding="utf-8")
    record = case.analyze(runs, earlier={})
    if (record["iterations_bound"], record["iterations_uncounted"]) != (29, 1):
        raise AssertionError(record)
    if not record["reading"].startswith("withheld"):
        raise AssertionError(record["reading"])


def test_a_failed_repeat_holds_its_label_so_the_counted_repeat_keeps_repeat_one() -> None:
    manifest = json.loads((case.CASES / "job-02" / "cases.json").read_text(encoding="utf-8"))
    settings = manifest["settings"]
    echo = {"circuit_params": settings[0]["circuit_params"], "compilation_seed": settings[0]["compilation_seed"]}
    failed = {"iteration": echo, "error": "lost"}
    counted = {"iteration": echo, "counts": {"1": 1}}
    bound, uncounted = case.bind_iterations(settings, {"iterations": [failed, counted]})
    if list(bound) != [3] or uncounted != 1:
        raise AssertionError((list(bound), uncounted))


def test_a_result_iteration_outside_the_case_raises(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, flat)
    path = runs[2] / "results.json"
    results = json.loads(path.read_text(encoding="utf-8"))
    results["iterations"][0]["iteration"]["compilation_seed"] = 1
    path.write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(RuntimeError, match="binds to no remaining setting"):
        case.analyze(runs, earlier={})


def test_a_run_whose_cases_differ_from_the_frozen_case_raises(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, flat)
    manifest = json.loads((runs[0] / "cases.json").read_text(encoding="utf-8"))
    manifest["max_samples"] += 1
    (runs[0] / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="differs from the frozen"):
        case.analyze(runs, earlier={})


def table_of(new: list[float]) -> dict[str, dict[Key, dict[str, Any]]]:
    packed = {(f"b{i}", 0): {"a": 0.5, "slot": 0} for i in range(len(new))}
    swapped = {(f"b{i}", 0): {"a": 0.5 + d, "slot": 3} for i, d in enumerate(new)}
    return {"packed": packed, "swapped": swapped}


def test_the_comparison_with_the_earlier_deltas_reads_reproduce_uncorrelated_and_indeterminate() -> None:
    new = [0.01 * (i - 15) for i in range(30)]
    table = table_of(new)
    keys = [(f"b{i}", 0) for i in range(len(new))]
    reproduce = case.compare_earlier(table, {k: 2 * d for k, d in zip(keys, new, strict=True)})
    if (reproduce["verdict"], reproduce["sign_agreement"], reproduce["sign_comparable"]) != ("reproduce", 29, 29):
        raise AssertionError(reproduce)
    uncorrelated = case.compare_earlier(table, {k: unit("old", k) for k in keys})
    if uncorrelated["verdict"] != "uncorrelated":
        raise AssertionError(uncorrelated)
    # A loose positive correlation: the interval neither clears the floor nor excludes strong reproduction.
    loose = {k: d + 0.35 * unit("noise", k) for k, d in zip(keys, new, strict=True)}
    indeterminate = case.compare_earlier(table, loose)
    if indeterminate["verdict"] != "indeterminate":
        raise AssertionError(indeterminate)
    with pytest.raises(RuntimeError, match="lacks blocks"):
        case.compare_earlier(table, {})


def test_every_table_cell_has_a_reading() -> None:
    verdicts = ("reproduce", "uncorrelated", "indeterminate")
    seen = {case.read({"beyond_mesh_variance": flag}, 5, {"verdict": v}) for flag in (True, False) for v in verdicts}
    seen.add(case.read({"beyond_mesh_variance": False}, 0, {"verdict": "reproduce"}))
    if seen != set(case.READING_TABLE.values()):
        raise AssertionError(seen ^ set(case.READING_TABLE.values()))


def test_slot_sign_rule_is_symmetric() -> None:
    expectations = (
        ((-0.8, -0.95, -0.31), "reversed-sign chip-mode effect"),
        ((0.8, 0.31, 0.95), "positive-sign chip-mode effect"),
        ((-0.6, -0.9, -0.29), "no sign-specific chip-mode reading"),
        ((-0.6, -0.9, 0.4), "no sign-specific chip-mode reading"),
    )
    for predictor, reading in expectations:
        if case.slot_sign(predictor) != reading:
            raise AssertionError((predictor, reading))
