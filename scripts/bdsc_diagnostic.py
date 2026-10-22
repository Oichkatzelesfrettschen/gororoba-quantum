"""Belenos crossed variance-identification case: target-complement states x templates x seeds x blocks, and its readout.

The case separates the response components that one compilation per setting
confounds: counting noise, a matched request's change between two acquisition
blocks, differences across compilation seeds of one state, the template, and
state-by-seed interaction. Its instances are the six target-complement states
of docs/evidence/bdsc/qualification_case.json under both preparation
templates, compiled with each of four seeds, in each of two blocks: 96
instances of 10000 eligible trials under an explicit empty mitigation list.

Every (template, seed) group of six states runs inside one job, so its two
sum-rule residuals compare iterations of one job. A block runs two jobs of 24
iterations; block 1 places outward seeds 0 and 1 with reverse seeds 2 and 3 in
its first job and the complement in its second, and block 2 swaps the two
assignments, so job position never aliases a seed or template across blocks.
A compiled circuit is a function of the seed, the parameters and the
compiler's component model (docs/evidence/bdsc/forensics/forensics.json,
compilation_determinism), so block 2 repeats block 1's returned circuits
while that model holds, which the readout verifies per instance.

Without --draw the case directories read draft and carry no seeds or order.
With --draw (an scripts/anu_qrng.py record of at least 100 uint16 values) the
first four distinct values are the seeds of slots 0 to 3, and value 4 + i
orders instance i within its job.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic.py --write [--draw FILE]
  "$PYTHON" scripts/bdsc_diagnostic.py --check [--draw FILE]
  "$PYTHON" scripts/bdsc_diagnostic.py --readout RUN_DIR...
  "$PYTHON" scripts/bdsc_diagnostic.py --self-test
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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_cases  # noqa: E402
import bdsc_certificate as cert  # noqa: E402

CASE = ROOT / "docs/evidence/bdsc/diagnostic/case.json"
CASES_DIR = ROOT / "results/quandela/cases/bdsc_diagnostic"
FAMILY = "bdsc_diagnostic"
PAIR = "target-complement"
POLICY: list[str] = []
LABELS = ("f", "g", "+", "-", "+i", "-i")
SLOTS = 4
BLOCKS = (1, 2)
TRIALS = 10000
MAX_SHOTS = 2 * TRIALS
# Billing and timing rules of docs/runbooks/quandela-credit-optimization.md, measured on retained qpu:belenos jobs.
CREDIT_PER_JOB = 1.0
CREDIT_PER_SHOT = 1e-6
SECONDS_PER_ITERATION = 6.3
SECONDS_PER_SAMPLE = 2.6e-5
# Block 2 waits this long after block 1's last execution ends, so the blocks are separated in time.
BLOCK_GAP_HOURS = 1
# A summary ratio of observed dispersion to its reference counting scale reads resolved at or above RESOLVED and
# consistent with counting below CONSISTENT; between them it is inconclusive.
CONSISTENT = 2.0
RESOLVED = 3.0
MARGIN = 0.02
DRAW_VALUES = SLOTS + 2 * 2 * SLOTS * len(LABELS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def outward_slots(block: int) -> tuple[int, ...]:
    """Seed slots whose outward-ladder groups run in a block's first job; its reverse groups take the others."""
    return (0, 1) if block == 1 else (2, 3)


def instances() -> list[dict[str, Any]]:
    """The 96 instances in canonical order, each with its block, job, template, seed slot and state."""
    out: list[dict[str, Any]] = []
    for block in BLOCKS:
        for template in cert.PREPARATION_DESCRIPTIONS:
            for slot in range(SLOTS):
                first = (slot in outward_slots(block)) == (template == cert.PREPARATION_DESCRIPTIONS[0])
                for label in LABELS:
                    out.append(
                        {
                            "index": len(out),
                            "block": block,
                            "job": f"b{block}-j{1 if first else 2}",
                            "template": template,
                            "slot": slot,
                            "label": label,
                        }
                    )
    return out


