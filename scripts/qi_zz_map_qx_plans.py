"""Build compact QX preflight twins of a Tuna-17 ZZ map plan of schema v1 or v2, entirely offline.

qi_zz_map_qx.py reads plan schema `qi-zz-map-plan-v1` alone, and every retained QX twin binds its bytes as
`qx_builder_sha256`, so that builder stays byte-fixed. This module reads both Tuna plan schemas: v1 from
qi_zz_map.py and v2, the laddered-pause proposal of qi_zz_map_floor.py, whose circuits and batching equal v1's.
A v2 plan passes qi_zz_map_floor.validate_plan, and each of its batch manifests names the v2 schema. The twin
reuses qi_zz_map_qx's compaction, relabeling, sanity policy and twin plan schema, so `qi_zz_map_qx.py --analyze`
reads it unchanged; the twin records the source plan schema and this module's digest beside the builder's.
This module performs no network access and has no submit command.

Usage: "$PYTHON" scripts/qi_zz_map_qx_plans.py (--write DIR | --check DIR) --source-plan PLAN [--catalogue CATALOGUE]
       "$PYTHON" scripts/qi_zz_map_qx_plans.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qi_zz_map_floor as floor  # noqa: E402
import qi_zz_map_qx as qx  # noqa: E402
from qi_platform import HARDWARE_BATCH_CIRCUITS  # noqa: E402
from qi_zz_map import CATALOGUE, digest, json_text, require  # noqa: E402

from parallel import ordered_map  # noqa: E402

SOURCE_SCHEMAS = ("qi-zz-map-plan-v1", floor.PLAN_SCHEMA)
V2_SOURCE = qx.ROOT / "results/quantum_inspire/proposals/zz-map-tuna17-pause-ladder-floor/plan.json"
V1_SOURCE = qx.ROOT / "results/quantum_inspire/cases/zz-map-tuna17-pause-ladder/plan.json"
V1_TWIN = qx.ROOT / "results/quantum_inspire/cases/zz-map-qx-pause-ladder"
DEADLINE_CATALOGUE = qx.ROOT / "docs/evidence/quantum_inspire/catalogue-submission-deadline-proposal.json"


def read_source(source_plan: Path) -> dict:
    """The Tuna plan, with every batch manifest bound to it and a v2 plan's pause budget validated."""
    source = json.loads(source_plan.read_bytes())
    require(source.get("schema") in SOURCE_SCHEMAS, "unrecognized Tuna plan")
    require(source["status"] == "proposed_not_submitted", "source is not the unsubmitted proposal")
    require(source["cost"]["total_jobs"] == 416 and len(source["batches"]) == 139, "Tuna budget changed")
    manifests = {}
    for batch in source["batches"]:
        name = f"{batch['directory']}/cases.json"
        text = (source_plan.parent / name).read_text(encoding="utf-8")
        require(digest(text.encode("utf-8")) == batch["cases_sha256"], "Tuna batch manifest differs from its plan")
        manifests[name] = text
    if source["schema"] == floor.PLAN_SCHEMA:
        floor.validate_plan(source, manifests)
    return source


def build(source_plan: Path, *, catalogue: Path = CATALOGUE) -> dict[str, str]:
    source_plan = source_plan.resolve()
    source = read_source(source_plan)
    require(HARDWARE_BATCH_CIRCUITS == 3, "hardware batch policy changed")
    catalogue_data = json.loads(catalogue.read_bytes())
    backend = next(b for b in catalogue_data["backend_types"] if b["identifier"] == "QXsinglenodesimulator")
    require(backend["nqubits"] >= 8 and backend["max_number_of_shots"] >= qx.SHOTS, "QX capacity changed")
    require(backend["max_jobs_per_batch_job"] >= 3, "QX batch limit changed")
    require(
        {"X90", "mX90", "Y90", "mY90", "init", "wait", "barrier", "measure"} <= set(backend["gateset"]),
        "QX lacks a required native instruction",
    )
    identities = {
        "source_tuna_plan_sha256": digest(source_plan.read_bytes()),
        "catalogue_sha256": digest(catalogue.read_bytes()),
        "qx_builder_sha256": digest(Path(qx.__file__).read_bytes()),
        "qx_plan_reader_sha256": digest(Path(__file__).read_bytes()),
    }
    rendered = ordered_map(qx.transform, [(str(source_plan.parent), row) for row in source["circuits"]])
    rows = [row for row, _ in rendered]
    files = {f"{row['batch_directory']}/{row['file']}": code for row, code in rendered}
    batches = []
    for batch in source["batches"]:
        directory = batch["directory"]
        batch_rows = [
            {k: v for k, v in row.items() if k != "batch_directory"}
            for row in rows
            if row["batch_directory"] == directory
        ]
        require(0 < len(batch_rows) <= HARDWARE_BATCH_CIRCUITS, "QX batch exceeds the matched hardware cap")
        cases = {
            "schema": qx.CASE_SCHEMA,
            "status": "proposed_not_submitted",
            "backend": backend["identifier"],
            "backend_type_id": backend["id"],
            "nqubits": max(row["nqubits"] for row in batch_rows),
            "register_width_convention": "nqubits is the batch maximum; each circuit records its exact nqubits",
            "shots": qx.SHOTS,
            "source_digests": identities,
            "source_tuna_plan_schema": source["schema"],
            "circuits": batch_rows,
        }
        text = json_text(cases)
        files[f"{directory}/cases.json"] = text
        batches.append({"directory": directory, "circuits": len(batch_rows), "cases_sha256": digest(text)})
    require(
        sum(len(row["pairs"]) for row in rows if row.get("quadrature") == "y") == qx.Y_TESTS, "Y-test family changed"
    )
    files["plan.json"] = json_text(
        {
            "schema": qx.PLAN_SCHEMA,
            "status": "proposed_not_submitted",
            "backend": backend["identifier"],
            "backend_type_id": backend["id"],
            "source_tuna_plan": str(source_plan.relative_to(qx.ROOT)),
            "source_tuna_plan_schema": source["schema"],
            "source_digests": identities,
            "shots": qx.SHOTS,
            "bit_order": "qubit_0_rightmost",
            "cost": {"total_jobs": 416, "batches": 139, "shots_per_job": qx.SHOTS, "total_job_shots": 416 * qx.SHOTS},
            "sanity_policy": qx.POLICY,
            "circuits": rows,
            "batches": batches,
        }
    )
    return files


