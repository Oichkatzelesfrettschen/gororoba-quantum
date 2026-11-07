"""Score a returned Ascella pathion four-term block run against its preregistered thresholds."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import qd_platform
from experiment_analysis import decode_photonic_counts

from parallel import ordered_map

FAMILY = "ascella_pathion_four_term_blocks"
SCHEMA = "ascella-pathion-four-term-blocks-analysis-v1"
FILES = ("cases.json", "circuit.json", "job-body.json", "submission.json", "results.json", "raw/result.json")
WIDTH = 12
# docs/design/ascella-pathion-four-term-blocks-case.md, "Outcomes": a simulator level that departs from the ideal
# law by more than this stops the sequence before the QPU job. cases.json carries no such key.
SIMULATOR_TOLERANCE = 0.01
# Same document, "Decision-chain power": a within-class spread of T readings at or above this attributes a failed
# conformance to mesh variance and withholds the refutation.
MESH_ATTRIBUTION_SPREAD = 0.05
ARMS_PER_SEGMENT_REPEAT = 2
CLASS_LABEL = re.compile(r"^(?P<operand>\w+) blocks (?P<first>\d+)(?:, (?P<second>\d+)| to (?P<last>\d+))$")


def odds(level: float) -> float:
    if level <= 0:
        return 0.0
    return math.inf if level >= 1 else level / (1 - level)


def odds_corrected(level: float, ratio: float) -> float:
    """The level whose odds are the observed odds divided by the branch-loss ratio r."""
    corrected = odds(level) / ratio
    return 1.0 if math.isinf(corrected) else corrected / (1 + corrected)


def observation(task: tuple[int, dict[str, Any], dict[str, Any], int, int, dict[str, list[int]]]) -> dict[str, Any]:
    """One iteration's click counts per mode, bound to the request that produced them."""
    index, setting, entry, samples, shots_cap, modes = task
    if "counts" not in entry:
        state = next((key for key in ("missing", "error", "malformed") if key in entry), "unreadable")
        return {"index": index, "name": setting["name"], "returned": False, "state": state}
    iteration = entry["iteration"]
    if any(iteration[key] != setting[key] for key in ("compilation_seed", "circuit_params")):
        raise ValueError(f"{setting['name']}: returned iteration differs from its request")
    ports, invalid = decode_photonic_counts(entry["counts"], WIDTH)
    events = sum(ports) + sum(invalid.values())
    shots = entry["result_fields"]["nb_shots_used"]
    if events != entry["samples"] or events != samples or type(shots) is not int or not events <= shots <= shots_cap:
        raise ValueError(f"{setting['name']}: returned sample or shot count differs from the case")
    success = sum(ports[mode] for mode in modes["success"])
    failure = sum(ports[mode] for mode in modes["failure"])
    sentinel = sum(ports[mode] for mode in modes["sentinel"])
    if success + failure == 0:
        raise ValueError(f"{setting['name']}: no click in the success or failure modes")
    law = setting["ideal_label_law"]
    labeled = modes["success"] + modes["failure"]
    distance = 0.5 * sum(
        abs(ports[mode] / (success + failure) - law[position]) for position, mode in enumerate(labeled)
    )
    return {
        "index": index,
        "name": setting["name"],
        "returned": True,
        "port_counts": ports,
        "invalid_events": invalid,
        "events": events,
        "shots_used": shots,
        "success": success,
        "failure": failure,
        "sentinel": sentinel,
        "a": success / (success + failure),
        "sentinel_share": sentinel / events,
        "label_law_distance": distance,
    }


