"""Belenos crossed variance-identification case: target-complement states x templates x seeds x blocks, and its readout.

The case separates the response components that one compilation per setting
confounds: counting noise, a matched request's change between two acquisition
blocks, differences across compilation seeds of one state, the template, and
state-by-seed interaction. Its instances are the six target-complement states
of docs/evidence/bdsc/qualification_case.json under both preparation
templates, compiled with each of four seeds, in each of two blocks: 96
instances of 40000 eligible trials under an explicit empty mitigation list.

Every (template, seed) group of six states runs inside one job, so its two
sum-rule residuals compare iterations of one job. A block runs two jobs of 24
iterations; block 1 places outward seeds 0 and 1 with reverse seeds 2 and 3 in
its first job and the complement in its second, and block 2 swaps the two
assignments, so job position never aliases a seed or template across blocks.
A compiled circuit is a function of the seed, the parameters and the
compiler's component model (docs/evidence/bdsc/forensics/forensics.json,
compilation_determinism), so block 2 repeats block 1's returned circuits
while that model holds. The readout compares each matched pair's returned
circuit and reads a changed one as a recompiled request, never as drift.
Job b2-j1 repeats exactly the groups of b1-j2, so --matched-check compares
their returned-circuit hashes after b2-j1 is collected and before b2-j2 is
submitted; a mismatch stops the case.

The target-complement bank sends f to one output mode and g to another and
splits every superposition equally between them. The provider reports
result_fields.physical_perf per iteration; it moves with the requested sample
budget and DetectorBalancing rescales it (docs/notes/quandela/strategy.md), so
it is no qualified output acceptance. Its ratio r-hat = perf_g / (perf_f +
perf_g) of a group's f and g iterations tracked the superposition mean in the
retained jobs, so the analysis reports r-hat per block, template and seed and
each superposition's deviation p(state) - r-hat as an uninterpreted provider
diagnostic (perf_ratio); no branch reads it and no cause is attributed to it. The
block-change statistic splits into a per-class common shift
(calibration_shift of the superpositions, f and g) and a heterogeneity test about
the class means, which is the statistic the stationarity branch reads. The
seed dispersion splits into the basis states f and g (seed_basis, no branch)
and the four superpositions (seed_superposition, the statistic the seed
branches read). The readout also reports whether out and rev circuits of one
seed alias, how many distinct circuits the four superpositions of a group
returned, the rank correlation of the superposition deviation with position in
the job, and flags every instance that put more than LEAK_SHARE of its
one-click samples outside the target support as a leak.

Without --draw the case directories read draft and carry no seeds or order.
With --draw (an scripts/anu_qrng.py record of at least 100 uint16 values) the
first four values, which must be distinct, seed slots 0 to 3, and value 4 + i
orders block-1 instance i within its job; a block-2 instance takes the order
value of its block-1 match (same template, seed slot and state), so every
matched pair runs at the same position and a within-job position trend cancels
in each block change. --check without --draw reads the record the
committed manifests name, so the gate holds before and after the draw.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic.py --write [--draw FILE]
  "$PYTHON" scripts/bdsc_diagnostic.py --check [--draw FILE]
  "$PYTHON" scripts/bdsc_diagnostic.py --readout RUN_DIR...
  "$PYTHON" scripts/bdsc_diagnostic.py --matched-check B1J2_RUN B2J1_RUN
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
import bdsc_forensics as forensics  # noqa: E402

import parallel  # noqa: E402

CASE = ROOT / "docs/evidence/bdsc/diagnostic/case.json"
CASES_DIR = ROOT / "results/quandela/cases/bdsc_diagnostic"
FAMILY = "bdsc_diagnostic"
PAIR = "target-complement"
POLICY: list[str] = []
LABELS = ("f", "g", "+", "-", "+i", "-i")
# The superposition states share one ideal response, so a common seed offset across them is identifiable apart from
# state-specific seed effects; the basis states f and g enter the per-state seed dispersion only.
SUPERPOSITIONS = ("+", "-", "+i", "-i")
BASIS = ("f", "g")
# Block-change classes: the mean change of each class is the calibration shift, and the changes about those means
# carry the heterogeneity statistic. f and g are separate classes because their output efficiencies drift
# independently (physical_perf), so a shift of one must not read as heterogeneity of the other.
CLASSES = {"superposition": SUPERPOSITIONS, "f": ("f",), "g": ("g",)}
# An instance whose one-click samples fall outside the target support (modes with column weight above
# bdsc_forensics.SUPPORT_FLOOR) by more than this share is a leak outlier.
LEAK_SHARE = 0.20
SLOTS = 4
BLOCKS = (1, 2)
TRIALS = 40000
MAX_SHOTS = 2 * TRIALS
# Billing and timing rules of docs/runbooks/quandela-credit-optimization.md, measured on retained qpu:belenos jobs.
CREDIT_PER_JOB = 1.0
CREDIT_PER_SHOT = 1e-6
SECONDS_PER_ITERATION = 6.3
SECONDS_PER_SAMPLE = 2.6e-5
# Block 2 waits this long after block 1's last execution ends, so the blocks are separated in time.
BLOCK_GAP_HOURS = 1
# A pooled chi-square of observed dispersion against its reference counting errors reads resolved below ALPHA,
# consistent at or above CONSISTENT_P, and inconclusive between.
ALPHA = 0.01
CONSISTENT_P = 0.05
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


def job_groups(job: str) -> set[tuple[str, int]]:
    """The (template, seed slot) groups a job runs."""
    return {(i["template"], i["slot"]) for i in instances() if i["job"] == job}


def matched_pairs() -> list[tuple[int, int]]:
    """(index in b1-j2, index in b2-j1) of every instance the two jobs request identically.

    b2-j1 must repeat exactly the groups of b1-j2: the matched-check gate compares their returned circuits before
    b2-j2 is submitted, and a layout that breaks the equality leaves that gate comparing unlike requests.
    """
    items = instances()
    require(job_groups("b1-j2") == job_groups("b2-j1"), "b2-j1 does not repeat the groups of b1-j2")
    first = {(i["template"], i["slot"], i["label"]): i["index"] for i in items if i["job"] == "b1-j2"}
    second = {(i["template"], i["slot"], i["label"]): i["index"] for i in items if i["job"] == "b2-j1"}
    require(first.keys() == second.keys(), "b2-j1 does not repeat the instances of b1-j2")
    return [(first[k], second[k]) for k in sorted(first)]


def order_index(index: int) -> int:
    """The instance whose drawn order value positions this one: itself in block 1, its block-1 match in block 2.

    A block-2 instance repeats the block-1 request of the same template, seed slot and state, and both members of
    a matched pair sit in jobs holding the same groups, so a shared order value puts them at the same position.
    """
    items = instances()
    item = items[index]
    if item["block"] == BLOCKS[0]:
        return index
    first = {(i["template"], i["slot"], i["label"]): i["index"] for i in items if i["block"] == BLOCKS[0]}
    return first[(item["template"], item["slot"], item["label"])]


def instance_name(item: dict[str, Any]) -> str:
    tag = bdsc_cases.TEMPLATE_TAGS[item["template"]]
    return f"{tag}-s{item['slot']}-{bdsc_cases.LABEL_TAGS[item['label']]}"


def case_record() -> dict[str, Any]:
    """The frozen design, layout, resources, analysis and stop conditions of the diagnostic case."""
    items = instances()
    matched_pairs()
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
            "use": "the first four values, which must be distinct, seed slots 0 to 3; value 4 + i orders block-1 "
            "instance i within its job, and a block-2 instance takes the order value of its block-1 match so matched "
            "pairs share a position",
        },
        "analysis": {
            "observation": "one-click conditioned selected fraction of returned counts; every standard error is a "
            "reference value under independent Bernoulli trials, which the provider contract has not established",
            "residuals": "Delta_R and Delta_I per block, template and seed, each from one job; the beyond-margin "
            "rule reads these raw residuals",
            "perf_ratio": "per block, template and seed, r-hat = perf_g / (perf_f + perf_g) from that group's f and "
            "g iterations (result_fields.physical_perf, a provider field that moves with the sample budget and that "
            "DetectorBalancing rescales, so no qualified output acceptance); the readout reports r-hat, each "
            "superposition's deviation p(state) - r-hat and their RMS as an uninterpreted diagnostic that no branch "
            "reads",
            "block_change": "p(block 2) - p(block 1) per instance whose pair returned one circuit, split by class "
            "(the four superpositions; f; g, each its own class because their output efficiencies drift apart). "
            "calibration_shift reports each class's inverse-variance mean change "
            "with its z; block_change is the chi-square of the changes about their class means (heterogeneity), "
            "the statistic the stationarity branch reads. A common shift is a calibration shift, not stationarity",
            "seed_dispersion": "pooled chi-square of the four seeds about their inverse-variance mean per block, "
            "template and state: seed_basis over f and g, reported and read by no branch, and seed_superposition "
            "over the four superpositions, which the seed branches read; residual_seed does the same per block, "
            "template and residual family",
            "seed_split": "per block and template, a weighted two-way fit of the four superposition states by state "
            "and seed: the drop in chi-square from the state-only to the additive fit tests a common seed offset "
            "(3 df each), and the additive fit's residual chi-square tests state-by-seed interaction (9 df each)",
            "template_effect": "seed-mean outward minus reverse per block and state; reported, no branch reads it",
            "aliasing": "per block, seed slot and state, whether the outward and reverse returned circuits are "
            "hash-equal; per block, template and seed, how many distinct hashes the four superpositions returned; "
            "effective_compilations summarizes both. Reported, no branch reads it",
            "position": "per job, the Spearman correlation of the superposition deviation p(state) - r-hat with "
            "position in the job (the drawn order). Reported, no branch reads it",
            "leak": f"every instance whose one-click samples fall outside the target support (modes with column "
            f"weight above {forensics.SUPPORT_FLOOR}) by more than {LEAK_SHARE} is listed in leak_outliers",
            "tests": f"resolved at p < {ALPHA}, consistent at p >= {CONSISTENT_P}, inconclusive between",
            "residual_margin": "a residual exceeds the margin when |Delta| minus its simultaneous normal quantile "
            f"at {ALPHA} over all 32 residuals times its reference error exceeds the margin",
            "branches": {
                "recompiled": "a matched pair returned different circuits: the blocks compare requests, the "
                "compiler's model changed, and the case reruns before any branch is read",
                "leak": f"an instance put more than {LEAK_SHARE} of its one-click samples outside the target "
                "support; read the failure before any other component",
                "stationarity": "matched requests change between blocks beyond their class means: address "
                "stationarity and provider calibration before any fixed-effect confirmation",
                "seed-common": "seeds shift the superposition states together: study seed selection on "
                "development data and validate a frozen selection on fresh data",
                "seed-interaction": "seed effects differ between superposition states: a seed selection cannot "
                "transfer across states, so study the per-state compilation before any seed choice",
                "common-effect": "seed dispersion is small but residuals persist beyond the margin: investigate "
                "preparation, filtering and processing, including unequal output acceptance, which only a qualified "
                "per-mode acceptance measurement can test; more seeds are not the remedy",
                "inconclusive": "no component resolved and one test inconclusive, or a resolved common seed offset "
                "beside an inconclusive interaction test: more compilations or trials before a branch",
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
            "an iteration returns no compiled circuit or no positive result_fields.physical_perf",
            "block 2 starts before both block-1 runs are collected and their readout integrity passes, or before "
            "the block gap elapses",
            "--matched-check on b1-j2 and b2-j1, run after b2-j1 is collected and before b2-j2 is submitted, finds "
            "a returned-circuit hash that differs for a matched instance",
            "a job of a block executes before the job that precedes it in the block, or a manifest differs from "
            "the frozen rebuild for its draw",
            "a scheduled maintenance window overlaps the span from block 1's first execution to block 2's last; "
            "the pair then waits and reruns both blocks on one side of the window",
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
            if isinstance(named, dict):
                hit = named.get("sha256") == binding["sha256"]
            else:
                # Older cases name the record by file name.
                hit = isinstance(named, str) and named == Path(binding["record"]).name
            if hit and manifest.get("diagnostic_case_sha256") != case_sha:
                claims.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
    return claims


def _params(item: tuple[str, Any, int]) -> Any:
    template, column, source = item
    return cert.union_params(template, column, source, modes=cert.MODES)


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
    keys = [(template, label) for template in cert.PREPARATION_DESCRIPTIONS for label in LABELS]
    solved = parallel.ordered_map(_params, [(t, chip[(PAIR, label)], source) for t, label in keys], min_items=1)
    params = dict(zip(keys, solved, strict=True))
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
            members.sort(key=lambda i: (drawn[1][order_index(i["index"])], order_index(i["index"])))
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
                setting["draw_indices"] = {"seed": item["slot"], "order": SLOTS + order_index(item["index"])}
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
    if draw is None:
        named = json.loads((CASES_DIR / "b1-j1" / "cases.json").read_text(encoding="utf-8")).get("draw")
        draw = ROOT / named["record"] if isinstance(named, dict) else None
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


def reading(p_value: float) -> str:
    return "resolved" if p_value < ALPHA else "consistent" if p_value >= CONSISTENT_P else "inconclusive"


def dispersion(groups: list[list[tuple[float, float]]]) -> tuple[float, int]:
    """Pooled chi-square of each group's (value, reference error) pairs about its inverse-variance mean, and its df."""
    statistic, df = 0.0, 0
    for group in groups:
        weights = [1 / s**2 for _, s in group]
        mean = sum(w * v for w, (v, _) in zip(weights, group, strict=True)) / sum(weights)
        statistic += sum(w * (v - mean) ** 2 for w, (v, _) in zip(weights, group, strict=True))
        df += len(group) - 1
    return statistic, df


