"""Freeze and analyze Ascella singleton and packed transition diagnostics.

The case reproduces five previously acquired parameter/seed combinations.
The provider's returned circuit and input identify the realized mesh; a seed
alone does not establish physical implementation equality.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import qd_platform as qd
from ascella_experiment_analysis import attribute_iteration, validate_sent_body
from ascella_experiment_run import body_projection
from experiment_analysis import binomial_interval, decode_photonic_counts, remote_compiled_prediction

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

SOURCE = Path(
    "docs/evidence/ascella-cancellation-transition-acquisition/cases/dimension-six-transition-pilot/cases.json"
)
BUNDLE = Path("docs/evidence/ascella-transition-context-diagnostics")
PRIOR_RUN = Path("results/quandela/runs/ascella-dimension-six-transition-pilot")
SAMPLES = 65_536
SHOTS = 131_072
CREDIT_CEILING = 1.131072
ENDPOINTS = 280
PROFILE = {"samples_per_setting": SAMPLES, "detected_shot_cap_per_setting": SHOTS}
SELECTION = (
    ("identity-2", "computational-to-computational-input-2"),
    ("identity-5", "computational-to-computational-input-5"),
    ("cross-4", "product_fourier-to-product_chirped-input-4"),
    ("identity-0", "computational-to-computational-input-0"),
    ("cross-0", "product_fourier-to-product_chirped-input-0"),
)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_files() -> dict[str, str]:
    """Copy source-bound settings into five singleton and two five-entry iterators."""
    original_bytes = (ROOT / SOURCE).read_bytes()
    original = json.loads(original_bytes)
    rows = {row["name"]: row for row in original["settings"]}
    if len(rows) != 12 or len(SELECTION) != 5:
        raise ValueError("the retained pilot does not carry the expected distinct settings")
    circuit_path = ROOT / SOURCE.parent / original["circuit"]["file"]
    circuit = circuit_path.read_bytes()
    if _sha(circuit) != original["circuit"]["sha256"]:
        raise ValueError("the retained circuit digest differs")
    groups = [(f"single-{short}", [(short, name)], "singleton") for short, name in SELECTION]
    groups += [("packed-forward", list(SELECTION), "forward"), ("packed-reverse", list(reversed(SELECTION)), "reverse")]
    campaign: dict[str, Any] = {
        "schema": "ascella-transition-context-campaign-v1",
        "source_manifest": {"file": SOURCE.as_posix(), "sha256": _sha(original_bytes)},
        "prior_run": PRIOR_RUN.as_posix(),
        "selection": [{"label": short, "name": name} for short, name in SELECTION],
        "samples_per_setting": SAMPLES,
        "detected_shot_cap_per_setting": SHOTS,
        "endpoints": ENDPOINTS,
        "confidence": 0.95,
        "family": "20 observations including five prior settings; 13 categories and one leakage aggregate each",
        "credit_ceiling_per_job": CREDIT_CEILING,
        "total_credit_ceiling": 7 * CREDIT_CEILING,
        "execution_stop_seconds": 300,
        "jobs": [],
    }
    files: dict[str, str] = {}
    for name, selected, context in groups:
        settings = []
        for index, (short, original_name) in enumerate(selected):
            row = copy.deepcopy(rows[original_name])
            row.update(
                cohort_id="ascella-transition-context-diagnostics",
                context=context,
                diagnostic_label=short,
                iteration_index=index,
            )
            settings.append(row)
        manifest = copy.deepcopy(original)
        manifest.pop("qualification_profile", None)
        manifest.update(
            job=f"context-{name}",
            family="mub-six",
            cohort_id="ascella-transition-context-diagnostics",
            settings=settings,
            iterations=len(settings),
            iterator=len(settings) == 1,
            max_samples=len(settings) * SAMPLES,
            max_shots=len(settings) * SHOTS,
            max_duration=300,
            max_credits=CREDIT_CEILING,
            acquisition_admission="awaiting-context-guard",
            diagnostic_source=campaign["source_manifest"],
            diagnostic_context=context,
            preregistered={
                "primary": "all twelve output categories, invalid photon-number events and leakage",
                "comparison": "matched returned-mesh singleton, packed-order and prior-pilot output distributions",
                "family": campaign["family"],
                "endpoints": ENDPOINTS,
            },
        )
        filename = f"cases/{name}/cases.json"
        files[filename] = _json_bytes(manifest).decode()
        files[f"cases/{name}/circuit.json"] = circuit.decode()
        campaign["jobs"].append(
            {
                "name": name,
                "context": context,
                "manifest": filename,
                "manifest_sha256": _sha(files[filename].encode()),
                "directory": f"results/quandela/runs/ascella-context-{name}",
                "labels": [short for short, _ in selected],
            }
        )
    files["campaign.json"] = _json_bytes(campaign).decode()
    return files


def write_files(bundle: Path) -> None:
    for name, content in build_files().items():
        path = bundle / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise ValueError(f"frozen request differs: {path}")
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def check_files(bundle: Path) -> None:
    for name, content in build_files().items():
        path = bundle / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError(f"frozen request differs: {path}")


def check_echo(setting: dict[str, Any], entry: dict[str, Any]) -> None:
    attribute_iteration(setting, entry, PROFILE)


def _preflight_job(arguments: tuple[Path, dict[str, Any]]) -> dict[str, Any]:
    bundle, job = arguments
    path = bundle / f"{job['name']}-preflight.json"
    if path.exists():
        record = _read(path)
        if record.get("cases_sha256") != job["manifest_sha256"]:
            raise ValueError(f"{job['name']}: retained preflight names a different case")
    else:
        record = qd.plan(bundle / Path(job["manifest"]).parent, "qpu:ascella", CREDIT_CEILING, 300, 1)
        record["preflight_observed_utc"] = qd.now()
        qd.write_json(path, record, exclusive=True)
    return {
        "job": job["name"],
        "cases_sha256": record["cases_sha256"],
        "body_sha256": record["body_sha256"],
        "credit_ceiling": record["credit_ceiling"],
        "status_at_plan": record["status_at_plan"],
    }


def preflight(bundle: Path) -> dict[str, Any]:
    """Validate the prior run and all seven complete SDK payloads without creating a job."""
    import perceval  # noqa: F401

    check_files(bundle)
    campaign = _read(bundle / "campaign.json")
    prior_metadata, prior_entries = read_run(ROOT / PRIOR_RUN)
    if not set(name for _, name in SELECTION) <= {row["name"] for row in prior_entries}:
        raise ValueError("the prior pilot lacks a selected setting")
    results = ordered_map(_preflight_job, [(bundle, job) for job in campaign["jobs"]], min_items=1)
    return {"schema": "ascella-transition-context-preflight-v1", "prior": prior_metadata, "jobs": results}


def _interval(arguments: tuple[int, int, int]) -> list[float]:
    return binomial_interval(*arguments)


def compare(first: dict[str, Any], second: dict[str, Any], *, endpoints: int) -> dict[str, Any]:
    """Give simultaneous total-variation bounds, retaining invalid events in both denominators."""
    counts = [first["counts"], second["counts"]]
    if any(len(row) != 13 or any(type(number) is not int or number < 0 for number in row) for row in counts):
        raise ValueError("a comparison needs twelve counts and one invalid category")
    totals = [sum(row) for row in counts]
    if any(total == 0 for total in totals):
        raise ValueError("a comparison needs positive returned event counts")
    arguments = [(number, total, endpoints) for row, total in zip(counts, totals, strict=True) for number in row]
    intervals = ordered_map(_interval, arguments)
    left, right = intervals[:13], intervals[13:]
    leakage = [first["leakage"], second["leakage"]]
    if any(
        type(count) is not int or count < row[-1] or count > total
        for count, row, total in zip(leakage, counts, totals, strict=True)
    ):
        raise ValueError("leakage must include every invalid event and fit its denominator")
    leakage_intervals = ordered_map(
        _interval, [(count, total, endpoints) for count, total in zip(leakage, totals, strict=True)]
    )
    lower = min(1.0, math.fsum(max(0.0, a[0] - b[1], b[0] - a[1]) for a, b in zip(left, right, strict=True)) / 2)
    upper = min(1.0, math.fsum(max(abs(a[0] - b[1]), abs(a[1] - b[0])) for a, b in zip(left, right, strict=True)) / 2)
    observed = math.fsum(abs(a / totals[0] - b / totals[1]) for a, b in zip(*counts, strict=True)) / 2
    matched = bool(first.get("mesh") and first.get("mesh") == second.get("mesh"))
    return {
        "first_events": totals[0],
        "second_events": totals[1],
        "observed_total_variation": observed,
        "simultaneous_total_variation_bounds": [lower, upper],
        "leakage_difference_second_minus_first": [
            leakage_intervals[1][0] - leakage_intervals[0][1],
            leakage_intervals[1][1] - leakage_intervals[0][0],
        ],
        "matched_mesh": matched,
        "matched_mesh_interpretation": "descriptive" if matched else "inconclusive",
    }


def _read(path: Path) -> Any:
    return json.loads(path.read_bytes())


def validate_run_manifest(
    actual: dict[str, Any], frozen: dict[str, Any], job: dict[str, Any], binding: dict[str, str]
) -> None:
    expected = {
        **frozen,
        "acquisition_admission": "ready",
        "source_case_sha256": job["manifest_sha256"],
        "reviewed_case": binding,
    }
    if actual != expected:
        raise ValueError(f"{job['name']}: submitted manifest differs from its frozen source")


def check_run_manifest(bundle: Path, job: dict[str, Any], directory: Path) -> None:
    actual, _, _ = qd.load_case(directory)
    frozen = _read(bundle / job["manifest"])
    written = bundle / "README.md"
    binding = {"file": written.relative_to(ROOT).as_posix(), "sha256": _sha(written.read_bytes())}
    validate_run_manifest(actual, frozen, job, binding)


def _entry(setting: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    check_echo(setting, entry)
    counts, invalid = decode_photonic_counts(entry["counts"], 12)
    categories = counts + [sum(invalid.values())]
    if sum(categories) != SAMPLES:
        raise ValueError(f"{setting['name']}: the accepted event target was not met")
    fields = entry.get("result_fields", {})
    detected = fields.get("nb_shots_used")
    if type(detected) is not int or not SAMPLES <= detected <= SHOTS:
        raise ValueError(f"{setting['name']}: detected-shot count is outside the case")
    remote = remote_compiled_prediction(fields, 12)
    if remote.get("status") != "reconstructed":
        raise ValueError(f"{setting['name']}: the returned mesh and input are unavailable")
    return {
        "name": setting["name"],
        "counts": categories,
        "leakage": categories[-1] + sum(counts[index] for index in setting["leakage_outputs"]),
        "mesh": [remote["computed_circuit_sha256"], remote["computed_input_sha256"]],
        "returned_probabilities": remote["probabilities"],
        "detected_shots": detected,
        "boundary": "The counts condition on returned accepted events; incident pulses are unknown.",
    }


def read_run(directory: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Bind the provider receipt and every returned iterator entry to the submitted operator."""
    qd.run_facts(directory)
    manifest, _, _ = qd.load_case(directory)
    body = _read(directory / "job-body.json")
    validate_sent_body(body, manifest, PROFILE)
    result = _read(directory / "results.json")
    duration = result.get("status", {}).get("duration")
    if (
        result.get("status", {}).get("status") != "completed"
        or isinstance(duration, bool)
        or not isinstance(duration, int | float)
        or not math.isfinite(duration)
        or not 0 <= duration <= 300
    ):
        raise ValueError(f"{directory.name}: completed status and finite duration are required")
    entries = result.get("iterations")
    if not isinstance(entries, list) or len(entries) != len(manifest["settings"]):
        raise ValueError(f"{directory.name}: iteration inventory differs")
    observed = [_entry(setting, entry) for setting, entry in zip(manifest["settings"], entries, strict=True)]
    sources = [
        {
            "file": (directory / name).relative_to(ROOT).as_posix(),
            "sha256": _sha((directory / name).read_bytes()),
        }
        for name in ("cases.json", "submission.json", "job-body.json", "results.json", "raw/result.json")
    ]
    return {
        "duration_seconds": duration,
        "start_time": result["status"].get("start_time"),
        "sources": sources,
    }, observed


