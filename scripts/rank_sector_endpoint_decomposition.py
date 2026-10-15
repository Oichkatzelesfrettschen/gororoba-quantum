"""Decompose the rank-sector estimation endpoints against exact algebra, the noise model and the other device.

The rank-sector family registers 196 contracts: 20 directional tests
(minimum_effect set), 160 success-probability means and 16 packed-minus-isolated
differences (precision_half_width set, no null test). This analysis takes the
collected ibm_kingston and ibm_fez runs and reports, for the 160 means:

- the exact success probability (rank_sector_experiments.exact_success_probability),
  the approved record's calibrated noise-model prediction and its simulation
  radius, and each device's measured estimate with its preregistered
  half-width;
- endpoints whose measurement departs from the model by more than the
  half-width plus the simulation radius, by sector and probe, and the sector
  holding most of them (its physical qubits from the record);
- medians of the ideal-zero (dark) and ideal-one (bright) endpoints, with and
  without that sector;
- endpoints where the two devices differ by more than both half-widths.

It tests shot-order stationarity of every Kingston member: the rate of its most
frequent outcome in STATIONARITY_BLOCKS consecutive shot blocks of its raw
register, as a chi-square statistic per degree of freedom by sector. It also
tabulates the 16 packing differences, and the median box-kite contrast
of each ripple lane on both devices (Kingston from the calibration-scoped
secondary analysis). It is descriptive: no threshold here is preregistered.

Usage:
    "$PYTHON" scripts/rank_sector_endpoint_decomposition.py --out results/live/rank-sector-endpoint-decomposition.json
    "$PYTHON" scripts/rank_sector_endpoint_decomposition.py --check results/live/rank-sector-endpoint-decomposition.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "results/live"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import rank_sector_experiments  # noqa: E402

DEVICES = {
    "ibm_kingston": {
        "approved": "2026-10-15T030638.132007Z",
        "collected": "2026-10-15T030903.235380Z",
        "ripple_record": "2026-10-15T031229.371738Z",
        "ripple_observables": "2026-10-15T031229.371738Z/calibration-scoped-analysis.json",
    },
    "ibm_fez": {
        "approved": "2026-10-13T031726.380783Z",
        "collected": "2026-10-13T032011.664435Z",
        "ripple_record": "2026-10-13T024407.448597Z",
        "ripple_observables": "2026-10-13T025444.603480Z/collect.json",
    },
}
STATIONARITY_BLOCKS = 8
SUCCESS = re.compile(r"rank_sector_(\d)_(.+)_t(\d+)d(\d+)_success$")


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def model(run: str) -> dict[str, dict[str, Any]]:
    optimization = read(LIVE / run / "record.json")["optimization"]
    selected = next(c for c in optimization["candidates"] if c["name"] == optimization["selected"])
    return {observable["name"]: observable for observable in selected["observables"]}


def measured(run: str) -> dict[str, dict[str, Any]]:
    analysis = read(LIVE / run / "collect.json")[0]["family_analysis"]
    return {observable["name"]: observable for observable in analysis["observables"]}


def ripple_observables(path: str) -> dict[str, dict[str, Any]]:
    data = read(LIVE / path)
    observables = data[0]["family_analysis"]["observables"] if isinstance(data, list) else data["observables"]
    return {observable["name"]: observable for observable in observables}


def stationarity(run: str) -> dict[str, Any]:
    """Chi-square of the modal outcome's rate across consecutive shot blocks, per sector."""
    record = read(LIVE / run / "record.json")
    per_sector: dict[int, list[float]] = {}
    for job in record["submission"]["jobs"]:
        for index, pub in enumerate(job["pubs"]):
            raw = read(LIVE / run / "raw" / job["job_id"] / f"pub_{index:02d}.json")
            if raw["pub_name"] != pub["name"]:
                raise ValueError(f"{job['job_id']} PUB {index} is {raw['pub_name']}, not {pub['name']}")
            for component in pub["components"]:
                bits = raw["registers"][component["registers_by_replica"][0][0]]["bitstrings"]
                size = len(bits) // STATIONARITY_BLOCKS
                modal = Counter(bits).most_common(1)[0][0]
                hits = [sum(b == modal for b in bits[i * size : (i + 1) * size]) for i in range(STATIONARITY_BLOCKS)]
                rate = sum(hits) / (size * STATIONARITY_BLOCKS)
                if 0 < rate < 1:
                    chi2 = sum((h - size * rate) ** 2 / (size * rate * (1 - rate)) for h in hits)
                    sector = int(component["group"].rsplit("_", 1)[1])
                    per_sector.setdefault(sector, []).append(chi2 / (STATIONARITY_BLOCKS - 1))
    return {
        str(sector): {
            "members": len(values),
            "mean_chi2_per_dof": round(statistics.mean(values), 3),
            "max_chi2_per_dof": round(max(values), 3),
        }
        for sector, values in sorted(per_sector.items())
    }


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 4) if values else None