def segment_layout(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Segments with their iteration index ranges, checked against the settings the manifest froze."""
    settings = manifest["settings"]
    layout = []
    start = 0
    for segment in manifest["segments"]:
        indices = list(range(start, start + len(segment["arms"])))
        start += len(segment["arms"])
        for index, arm in zip(indices, segment["arms"], strict=True):
            setting = settings[index]
            expected = (segment["operand"], segment["block"], segment["seed_index"], arm, index)
            actual = (
                setting["operand"],
                setting["block"],
                setting["seed_index"],
                setting["arm"],
                setting["observation_index"],
            )
            if expected != actual:
                raise ValueError(f"{setting['name']}: setting differs from segment {segment['name']}")
        arms: dict[str, list[int]] = {}
        for index, arm in zip(indices, segment["arms"], strict=True):
            arms.setdefault(arm, []).append(index)
        if any(len(found) != ARMS_PER_SEGMENT_REPEAT for found in arms.values()):
            raise ValueError(f"segment {segment['name']}: every arm must repeat exactly twice")
        layout.append({**segment, "arm_indices": arms})
    if start != len(settings) or start != manifest["iterations"]:
        raise ValueError("the segments do not cover the settings")
    return layout


def pool(rows: list[dict[str, Any]]) -> dict[str, Any]:
    success = sum(row["success"] for row in rows)
    failure = sum(row["failure"] for row in rows)
    return {"success": success, "failure": failure, "a": success / (success + failure)}


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def condition(name: str, status: str, value: Any, limit: Any) -> dict[str, Any]:
    return {"condition": name, "status": status, "value": value, "limit": limit}


def verdict_of(failed: bool, incomplete: bool) -> str:
    return "fail" if failed else "incomplete" if incomplete else "pass"


def score(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply every preregistered threshold of one returned run, which may be a cut run with unreturned iterations."""
    if manifest.get("family") != FAMILY:
        raise ValueError(f"a {FAMILY} case is required")
    settings = manifest["settings"]
    if len(entries) != len(settings):
        raise ValueError("the result must carry one entry per setting, padded for unreturned iterations")
    registered = manifest["preregistered"]
    limits = registered["thresholds"]
    tolerance = limits["level_tolerance"]
    modes = {
        "success": registered["success_modes"],
        "failure": registered["failure_modes"],
        "sentinel": registered["sentinel_modes"],
    }
    layout = segment_layout(manifest)
    samples, shots_cap = (
        manifest["max_samples"] // manifest["iterations"],
        manifest["max_shots"] // manifest["iterations"],
    )
    tasks = [
        (index, setting, entry, samples, shots_cap, modes)
        for index, (setting, entry) in enumerate(zip(settings, entries, strict=True))
    ]
    iterations = ordered_map(observation, tasks, min_items=1)

    readings: dict[tuple[str, str], dict[str, Any]] = {}
    pairs: list[dict[str, Any]] = []
    for segment in layout:
        for arm, indices in segment["arm_indices"].items():
            members = [iterations[index] for index in indices]
            ideals = {settings[index]["ideal_success"] for index in indices}
            if len(ideals) != 1:
                raise ValueError(f"segment {segment['name']} arm {arm}: the two iterations carry different ideals")
            first = settings[indices[0]]
            if not all(row["returned"] for row in members):
                continue
            readings[(segment["name"], arm)] = {
                "segment": segment["name"],
                "role": segment["role"],
                "operand": segment["operand"],
                "block": segment["block"],
                "arm": arm,
                "iterations": indices,
                "ideal": first["ideal_success"],
                "true_top_level": first["true_top_level"],
                **pool(members),
            }
            gap = abs(members[0]["a"] - members[1]["a"])
            pairs.append(
                {
                    "segment": segment["name"],
                    "arm": arm,
                    "iterations": indices,
                    "difference": gap,
                    "exceeds": gap > limits["repeat_spread"],
                }
            )
    pairs_total = sum(len(segment["arm_indices"]) for segment in layout)

    dark = [r for (_, arm), r in readings.items() if arm == "D"]
    anchor_rows = [
        iterations[index]
        for segment in layout
        if segment["role"] == "anchor"
        for index in segment["arm_indices"]["T"]
        if iterations[index]["returned"]
    ]
    early = next(s for s in layout if s["role"] == "anchor")
    late = [s for s in layout if s["role"] == "anchor"][-1]
    if not dark or not any(iterations[i]["returned"] for i in early["arm_indices"]["T"]):
        raise ValueError("the anchor-early segment and one dark reading are required")
    a_dark = mean([r["a"] for r in dark])
    a_anchor = mean([row["a"] for row in anchor_rows])
    denominator = a_anchor - a_dark
    normalized = denominator > 0

    def prime(a: float) -> float | None:
        return (a - a_dark) / denominator if normalized else None

    early_t = readings.get((early["name"], "T"))
    late_t = readings.get((late["name"], "T")) if late is not early else None
    null = {arm: readings.get((s["name"], arm)) for s in layout if s["role"] == "null" for arm in ("E0", "E1")}
    null_ideals = [settings[i]["ideal_success"] for s in layout if s["role"] == "null" for i in s["arm_indices"]["E0"]]

    # Admission.
    conditions = [
        condition(
            "anchor and dark levels",
            "pass" if a_anchor >= limits["anchor_floor"] and a_dark <= limits["dark_ceiling"] else "fail",
            {"a_anchor": a_anchor, "a_dark": a_dark},
            {"anchor_floor": limits["anchor_floor"], "dark_ceiling": limits["dark_ceiling"]},
        )
    ]
    spreads = {r["segment"]: abs(r["a"] - a_dark) for r in dark}
    conditions.append(
        condition(
            "segment dark spread",
            "pass" if max(spreads.values()) <= limits["dark_spread"] else "fail",
            {"max": max(spreads.values()), "by_segment": spreads},
            limits["dark_spread"],
        )
    )
    if early_t is None or late_t is None:
        conditions.append(condition("anchor drift", "unevaluated", None, limits["anchor_drift"]))
    else:
        drift = abs(early_t["a"] - late_t["a"])
        conditions.append(
            condition(
                "anchor drift",
                "pass" if drift <= limits["anchor_drift"] else "fail",
                {"early": early_t["a"], "late": late_t["a"], "difference": drift},
                limits["anchor_drift"],
            )
        )
    exceeding = sum(pair["exceeds"] for pair in pairs)
    conditions.append(
        condition(
            "repeated arm pairs",
            "unevaluated" if not pairs else "pass" if exceeding <= limits["repeat_failures"] else "fail",
            {"exceeding": exceeding, "pairs_evaluated": len(pairs), "pairs_total": pairs_total},
            limits["repeat_failures"],
        )
    )
    returned = [row for row in iterations if row["returned"]]
    worst = max(returned, key=lambda row: row["sentinel_share"])
    conditions.append(
        condition(
            "sentinel share",
            "pass" if worst["sentinel_share"] <= limits["sentinel_share"] else "fail",
            {"max": worst["sentinel_share"], "iteration": worst["index"], "returned_iterations": len(returned)},
            limits["sentinel_share"],
        )
    )
    if any(reading is None for reading in null.values()):
        conditions.append(condition("null levels", "unevaluated", None, limits["null_level_tolerance"]))
        null_value: dict[str, Any] = {}
    else:
        e0, e1 = null["E0"], null["E1"]
        assert e0 is not None and e1 is not None  # noqa: S101 - narrowed above for mypy
        off = max(abs(e0["a"] - null_ideals[0]), abs(e1["a"] - null_ideals[0]))
        gap = abs(e0["a"] - e1["a"])
        null_value = {"E0": e0["a"], "E1": e1["a"], "ideal": null_ideals[0], "max_offset": off, "pair_difference": gap}
        conditions.append(
            condition(
                "null levels",
                "pass" if off <= limits["null_level_tolerance"] and gap <= limits["null_pair_spread"] else "fail",
                null_value,
                {"level": limits["null_level_tolerance"], "pair": limits["null_pair_spread"]},
            )
        )
    failed = [c["condition"] for c in conditions if c["status"] == "fail"]
    unevaluated = [c["condition"] for c in conditions if c["status"] == "unevaluated"]
    admitted = not failed
    admission = {
        "verdict": "admitted" if admitted else "instrument not admitted",
        "failed": failed,
        "unevaluated": unevaluated,
        "conditions": conditions,
    }

    # Normalized readings and the branch-odds estimate.
    ratio: float | None = None
    if null and all(null.values()) and normalized:
        pooled_null = pool([iterations[i] for s in layout if s["role"] == "null" for i in _span(s)])
        null_level = prime(pooled_null["a"])
        if null_level is not None and 0 < null_level < 1:
            ratio = odds(null_level) / odds(null_ideals[0])
    for reading in readings.values():
        level = prime(reading["a"])
        reading["a_prime"] = level
        reading["deviation"] = None if level is None else level - reading["ideal"]
        reading["within_tolerance"] = None if level is None else abs(level - reading["ideal"]) <= tolerance
        reading["a_prime_odds_corrected"] = (
            None if level is None or ratio is None else odds_corrected(level, ratio) if 0 < level < 1 else level
        )
        reading["raw_departure_from_ideal"] = abs(reading["a"] - reading["ideal"])

    def verdict(rows: list[dict[str, Any]], expected: int, failing: bool) -> str:
        if not admitted:
            return "not interpreted"
        return verdict_of(failing, len(rows) < expected)

    # Conformance: pathion T readings, reference T and F readings, and the outlier allowance over the T and F readings.
    tested = [r for r in readings.values() if r["role"] in ("pathion", "reference") and r["arm"] in ("T", "F")]
    tested_expected = sum(
        1 for s in layout if s["role"] in ("pathion", "reference") for arm in ("T", "F") if arm in s["arm_indices"]
    )
    pathion_t = [r for r in tested if r["role"] == "pathion" and r["arm"] == "T"]
    reference = [r for r in tested if r["role"] == "reference"]
    outliers = [r for r in tested if r["within_tolerance"] is False]
    allowance = math.floor(round(limits["outlier_fraction"] * tested_expected, 9))
    conformance_fails = any(r["within_tolerance"] is False for r in pathion_t + reference) or len(outliers) > allowance
    pathion_t_expected = sum(1 for s in layout if s["role"] == "pathion")
    conformance = {
        "verdict": verdict(tested, tested_expected, conformance_fails),
        "pathion_t_within": sum(1 for r in pathion_t if r["within_tolerance"]),
        "pathion_t_expected": pathion_t_expected,
        "reference_within": sum(1 for r in reference if r["within_tolerance"]),
        "reference_expected": 2,
        "outliers": [(r["segment"], r["arm"]) for r in outliers],
        "outlier_allowance": allowance,
        "readings_expected": tested_expected,
        "readings_present": len(tested),
    }

    # Mutation sensitivity: C and N readings against their mutated ideals.
    mutated = [r for r in readings.values() if r["arm"] in ("C", "N")]
    mutated_expected = sum(1 for s in layout for arm in ("C", "N") if arm in s["arm_indices"])
    for reading in mutated:
        level = reading["a_prime"]
        reading["follows_true_top_level"] = (
            None if level is None else abs(level - reading["true_top_level"]) <= tolerance
        )
        reading["mutation_failure"] = (
            None
            if reading["within_tolerance"] is None
            else "follows true level"
            if not reading["within_tolerance"] and reading["follows_true_top_level"]
            else "neither level"
            if not reading["within_tolerance"]
            else None
        )
    mutation = {
        "verdict": verdict(mutated, mutated_expected, any(r["within_tolerance"] is False for r in mutated)),
        "within": sum(1 for r in mutated if r["within_tolerance"]),
        "readings_expected": mutated_expected,
        "readings_present": len(mutated),
        "failures": [(r["segment"], r["arm"], r["mutation_failure"]) for r in mutated if r["mutation_failure"]],
    }

    classes = class_table(manifest, layout, readings, tolerance, early_t, late_t, a_anchor)
    label_to_group = {
        "B12": [c for c in classes if c["blocks"] and c["blocks"][0][0] == "B12"],
        "C8": [c for c in classes if c["blocks"] and c["blocks"][0][0] == "C8"],
    }
    mesh_spread = {}
    for operand, groups in label_to_group.items():
        levels = [v for c in groups for v in c["t_levels"].values()]
        spread = max(levels) - min(levels) if len(levels) > 1 else None
        mesh_spread[operand] = {
            "t_levels": {k: v for c in groups for k, v in c["t_levels"].items()},
            "range": spread,
            "exceeds_tolerance": None if spread is None else spread > tolerance,
            "attributes_failure_to_mesh_variance": None if spread is None else spread >= MESH_ATTRIBUTION_SPREAD,
        }

    ideal_departure = max((r["raw_departure_from_ideal"] for r in readings.values()), default=None)
    platform = manifest["platforms"][0]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "platform": platform,
        "definitions": {
            "a": "clicks in the success modes over clicks in the success and failure modes, per iteration or pooled",
            "pooling": "the two iterations of one arm in one segment add their clicks",
            "sentinel_share": "clicks in the sentinel modes over the iteration's returned events (samples)",
            "a_dark": "mean of the pooled dark readings of every segment",
            "a_anchor": "mean of the returned anchor T iteration readings",
            "a_prime": "(a - a_dark) / (a_anchor - a_dark)",
            "odds_corrected": (
                "a_prime with its odds divided by r; r is the odds of the normalized pooled null level "
                "over the odds of the null ideal"
            ),
            "raw_tests": "dark spread, anchor drift, repeated pairs and null levels use raw a",
        },
        "thresholds": limits,
        "instrument": {
            "a_dark": a_dark,
            "a_anchor": a_anchor,
            "normalization_denominator": denominator,
            "anchor_iterations_used": [row["index"] for row in anchor_rows],
            "branch_odds_ratio": ratio,
        },
        "admission": admission,
        "conformance": conformance,
        "mutation": mutation,
        "mesh_spread": mesh_spread,
        "classes": classes,
        "null": null_value,
        "repeated_pairs": pairs,
        "ideal_departure": {"max_pooled_raw": ideal_departure},
        "readings": list(readings.values()),
        "iterations": iterations,
        "caveats": [f"unevaluated: {name}" for name in unevaluated],
    }
    if platform.startswith("sim:"):
        complete = len(returned) == len(settings)
        within = ideal_departure is not None and ideal_departure <= SIMULATOR_TOLERANCE
        result["simulator_gate"] = {
            "tolerance": SIMULATOR_TOLERANCE,
            "max_pooled_departure": ideal_departure,
            "iterations_returned": len(returned),
            "verdict": "proceed to the QPU job" if complete and within else "stop before the QPU job",
        }
    return result


