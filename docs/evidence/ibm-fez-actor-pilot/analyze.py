"""Descriptive Fez full-register analysis of externally anchored PUBs."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path.cwd()
RUN = ROOT / "results/live/2026-10-29T191606.826758Z"
COLLECTION_SHA = "979b07a5ab676cca4918dc9c2b690ab4c145e93b017a4d5cc45537ed6138b186"
RECORD_SHA = "57ba884d85602af45de06e6604b289482cecca4cec184ea58f73109eaf28d00c"
sys.path[:0] = [str(ROOT / "gororoba_quantum"), str(ROOT / "scripts")]
from readout_information_controls import observed_information, paired_component_moments  # noqa: E402

from parallel import ordered_map  # noqa: E402


def read_sha(path, sha):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise ValueError(f"anchored digest differs: {path.name}")
    return json.loads(data)


def rounded(value):
    """Canonicalize descriptive floating-point values for portable replay."""
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, list):
        return [rounded(item) for item in value]
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    return value


def analyze_pub(task):
    job_id, pub, allocation = task
    directory = RUN / "raw" / job_id
    name = pub["name"]
    raw_path = directory / f"pub_{pub['pub_index']:02d}.json"
    index_name = pub["index_file"]
    manifest_name = pub["manifest_file"]
    if not re.fullmatch(r"index-[0-9a-f]{64}\.json", index_name):
        raise ValueError("invalid immutable index identity")
    if not re.fullmatch(r"projection-[0-9a-f]{64}\.json", manifest_name):
        raise ValueError("invalid projection identity")
    index = read_sha(directory / index_name, index_name[6:-5])
    raw = read_sha(raw_path, index["files"][raw_path.name])
    manifest = read_sha(directory / manifest_name, manifest_name[11:-5])
    shots = raw["registers"]["c"]["bitstrings"]
    count = len(shots)
    if raw["pub_name"] != name or count != allocation["shots"] or any(len(x) != 156 for x in shots):
        raise ValueError("PUB identity, width or shot count differs")
    encoded = np.frombuffer("".join(shots).encode("ascii"), dtype=np.uint8).reshape(count, 156)
    if not np.all((encoded == 48) | (encoded == 49)):
        raise ValueError("invalid bitstring")
    measured = (encoded[:, ::-1] - 48).copy()
    prep = np.zeros(156, dtype=np.uint8)
    for bit in manifest["bits"]:
        if bit["logical"] != bit["index"] or bit["physical"] != bit["index"]:
            raise ValueError("analysis expects validated identity mapping")
        prep[bit["index"]] = bit["prepared"]
    errors = measured ^ prep
    cells = np.bincount(2 * errors[:, 0] + errors[:, 1], minlength=4).astype(int)
    accepted = pub["result"]["projection"]["pair_counts"][0]["error_cells_00_01_10_11"]
    if cells.tolist() != accepted:
        raise ValueError("raw pair counts disagree with anchored sparse replay")
    n00, n01, n10, n11 = map(int, cells)
    moments = paired_component_moments(tuple(map(int, cells)))
    n = count
    p0 = (n10 + n11) / n
    p1 = (n01 + n11) / n
    parity = (n01 + n10) / n
    shared = n11 / n
    isolated = parity
    difference = (n01 - n10) / n
    gain = min((n11 - n01) / n, (n11 - n10) / n)
    if not np.isclose(gain, shared - isolated / 2 - abs(difference) / 2, rtol=0, atol=1e-14):
        raise ValueError("parity decomposition disagrees")
    x = errors[:, 0].astype(float)
    y = errors[:, 1].astype(float)
    rho = float(np.corrcoef(x, y)[0, 1]) if 0 < x.mean() < 1 and 0 < y.mean() < 1 else None
    half = count // 2
    half_differences = [float(errors[half:, i].mean() - errors[:half, i].mean()) for i in (0, 1)]
    sensor_ids = np.array([i for i in range(156) if i not in (0, 1, 2)])
    sensors = errors[:, sensor_ids]
    marginal = sensors.mean(axis=0)
    sensor_float = sensors.astype(np.float64)
    joint = (sensor_float.T @ sensor_float) / n
    gains = 2 * joint - np.maximum(marginal[:, None], marginal[None, :])
    tri = np.triu_indices(len(sensor_ids), 1)
    rank = np.argsort(gains[tri], kind="stable")[-3:][::-1]
    top = [
        {
            "qubits": [int(sensor_ids[tri[0][k]]), int(sensor_ids[tri[1][k]])],
            "gain": float(gains[tri][k]),
            "shared_count": int(round(joint[tri][k] * n)),
            "marginals": [float(marginal[tri[0][k]]), float(marginal[tri[1][k]])],
        }
        for k in rank
    ]
    sensor_load = sensors.sum(axis=1)
    if np.std(sensor_load[:-1]) and np.std(sensor_load[1:]):
        lag1 = float(np.corrcoef(sensor_load[:-1], sensor_load[1:])[0, 1])
    else:
        lag1 = None
    # Independent Bernoulli reference uses the empirical marginal rates, not a fitted physical model.
    distribution = np.array([1.0])
    for probability in marginal:
        distribution = np.convolve(distribution, [1 - probability, probability])
    threshold = 5
    tail_obs = float(np.mean(sensor_load >= threshold))
    tail_reference = float(distribution[threshold:].sum())
    timing = raw["metadata"].get("compilation", {}).get("scheduler_timing", {})
    rows = timing.get("timing", "").splitlines()
    starts = {}
    for line in rows:
        match = re.fullmatch(r"main,measure_(\d+),Qubit (\d+),(\d+),(\d+),play", line)
        if match and match.group(1) == match.group(2):
            qubit, start = int(match.group(1)), int(match.group(3))
            if qubit in starts:
                raise ValueError("duplicate measurement start")
            starts[qubit] = start
    if set(starts) != set(range(156)):
        raise ValueError("served scheduler lacks full measurement schedule")
    actor_x = [line for line in rows if re.fullmatch(r"main,x_2,Qubit 2,\d+,\d+,play", line)]
    if len(actor_x) != (1 if allocation["arm"] == "active" else 0):
        raise ValueError("actor scheduler activity differs")
    schedule = {"circuit_duration_dt": timing.get("circuit_duration"), "actor_x": actor_x}
    output_codes = measured[:, 0] + 2 * measured[:, 1]
    output_counts = np.bincount(output_codes, minlength=4).astype(int).tolist()
    result = {
        "name": name,
        "job_id": job_id,
        "pub_index": pub["pub_index"],
        "delay_us": round(allocation["rep_delay_seconds"] * 1e6),
        "arm": allocation["arm"],
        "input": allocation["input"],
        "n": n,
        "cells": cells.tolist(),
        "p0": p0,
        "p1": p1,
        "parity_error": parity,
        "gain": gain,
        "shared": shared,
        "isolated": isolated,
        "imbalance": difference,
        "max_gain_given_marginals": 2 * min(p0, p1) - max(p0, p1),
        "rho": rho,
        "score_variances": [float(v) for v in moments["sample_variances"]],
        "score_covariance": float(moments["sample_covariance"]),
        "half_difference": half_differences,
        "sensor_mean_errors": float(sensor_load.mean()),
        "sensor_tail_5_observed": tail_obs,
        "sensor_tail_5_independent_reference": tail_reference,
        "sensor_count_lag1": lag1,
        "positive_sensor_pair_count": int(np.count_nonzero(gains[tri] > 0)),
        "top_sensor_pairs_posthoc": top,
        "output_counts": output_counts,
        "sensor_marginals": marginal.tolist(),
        "sensor_ids": sensor_ids.tolist(),
    }
    return result, starts, schedule


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare the replay with retained bytes")
    args = parser.parse_args()
    record = read_sha(RUN / "record.json", RECORD_SHA)
    collection = read_sha(RUN / f"actor-collection-{COLLECTION_SHA}.json", COLLECTION_SHA)
    if collection["record_sha256"] != RECORD_SHA or not collection["all_allocations_retained"]:
        raise ValueError("incomplete or mismatched acquisition")
    case = record["family_configuration"]["case"]
    allocations = {row["name"]: row for row in case["allocations"]}
    tasks = []
    for job_id, job in collection["jobs"].items():
        if job["status"] != "DONE":
            raise ValueError("non-completed job")
        tasks.extend((job_id, pub, allocations[pub["name"]]) for pub in job["pubs"])
    analyzed = ordered_map(analyze_pub, tasks, min_items=1)
    results = [row[0] for row in analyzed]
    measurements = {row[0]["name"]: row[1] for row in analyzed}
    job_schedules = {row[0]["name"]: row[2] for row in analyzed}
    conditions = {(row["delay_us"], row["arm"], row["input"]): row for row in results}
    if len(results) != 24 or set(allocations) != {r["name"] for r in results}:
        raise ValueError("case condition coverage differs")
    first = next(iter(measurements.values()))
    identical_measurement_schedule = all(row == first for row in measurements.values())
    contrasts = []
    for delay in (30, 50, 250):
        for input_value in range(4):
            a = conditions[(delay, "active", input_value)]
            b = conditions[(delay, "idle", input_value)]
            diffs = np.array(a["sensor_marginals"]) - np.array(b["sensor_marginals"])
            idx = np.argsort(np.abs(diffs), kind="stable")[-3:][::-1]
            contrasts.append(
                {
                    "delay_us": delay,
                    "input": input_value,
                    "delta_p0": a["p0"] - b["p0"],
                    "delta_p1": a["p1"] - b["p1"],
                    "delta_parity_error": a["parity_error"] - b["parity_error"],
                    "delta_gain": a["gain"] - b["gain"],
                    "top_sensor_shifts_posthoc": [{"qubit": a["sensor_ids"][i], "delta": float(diffs[i])} for i in idx],
                }
            )
    information = []
    for delay in (30, 50, 250):
        for arm in ("idle", "active"):
            counts = [conditions[(delay, arm, i)]["output_counts"] for i in range(4)]
            value = observed_information(counts)
            information.append({"delay_us": delay, "arm": arm, **value})
    result = {
        "schema": "ibm-fez-descriptive-analysis-v1",
        "collection_sha256": COLLECTION_SHA,
        "record_sha256": RECORD_SHA,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                Path(__file__).resolve(),
                ROOT / "scripts/readout_information_controls.py",
                ROOT / "gororoba_quantum/parallel.py",
            )
        },
        "analysis_boundary": (
            "Descriptive only. Shot positions are within PUB; cross-PUB chronology, randomization, "
            "independence, physical alignment and inference remain unverified."
        ),
        "conditions": results,
        "actor_contrasts": contrasts,
        "information": information,
        "scheduler": {
            "identical_measurement_starts_all_24": identical_measurement_schedule,
            "measurement_start_dt_unique": sorted(set(first.values())),
            "durations_dt_unique": sorted({v["circuit_duration_dt"] for v in job_schedules.values()}),
            "actor_x_matches_arm": True,
        },
        "sampling": {
            "conditions": 24,
            "shots_total": sum(r["n"] for r in results),
            "sensor_pair_scan_per_condition": 153 * 152 // 2,
            "sensor_pair_selection": "post hoc within each condition",
        },
        "reference_model": (
            "Independent Bernoulli errors with observed marginal rates; plug-in expected sensor-tail "
            "frequencies, not a test or physical model."
        ),
    }
    out = ROOT / "docs/evidence/ibm-fez-actor-pilot/analysis.json"
    payload = json.dumps(rounded(result), indent=2, allow_nan=False) + "\n"
    if args.check:
        if out.read_text() != payload:
            raise ValueError("Fez analysis replay differs from retained bytes")
    else:
        out.write_text(payload)
    print(
        "saved", out, "shots", result["sampling"]["shots_total"], "identical schedule", identical_measurement_schedule
    )


if __name__ == "__main__":
    main()
