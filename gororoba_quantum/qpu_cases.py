"""Write an unapproved, artifact-bound case for an admitted diagnostic dry run.

The writer reads retained records and QPY circuits only. It constructs neither
an IBM service nor a primitive. The case separates model admission from future
hardware observations and carries the existing runner's approval command.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import re
import shlex
import tempfile
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qpy

CASE_FILENAME = "UNAPPROVED_CASE.md"
FAMILIES = {"folded-qpe", "n21-feedback"}
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:+/-]*\Z")
_HEX_DIGEST = re.compile(r"[a-f0-9]{64}\Z")
_DESIGN_OPTIONS = (
    "shot_tiers",
    "replica_tiers",
    "optimizer_candidates",
    "model_shots",
    "precision",
    "alpha",
    "power",
    "simulation_alpha",
    "job_overhead_seconds",
    "classical_latency_us",
    "reserve_seconds",
    "max_total_execution_seconds",
)
_MAPPING_FIELDS = (
    "replica_cap",
    "measurement_delay_dt",
    "replaced_measurement_qubits",
    "shared_initial_layout",
    "extra_control",
    "measurement_seconds",
    "measurement_sites",
    "dt_seconds",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _identifier(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(_IDENTIFIER.fullmatch(value)), f"{label} needs a public identifier")
    _require(".." not in value.split("/"), f"{label} contains a parent path")
    return str(value)


def _number(value: Any, label: str, *, positive: bool = False) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be numeric")
    number = float(value)
    _require(math.isfinite(number), f"{label} must be finite")
    if positive:
        _require(number > 0, f"{label} must be positive")
    return number


def _count(value: Any, label: str) -> int:
    _require(type(value) is int and value > 0, f"{label} must be a positive integer")
    return int(value)


def _format_number(value: Any) -> str:
    return "n/a" if value is None else format(_number(value, "reported quantity"), ".12g")


def _portable_run_path(run_dir: Path) -> Path:
    """Use a checkout-relative destination when evidence comes from temporary storage."""
    repository = Path(__file__).resolve().parent.parent
    try:
        relative = run_dir.resolve().relative_to(repository)
    except ValueError:
        relative = Path("results/live") / run_dir.name
    _require(bool(relative.parts) and all(part not in (".", "..") for part in relative.parts), "invalid run location")
    for part in relative.parts:
        _identifier(part, "run path component")
    return relative


def _numeric_mapping(value: Any) -> Any:
    """Limit mapping output to public names and numeric calibration/placement data."""
    if isinstance(value, dict):
        return {_identifier(key, "mapping key"): _numeric_mapping(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_numeric_mapping(item) for item in value]
    if value is None:
        return None
    _number(value, "mapping value")
    return value


def _reproduction_arguments(record: dict[str, Any], location: Path) -> list[str]:
    policy = record["policy"]
    design = policy["design"]
    family = _identifier(design["family"], "family")
    _require(family == record["family_configuration"]["name"], "policy and family configuration differ")
    _require(type(design["optimize"]) is bool, "optimize must be Boolean")
    _require(not policy["twirl"] and policy["dd"] is None, "matched families require the unmitigated policy")
    inventory = record["system_inventory"]
    _require(isinstance(inventory, dict) and bool(inventory), "the case needs the complete known backend inventory")
    backends = sorted(_identifier(name, "backend") for name in inventory)
    _require(
        {group["backend"] for group in record["groups"]} <= set(backends), "selected backend is absent from inventory"
    )
    arguments = ["--family", family]
    if design["optimize"]:
        arguments.append("--optimize")
    arguments.extend(["--backends", ",".join(backends), "--shots", str(_count(record["shots"], "shots"))])
    for name in ("seeds", "max_pending", "min_remaining_seconds", "max_execution_seconds"):
        value = policy[name]
        _number(value, name)
        arguments.extend(["--" + name.replace("_", "-"), str(value)])
    for name in ("replica_floor", "max_replicas"):
        if policy[name] is not None:
            _number(policy[name], name, positive=True)
            arguments.extend(["--" + name.replace("_", "-"), str(policy[name])])
    for name in ("isolated_reference", "cross_group_buffer"):
        _require(type(policy[name]) is bool, f"{name} must be Boolean")
        arguments.append("--" + ("" if policy[name] else "no-") + name.replace("_", "-"))
    for name in _DESIGN_OPTIONS:
        value = design[name]
        if name in ("shot_tiers", "replica_tiers"):
            _require(isinstance(value, list) and bool(value), f"{name} must contain positive counts")
            argument = ",".join(str(_count(item, name)) for item in value)
        else:
            _number(value, name)
            argument = str(value)
        arguments.extend(["--" + name.replace("_", "-"), argument])
    arguments.extend(["--out", (Path("..") / location.parent).as_posix()])
    return arguments


def _command(arguments: list[str]) -> str:
    command = [
        "cd gororoba_quantum",
        'PYTHON="${PYTHON:-$(command -v python3)}"',
        '"$PYTHON" live_run.py \\',
    ]
    grouped: list[str] = []
    for token in arguments:
        if token.startswith("--"):
            grouped.append(shlex.quote(token))
        else:
            grouped[-1] += " " + shlex.quote(token)
    for index, option in enumerate(grouped):
        suffix = " \\" if index + 1 < len(grouped) else ""
        command.append("  " + option + suffix)
    return "\n".join(command)


def _validate_costs(candidate: dict[str, Any], record: dict[str, Any]) -> None:
    """Cross-check the selected cost ledger against its declared circuit workload."""
    policy = record["policy"]
    expected_shots = _count(record["shots"], "recorded shots")
    pub_names: list[str] = []
    job_names: list[str] = []
    for job in candidate["jobs"]:
        job_names.append(_identifier(job["name"], "job"))
        _require(bool(job["pubs"]), "selected job has no PUBs")
        overhead = _number(job["overhead_seconds"], "job overhead")
        _require(overhead >= 0, "job overhead must be nonnegative")
        _require(overhead == policy["design"]["job_overhead_seconds"], "job overhead differs from the design policy")
        executions = []
        for pub in job["pubs"]:
            pub_names.append(_identifier(pub["name"], "PUB"))
            _require(_count(pub["shots"], "PUB shots") == expected_shots, "PUB shots differ from the saved plan")
            durations = [
                _number(pub[key], key)
                for key in (
                    "scheduled_seconds",
                    "repetition_delay_seconds",
                    "reset_seconds",
                    "classical_latency_seconds",
                )
            ]
            _require(all(value >= 0 for value in durations), "PUB duration components must be nonnegative")
            expected = expected_shots * math.fsum(durations)
            _require(expected > 0, "PUB repetition duration must be positive")
            _require(
                math.isclose(expected, _number(pub["estimated_execution_seconds"], "PUB charge"), rel_tol=1e-12),
                "PUB estimated execution disagrees with its shots and durations",
            )
            executions.append(expected)
        charge = _number(job["estimated_charge_seconds"], "job charge", positive=True)
        _require(math.isclose(charge, math.fsum([overhead, *executions]), rel_tol=1e-12), "job charge sum disagrees")
        _require(charge <= job["max_execution_seconds"], "estimated job charge exceeds its service ceiling")
        _require(job["max_execution_seconds"] == policy["max_execution_seconds"], "job ceiling differs from policy")
    _require(len(job_names) == len(set(job_names)), "selected jobs must have distinct names")
    _require(len(pub_names) == len(set(pub_names)), "selected PUBs must have distinct names")
    _require(
        sorted(pub_names) == sorted(pub["name"] for pub in record["execution_pubs"]),
        "costed PUBs differ from the execution-PUB manifest",
    )
    _require(
        math.isclose(
            candidate["estimated_charge_seconds"],
            math.fsum(job["estimated_charge_seconds"] for job in candidate["jobs"]),
            rel_tol=1e-12,
        ),
        "candidate charge differs from its job sum",
    )


def _case_inputs(run_dir: Path, record: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    record_bytes = (run_dir / "record.json").read_bytes()
    retained = json.loads(record_bytes)
    _require(
        retained == json.loads(json.dumps(record, default=str)), "supplied record differs from retained record.json"
    )
    selected_name = record["optimization"]["selected"]
    candidates = [item for item in record["optimization"]["candidates"] if item["name"] == selected_name]
    _require(len(candidates) == 1 and candidates[0]["feasible"] is True, "selected candidate must be uniquely feasible")
    candidate = candidates[0]
    _identifier(selected_name, "selected candidate")
    _number(candidate["estimated_charge_seconds"], "estimated total charge", positive=True)
    ceiling = _number(candidate["total_execution_ceiling_seconds"], "summed execution ceilings", positive=True)
    _require(bool(candidate["jobs"]), "selected candidate has no jobs")
    _require(
        math.isclose(
            sum(_number(job["max_execution_seconds"], "job ceiling", positive=True) for job in candidate["jobs"]),
            ceiling,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        "selected job ceilings differ from their aggregate",
    )
    budget = record["budget_plan"]
    _require(
        math.isclose(ceiling, _number(budget["combined_ceiling_seconds"], "budget ceiling"), rel_tol=1e-12),
        "selected candidate and budget ledger disagree on summed ceilings",
    )
    _require(
        ceiling <= _number(budget["max_total_execution_seconds"], "invocation ceiling", positive=True),
        "summed ceilings exceed the invocation ceiling",
    )
    reserve = _number(budget["reserve_seconds"], "quota reserve")
    _require(reserve >= 0, "quota reserve must be nonnegative")
    for key in ("max_total_execution_seconds", "reserve_seconds"):
        _require(budget[key] == record["policy"]["design"][key], f"budget {key} differs from the design policy")
    if budget["remaining_seconds"] is not None:
        _require(
            ceiling + reserve <= _number(budget["remaining_seconds"], "remaining quota"),
            "summed ceilings consume the declared quota reserve",
        )
    _validate_costs(candidate, record)
    _require(
        bool(candidate["observables"]) and all(item["feasible"] is True for item in candidate["observables"]),
        "selected observables must all pass admission",
    )
    contract_names = [item["name"] for item in record["observable_contracts"]]
    _require(len(contract_names) == len(set(contract_names)), "endpoint contracts must have unique names")
    _require(
        contract_names == [item["name"] for item in candidate["observables"]],
        "endpoint contracts differ from selection",
    )
    archive_bytes = (run_dir / "isa.qpy").read_bytes()
    circuits = qpy.load(io.BytesIO(archive_bytes))
    _require(
        [circuit.name for circuit in circuits] == [pub["name"] for pub in record["execution_pubs"]],
        "QPY circuit names differ from the ordered execution-PUB manifest",
    )
    _require(bool(circuits), "the QPY archive has no execution circuits")
    return candidate, hashlib.sha256(record_bytes).hexdigest(), hashlib.sha256(archive_bytes).hexdigest()


def _endpoints(record: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    lines = [
        "## Preregistered endpoints",
        "",
        "Every endpoint uses raw measured outcomes and the archived score coefficients. "
        "The collection test uses the planned PUB grouping and the same one-sided detection "
        "radius; the two-sided interval describes precision separately.",
        "",
    ]
    contracts = {contract["name"]: contract for contract in record["observable_contracts"]}
    members = {member["name"]: member for group in record["groups"] for member in group["members"]}
    for endpoint in candidate["observables"]:
        name = _identifier(endpoint["name"], "endpoint")
        contract = contracts[name]
        lines.extend([f"### {name}", "", "Score terms (each member averages its recorded replicas):", ""])
        for term in contract["terms"]:
            member = _identifier(term["member"], "observable member")
            _require(member in members, "observable member is absent from the execution groups")
            _require(term["sign"] in (-1, 1), "observable sign must be -1 or +1")
            coefficients = [_number(value, "score coefficient") for value in term["values"]]
            _require(
                len(coefficients) == len(members[member]["ideal"]), "score labels differ from the member ideal law"
            )
            lines.append(f"- `{member}`: sign {term['sign']:+d}, labeled score vector `{json.dumps(coefficients)}`.")
        lines.extend(
            [
                "",
                f"The noise model predicts {_format_number(endpoint['predicted_value'])}; "
                "the simultaneous finite-simulation allowance is "
                f"+/-{_format_number(endpoint['simulation_error_radius'])}. "
                f"The lower modeled value is {_format_number(endpoint['modeled_value_lower_bound'])}.",
                "",
                f"At alpha {_format_number(endpoint['alpha'])}, the two-sided confidence half-width is "
                f"{_format_number(endpoint['confidence_half_width'])}; requested precision is "
                f"{_format_number(endpoint['precision_half_width'])}.",
            ]
        )
        if endpoint["minimum_effect"] is not None:
            threshold = _number(endpoint["null_value"], "null value") + _number(
                endpoint["detection_radius"], "detection radius"
            )
            lines.extend(
                [
                    "",
                    f"Reject the directional null only when the measured score exceeds {threshold:.12g} "
                    f"(null {_format_number(endpoint['null_value'])} plus one-sided radius "
                    f"{_format_number(endpoint['detection_radius'])}). The admitted alternative effect is "
                    f"{_format_number(endpoint['effect_used_for_power'])}, with conditional target power "
                    f"{_format_number(endpoint['power'])} and lower-tail radius "
                    f"{_format_number(endpoint['power_radius'])}. "
                    f"The requested minimum effect is {_format_number(endpoint['minimum_effect'])}.",
                ]
            )
            if endpoint["minimum_effect"] == 0:
                lines.extend(
                    [
                        "",
                        "Zero requested minimum effect selects the positive modeled contrast after the "
                        "simulation allowance. The power statement concerns that reported alternative, "
                        "rather than every arbitrarily small effect.",
                    ]
                )
        if endpoint.get("covariance_assumptions"):
            lines.extend(
                [
                    "",
                    "Additional covariance upper-bound assumptions appear in the selected endpoint's "
                    "`covariance_assumptions` in record.json and form part of the conditional guarantee.",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "The search-wide simulation error probability is "
            f"{_format_number(record['optimization']['simulation_alpha'])} "
            f"across {record['optimization']['simulation_comparisons']} scored finite-shot marginals. "
            "Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary "
            "repetitions remain an assumption. Endpoint alpha and power are conditional on the supplied "
            "outcome model; hardware-model discrepancy remains unquantified.",
            "",
        ]
    )
    return lines


def _scientific_case(family: str) -> list[str]:
    if family == "folded-qpe":
        return [
            "## Scientific question and interpretation",
            "",
            "The folded-QPE ladder measures terminal-bit contrasts for four supplied eigenstate labels. "
            "The archived arm, calibrated-delay arm, measurement-without-feedback arm, and coherent "
            "two-control arm expose distinct failures of the calibration-derived outcome model. "
            "The delay arm measures only its terminal bit; the supplied first-bit label is a preparation "
            "input. The other arms retain two measured bits with label index b0 + 2*b1.",
            "",
            "The delay replaces the compiled first measurement's duration, rounded to device granularity, "
            "retains reset, and uses the supplied eigenstate label for its unconditional correction. "
            "The intervention changes measurement and correction behavior together. Removing feedback "
            "changes some ideal laws. The coherent arm adds a control qubit and runs in a separate static "
            "job. Shared initial placement preserves the initial register assignment; coherent routing "
            "and terminal readout sites can differ. The archived mapping below records those confounds. "
            "A contrast therefore does not establish a unique gate-level cause.",
            "",
            "Noise simulation computes conditional predictions from Target/properties and declared "
            "latency assumptions. Only future hardware observations measure scheduler residuals, "
            "correlated errors, readout disturbance, and drift omitted by that model. Raw outcomes, "
            "scheduler metadata, calibration windows, and charged usage support the comparison.",
            "",
        ]
    return [
        "## Scientific question and interpretation",
        "",
        "The N=21, base-4 family measures the change in the labeled two-phase-bit distribution when "
        "feed-forward is removed. Array labels are 00, 01, 10, 11 (index b0 + 2*b1). The preregistered "
        "score is P(01)-P(11) with feedback, minus the same score without feedback. Two phase bits "
        "provide a feedback diagnostic; they do not establish successful general order recovery, "
        "factoring advantage, or an asymptotic speedup.",
        "",
        "Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, "
        "replica correlations, and calibration drift can change the contrast. Calibration-based Aer "
        "simulation supplies a conditional model and power admission. Future hardware observations "
        "measure the actual contrast and model residual. A failed directional test leaves the stated "
        "hardware distinction unresolved; the case does not convert a simulated power calculation "
        "into a measured hardware guarantee.",
        "",
    ]


def _render(
    record: dict[str, Any], candidate: dict[str, Any], location: Path, record_digest: str, qpy_digest: str
) -> str:
    family = record["family_configuration"]["name"]
    source = record["code_commit"]
    head = source["head"]
    _require(isinstance(head, str) and bool(re.fullmatch(r"[a-f0-9]{40,64}", head)), "source commit is unavailable")
    _require(type(source["sources_modified"]) is bool, "source cleanliness is unavailable")
    _require(bool(_HEX_DIGEST.fullmatch(record["experiment_digest"])), "experiment digest is invalid")
    arguments = _reproduction_arguments(record, location)
    lines = [
        f"# Unapproved QPU case: {family}",
        "",
        "Status: UNAPPROVED. The saved record describes a feasible "
        "submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.",
        "",
        f"The selected bounded-search candidate is `{_identifier(candidate['name'], 'candidate')}` at "
        f"{_count(record['shots'], 'shots')} shots per PUB. Global optimality remains outside the claim.",
        "",
        "## Artifact and source binding",
        "",
        f"- Saved run: `{location.as_posix()}`.",
        f"- [record.json](record.json) SHA-256: `{record_digest}`.",
        f"- [isa.qpy](isa.qpy) SHA-256: `{qpy_digest}`.",
        f"- Experiment source digest: `{record['experiment_digest']}`.",
        f"- Source commit: `{head}`; sources_modified=`{str(source['sources_modified']).lower()}`.",
        f"- Simulator seed: `{_count(record['seed_simulator'], 'simulator seed')}`; "
        "the source digest binds the simulator implementation.",
        "",
    ]
    if source["sources_modified"]:
        lines.extend(
            [
                "The source flag marks validation-only evidence from edited sources. The base commit "
                "alone cannot reproduce those edits; reproduction needs the exact source files bound "
                "by the experiment digest. A reviewed-source dry run supplies the release evidence.",
                "",
            ]
        )
    lines.extend(["Recorded dependency versions:", "", "| Dependency | Version |", "|---|---|"])
    for package, version in sorted(record["versions"].items()):
        lines.append(f"| {_identifier(package, 'package')} | {_identifier(version, 'version')} |")
    lines.append("")
    lines.extend(_scientific_case(family))
    lines.extend(
        [
            "## Archived ideal laws and placement",
            "",
            "The ideal arrays below come from the retained record. Their label order stays intact; "
            "sorting probabilities would discard the feedback distinction.",
            "",
            "| Member | Labeled ideal probabilities |",
            "|---|---|",
        ]
    )
    for group in record["groups"]:
        for member in group["members"]:
            name = _identifier(member["name"], "member")
            ideal = [_number(value, "ideal probability") for value in member["ideal"]]
            _require(
                all(0 <= value <= 1 for value in ideal) and math.isclose(sum(ideal), 1.0, abs_tol=1e-9),
                "invalid ideal law",
            )
            lines.append(f"| {name} | `{json.dumps(ideal)}` |")
    lines.extend(["", "| Group | Backend | Calibration | Transpiler seed | Initial layout |", "|---|---|---|---:|---|"])
    for group in record["groups"]:
        calibration = _identifier(group["calibration"], "calibration")
        lines.append(
            f"| {_identifier(group['group'], 'group')} | {_identifier(group['backend'], 'backend')} | "
            f"{calibration} | {_count(group['seed_transpiler'], 'transpiler seed')} | "
            f"`{json.dumps(_numeric_mapping(group['initial_layout']))}` |"
        )
    mappings = {
        key: _numeric_mapping(value) for key, value in record["family_configuration"].items() if key in _MAPPING_FIELDS
    }
    mappings["group_replica_mappings"] = {
        _identifier(group["group"], "group"): [_numeric_mapping(replica["mapping"]) for replica in group["replicas"]]
        for group in record["groups"]
    }
    lines.extend(
        ["", "Calibration-bound family and replica mapping:", "", "```json", json.dumps(mappings, indent=2), "```", ""]
    )
    lines.extend(_endpoints(record, candidate))
    budget = record["budget_plan"]
    lines.extend(
        [
            "## Expected charge and service ceilings",
            "",
            "| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for job in candidate["jobs"]:
        pub_shots = sum(_count(pub["shots"], "PUB shots") for pub in job["pubs"])
        lines.append(
            f"| {_identifier(job['name'], 'job')} | {len(job['pubs'])} | {pub_shots} | "
            f"{_format_number(job['estimated_charge_seconds'])} | {_format_number(job['max_execution_seconds'])} |"
        )
    lines.extend(
        [
            "",
            f"The cost model predicts {_format_number(candidate['estimated_charge_seconds'])} seconds. "
            "The per-job service ceilings sum to "
            f"{_format_number(candidate['total_execution_ceiling_seconds'])} seconds "
            f"against an invocation cap of {_format_number(budget['max_total_execution_seconds'])} seconds. "
            f"The global reserve is {_format_number(budget['reserve_seconds'])} seconds; the saved quota "
            f"reports {_format_number(budget['remaining_seconds'])} seconds remaining.",
            "",
            "Every PUB cost includes its Target duration, explicit repetition delay, and "
            "declared reset/classical-latency additions. Each job also includes its declared fixed "
            "overhead. Those model assumptions estimate charge; the ceilings bound service execution "
            "instead. The ledger retains accepted and attempted jobs' reservations while their charges "
            "remain unsettled. External submissions can still change the shared quota. Dynamic Target "
            "duration omits classical scheduler latency; the declared addition remains a planning assumption.",
            "",
            "| PUB | Shots | Target duration (s) | Repetition delay (s) | "
            "Reset addition (s) | Classical latency addition (s) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for job in candidate["jobs"]:
        for pub in job["pubs"]:
            lines.append(
                f"| {_identifier(pub['name'], 'PUB')} | {_count(pub['shots'], 'PUB shots')} | "
                f"{_format_number(pub['scheduled_seconds'])} | {_format_number(pub['repetition_delay_seconds'])} | "
                f"{_format_number(pub['reset_seconds'])} | {_format_number(pub['classical_latency_seconds'])} |"
            )
        lines.extend(
            [
                "",
                f"Job `{_identifier(job['name'], 'job')}` adds "
                f"{_format_number(job['overhead_seconds'])} seconds of modeled overhead.",
                "",
            ]
        )
    lines.extend(
        [
            "The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) "
            "defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace "
            "each job's execution ceiling. Actual charge comes from completed job usage.",
            "",
            "## Reproduce the dry run",
            "",
            "Run from the repository root with the recorded dependency versions and source digest. "
            "The command pins every backend in the saved discovery inventory, preserving the known "
            "candidate universe. The runner refreshes calibration and queue admission, so a changed "
            "backend can produce a different case. The transpiler seed count and simulator seed "
            "retain their recorded meanings.",
            "",
            "```sh",
            _command(arguments),
            "```",
            "",
            "## Approval-only submission template",
            "",
            "Execute the following command only after the owner explicitly approves this concrete "
            "case and its ceilings. Keep the complete saved run at the repository-relative location "
            "above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. "
            "The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence "
            "with the approved record, consumes its approval once, and stops for renewed approval when "
            "the comparison changes.",
            "",
            "```sh",
            _command(
                [
                    *arguments,
                    "--approved-record",
                    (Path("..") / location).as_posix(),
                    "--approved-record-sha256",
                    record_digest,
                    "--submit",
                ]
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_case(run_dir: Path, record: dict[str, Any]) -> Path | None:
    """Write an unapproved case only for an admitted family dry-run artifact pair."""
    family = record.get("family_configuration", {}).get("name")
    if family not in FAMILIES or record.get("state") != "planned":
        return None
    if (
        record.get("budget_plan", {}).get("admitted") is not True
        or record.get("optimization", {}).get("selected") is None
        or record.get("submission")
        or record.get("approval_consumed")
        or (run_dir / "approval-consumed.json").exists()
    ):
        return None
    candidate, record_digest, qpy_digest = _case_inputs(run_dir, record)
    text = _render(record, candidate, _portable_run_path(run_dir), record_digest, qpy_digest)
    destination = run_dir / CASE_FILENAME
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=run_dir, prefix=".qpu-case-", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return destination


def _fixture() -> dict[str, Any]:
    """Minimal retained-record schema for artifact and command regression checks."""
    pub = dict(
        name="feedback_pub",
        shots=2048,
        scheduled_seconds=0.001,
        repetition_delay_seconds=0.00025,
        reset_seconds=0.0,
        classical_latency_seconds=0.00002,
        estimated_execution_seconds=2.60096,
    )
    endpoint = dict(
        name="feedback_contrast",
        feasible=True,
        predicted_value=0.25,
        simulation_error_radius=0.01,
        modeled_value_lower_bound=0.24,
        confidence_half_width=0.07,
        precision_half_width=None,
        minimum_effect=0.0,
        null_value=0.0,
        detection_radius=0.06,
        effect_used_for_power=0.24,
        power=0.8,
        power_radius=0.04,
        alpha=0.05,
        covariance_assumptions=[],
    )
    design = dict(
        family="n21-feedback",
        optimize=True,
        shot_tiers=[2048, 4096],
        replica_tiers=[1, 2],
        optimizer_candidates=3,
        model_shots=32768,
        precision=0.08,
        alpha=0.05,
        power=0.8,
        simulation_alpha=0.01,
        job_overhead_seconds=2.3,
        classical_latency_us=20.0,
        reserve_seconds=10.0,
        max_total_execution_seconds=90.0,
    )
    return dict(
        state="planned",
        family_configuration={"name": "n21-feedback", "replica_cap": 1},
        shots=2048,
        seed_simulator=7,
        experiment_digest="a" * 64,
        code_commit={"head": "b" * 40, "sources_modified": False},
        versions={"numpy": "2.5.4+local"},
        system_inventory={"ibm_fez": {}, "ibm_kingston": {}},
        policy=dict(
            design=design,
            twirl=False,
            dd=None,
            seeds=2,
            max_pending=25,
            min_remaining_seconds=60.0,
            max_execution_seconds=90,
            replica_floor=None,
            max_replicas=None,
            isolated_reference=True,
            cross_group_buffer=True,
        ),
        execution_pubs=[{"name": "feedback_pub"}],
        observable_contracts=[
            dict(name="feedback_contrast", terms=[dict(member="feedback", sign=1, values=[0.0, 1.0])])
        ],
        optimization=dict(
            selected="candidate-000-shots-2048",
            simulation_alpha=0.01,
            simulation_comparisons=4,
            candidates=[
                dict(
                    name="candidate-000-shots-2048",
                    feasible=True,
                    estimated_charge_seconds=4.90096,
                    total_execution_ceiling_seconds=90.0,
                    observables=[endpoint],
                    jobs=[
                        dict(
                            name="ibm_fez/dynamic/1",
                            pubs=[pub],
                            overhead_seconds=2.3,
                            estimated_charge_seconds=4.90096,
                            max_execution_seconds=90,
                        )
                    ],
                )
            ],
        ),
        budget_plan=dict(
            admitted=True,
            combined_ceiling_seconds=90.0,
            max_total_execution_seconds=90.0,
            reserve_seconds=10.0,
            remaining_seconds=591.0,
        ),
        groups=[
            dict(
                group="feedback_group",
                backend="ibm_fez",
                calibration="2026-10-11T12:00:00+00:00",
                seed_transpiler=7,
                initial_layout=[0],
                replicas=[{"mapping": {"0": 0}}],
                members=[dict(name="feedback", ideal=[0.5, 0.5])],
            )
        ],
    )


def _verify() -> None:
    record = _fixture()
    with tempfile.TemporaryDirectory(prefix="qpu-case-check-") as temporary:
        run_dir = Path(temporary) / "retained-run"
        run_dir.mkdir()
        circuit = QuantumCircuit(1, 1, name="feedback_pub")
        circuit.measure(0, 0)
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuit, handle)

        def retain(value: dict[str, Any]) -> None:
            (run_dir / "record.json").write_text(json.dumps(value, indent=2) + "\n")

        retain(record)
        originals = {name: (run_dir / name).read_bytes() for name in ("record.json", "isa.qpy")}
        destination = write_case(run_dir, record)
        assert destination is not None
        text = destination.read_text()
        assert "UNAPPROVED" in text and "--approved-record-sha256" in text
        assert hashlib.sha256(originals["record.json"]).hexdigest() in text
        assert hashlib.sha256(originals["isa.qpy"]).hexdigest() in text
        assert "--backends ibm_fez,ibm_kingston" in text
        assert "--shot-tiers 2048,4096" in text
        assert "2026-10-11T12:00:00+00:00" in text and "2.5.4+local" in text
        assert "exceeds 0.06" in text and "conditional target power 0.8" in text
        assert str(run_dir) not in text and "crn:" not in text
        assert "--submit" not in text.split("## Approval-only submission template")[0]
        assert write_case(run_dir, record) == destination and destination.read_text() == text
        assert all((run_dir / name).read_bytes() == value for name, value in originals.items())
        for state in ("design_infeasible", "budget_infeasible", "submitted", "approval_required"):
            changed = copy.deepcopy(record)
            changed["state"] = state
            assert write_case(run_dir, changed) is None
            assert destination.read_text() == text
        assert write_case(run_dir, {"state": "planned"}) is None
        for key in ("submission", "approval_consumed"):
            changed = copy.deepcopy(record)
            changed[key] = {"present": True}
            assert write_case(run_dir, changed) is None
        consumed = run_dir / "approval-consumed.json"
        consumed.write_text("{}\n")
        assert write_case(run_dir, record) is None
        consumed.unlink()
        folded = copy.deepcopy(record)
        folded["family_configuration"] = {
            "name": "folded-qpe",
            "measurement_delay_dt": {"1": 1600},
            "replaced_measurement_qubits": {"1": 3},
            "shared_initial_layout": [0, 1],
            "extra_control": 2,
            "measurement_seconds": {"1": 0.000004},
            "measurement_sites": {"feedback": [[3], [4]]},
            "dt_seconds": 2.5e-9,
        }
        folded["policy"]["design"]["family"] = "folded-qpe"
        folded_endpoint = folded["optimization"]["candidates"][0]["observables"][0]
        folded_endpoint.update(minimum_effect=None, precision_half_width=0.08)
        retain(folded)
        assert write_case(run_dir, folded) == destination
        folded_text = destination.read_text()
        assert "calibrated-delay arm" in folded_text and "measurement_sites" in folded_text
        assert "coherent routing and terminal readout sites can differ" in folded_text
        assert "--family folded-qpe" in folded_text and "requested precision is 0.08" in folded_text
        assert "Reject the directional null" not in folded_text
        changed = copy.deepcopy(record)
        changed["code_commit"]["sources_modified"] = True
        retain(changed)
        assert write_case(run_dir, changed) == destination
        assert "validation-only evidence from edited sources" in destination.read_text()
        retain(record)
        changed = copy.deepcopy(record)
        changed["shots"] = 4096
        try:
            write_case(run_dir, changed)
        except ValueError as error:
            assert "retained record.json" in str(error)
        else:
            raise AssertionError("case writer accepts mismatched in-memory record")
        changed = copy.deepcopy(record)
        changed["budget_plan"]["combined_ceiling_seconds"] = 180
        retain(changed)
        try:
            write_case(run_dir, changed)
        except ValueError as error:
            assert "budget ledger" in str(error)
        else:
            raise AssertionError("case writer accepts an inconsistent aggregate budget")
        for field, invalid_budget, expected_error in (
            ("remaining_seconds", 95.0, "quota reserve"),
            ("reserve_seconds", 9.0, "design policy"),
        ):
            changed = copy.deepcopy(record)
            changed["budget_plan"][field] = invalid_budget
            retain(changed)
            try:
                write_case(run_dir, changed)
            except ValueError as error:
                assert expected_error in str(error)
            else:
                raise AssertionError(f"case writer accepts inconsistent {field}")
        for field, invalid_pub, expected_error in (
            ("shots", 1024, "PUB shots"),
            ("name", "different_pub", "costed PUBs"),
            ("estimated_execution_seconds", 0.1, "estimated execution"),
        ):
            changed = copy.deepcopy(record)
            changed["optimization"]["candidates"][0]["jobs"][0]["pubs"][0][field] = invalid_pub
            retain(changed)
            try:
                write_case(run_dir, changed)
            except ValueError as error:
                assert expected_error in str(error)
            else:
                raise AssertionError(f"case writer accepts inconsistent PUB {field}")
        retain(record)
        circuit.name = "different_pub"
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuit, handle)
        try:
            write_case(run_dir, record)
        except ValueError as error:
            assert "ordered execution-PUB manifest" in str(error)
        else:
            raise AssertionError("case writer accepts a different QPY manifest")
    print("QPU cases: artifact and cost binding, both families, relative commands, and refusal checks pass")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true", help="run credential-free case-writer regression checks")
    args = parser.parse_args(argv)
    if args.check:
        _verify()
        return 0
    if args.run_dir is None:
        parser.error("supply a retained run directory or --check")
    record = json.loads((args.run_dir / "record.json").read_text())
    destination = write_case(args.run_dir, record)
    if destination is None:
        print("The saved record supplies no admitted family dry-run case.")
        return 0
    print(f"Written {destination.name}; status UNAPPROVED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
