"""Design independent Ascella compilations and explicit physical-output permutations."""

from __future__ import annotations

import argparse
import copy
import importlib.metadata
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import anu_qrng
import ascella_transition_context as context
import numpy as np
import qd_platform as qd
from hypercomplex_cases import encoded

from operator_arithmetic import photonic_template, probabilities
from parallel import ordered_map

ROOT = context.ROOT
BUNDLE = Path("docs/evidence/ascella-transition-mesh-port-diagnostics")
DRAW = Path("docs/evidence/anu_qrng/draw-2026-10-28T003533Z.json")
PRIOR_MAPPING = Path("docs/evidence/quantum-experiment-conformance/cases/seeds.json")
ENDPOINTS = 1876

PORT_MAPS = {
    "original": list(range(12)),
    "logical-swap": [3, 1, 5, 0, 4, 2, 6, 7, 8, 9, 10, 11],
    "outer-swap": [0, 1, 8, 3, 4, 9, 6, 7, 2, 5, 10, 11],
}


def permute_operator(matrix: Any, permutation: list[int]) -> Any:
    """Move each original output row to its specified physical port."""
    array = np.asarray(matrix, dtype=np.complex128)
    if array.shape != (12, 12) or sorted(permutation) != list(range(12)):
        raise ValueError("the physical output mapping must permute twelve rows")
    result = np.zeros_like(array)
    result[permutation, :] = array
    return result


def assignments(values: list[int], blocked: set[int]) -> list[dict[str, Any]]:
    """Use draw positions once, balancing eight compilations across each setting and port map."""
    available: list[tuple[int, int]] = []
    used = set(blocked)
    for index, value in enumerate(values):
        if type(value) is not int or value < 0 or value in used:
            continue
        used.add(value)
        available.append((index, value))
    if len(available) < 120:
        raise ValueError("the draw lacks 120 distinct unused compilation identifiers")
    cases = [(label, port_map) for port_map in PORT_MAPS for label, _ in context.SELECTION]
    design = []
    position = 0
    for replicate in range(8):
        shifted = cases[replicate:] + cases[:replicate]
        for label, port_map in shifted:
            index, value = available[position]
            design.append(
                {
                    "label": label,
                    "port_map": port_map,
                    "replicate": replicate,
                    "draw_index": index,
                    "value": value,
                }
            )
            position += 1
    return design


def _variant(arguments: tuple[str, dict[str, Any], str, list[int]]) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    label, source, map_name, permutation = arguments
    operator = source["operator"]
    matrix = np.asarray(operator["real"], dtype=float) + 1j * np.asarray(operator["imaginary"], dtype=float)
    mapped = permute_operator(matrix, permutation)
    circuit, parameters = photonic_template(mapped)
    active = [permutation[index] for index in source["active_outputs"]]
    labels = [""] * 12
    for original, physical in enumerate(permutation):
        labels[physical] = source["logical_output_labels"][original]
    variant = copy.deepcopy(source)
    variant.update(
        diagnostic_label=label,
        port_map=map_name,
        physical_port_permutation=permutation,
        circuit_params=parameters,
        operator=encoded(mapped),
        column=[[float(value.real), float(value.imag)] for value in mapped[:, 0]],
        requested_probabilities=probabilities(mapped),
        native_probabilities=probabilities(mapped),
        active_outputs=active,
        leakage_outputs=[index for index in range(12) if index not in active],
        logical_output_labels=labels,
        prediction_scope="requested permuted operator; compare against the returned compiled mesh",
    )
    return label, map_name, variant, circuit


