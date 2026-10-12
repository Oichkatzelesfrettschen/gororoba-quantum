"""Bound noisy distribution differences while preserving the retained failure."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any


def _enabled_execution_mode(circuit: Any) -> str:
    """Classify the retained density-matrix circuit before terminal sampling.

    Reset before the terminal readout is a deterministic density-matrix
    channel. Aer can defer measurements past operations on disjoint qubits;
    operations on measured qubits and classical control require branching.
    The classifier covers the retained gate/reset/delay/readout corpus.
    """
    supported = {"barrier", "cz", "delay", "h", "if_else", "measure", "reset", "rz", "sx", "x"}
    if any(instruction.operation.name not in supported for instruction in circuit.data):
        raise RuntimeError(f"{circuit.name}: instruction lies outside the retained execution-mode contract")
    measured_qubits: set[Any] = set()
    for instruction in circuit.data:
        operation = instruction.operation
        if getattr(operation, "blocks", ()) or getattr(operation, "condition", None) is not None:
            if not measured_qubits:
                raise RuntimeError(f"{circuit.name}: classical control precedes the retained measurement boundary")
            return "shot_branching"
        if operation.name == "measure":
            measured_qubits.update(instruction.qubits)
    if not measured_qubits:
        raise RuntimeError(f"{circuit.name}: retained member lacks terminal measurement")
    ancestors: set[Any] = set()
    relevant = []
    for instruction in reversed(circuit.data):
        if instruction.operation.name == "barrier":
            continue
        if instruction.operation.name == "measure" or ancestors.intersection(instruction.qubits):
            ancestors.update(instruction.qubits)
            relevant.append(instruction)
    measured_qubits.clear()
    for instruction in reversed(relevant):
        if instruction.operation.name == "measure":
            measured_qubits.update(instruction.qubits)
        elif measured_qubits.intersection(instruction.qubits):
            return "shot_branching"
    return "measurement_sampling"


def execution_mode_audit(
    members: list[dict[str, Any]], circuits: list[Any], cases: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bind every metadata position to the retained QPY member before checking flags."""
    if not members or len(members) != len(circuits):
        raise RuntimeError("Retained member and QPY cardinalities differ or are empty")
    identities = [member["name"] for member in members]
    if any(not isinstance(name, str) or not name for name in identities) or len(set(identities)) != len(identities):
        raise RuntimeError("Retained member names must be unique nonempty strings")
    catalog = []
    for archive_index, (member, circuit) in enumerate(zip(members, circuits, strict=True)):
        if member["name"] != circuit.name:
            raise RuntimeError(f"QPY member order differs at index {archive_index}")
        if not isinstance(member["family"], str) or not member["family"]:
            raise RuntimeError("Retained member family must be a nonempty string")
        catalog.append(
            {
                "archive_index": archive_index,
                "family": member["family"],
                "member": member["name"],
                "enabled_execution_mode": _enabled_execution_mode(circuit),
            }
        )
    if not cases:
        raise RuntimeError("Execution-mode audit requires completed cases")
    mismatches = []
    checked_results = 0
    for case_index, case in enumerate(cases):
        selected = [member for member in catalog if member["family"] == case["family"]]
        if not selected:
            raise RuntimeError(f"Case {case_index}: family lacks retained QPY members")
        names = {member["member"] for member in selected}
        if set(case["distributions"]) != names or set(case["counts_total"]) != names:
            raise RuntimeError(f"Case {case_index}: result names differ from retained QPY members")
        metadata_rows = case["metadata"]
        if not isinstance(metadata_rows, list) or len(metadata_rows) != len(selected):
            raise RuntimeError(f"Case {case_index}: metadata cardinality differs from retained member order")
        enabled = case["shot_branching_enable"]
        if type(enabled) is not bool:
            raise RuntimeError(f"Case {case_index}: branching request must be Boolean")
        for member_index, (member, metadata) in enumerate(zip(selected, metadata_rows, strict=True)):
            if not isinstance(metadata, dict):
                raise RuntimeError(f"Case {case_index}: member metadata must be an object")
            reasons = []
            for name, expected in (("device", "CPU"), ("method", "density_matrix")):
                if metadata.get(name) != expected:
                    reasons.append(f"{name} must be {expected}")
            for name in ("shot_branching_enabled", "measure_sampling"):
                if name in metadata and type(metadata[name]) is not bool:
                    reasons.append(f"{name} must be Boolean when present")
            branching = metadata.get("shot_branching_enabled", False)
            sampling = metadata.get("measure_sampling", False)
            expected_mode = member["enabled_execution_mode"] if enabled else "branching_disabled"
            if expected_mode == "shot_branching":
                if branching is not True or sampling is not False:
                    reasons.append("intermediate measurement or classical control requires branching without sampling")
            elif expected_mode == "measurement_sampling":
                if sampling is not True or branching is not False:
                    reasons.append("terminal readout requires measurement sampling without branching")
            elif branching is not False:
                reasons.append("disabled case requires shot_branching_enabled absent or false")
            checked_results += 1
            if reasons:
                mismatches.append(
                    {
                        "case_index": case_index,
                        "member_index": member_index,
                        "member": member["member"],
                        "family": case["family"],
                        "expected_execution_mode": expected_mode,
                        "observed_branching": metadata.get("shot_branching_enabled"),
                        "observed_sampling": metadata.get("measure_sampling"),
                        "reasons": reasons,
                    }
                )
    return {
        "contract": "retained-qpy-density-matrix-execution-modes-v1",
        "metadata_order": "qualification circuit order, filtered by case family, as submitted by the reuse probe",
        "members": catalog,
        "case_count": len(cases),
        "member_result_count": checked_results,
        "mismatches": mismatches,
        "all_modes_match": not mismatches,
    }