def decompose() -> dict[str, Any]:
    contracts = read(LIVE / DEVICES["ibm_kingston"]["approved"] / "record.json")["observable_contracts"]
    kinds = Counter(
        "test"
        if contract["minimum_effect"] is not None
        else "packing_difference"
        if contract["name"].endswith("packed_minus_reference")
        else "success_mean"
        for contract in contracts
    )
    per_device: dict[str, Any] = {}
    estimates: dict[str, dict[str, dict[str, Any]]] = {}
    for device, runs in DEVICES.items():
        predicted, observed = model(runs["approved"]), measured(runs["collected"])
        lanes = {
            g["group"]: g["replicas"][0]["physical_qubits"]
            for g in read(LIVE / runs["collected"] / "record.json")["groups"]
        }
        rows = []
        for name, observable in sorted(observed.items()):
            match = SUCCESS.match(name)
            if not match:
                continue
            sector, probe = int(match[1]), match[2]
            exact = rank_sector_experiments.exact_success_probability(
                sector, probe, Fraction(int(match[3]), int(match[4]))
            )
            rows.append(
                {
                    "name": name,
                    "sector": sector,
                    "probe": probe,
                    "exact": float(exact),
                    "model": predicted[name]["predicted_value"],
                    "model_radius": predicted[name]["simulation_error_radius"],
                    "measured": observable["estimate"],
                    "half_width": observable["confidence_half_width"],
                }
            )
        estimates[device] = {row["name"]: row for row in rows}
        off_model = [r for r in rows if abs(r["measured"] - r["model"]) > r["half_width"] + r["model_radius"]]
        weak_sector = Counter(r["sector"] for r in off_model).most_common(1)[0][0]

        def medians(selection: list[dict[str, Any]]) -> dict[str, float | None]:
            return {
                "measured": median([r["measured"] for r in selection]),
                "model": median([r["model"] for r in selection]),
                "count": len(selection),
            }

        tests = [observed[c["name"]] for c in contracts if c["minimum_effect"] is not None]
        per_device[device] = {
            "tests_rejecting": sum(bool(t["reject_null"]) for t in tests),
            "tests": len(tests),
            "off_model_endpoints": len(off_model),
            "off_model_by_sector": dict(sorted(Counter(r["sector"] for r in off_model).items())),
            "off_model_by_probe": dict(sorted(Counter(r["probe"] for r in off_model).items())),
            "weak_sector": weak_sector,
            "weak_sector_qubits": lanes[f"rank_sector_{weak_sector}"],
            "dark_all": medians([r for r in rows if r["exact"] == 0]),
            "dark_outside_weak_sector": medians([r for r in rows if r["exact"] == 0 and r["sector"] != weak_sector]),
            "bright_outside_weak_sector": medians([r for r in rows if r["exact"] == 1 and r["sector"] != weak_sector]),
            "packing_differences": {
                name: {"estimate": round(o["estimate"], 4), "half_width": round(o["confidence_half_width"], 4)}
                for name, o in sorted(observed.items())
                if name.endswith("packed_minus_reference")
            },
        }
    kingston, fez = estimates["ibm_kingston"], estimates["ibm_fez"]
    separated = sorted(
        name
        for name in kingston
        if abs(kingston[name]["measured"] - fez[name]["measured"])
        > kingston[name]["half_width"] + fez[name]["half_width"]
    )
    ripple: dict[str, Any] = {}
    for device, runs in DEVICES.items():
        record = read(LIVE / runs["ripple_record"] / "record.json")
        lanes = {g["group"]: g["replicas"][0]["physical_qubits"] for g in record["groups"]}
        observables = ripple_observables(runs["ripple_observables"])
        terms = {c["name"]: c["terms"] for c in record["observable_contracts"]}
        by_lane: dict[str, list[float]] = {}
        for name, observable in observables.items():
            if not observable.get("reject_null") or not name.endswith("bright_minus_dark"):
                continue
            lane = sorted({re.search(r"lane(\d+)", t["member"])[1] for t in terms[name]})  # type: ignore[index]
            by_lane.setdefault(",".join(lane), []).append(observable["estimate"])
        ripple[device] = {
            lane: {
                "box_kite_median": median(values),
                "contrasts": len(values),
                "qubits": lanes[f"ripple_atlas_lane{lane}"],
            }
            for lane, values in sorted(by_lane.items())
        }
    return {
        "schema": "rank-sector-endpoint-decomposition-v1",
        "scope": "Descriptive decomposition of collected estimation endpoints; no threshold here is preregistered.",
        "contract_kinds": dict(sorted(kinds.items())),
        "devices": per_device,
        "kingston_vs_fez_separated": separated,
        "ripple_lanes": ripple,
        "kingston_shot_order_stationarity": stationarity(DEVICES["ibm_kingston"]["collected"]),
        "inputs_sha256": {
            path: hashlib.sha256((LIVE / path).read_bytes()).hexdigest()
            for runs in DEVICES.values()
            for path in (
                f"{runs['approved']}/record.json",
                f"{runs['collected']}/collect.json",
                runs["ripple_observables"],
            )
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    data = decompose()
    rendered = json.dumps(data, indent=1, sort_keys=True) + "\n"
    if arguments.out is not None:
        arguments.out.write_text(rendered)
    elif arguments.check.read_text() != rendered:
        raise SystemExit(f"rank-sector decomposition differs from {arguments.check}")
    for device, summary in data["devices"].items():
        print(
            f"{device}: {summary['tests_rejecting']}/{summary['tests']} tests reject; "
            f"{summary['off_model_endpoints']} of 160 means off the model, sector {summary['weak_sector']} "
            f"(qubits {summary['weak_sector_qubits']}) holds {summary['off_model_by_sector'][summary['weak_sector']]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
