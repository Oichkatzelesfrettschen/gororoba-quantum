"""Freeze six iterator jobs for cancellation and dimension-six screening, entirely offline.

The first dark arm also qualifies the larger template's hardware duration and
result interface. Subsequent acquisition requires its complete attributed result.
The canonical operator cases retain their bytes and compilation seed identities.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

CANONICAL = Path("docs/evidence/quantum-experiment-conformance/runner-scalar-operators/ascella")
BUNDLE = Path("docs/evidence/ascella-cancellation-transition-acquisition")
COHORT = "ascella-cancellation-transition-screening"
SAMPLES = 65_536
SHOTS = 131_072
JOB_CREDIT_CEILING = 1.131072
CANCELLATION = ("dark", "bright", "bright-repeat", "dark-repeat", "fixture")


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def qualification_profile() -> dict[str, Any]:
    """Scientific screening requirements, distinct from assumptions about the instrument."""
    return {
        "schema": "ascella-experiment-qualification-v1",
        "cohort_id": COHORT,
        "familywise_confidence": 0.95,
        "endpoints": 243,
        "endpoint_definition": "17*(12 physical ports + 1 invalid category)+17 leakage aggregates+5 heralds",
        "samples_per_setting": SAMPLES,
        "detected_shot_cap_per_setting": SHOTS,
        "precision": 0.01,
        "leakage_includes_invalid": True,
        "thresholds": {
            "compilation_tv": 0.01,
            "dark_herald_upper": 0.02,
            "bright_herald_lower": 0.98,
            "fixture_lower": 0.47,
            "fixture_upper": 0.53,
            "repeat_difference": 0.01,
            "identity_lower": 0.95,
            "cross_basis_tv_upper": 0.05,
            "leakage_upper": 0.02,
        },
        "denominator": (
            "All returned accepted events, including invalid photon-number outcomes; incident pulses unknown."
        ),
        "expansion": "All twelve pilot settings qualify once; a failed or incomplete pilot stops automatic expansion.",
        "sampling_model": "Simultaneous Clopper-Pearson intervals conditional on IID Bernoulli trials within settings.",
        "confirmation": (
            "The full 54-setting acquisition uses a fresh cohort and a separately frozen confidence family."
        ),
    }


def _load_setting(family: str, name: str, position: int, iteration: int) -> tuple[dict[str, Any], dict[str, Any], str]:
    source = CANONICAL / family / name / "cases.json"
    data = (ROOT / source).read_bytes()
    manifest = json.loads(data)
    circuit_path = source.parent / manifest["circuit"]["file"]
    circuit = (ROOT / circuit_path).read_text(encoding="utf-8")
    if sha256(circuit.encode()) != manifest["circuit"]["sha256"]:
        raise ValueError(f"canonical circuit digest differs: {name}")
    row = copy.deepcopy(manifest["settings"][0])
    row.update(
        cohort_id=COHORT,
        setting_id=f"{family}/{name}",
        iteration_index=iteration,
        sequence_position=position,
        compilation_seed=manifest["compilation_seed"],
        compilation_seed_allocation=manifest["compilation_seed_allocation"],
        source_manifest={"file": source.as_posix(), "sha256": sha256(data)},
        pilot_role="cancellation"
        if family == "sedenion-lcu"
        else ("identity" if name.startswith("computational-to-computational-") else "cross-basis"),
    )
    return manifest, row, circuit


def build_files() -> dict[str, str]:
    """Copy the selected canonical operators into five singleton and one twelve-entry iterator."""
    profile_text = json_text(qualification_profile())
    binding = {"file": (BUNDLE / "qualification-profile.json").as_posix(), "sha256": sha256(profile_text.encode())}
    files = {"qualification-profile.json": profile_text}
    groups = [(f"sedenion-cancellation-{name}", [("sedenion-lcu", name)]) for name in CANCELLATION]
    pilot = [("mub-six", f"computational-to-computational-input-{index}") for index in range(6)]
    pilot += [("mub-six", f"product_fourier-to-product_chirped-input-{index}") for index in range(6)]
    groups.append(("dimension-six-transition-pilot", pilot))
    campaign: dict[str, Any] = {
        "schema": "ascella-cancellation-transition-campaign-v1",
        "cohort_id": COHORT,
        "qualification_profile": binding,
        "cases": [],
        "settings": [],
        "execution_stop_seconds_per_job": 300,
        "summed_execution_stop_seconds": 1800,
        "credit_ceiling": round(len(groups) * JOB_CREDIT_CEILING, 6),
        "remaining_account_credits": None,
        "account_credit_expiry_utc": None,
    }
    position = 0
    for job, selections in groups:
        originals, rows, circuits = [], [], []
        for iteration, (family, name) in enumerate(selections):
            original, row, circuit = _load_setting(family, name, position, iteration)
            originals.append(original)
            rows.append(row)
            circuits.append(circuit)
            position += 1
        if len(set(circuits)) != 1:
            raise ValueError(f"{job}: a packed job needs byte-identical circuit templates")
        manifest = copy.deepcopy(originals[0])
        for key in ("compilation_seed", "compilation_seed_allocation", "compilation_seed_role"):
            manifest.pop(key, None)
        manifest.update(
            job=job,
            cohort_id=COHORT,
            iterator=len(rows) == 1,
            iterations=len(rows),
            settings=rows,
            max_samples=len(rows) * SAMPLES,
            max_shots=len(rows) * SHOTS,
            max_duration=300,
            max_credits=JOB_CREDIT_CEILING,
            acquisition_admission="awaiting-written-case-review",
            qualification_profile=binding,
            compilation_seed_role="reproduce-registered-base-meshes",
            runtime_question="Qualify 342-operation template on Ascella; dry-run supplies no runtime forecast.",
        )
        manifest_file = f"cases/{job}/cases.json"
        files[manifest_file] = json_text(manifest)
        files[f"cases/{job}/circuit.json"] = circuits[0]
        directory = f"results/quandela/runs/ascella-{job}"
        identifiers = [row["setting_id"] for row in rows]
        campaign["cases"].append(
            {
                "name": job,
                "directory": directory,
                "manifest": manifest_file,
                "sha256": sha256(files[manifest_file].encode()),
                "settings": identifiers,
            }
        )
        campaign["settings"].extend(
            {
                "setting_id": row["setting_id"],
                "case": directory,
                "iteration_index": row["iteration_index"],
                "sequence_position": row["sequence_position"],
                "pilot_role": row["pilot_role"],
            }
            for row in rows
        )
    files["campaign.json"] = json_text(campaign)
    return files


def write_files(out: Path) -> None:
    """Write prospective inputs, refusing to overwrite a different frozen file."""
    for name, value in build_files().items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") != value:
            raise ValueError(f"frozen file differs: {path}")
        if not path.exists():
            path.write_text(value, encoding="utf-8")


def check_files(out: Path) -> None:
    """Recompute the exact cohort without touching frozen artifacts."""
    for name, value in build_files().items():
        path = out / name
        if not path.is_file() or path.read_text(encoding="utf-8") != value:
            raise ValueError(f"frozen file differs: {path}")


def _validate_case(directory: Path) -> dict[str, Any]:
    from qd_platform import iteration_budgets, iteration_form, load_case, template_experiment

    manifest, circuit, manifest_hash = load_case(directory)
    template_experiment(manifest, circuit)
    budgets = iteration_budgets(manifest)
    if iteration_form(manifest) != "template" or budgets != [(SAMPLES, SHOTS)] * len(manifest["settings"]):
        raise ValueError("the screening payload needs exact template-iterator budgets")
    return {
        "case": directory.name,
        "cases_sha256": manifest_hash,
        "validated_complete_operators": len(manifest["settings"]),
        "modes": circuit["modes"],
        "template_operations": len(circuit["ops"]),
        "iterator_form": "template",
        "samples_per_iteration": SAMPLES,
        "detected_shots_per_iteration": SHOTS,
    }


def validate_files(out: Path) -> dict[str, Any]:
    """Reconstruct every full template operator using the provider's local SDK."""
    import perceval  # noqa: F401
    from experiment_analysis import binomial_interval

    check_files(out)
    campaign = json.loads((out / "campaign.json").read_bytes())
    directories = [out / Path(case["manifest"]).parent for case in campaign["cases"]]
    checks = ordered_map(_validate_case, directories, min_items=1)
    lower, upper = binomial_interval(SAMPLES // 2, SAMPLES, endpoints=243)
    return {
        "schema": "ascella-experiment-local-validation-v1",
        "cases": checks,
        "endpoint_family": 243,
        "worst_iid_interval_half_width": (upper - lower) / 2,
        "zero_event_iid_upper_bound": binomial_interval(0, SAMPLES, endpoints=243)[1],
        "provider_submissions": 0,
    }


def prepare_runs(out: Path, written_case: Path, *, case_index: int = 0) -> list[Path]:
    """Prepare one successor; future cases stay outside the retained acquisition census."""
    check_files(out)
    case_path = written_case.resolve()
    relative = case_path.relative_to(ROOT)
    binding = {"file": relative.as_posix(), "sha256": sha256(case_path.read_bytes())}
    campaign = json.loads((out / "campaign.json").read_bytes())
    prepared = []
    for index, case in enumerate(campaign["cases"]):
        if index != case_index:
            continue
        source = out / case["manifest"]
        manifest = json.loads(source.read_bytes())
        manifest.update(
            acquisition_admission="ready" if index == 0 else "awaiting-prerequisites",
            reviewed_case=binding,
            source_case_sha256=case["sha256"],
        )
        directory = ROOT / case["directory"]
        values = {"cases.json": json_text(manifest), "circuit.json": (source.parent / "circuit.json").read_text()}
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            path = directory / name
            if path.exists() and path.read_text() != value:
                raise ValueError(f"prepared successor differs: {path}")
            if not path.exists():
                path.write_text(value, encoding="utf-8")
        prepared.append(directory)
    return prepared


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / BUNDLE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--prepare", type=Path, metavar="WRITTEN_CASE")
    args = parser.parse_args()
    if args.validate:
        print(json_text(validate_files(args.out)), end="")
        return 0
    if args.prepare is not None:
        for directory in prepare_runs(args.out, args.prepare):
            print(directory.relative_to(ROOT))
    elif args.check:
        check_files(args.out)
    else:
        write_files(args.out)
    print("six Ascella iterator cases: five ordered cancellation jobs and twelve pilot settings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