def _bound_execution_mode_audit(
    retained: dict[str, Any], replay: dict[str, Any], qualification_bytes: bytes, archive_bytes: bytes
) -> dict[str, Any]:
    from qiskit import qpy

    if replay["state"] != "completed":
        raise RuntimeError("The reuse probe must finish before analysis")
    if replay["qualification_input_sha256"] != hashlib.sha256(qualification_bytes).hexdigest():
        raise RuntimeError("Qualification bytes differ from the reuse probe's input")
    if retained["qpy_sha256"] != replay["qpy_sha256"]:
        raise RuntimeError("Compiled circuit archives differ")
    if hashlib.sha256(archive_bytes).hexdigest() != retained["qpy_sha256"]:
        raise RuntimeError("Compiled circuit archive changed")
    return execution_mode_audit(retained["circuits"], list(qpy.load(io.BytesIO(archive_bytes))), replay["cases"])


def _verify_retained_evidence() -> None:
    root = Path(__file__).resolve().parent
    qualification_bytes = gzip.decompress((root / "cpu_branching_qualification.json.gz").read_bytes())
    retained = json.loads(qualification_bytes)
    replay = json.loads(gzip.decompress((root / "cpu_branching_reuse_probe.json.gz").read_bytes()))
    archive_bytes = gzip.decompress((root / "cpu_branching_inputs.qpy.gz").read_bytes())
    audit = _bound_execution_mode_audit(retained, replay, qualification_bytes, archive_bytes)
    if not audit["all_modes_match"]:
        raise RuntimeError(f"Retained execution-mode mismatches: {audit['mismatches']}")
    print(
        f"Retained execution modes: {len(audit['members'])} QPY members, "
        f"{audit['case_count']} cases, {audit['member_result_count']} results pass"
    )