def write(directory: Path, files: dict[str, str]) -> None:
    existing = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    require(not existing - set(files), "refusing to overwrite retained acquisitions or unrelated files")
    for name, text in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def check(directory: Path, files: dict[str, str]) -> None:
    existing = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    require(existing == set(files), "QX proposal file set differs from regeneration")
    require(
        all((directory / name).read_text(encoding="utf-8") == text for name, text in files.items()),
        "QX proposal content differs",
    )


def self_test() -> None:
    v2 = build(V2_SOURCE, catalogue=DEADLINE_CATALOGUE)
    v1 = build(V1_SOURCE, catalogue=DEADLINE_CATALOGUE)
    retained = qx.build(V1_SOURCE, catalogue=DEADLINE_CATALOGUE)
    for files, schema in ((v2, floor.PLAN_SCHEMA), (v1, "qi-zz-map-plan-v1")):
        plan = json.loads(files["plan.json"])
        require(plan["source_tuna_plan_schema"] == schema, "twin lost its source plan schema")
        require(len(plan["circuits"]) == 416 and len(plan["batches"]) == 139, "twin size changed")
    circuits = {name: text for name, text in retained.items() if name.endswith(".cq")}
    for files in (v1, v2):
        require({n: t for n, t in files.items() if n.endswith(".cq")} == circuits, "twin circuits differ from v1")
    retained_rows = json.loads(retained["plan.json"])["circuits"]
    for files in (v1, v2):
        require(json.loads(files["plan.json"])["circuits"] == retained_rows, "twin roles differ from the builder's")
    try:
        qx.build(V2_SOURCE, catalogue=DEADLINE_CATALOGUE)
    except ValueError:
        pass
    else:
        raise AssertionError("the byte-fixed QX builder accepted a v2 plan")
    with tempfile.TemporaryDirectory() as scratch:
        source = json.loads(V2_SOURCE.read_bytes())
        source["cost"]["minimum_interbatch_pause_seconds"] = source["cost"]["ceiling_interbatch_pause_seconds"]
        altered = Path(scratch) / "plan.json"
        altered.write_text(json_text(source), encoding="utf-8")
        for batch in source["batches"]:
            (Path(scratch) / batch["directory"]).symlink_to(V2_SOURCE.parent / batch["directory"])
        for broken, label in (
            (source, "ceiling-valued pause minimum"),
            ({**source, "schema": "qi-zz-map-plan-v3"}, ""),
        ):
            altered.write_text(json_text(broken), encoding="utf-8")
            try:
                read_source(altered)
            except ValueError:
                pass
            else:
                raise AssertionError(f"an invalid Tuna plan was accepted: {label or broken['schema']}")
    print("QX ZZ twins: v1 and v2 Tuna plans compact to the retained circuits; v2 pause and schema guards hold")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--source-plan", type=Path, default=V2_SOURCE)
    parser.add_argument("--catalogue", type=Path, default=DEADLINE_CATALOGUE)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    files = build(args.source_plan, catalogue=args.catalogue)
    if args.check:
        check(args.check, files)
    else:
        write(args.write, files)
    print(f"QX ZZ twin: {len(files)} files, 416 compact circuits, 139 batches from {args.source_plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
