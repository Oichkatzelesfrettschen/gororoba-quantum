"""Contracts of the Belenos interleaved mode-swap request: frozen cases, seeds, timing, binding, validity, mesh
variance per class, slot homogeneity, placement, the descriptive slot predictor, the comparison with the earlier
deltas and their excess over the mesh variance."""

from __future__ import annotations

import hashlib
import json
import math
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
    (case.EXTRA_REPLICATE_SEED_DRAW, case.EXTRA_REPLICATE_SEEDS),
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
    every = case.COMPILATION_SEEDS + case.REPLICATE_COMPILATION_SEEDS + case.EXTRA_REPLICATE_SEEDS
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


def set_settings() -> dict[int, list[dict[str, Any]]]:
    """Each block set's six settings in run order: set 0 from job-00, sets 1 to 4 from their two half-set jobs."""
    out: dict[int, list[dict[str, Any]]] = {}
    for job in case.JOBS:
        settings = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))["settings"]
        for setting in settings:
            if job in case.RETAINED_CASES and setting["block_set"] != 0:
                continue
            out.setdefault(setting["block_set"], []).append(setting)
    return out


def test_each_set_alternates_the_layouts_and_each_seed_binds_its_iterations() -> None:
    sets = set_settings()
    if sorted(sets) != [0, 1, 2, 3, 4] or [len(sets[s]) for s in sorted(sets)] != [6, 10, 10, 10, 10]:
        raise AssertionError({s: len(v) for s, v in sets.items()})
    for block_set, mine in sets.items():
        first = "packed" if block_set % 2 == 0 else "swapped"
        if [s["layout"] for s in mine] != [first, case.MIRROR[first]] * (len(mine) // 2):
            raise AssertionError(f"set {block_set} does not alternate the layouts from {first}")
        seen: set[int] = set()
        for layout in ("packed", "swapped"):
            primary = [slot for slot, s in enumerate(mine) if (s["layout"], s["arm"]) == (layout, "primary")]
            replicate = [slot for slot, s in enumerate(mine) if (s["layout"], s["arm"]) == (layout, "replicate")]
            if len(primary) != 2 or sum(replicate) * 2 != sum(primary) * len(replicate):
                raise AssertionError(f"set {block_set} {layout} replicates are off the primary mean slot")
            if primary != [min(primary + replicate), max(primary + replicate)]:
                raise AssertionError(f"set {block_set} {layout} primary repeats do not bracket the replicates")
            for s in mine:
                if s["layout"] != layout:
                    continue
                if s["compilation_seed"] != case.seed_of(block_set, layout, s["arm"], s["repeat"]):
                    raise AssertionError(f"{s['name']} seed")
                if s["arm"] == "replicate":
                    seen.add(s["compilation_seed"])
        if len(seen) != len(mine) - 4:
            raise AssertionError(f"set {block_set} reuses a replicate seed")
    for job, parts in case.JOBS.items():
        if job not in case.RETAINED_CASES and (len(parts) != 1 or case.iterations(job) != case.ITERATIONS_PER_JOB):
            raise AssertionError(f"{job} is not one half of a packed set")


def test_the_retained_job_00_keeps_its_bytes_and_its_settings_rebuild() -> None:
    for job, digest in case.RETAINED_CASES.items():
        data = (case.CASES / job / "cases.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise AssertionError(f"{job} cases.json moved")
    with pytest.raises(RuntimeError, match="keeps its retained bytes"):
        case.build("job-00")


def test_duration_bound_leaves_one_iteration_of_margin_and_credits_follow_the_largest_iteration() -> None:
    for job in case.JOBS:
        manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
        if manifest["max_shots"] != case.SHOTS_PER_ITERATION * manifest["iterations"]:
            raise AssertionError(f"{job}: max_shots")
        if job in case.RETAINED_CASES:
            continue
        bound = case.bound_seconds(job)
        if bound + case.SECONDS_PER_ITERATION > case.MAX_DURATION or manifest["max_duration"] != case.MAX_DURATION:
            raise AssertionError(f"{job}: bound {bound} s")
        if not bound <= case.expected_seconds(job) < case.MAX_DURATION:
            raise AssertionError(f"{job}: expected seconds {case.expected_seconds(job)}")


def test_the_frozen_interpretation_is_the_design_document_reading() -> None:
    doc = " ".join((ROOT / case.DESIGN).read_text(encoding="utf-8").split())
    if case.READING not in doc:
        raise AssertionError("the design document does not carry the preregistered reading word for word")
    for job in case.JOBS:
        if job in case.RETAINED_CASES:
            continue
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
    split_primary: tuple[int, str] | None = None,
) -> list[Path]:
    """Three runs whose block shares follow model(setting, block), 20000 one-click samples per block.

    split_primary (block set, layout) returns that layout's two primary repeats on two meshes.
    """
    runs = []
    for job in case.JOBS:
        raw = (case.CASES / job / "cases.json").read_bytes()
        manifest = json.loads(raw)
        iterations: list[dict[str, Any]] = []
        for setting in manifest["settings"]:
            if job in case.RETAINED_CASES and setting["block_set"] != 0:
                iterations.append({"missing": True})
                continue
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
            split = split_primary == (setting["block_set"], setting["layout"])
            if setting["arm"] == "primary" and (not primary_same_mesh or split):
                mesh += f"-{setting['repeat']}"
            if setting["arm"] == "replicate":
                mesh += f"-{setting['repeat']}"
                if not replicate_distinct:
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
        run.mkdir(parents=True)
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


def mesh_offset(setting: dict[str, Any], block: dict[str, Any], size: float = 0.04) -> float:
    """A per-seed mesh offset of the block, the same for both primary repeats of a layout."""
    seed = setting["arm"] + (str(setting["repeat"]) if setting["arm"] == "replicate" else "")
    return size * unit("mesh", setting["block_set"], setting["layout"], seed, block["t"], block["m"])


def keys_of(runs: list[Path]) -> list[Key]:
    keys: set[Key] = set()
    for run in runs:
        for setting in json.loads((run / "cases.json").read_text(encoding="utf-8"))["settings"]:
            keys.update((json.dumps(b["m"]), b["t"]) for b in setting["blocks"])
    return sorted(keys)


def old_of(deltas: dict[Key, float], v: float = 1e-6) -> dict[Key, dict[str, float]]:
    return {key: {"delta": delta, "v": v} for key, delta in deltas.items()}


def zero_deltas(runs: list[Path]) -> dict[Key, dict[str, float]]:
    return old_of(dict.fromkeys(keys_of(runs), 0.0))


def earlier_from(record: dict[str, Any], scale: float = 1.0) -> dict[Key, dict[str, float]]:
    return old_of({(row["block"][0], row["block"][1]): scale * row["new"] for row in record["comparison"]["rows"]})


def test_a_chip_mode_effect_moves_beyond_the_mesh_variance_and_reproduces_the_earlier_deltas(
    tmp_path: Path,
) -> None:
    runs = synthetic(tmp_path, chip_mode(+1.0), reverse=True)
    first = case.analyze(runs, earlier=zero_deltas(runs))
    record = case.analyze(runs, earlier=earlier_from(first, 1.1))
    if record["iterations_bound"] != 46 or record["withheld"]:
        raise AssertionError(record["withheld"])
    slot = record["slot_predictor"]
    if slot["verdict"] != "slot" or slot["descriptive"] is not True or "reading" in slot:
        raise AssertionError(slot)
    classes = record["mesh_variance"]["classes"]
    if record["validity"]["detected"] is not False or any(c["sigma2"] > 1e-6 for c in classes.values()):
        raise AssertionError(record["validity"])
    if (classes["half"]["dof"], classes["extreme"]["dof"]) != (68, 88):
        raise AssertionError(classes)
    if record["comparison"]["verdict"] != "reproduce" or record["comparison"]["sign_agreement"] != 30:
        raise AssertionError(record["comparison"])
    if record["reading"] != case.READING_TABLE[("beyond", "reproduce")]:
        raise AssertionError(record["reading"])


def test_the_slot_predictor_is_reported_without_a_reading(tmp_path: Path) -> None:
    def model(setting: dict[str, Any], block: dict[str, Any]) -> float:
        sign = 1.0 if setting["layout"] == "packed" else -1.0
        return 0.5 + sign * GAIN[slot_of(block)]

    runs = synthetic(tmp_path, model)
    record = case.analyze(runs, earlier=zero_deltas(runs))
    slot = record["slot_predictor"]
    if slot["slot_predictor"][0] > -0.9 or slot["descriptive"] is not True or "reading" in slot:
        raise AssertionError(slot)


def test_the_mesh_variance_is_estimated_per_class(tmp_path: Path) -> None:
    def model(setting: dict[str, Any], block: dict[str, Any]) -> float:
        size = 0.08 if block["p_algebra"] == "1/2" else 0.02
        return 0.5 + mesh_offset(setting, block, size)

    runs = synthetic(tmp_path, model)
    classes = case.analyze(runs, earlier=zero_deltas(runs))["mesh_variance"]["classes"]
    half, extreme = classes["half"], classes["extreme"]
    if not half["sigma"] > 2.5 * extreme["sigma"] or not half["sigma2_upper"] > half["sigma2"]:
        raise AssertionError(classes)


def test_mesh_variance_absorbs_moves_that_binomial_error_alone_would_call(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, lambda setting, block: 0.5 + mesh_offset(setting, block, 0.08))
    record = case.analyze(runs, earlier=old_of({key: 0.2 * unit("earlier", key) for key in keys_of(runs)}))
    if record["moved_binomial"] < 10:
        raise AssertionError("the mesh offsets should move many blocks against binomial error alone")
    if record["placement"]["beyond_mesh_variance"] or record["placement"]["moved_beyond_mesh"]:
        raise AssertionError(record["placement"]["moved_beyond_mesh"])
    if any(c["excess_ratio"] < 20 for c in record["mesh_variance"]["classes"].values()):
        raise AssertionError(record["mesh_variance"]["classes"])
    if not record["reading"].startswith(case.PLACED["within"]):
        raise AssertionError(record["reading"])


def placed(blocks: set[int], gain: float = 0.3) -> Model:
    """Mesh offsets everywhere and a placement step on the swapped layout of the chosen block numbers."""

    def model(setting: dict[str, Any], block: dict[str, Any]) -> float:
        index = setting["blocks"].index(block) + 6 * setting["block_set"]
        step = gain if setting["layout"] == "swapped" and index in blocks else 0.0
        return 0.35 + mesh_offset(setting, block, 0.02) + step

    return model


def test_one_block_beyond_the_mesh_variance_stays_within_and_two_place_it_beyond(tmp_path: Path) -> None:
    for chosen, beyond in (({0}, False), ({0, 7}, True)):
        runs = synthetic(tmp_path / str(len(chosen)), placed(chosen))
        record = case.analyze(runs, earlier=zero_deltas(runs))
        placement = record["placement"]
        if placement["moved_beyond_mesh"] != len(chosen) or placement["beyond_mesh_variance"] is not beyond:
            raise AssertionError(placement["moved_beyond_mesh"])


def test_one_slot_with_a_larger_mesh_scale_withholds_the_beyond_class(tmp_path: Path) -> None:
    base = placed({0, 7})

    def model(setting: dict[str, Any], block: dict[str, Any]) -> float:
        wide = slot_of(block) == 5
        return base(setting, block) + (mesh_offset(setting, block, 0.4) if wide else 0.0)

    runs = synthetic(tmp_path, model)
    record = case.analyze(runs, earlier=zero_deltas(runs))
    homogeneity = record["slot_homogeneity"]
    if homogeneity["homogeneous"] or min(row["p"] for row in homogeneity["rows"]) >= case.SLOT_ALPHA / case.SLOTS:
        raise AssertionError(homogeneity)
    if record["placement"]["moved_beyond_mesh"] < 2 or record["placement"]["beyond_mesh_variance"]:
        raise AssertionError(record["placement"]["moved_beyond_mesh"])


def test_a_primary_pair_on_two_meshes_drops_its_contrasts_and_blocks(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, placed({0, 7}), split_primary=(1, "swapped"))
    record = case.analyze(runs, earlier=zero_deltas(runs))
    dropped = record["mesh_variance"]["dropped"]
    if len(dropped) != 6 or {row["layout"] for row in dropped} != {"swapped"}:
        raise AssertionError(dropped)
    if record["placement"]["blocks"] != 24 or record["validity"]["dof"] != 54 or record["withheld"]:
        raise AssertionError(record["placement"]["blocks"])
    if record["placement"]["moved_beyond_mesh"] != 1 or record["comparison"]["blocks"] != 30:
        raise AssertionError("block 7 of set 1 leaves the placement test and stays in the comparison")


def test_each_earlier_excess_branch_reads_end_to_end(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, lambda setting, block: 0.5 + mesh_offset(setting, block, 0.08))
    keys = keys_of(runs)
    probe = case.analyze(runs, earlier=zero_deltas(runs))
    classes = probe["mesh_variance"]["classes"]
    p_of = {(row["block"][0], row["block"][1]): row["class"] for row in probe["placement"]["rows"]}
    sign = {key: 1.0 if unit("sign", key) > 0 else -1.0 for key in keys}
    for factor, verdict in ((0.8, "mesh"), (3.0, "window"), (8.0, "excess")):
        old = {key: sign[key] * math.sqrt(2 * factor * classes[p_of[key]]["sigma2_upper"]) for key in keys}
        record = case.analyze(runs, earlier=old_of(old, 0.0))
        comparison = record["comparison"]
        if comparison["verdict"] != "uncorrelated" or comparison["excess"]["verdict"] != verdict:
            raise AssertionError((factor, comparison["pearson"], comparison["excess"]))
        if record["reading"] != case.READING_TABLE[("within", f"uncorrelated-{verdict}")]:
            raise AssertionError(record["reading"])


def test_the_default_earlier_deltas_resolve_every_block_of_the_case(tmp_path: Path) -> None:
    record = case.analyze(synthetic(tmp_path, flat))
    if record["comparison"]["blocks"] != 30 or record["comparison"]["verdict"] not in {
        "reproduce",
        "uncorrelated",
        "indeterminate",
    }:
        raise AssertionError(record["comparison"])
    if any(entry["v"] <= 0 for entry in case.earlier_deltas().values()):
        raise AssertionError("an earlier delta carries no binomial variance")


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
    sets = record["validity"]["sets"]
    if not all(j["detected"] is True and j["inflation"] > 1 and j["dof"] > 0 for j in sets.values()):
        raise AssertionError(sets)
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
    if (record["iterations_bound"], record["iterations_uncounted"]) != (45, 7):
        raise AssertionError(record)
    if not record["reading"].startswith("withheld"):
        raise AssertionError(record["reading"])


def test_a_failed_repeat_holds_its_label_so_the_counted_repeat_keeps_repeat_one() -> None:
    manifest = json.loads((case.CASES / "job-00" / "cases.json").read_text(encoding="utf-8"))
    settings = manifest["settings"]
    echo = {"circuit_params": settings[0]["circuit_params"], "compilation_seed": settings[0]["compilation_seed"]}
    failed = {"iteration": echo, "error": "lost"}
    counted = {"iteration": echo, "counts": {"1": 1}}
    bound, uncounted = case.bind_iterations(settings, {"iterations": [failed, counted]})
    if list(bound) != [4] or uncounted != 1:
        raise AssertionError((list(bound), uncounted))


def test_a_result_iteration_outside_the_case_raises(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, flat)
    path = runs[2] / "results.json"
    results = json.loads(path.read_text(encoding="utf-8"))
    results["iterations"][0]["iteration"]["compilation_seed"] = 1
    path.write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(RuntimeError, match="binds to no remaining setting"):
        case.analyze(runs, earlier={})


def test_an_iteration_counted_in_two_runs_raises(tmp_path: Path) -> None:
    runs = synthetic(tmp_path, flat)
    first = json.loads((runs[0] / "results.json").read_text(encoding="utf-8"))
    path = runs[1] / "results.json"
    second = json.loads(path.read_text(encoding="utf-8"))
    # job-03 is set 1 half 0; job-00 index 6 is the same set-1 setting, counted again.
    duplicate = dict(second["iterations"][0])
    first["iterations"][6] = duplicate
    (runs[0] / "results.json").write_text(json.dumps(first), encoding="utf-8")
    with pytest.raises(RuntimeError, match="returned counts in two runs"):
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
    reproduce = case.compare_earlier(table, old_of({k: 2 * d for k, d in zip(keys, new, strict=True)}))
    if (reproduce["verdict"], reproduce["sign_agreement"], reproduce["sign_comparable"]) != ("reproduce", 29, 29):
        raise AssertionError(reproduce)
    uncorrelated = case.compare_earlier(table, old_of({k: unit("old", k) for k in keys}))
    if uncorrelated["verdict"] != "uncorrelated":
        raise AssertionError(uncorrelated)
    # A loose positive correlation: the interval neither clears the floor nor excludes strong reproduction.
    loose = {k: d + 0.35 * unit("noise", k) for k, d in zip(keys, new, strict=True)}
    indeterminate = case.compare_earlier(table, old_of(loose))
    if indeterminate["verdict"] != "indeterminate":
        raise AssertionError(indeterminate)
    with pytest.raises(RuntimeError, match="lacks blocks"):
        case.compare_earlier(table, {})


def test_every_table_cell_has_a_reading() -> None:
    comparisons = [{"verdict": v} for v in ("reproduce", "indeterminate")] + [
        {"verdict": "uncorrelated", "excess": {"verdict": e}} for e in case.EARLIER_UNCORRELATED
    ]
    seen = {case.read({"beyond_mesh_variance": flag}, 5, c) for flag in (True, False) for c in comparisons}
    seen.add(case.read({"beyond_mesh_variance": False}, 0, {"verdict": "reproduce"}))
    if seen != set(case.READING_TABLE.values()) or len(seen) != 11:
        raise AssertionError(seen ^ set(case.READING_TABLE.values()))
