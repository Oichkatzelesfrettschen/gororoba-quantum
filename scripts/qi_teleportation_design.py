"""Prepare or analyze an unsubmitted, fixed-route six-state QI design.

No provider call or submission mode exists. The existing qi_records reader
owns receipts and raw-record validation. Random ordering uses qrng_seeds;
new QRNG allocations and provider execution retain their approval gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from teleportation_contract import (  # noqa: E402
    SCHEMA,
    make_plan,
    require,
    score_histogram,
    six_state_estimate,
    validate_plan,
)


def serialized(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def write_bundle(out: Path, plan: dict[str, Any], files: dict[str, str]) -> None:
    """Publish a complete directory without overwriting an existing case."""
    require(not out.exists(), "output already exists; retained cases are immutable")
    require(out.parent.is_dir(), "output parent must exist")
    require(files == validate_plan(plan), "circuit files disagree with the regenerated plan")
    plan_text = serialized(plan)
    plan_digest = hashlib.sha256(plan_text.encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix=".teleport-case-", dir=out.parent) as temporary:
        stage = Path(temporary) / "case"
        stage.mkdir()
        (stage / "plan.json").write_text(plan_text, encoding="utf-8")
        for batch in plan["batches"]:
            directory = stage / batch["batch"]
            directory.mkdir()
            manifest = {key: plan[key] for key in ("backend", "backend_type_id", "nqubits", "shots")}
            manifest.update(schema=SCHEMA, batch=batch["batch"], series_sha256=plan_digest, circuits=batch["circuits"])
            (directory / "cases.json").write_text(serialized(manifest), encoding="utf-8")
            for row in batch["circuits"]:
                (directory / row["file"]).write_text(files[f"{batch['batch']}/{row['file']}"], encoding="utf-8")
        require(not out.exists(), "output appeared while preparing the case")
        stage.rename(out)


def prepare(args: argparse.Namespace) -> None:
    from qi_platform import HARDWARE_BATCH_CIRCUITS

    from qrng_seeds import seed_record

    catalogue_bytes = args.catalogue.read_bytes()
    catalogue = json.loads(catalogue_bytes)
    selected = [b for b in catalogue["backend_types"] if b["identifier"] == args.backend]
    require(len(selected) == 1, "backend must resolve uniquely in the supplied catalogue")
    require(
        args.backend in {"tuna_17", "tuna_9", "tuna_5", "QXsinglenodesimulator"},
        "unsupported result-order/dialect contract",
    )
    backend = selected[0]
    require(args.blocks > 0 and args.shots > 0, "blocks and shots must be positive")
    rng = random.Random(args.seed)
    orders = []
    for _ in range(args.blocks):
        order = list(range(6 * len(args.route)))
        rng.shuffle(order)
        orders.append(order)
    plan, files = make_plan(
        args.backend,
        backend["id"],
        backend["nqubits"],
        backend["topology"],
        args.route,
        args.shots,
        orders,
        HARDWARE_BATCH_CIRCUITS,
    )
    plan["ordering"] = "randomized_complete_blocks"
    plan["seed_source"] = seed_record("scripts/qi_teleportation_design.py", "--seed", args.experiment, args.seed_source)
    plan["catalogue_sha256"] = hashlib.sha256(catalogue_bytes).hexdigest()
    plan["admission"] = {
        "hardware_approval": "required",
        "fresh_provider_configuration": "required",
        "native_common_channel_receipt": "required",
        "input_side_information_audit": "required",
        "calibration_and_readout_controls": "required",
        "public_network_link_claim": False,
    }
    write_bundle(args.out, plan, files)


def analyze(plan_path: Path, directories: list[Path], calibration: Path, alpha: float) -> dict[str, Any]:
    require(
        type(alpha) in (int, float) and math.isfinite(alpha) and 0 < alpha < 1,
        "family alpha must be in (0,1)",
    )
    from qi_records import load_run, validate_run

    data = plan_path.read_bytes()
    plan = json.loads(data)
    validate_plan(plan)
    plan_digest = hashlib.sha256(data).hexdigest()
    epoch = hashlib.sha256(calibration.read_bytes()).hexdigest()
    expected = {b["batch"]: b for b in plan["batches"]}
    seen: set[str] = set()
    job_ids: set[tuple[str, str]] = set()
    rows: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    provenance = []
    for directory in directories:
        record = load_run(directory)
        acquisition = validate_run(record, f"six-state {directory.name}")
        cases = record["cases"]
        name = cases.get("batch")
        require(name in expected and name not in seen, "unknown or duplicate acquisition batch")
        require(cases.get("series_sha256") == plan_digest, "acquisition is not bound to this plan")
        require(cases.get("circuits") == expected[name]["circuits"], "acquisition circuit rows differ from plan")
        require(
            all(cases.get(key) == plan[key] for key in ("backend", "backend_type_id", "shots", "nqubits")),
            "acquisition configuration differs from plan",
        )
        require(acquisition.completed, "incomplete acquisition cannot be scored")
        seen.add(name)
        for spec, job in zip(cases["circuits"], acquisition.jobs, strict=True):
            identity = (acquisition.backend, str(job.job_id))
            require(identity not in job_ids, "same provider job appears twice")
            job_ids.add(identity)
            require(job.shots_done == plan["shots"], "missing shots; no silent accepted-only normalization")
            if job.histogram is None:
                raise ValueError("completed job has no histogram")
            route = plan["routes"][spec["route_index"]]
            score = score_histogram(job.histogram, plan["nqubits"], route, spec["input"])
            require(score["shots"] == plan["shots"], "histogram denominator differs from plan")
            score.update(
                route=route,
                selection="all_shots",
                calibration_id=epoch,
                channel_id=f"{plan_digest}:route-{spec['route_index']}",
                job_id=str(job.job_id),
            )
            rows[(spec["block"], spec["route_index"])].append(score)
        provenance.append({"batch": name, "digests": record["digests"]})
    require(seen == set(expected), "every scheduled batch must be present")
    groups = []
    # Bonferroni covers reporting every planned block/route together, rather
    # than presenting only the best-looking hardware location.
    family_size = len(plan["orders"]) * len(plan["routes"])
    for (block, route_index), scores in sorted(rows.items()):
        estimate = six_state_estimate(scores, alpha / family_size)
        groups.append({"block": block, "route_index": route_index, "rows": scores, "estimate": estimate})
    require(len(groups) == family_size, "incomplete crossed design")
    return {
        "schema": "qi-fixed-route-six-state-analysis-v1",
        "plan_sha256": plan_digest,
        "calibration_record_sha256": epoch,
        "family_alpha": alpha,
        "groups": groups,
        "acquisition_provenance": sorted(provenance, key=lambda p: p["batch"]),
        "instrument_admission": "not_independently_certified_by_this_analysis",
        "limits": [
            "independent-shot, fixed-stopping bounds only",
            "no drift or SPAM correction",
            "no cross-block/channel pooling",
            "no surviving-output or cross-device claim",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--catalogue", type=Path, required=True)
    prep.add_argument("--backend", required=True)
    prep.add_argument("--route", nargs=4, type=int, action="append", required=True)
    prep.add_argument("--blocks", type=int, required=True)
    prep.add_argument("--shots", type=int, required=True)
    prep.add_argument("--experiment", required=True)
    prep.add_argument("--out", type=Path, required=True)
    # Import only to declare the production seed flag. No source is queried.
    from qrng_seeds import add_seed_argument

    add_seed_argument(prep, "--seed", required=True)
    replay = commands.add_parser("analyze")
    replay.add_argument("--plan", type=Path, required=True)
    replay.add_argument("--calibration-record", type=Path, required=True)
    replay.add_argument("--alpha", type=float, default=0.05)
    replay.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args)
        else:
            print(serialized(analyze(args.plan, args.runs, args.calibration_record, args.alpha)), end="")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