def instance_name(item: dict[str, Any]) -> str:
    tag = bdsc_cases.TEMPLATE_TAGS[item["template"]]
    return f"{tag}-s{item['slot']}-{bdsc_cases.LABEL_TAGS[item['label']]}"


def case_record() -> dict[str, Any]:
    """The frozen design, layout, resources, analysis and stop conditions of the diagnostic case."""
    items = instances()
    jobs = sorted({i["job"] for i in items})
    per_job = len(items) // len(jobs)
    seconds_per_job = per_job * (SECONDS_PER_ITERATION + SECONDS_PER_SAMPLE * TRIALS)
    qualification = bdsc_cases.CASE.read_bytes()
    return {
        "schema": "bdsc-diagnostic-case-v1",
        "record": "diagnostic_case",
        "question": "which of counting noise, a matched request's change between blocks, compilation seed, template "
        "and state-by-seed interaction carry the per-setting response scatter of the target-complement bank",
        "authorization": "none: the case waits for its written-case approval, which also covers its QRNG read",
        "qualification_case_sha256": sha256_bytes(qualification),
        "target_sha256": json.loads(qualification)["target_sha256"],
        "design": {
            "pair": PAIR,
            "states": list(LABELS),
            "templates": list(cert.PREPARATION_DESCRIPTIONS),
            "seed_slots": SLOTS,
            "blocks": list(BLOCKS),
            "instances": len(items),
            "processing": "empty-mitigation",
            "mitigations": POLICY,
            "eligible_trials_per_instance": TRIALS,
            "max_shots_per_iteration": MAX_SHOTS,
            "block_gap_hours": BLOCK_GAP_HOURS,
            "role": "diagnostic, not a confirmation design: four seeds do not determine the tails of a seed "
            "distribution, and the result decides whether further compilation replication is warranted",
        },
        "jobs": [
            {
                "job": job,
                "block": int(job[1]),
                "groups": sorted(
                    {f"{bdsc_cases.TEMPLATE_TAGS[i['template']]}-s{i['slot']}" for i in items if i["job"] == job}
                ),
                "iterations": per_job,
            }
            for job in jobs
        ],
        "resources": {
            "billing_rule": "1 credit per job plus 1e-6 per shot of the job's largest iteration max_shots",
            "credits": round(len(jobs) * (CREDIT_PER_JOB + CREDIT_PER_SHOT * MAX_SHOTS), 6),
            "eligible_trials_total": TRIALS * len(items),
            "max_shots_total": MAX_SHOTS * len(items),
            "seconds_per_job_estimate": round(seconds_per_job, 3),
            "seconds_estimate": round(seconds_per_job * len(jobs), 3),
            "timing_rule": "6.3 s plus 2.6e-05 s per sample for each iteration against the 300 s per-job limit; "
            "the written case restates credits and seconds from the live qd_platform.py plan output",
        },
        "qrng": {
            "service": "ANU Quantum Numbers (aqn, keyed), scripts/anu_qrng.py draw",
            "type": "uint16",
            "values": DRAW_VALUES,
            "requests": 1,
            "credits": 0,
            "use": "the first four distinct values seed slots 0 to 3; value 4 + i orders instance i within its job",
        },
        "analysis": {
            "observation": "one-click conditioned selected fraction of returned counts; every standard error is a "
            "reference value under independent Bernoulli trials, which the provider contract has not established",
            "residuals": "Delta_R and Delta_I per block, template and seed, each from one job",
            "block_change": "p(block 2) - p(block 1) per instance, with the returned-circuit identity of the pair",
            "seed_dispersion": "SD over the four seeds per block, template and state, and of each residual",
            "template_effect": "seed-mean outward minus reverse per block and state",
            "ratios": "RMS observed dispersion over RMS reference standard error, read consistent below "
            f"{CONSISTENT}, resolved at or above {RESOLVED}, inconclusive between",
            "branches": {
                "stationarity": "matched requests change between blocks: address stationarity and provider "
                "calibration before any fixed-effect confirmation",
                "seed": "seeds give reproducible differences: study seed selection on development data and "
                "validate a frozen selection on fresh data",
                "common-effect": "seed dispersion is small but residuals persist beyond the margin: investigate "
                "preparation, filtering and processing; more seeds are not the remedy",
                "ensemble-candidate": "seed effects small and residuals within the margin: an ensemble-defined "
                "certification case becomes a candidate once a common ensemble effect is supported",
            },
            "margin": MARGIN,
        },
        "stop_conditions": [
            "scripts/qd_platform.py plan refuses the platform",
            "a retained job body differs from the empty mitigation list, or a result is not an integer BSCount",
            "a job fails, an iteration returns fewer samples than the frozen n, or the one-click eligibility rule "
            "excludes more than 0.01 of an iteration's samples",
            "an iteration returns no compiled circuit",
            "block 2 starts before block 1's readout integrity passes or before the block gap elapses",
            "spent credits or seconds reach the approved ceiling",
        ],
    }