def _verify() -> None:
    from qiskit import QuantumCircuit, qpy

    coherent = QuantumCircuit(1, 1, name="coherent")
    coherent.h(0)
    coherent.measure(0, 0)
    delayed = QuantumCircuit(1, 1, name="reset_delay")
    delayed.h(0)
    delayed.delay(8, 0, unit="dt")
    delayed.reset(0)
    delayed.measure(0, 0)
    intermediate = QuantumCircuit(1, 2, name="intermediate_measurement")
    intermediate.measure(0, 0)
    intermediate.reset(0)
    intermediate.h(0)
    intermediate.measure(0, 1)
    controlled = QuantumCircuit(1, 2, name="classical_control")
    controlled.measure(0, 0)
    with controlled.if_test((controlled.clbits[0], 1)):
        controlled.x(0)
    controlled.measure(0, 1)
    disjoint = QuantumCircuit(2, 2, name="deferred_measurement")
    disjoint.h(0)
    disjoint.measure(0, 0)
    disjoint.barrier()
    disjoint.reset(1)
    disjoint.h(1)
    disjoint.measure(1, 1)
    pruned = coherent.copy(name="pruned_output")
    pruned.x(0)
    intermediate_delay = QuantumCircuit(1, 2, name="intermediate_delay")
    intermediate_delay.measure(0, 0)
    intermediate_delay.delay(8, 0, unit="dt")
    intermediate_delay.measure(0, 1)
    original = [coherent, delayed, intermediate, controlled, disjoint, pruned, intermediate_delay]
    archive = io.BytesIO()
    qpy.dump(original, archive)
    archive.seek(0)
    circuits = list(qpy.load(archive))
    members = [{"name": circuit.name, "family": "fixture"} for circuit in original]
    expected_modes = [
        "measurement_sampling",
        "measurement_sampling",
        "shot_branching",
        "shot_branching",
        "measurement_sampling",
        "measurement_sampling",
        "shot_branching",
    ]
    cases: list[dict[str, Any]] = [
        {
            "family": "fixture",
            "shot_branching_enable": enabled,
            "distributions": {circuit.name: [1.0] for circuit in circuits},
            "counts_total": {circuit.name: 8 for circuit in circuits},
            "metadata": [
                {
                    "device": "CPU",
                    "method": "density_matrix",
                    "measure_sampling": mode == "measurement_sampling",
                    **({"shot_branching_enabled": True} if enabled and mode == "shot_branching" else {}),
                }
                for mode in expected_modes
            ],
        }
        for enabled in (False, True)
    ]
    observed = execution_mode_audit(members, circuits, cases)
    if (
        not observed["all_modes_match"]
        or [row["enabled_execution_mode"] for row in observed["members"]] != expected_modes
    ):
        raise RuntimeError("QPY-structure execution-mode fixture failed")
    rejected = 0

    def reject(
        changed_members: list[dict[str, Any]], changed_circuits: list[Any], changed_cases: list[dict[str, Any]]
    ) -> None:
        nonlocal rejected
        try:
            result = execution_mode_audit(changed_members, changed_circuits, changed_cases)
        except RuntimeError:
            rejected += 1
            return
        if result["all_modes_match"]:
            raise RuntimeError("Execution-mode mutation passed")
        rejected += 1

    for case_index, member_index, mutation in (
        (0, 0, {"shot_branching_enabled": True}),
        (0, 2, {"shot_branching_enabled": True}),
        (1, 2, {"shot_branching_enabled": False, "measure_sampling": True}),
        (1, 3, {"shot_branching_enabled": False}),
        (1, 0, {"shot_branching_enabled": True, "measure_sampling": False}),
        (1, 1, {"measure_sampling": False}),
        (1, 2, {"measure_sampling": True}),
        (1, 0, {"measure_sampling": "true"}),
        (0, 0, {"shot_branching_enabled": None}),
        (1, 2, {"shot_branching_enabled": 1}),
        (1, 0, {"device": "GPU"}),
        (1, 0, {"method": "automatic"}),
    ):
        changed = copy.deepcopy(cases)
        changed[case_index]["metadata"][member_index].update(mutation)
        reject(members, circuits, changed)
    metadata_variant: list[dict[str, Any]]
    for metadata_variant in ([], cases[1]["metadata"][:-1], cases[1]["metadata"] + [cases[1]["metadata"][0]]):
        changed = copy.deepcopy(cases)
        changed[1]["metadata"] = metadata_variant
        reject(members, circuits, changed)
    changed = copy.deepcopy(cases)
    changed[1]["metadata"][0], changed[1]["metadata"][2] = changed[1]["metadata"][2], changed[1]["metadata"][0]
    reject(members, circuits, changed)
    changed = copy.deepcopy(cases)
    changed[1]["distributions"].pop("coherent")
    reject(members, circuits, changed)
    changed = copy.deepcopy(cases)
    changed[1]["counts_total"]["unexpected"] = 8
    reject(members, circuits, changed)
    reject([members[2], members[1], members[0], *members[3:]], circuits, cases)
    reject([members[0], members[0], *members[2:]], circuits, cases)
    reject(members, circuits[:-1], cases)
    reject(members, circuits, [])
    unsupported = coherent.copy()
    unsupported.initialize([1.0, 0.0], 0)
    reject(members, [unsupported, *circuits[1:]], cases)
    print(f"Execution modes: QPY order, reset/deferral eligibility, mode flags, and {rejected} mutations pass")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        if arguments.repo is not None or arguments.out is not None:
            parser.error("--check runs independently of repository/output arguments")
        _verify()
        _verify_retained_evidence()
        return
    if arguments.repo is None or arguments.out is None:
        parser.error("--repo and --out are required")
    sys.path.insert(0, str(arguments.repo / "gororoba_quantum"))
    from diagnostic_experiments import family_contracts

    filenames = ("cpu_branching_qualification.json", "cpu_branching_reuse_probe.json")
    inputs = {name: (arguments.out / name).read_bytes() for name in filenames}
    retained, replay = (json.loads(inputs[name]) for name in filenames)
    archive_bytes = (arguments.out / "cpu_branching_inputs.qpy").read_bytes()
    archive_digest = hashlib.sha256(archive_bytes).hexdigest()
    mode_audit = _bound_execution_mode_audit(retained, replay, inputs[filenames[0]], archive_bytes)

    pairs: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
    for family, baseline_shots in (("folded-qpe", 2048), ("n21-feedback", 256)):
        baseline = next(
            case
            for case in retained["cases"]
            if case["family"] == family and case["shots"] == baseline_shots and not case["shot_branching_enable"]
        )
        fresh = [case for case in replay["cases"] if case["family"] == family and case["mode"].startswith("fresh_")]
        if len(fresh) != 3:
            raise RuntimeError("Expected three completed fresh trials per family")
        for trial in fresh:
            pairs.append(("retained_baseline_vs_fresh", family, baseline, trial))
        for left, right in itertools.combinations(fresh, 2):
            pairs.append(("fresh_vs_fresh", family, left, right))
        if family == "folded-qpe":
            original = next(
                case
                for case in retained["cases"]
                if case["family"] == family and case["shots"] == 2048 and case["shot_branching_enable"]
            )
            reused = next(
                case
                for case in replay["cases"]
                if case["family"] == family and case["shots"] == 2048 and case["shot_branching_enable"]
            )
            pairs.append(("retained_baseline_vs_reused", family, baseline, reused))
            for trial in fresh:
                pairs.append(("retained_failed_vs_fresh", family, original, trial))

    alpha = 1e-6
    bin_count = sum(len(values) for _kind, _family, left, _right in pairs for values in left["distributions"].values())
    term_count = sum(
        2 * sum(len(contract.terms) for contract in family_contracts(family, 0.08, 0.05, 0.8))
        for _kind, family, _left, _right in pairs
    )
    comparisons = []
    contrast_comparisons = []
    for kind, family, left, right in pairs:
        if left["distributions"].keys() != right["distributions"].keys():
            raise RuntimeError("Paired circuit labels differ")
        radius = sum(math.sqrt(math.log(8 * bin_count / alpha) / (2 * row["shots"])) for row in (left, right))
        differences = {
            name: [abs(first - second) for first, second in zip(values, right["distributions"][name], strict=True)]
            for name, values in left["distributions"].items()
        }
        maximum = max(value for values in differences.values() for value in values)
        identity = {
            "kind": kind,
            "family": family,
            "left_shots": left["shots"],
            "right_shots": right["shots"],
            "left_seed": left["seed"],
            "right_seed": right["seed"],
        }
        comparisons.append(
            {
                **identity,
                "bin_differences": differences,
                "max_absolute_bin_difference": maximum,
                "simultaneous_radius": radius,
                "compatible": maximum <= radius,
            }
        )
        for contract in family_contracts(family, 0.08, 0.05, 0.8):
            estimates = [
                sum(
                    term.sign
                    * sum(
                        value * probability
                        for value, probability in zip(term.values, row["distributions"][term.member], strict=True)
                    )
                    for term in contract.terms
                )
                for row in (left, right)
            ]
            contrast_radius = sum(
                math.sqrt(math.log(4 * term_count / alpha) / (2 * row["shots"])) for row in (left, right)
            ) * sum(max(term.values) - min(term.values) for term in contract.terms)
            difference = abs(estimates[0] - estimates[1])
            contrast_comparisons.append(
                {
                    **identity,
                    "contrast": contract.name,
                    "estimates": estimates,
                    "absolute_difference": difference,
                    "simultaneous_radius": contrast_radius,
                    "compatible": difference <= contrast_radius,
                }
            )

    all_counts_complete = all(
        count == case["shots"] for case in replay["cases"] for count in case["counts_total"].values()
    )
    all_qpy_unchanged = all(case["qpy_before"] == case["qpy_after"] for case in replay["cases"])
    report = {
        "state": "failed_fresh_instance_repair_falsified",
        "production_shot_branching_qualified": False,
        "analysis_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_input_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in inputs.items()},
        "qpy_sha256": archive_digest,
        "familywise_alpha": alpha,
        "total_bin_comparisons": bin_count,
        "total_contrast_term_estimates": term_count,
        "bound_scope": (
            "Hoeffding union bounds allocate alpha/2 to all listed bin comparisons and alpha/2 to all listed "
            "contrast comparisons. Each estimate assumes stationary independent shots; comparisons and runs "
            "need not be independent. Compatibility does not establish numerical equivalence."
        ),
        "residuals": [
            "A fresh32768 trial fails on qpe_no_feed_forward_s3; fresh-instance construction fails as a repair.",
            "The retained noisy folded2048 failure on qpe_archived_s1 remains unexplained.",
            "The reuse probe starts from QPY-loaded circuits; the original used in-memory compiled circuit objects.",
            "N21 branch-off baseline has 256 shots; a full32768 paired baseline was not measured.",
            "Repeated branch-enabled draws test stability and do not independently validate noisy probabilities.",
            "Nearby seeds may share pseudorandom streams; independence between repeat runs is unclaimed.",
            "Serialized channel identity excludes delay-noise passes; fixture reconstruction supplies those passes.",
        ],
        "all_count_totals_complete": all_counts_complete,
        "all_qpy_before_after_identical": all_qpy_unchanged,
        "all_execution_modes_match": mode_audit["all_modes_match"],
        "execution_mode_audit": mode_audit,
        "execution_mode_boundary": (
            "QPY member order binds every CPU density_matrix result. Enabled cases require branching for "
            "operations on measured qubits or classical control, and measurement sampling for deferrable "
            "readout, including reset/delay channels before readout. Disabled cases require branching absent or false. "
            "Runtime's broader dynamic classification does not determine Aer sampling eligibility."
        ),
        "comparisons": comparisons,
        "contrast_comparisons": contrast_comparisons,
    }
    (arguments.out / "cpu_branching_reuse_analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {key: value for key, value in report.items() if key not in ("comparisons", "contrast_comparisons")},
            indent=2,
        )
    )
    for kind in dict.fromkeys(row["kind"] for row in comparisons):
        selected = [row for row in comparisons if row["kind"] == kind]
        print(kind, sum(row["compatible"] for row in selected), "/", len(selected))


if __name__ == "__main__":
    main()
