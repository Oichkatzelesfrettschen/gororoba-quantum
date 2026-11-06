"""Score a returned Ascella two-coset-block run against its preregistered thresholds.

The counting helpers (odds, mean, condition, verdict_of) come from the predecessor's scoring module; the layout,
the per-slot calibration and the decisions differ because one iteration reads two blocks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import qd_platform
from ascella_pathion_four_term_blocks_analysis import condition, mean, verdict_of
from experiment_analysis import decode_photonic_counts

from parallel import ordered_map

FAMILY = "ascella_pathion_coset_block_pairs"
SCHEMA = "ascella-pathion-coset-block-pairs-analysis-v1"
FILES = ("cases.json", "circuit.json", "job-body.json", "submission.json", "results.json", "raw/result.json")
WIDTH = 12
ACTIVE = 9
SLOTS = ("A", "B")
# docs/design/ascella-pathion-coset-block-pairs-case.md, "Outcomes": a simulator level that departs from the ideal
# law by more than this stops the sequence before the QPU job. cases.json carries no such key.
SIMULATOR_TOLERANCE = 0.01
EM_ITERATIONS = 400


def observation(task: tuple[int, dict[str, Any], dict[str, Any], int, int, dict[str, Any]]) -> dict[str, Any]:
    """One iteration's click counts per slot, bound to the request that produced them."""
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
    slot = {name: sum(ports[m] for m in modes["slots"][name]) for name in SLOTS}
    failure = ports[modes["failure"]]
    sentinel = sum(ports[m] for m in modes["sentinel"])
    total = sum(slot.values()) + failure
    if total == 0:
        raise ValueError(f"{setting['name']}: no click in the slot or failure modes")
    law = setting["ideal_label_law"]
    distance = 0.5 * sum(abs(ports[m] / total - law[m]) for m in range(ACTIVE))
    return {
        "index": index,
        "name": setting["name"],
        "returned": True,
        "port_counts": ports,
        "invalid_events": invalid,
        "events": events,
        "shots_used": shots,
        "slot": slot,
        "failure": failure,
        "sentinel": sentinel,
        "total": total,
        "sentinel_share": sentinel / events,
        "label_law_distance": distance,
    }


def layout(manifest: dict[str, Any]) -> dict[str, Any]:
    """The distinct settings with their iteration indices per slot orientation, checked against the frozen settings."""
    settings = manifest["settings"]
    if len(settings) != manifest["iterations"]:
        raise ValueError("the settings do not cover the iterations")
    designs = {design["name"]: design for design in manifest["designs"]}
    names = [setting["setting"] for setting in settings]
    if names != names[::-1]:
        raise ValueError("the setting order is not a palindrome")
    by_setting: dict[str, dict[int, list[int]]] = {name: {} for name in designs}
    for index, setting in enumerate(settings):
        if setting["observation_index"] != index or setting["setting"] not in designs:
            raise ValueError(f"{setting['name']}: setting differs from its position")
        design = designs[setting["setting"]]
        orientation = setting["orientation"]
        items = [tuple(item) for item in design["items"]]
        shown = [(setting["slots"][slot]["code"], setting["slots"][slot]["arm"]) for slot in SLOTS]
        if shown != (items if orientation == 0 else items[::-1]) or setting["role"] != design["role"]:
            raise ValueError(f"{setting['name']}: slot items differ from design {design['name']}")
        by_setting[setting["setting"]].setdefault(orientation, []).append(index)
    for name, design in designs.items():
        found = by_setting[name]
        if design["role"] in ("sign", "null") and {o: len(v) for o, v in found.items()} != {0: 1, 1: 1}:
            raise ValueError(f"{name}: a sign setting runs once in each slot orientation")
    return {"designs": designs, "by_setting": by_setting}


def pooled_counts(rows: list[dict[str, Any]], slot: str) -> tuple[float, float, float]:
    """(slot clicks, all labeled clicks, failure clicks) summed over rows."""
    return (
        sum(row["slot"][slot] for row in rows),
        sum(row["total"] for row in rows),
        sum(row["failure"] for row in rows),
    )