def draw_values(path: Path | None) -> tuple[list[int], list[int]] | None:
    """(seeds of slots 0 to 3, order keys of the 96 instances) from a keyed ANU record, or None without one."""
    if path is None:
        return None
    import anu_qrng

    record = json.loads(path.read_text(encoding="utf-8"))
    anu_qrng.admit(record)
    require(str(record.get("source", "")).startswith(anu_qrng.ENDPOINTS["aqn"]), f"{path}: not the keyed AQN service")
    require(record["type"] == "uint16", f"{path}: type {record['type']!r}, the case draws uint16")
    values = list(record["values"])
    require(len(values) >= DRAW_VALUES, f"{path}: {len(values)} values, need {DRAW_VALUES}")
    seeds: list[int] = []
    for value in values[:SLOTS]:
        require(value not in seeds, f"{path}: seed values repeat; the case needs four distinct seeds")
        seeds.append(value)
    return seeds, values[SLOTS:DRAW_VALUES]


def draw_claims(binding: dict[str, Any]) -> list[str]:
    """Retained manifests of any other case that name the record."""
    case_sha = sha256_bytes((json.dumps(case_record(), indent=1) + "\n").encode())
    claims = []
    for root in bdsc_cases.MANIFEST_ROOTS:
        for path in sorted(root.glob("**/cases.json")) if root.is_dir() else []:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            named = manifest.get("draw")
            if isinstance(named, dict) and named.get("sha256") == binding["sha256"]:
                if manifest.get("diagnostic_case_sha256") != case_sha:
                    claims.append(str(path.relative_to(ROOT)))
    return claims


