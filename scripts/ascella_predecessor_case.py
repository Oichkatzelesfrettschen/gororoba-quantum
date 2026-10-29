"""One qpu:ascella predecessor job from three retained seed-0 settings.

docs/design/ascella-predecessor-intervention.md is the written case. The builder
copies theta2-x-arm1 and theta0-x-arm0 in front of theta2-x-arm0, both orders,
into one eight-iteration template job. Every compilation seed is the value
carried by that job-00 setting. The builder sends nothing and has no submit
command. --check rebuilds the case in memory, compares it with the retained
files, and binds the template through qd_platform.template_experiment.

Usage:
  "$PYTHON" scripts/ascella_predecessor_case.py --build
  "$PYTHON" scripts/ascella_predecessor_case.py --check
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from qd_platform import JOB_NAME_LIMIT, iteration_form, sha256_bytes, template_experiment  # noqa: E402

MODES = 12
LOGICAL = 4
SOURCE_CASES = ROOT / "results/quandela/cases/ascella_signed_coherence"
CASE = ROOT / "results/quandela/cases/ascella_predecessor/job-00"
DESIGN = "docs/design/ascella-predecessor-intervention.md"
FAMILY = "ascella_predecessor"
JOB = "job-00"
PLATFORM = "qpu:ascella"
COMMAND = "sample_count"
MAX_DURATION = 300
SAMPLES_PER_ITERATION = 32768
SHOTS_PER_ITERATION = 32768
EXPECTED_SECONDS = 40
JOB_PRICE = 1.0
SHOT_PRICE = 1e-6
OUTCOMES = 12
ALPHA = 0.05
DELTA = 0.1
SEPARATION = 0.5
# (order, job-00 setting name, role). Targets sit in slot 1, so their iteration indices are odd.
ORDER = (
    ("A", "theta2-x-arm1", "predecessor"),
    ("A", "theta2-x-arm0", "target"),
    ("A", "theta0-x-arm0", "predecessor"),
    ("A", "theta2-x-arm0", "target"),
    ("B", "theta0-x-arm0", "predecessor"),
    ("B", "theta2-x-arm0", "target"),
    ("B", "theta2-x-arm1", "predecessor"),
    ("B", "theta2-x-arm0", "target"),
)
CARRIED = (
    "block",
    "readout",
    "arm",
    "theta_index",
    "theta",
    "phi_sign",
    "phi",
    "generator",
    "ideal",
    "circuit_params",
    "column",
    "operator",
    "compilation_seed",
)
MESH_RUNS = {
    "job-00": "results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00",
    "job-01": "results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01",
    "job-02": "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02",
    "job-03": "results/quandela/runs/2026-10-26T035018Z-qpu_ascella-ascella_signed_coherence-job-03",
}
BILLING_RUNS = (
    ("job-00", MESH_RUNS["job-00"]),
    ("job-03", MESH_RUNS["job-03"]),
    ("job-04", "results/quandela/runs/2026-10-26T204432Z-qpu_ascella-ascella_signed_coherence-job-04"),
    ("job-05", "results/quandela/runs/2026-10-26T223524Z-qpu_ascella-ascella_signed_coherence-job-05-i88"),
    ("job-06", "results/quandela/runs/2026-10-27T004134Z-qpu_ascella-ascella_signed_coherence-job-06"),
    ("job-07", "results/quandela/runs/2026-10-27T004828Z-qpu_ascella-ascella_signed_coherence-job-07-i96"),
)
PREDECESSORS = ("theta2-x-arm1", "theta0-x-arm0")
TARGET = "theta2-x-arm0"


def require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def probabilities(column: list[list[float]]) -> list[float]:
    """Occupation probabilities of one requested column, the squared modulus of each amplitude."""
    raw = [float(real) * float(real) + float(imag) * float(imag) for real, imag in column]
    total = math.fsum(raw)
    require(len(raw) == MODES and abs(total - 1.0) < 1e-9, f"a requested column sums to {total}, over {len(raw)} modes")
    return raw


def total_variation(first: list[float], second: list[float]) -> float:
    require(len(first) == len(second) == MODES, "probability vectors differ in length")
    return 0.5 * math.fsum(abs(left - right) for left, right in zip(first, second, strict=True))


def subset_radius(laws: int, events: int) -> float:
    """Subset-Hoeffding deviation of one law, then the radius of a difference of two laws."""
    epsilon = math.sqrt((OUTCOMES * math.log(2.0) + math.log(laws / ALPHA)) / (2.0 * events))
    return epsilon


def charge(max_shots: int) -> float:
    """Retained iterated-job charge: one per-job price plus the largest iteration's max_shots, once."""
    return round(JOB_PRICE + SHOT_PRICE * max_shots, 6)