def weighted_residual(design: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    """Residual chi-square sum w (y - design beta)^2 of the weighted least-squares fit."""
    root = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(design * root[:, None], y * root, rcond=None)
    return float(np.sum(w * (y - design @ beta) ** 2))


def seed_split(groups: list[dict[tuple[str, int], tuple[float, float]]]) -> tuple[float, int, float, int]:
    """(common-seed statistic, df, interaction statistic, df) pooled over groups keyed by (state, seed slot).

    Each group is fitted by weighted least squares with weights 1/se^2, first by state alone and then by state plus
    seed; the chi-square drop is the common-seed statistic and the additive fit's residual chi-square the interaction.
    """
    common = interaction = 0.0
    common_df = interaction_df = 0
    for group in groups:
        states = sorted({state for state, _ in group})
        slots = sorted({slot for _, slot in group})
        cells = sorted(group)
        y = np.array([group[c][0] for c in cells])
        w = np.array([1 / group[c][1] ** 2 for c in cells])
        state_cols = np.array([[float(c[0] == state) for state in states] for c in cells])
        slot_cols = np.array([[float(c[1] == slot) for slot in slots[1:]] for c in cells])
        state_only = weighted_residual(state_cols, y, w)
        additive = weighted_residual(np.hstack([state_cols, slot_cols]), y, w)
        common += state_only - additive
        interaction += additive
        common_df += len(slots) - 1
        interaction_df += (len(states) - 1) * (len(slots) - 1)
    return common, common_df, interaction, interaction_df


def class_of(label: str) -> str:
    return "superposition" if label in SUPERPOSITIONS else label


def analyse(observed: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Residuals, acceptance, block changes, seed dispersion, aliasing, leaks, their tests and the branch.

    observed maps each instance index to its selected and eligible counts, returned-circuit sha256, physical_perf,
    outside-support share of one-click samples and position in its job.
    """
    from scipy.stats import chi2, norm, spearmanr

    items = instances()
    require(sorted(observed) == [i["index"] for i in items], "the readout needs every instance")
    matched_pairs()
    key = {(i["block"], i["template"], i["slot"], i["label"]): i["index"] for i in items}

    def p(b: int, t: str, s: int, label: str) -> float:
        o = observed[key[(b, t, s, label)]]
        return o["selected"] / o["eligible"]

    def se(b: int, t: str, s: int, label: str) -> float:
        o = observed[key[(b, t, s, label)]]
        return reference_se(o["selected"] / o["eligible"], o["eligible"])

    def rhat(b: int, t: str, s: int) -> float:
        return observed[key[(b, t, s, "g")]]["perf"] / (
            observed[key[(b, t, s, "f")]]["perf"] + observed[key[(b, t, s, "g")]]["perf"]
        )

    for item in observed.values():
        require(item["perf"] > 0, "physical_perf must be positive")
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
    r_hats: list[dict[str, Any]] = []
    deviations: list[dict[str, Any]] = []
    for b in BLOCKS:
        for t in templates:
            for s in range(SLOTS):
                r = rhat(b, t, s)
                r_hats.append(
                    {
                        "block": b,
                        "template": t,
                        "slot": s,
                        "perf_f": observed[key[(b, t, s, "f")]]["perf"],
                        "perf_g": observed[key[(b, t, s, "g")]]["perf"],
                        "r_hat": r,
                    }
                )
                for label in SUPERPOSITIONS:
                    deviations.append(
                        {
                            "block": b,
                            "template": t,
                            "slot": s,
                            "label": label,
                            "fraction": p(b, t, s, label),
                            "r_hat": r,
                            "deviation": p(b, t, s, label) - r,
                            "se": se(b, t, s, label),
                        }
                    )
    r_values = [r["r_hat"] for r in r_hats]
    acceptance = {
        "r_hat": r_hats,
        "r_hat_summary": {"min": min(r_values), "max": max(r_values), "mean": float(np.mean(r_values))},
        "deviations": deviations,
        "deviation_rms": math.sqrt(float(np.mean([d["deviation"] ** 2 for d in deviations]))),
        "residual_rms": math.sqrt(float(np.mean([r["value"] ** 2 for r in residuals]))),
        "reading": "diagnostic only: the uncertainty of a deviation exceeds the margin, so no branch reads it",
    }
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
    seed_groups = {
        name: [
            [(p(b, t, s, label), se(b, t, s, label)) for s in range(SLOTS)]
            for b in BLOCKS
            for t in templates
            for label in labels
        ]
        for name, labels in (("seed_basis", BASIS), ("seed_superposition", SUPERPOSITIONS))
    }
    residual_groups = [
        [(r["value"], r["se"]) for r in residuals if (r["block"], r["template"], r["family"]) == (b, t, family)]
        for b in BLOCKS
        for t in templates
        for family in ("delta_R", "delta_I")
    ]
    split_groups = [
        {(label, s): (p(b, t, s, label), se(b, t, s, label)) for label in SUPERPOSITIONS for s in range(SLOTS)}
        for b in BLOCKS
        for t in templates
    ]
    template_effect: list[dict[str, Any]] = []
    for b in BLOCKS:
        for label in LABELS:
            effect = float(np.mean([p(b, templates[0], s, label) - p(b, templates[1], s, label) for s in range(SLOTS)]))
            ref = math.sqrt(sum(se(b, t, s, label) ** 2 for t in templates for s in range(SLOTS))) / SLOTS
            template_effect.append({"block": b, "label": label, "effect": effect, "se": ref})
    repeated = [c for c in changes if c["same_returned_circuit"]]
    tests: dict[str, dict[str, Any]] = {}
    calibration_shift: dict[str, dict[str, Any]] = {}
    if repeated:
        heterogeneity, df = 0.0, 0
        for name in CLASSES:
            members = [c for c in repeated if class_of(c["label"]) == name]
            if not members:
                continue
            weights = [1 / c["se"] ** 2 for c in members]
            mean = sum(w * c["change"] for w, c in zip(weights, members, strict=True)) / sum(weights)
            mean_se = 1 / math.sqrt(sum(weights))
            p_shift = float(2 * norm.sf(abs(mean / mean_se)))
            calibration_shift[name] = {
                "n": len(members),
                "mean": mean,
                "se": mean_se,
                "z": mean / mean_se,
                "p_value": p_shift,
                "reading": reading(p_shift),
            }
            heterogeneity += sum(w * (c["change"] - mean) ** 2 for w, c in zip(weights, members, strict=True))
            df += len(members) - 1
        tests["block_change"] = {"statistic": heterogeneity, "df": df}
    for name, groups in (*seed_groups.items(), ("residual_seed", residual_groups)):
        statistic, df = dispersion(groups)
        tests[name] = {"statistic": statistic, "df": df}
    common, common_df, interaction, interaction_df = seed_split(split_groups)
    tests["seed_common"] = {"statistic": common, "df": common_df}
    tests["seed_interaction"] = {"statistic": interaction, "df": interaction_df}
    tests["template"] = {
        "statistic": sum((x["effect"] / x["se"]) ** 2 for x in template_effect),
        "df": len(template_effect),
    }
    for test in tests.values():
        test["p_value"] = float(chi2.sf(test["statistic"], test["df"]))
        test["reading"] = reading(test["p_value"])
    # A residual exceeds the margin when its simultaneous lower bound over all residuals clears it.
    z = float(norm.isf(ALPHA / (2 * len(residuals))))
    beyond = [r for r in residuals if abs(r["value"]) - z * r["se"] > MARGIN]
    template_pairs: list[dict[str, Any]] = [
        {
            "block": b,
            "slot": s,
            "label": label,
            "equal": observed[key[(b, templates[0], s, label)]]["circuit_sha256"]
            == observed[key[(b, templates[1], s, label)]]["circuit_sha256"],
        }
        for b in BLOCKS
        for s in range(SLOTS)
        for label in LABELS
    ]
    superposition_groups: list[dict[str, Any]] = [
        {
            "block": b,
            "template": t,
            "slot": s,
            "distinct_circuits": len({observed[key[(b, t, s, label)]]["circuit_sha256"] for label in SUPERPOSITIONS}),
        }
        for b in BLOCKS
        for t in templates
        for s in range(SLOTS)
    ]
    aliasing = {
        "template_pairs": template_pairs,
        "superposition_groups": superposition_groups,
        "effective_compilations": {
            "returned_circuits": len({o["circuit_sha256"] for o in observed.values()}),
            "per_block": {
                str(b): len({observed[i["index"]]["circuit_sha256"] for i in items if i["block"] == b}) for b in BLOCKS
            },
            "template_pairs_equal": sum(1 for x in template_pairs if x["equal"]),
            "template_pairs": len(template_pairs),
            "superposition_groups_sharing_circuits": sum(1 for x in superposition_groups if x["distinct_circuits"] < 4),
            "superposition_groups": len(superposition_groups),
        },
    }
    position: dict[str, dict[str, Any]] = {}
    for job in sorted({i["job"] for i in items}):
        indexed = [(key[(d["block"], d["template"], d["slot"], d["label"])], d["deviation"]) for d in deviations]
        points = [(observed[index]["position"], value) for index, value in indexed if items[index]["job"] == job]
        xs, ys = [x for x, _ in points], [y for _, y in points]
        if len(set(ys)) < 2:
            position[job] = {"n": len(points), "rho": None, "p_value": None}
        else:
            rho, p_rho = spearmanr(xs, ys)
            position[job] = {"n": len(points), "rho": float(rho), "p_value": float(p_rho)}
    leak_outliers = [
        {
            "index": i["index"],
            "job": i["job"],
            "block": i["block"],
            "template": i["template"],
            "slot": i["slot"],
            "label": i["label"],
            "outside_support_share": observed[i["index"]]["outside_share"],
        }
        for i in items
        if observed[i["index"]]["outside_share"] > LEAK_SHARE
    ]
    readings = {name: test["reading"] for name, test in tests.items()}
    if len(repeated) < len(changes):
        branch = "recompiled"
    elif leak_outliers:
        branch = "leak"
    elif readings["block_change"] == "resolved":
        branch = "stationarity"
    elif readings["seed_superposition"] == "resolved":
        # Seed dispersion that the common offset does not carry in the superpositions is state-specific; a common
        # offset reads as transferable only once the interaction test is consistent with none.
        if readings["seed_interaction"] == "resolved" or readings["seed_common"] != "resolved":
            branch = "seed-interaction"
        elif readings["seed_interaction"] == "consistent":
            branch = "seed-common"
        else:
            branch = "inconclusive"
    elif beyond:
        branch = "common-effect"
    elif "inconclusive" in (readings["block_change"], readings["seed_superposition"], readings["residual_seed"]):
        branch = "inconclusive"
    else:
        branch = "ensemble-candidate"
    return {
        "residuals": residuals,
        "perf_ratio": acceptance,
        "block_changes": changes,
        "calibration_shift": calibration_shift,
        "template_effect": template_effect,
        "tests": tests,
        "readings": readings,
        "aliasing": aliasing,
        "position": position,
        "leak_outliers": leak_outliers,
        "residuals_beyond_margin": len(beyond),
        "returned_circuit_repeats": len(repeated),
        "branch": branch,
    }


def utc(text: str) -> float:
    import datetime

    return datetime.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()


def admit_run(
    run: Path, validate: bool, context: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """(manifest, result, submission) of one diagnostic run after every integrity check the readout applies.

    validate runs qd_platform.run_facts, binding cases.json, circuit.json, job-body.json and the receipt to one another
    and results.json to raw/result.json; the self-test's synthetic runs carry no receipt or raw result. context holds
    the QRNG draws and the frozen rebuild shared across one call's runs.
    """
    import qd_platform

    record_sha = sha256_bytes(CASE.read_bytes())
    target_sha = json.loads(bdsc_cases.TARGET.read_text(encoding="utf-8"))["target_sha256"]
    draws: dict[str, tuple[list[int], list[int]]] = context.setdefault("draws", {})
    if validate:
        qd_platform.run_facts(run)
    manifest_bytes = (run / "cases.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    result = json.loads((run / "results.json").read_text(encoding="utf-8"))
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    body_bytes = (run / "job-body.json").read_bytes()
    platform = bdsc_cases.QUALIFYING_PLATFORM
    require(submission.get("platform") == platform, f"{run}: submitted to {submission.get('platform')!r}")
    served = result.get("data", {}).get("platform_name")
    require(served == platform, f"{run}: the service reports {served!r}")
    require(submission.get("cases_sha256") == sha256_bytes(manifest_bytes), f"{run}: cases.json changed")
    require(submission.get("body_sha256") == bdsc_cases.body_digest(body_bytes), f"{run}: job-body.json differs")
    require(result.get("job_id") == submission.get("job_id"), f"{run}: the result answers another job")
    require(manifest.get("diagnostic_case_sha256") == record_sha, f"{run}: built from another case record")
    require(manifest.get("target_sha256") == target_sha, f"{run}: built for another target")
    require(manifest.get("mitigations") == POLICY, f"{run}: the manifest policy differs")
    require(qd_platform.body_mitigations(json.loads(body_bytes)) == POLICY, f"{run}: the body's policy differs")
    require(result.get("status", {}).get("status") == "completed", f"{run}: the job did not complete")
    require(result.get("partial") is False, f"{run}: a partial result")
    binding = manifest.get("draw")
    require(isinstance(binding, dict) and not manifest.get("draft", True), f"{run}: no bound QRNG draw")
    if binding["sha256"] not in draws:
        record = ROOT / binding["record"]
        require(sha256_bytes(record.read_bytes()) == binding["sha256"], f"{run}: the QRNG record changed")
        drawn = draw_values(record)
        require(drawn is not None, f"{run}: unreadable QRNG record")
        if drawn is not None:
            draws[binding["sha256"]] = drawn
        rebuilt = documents(record)
        context["frozen"] = {
            job: json.loads(files["cases.json"]) for job, files in rebuilt.items() if isinstance(files, dict)
        }
    require(len(draws) == 1, f"{run}: the runs draw from more than one QRNG record")
    job = manifest.get("job")
    frozen: dict[str, dict[str, Any]] = context["frozen"]
    require(job in frozen, f"{run}: job {job!r} is not a job of the case")
    cert.close(frozen[job], manifest, f"{run}: manifest against the frozen rebuild")
    seeds, order = draws[binding["sha256"]]
    members = [s["instance_index"] for s in manifest["settings"]]
    require(
        members == sorted(members, key=lambda i: (order[order_index(i)], order_index(i))),
        f"{run}: the iterations are not in drawn order",
    )
    for setting in manifest["settings"]:
        require(setting["compilation_seed"] == seeds[setting["slot"]], f"{run}/{setting['name']}: seed not drawn")
        indices = {"seed": setting["slot"], "order": SLOTS + order_index(setting["instance_index"])}
        require(setting["draw_indices"] == indices, f"{run}/{setting['name']}: draw indices")
    return manifest, result, submission


def readout(runs: list[Path], validate: bool = True) -> dict[str, Any]:
    """The analysis of collected qpu:belenos runs of every diagnostic job, after the integrity checks.

    validate runs qd_platform.run_facts on each run, binding cases.json, circuit.json, job-body.json and the receipt to
    one another and results.json to raw/result.json; the self-test's synthetic runs carry no receipt or raw result.
    """
    observed: dict[int, dict[str, Any]] = {}
    frozen: dict[str, dict[str, Any]] = {}
    windows: dict[str, tuple[float, float]] = {}
    collected: dict[str, float] = {}
    maintenance: set[tuple[float, float]] = set()
    context: dict[str, Any] = {}
    for run in runs:
        manifest, result, submission = admit_run(run, validate, context)
        job = manifest["job"]
        frozen = context["frozen"]
        require(job not in windows, f"{run}: job {job} collected twice")
        start = utc(result["data"]["start_time"])
        windows[job] = (start, start + float(result["data"]["duration"]))
        collected[job] = utc(result["collected_utc"])
        window = submission.get("platform_at_plan", {}).get("maintenance")
        if isinstance(window, dict):
            maintenance.add((utc(window["start_time"]), utc(window["end_time"])))
        for index, item in observations(manifest, result).items():
            require(index not in observed, f"{run}: instance {index} collected twice")
            observed[index] = item
    require(sorted(windows) == sorted(frozen), f"the readout needs every job; it holds {sorted(windows)}")
    for block in BLOCKS:
        require(
            windows[f"b{block}-j1"][1] <= windows[f"b{block}-j2"][0],
            f"block {block}: job 2 started before job 1 ended, so job position aliases the seed assignment",
        )
    first_end = max(end for job, (_, end) in windows.items() if job.startswith("b1"))
    second_start = min(start for job, (start, _) in windows.items() if job.startswith("b2"))
    require(second_start >= first_end + 3600 * BLOCK_GAP_HOURS, "block 2 started within the block gap")
    # Block 1's integrity is checked on its collected records, so both must exist before block 2 executes.
    require(
        all(collected[job] < second_start for job in collected if job.startswith("b1")),
        "block 2 started before block 1 was collected and checked",
    )
    span = (min(start for start, _ in windows.values()), max(end for _, end in windows.values()))
    require(
        not any(opens < span[1] and closes > span[0] for opens, closes in maintenance),
        "a scheduled maintenance window overlaps the acquisition",
    )
    return analyse(observed)


def observations(manifest: dict[str, Any], result: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Per-instance one-click tallies of one job, with seed, parameter, sample and eligibility checks.

    Each item also carries the iteration's physical_perf, the share of its one-click samples outside the target
    support (modes with column weight above forensics.SUPPORT_FLOOR) and its position in the job.
    """
    out = {}
    iterations = result["iterations"]
    require(len(iterations) == len(manifest["settings"]), f"{manifest['job']}: iteration count differs")
    for position, (setting, iteration) in enumerate(zip(manifest["settings"], iterations, strict=True)):
        ran = iteration["iteration"]
        echoed = ran.get("circuit_params") or {}
        owner = f"{manifest['job']}/{setting['name']}"
        require(
            echoed.keys() == setting["circuit_params"].keys()
            and all(
                abs(echoed[x] - v) <= bdsc_cases.PARAM_ECHO_TOLERANCE for x, v in setting["circuit_params"].items()
            ),
            f"{owner}: parameters",
        )
        require(ran.get("compilation_seed") == setting["compilation_seed"], f"{owner}: seed")
        require(iteration.get("samples") == TRIALS, f"{owner}: samples")
        counted = bdsc_cases.tally(iteration["counts"], manifest["selected_modes"])
        require(counted["eligible"] >= (1 - cert.ELIGIBLE_LOSS) * TRIALS, f"{owner}: eligible")
        circuit = iteration.get("result_fields", {}).get("computed_circuit")
        require(isinstance(circuit, str), f"{owner}: no compiled circuit")
        perf = iteration.get("result_fields", {}).get("physical_perf")
        require(isinstance(perf, (int, float)) and not isinstance(perf, bool) and perf > 0, f"{owner}: physical_perf")
        per_mode, _, _ = forensics.one_click(iteration["counts"], cert.MODES)
        weight = np.abs(forensics.column(setting)) ** 2
        on_support = sum(per_mode[m] for m in range(cert.MODES) if weight[m] > forensics.SUPPORT_FLOOR)
        out[setting["instance_index"]] = {
            "selected": counted["selected"],
            "eligible": counted["eligible"],
            "circuit_sha256": hashlib.sha256(circuit.encode()).hexdigest(),
            "perf": float(perf),
            "outside_share": 1 - on_support / counted["eligible"],
            "position": position,
        }
    return out


def matched_check(b1j2: Path, b2j1: Path, validate: bool = True) -> list[str]:
    """Matched instances of b1-j2 and b2-j1 whose returned-circuit hashes differ, one line each.

    The two jobs request the same groups with the same seeds and parameters (matched_pairs), so a differing hash is
    a recompiled request. Each run first passes every integrity check of the readout (admit_run): qpu:belenos
    submitted and served, completed and not partial, the current case, the empty policy, the bound QRNG draw and
    the frozen manifest, so only a valid b2-j1 can clear the checkpoint before b2-j2.
    """
    items = instances()
    context: dict[str, Any] = {}
    loaded: dict[str, tuple[dict[str, Any], dict[int, dict[str, Any]]]] = {}
    for run, job in ((b1j2, "b1-j2"), (b2j1, "b2-j1")):
        manifest, result, _ = admit_run(run, validate, context)
        require(manifest.get("job") == job, f"{run}: job {manifest.get('job')!r}, expected {job}")
        loaded[job] = (manifest, observations(manifest, result))
    requested = {
        job: {s["instance_index"]: (s["compilation_seed"], s["circuit_params"]) for s in manifest["settings"]}
        for job, (manifest, _) in loaded.items()
    }
    out = []
    for first, second in matched_pairs():
        require(
            requested["b1-j2"][first] == requested["b2-j1"][second],
            f"{instance_name(items[first])}: the two jobs request different seeds or parameters",
        )
        if loaded["b1-j2"][1][first]["circuit_sha256"] != loaded["b2-j1"][1][second]["circuit_sha256"]:
            out.append(f"{instance_name(items[first])}: b2-j1 returned another circuit than b1-j2")
    return out


def run_matched_check(b1j2: Path, b2j1: Path, validate: bool = True) -> int:
    """Print the matched-check verdict; 0 when every matched hash is equal, 1 on any mismatch."""
    mismatches = matched_check(b1j2, b2j1, validate)
    if mismatches:
        print(
            f"bdsc diagnostic matched check: {len(mismatches)} of {len(matched_pairs())} matched instances "
            "returned another circuit; stop before submitting b2-j2",
            file=sys.stderr,
        )
        for line in mismatches:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"bdsc diagnostic matched check: all {len(matched_pairs())} matched returned circuits are equal")
    return 0


def synthetic_runs(
    root: Path, manifests: dict[str, dict[str, Any]], response: Any, edit: Any = None, perf: Any = None
) -> list[Path]:
    """Collected run directories whose one-click counts draw from response(setting); edit may alter any record.

    perf(setting) is the iteration's physical_perf, 0.078 when absent.
    """
    import qd_platform

    body = bdsc_cases.synthetic_body(POLICY)
    starts = {"b1-j1": 0.0, "b1-j2": 400.0, "b2-j1": 8000.0, "b2-j2": 8400.0}
    base = utc("2026-01-01T00:00:00Z")
    runs = []
    for k, (job, original) in enumerate(sorted(manifests.items())):
        manifest = copy.deepcopy(original)
        rng = np.random.default_rng(300 + k)
        selected = manifest["selected_modes"][0]
        other = next(m for m in range(cert.MODES) if m not in manifest["selected_modes"])
        iterations = []
        for setting in manifest["settings"]:
            hits = int(rng.binomial(TRIALS, response(setting)))
            hit, miss = ["0"] * cert.MODES, ["0"] * cert.MODES
            hit[selected], miss[other] = "1", "1"
            iterations.append(
                {
                    "counts": {",".join(hit): hits, ",".join(miss): TRIALS - hits},
                    "iteration": {
                        "circuit_params": setting["circuit_params"],
                        "compilation_seed": setting["compilation_seed"],
                    },
                    "result_fields": {
                        "computed_circuit": f"{setting['compilation_seed']} {setting['name']}",
                        "physical_perf": 0.078 if perf is None else perf(setting),
                    },
                    "samples": TRIALS,
                }
            )
        import datetime

        start = datetime.datetime.fromtimestamp(base + starts[job], datetime.UTC).isoformat()
        result = {
            "job_id": job,
            "status": {"status": "completed"},
            "partial": False,
            "data": {"platform_name": bdsc_cases.QUALIFYING_PLATFORM, "start_time": start, "duration": 160},
            "collected_utc": datetime.datetime.fromtimestamp(base + starts[job] + 220, datetime.UTC).isoformat(),
            "iterations": iterations,
        }
        maintenance = {"start_time": "2026-02-01T00:00:00Z", "end_time": "2026-02-01T03:00:00Z"}
        submission = {
            "platform": bdsc_cases.QUALIFYING_PLATFORM,
            "job_id": job,
            "platform_at_plan": {"maintenance": maintenance},
        }
        if edit is not None:
            edit(job, manifest, result, submission)
        run = root / job
        run.mkdir()
        manifest_bytes = (json.dumps(manifest, indent=1) + "\n").encode()
        (run / "cases.json").write_bytes(manifest_bytes)
        (run / "job-body.json").write_bytes(body)
        submission["cases_sha256"] = sha256_bytes(manifest_bytes)
        submission["body_sha256"] = bdsc_cases.body_digest(body)
        qd_platform.write_json(run / "results.json", result)
        qd_platform.write_json(run / "submission.json", submission)
        runs.append(run)
    return runs


def self_test() -> int:
    """Synthetic runs with a known component read into the branch it predicts; malformed runs are refused."""
    import tempfile

    base = {"f": 0.003, "g": 0.986}
    sup = (base["f"] + base["g"]) / 2

    def label(setting: dict[str, Any]) -> str:
        return next(k for k, tag in bdsc_cases.LABEL_TAGS.items() if setting["name"].endswith(f"-{tag}"))

    def response(
        seed: list[float] | None = None,
        drift: float = 0.0,
        common: float = 0.0,
        odd: bool = False,
        g_drift: float = 0.0,
        accept: Any = None,
        endpoint: list[float] | None = None,
        het: float = 0.0,
    ) -> Any:
        """Selected-fraction model: seed shifts and a block drift on the superpositions, which sit at accept(setting)
        when given; endpoint shifts g by seed; het shifts block 2 with zero mean over (template, seed) groups."""

        def at(setting: dict[str, Any]) -> float:
            lab = label(setting)
            if lab in base:
                shift = (endpoint or [0.0] * SLOTS)[setting["slot"]] if lab == "g" else 0.0
                moved = g_drift * (setting["block"] - 1) if lab == "g" else 0.0
                return base[lab] + shift + moved
            centre = sup if accept is None else accept(setting)
            shift = (seed or [0.0] * SLOTS)[setting["slot"]] * (-1 if odd and lab in ("-", "-i") else 1)
            sign = 1 if (setting["slot"] + (setting["preparation"] == cert.PREPARATION_DESCRIPTIONS[0])) % 2 else -1
            return centre + shift + common + (drift + het * sign) * (setting["block"] - 1)

        return at

    def accepting(setting: dict[str, Any]) -> float:
        """Output acceptance ratio r-hat of a group: unequal between the two templates, equal across seeds."""
        return 0.485 if setting["preparation"] == cert.PREPARATION_DESCRIPTIONS[0] else 0.495

    def perf(setting: dict[str, Any]) -> float:
        r = accepting(setting)
        return 0.078 * r / (1 - r) if label(setting) == "g" else 0.078

    # (name, response model, perf model, expected branch(es), expectation check on the readout)
    cases = [
        # Under counting noise alone the inconclusive branch is a preregistered null reading: it fires when any of
        # three calibrated tests lands in [ALPHA, CONSISTENT_P), about one null draw in eleven.
        ("counting only", response(), None, ("ensemble-candidate", "inconclusive"), None),
        ("common seed shifts", response(seed=[0.008, -0.008, 0.006, -0.006]), None, "seed-common", None),
        (
            "state-specific seed shifts cancelling in each residual",
            response(seed=[0.02, -0.02, 0.01, -0.01], odd=True),
            None,
            "seed-interaction",
            None,
        ),
        (
            "common block shift",
            response(drift=0.012),
            None,
            ("ensemble-candidate", "inconclusive"),
            lambda read: (
                read["calibration_shift"]["superposition"]["reading"] == "resolved"
                and read["readings"]["block_change"] != "resolved"
            ),
        ),
        ("heterogeneous block shift", response(het=0.012), None, "stationarity", None),
        (
            "a block shift of g alone",
            response(g_drift=0.005),
            None,
            ("ensemble-candidate", "inconclusive"),
            lambda read: (
                read["calibration_shift"]["g"]["reading"] == "resolved"
                and read["readings"]["block_change"] != "resolved"
            ),
        ),
        ("common residual", response(common=-0.03), None, "common-effect", None),
        (
            "unequal output acceptance within the margin",
            response(accept=accepting),
            perf,
            ("ensemble-candidate", "inconclusive"),
            lambda read: (
                read["perf_ratio"]["deviation_rms"] < 0.006
                and read["perf_ratio"]["residual_rms"] > 2 * read["perf_ratio"]["deviation_rms"]
                and 0.48 < read["perf_ratio"]["r_hat_summary"]["min"] < read["perf_ratio"]["r_hat_summary"]["max"] < 0.5
            ),
        ),
        (
            "endpoint-only seed scatter",
            response(endpoint=[0.004, -0.004, 0.003, -0.003]),
            None,
            ("ensemble-candidate", "inconclusive"),
            lambda read: (
                read["readings"]["seed_basis"] == "resolved" and read["readings"]["seed_superposition"] != "resolved"
            ),
        ),
    ]
    # The QRNG record must sit inside the repository, so the synthetic one goes under the ignored docs/local.
    scratch_root = ROOT / "docs/local"
    scratch_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch_root) as scratch:
        root = Path(scratch)
        draw = bdsc_cases.synthetic_draw(root, DRAW_VALUES // 2)
        manifests = {k: json.loads(v["cases.json"]) for k, v in documents(draw).items() if isinstance(v, dict)}
        # Every block-2 instance sits at the position of its block-1 match, so position cancels in each block change.
        position = {
            s["instance_index"]: k for manifest in manifests.values() for k, s in enumerate(manifest["settings"])
        }
        for item in instances():
            if item["block"] != BLOCKS[0]:
                match = order_index(item["index"])
                require(
                    position[item["index"]] == position[match],
                    f"self-test: {instance_name(item)} sits at {position[item['index']]}, its match at "
                    f"{position[match]}",
                )
        for n, (name, model, perf_model, expected, holds) in enumerate(cases):
            (root / str(n)).mkdir()
            read = readout(validate=False, runs=synthetic_runs(root / str(n), manifests, model, perf=perf_model))
            got = read["branch"]
            allowed = expected if isinstance(expected, tuple) else (expected,)
            require(got in allowed, f"self-test: {name} read {got}, expected {expected}")
            require(not read["leak_outliers"], f"self-test: {name} flagged a leak")
            if holds is not None:
                require(holds(read), f"self-test: {name} violated its expectation")
            if name == "counting only":
                resolved = [k for k, reading in read["readings"].items() if reading == "resolved"]
                require(not resolved, f"self-test: {name} resolved {resolved} under counting noise alone")
                require(
                    all(x["reading"] != "resolved" for x in read["calibration_shift"].values()),
                    f"self-test: {name} resolved a calibration shift",
                )
                require(read["aliasing"]["effective_compilations"]["template_pairs_equal"] == 0, "self-test: aliasing")
                require(
                    read["aliasing"]["effective_compilations"]["returned_circuits"] == len(instances()) // 2,
                    "self-test: effective compilations",
                )
                require(all(v["n"] == 16 for v in read["position"].values()), "self-test: position report")

        def leaking(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job == "b1-j1":
                counts = result["iterations"][3]["counts"]
                miss = max(counts, key=lambda k: counts[k])
                moved = ["0"] * cert.MODES
                moved[1] = "1"
                share = int(0.3 * TRIALS)
                counts[miss] -= share
                counts[",".join(moved)] = share

        (root / "leak").mkdir()
        read = readout(validate=False, runs=synthetic_runs(root / "leak", manifests, response(), leaking))
        require(read["branch"] == "leak", f"self-test: a leaking instance read {read['branch']}")
        require(len(read["leak_outliers"]) == 1, "self-test: the leak was not isolated to one instance")

        def recompile(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job.startswith("b2"):
                result["iterations"][0]["result_fields"]["computed_circuit"] += " recompiled"

        (root / "recompiled").mkdir()
        runs = synthetic_runs(root / "recompiled", manifests, response(), recompile)
        got = readout(validate=False, runs=runs)["branch"]
        require(got == "recompiled", f"self-test: a changed returned circuit read {got}")
        require(run_matched_check(runs[1], runs[2], validate=False) == 1, "self-test: a matched mismatch passed")
        (root / "matched").mkdir()
        runs = synthetic_runs(root / "matched", manifests, response())
        require(run_matched_check(runs[1], runs[2], validate=False) == 0, "self-test: equal matched hashes failed")

        def simulated(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job == "b2-j1":
                result["data"]["platform_name"] = "sim:belenos"

        # The checkpoint applies the readout's run integrity, so a simulator collection cannot clear it.
        (root / "matched-sim").mkdir()
        runs = synthetic_runs(root / "matched-sim", manifests, response(), simulated)
        try:
            run_matched_check(runs[1], runs[2], validate=False)
        except ValueError:
            pass
        else:
            raise ValueError("self-test: the matched check admitted a b2-j1 served by sim:belenos")

        def undrawn(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job == "b2-j2":
                for setting, iteration in zip(manifest["settings"], result["iterations"], strict=True):
                    setting["compilation_seed"] = iteration["iteration"]["compilation_seed"] = 7

        def served(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            result["data"]["platform_name"] = "sim:belenos"

        def early(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job.startswith("b2"):
                result["data"]["start_time"] = result["data"]["start_time"].replace("T02", "T00")

        def window(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            span = {"start_time": "2026-01-01T01:00:00Z", "end_time": "2026-01-01T01:30:00Z"}
            submission["platform_at_plan"]["maintenance"] = span

        def uncollected(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job == "b1-j2":
                result["collected_utc"] = "2026-01-01T03:00:00+00:00"

        def straddle(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            span = {"start_time": "2025-12-31T23:00:00Z", "end_time": "2026-01-01T00:30:00Z"}
            submission["platform_at_plan"]["maintenance"] = span

        def reversed_block(
            job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]
        ) -> None:
            moved = {"b1-j1": "T00:06:40", "b1-j2": "T00:00:00"}
            if job in moved:
                result["data"]["start_time"] = f"2026-01-01{moved[job]}+00:00"

        def substituted(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
            if job == "b1-j1":
                first = manifest["settings"][0]
                other = next(x for x in manifest["settings"] if x["circuit_params"] != first["circuit_params"])
                first["circuit_params"] = dict(other["circuit_params"])
                result["iterations"][0]["iteration"]["circuit_params"] = first["circuit_params"]

        for name, edit in (
            ("an undrawn seed", undrawn),
            ("a simulator run", served),
            ("a short block gap", early),
            ("a maintenance window between blocks", window),
            ("a maintenance window open when block 1 started", straddle),
            ("job 2 of block 1 before its job 1", reversed_block),
            ("block 1 collected after block 2 started", uncollected),
            ("a manifest whose setting carries another state's parameters", substituted),
        ):
            (root / name).mkdir()
            runs = synthetic_runs(root / name, manifests, response(), edit)
            try:
                readout(runs, validate=False)
            except ValueError:
                continue
            raise ValueError(f"self-test: {name} was admitted")
    print(
        f"bdsc diagnostic self-test: {len(cases) + 3} synthetic run sets read their branches, the matched check "
        "failed on a mismatch and passed on equal hashes; 8 malformed sets refused"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--readout", type=Path, nargs="+")
    group.add_argument("--matched-check", type=Path, nargs=2, metavar=("B1J2_RUN", "B2J1_RUN"))
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--draw", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.draw)
    elif args.check:
        check(args.draw)
    elif args.readout:
        print(json.dumps(readout(args.readout), indent=1))
    elif args.matched_check:
        return run_matched_check(*args.matched_check)
    else:
        return self_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