def documents(draw: Path | None) -> dict[str, bytes | dict[str, bytes]]:
    """{"case.json": bytes, job: {"cases.json": bytes, "circuit.json": bytes}} for the record and every job."""
    record_bytes = (json.dumps(case_record(), indent=1) + "\n").encode()
    qualification = json.loads(bdsc_cases.CASE.read_text(encoding="utf-8"))
    target = json.loads(bdsc_cases.TARGET.read_text(encoding="utf-8"))
    source = target["source_mode"]
    chip = bdsc_cases.columns(qualification, target)
    ideal = {(b["pair"], r["label"]): r["ideal_selected"]["E0"] for b in qualification["banks"] for r in b["settings"]}
    drawn = draw_values(draw)
    binding = None
    if draw is not None:
        binding = bdsc_cases.draw_binding(draw)
        claims = draw_claims(binding)
        require(not claims, f"{draw}: another case already draws from this record: {claims[:3]}")
    params = {
        (template, label): cert.union_params(template, chip[(PAIR, label)], source, modes=cert.MODES)
        for template in cert.PREPARATION_DESCRIPTIONS
        for label in LABELS
    }
    ops = cert.union_ops(source, modes=cert.MODES)
    input_state = [0] * cert.MODES
    input_state[source] = 1
    circuit = {
        "schema": bdsc_cases.CIRCUIT_SCHEMA,
        "template": cert.UNION_CIRCUIT,
        "modes": cert.MODES,
        "input_state": input_state,
        "parameters": sum(1 for _, _, k in ops if k is not None),
        "ops": [list(op) for op in ops],
    }
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    items = instances()
    out: dict[str, bytes | dict[str, bytes]] = {"case.json": record_bytes}
    for job in sorted({i["job"] for i in items}):
        members = [i for i in items if i["job"] == job]
        if drawn is not None:
            members.sort(key=lambda i: (drawn[1][i["index"]], i["index"]))
        settings = []
        for item in members:
            column = chip[(PAIR, item["label"])]
            setting: dict[str, Any] = {
                "name": instance_name(item),
                "instance_index": item["index"],
                "block": item["block"],
                "slot": item["slot"],
                "preparation": item["template"],
                "circuit_params": {f"x{k}": float(v) for k, v in enumerate(params[(item["template"], item["label"])])},
                "column": [[float(z.real), float(z.imag)] for z in column],
                "ideal_selected_E0": ideal[(PAIR, item["label"])],
            }
            if drawn is not None:
                setting["compilation_seed"] = drawn[0][item["slot"]]
                setting["draw_indices"] = {"seed": item["slot"], "order": SLOTS + item["index"]}
            settings.append(setting)
        manifest: dict[str, Any] = {
            "schema": bdsc_cases.CASES_SCHEMA,
            "family": FAMILY,
            "job": job,
            "platforms": bdsc_cases.PLATFORMS,
            "command": "sample_count",
            "gate_form": "template",
            "min_detected_photons": 1,
            "iterations": len(settings),
            "max_samples": TRIALS * len(settings),
            "max_shots": MAX_SHOTS * len(settings),
            "max_duration": bdsc_cases.MAX_DURATION,
            "mitigations": POLICY,
            "job_spec": {
                "pair": PAIR,
                "processing": "empty-mitigation",
                "block": int(job[1]),
                "circuit": cert.UNION_CIRCUIT,
            },
            "settings": settings,
            "selected_modes": target["selected_modes"],
            "eligibility": bdsc_cases.ELIGIBILITY,
            "diagnostic_case_sha256": sha256_bytes(record_bytes),
            "target_sha256": target["target_sha256"],
            "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
            "draft": drawn is None,
        }
        if binding is not None:
            manifest["draw"] = binding
        out[job] = {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}
    return out


def write(draw: Path | None) -> None:
    for name, content in documents(draw).items():
        if isinstance(content, bytes):
            CASE.parent.mkdir(parents=True, exist_ok=True)
            CASE.write_bytes(content)
            continue
        (CASES_DIR / name).mkdir(parents=True, exist_ok=True)
        for file, data in content.items():
            (CASES_DIR / name / file).write_bytes(data)
    print(
        f"bdsc diagnostic: wrote {CASE.relative_to(ROOT)} and the job directories under {CASES_DIR.relative_to(ROOT)}"
    )


def check(draw: Path | None) -> None:
    """A rebuild matches: the record and circuits exactly, manifests within cert.CHECK_TOLERANCE on floats."""
    fresh = documents(draw)
    require(CASE.read_bytes() == fresh["case.json"], f"{CASE.relative_to(ROOT)} differs from a fresh build")
    jobs = sorted(k for k in fresh if k != "case.json")
    present = sorted(p.name for p in CASES_DIR.iterdir() if p.is_dir())
    require(present == jobs, f"job directories differ: {sorted(set(present) ^ set(jobs))}")
    for job in jobs:
        files = fresh[job]
        require(isinstance(files, dict), f"{job}: not a job")
        if isinstance(files, dict):
            require((CASES_DIR / job / "circuit.json").read_bytes() == files["circuit.json"], f"{job}/circuit.json")
            cert.close(json.loads(files["cases.json"]), json.loads((CASES_DIR / job / "cases.json").read_bytes()), job)
    print(f"bdsc diagnostic: the case record and {len(jobs)} job directories match a fresh build")


def reference_se(p: float, n: int) -> float:
    return math.sqrt(max(p * (1 - p), 0.25 / n) / n)