def analyze(bundle: Path) -> dict[str, Any]:
    """Compare singleton, packed orders and prior pilot without inferring unrecorded chronology."""
    check_files(bundle)
    campaign = _read(bundle / "campaign.json")
    prior_metadata, prior_entries = read_run(ROOT / PRIOR_RUN)
    prior = {row["name"]: row for row in prior_entries}
    collected: dict[str, dict[str, dict[str, Any]]] = {}
    jobs = []
    for job in campaign["jobs"]:
        directory = ROOT / job["directory"]
        if not (directory / "results.json").is_file():
            jobs.append({"name": job["name"], "status": "missing"})
            continue
        check_run_manifest(bundle, job, directory)
        metadata, entries = read_run(directory)
        jobs.append({"name": job["name"], "status": "completed", **metadata})
        for label, entry in zip(job["labels"], entries, strict=True):
            collected.setdefault(label, {})[job["context"]] = entry
    comparisons = []
    for short, name in SELECTION:
        available = {"prior": prior[name], **collected.get(short, {})}
        pairs = (("prior", "singleton"), ("singleton", "forward"), ("singleton", "reverse"), ("forward", "reverse"))
        for first, second in pairs:
            if first in available and second in available:
                comparisons.append(
                    {
                        "setting": short,
                        "first": first,
                        "second": second,
                        **compare(available[first], available[second], endpoints=ENDPOINTS),
                    }
                )
    return {
        "schema": "ascella-transition-context-analysis-v1",
        "campaign_sha256": _sha((bundle / "campaign.json").read_bytes()),
        "analysis_source_sha256": _sha(Path(__file__).read_bytes()),
        "endpoints": ENDPOINTS,
        "confidence": 0.95,
        "confidence_boundary": (
            "Simultaneous intervals assume IID events within each setting; time and calibration can confound context."
        ),
        "order_boundary": (
            "Iterator list position attributes a setting; physical execution order inside a packed job is not recorded."
        ),
        "prior": prior_metadata,
        "prior_observations": {short: prior[name] for short, name in SELECTION},
        "jobs": jobs,
        "observations": collected,
        "comparisons": comparisons,
        "complete": len(jobs) == 7 and all(job["status"] == "completed" for job in jobs),
    }


