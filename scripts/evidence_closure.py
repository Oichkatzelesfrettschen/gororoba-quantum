"""Read-only, commit-pinned evidence reconciliation; never a second registry.

No provider client is imported. Missing denominators are null, not zero.
The authoritative registry and historical evidence remain unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

DEST = ROOT / "docs/evidence/evidence-closure"
PRODUCER_DIGEST = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
FIELDS = ("planned_observations", "submitted_shot_ceiling", "provider_reported_shots", "returned_samples")
CLASSIFICATION = {
    "exact finite certificate": "exact finite result",
    "mathematical claim": "externally/repository proved statement; proof origin retained",
    "machine-checked proof": "kernel-checked statement; receipt scope retained",
    "numerical or stochastic simulation": "simulation result",
    "circuit-conformance check": "ideal circuit-conformance result",
    "preregistered hardware inference": "named-acquisition hardware inference",
    "preregistered emulator control": "emulator control (not hardware)",
    "exploratory reanalysis": "exploratory analysis (not confirmation)",
    "proposed experiment": "proposal (not a result)",
    "withdrawn claim": "withdrawn",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


class Tree:
    def __init__(self, pin: str):
        require(bool(re.fullmatch(r"[0-9a-f]{40}", pin)), "A source pin must be a full commit SHA")
        require(git("rev-parse", f"{pin}^{{commit}}").decode().strip() == pin, "Source commit unavailable")
        self.pin = pin
        self.files: dict[str, str] = {}
        for row in git("ls-tree", "-r", "-z", pin).split(b"\0"):
            if row:
                meta, path = row.split(b"\t", 1)
                if meta.split()[1] == b"blob":
                    self.files[path.decode()] = meta.split()[2].decode()
        self.inputs: dict[str, dict[str, str]] = {}
        self.reader = subprocess.Popen(
            ["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def read(self, path: str) -> Any:
        require(path in self.files, f"{self.pin}:{path}: missing pinned input")
        if self.reader.stdin is None or self.reader.stdout is None:
            raise ValueError("Git object stream unavailable")
        self.reader.stdin.write((self.files[path] + "\n").encode())
        self.reader.stdin.flush()
        header = self.reader.stdout.readline().split()
        require(len(header) == 3 and header[1] == b"blob", f"{path}: missing Git blob")
        size = int(header[2])
        raw = self.reader.stdout.read(size)
        require(len(raw) == size and self.reader.stdout.read(1) == b"\n", f"{path}: truncated Git blob")
        self.inputs[path] = {"git_blob": self.files[path], "sha256": sha(raw)}
        return json.loads(raw)

    def optional(self, path: str) -> Any:
        return self.read(path) if path in self.files else None

    def close(self) -> None:
        if self.reader.stdin:
            self.reader.stdin.close()
        if self.reader.stdout:
            self.reader.stdout.close()
        require(self.reader.wait() == 0, "Git object reader failed")


def count_histogram(counts: Any) -> int | None:
    if not isinstance(counts, dict) or not counts:
        return None
    if not all(isinstance(n, int) and not isinstance(n, bool) and n >= 0 for n in counts.values()):
        return None
    return sum(counts.values())


def classify_record(record: dict[str, Any], collection_present: bool) -> dict[str, Any]:
    submission = record.get("submission") or {}
    jobs = [str(j["job_id"]) for j in submission.get("jobs", []) if j.get("job_id")]
    state = record.get("state")
    if jobs:
        category = "completed or failed execution" if collection_present else "dispatched with a provider identity"
    elif submission:
        category = "ambiguously dispatched" if submission.get("started") else "approved but not submitted"
    elif state in {"design_infeasible", "budget_infeasible"}:
        category = "infeasible before dispatch"
    elif state == "planned":
        category = "planning-only"
    elif state == "approval_required":
        category = "planning-only"
    elif record.get("qpu_execution") is False or record.get("evidence_kind"):
        category = "analysis-only or successor artifact"
    else:
        category = "unresolved"
    return {
        "classification": category,
        "state": state,
        "job_ids": jobs,
        "submission_field_present": "submission" in record,
        "reason": (
            "Classification uses explicit record fields; absence of a submission is not "
            "proof of no historical execution."
        ),
    }


def one_photon_exclusions(counts: dict[str, int]) -> dict[str, int]:
    categories: Counter[str] = Counter()
    for state, n in counts.items():
        if not re.fullmatch(r"[0-9]+(?:,[0-9]+)*", state):
            categories["unparsed_outcome"] += n
            continue
        photons = sum(int(x) for x in state.split(","))
        categories["vacuum" if photons == 0 else "single_photon" if photons == 1 else "multi_photon"] += n
    return dict(sorted(categories.items()))


def quantum_inspire(tree: Tree, run: str, acquisition: dict[str, Any]) -> list[dict[str, Any]]:
    sub = tree.optional(run + "/submission.json")
    result = tree.optional(run + "/results.json")
    if not sub or not result:
        return []
    returned = {str(r["job"]["id"]): r for r in result["jobs"]}
    rows = []
    for item in sub["jobs"]:
        identity = str(item["job"])
        observation = returned.get(identity, {})
        job = observation.get("job", {})
        if job:
            require(job.get("number_of_shots") == sub.get("shots"), f"{run}: requested shot identity differs")
        results = observation.get("results") or []
        done = [r.get("shots_done") for r in results]
        samples = [count_histogram(r.get("results")) for r in results]
        row = {
            "provider": "quantum_inspire",
            "job_id": identity,
            "backend": sub.get("backend"),
            "execution_kind": "hardware" if sub.get("backend") == "tuna_17" else "emulator or unqualified backend",
            "status": job.get("status", "unobserved"),
            "session": job.get("session_id"),
            "calibration": None,
            "compilation": None,
            "requested_program_git_blob": tree.files.get(run + "/" + item["file"]),
            "preparations": None,
            "planned_observations": 1,
            "submitted_shot_ceiling": sub.get("shots"),
            "provider_reported_shots": sum(done) if done and all(isinstance(n, int) for n in done) else None,
            "returned_samples": sum(n for n in samples if n is not None)
            if samples and all(isinstance(n, int) for n in samples)
            else None,
            "eligible_outcomes": None,
            "exclusions": None,
            "processing_boundary": (
                "Returned integer histograms are service observations; raw-trial likelihood is "
                "not inferred from integer counts."
            ),
            "acquisition_id": acquisition["id"],
            "run": run,
            "source_paths": [run + "/submission.json", run + "/results.json"],
        }
        rows.append(row)
    return rows


def quandela(tree: Tree, run: str, acquisition: dict[str, Any]) -> list[dict[str, Any]]:
    sub = tree.optional(run + "/submission.json")
    result = tree.optional(run + "/results.json")
    case = tree.optional(run + "/cases.json")
    if not sub or not result:
        return []
    require(str(result.get("job_id")) == str(sub["job_id"]), f"{run}: submission/result job identities differ")
    counts = result.get("counts") or {}
    iterations = result.get("iterations") or []
    shots_used = result.get("shots_used")
    # qd_platform explicitly distinguishes top-level per-iteration max_shots
    # from the sum of nb_shots_used. Never sum or multiply the former.
    if iterations and shots_used is None:
        parts = [i.get("result_fields", {}).get("nb_shots_used") for i in iterations]
        if parts and all(isinstance(n, int) and n >= 0 for n in parts):
            shots_used = sum(parts)
    status = result.get("status") or {}
    settings = (case or {}).get("settings") or []
    return [
        {
            "provider": "quandela",
            "job_id": str(sub["job_id"]),
            "backend": sub.get("platform"),
            "execution_kind": "hardware"
            if str(sub.get("platform", "")).startswith("qpu:")
            else "simulator or unqualified backend",
            "status": status.get("status", "unobserved"),
            "session": None,
            "calibration": None,
            "compilation": None,
            "preparations": sorted({str(s.get("preparation")) for s in settings if s.get("preparation")}),
            "planned_observations": (case or {}).get("iterations", 1),
            "submitted_shot_ceiling": sub.get("max_shots"),
            "provider_reported_shots": shots_used,
            "provider_top_level_shots_not_a_total": result.get("shots"),
            "returned_samples": count_histogram(counts),
            "eligible_outcomes": None,
            "outcome_categories": one_photon_exclusions(counts),
            "exclusions": None,
            "processing_boundary": (
                "Outcome categories are diagnostic partitions, not exclusions from an "
                "unspecified estimator. Missing mitigation policy is not an explicit empty "
                "list."
            ),
            "acquisition_id": acquisition["id"],
            "run": run,
            "source_paths": [run + "/submission.json", run + "/results.json", run + "/cases.json"],
        }
    ]


def load_snapshot(source: dict[str, str]) -> dict[str, Any]:
    tree = Tree(source["commit"])
    registry = tree.read("docs/state/research_state.json")
    acquisitions = registry["acquisitions"]
    rows = []
    for acq in acquisitions:
        if acq["provider"] == "quantum_inspire":
            rows.extend(quantum_inspire(tree, acq["run"], acq))
        elif acq["provider"] == "quandela":
            rows.extend(quandela(tree, acq["run"], acq))
    retention = tree.read("results/live/qpu-job-retention-audit.json")
    inventories = [
        tree.read(path)
        for path in sorted(tree.files)
        if re.fullmatch(r"results/live/qpu-job-inventory(?:\.[^/]+)?\.json", path)
    ]
    service = {j["job_id"]: j for inventory in inventories for j in inventory["jobs"]}
    by_run = {a["run"]: a["id"] for a in acquisitions if a["provider"] == "ibm"}
    for item in retention["jobs"]:
        job = service.get(item["job_id"], {})
        run = item["run"]
        pub_counts = []
        for path in item.get("source_files", {}):
            if re.search(r"/pub_\d+\.json$", path):
                pub = tree.read(path)
                lengths = {len(v["bitstrings"]) for v in pub.get("registers", {}).values() if "bitstrings" in v}
                require(len(lengths) <= 1, f"{path}: register shot counts disagree")
                if lengths:
                    pub_counts.append(next(iter(lengths)))
        ceiling = item.get("submitted_pub_shots")
        if ceiling is None and isinstance(job.get("pub_count"), int) and isinstance(job.get("shots_per_pub"), int):
            ceiling = job["pub_count"] * job["shots_per_pub"]
        rows.append(
            {
                "provider": "ibm",
                "job_id": item["job_id"],
                "backend": item.get("backend"),
                "execution_kind": "hardware",
                "status": job.get("status", "unobserved"),
                "session": None,
                "calibration": None,
                "compilation": tree.files.get(run + "/isa.qpy"),
                "preparations": None,
                "planned_observations": job.get("pub_count"),
                "submitted_shot_ceiling": ceiling,
                "provider_reported_shots": None,
                "returned_samples": sum(pub_counts) if pub_counts else None,
                "eligible_outcomes": None,
                "exclusions": None,
                "processing_boundary": (
                    "Returned samples count PUB-shot records once per PUB, never once per "
                    "classical register or replica. Requested shots are not completed shots."
                ),
                "acquisition_id": by_run.get(run),
                "run": run,
                "source_paths": ["results/live/qpu-job-retention-audit.json", *item.get("source_files", {})],
            }
        )
    records = []
    for path in sorted(tree.files):
        if re.fullmatch(r"results/live/[^/]+/record\.json", path) and str(Path(path).parent) not in by_run:
            record = tree.read(path)
            records.append(
                {
                    "path": path,
                    "git_blob": tree.files[path],
                    **classify_record(record, str(Path(path).parent / "collect.json") in tree.files),
                }
            )
    # The ledger's cross-branch identities are a coverage question, not a new execution.
    ledger = tree.read("docs/evidence/quantum_inspire/usage.json")
    contrasts = {}
    visibility_path = "results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json"
    if visibility_path in tree.files:
        contrasts["tuna_visibility"] = raw_visibility_sensitivity(tree.read(visibility_path)["replicas"])
    readout_path = "results/hypercomplex/belenos-repeat-readout.json"
    if readout_path in tree.files:
        readout = tree.read(readout_path)
        audit_path = "results/hypercomplex/belenos-compilation-measurement-audit.json"
        audit = tree.optional(audit_path)
        contrasts["fourier_mismatch"] = fourier_recheck(readout["observations"], audit)
        for row in rows:
            observations = [
                o
                for o in readout["observations"]
                if str(o["job_id"]) == row["job_id"] and row["provider"] == "quandela"
            ]
            if observations:
                row["estimator_denominators"] = {
                    "estimator": "retained one-photon per-mode diagnostic",
                    "eligible_outcomes": sum(o["eligible_samples"] for o in observations),
                    "excluded_outcomes": sum(o["excluded_samples"] for o in observations),
                    "categories": {
                        key: sum(o[key] for o in observations) for key in ["vacuum_samples", "multiple_click_samples"]
                    },
                    "source": readout_path,
                }
                row["returned_compilation_identities"] = sorted({o["computed_circuit_sha256"] for o in observations})
        case_path = "results/hypercomplex/photonic-successors/belenos/transform-repeat-block-0/cases.json"
        if case_path in tree.files:
            contrasts["fourier_candidate"] = fourier_candidate(tree.read(case_path), readout["observations"], source)
    tree.close()
    return {
        "source": source,
        "schema": registry["schema"],
        "claims": registry["claims"],
        "acquisitions": acquisitions,
        "observations": rows,
        "unbound_ibm_records": records,
        "declared_unretained_qi": ledger.get("unretained", []),
        "inputs": tree.inputs,
        "ibm_budget_observation": retention["account_usage_observation"],
        "numerical_rechecks": contrasts,
    }


def raw_visibility_sensitivity(replicas: list[dict[str, Any]]) -> dict[str, Any]:
    def estimate(rows: list[dict[str, Any]]) -> float | None:
        probabilities = {}
        for case in ("dark", "bright"):
            selected = [r for r in rows if r["case"] == case]
            n = sum(r["shots"] for r in selected)
            if not n:
                return None
            probabilities[case] = sum(r["selector_zero_count"] for r in selected) / n
        return probabilities["bright"] - probabilities["dark"]

    return {
        "estimand": "raw pooled bright-minus-dark selector fraction",
        "full": estimate(replicas),
        "leave_one_compiled_job_out": [
            {"file": name, "raw_contrast": estimate([r for r in replicas if r["file"] != name])}
            for name in sorted({r["file"] for r in replicas})
        ],
        "boundary": (
            "A Latin file is one shared-shot job, so every case score from it is removed "
            "together. This descriptive raw contrast does not re-adjudicate the "
            "preregistered contraction test or calibration model."
        ),
    }


def tv(first: list[float], second: list[float]) -> float:
    require(len(first) == len(second) and bool(first), "Probability vectors need equal nonzero length")
    require(all(math.isfinite(p) and p >= 0 for p in first + second), "Probability vector is invalid")
    require(abs(sum(first) - 1) < 1e-9 and abs(sum(second) - 1) < 1e-9, "Probability vector is not normalized")
    return 0.5 * sum(abs(a - b) for a, b in zip(first, second, strict=True))


def fourier_recheck(observations: list[dict[str, Any]], audit: dict[str, Any] | None = None) -> dict[str, Any]:
    job = "e99c049c-b9c1-4663-bbd0-e57e59bb6993"
    ordered = {o["observation_index"]: o for o in observations if o["job_id"] == job}
    rows = []
    for index in (6, 14, 22):
        if index not in ordered:
            continue
        target = ordered[index]
        previous = ordered[index - 1]
        n = sum(target["mode_counts"])
        require(n == target["eligible_samples"] and n > 0, "Fourier eligible denominator differs")
        observed = [count / n for count in target["mode_counts"]]
        record = {
            "observation_index": index,
            "setting": target["setting"],
            "job_id": job,
            "eligible_samples": n,
            "excluded_samples": target["excluded_samples"],
            "computed_circuit_sha256": target["computed_circuit_sha256"],
            "tv_observed_requested": tv(observed, target["expected_mode_probabilities"]),
            "tv_observed_predecessor_requested": tv(observed, previous["expected_mode_probabilities"]),
            "observed": observed,
            "requested": target["expected_mode_probabilities"],
            "predecessor_requested": previous["expected_mode_probabilities"],
        }
        served = next(
            (r for r in (audit or {}).get("rows", []) if r["job_id"] == job and r["observation_index"] == index), None
        )
        record["tv_returned_requested"] = (
            tv(served["compiled_mode_probabilities"], target["expected_mode_probabilities"]) if served else None
        )
        record["tv_observed_returned"] = tv(observed, served["compiled_mode_probabilities"]) if served else None
        rows.append(record)
    return {
        "rows": rows,
        "boundary": (
            "Count-level recheck of retained readout mode_counts and requested "
            "probabilities, not a full provider-response replay. Predecessor resemblance "
            "does not identify causation."
        ),
    }


def fourier_candidate(
    case: dict[str, Any], observations: list[dict[str, Any]], source: dict[str, str]
) -> dict[str, Any]:
    job = "e99c049c-b9c1-4663-bbd0-e57e59bb6993"
    bank = {o["observation_index"]: o for o in observations if o["job_id"] == job}
    target = case["settings"][6]
    require(
        target["name"].startswith("transform-forward-imaginary-superposition-representative0-"),
        "Candidate target identity changed",
    )
    controls = [2, 3, 0, 1]
    separation = min(
        tv(bank[a]["expected_mode_probabilities"], bank[b]["expected_mode_probabilities"])
        for i, a in enumerate(controls)
        for b in controls[i + 1 :]
    )
    require(separation >= 0.5, "Predecessors are not distinguishable")
    n, distributions, alpha = 40000, 18, 0.05
    radius = math.sqrt((24 * math.log(2) + math.log(distributions / alpha)) / (2 * n))
    return {
        "schema": "fourier-history-candidate-v1",
        "status": "draft; not admitted; no submission authorization",
        "source": source,
        "target_setting": target,
        "target_setting_sha256": sha(canonical(target).encode()),
        "historical_target_compiled_sha256": bank[6]["computed_circuit_sha256"],
        "predecessor_settings": [case["settings"][i] for i in controls],
        "minimum_requested_predecessor_tvd": separation,
        "invocation_orders": [controls + [None], [None] + list(reversed(controls))],
        "target_slot_with_predecessor": 1,
        "static_control_boundary": (
            "Target-only means no preceding iteration in that invocation, not a reset of "
            "provider history; its payload-form difference is a control limitation."
        ),
        "planning_sensitivity_only": {
            "eligible_events_per_setting": n,
            "simultaneous_distributions": distributions,
            "family_alpha": alpha,
            "iid_multinomial_tvd_radius": radius,
            "two_empirical_distribution_radius": 2 * radius,
            "minimum_relevant_history_tvd": 0.1,
            "bound": (
                "Union bound over all 2^24 subsets and 18 empirical laws: epsilon=sqrt((24 ln 2 + ln(18/alpha))/(2n))."
            ),
            "qualification": (
                "Conditional planning calculation only. Independence, physical trials, "
                "processing and effective n remain unqualified."
            ),
        },
        "stop_rules": [
            (
                "Stop on any target parameter/seed/returned-compilation change, incomplete "
                "result, unknown effective policy or invalid control."
            ),
            (
                "Support history dependence only when a simultaneous lower bound on a "
                "counterbalanced target difference exceeds 0.1 and predecessors themselves "
                "respond distinctly."
            ),
            (
                "Support a stable setting-specific wrong response only when simultaneous "
                "upper bounds are below 0.1 across distinct predecessors and the "
                "wrong-target response persists."
            ),
            "Otherwise close inconclusive within the written budget; never retry automatically.",
        ],
        "admission_blockers": [
            "Physical observation chain and effective sample size unqualified.",
            "Fresh target-compilation identity and applied-control availability unverified.",
            "Current seconds/credits/shot ceilings and reserve not priced or approved.",
            "Target-only versus paired payload form remains a stated confound.",
            "Independent user approval of a fully written executable case is absent.",
        ],
        "scope": (
            "Distinguishes predecessor dependence from target invariance; cannot "
            "distinguish stale controls from result association without provider-side "
            "evidence."
        ),
    }


def consensus(observations: list[dict[str, Any]], field: str) -> dict[str, Any]:
    known = {canonical(o[field]): o[field] for o in observations if o.get(field) is not None}
    return {
        "value": next(iter(known.values())) if len(known) == 1 else None,
        "status": "unavailable"
        if not known
        else "agreed available observations"
        if len(known) == 1
        else "conflicting observations",
        "missing_observations": sum(o.get(field) is None for o in observations),
        "alternatives": list(known.values()) if len(known) > 1 else [],
    }


def reconcile(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    jobs: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    claim_versions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for snap in snapshots:
        for row in snap["observations"]:
            jobs[row["provider"], row["job_id"]].append({**row, "source": snap["source"], "schema": snap["schema"]})
        for claim in snap["claims"]:
            claim_versions[claim["id"]].append({"source": snap["source"], "claim": claim})
    claims: list[dict[str, Any]] = []
    conflicts = []
    for identity, variants in sorted(claim_versions.items()):
        semantic_fields = (
            "statement",
            "status",
            "evidence_class",
            "boundary",
            "acquisitions",
            "depends_on",
            "assumptions",
        )
        semantics = {canonical({k: v["claim"].get(k) for k in semantic_fields}) for v in variants}
        classification = "claim conflict" if len(semantics) > 1 else "same declared semantics"
        if len(semantics) > 1:
            conflicts.append(
                {
                    "claim": identity,
                    "reason": (
                        "Pinned branches disagree in declared scope/status/support; no latest-wins "
                        "adjudication applied."
                    ),
                }
            )
        claims.append({"id": identity, "classification": classification, "variants": variants})
    identities = []
    unresolved = list(conflicts)
    for (provider, identity), observations in sorted(jobs.items()):
        labels = []
        if len({o["run"] for o in observations}) > 1:
            labels.append("multi-location execution")
        if len({canonical({k: v for k, v in o.items() if k not in {"source", "schema"}}) for o in observations}) > 1:
            labels.append("versioned observation")
        if {o["schema"] for o in observations} >= {"research-state-v1", "research-state-v2"}:
            labels.append("v1-to-v2 migration")
        if len({o["source"]["name"] for o in observations}) < len(snapshots):
            labels.append("cross-branch coverage")
        acquisition_ids = {o["acquisition_id"] for o in observations}
        supported = [
            c for c in claims if any(acquisition_ids.intersection(v["claim"]["acquisitions"]) for v in c["variants"])
        ]
        if len(supported) > 1:
            labels.append("multi-analysis acquisition")
        if any(c["classification"] == "claim conflict" for c in supported):
            labels.append("claim conflict")
        denominators = {f: consensus(observations, f) for f in FIELDS}
        if any(v["status"] == "conflicting observations" for v in denominators.values()):
            unresolved.append(
                {
                    "provider": provider,
                    "job_id": identity,
                    "reason": "Conflicting denominator observations; excluded from agreed totals.",
                }
            )
        identities.append(
            {
                "provider": provider,
                "job_id": identity,
                "classifications": labels or ["single observed execution"],
                "denominators": denominators,
                "observations": observations,
            }
        )
    coverage_resolutions = []
    for snap in snapshots:
        for identity in snap["declared_unretained_qi"]:
            key = ("quantum_inspire", str(identity))
            if key not in jobs:
                unresolved.append(
                    {
                        "source": snap["source"],
                        "provider": key[0],
                        "job_id": key[1],
                        "reason": "unresolved retention gap within the pinned source trees",
                    }
                )
            else:
                coverage_resolutions.append(
                    {
                        "declared_by": snap["source"],
                        "provider": key[0],
                        "job_id": key[1],
                        "classification": "cross-branch coverage",
                        "retained_locations": [{"source": o["source"], "run": o["run"]} for o in jobs[key]],
                    }
                )
    return {
        "identities": identities,
        "claims": claims,
        "unresolved": unresolved,
        "declared_unretained_resolutions": coverage_resolutions,
    }


def denominator_census(view: dict[str, Any], snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    providers = {}
    for provider in sorted({j["provider"] for j in view["identities"]}):
        jobs = [j for j in view["identities"] if j["provider"] == provider]
        fields = {}
        for field in FIELDS:
            available = [
                j["denominators"][field]["value"] for j in jobs if j["denominators"][field]["value"] is not None
            ]
            fields[field] = {
                "agreed_available_sum": sum(available) if available else None,
                "available_job_count": len(available),
                "total_job_count": len(jobs),
                "coverage": "complete" if len(available) == len(jobs) else "partial; not a provider-wide total",
            }
        providers[provider] = {
            "unique_jobs": len(jobs),
            "fields": fields,
            "eligible_outcomes": None,
            "exclusions_by_estimator": None,
            "unavailable_reason": (
                "Eligibility, processing exclusions and independence are estimator-specific; "
                "no program-wide contract is declared."
            ),
            "sessions": sorted({str(o["session"]) for j in jobs for o in j["observations"] if o.get("session")}),
            "calibration_clusters": None,
            "rates_computed": False,
            "available_estimator_denominators": [
                {
                    "job_id": j["job_id"],
                    "observations": [
                        {"source": o["source"], "denominators": o["estimator_denominators"]}
                        for o in j["observations"]
                        if "estimator_denominators" in o
                    ],
                }
                for j in jobs
                if any("estimator_denominators" in o for o in j["observations"])
            ],
        }
    return {
        "providers": providers,
        "ibm_unbound_by_source": [
            {
                "source": s["source"],
                "count": len(s["unbound_ibm_records"]),
                "classifications": dict(sorted(Counter(r["classification"] for r in s["unbound_ibm_records"]).items())),
                "records": s["unbound_ibm_records"],
            }
            for s in snapshots
        ],
        "historical_ibm_remaining_seconds": snapshots[0]["ibm_budget_observation"],
        "new_allocation_seconds": 0,
        "budget_boundary": (
            "117 seconds is a timestamped historical account observation, not a refreshed current balance."
        ),
    }


def dependency_report(view: dict[str, Any]) -> dict[str, Any]:
    versions = {(v["source"]["commit"], c["id"]): v["claim"] for c in view["claims"] for v in c["variants"]}
    root_cache: dict[tuple[str, str], set[str]] = {}

    def declared_roots(commit: str, identity: str, active: frozenset[str] = frozenset()) -> set[str]:
        key = (commit, identity)
        if key in root_cache:
            return root_cache[key]
        require(identity not in active, f"{commit}:{identity}: cyclic support")
        require(key in versions, f"{commit}:{identity}: missing declared dependency")
        claim = versions[key]
        roots = {f"analysis:{e['path']}:{e['sha256']}" for e in claim["evidence"]}
        roots |= {f"gate:{commit}:{gate}" for gate in claim["gates"]}
        roots |= {
            f"job:{j['provider']}:{j['job_id']}"
            for j in view["identities"]
            if any(
                o["source"]["commit"] == commit and o["acquisition_id"] in claim["acquisitions"]
                for o in j["observations"]
            )
        }
        for parent in claim["depends_on"]:
            roots.add(f"claim:{commit}:{parent}")
            roots |= declared_roots(commit, parent, active | {identity})
        root_cache[key] = roots
        return roots

    reports = []
    for entry in view["claims"]:
        for version in entry["variants"]:
            claim = version["claim"]
            if claim["evidence_class"] != "preregistered hardware inference" or claim["status"] != "established":
                continue
            source = version["source"]
            all_roots = declared_roots(source["commit"], claim["id"])
            physical = [
                j
                for j in view["identities"]
                if f"job:{j['provider']}:{j['job_id']}" in all_roots
                and any(o["source"] == source for o in j["observations"])
            ]
            roots = [f"job:{j['provider']}:{j['job_id']}" for j in physical]
            hardware = [
                j
                for j in physical
                if any(o["source"] == source and o.get("execution_kind") == "hardware" for o in j["observations"])
            ]
            physical_roots = [f"job:{j['provider']}:{j['job_id']}" for j in hardware]
            roots += [f"claim:{source['commit']}:{c}" for c in claim["depends_on"]]
            analytical = [{"kind": "declared evidence", **e} for e in claim["evidence"]]
            analytical += [{"kind": "declared gate", "id": g, "role": role} for g, role in claim["gates"].items()]
            controls = [root for root in roots if root not in physical_roots]
            roots += [f"analysis:{e['path']}:{e['sha256']}" for e in claim["evidence"]]
            roots += [f"gate:{source['commit']}:{gate}" for gate in claim["gates"]]
            observed = [o for j in hardware for o in j["observations"] if o["source"] == source]
            axes = {}
            for axis, field in [
                ("sessions", "session"),
                ("calibrations", "calibration"),
                ("devices", "backend"),
                ("compilations", "compilation"),
            ]:
                values = sorted({str(o[field]) for o in observed if o.get(field)})
                if axis == "compilations":
                    values = sorted(
                        set(values) | {v for o in observed for v in o.get("returned_compilation_identities", [])}
                    )
                axes[axis] = {
                    "known_count": len(values),
                    "values": values,
                    "coverage": "complete"
                    if observed and all(o.get(field) for o in observed)
                    else "partial or unavailable",
                }
            axes["jobs"] = {"count": len(hardware), "control_or_unqualified_jobs": len(physical) - len(hardware)}
            axes["preparations"] = {
                "count": None,
                "reason": "Preparation identity is not inferred from a state name or directory.",
            }
            gaps = [
                (
                    "Calibration identity, effective outcome mapping, compiler transformation and "
                    "shared analysis closure require claim-specific qualification."
                )
            ]
            if not claim["assumptions"]:
                gaps.append(
                    "The registry declares no assumptions; this is missing metadata, not an assumption-free inference."
                )
            reports.append(
                {
                    "claim": claim["id"],
                    "source": source,
                    "statement": claim["statement"],
                    "boundary": claim["boundary"],
                    "physical_support_roots": physical_roots,
                    "declared_control_and_claim_roots": controls,
                    "analytical_support_roots": analytical,
                    "inherited_support_roots": sorted(all_roots - set(roots)),
                    "declared_assumptions": claim["assumptions"],
                    "qualification_gaps": gaps,
                    "replication_axes": axes,
                    "tested_differences": {
                        "registered_statement": claim["statement"],
                        "scope_boundary": claim["boundary"],
                        "independent_replication_adjudication": "unavailable",
                    },
                    "withdrawal": [
                        {
                            "root": root,
                            "outcome": "declared support incomplete; re-adjudication required",
                            "meaning": (
                                "Conservative withdrawal of declared evidence, not a claim of scientific falsification."
                            ),
                        }
                        for root in sorted(all_roots)
                    ],
                    "numerical_leave_one_out": [
                        {
                            "axis": axis,
                            "status": "unavailable",
                            "reason": (
                                "No claim-specific endpoint re-estimator with a frozen deletion contract is "
                                "registered. Support withdrawal is not numerical sensitivity."
                            ),
                        }
                        for axis in ["job", "session", "calibration", "implementation family"]
                    ],
                }
            )
    return {
        "claims": reports,
        "boundary": (
            "Declared dependency census, not a complete causal identification or a "
            "numerical re-estimation. Missing numerical contracts remain unresolved."
        ),
    }


def evidence_matrix(view: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for source in sorted({canonical(v["source"]) for c in view["claims"] for v in c["variants"]}):
        values = [v["claim"] for c in view["claims"] for v in c["variants"] if canonical(v["source"]) == source]
        counts = Counter((CLASSIFICATION.get(c["evidence_class"], c["evidence_class"]), c["status"]) for c in values)
        rows.extend(
            {"source": json.loads(source), "evidence_class": cls, "status": status, "count": count}
            for (cls, status), count in sorted(counts.items())
        )
    # Counts of devices alone never promote a claim to independently replicated.
    return {
        "rows": rows,
        "independently_replicated_hardware_inference": {
            "count": None,
            "reason": "Requires adjudicated independent replication axes; not derived from device/job counts.",
        },
        "aggregate_established_headline": (
            "withdrawn; incomparable evidence classes are not summed into a scientific result count"
        ),
    }


def build(pins: list[dict[str, str]]) -> dict[str, Any]:
    snapshots = ordered_map(load_snapshot, pins, min_items=2)
    view = reconcile(snapshots)
    return {
        "schema": "evidence-closure-derived-view-v1",
        "producer_sha256": PRODUCER_DIGEST,
        "parallel_source_sha256": sha((ROOT / "gororoba_quantum/parallel.py").read_bytes()),
        "coverage": (
            "Four requested source pins plus two observed supplemental PR heads; no live "
            "provider observations; not a replacement registry."
        ),
        "pins": pins,
        "reconciliation": view,
        "denominators": denominator_census(view, snapshots),
        "dependencies": dependency_report(view),
        "evidence_matrix": evidence_matrix(view),
        "numerical_rechecks": [{"source": s["source"], "results": s["numerical_rechecks"]} for s in snapshots],
        "closure_gaps": {
            "legacy_ibm_records": sorted(
                {r["path"] for s in snapshots for r in s["unbound_ibm_records"] if r["classification"] == "unresolved"}
            ),
            "numerical_claim_reestimation": (
                "Claim-specific endpoint deletion contracts remain unregistered; the separate "
                "raw-contrast sensitivity is descriptive only."
            ),
            "physical_model_qualification": (
                "Calibration, preparation, effective processing and shared analytical closure "
                "require claim-specific qualification; no missing field is treated as "
                "independence."
            ),
            "future_acquisitions": (
                "No new execution authorized. Diagnostic block 2 absent at pinned sources; "
                "successor admission and Fourier discrimination remain prospective."
            ),
        },
        "source_inputs": [{"source": s["source"], "schema": s["schema"], "inputs": s["inputs"]} for s in snapshots],
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Derived evidence closure",
        "",
        result["coverage"],
        "",
        "Generated by `scripts/evidence_closure.py --write`; the authoritative registry stays at",
        "`docs/state/research_state.json`. Conflicts are preserved, not resolved by choosing the newest branch.",
        "",
        "## Identity and unresolved coverage",
        "",
        f"Unique provider job identities: {len(result['reconciliation']['identities'])}.",
        f"Unresolved claim/denominator/retention entries: {len(result['reconciliation']['unresolved'])}.",
        "",
        "See snapshot.json for every identity, observation version, source hash, unresolved item,",
        "denominator and declared dependency. Unknown values are null, never zero.",
        "",
        "## IBM records outside registry-bound runs",
        "",
        "| Source | Directories | Classification counts |",
        "| --- | ---: | --- |",
    ]
    for row in result["denominators"]["ibm_unbound_by_source"]:
        counts = "; ".join(f"{k}: {v}" for k, v in row["classifications"].items())
        lines.append(f"| {row['source']['name']} | {row['count']} | {counts} |")
    lines += [
        "",
        "The stated 198 is not assumed. The pinned main count is recomputed from tracked record paths,",
        "with every path classified. Legacy records without explicit dispatch state remain unresolved.",
        "",
        "## Denominator coverage",
        "",
        "| Provider | Unique jobs | Field | Agreed available sum | Jobs covered |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for provider, row in result["denominators"]["providers"].items():
        for field, values in row["fields"].items():
            value = values["agreed_available_sum"]
            lines.append(
                f"| {provider} | {row['unique_jobs']} | {field} | {value if value is not None else 'unavailable'} | {
                    values[('available_job_count')]
                }/{values[('total_job_count')]} |"
            )
    lines += [
        "",
        "Partial sums are not provider-wide totals. No rate is computed. Eligibility and exclusions",
        "require the declared estimator; an observed one-photon category is not automatically an exclusion.",
        "Quandela top-level shots can be a per-iteration ceiling; only retained shots_used/nb_shots_used",
        "are treated as its reported total. IBM requested PUB shots are not relabelled completed shots.",
        "",
        "## Evidence-class matrix",
        "",
        "| Source | Evidence class | Status | Count |",
        "| --- | --- | --- | ---: |",
    ]
    for row in result["evidence_matrix"]["rows"]:
        lines.append(f"| {row['source']['name']} | {row['evidence_class']} | {row['status']} | {row['count']} |")
    lines += [
        "",
        "Independent hardware replication is unadjudicated, not zero and not inferred from multiple jobs.",
        "",
        "## Dependency withdrawal and numerical sensitivity",
        "",
        f"{len(result['dependencies']['claims'])} source-relative established hardware claim versions are listed.",
        "Declared physical and analytical roots are separate. Removing a declared root marks support",
        "incomplete, not the claim false. Numerical leave-one-out remains explicitly unavailable until",
        "each endpoint has a frozen deletion/re-estimation contract. Empty registry assumption lists",
        "and unavailable calibration/preparation identities remain qualification gaps.",
        "",
        "Numerical rechecks separately delete each shared-shot Latin job from the raw Tuna visibility",
        "and rederive the Fourier own-target/predecessor distances from eligible mode counts.",
        "They do not silently re-adjudicate a calibrated endpoint or identify a causal mechanism.",
        "",
        "The external-auditor packet in auditor-subset.json supplies full source-relative claim records,",
        "boundaries, hashes and gate roles. It is a review packet, not an assertion that an external audit passed.",
        "",
    ]
    return "\n".join(lines)


def auditor_subset(view: dict[str, Any]) -> dict[str, Any]:
    chosen = []
    for entry in view["claims"]:
        if entry["classification"] != "same declared semantics":
            continue
        version = next((v for v in entry["variants"] if v["source"]["name"] == "main"), None)
        if version and version["claim"]["evidence"] and "replay" in version["claim"]["gates"].values():
            chosen.append(version)
    return {
        "scope": (
            "Nonconflicting main claims with explicit retained evidence and a declared "
            "replay gate; metadata selection only, external audit not performed."
        ),
        "claims": chosen,
        "review_obligations": [
            "Check the stated proof/likelihood assumptions and boundary.",
            "Re-run the named replay, not merely a checksum gate.",
            "Verify source-relative evidence hashes and all physical support dependencies.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument(
        "--fetch-pins", action="store_true", help="Fetch missing Git source commits only; no provider calls"
    )
    args = parser.parse_args()
    pins = json.loads((DEST / "pins.json").read_text())
    if args.fetch_pins:
        for source in pins:
            commit = source["commit"]
            require(bool(re.fullmatch(r"[0-9a-f]{40}", commit)), "Invalid source pin")
            present = subprocess.run(
                ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if present.returncode:
                git("fetch", "--no-tags", "--depth=1", "origin", commit)
    result = build(pins)
    require(sha(Path(__file__).read_bytes()) == PRODUCER_DIGEST, "Producer changed during replay; discard this run")
    outputs = {
        "snapshot.json": json.dumps(result, indent=2, sort_keys=True) + "\n",
        "README.md": render(result),
        "auditor-subset.json": json.dumps(auditor_subset(result["reconciliation"]), indent=2, sort_keys=True) + "\n",
    }
    candidate = next(
        row["results"]["fourier_candidate"]
        for row in result["numerical_rechecks"]
        if row["source"]["name"] == "photonic-conformance"
    )
    outputs["fourier-candidate.json"] = json.dumps(candidate, indent=2, sort_keys=True) + "\n"
    for name, text in outputs.items():
        path = DEST / name
        if args.write:
            path.write_text(text)
        else:
            require(
                path.is_file() and path.read_text() == text, f"{path.relative_to(ROOT)} differs; regenerate explicitly"
            )
    count = len(result["reconciliation"]["identities"])
    gaps = len(result["reconciliation"]["unresolved"])
    print(f"evidence closure: {count} unique jobs; {gaps} unresolved entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