def reading(ratio: float) -> str:
    return "consistent" if ratio < CONSISTENT else "resolved" if ratio >= RESOLVED else "inconclusive"


def rms(values: list[float]) -> float:
    return math.sqrt(sum(v * v for v in values) / len(values))


def analyse(observed: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Residuals, block changes, seed dispersion, template effect, summary ratios and the preregistered branch.

    observed maps each instance index to its selected and eligible counts and returned-circuit sha256.
    """
    items = instances()
    require(sorted(observed) == [i["index"] for i in items], "the readout needs every instance")
    key = {(i["block"], i["template"], i["slot"], i["label"]): i["index"] for i in items}

    def p(b: int, t: str, s: int, label: str) -> float:
        o = observed[key[(b, t, s, label)]]
        return o["selected"] / o["eligible"]

    def se(b: int, t: str, s: int, label: str) -> float:
        o = observed[key[(b, t, s, label)]]
        return reference_se(o["selected"] / o["eligible"], o["eligible"])

    templates = cert.PREPARATION_DESCRIPTIONS
    residuals: list[dict[str, Any]] = []
    for b in BLOCKS:
        for t in templates:
            for s in range(SLOTS):
                for family, (plus, minus) in (("delta_R", ("+", "-")), ("delta_I", ("+i", "-i"))):
                    value = p(b, t, s, plus) + p(b, t, s, minus) - p(b, t, s, "f") - p(b, t, s, "g")
                    ref = math.sqrt(sum(se(b, t, s, x) ** 2 for x in (plus, minus, "f", "g")))
                    residuals.append(
                        {"block": b, "template": t, "slot": s, "family": family, "value": value, "se": ref}
                    )
    changes: list[dict[str, Any]] = []
    for t in templates:
        for s in range(SLOTS):
            for label in LABELS:
                first, second = observed[key[(1, t, s, label)]], observed[key[(2, t, s, label)]]
                changes.append(
                    {
                        "template": t,
                        "slot": s,
                        "label": label,
                        "change": p(2, t, s, label) - p(1, t, s, label),
                        "se": math.hypot(se(1, t, s, label), se(2, t, s, label)),
                        "same_returned_circuit": first["circuit_sha256"] == second["circuit_sha256"],
                    }
                )
    seeds: list[dict[str, Any]] = []
    for b in BLOCKS:
        for t in templates:
            for label in LABELS:
                values = [p(b, t, s, label) for s in range(SLOTS)]
                seeds.append(
                    {
                        "block": b,
                        "template": t,
                        "label": label,
                        "sd": float(np.std(values, ddof=1)),
                        "se": rms([se(b, t, s, label) for s in range(SLOTS)]),
                    }
                )
    residual_seeds: list[dict[str, Any]] = []
    for b in BLOCKS:
        for t in templates:
            for family in ("delta_R", "delta_I"):
                chosen = [r for r in residuals if (r["block"], r["template"], r["family"]) == (b, t, family)]
                residual_seeds.append(
                    {
                        "block": b,
                        "template": t,
                        "family": family,
                        "mean": float(np.mean([r["value"] for r in chosen])),
                        "sd": float(np.std([r["value"] for r in chosen], ddof=1)),
                        "se": rms([r["se"] for r in chosen]),
                    }
                )
    template_effect = [
        {
            "block": b,
            "label": label,
            "effect": float(
                np.mean([p(b, templates[0], s, label) - p(b, templates[1], s, label) for s in range(SLOTS)])
            ),
        }
        for b in BLOCKS
        for label in LABELS
    ]
    ratios = {
        "block_change": rms([c["change"] for c in changes]) / rms([c["se"] for c in changes]),
        "seed": rms([x["sd"] for x in seeds]) / rms([x["se"] for x in seeds]),
        "residual_seed": rms([x["sd"] for x in residual_seeds]) / rms([x["se"] for x in residual_seeds]),
    }
    readings = {k: reading(v) for k, v in ratios.items()}
    mean_residual = float(np.mean([abs(r["value"]) for r in residuals]))
    if readings["block_change"] == "resolved":
        branch = "stationarity"
    elif readings["seed"] == "resolved" and readings["residual_seed"] == "resolved":
        branch = "seed"
    elif mean_residual > MARGIN:
        branch = "common-effect"
    else:
        branch = "ensemble-candidate"
    return {
        "residuals": residuals,
        "block_changes": changes,
        "seed_dispersion": seeds,
        "residual_seed_dispersion": residual_seeds,
        "template_effect": template_effect,
        "ratios": ratios,
        "readings": readings,
        "mean_abs_residual": mean_residual,
        "returned_circuit_repeats": sum(c["same_returned_circuit"] for c in changes),
        "branch": branch,
    }


def readout(runs: list[Path]) -> dict[str, Any]:
    """The analysis of collected qpu:belenos runs of every diagnostic job, after the integrity checks."""
    import qd_platform

    record_sha = sha256_bytes(CASE.read_bytes())
    observed: dict[int, dict[str, Any]] = {}
    for run in runs:
        manifest_bytes = (run / "cases.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        result = json.loads((run / "results.json").read_text(encoding="utf-8"))
        submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
        body_bytes = (run / "job-body.json").read_bytes()
        require(
            submission.get("platform") == bdsc_cases.QUALIFYING_PLATFORM, f"{run}: not {bdsc_cases.QUALIFYING_PLATFORM}"
        )
        require(submission.get("cases_sha256") == sha256_bytes(manifest_bytes), f"{run}: cases.json changed")
        require(submission.get("body_sha256") == bdsc_cases.body_digest(body_bytes), f"{run}: job-body.json differs")
        require(result.get("job_id") == submission.get("job_id"), f"{run}: the result answers another job")
        require(manifest.get("diagnostic_case_sha256") == record_sha, f"{run}: built from another case record")
        require(not manifest.get("draft", True), f"{run}: a draft case")
        require(qd_platform.body_mitigations(json.loads(body_bytes)) == POLICY, f"{run}: the body's policy differs")
        require(result.get("status", {}).get("status") == "completed", f"{run}: the job did not complete")
        require(result.get("partial") is False, f"{run}: a partial result")
        for index, item in observations(manifest, result).items():
            require(index not in observed, f"{run}: instance {index} collected twice")
            observed[index] = item
    return analyse(observed)


def observations(manifest: dict[str, Any], result: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Per-instance one-click tallies of one job, with seed, parameter, sample and eligibility checks."""
    out = {}
    iterations = result["iterations"]
    require(len(iterations) == len(manifest["settings"]), f"{manifest['job']}: iteration count differs")
    for setting, iteration in zip(manifest["settings"], iterations, strict=True):
        ran = iteration["iteration"]
        echoed = ran.get("circuit_params") or {}
        require(
            echoed.keys() == setting["circuit_params"].keys()
            and all(
                abs(echoed[x] - v) <= bdsc_cases.PARAM_ECHO_TOLERANCE for x, v in setting["circuit_params"].items()
            ),
            f"{manifest['job']}/{setting['name']}: parameters",
        )
        require(
            ran.get("compilation_seed") == setting["compilation_seed"], f"{manifest['job']}/{setting['name']}: seed"
        )
        require(iteration.get("samples") == TRIALS, f"{manifest['job']}/{setting['name']}: samples")
        counted = bdsc_cases.tally(iteration["counts"], manifest["selected_modes"])
        require(
            counted["eligible"] >= (1 - cert.ELIGIBLE_LOSS) * TRIALS, f"{manifest['job']}/{setting['name']}: eligible"
        )
        circuit = iteration.get("result_fields", {}).get("computed_circuit")
        require(isinstance(circuit, str), f"{manifest['job']}/{setting['name']}: no compiled circuit")
        out[setting["instance_index"]] = {
            "selected": counted["selected"],
            "eligible": counted["eligible"],
            "circuit_sha256": hashlib.sha256(circuit.encode()).hexdigest(),
        }
    return out


def synthetic_result(
    manifest: dict[str, Any], response: dict[tuple[int, str, int], float], seed: int
) -> dict[str, Any]:
    """A completed result whose iterations draw one-click counts from response[(block, name-without-slot, slot)]."""
    rng = np.random.default_rng(seed)
    selected = manifest["selected_modes"][0]
    other = next(m for m in range(cert.MODES) if m not in manifest["selected_modes"])
    iterations = []
    for setting in manifest["settings"]:
        probability = response[(setting["block"], setting["name"], setting["slot"])]
        k = int(rng.binomial(TRIALS, probability))
        pattern = ["0"] * cert.MODES
        hit, miss = pattern.copy(), pattern.copy()
        hit[selected], miss[other] = "1", "1"
        iterations.append(
            {
                "counts": {",".join(hit): k, ",".join(miss): TRIALS - k},
                "iteration": {
                    "circuit_params": setting["circuit_params"],
                    "compilation_seed": setting["compilation_seed"],
                },
                "result_fields": {"computed_circuit": f"seed {setting['compilation_seed']} {setting['name']}"},
                "samples": TRIALS,
            }
        )
    return {"iterations": iterations}


def self_test() -> int:
    """Synthetic responses with a known component are read into the branch that component predicts."""
    seeds = [101, 202, 303, 404]
    base = {"f": 0.003, "g": 0.986}
    jobs = {}
    for name, content in documents(None).items():
        if isinstance(content, dict):
            manifest = json.loads(content["cases.json"])
            for setting in manifest["settings"]:
                setting["compilation_seed"] = seeds[setting["slot"]]
            jobs[name] = manifest
    label_of = {f"-{tag}": label for label, tag in bdsc_cases.LABEL_TAGS.items()}

    def label(name: str) -> str:
        return next(v for k, v in label_of.items() if name.endswith(k))

    def run(shift: dict[str, Any]) -> dict[str, Any]:
        observed: dict[int, dict[str, Any]] = {}
        for k, manifest in enumerate(jobs.values()):
            response = {}
            for s in manifest["settings"]:
                lab = label(s["name"])
                p0 = base.get(lab, 0.4945)
                p0 += shift.get("seed", [0.0] * SLOTS)[s["slot"]] if lab not in base else 0.0
                p0 += (
                    shift.get("block", 0.0) * (s["block"] - 1) * (1 if s["slot"] % 2 else -1)
                    if lab not in base
                    else 0.0
                )
                response[(s["block"], s["name"], s["slot"])] = p0
            observed.update(observations(manifest, synthetic_result(manifest, response, 7 + k)))
        return analyse(observed)

    null = run({})
    require(null["branch"] == "ensemble-candidate", f"a counting-only response read {null['branch']}")
    require(null["returned_circuit_repeats"] == 2 * SLOTS * len(LABELS), "matched requests lost their circuit identity")
    seeded = run({"seed": [0.03, -0.03, 0.02, -0.02]})
    require(seeded["branch"] == "seed", f"a seed-dependent response read {seeded['branch']}")
    drifting = run({"block": 0.04})
    require(drifting["branch"] == "stationarity", f"a block-dependent response read {drifting['branch']}")
    common = run({"seed": [-0.03] * SLOTS})
    require(common["branch"] == "common-effect", f"a common residual read {common['branch']}")
    broken = copy.deepcopy(next(iter(jobs.values())))
    broken["settings"][0]["compilation_seed"] = 9
    try:
        observations(
            broken,
            synthetic_result(
                next(iter(jobs.values())), {(s["block"], s["name"], s["slot"]): 0.5 for s in broken["settings"]}, 1
            ),
        )
    except ValueError:
        pass
    else:
        raise ValueError("an iteration that ran another seed was admitted")
    print("bdsc diagnostic self-test: counting, seed, block and common-residual responses read their branches")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--readout", type=Path, nargs="+")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--draw", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.draw)
    elif args.check:
        check(args.draw)
    elif args.readout:
        print(json.dumps(readout(args.readout), indent=1))
    else:
        return self_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