@cache
def job00() -> tuple[dict[str, Any], bytes, str]:
    case_dir = SOURCE_CASES / "job-00"
    manifest = load_json(case_dir / "cases.json")
    circuit_bytes = (case_dir / manifest["circuit"]["file"]).read_bytes()
    require(
        sha256_bytes(circuit_bytes) == manifest["circuit"]["sha256"],
        "job-00 circuit.json differs from the digest in its cases.json",
    )
    return manifest, circuit_bytes, sha256_bytes((case_dir / "cases.json").read_bytes())


def source_settings() -> dict[str, dict[str, Any]]:
    manifest, _, _ = job00()
    found: dict[str, dict[str, Any]] = {}
    for setting in manifest["settings"]:
        if setting["name"] in {TARGET, *PREDECESSORS}:
            require(setting["name"] not in found, f"job-00 names {setting['name']} twice")
            found[setting["name"]] = setting
    require(
        set(found) == {TARGET, *PREDECESSORS},
        f"job-00 lacks a source setting: {sorted(set(PREDECESSORS) | {TARGET} - set(found))}",
    )
    for name, setting in found.items():
        require(setting["compilation_seed"] == 0, f"{name} carries compilation seed {setting['compilation_seed']!r}")
        require(isinstance(setting["compilation_seed"], int), f"{name} compilation seed is not an int")
    return found


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode())