def submit_next(bundle: Path, approval: str) -> dict[str, Any]:
    """Enforce source, sequential collection and duration checks before the provider runner posts."""
    if not approval.strip():
        raise ValueError("the user's acquisition instruction is required")
    check_files(bundle)
    campaign = _read(bundle / "campaign.json")
    durations = []
    for index, job in enumerate(campaign["jobs"]):
        directory = ROOT / job["directory"]
        if (directory / "submission.json").exists():
            if not (directory / "results.json").exists():
                raise ValueError(f"collect the existing job before continuing: {directory}")
            check_run_manifest(bundle, job, directory)
            metadata, _ = read_run(directory)
            durations.append(metadata["duration_seconds"])
            continue
        if any((directory / name).exists() for name in ("submission-state.json", "job-body.json")):
            raise ValueError(f"reconcile the existing checkpoint: {directory}")
        if index >= 5 and 5 * max(durations) + 60 > 300:
            raise ValueError("the five-setting packing duration model exceeds the provider limit")
        source = bundle / job["manifest"]
        case = _read(source)
        written = bundle / "README.md"
        case.update(
            acquisition_admission="ready",
            reviewed_case={"file": written.relative_to(ROOT).as_posix(), "sha256": _sha(written.read_bytes())},
            source_case_sha256=job["manifest_sha256"],
        )
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in (
            ("cases.json", _json_bytes(case)),
            ("circuit.json", (source.parent / "circuit.json").read_bytes()),
        ):
            path = directory / name
            if path.exists() and path.read_bytes() != value:
                raise ValueError(f"prepared case differs: {path}")
            if not path.exists():
                path.write_bytes(value)
        preflight = _read(bundle / f"{job['name']}-preflight.json")
        case_hash = _sha((directory / "cases.json").read_bytes())
        prior_hashes = {
            previous["directory"]: _sha((ROOT / previous["directory"] / "results.json").read_bytes())
            for previous in campaign["jobs"][:index]
        }

        def verify(
            planned: dict[str, Any],
            *,
            hashes: dict[str, str] = prior_hashes,
            expected_case_hash: str = case_hash,
            expected_preflight: dict[str, Any] = preflight,
            case_file: Path = written,
            expected_written_hash: str = case["reviewed_case"]["sha256"],
        ) -> None:
            if any(_sha((ROOT / path / "results.json").read_bytes()) != digest for path, digest in hashes.items()):
                raise qd.PlatformError("predecessor results changed during submission")
            if (
                planned["cases_sha256"] != expected_case_hash
                or body_projection(planned["body"]) != body_projection(expected_preflight["body"])
                or planned["credit_ceiling"] > CREDIT_CEILING
                or planned["admitted_statuses"] != ["available"]
                or _sha(case_file.read_bytes()) != expected_written_hash
            ):
                raise qd.PlatformError("the live payload differs from the frozen acquisition case")

        return qd.submit(directory, "qpu:ascella", approval, CREDIT_CEILING, 300, 1, verify=verify)
    raise ValueError("all seven diagnostic jobs already have results")


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--bundle", type=Path, default=ROOT / BUNDLE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--analyze", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--submit-next", action="store_true")
    parser.add_argument("--approval")
    args = parser.parse_args()
    try:
        if args.submit_next:
            record = submit_next(args.bundle, args.approval or "")
            print(f"submitted {record['case']}: {record['job_id']}")
        elif args.analyze:
            qd.write_json(args.analyze, analyze(args.bundle), exclusive=True)
            print(f"wrote {args.analyze}")
        elif args.preflight:
            print(_json_bytes(preflight(args.bundle)).decode(), end="")
        elif args.check:
            check_files(args.bundle)
            print("seven frozen context-diagnostic cases match their source")
        else:
            write_files(args.bundle)
            print("wrote seven context-diagnostic cases")
    except (ValueError, qd.PlatformError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