@cache
def build_files() -> dict[str, str]:
    """Freeze 120 new compilation identifiers and twelve matched-mesh anchors in six jobs."""
    source_bytes = (ROOT / context.SOURCE).read_bytes()
    source = json.loads(source_bytes)
    rows = {row["name"]: row for row in source["settings"]}
    draw_bytes = (ROOT / DRAW).read_bytes()
    draw = json.loads(draw_bytes)
    anu_qrng.admit(draw)
    old = json.loads((ROOT / PRIOR_MAPPING).read_bytes())
    blocked = {row["value"] for row in old["allocations"]} | {0}
    design = assignments(draw["values"], blocked)
    allocation = {
        "schema": "ascella-mesh-port-seed-allocation-v1",
        "source": DRAW.as_posix(),
        "source_sha256": context._sha(draw_bytes),
        "allocations": design,
        "boundary": "Each draw index is consumed once; unused indices remain unallocated.",
    }
    allocation_text = context._json_bytes(allocation).decode()
    allocation_binding = {
        "file": (BUNDLE / "seed-allocation.json").as_posix(),
        "sha256": context._sha(allocation_text.encode()),
    }
    variants = ordered_map(
        _variant,
        [
            (label, rows[name], map_name, permutation)
            for label, name in context.SELECTION
            for map_name, permutation in PORT_MAPS.items()
        ],
        min_items=1,
    )
    circuit = variants[0][3]
    if any(variant[3] != circuit for variant in variants):
        raise ValueError("all permuted operators must share a single parameterized circuit")
    circuit_text = json.dumps(circuit, indent=1) + "\n"
    candidates = {(label, name): row for label, name, row, _ in variants}
    anchors = {label: rows[name] for label, name in context.SELECTION if label in {"identity-2", "identity-0"}}
    if set(anchors) != {"identity-2", "identity-0"}:
        raise ValueError("the frozen matched-mesh anchors are incomplete")
    campaign: dict[str, Any] = {
        "schema": "ascella-transition-mesh-port-campaign-v1",
        "source_manifest": {"file": context.SOURCE.as_posix(), "sha256": context._sha(source_bytes)},
        "seed_allocation": allocation_binding,
        "source_draw": {"file": DRAW.as_posix(), "sha256": context._sha(draw_bytes)},
        "seed_exclusion_source": {
            "file": PRIOR_MAPPING.as_posix(),
            "sha256": context._sha((ROOT / PRIOR_MAPPING).read_bytes()),
        },
        "baseline_analysis": {
            "file": "results/quandela/ascella-transition-context-parallel-analysis.json",
            "sha256": context._sha(
                (ROOT / "results/quandela/ascella-transition-context-parallel-analysis.json").read_bytes()
            ),
        },
        "written_case": {
            "file": (BUNDLE / "README.md").as_posix(),
            "sha256": context._sha((ROOT / BUNDLE / "README.md").read_bytes()),
        },
        "producer_sha256": context._sha(Path(__file__).read_bytes()),
        "dependencies": [
            {"file": name, "sha256": context._sha((ROOT / name).read_bytes())}
            for name in (
                "scripts/ascella_transition_context.py",
                "scripts/qd_platform.py",
                "scripts/anu_qrng.py",
                "scripts/hypercomplex_cases.py",
                "gororoba_quantum/operator_arithmetic.py",
                "gororoba_quantum/parallel.py",
            )
        ],
        "port_maps": PORT_MAPS,
        "replicates_per_condition": 8,
        "samples_per_setting": context.SAMPLES,
        "detected_shot_cap_per_setting": context.SHOTS,
        "confidence": 0.95,
        "endpoints": ENDPOINTS,
        "family": "132 new observations and two retained singleton anchors; 14 endpoints each",
        "execution_stop_seconds": 300,
        "credit_ceiling_per_job": context.CREDIT_CEILING,
        "total_credit_ceiling": round(6 * context.CREDIT_CEILING, 6),
        "jobs": [],
    }
    files = {"seed-allocation.json": allocation_text}
    for job_index in range(6):
        selected = design[job_index * 20 : (job_index + 1) * 20]
        result_rows = []
        for anchor in ("identity-2", "identity-0"):
            row = copy.deepcopy(anchors[anchor])
            row.update(
                name=f"anchor-{anchor}",
                diagnostic_label=anchor,
                port_map="original",
                physical_port_permutation=PORT_MAPS["original"],
                compilation_kind="matched-mesh-anchor",
            )
            result_rows.append(row)
        for entry in selected:
            row = copy.deepcopy(candidates[(entry["label"], entry["port_map"])])
            row.update(
                name=f"{entry['label']}-{entry['port_map']}-mesh-{entry['replicate']}",
                compilation_seed=entry["value"],
                compilation_kind="independent-mesh",
                replicate=entry["replicate"],
                compilation_seed_allocation={
                    "path": allocation_binding["file"],
                    "sha256": allocation_binding["sha256"],
                    "source": DRAW.as_posix(),
                    "draw_index": entry["draw_index"],
                    "kind": "one fresh ANU draw position per independent compilation",
                },
            )
            result_rows.append(row)
        for iteration, row in enumerate(result_rows):
            row.update(cohort_id="ascella-transition-mesh-port-diagnostics", iteration_index=iteration)
        manifest = copy.deepcopy(source)
        manifest.pop("qualification_profile", None)
        name = f"mesh-port-{job_index + 1}"
        manifest.update(
            job=f"transition-{name}",
            family="mub-six",
            cohort_id="ascella-transition-mesh-port-diagnostics",
            settings=result_rows,
            iterations=len(result_rows),
            iterator=False,
            max_samples=len(result_rows) * context.SAMPLES,
            max_shots=len(result_rows) * context.SHOTS,
            max_duration=300,
            max_credits=context.CREDIT_CEILING,
            acquisition_admission="awaiting-intervention-guard",
            circuit={"file": "circuit.json", "sha256": context._sha(circuit_text.encode())},
            seed_allocation=allocation_binding,
            preregistered={"family": campaign["family"], "endpoints": ENDPOINTS, "confidence": 0.95},
        )
        filename = f"cases/{name}/cases.json"
        files[filename] = context._json_bytes(manifest).decode()
        files[f"cases/{name}/circuit.json"] = circuit_text
        campaign["jobs"].append(
            {
                "name": name,
                "manifest": filename,
                "manifest_sha256": context._sha(files[filename].encode()),
                "directory": f"results/quandela/runs/ascella-transition-{name}",
            }
        )
    files["campaign.json"] = context._json_bytes(campaign).decode()
    return files