def iteration_blobs(run: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    directory = ROOT / run
    cases = load_json(directory / "cases.json")
    results = load_json(directory / "results.json")
    iterations = results["iterations"]
    require(len(cases["settings"]) == len(iterations), f"{run}: settings and iterations differ in length")
    blobs: list[str] = []
    for setting, row in zip(cases["settings"], iterations, strict=True):
        text = row["result_fields"]["computed_circuit"]
        require(
            isinstance(text, str) and text.startswith(":PCVL:"),
            f"{run}/{setting['name']}: computed_circuit is not a Perceval blob",
        )
        blobs.append(text)
    return cases, results, blobs


def compilation_identity() -> dict[str, Any]:
    """Sha256 of the retained computed_circuit strings. Job-02 and job-03 seed-0 anchors share the target."""
    sources = source_settings()
    own_cases, own_results, own_blobs = iteration_blobs(MESH_RUNS["job-00"])
    require(
        [row["name"] for row in own_cases["settings"]] == [row["name"] for row in job00()[0]["settings"]],
        "job-00 run cases differ in order from the retained manifest",
    )
    by_name: dict[str, str] = {}
    input_by_name: dict[str, str] = {}
    for setting, blob, result in zip(own_cases["settings"], own_blobs, own_results["iterations"], strict=True):
        by_name[setting["name"]] = sha256_text(blob)
        returned_input = result["result_fields"].get("computed_input")
        require(isinstance(returned_input, str) and bool(returned_input), "the retained input identity is absent")
        input_by_name[setting["name"]] = sha256_text(returned_input)
    repeat_cases, _, repeat_blobs = iteration_blobs(MESH_RUNS["job-01"])
    require(
        {row["name"] for row in repeat_cases["settings"]} == set(by_name),
        "job-01 does not repeat job-00's setting names",
    )
    for setting, blob in zip(repeat_cases["settings"], repeat_blobs, strict=True):
        if setting["name"] in by_name:
            require(
                sha256_text(blob) == by_name[setting["name"]],
                f"job-01 {setting['name']} computed_circuit differs from job-00",
            )
    anchors: dict[str, list[str]] = {}
    for label in ("job-02", "job-03"):
        cases, _, blobs = iteration_blobs(MESH_RUNS[label])
        hashes = [
            sha256_text(blob)
            for setting, blob in zip(cases["settings"], blobs, strict=True)
            if setting["compilation_seed"] == 0
        ]
        require(len(hashes) == 8 and len(set(hashes)) == 1, f"{label} seed-0 anchors are not one shared mesh")
        require(hashes[0] == by_name[TARGET], f"{label} seed-0 anchor differs from job-00 {TARGET}")
        anchors[label] = hashes
    return {
        "job_00_id": own_results["job_id"],
        "target": {
            "name": TARGET,
            "source_observation_index": sources[TARGET]["observation_index"],
            "computed_circuit_sha256": by_name[TARGET],
            "computed_input_sha256": input_by_name[TARGET],
        },
        "predecessors": {
            name: {
                "source_observation_index": sources[name]["observation_index"],
                "computed_circuit_sha256": by_name[name],
                "computed_input_sha256": input_by_name[name],
            }
            for name in PREDECESSORS
        },
        "job_01_repeats_job_00": True,
        "seed0_anchor_count": {"job-02": len(anchors["job-02"]), "job-03": len(anchors["job-03"])},
        "anchors_match_job_00_target": True,
    }


def ascella_free(report: list[dict[str, Any]]) -> tuple[int, int, float]:
    require(len(report) == 1, "a usage report holds one snapshot")
    usage = next(row for row in report[0]["usage"] if row["platform_name"] == PLATFORM)
    return report[0]["total_jobs"], usage["nb_jobs"], usage["free_credits"]


def billing_examples() -> list[dict[str, Any]]:
    rows = []
    for label, run in BILLING_RUNS:
        directory = ROOT / run
        cases = load_json(directory / "cases.json")
        submission = load_json(directory / "submission.json")
        results = load_json(directory / "results.json")
        iterations = cases["iterations"]
        per_shots = cases["max_shots"] // iterations
        require(cases["max_shots"] % iterations == 0, f"{label}: shots do not divide evenly")
        before = ascella_free(submission["usage_before"])
        after = ascella_free(results["usage_after"])
        delta = round(after[2] - before[2], 6)
        require(
            after[0] == before[0] + 1 and after[1] == before[1] + 1,
            f"{label}: the usage movement is not one qpu:ascella job",
        )
        require(
            delta == charge(per_shots),
            f"{label}: retained charge {delta} differs from {charge(per_shots)} at {per_shots} shots",
        )
        rows.append(
            {
                "label": label,
                "job_id": results["job_id"],
                "iterations": iterations,
                "max_samples_per_iteration": cases["max_samples"] // iterations,
                "max_shots_per_iteration": per_shots,
                "duration_seconds": results["data"]["duration"],
                "seconds_per_iteration": results["data"]["duration"] / iterations,
                "free_credit_delta": delta,
            }
        )
    return rows


def requested_distances(sources: dict[str, dict[str, Any]]) -> dict[str, float]:
    laws = {name: probabilities(setting["column"]) for name, setting in sources.items()}
    pairs = {
        "target_theta2_x_arm1": total_variation(laws[TARGET], laws["theta2-x-arm1"]),
        "target_theta0_x_arm0": total_variation(laws[TARGET], laws["theta0-x-arm0"]),
        "predecessors": total_variation(laws["theta2-x-arm1"], laws["theta0-x-arm0"]),
    }
    for name, distance in pairs.items():
        require(distance >= SEPARATION, f"requested TVD {name} is {distance}, below {SEPARATION}")
    return pairs


def build_settings(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    settings = []
    for index, (order, source_name, role) in enumerate(ORDER):
        source = sources[source_name]
        slot = 1 if role == "target" else 0
        require(index % 2 == slot, f"iteration {index} breaks the odd-target slot rule")
        missing = [key for key in CARRIED if key not in source]
        require(not missing, f"{source_name} lacks {missing}")
        settings.append(
            {
                "name": f"{order}-{slot}-{role}-{source_name}",
                "observation_index": index,
                "order": order,
                "slot": slot,
                "role": role,
                "source_name": source_name,
                "source_observation_index": source["observation_index"],
                **{key: source[key] for key in CARRIED},
            }
        )
    return settings


def documents() -> dict[str, bytes]:
    sources = source_settings()
    _, circuit_bytes, cases_sha = job00()
    settings = build_settings(sources)
    require(len(settings) == len(ORDER), "the schedule lost an iteration")
    distances = requested_distances(sources)
    epsilon = subset_radius(len(settings), SAMPLES_PER_ITERATION)
    identity = compilation_identity()
    examples = billing_examples()
    timed = [
        row for row in examples if row["max_shots_per_iteration"] == SHOTS_PER_ITERATION and row["iterations"] >= 80
    ]
    require(len(timed) == 4, "the 32,768-shot timing jobs are not the four retained runs")
    slowest = max(row["seconds_per_iteration"] for row in timed)
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": JOB,
        "platforms": [PLATFORM],
        "command": COMMAND,
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES_PER_ITERATION * len(settings),
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "max_credits": charge(SHOTS_PER_ITERATION),
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(LOGICAL)),
        "eligibility": "occupation sum one across all twelve returned modes",
        "design": DESIGN,
        "analysis_sources": {
            name: sha256_bytes((ROOT / name).read_bytes())
            for name in (
                "scripts/ascella_predecessor_case.py",
                "scripts/ascella_predecessor_analysis.py",
                "scripts/ascella_experiment_analysis.py",
                "scripts/experiment_analysis.py",
                "scripts/qd_platform.py",
                "gororoba_quantum/parallel.py",
            )
        },
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "admitted_platform_statuses": ["available", "running"],
            "question": "whether the signed contrast of four attributed target distributions exceeds 0.1 TVD",
            "predecessors": list(PREDECESSORS),
            "target": TARGET,
            "orders": ["A", "B"],
            "order_A": "theta2-x-arm1, target, theta0-x-arm0, target",
            "order_B": "theta0-x-arm0, target, theta2-x-arm1, target",
            "target_slots": [1, 3, 5, 7],
            "common_coefficients": ["1/2", "-1/2", "-1/2", "1/2"],
            "reversal_coefficients": ["-1/2", "1/2", "-1/2", "1/2"],
            "contrast_pairs": [[1, 3], [7, 5]],
            "predecessor_pairs": [[0, 2], [4, 6]],
            "requested_tvd": distances,
            "requested_separation": SEPARATION,
            "delta_tvd": DELTA,
            "outcomes": OUTCOMES,
            "laws": len(settings),
            "alpha": ALPHA,
            "events_per_iteration": SAMPLES_PER_ITERATION,
            "subset_hoeffding_epsilon": epsilon,
            "two_law_radius": 2.0 * epsilon,
            "expected_seconds": EXPECTED_SECONDS,
            "expected_credits": charge(SHOTS_PER_ITERATION),
            "credit_basis": "1 + 1e-6 times the largest iteration max_shots, once per job",
            "projected_seconds_at_slowest_retained_rate": len(settings) * slowest,
            "histogram": "twelve single-photon modes, modes 4..11 included",
            "response_above_margin": "the signed common-contrast norm lower bound exceeds delta_tvd",
            "response_below_margin": "the signed common-contrast norm upper bound is below delta_tvd",
            "predecessor_control": "both predecessor-pair TVD lower bounds exceed delta_tvd",
            "inference": "conditional on an externally anchored pre-acquisition IID sampling contract",
            "physical_predecessor_attribution": (
                "unavailable: returned iteration order does not prove physical chronology"
            ),
            "drift_boundary": (
                "common coefficients cancel affine request-index drift; quadratic drift and carryover remain confounded"
            ),
            "otherwise": "inconclusive within this job",
            "compilation_stop": (
                "a computed_circuit sha256 outside compilation_identity stops the comparison before either reading"
            ),
            "target_only": "absent",
            "auto_retry": False,
            "source_cases": "results/quandela/cases/ascella_signed_coherence/job-00/cases.json",
            "source_cases_sha256": cases_sha,
            "compilation_identity": identity,
            "billing_examples": examples,
            "interpretation": "one-job counterbalanced predecessor contrast on retained Ascella seed-0 meshes",
        },
    }
    require(len(f"{FAMILY}/{JOB}") <= JOB_NAME_LIMIT, "the Perceval job name exceeds 50 characters")
    require(iteration_form(manifest) == "template", "the iterations do not form a template job")
    experiment, bound = template_experiment(manifest, json.loads(circuit_bytes))
    require(experiment is not None and len(bound) == len(settings), "the template did not bind every iteration")
    require(2.0 * epsilon < DELTA, "the two-law radius is at least the decision threshold")
    payload = {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}
    return payload