def _span(segment: dict[str, Any]) -> range:
    """The consecutive iteration indices of one segment."""
    flat = [index for indices in segment["arm_indices"].values() for index in indices]
    return range(min(flat), max(flat) + 1)


def class_table(
    manifest: dict[str, Any],
    layout: list[dict[str, Any]],
    readings: dict[tuple[str, str], dict[str, Any]],
    tolerance: float,
    early_t: dict[str, Any] | None,
    late_t: dict[str, Any] | None,
    a_anchor: float,
) -> list[dict[str, Any]]:
    """The four block classes that occur only at dimension 32: three tested classes and the rank-1 anchor class."""
    census = manifest["block_classes"]
    table = []
    for label, class_id in census["pathion_only_classes"].items():
        found = CLASS_LABEL.fullmatch(label)
        if found is None:
            raise ValueError(f"unreadable class label {label!r}")
        if found["last"] is not None:
            ordinals = list(range(int(found["first"]), int(found["last"]) + 1))
        else:
            ordinals = [int(found["first"]), int(found["second"])]
        names = [
            s["name"]
            for s in layout
            if s["role"] == "pathion" and s["operand"] == found["operand"] and s["block"] in ordinals
        ]
        arms: dict[str, dict[str, Any]] = {}
        for arm in ("T", "F", "C", "N"):
            levels = {n: readings[(n, arm)] for n in names if (n, arm) in readings}
            if levels:
                arms[arm] = {
                    name: {
                        "a_prime": r["a_prime"],
                        "ideal": r["ideal"],
                        "deviation": r["deviation"],
                        "within_tolerance": r["within_tolerance"],
                    }
                    for name, r in levels.items()
                }
        t_levels = {n: arms["T"][n]["a_prime"] for n in arms.get("T", {}) if arms["T"][n]["a_prime"] is not None}
        spread = max(t_levels.values()) - min(t_levels.values()) if len(t_levels) > 1 else None
        table.append(
            {
                "class": label,
                "class_id": class_id,
                "blocks": [[found["operand"], ordinal] for ordinal in ordinals],
                "segments": names,
                "arms": arms,
                "t_levels": t_levels,
                "t_mean": mean(list(t_levels.values())) if t_levels else None,
                "t_range": spread,
                "range_exceeds_tolerance": None if spread is None else spread > tolerance,
                "range_attributes_failure": None if spread is None else spread >= MESH_ATTRIBUTION_SPREAD,
            }
        )
    table.append(
        {
            "class": "A16 blocks 4 to 7 (rank 1, anchor only)",
            "class_id": census["anchor_class"],
            "blocks": [],
            "segments": [s["name"] for s in layout if s["role"] == "anchor"],
            "a_anchor": a_anchor,
            "early_t_raw": None if early_t is None else early_t["a"],
            "late_t_raw": None if late_t is None else late_t["a"],
            "note": "a rank-1 block reads identically in any click basis, so it anchors the scale and tests no sign",
            "t_levels": {},
        }
    )
    return table