def write_files(bundle: Path) -> None:
    for name, content in build_files().items():
        path = bundle / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise ValueError(f"the intervention case differs: {path}")
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def check_files(bundle: Path) -> None:
    campaign = json.loads((bundle / "campaign.json").read_bytes())
    for key in ("source_manifest", "source_draw", "seed_exclusion_source", "baseline_analysis", "written_case"):
        reference = campaign[key]
        if context._sha((ROOT / reference["file"]).read_bytes()) != reference["sha256"]:
            raise ValueError(f"the intervention source differs: {reference['file']}")
    if context._sha(Path(__file__).read_bytes()) != campaign["producer_sha256"]:
        raise ValueError("the intervention producer differs")
    for reference in campaign["dependencies"]:
        if context._sha((ROOT / reference["file"]).read_bytes()) != reference["sha256"]:
            raise ValueError(f"the intervention dependency differs: {reference['file']}")
    for name, content in build_files().items():
        path = bundle / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError(f"the intervention case differs: {path}")


def baseline(bundle: Path) -> dict[str, Any]:
    """Verify the completed first study and every source bound by its analysis."""
    check_files(bundle)
    campaign = context._read(bundle / "campaign.json")
    report = context._read(ROOT / campaign["baseline_analysis"]["file"])
    if not report.get("complete") or len(report.get("jobs", [])) != 7:
        raise ValueError("the seven-job context diagnostic is incomplete")
    if report.get("analysis_source_sha256") != context._sha(Path(context.__file__).read_bytes()):
        raise ValueError("the context analysis producer differs")
    for job in [report["prior"], *report["jobs"]]:
        for source in job["sources"]:
            if context._sha((ROOT / source["file"]).read_bytes()) != source["sha256"]:
                raise ValueError(f"the context baseline source differs: {source['file']}")
    return report


def _preflight_job(arguments: tuple[Path, dict[str, Any]]) -> dict[str, Any]:
    bundle, job = arguments
    path = bundle / f"{job['name']}-preflight.json"
    if path.exists():
        record = context._read(path)
        if record.get("cases_sha256") != job["manifest_sha256"]:
            raise ValueError(f"{job['name']}: the preflight names another case")
    else:
        record = qd.plan(bundle / Path(job["manifest"]).parent, "qpu:ascella", context.CREDIT_CEILING, 300, 1)
        record["preflight_observed_utc"] = qd.now()
        qd.write_json(path, record, exclusive=True)
    return {
        "job": job["name"],
        "case_sha256": record["cases_sha256"],
        "body_sha256": record["body_sha256"],
        "credit_ceiling": record["credit_ceiling"],
        "status_at_plan": record["status_at_plan"],
    }