def calibrate(rows: list[dict[str, Any]], settings: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-slot dark, anchor and efficiency relative to the failure mode, from the anchor and dark iterations.

    Dark: both blocks in their kernels, so the photon sits in the failure mode and any slot click is leakage; its
    share of the labeled clicks is d. Anchor: an A16 rank-1 block at ideal level 1 beside a kernel block, which
    puts half the photon in the slot and half in the failure mode; the dark-subtracted level a* = 2 r / (1 + r)
    gives the slot's efficiency r relative to the failure mode.
    """
    dark_rows = [r for r, s in zip(rows, settings, strict=True) if r["returned"] and s["role"] == "dark"]
    calibration: dict[str, Any] = {"dark": {}, "anchor_raw": {}, "efficiency": {}, "anchor_rows": {}, "dark_rows": []}
    if not dark_rows:
        raise ValueError("the early dark iteration is required")
    calibration["dark_rows"] = [r["index"] for r in dark_rows]
    for slot in SLOTS:
        bright = [
            r
            for r, s in zip(rows, settings, strict=True)
            if r["returned"] and s["role"] == "anchor" and s["slots"][slot]["arm"] == "T"
        ]
        if not bright:
            raise ValueError("the early anchor iterations are required")
        clicks, total, _ = pooled_counts(dark_rows, slot)
        share = clicks / total
        calibration["dark"][slot] = share
        calibration["anchor_rows"][slot] = [r["index"] for r in bright]
        calibration["anchor_raw"][slot] = 2 * sum(r["slot"][slot] for r in bright) / sum(r["total"] for r in bright)
        star = sum(r["slot"][slot] - share * r["total"] for r in bright)
        other = "B" if slot == "A" else "A"
        other_share = pooled_counts(dark_rows, other)[0] / pooled_counts(dark_rows, other)[1]
        denominator = sum(
            (r["slot"][slot] - share * r["total"]) + (r["slot"][other] - other_share * r["total"]) + r["failure"]
            for r in bright
        )
        a_star = 2 * star / denominator
        if not 0 < a_star < 2:
            raise ValueError(f"slot {slot}: the dark-subtracted anchor level {a_star} is outside (0, 2)")
        calibration["efficiency"][slot] = a_star / (2 - a_star)
    return calibration


def slot_levels(row: dict[str, Any], calibration: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Raw level a, normalized a' and calibrated level of both slots of one returned iteration."""
    dark, eff = calibration["dark"], calibration["efficiency"]
    star = {slot: row["slot"][slot] - dark[slot] * row["total"] for slot in SLOTS}
    scaled = {slot: star[slot] / eff[slot] for slot in SLOTS}
    denominator = sum(scaled.values()) + row["failure"]
    out = {}
    for slot in SLOTS:
        a = 2 * row["slot"][slot] / row["total"]
        a_dark = 2 * dark[slot]
        denominator_prime = calibration["anchor_raw"][slot] - a_dark
        out[slot] = {
            "a": a,
            "a_prime": (a - a_dark) / denominator_prime if denominator_prime > 0 else float("nan"),
            "l_hat": 2 * scaled[slot] / denominator,
        }
    return out


def standard_error(level: float, total: int) -> float:
    return math.sqrt(max(level * (2 - level), 0.0) / total)


def mode_efficiency_fit(rows: list[dict[str, Any]], settings: list[dict[str, Any]]) -> list[float] | None:
    """Maximum-likelihood efficiency of each of modes 0..8 under counts_m proportional to eta_m times the ideal law."""
    usable = [(r, s) for r, s in zip(rows, settings, strict=True) if r["returned"]]
    if not usable:
        return None
    counts = np.array([[r["port_counts"][m] for m in range(ACTIVE)] for r, _ in usable], dtype=float)
    law = np.array([s["ideal_label_law"] for _, s in usable], dtype=float)
    totals = counts.sum(axis=1)
    eta = np.ones(ACTIVE)
    for _ in range(EM_ITERATIONS):
        denominator = law @ eta
        expected = (totals / denominator)[:, None] * law
        eta = np.where(expected.sum(axis=0) > 0, counts.sum(axis=0) / np.maximum(expected.sum(axis=0), 1e-300), eta)
        eta = eta / np.exp(np.mean(np.log(np.maximum(eta, 1e-300))))
    return [float(v) for v in eta]


def model_rows(
    rows: list[dict[str, Any]], settings: list[dict[str, Any]], eta: list[float], modes: dict[str, Any]
) -> list[dict[str, Any]]:
    """Expected click counts of every returned iteration under per-mode efficiencies, in the row format."""
    out = []
    weights = np.array(eta)
    for row, setting in zip(rows, settings, strict=True):
        if not row["returned"]:
            out.append(row)
            continue
        law = np.array(setting["ideal_label_law"]) * weights
        counts = row["total"] * law / law.sum()
        out.append(
            {
                **row,
                "slot": {name: float(sum(counts[m] for m in modes["slots"][name])) for name in SLOTS},
                "failure": float(counts[modes["failure"]]),
            }
        )
    return out


def readings_of(
    manifest: dict[str, Any],
    structure: dict[str, Any],
    rows: list[dict[str, Any]],
    calibration: dict[str, Any],
    tolerance: float,
) -> list[dict[str, Any]]:
    """Each block item of every sign and null setting, in both slot orientations and pooled over them."""
    settings = manifest["settings"]
    readings = []
    for name, design in structure["designs"].items():
        if design["role"] not in ("sign", "null"):
            continue
        for item_index in (0, 1):
            per: dict[str, Any] = {}
            for orientation in (0, 1):
                index = structure["by_setting"][name][orientation][0]
                slot = SLOTS[item_index if orientation == 0 else 1 - item_index]
                if not rows[index]["returned"]:
                    continue
                level = slot_levels(rows[index], calibration)[slot]
                per[str(orientation)] = {
                    "iteration": index,
                    "slot": slot,
                    **level,
                    "se": standard_error(min(max(level["l_hat"], 1e-9), 2 - 1e-9), rows[index]["total"]),
                }
            first = settings[structure["by_setting"][name][0][0]]["slots"]["A" if item_index == 0 else "B"]
            if not per:
                continue
            values = list(per.values())
            pooled = mean([v["l_hat"] for v in values])
            record = {
                "setting": name,
                "item": item_index,
                "role": design["role"],
                "group": design["group"],
                "block": first["block"],
                "code": first["code"],
                "arm": first["arm"],
                "ideal": first["ideal_level"],
                "true_top_level": first["true_top_level"],
                "orientations": per,
                "complete": len(per) == 2,
                "l_hat": pooled,
                "a_prime": mean([v["a_prime"] for v in values]),
                "a": mean([v["a"] for v in values]),
                "se": math.sqrt(sum(v["se"] ** 2 for v in values)) / len(values),
                "deviation": pooled - first["ideal_level"],
                "within_tolerance": abs(pooled - first["ideal_level"]) <= tolerance,
                "mirror_difference": abs(values[0]["l_hat"] - values[1]["l_hat"]) if len(values) == 2 else None,
            }
            readings.append(record)
    return readings


def c8_spread(
    manifest: dict[str, Any], rows: list[dict[str, Any]], calibration: dict[str, Any], predecessor: dict[str, Any]
) -> dict[str, Any]:
    """Within-class contrast of the C8 T readings per slot: block 7 minus the mean of blocks 4, 5 and 6."""
    registered = manifest["preregistered"]
    cells: dict[tuple[int, str], list[float]] = {}
    for row, setting in zip(rows, manifest["settings"], strict=True):
        if not row["returned"] or setting["role"] != "sign":
            continue
        levels = slot_levels(row, calibration)
        for slot in SLOTS:
            item = setting["slots"][slot]
            operand, ordinal = item["block"].split("/")
            if operand == "C8" and item["arm"] == "T":
                cells.setdefault((int(ordinal), slot), []).append(levels[slot]["l_hat"] - item["ideal_level"])
    threshold = registered["thresholds"]["contrast_fraction"] * predecessor["c8_contrast"]
    needed = [(ordinal, slot) for ordinal in (4, 5, 6, 7) for slot in SLOTS]
    result: dict[str, Any] = {
        "predecessor_contrast": predecessor["c8_contrast"],
        "threshold": threshold,
        "cells": {f"c8-{o}/slot {s}": mean(v) for (o, s), v in sorted(cells.items())},
        "cell_readings": {f"c8-{o}/slot {s}": len(v) for (o, s), v in sorted(cells.items())},
    }
    if any(cell not in cells for cell in needed):
        return {**result, "verdict": "incomplete", "contrast": {}}
    contrast = {}
    for slot in SLOTS:
        deviation = {o: mean(cells[(o, slot)]) for o in (4, 5, 6, 7)}
        contrast[slot] = {
            "low_blocks_mean_deviation": mean([deviation[4], deviation[5], deviation[6]]),
            "block_7_deviation": deviation[7],
            "contrast": deviation[7] - mean([deviation[4], deviation[5], deviation[6]]),
        }
    reproduced = [slot for slot in SLOTS if contrast[slot]["contrast"] >= threshold]
    reversed_in = [slot for slot in SLOTS if contrast[slot]["contrast"] <= -threshold]
    verdict = {2: "follows the block", 1: "follows the mode slot", 0: "not reproduced"}[len(reproduced)]
    swing = {f"c8-{o}": mean(cells[(o, "B")]) - mean(cells[(o, "A")]) for o in (4, 5, 6, 7)}
    return {
        **result,
        "verdict": verdict,
        "contrast": contrast,
        "slots_reproducing": reproduced,
        "slots_reversed": reversed_in,
        "slot_swing_by_block": swing,
    }


def pair_differences(readings: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """For each same-class T/T setting, the difference between its two blocks in each slot orientation."""
    wanted = {frozenset(pair) for pair in manifest["preregistered"]["same_class_pairs"]}
    by_setting: dict[str, list[dict[str, Any]]] = {}
    for reading in readings:
        by_setting.setdefault(reading["setting"], []).append(reading)
    table = []
    for name, items in by_setting.items():
        if len(items) != 2 or {i["arm"] for i in items} != {"T"} or frozenset(i["code"] for i in items) not in wanted:
            continue
        first, second = sorted(items, key=lambda i: i["item"])
        if not (first["complete"] and second["complete"]):
            continue
        difference = {o: first["orientations"][o]["l_hat"] - second["orientations"][o]["l_hat"] for o in ("0", "1")}
        table.append(
            {
                "setting": name,
                "blocks": [first["block"], second["block"]],
                "difference_by_orientation": difference,
                "keeps_sign": difference["0"] * difference["1"] > 0,
            }
        )
    return table


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
        "slots": registered["slot_modes"],
        "failure": registered["failure_mode"],
        "sentinel": registered["sentinel_modes"],
    }
    structure = layout(manifest)
    samples, shots_cap = (
        manifest["max_samples"] // manifest["iterations"],
        manifest["max_shots"] // manifest["iterations"],
    )
    tasks = [
        (index, setting, entry, samples, shots_cap, modes)
        for index, (setting, entry) in enumerate(zip(settings, entries, strict=True))
    ]
    rows = ordered_map(observation, tasks, min_items=1)
    calibration = calibrate(rows, settings)
    half = len(settings) // 2
    returned = [row for row in rows if row["returned"]]

    def early_late(role: str, slot: str) -> tuple[dict[str, float] | None, dict[str, float] | None]:
        picks: dict[str, list[dict[str, Any]]] = {"early": [], "late": []}
        for row, setting in zip(rows, settings, strict=True):
            bright = role == "anchor" and setting["role"] == "anchor" and setting["slots"][slot]["arm"] == "T"
            if row["returned"] and (bright or (role == "dark" and setting["role"] == "dark")):
                picks["early" if row["index"] < half else "late"].append(row)
        values: list[dict[str, float] | None] = []
        for key in ("early", "late"):
            group = picks[key]
            if not group:
                values.append(None)
                continue
            total = sum(r["total"] for r in group)
            values.append({"a": 2 * sum(r["slot"][slot] for r in group) / total})
        return values[0], values[1]

    conditions = []
    anchor_values = {s: calibration["anchor_raw"][s] for s in SLOTS}
    dark_values = {s: 2 * calibration["dark"][s] for s in SLOTS}
    conditions.append(
        condition(
            "anchor and dark levels",
            "pass"
            if all(
                anchor_values[s] >= limits["anchor_floor"] and dark_values[s] <= limits["dark_ceiling"] for s in SLOTS
            )
            else "fail",
            {"anchor": anchor_values, "dark": dark_values, "efficiency_vs_failure_mode": calibration["efficiency"]},
            {"anchor_floor": limits["anchor_floor"], "dark_ceiling": limits["dark_ceiling"]},
        )
    )
    for name, role, key in (("anchor drift", "anchor", "anchor_drift"), ("dark drift", "dark", "dark_drift")):
        differences = {}
        for slot in SLOTS:
            early, late = early_late(role, slot)
            if early is not None and late is not None:
                differences[slot] = abs(early["a"] - late["a"])
        if len(differences) < len(SLOTS):
            conditions.append(condition(name, "unevaluated", differences, limits[key]))
        else:
            ok = all(d <= limits[key] for d in differences.values())
            conditions.append(condition(name, "pass" if ok else "fail", differences, limits[key]))
    worst = max(returned, key=lambda row: row["sentinel_share"])
    conditions.append(
        condition(
            "sentinel share",
            "pass" if worst["sentinel_share"] <= limits["sentinel_share"] else "fail",
            {"max": worst["sentinel_share"], "iteration": worst["index"], "returned_iterations": len(returned)},
            limits["sentinel_share"],
        )
    )
    readings = readings_of(manifest, structure, rows, calibration, tolerance)
    null_items = [r for r in readings if r["role"] == "null" and r["complete"]]
    if len(null_items) < 2:
        conditions.append(condition("null levels", "unevaluated", None, limits["null_level_tolerance"]))
    else:
        offset = max(abs(r["l_hat"] - r["ideal"]) for r in null_items)
        gap = abs(null_items[0]["l_hat"] - null_items[1]["l_hat"])
        passed = offset <= limits["null_level_tolerance"] and gap <= limits["null_pair_spread"]
        conditions.append(
            condition(
                "null levels",
                "pass" if passed else "fail",
                {"levels": [r["l_hat"] for r in null_items], "max_offset": offset, "pair_difference": gap},
                {"level": limits["null_level_tolerance"], "pair": limits["null_pair_spread"]},
            )
        )
    both = [r for r in readings if r["complete"]]
    exceeding = sum(r["mirror_difference"] > limits["mirror_spread"] for r in both)
    allowance = math.floor(round(limits["mirror_fraction"] * len(both), 9))
    conditions.append(
        condition(
            "mirror agreement",
            "unevaluated" if not both else "pass" if exceeding <= allowance else "fail",
            {"exceeding": exceeding, "readings": len(both), "allowance": allowance},
            limits["mirror_spread"],
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

    def verdict(expected: int, present: int, failing: bool) -> str:
        return "not interpreted" if not admitted else verdict_of(failing, present < expected)

    sign = [r for r in readings if r["role"] == "sign"]
    designs = manifest["designs"]
    expected_by_arm: dict[str, int] = {}
    for design in designs:
        if design["role"] == "sign":
            for _, arm in design["items"]:
                expected_by_arm[arm] = expected_by_arm.get(arm, 0) + 1
    tested = [r for r in sign if r["arm"] in ("T", "F") and r["complete"]]
    tested_expected = expected_by_arm.get("T", 0) + expected_by_arm.get("F", 0)
    top = [r for r in tested if r["arm"] == "T"]
    outliers = [r for r in tested if not r["within_tolerance"]]
    outlier_allowance = math.floor(round(limits["outlier_fraction"] * tested_expected, 9))
    conformance = {
        "verdict": verdict(
            tested_expected,
            len(tested),
            any(not r["within_tolerance"] for r in top) or len(outliers) > outlier_allowance,
        ),
        "t_within": sum(1 for r in top if r["within_tolerance"]),
        "t_expected": expected_by_arm.get("T", 0),
        "outliers": [(r["setting"], r["block"], r["arm"]) for r in outliers],
        "outlier_allowance": outlier_allowance,
        "readings_expected": tested_expected,
        "readings_present": len(tested),
    }
    mutated = [r for r in sign if r["arm"] in ("C", "N") and r["complete"]]
    mutated_expected = expected_by_arm.get("C", 0) + expected_by_arm.get("N", 0)
    for reading in mutated:
        near_true = abs(reading["l_hat"] - reading["true_top_level"]) <= tolerance
        reading["mutation_failure"] = (
            None if reading["within_tolerance"] else "follows true level" if near_true else "neither level"
        )
    mutation = {
        "verdict": verdict(mutated_expected, len(mutated), any(not r["within_tolerance"] for r in mutated)),
        "within": sum(1 for r in mutated if r["within_tolerance"]),
        "readings_expected": mutated_expected,
        "readings_present": len(mutated),
        "failures": [
            (r["setting"], r["block"], r["arm"], r["mutation_failure"]) for r in mutated if r["mutation_failure"]
        ],
    }

    # Crosstalk: the dark slot beside a bright partner, against the slot's own dark reading.
    crosstalk_rows = []
    crosstalk_expected = 0
    for row, setting in zip(rows, settings, strict=True):
        for slot, other in (("A", "B"), ("B", "A")):
            item, partner = setting["slots"][slot], setting["slots"][other]
            if item["arm"] != "D" or partner["ideal_level"] < limits["bright_partner_level"]:
                continue
            crosstalk_expected += 1
            if not row["returned"]:
                continue
            a = 2 * row["slot"][slot] / row["total"]
            excess = a - 2 * calibration["dark"][slot]
            crosstalk_rows.append(
                {
                    "iteration": row["index"],
                    "setting": setting["setting"],
                    "slot": slot,
                    "partner_level": partner["ideal_level"],
                    "a": a,
                    "excess_over_dark": excess,
                    "sentinel_scale": 2 * (4 / 3) * row["sentinel_share"],
                    "within_sentinel_scale": excess <= 2 * (4 / 3) * row["sentinel_share"],
                }
            )
    crosstalk = {
        "verdict": verdict(
            crosstalk_expected,
            len(crosstalk_rows),
            any(c["excess_over_dark"] > limits["crosstalk_ceiling"] for c in crosstalk_rows),
        ),
        "max_excess": max((c["excess_over_dark"] for c in crosstalk_rows), default=None),
        "readings_expected": crosstalk_expected,
        "readings_present": len(crosstalk_rows),
        "rows": crosstalk_rows,
    }

    # Independence: the fixed T item of each group across its partner arms.
    groups = {}
    for group in registered["independence_groups"]:
        members = [r for r in sign if r["group"] == group and r["item"] == 0 and r["complete"]]
        members_expected = sum(1 for d in designs if d["group"] == group)
        spread = max((r["l_hat"] for r in members), default=0.0) - min((r["l_hat"] for r in members), default=0.0)
        raw_spread = max((r["a"] for r in members), default=0.0) - min((r["a"] for r in members), default=0.0)
        partner_arms = {}
        for r in members:
            partner = next(x for x in sign if x["setting"] == r["setting"] and x["item"] == 1)
            partner_arms[r["setting"]] = partner["arm"]
        groups[group] = {
            "range": spread,
            "uncalibrated_range": raw_spread,
            "settings": len(members),
            "settings_expected": members_expected,
            "levels": {r["setting"]: r["l_hat"] for r in members},
            "partner_arms": partner_arms,
            "exceeds": spread > limits["independence_range"],
        }
    independence = {
        "verdict": verdict(
            sum(g["settings_expected"] for g in groups.values()),
            sum(g["settings"] for g in groups.values()),
            any(g["exceeds"] for g in groups.values()),
        ),
        "groups": groups,
    }

    predecessor = registered["predecessor"]
    spread = c8_spread(manifest, rows, calibration, predecessor)
    eta = mode_efficiency_fit(rows, settings)
    model = None
    if eta is not None and spread["verdict"] != "incomplete":
        expected_rows = model_rows(rows, settings, eta, modes)
        model = c8_spread(manifest, expected_rows, calibrate(expected_rows, settings), predecessor)
    pairs = pair_differences(readings, manifest)

    ideal_departure = max((abs(r["deviation"]) for r in readings if r["complete"]), default=None)
    platform = manifest["platforms"][0]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "platform": platform,
        "definitions": {
            "a": "twice the clicks of a slot's four modes over the clicks of modes 0..8, per iteration",
            "l_hat": (
                "calibrated level: the slot's dark-subtracted clicks over its efficiency relative to the failure "
                "mode, in the same ratio; the efficiency is a / (2 - a) of the slot's dark-subtracted anchor level"
            ),
            "a_prime": "(a - a_dark) / (a_anchor - a_dark) with the slot's own anchor and dark",
            "pooling": "the two slot orientations of one block item average their calibrated levels",
        },
        "thresholds": limits,
        "calibration": calibration,
        "admission": admission,
        "conformance": conformance,
        "mutation": mutation,
        "crosstalk": crosstalk,
        "independence": independence,
        "c8_spread": spread,
        "c8_spread_under_mode_efficiencies": model,
        "mode_efficiency": eta,
        "same_class_pair_differences": pairs,
        "ideal_departure": {"max_pooled": ideal_departure},
        "readings": readings,
        "iterations": rows,
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
            "scope": "sim:ascella is noiseless: the gate checks the client and pipeline, not the device",
        }
    return result


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
            "Conformance of programmed operator blocks to their interference law on one 12-mode mesh with two "
            "blocks per photon; the client computes every cd_core sign, so the chip does not compute the algebra."
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