def describe(directory: Path) -> dict[str, Any]:
    """Validate the retained run record, then score its returned iterations."""
    facts = qd_platform.run_facts(directory)
    manifest = json.loads((directory / "cases.json").read_bytes())
    results = json.loads((directory / "results.json").read_bytes())
    if manifest.get("family") != FAMILY or results["status"]["status"] not in qd_platform.TERMINAL:
        raise ValueError(f"a terminal {FAMILY} run is required")
    scored = score(manifest, results["iterations"])
    return {
        **scored,
        "job_id": results["job_id"],
        "job_status": results["status"]["status"],
        "backend": facts["backends"][0],
        "charge": facts["charge"],
        "artifact_sha256": {
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in FILES
            if (directory / name).is_file()
        },
        "interpretation": (
            "Conformance of programmed operator blocks to their interference law on one 12-mode mesh; the client "
            "computes every cd_core sign, so the chip does not compute the algebra."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, help="write the analysis here instead of standard output")
    parser.add_argument("--sim-gate", action="store_true", help="exit 1 unless a simulator run clears the stop gate")
    args = parser.parse_args()
    analysis = describe(args.run)
    text = json.dumps(analysis, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out is None:
        print(text, end="")
    else:
        args.out.write_text(text, encoding="utf-8")
    if args.sim_gate:
        gate = analysis.get("simulator_gate")
        if gate is None:
            raise SystemExit("--sim-gate needs a sim: platform run")
        print(f"simulator gate: {gate['verdict']} (max departure {gate['max_pooled_departure']})")
        return 0 if gate["verdict"].startswith("proceed") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