def preflight(bundle: Path) -> dict[str, Any]:
    import perceval  # noqa: F401

    previous = baseline(bundle)
    campaign = context._read(bundle / "campaign.json")
    jobs = ordered_map(_preflight_job, [(bundle, job) for job in campaign["jobs"]], min_items=1)
    return {
        "schema": "ascella-transition-mesh-port-preflight-v1",
        "baseline_complete": previous["complete"],
        "jobs": jobs,
    }


def _check_run(bundle: Path, job: dict[str, Any], directory: Path) -> None:
    actual, _, _ = qd.load_case(directory)
    frozen = context._read(bundle / job["manifest"])
    written = bundle / "README.md"
    binding = {"file": written.relative_to(ROOT).as_posix(), "sha256": context._sha(written.read_bytes())}
    context.validate_run_manifest(actual, frozen, job, binding)


def submit_next(bundle: Path, approval: str) -> dict[str, Any]:
    """Run one preflight-bound intervention only after its predecessors are complete."""
    if not approval.strip():
        raise ValueError("the user's acquisition instruction is required")
    previous = baseline(bundle)
    campaign = context._read(bundle / "campaign.json")
    prior_job_durations = [job["duration_seconds"] for job in previous["jobs"][:5]]
    if 22 * max(prior_job_durations) + 60 > 300:
        raise ValueError("the initial 22-setting duration model exceeds the provider limit")
    durations = []
    for job in campaign["jobs"]:
        directory = ROOT / job["directory"]
        if (directory / "submission.json").exists():
            if not (directory / "results.json").exists():
                raise ValueError(f"collect the existing intervention job: {directory}")
            _check_run(bundle, job, directory)
            metadata, _ = context.read_run(directory)
            durations.append(metadata["duration_seconds"])
            if durations[-1] > 240:
                raise ValueError("a completed intervention exceeded the 60-second reserve")
            continue
        if any((directory / name).exists() for name in ("submission-state.json", "job-body.json")):
            raise ValueError(f"reconcile the existing submission checkpoint: {directory}")
        source = bundle / job["manifest"]
        manifest = context._read(source)
        written = bundle / "README.md"
        binding = {"file": written.relative_to(ROOT).as_posix(), "sha256": context._sha(written.read_bytes())}
        manifest.update(acquisition_admission="ready", reviewed_case=binding, source_case_sha256=job["manifest_sha256"])
        directory.mkdir(parents=True, exist_ok=True)
        for name, data in (
            ("cases.json", context._json_bytes(manifest)),
            ("circuit.json", (source.parent / "circuit.json").read_bytes()),
        ):
            path = directory / name
            if path.exists() and path.read_bytes() != data:
                raise ValueError(f"the prepared intervention case differs: {path}")
            if not path.exists():
                path.write_bytes(data)
        preflight_record = context._read(bundle / f"{job['name']}-preflight.json")
        case_hash = context._sha((directory / "cases.json").read_bytes())
        baseline_hash = campaign["baseline_analysis"]["sha256"]
        baseline_path = ROOT / campaign["baseline_analysis"]["file"]

        def verify(
            planned: dict[str, Any],
            *,
            expected_preflight: dict[str, Any] = preflight_record,
            expected_case_hash: str = case_hash,
            expected_binding: dict[str, str] = binding,
            expected_baseline_hash: str = baseline_hash,
            expected_baseline_path: Path = baseline_path,
            expected_written: Path = written,
        ) -> None:
            if (
                planned["cases_sha256"] != expected_case_hash
                or context.body_projection(planned["body"]) != context.body_projection(expected_preflight["body"])
                or planned["credit_ceiling"] > context.CREDIT_CEILING
                or planned["admitted_statuses"] != ["available"]
                or context._sha(expected_written.read_bytes()) != expected_binding["sha256"]
                or context._sha(expected_baseline_path.read_bytes()) != expected_baseline_hash
            ):
                raise qd.PlatformError("the current intervention payload or reviewed case differs")

        return qd.submit(directory, "qpu:ascella", approval, context.CREDIT_CEILING, 300, 1, verify=verify)
    raise ValueError("all six intervention jobs already have results")


def average_interval(intervals: list[list[float]]) -> list[float]:
    """Bound the mean by averaging simultaneously valid per-mesh limits."""
    if not intervals or any(len(pair) != 2 or not 0 <= pair[0] <= pair[1] <= 1 for pair in intervals):
        raise ValueError("the group needs finite probability intervals")
    return [
        math.fsum(pair[0] for pair in intervals) / len(intervals),
        math.fsum(pair[1] for pair in intervals) / len(intervals),
    ]