def check() -> dict[str, Any]:
    rebuilt = documents()
    for name, data in rebuilt.items():
        retained = CASE / name
        require(retained.is_file(), f"{retained} is missing; build the case first")
        require(retained.read_bytes() == data, f"{retained} differs from the builder")
    manifest = json.loads(rebuilt["cases.json"])
    return manifest


def summary(manifest: dict[str, Any]) -> str:
    registered = manifest["preregistered"]
    lines = [
        f"cases_sha256 {sha256_bytes((json.dumps(manifest, indent=1) + '\n').encode())}",
        f"circuit_sha256 {manifest['circuit']['sha256']}",
        f"iterations {manifest['iterations']}",
        f"max_samples {manifest['max_samples']}",
        f"max_shots {manifest['max_shots']}",
        f"max_credits {manifest['max_credits']}",
        f"expected_seconds {registered['expected_seconds']}",
        f"projected_seconds {registered['projected_seconds_at_slowest_retained_rate']}",
        f"epsilon {registered['subset_hoeffding_epsilon']}",
        f"two_law_radius {registered['two_law_radius']}",
        f"requested_tvd {json.dumps(registered['requested_tvd'], sort_keys=True)}",
        f"target_circuit {registered['compilation_identity']['target']['computed_circuit_sha256']}",
    ]
    for name, row in registered["compilation_identity"]["predecessors"].items():
        lines.append(f"predecessor {name} index {row['source_observation_index']} {row['computed_circuit_sha256']}")
    for row in registered["billing_examples"]:
        lines.append(
            f"billing {row['label']} {row['job_id']} iterations {row['iterations']} "
            f"shots {row['max_shots_per_iteration']} duration {row['duration_seconds']} "
            f"charge {row['free_credit_delta']}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.build:
        CASE.mkdir(parents=True, exist_ok=True)
        for name, data in documents().items():
            (CASE / name).write_bytes(data)
    manifest = check()
    sys.stdout.write(summary(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