def _measure(setting: dict[str, Any], decoded: dict[str, Any]) -> dict[str, Any]:
    result = dict(decoded)
    result.update(
        label=setting["diagnostic_label"],
        port_map=setting["port_map"],
        physical_port_permutation=setting["physical_port_permutation"],
        compilation_kind=setting["compilation_kind"],
        requested_probabilities=setting["requested_probabilities"],
    )
    if setting["compilation_kind"] == "independent-mesh":
        result["replicate"] = setting["replicate"]
        result["draw_index"] = setting["compilation_seed_allocation"]["draw_index"]
    if setting["diagnostic_label"].startswith("identity-"):
        result["target_port"] = max(range(12), key=lambda index: setting["requested_probabilities"][index])
    return result


def analyze(bundle: Path) -> dict[str, Any]:
    """Describe all output categories and group only distinct returned meshes."""
    prior = baseline(bundle)
    campaign = context._read(bundle / "campaign.json")
    baseline_rows = [
        {**prior["observations"][label]["singleton"], "label": label, "compilation_kind": "baseline"}
        for label in ("identity-2", "identity-0")
    ]
    known_meshes = {tuple(prior["observations"][label]["singleton"]["mesh"]) for label, _ in context.SELECTION}
    jobs = []
    measurements: list[dict[str, Any]] = []
    for job in campaign["jobs"]:
        directory = ROOT / job["directory"]
        if not (directory / "results.json").is_file():
            jobs.append({"name": job["name"], "status": "missing"})
            continue
        try:
            _check_run(bundle, job, directory)
            metadata, entries = context.read_run(directory)
            manifest, _, _ = qd.load_case(directory)
            rows = []
            for setting, decoded in zip(manifest["settings"], entries, strict=True):
                rows.append(_measure(setting, decoded))
            if len(rows) != len(entries):
                raise ValueError("the intervention result inventory differs")
            measurements.extend({**row, "job": job["name"]} for row in rows)
            jobs.append({"name": job["name"], "status": "completed", **metadata})
        except (ValueError, qd.PlatformError, OSError, KeyError) as error:
            jobs.append({"name": job["name"], "status": "refused", "reason": str(error)})
    all_rows = baseline_rows + measurements
    arguments = [
        (number, sum(row["counts"]), ENDPOINTS) for row in all_rows for number in [*row["counts"], row["leakage"]]
    ]
    intervals = ordered_map(context._interval, arguments)
    for index, row in enumerate(all_rows):
        row["category_intervals"] = intervals[14 * index : 14 * index + 13]
        row["leakage_interval"] = intervals[14 * index + 13]
        if "target_port" in row:
            row["correct_output_interval"] = row["category_intervals"][row["target_port"]]
        predicted = row.get("returned_probabilities")
        if predicted is not None:
            categories = predicted + [0.0]
            total = sum(row["counts"])
            row["observed_to_returned_tv"] = (
                math.fsum(
                    abs(number / total - target) for number, target in zip(row["counts"], categories, strict=True)
                )
                / 2
            )
            row["observed_to_returned_tv_bounds"] = [
                min(
                    1.0,
                    math.fsum(
                        max(0.0, interval[0] - target, target - interval[1])
                        for interval, target in zip(row["category_intervals"], categories, strict=True)
                    )
                    / 2,
                ),
                min(
                    1.0,
                    math.fsum(
                        max(abs(interval[0] - target), abs(interval[1] - target))
                        for interval, target in zip(row["category_intervals"], categories, strict=True)
                    )
                    / 2,
                ),
            ]
    groups = []
    for label, _ in context.SELECTION:
        for port_map in PORT_MAPS:
            selected = [
                row
                for row in measurements
                if row["compilation_kind"] == "independent-mesh"
                and row["label"] == label
                and row["port_map"] == port_map
            ]
            unique = []
            seen: set[tuple[str, ...]] = set()
            prior_collisions = 0
            for row in selected:
                mesh = tuple(row["mesh"])
                if mesh in known_meshes:
                    prior_collisions += 1
                elif mesh not in seen:
                    unique.append(row)
                    seen.add(mesh)
            group: dict[str, Any] = {
                "label": label,
                "port_map": port_map,
                "acquired": len(selected),
                "unique_new_meshes": len(unique),
                "prior_mesh_collisions": prior_collisions,
                "within_group_collisions": len(selected) - len(unique) - prior_collisions,
                "status": "complete" if len(selected) == 8 and len(unique) == 8 else "incomplete-or-colliding",
            }
            if unique:
                group["mean_leakage"] = math.fsum(row["leakage"] / sum(row["counts"]) for row in unique) / len(unique)
                group["mean_leakage_interval"] = average_interval([row["leakage_interval"] for row in unique])
                group["mean_returned_tv"] = math.fsum(row["observed_to_returned_tv"] for row in unique) / len(unique)
                group["mean_returned_tv_bounds"] = average_interval(
                    [row["observed_to_returned_tv_bounds"] for row in unique]
                )
                if label.startswith("identity-"):
                    group["mean_correct"] = math.fsum(
                        row["counts"][row["target_port"]] / sum(row["counts"]) for row in unique
                    ) / len(unique)
                    group["mean_correct_interval"] = average_interval(
                        [row["correct_output_interval"] for row in unique]
                    )
            groups.append(group)
    anchors = []
    for row in measurements:
        if row["compilation_kind"] == "matched-mesh-anchor":
            prior_row = next(item for item in baseline_rows if item["label"] == row["label"])
            anchors.append(
                {"job": row["job"], "label": row["label"], **context.compare(prior_row, row, endpoints=ENDPOINTS)}
            )
    return {
        "schema": "ascella-transition-mesh-port-analysis-v1",
        "campaign_sha256": context._sha((bundle / "campaign.json").read_bytes()),
        "analysis_source_sha256": context._sha(Path(__file__).read_bytes()),
        "analysis_environment": {
            "python": sys.version.split()[0],
            **{name: importlib.metadata.version(name) for name in ("numpy", "scipy", "perceval-quandela")},
        },
        "confidence": 0.95,
        "endpoints": ENDPOINTS,
        "confidence_boundary": (
            "Simultaneous bounds assume IID events within each observation; group intervals average per-mesh limits."
        ),
        "causal_boundary": (
            "Port maps change compiled operators; time, mesh and detector response remain potentially confounded."
        ),
        "order_boundary": "Packed result position does not establish physical iteration chronology.",
        "baseline": baseline_rows,
        "jobs": jobs,
        "observations": measurements,
        "groups": groups,
        "anchors": anchors,
        "complete": len(jobs) == 6 and all(job["status"] == "completed" for job in jobs),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--bundle", type=Path, default=ROOT / BUNDLE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--analyze", type=Path)
    parser.add_argument("--submit-next", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approval")
    args = parser.parse_args()
    try:
        if args.execute:
            if not args.approval or not args.approval.strip():
                raise ValueError("the user's acquisition instruction is required")
            campaign = context._read(args.bundle / "campaign.json")
            for job in campaign["jobs"]:
                directory = ROOT / job["directory"]
                if (directory / "results.json").exists():
                    continue
                record = submit_next(args.bundle, args.approval)
                if record["case"] != directory.name:
                    raise ValueError("the submitted job differs from the frozen acquisition sequence")
                print(f"submitted {record['case']}: {record['job_id']}", flush=True)
                result = qd.collect(directory, 5, 600)
                print(
                    f"collected {record['case']}: {result['status']['status']}, "
                    f"{result.get('samples')} accepted events, {result['status'].get('duration')} seconds",
                    flush=True,
                )
                if result["status"]["status"] != "completed":
                    raise ValueError("the intervention stopped after a non-completed job")
        elif args.submit_next:
            record = submit_next(args.bundle, args.approval or "")
            print(f"submitted {record['case']}: {record['job_id']}")
        elif args.analyze:
            qd.write_json(args.analyze, analyze(args.bundle), exclusive=True)
            print(f"wrote {args.analyze}")
        elif args.preflight:
            print(context._json_bytes(preflight(args.bundle)).decode(), end="")
        elif args.check:
            check_files(args.bundle)
            print("six frozen mesh and port intervention cases match their sources")
        else:
            write_files(args.bundle)
            print("wrote six mesh and port intervention cases")
    except (ValueError, qd.PlatformError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
