"""Forensic reconstruction of the retained qpu:belenos qualification runs and the next case's planning bound.

Every retained run of results/quandela/runs/*-qpu_belenos-bdsc_qualification-*
contributes one row per iteration: logical state, template, policy, epoch,
requested and echoed compilation seed and parameters, the sent body's
mitigation request, run timestamps, the source figures at plan and the noise
model returned at execution, every one-click output count with the zero- and
multi-click categories, and the identity of the returned compiled circuit.
The rows feed four derived tables:

- cells: per pair, template, policy and epoch, the even components
  m_Z, m_X, m_Y, the odd components d_X, d_Y and the two sum-rule residuals;
- repeats: each setting acquired in two epochs, classified on the five repeat
  levels (logical target, submitted parameters, seed, returned transformation,
  processing request), with its selected-fraction shift;
- models: the ideal column (A), the plan receipt's t_out terminal weights (B),
  a fixed linear effect and the filtered ratio Tr(G rho)/Tr(D rho) with
  0 <= G <= D (C) fitted on the two-dimensional span of f and g, shared and
  per template, with held-out prediction across templates and epochs;
- planning: the simultaneous Hoeffding radius of the qualification contrasts
  and the campaign-power lower bound it implies at candidate trial counts.

Probabilities are one-click conditioned fractions of returned counts. Every
standard error, deviance and planning bound here assumes independent
Bernoulli trials per returned sample, an observation law the provider
contract (docs/evidence/bdsc/provider_contract.json) has not established, so
each is a reference-model calculation. A returned compiled circuit is the
provider's declared matrix; its physical realization is the unresolved
returned_circuit_semantics capability.

Usage:
  "$PYTHON" scripts/bdsc_forensics.py --write
  "$PYTHON" scripts/bdsc_forensics.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_cases  # noqa: E402
import bdsc_certificate as cert  # noqa: E402
import qd_platform  # noqa: E402

import parallel  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
RUN_GLOB = "*-qpu_belenos-bdsc_qualification-*"
SIM_GLOB = "*-sim_belenos-bdsc_qualification-*"
OUT = ROOT / "docs/evidence/bdsc/forensics/forensics.json"
SCHEMA = "bdsc-forensics-v1"
LABELS = ("f", "g", "+", "-", "+i", "-i")
# Output amplitudes below this are outside a column's intended support.
SUPPORT_FLOOR = 1e-12
# Derived floats are rounded so that a rebuild on another BLAS reproduces the record.
DIGITS = 10
FIT_DIGITS = 6
FIT_STARTS = 24
FIT_SEED = 20261022
# Planning premises of the next confirmatory case (docs/design/bdsc-qualification.md).
PLAN_ALPHA = 0.01
PLAN_MARGIN = 0.02
PLAN_RESIDUAL = 0.005
PLAN_POWER = 0.95
PLAN_TRIALS = (300000, 331672, 350000, 400000)
# check compares regenerated floats with this relative and absolute tolerance; a multi-start fit may settle a little
# differently on another BLAS, so fitted fields get FIT_TOL.
CHECK_TOL = 1e-5
FIT_TOL = 1e-3


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def rounded(value: float, digits: int = DIGITS) -> float:
    return float(round(float(value), digits))


def column(setting: dict[str, Any]) -> np.ndarray:
    return np.array([complex(re, im) for re, im in setting["column"]])


def _circuit(serialized: str) -> dict[str, Any]:
    """Unitary, fixed beam-splitter angles and phase-shifter values of one returned compiled circuit."""
    from perceval.serialization import deserialize

    circuit = deserialize(serialized)
    thetas: list[float] = []
    phases: list[float] = []
    kinds: list[str] = []
    for modes, component in circuit:
        name = type(component).__name__
        kinds.append(f"{name}{tuple(modes)}")
        values = {p.name: float(p) for p in component.get_parameters(all_params=True)}
        if name == "BS":
            thetas.append(values["theta"])
        elif name == "PS":
            phases.append(values["phi"])
    return {
        "unitary": np.array(circuit.compute_unitary(), dtype=complex),
        "thetas": np.array(thetas),
        "phases": np.array(phases),
        "structure": sha256_text(";".join(kinds)),
    }


def one_click(counts: dict[str, int], modes: int) -> tuple[list[int], int, int]:
    """Per-mode one-click counts, zero-click and multi-click totals of one iteration."""
    per_mode = [0] * modes
    zero = multi = 0
    for pattern, count in counts.items():
        clicks = [m for m, c in enumerate(pattern.split(",")) if int(c) > 0]
        require(len(pattern.split(",")) == modes, f"pattern {pattern!r} has the wrong width")
        if not clicks:
            zero += count
        elif len(clicks) > 1:
            multi += count
        else:
            per_mode[clicks[0]] += count
    return per_mode, zero, multi


def load_runs() -> list[dict[str, Any]]:
    """Every retained qualification run on qpu:belenos with its manifest, result, submission and sent body."""
    contract = json.loads(bdsc_cases.CONTRACT.read_text(encoding="utf-8"))
    status = {c["capability"]: c["status"] for c in contract["capabilities"]}
    # A returned iteration names no applied mitigation; the contract capability carries what is known of it.
    capability = {None: "processor_record_completeness", (): "uncorrected_observations"}
    runs = []
    for path in sorted(RUNS.glob(RUN_GLOB)):
        manifest = json.loads((path / "cases.json").read_text(encoding="utf-8"))
        result = json.loads((path / "results.json").read_text(encoding="utf-8"))
        submission = json.loads((path / "submission.json").read_text(encoding="utf-8"))
        body = json.loads((path / "job-body.json").read_text(encoding="utf-8"))
        circuit = json.loads((path / "circuit.json").read_text(encoding="utf-8"))
        require(submission["platform"] == bdsc_cases.QUALIFYING_PLATFORM, f"{path.name}: platform")
        require(result["job_id"] == submission["job_id"], f"{path.name}: the result answers another job")
        require(result["status"]["status"] == "completed" and result["partial"] is False, f"{path.name}: incomplete")
        runs.append(
            {
                "path": path,
                "manifest": manifest,
                "source": circuit["input_state"].index(1),
                "result": result,
                "submission": submission,
                "requested_mitigations": qd_platform.body_mitigations(body),
                "effective_processing": {
                    "applied": "unknown",
                    "capability": capability[
                        None if manifest["mitigations"] is None else tuple(manifest["mitigations"])
                    ],
                    "status": status[
                        capability[None if manifest["mitigations"] is None else tuple(manifest["mitigations"])]
                    ],
                },
            }
        )
    require(bool(runs), f"no run matches {RUN_GLOB}")
    return runs


def setting_rows(runs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Per-iteration forensic rows and per-run records; the compiled circuits deserialize in the process pool."""
    pending = []
    for run in runs:
        iterations = zip(run["manifest"]["settings"], run["result"]["iterations"], strict=True)
        for position, (setting, iteration) in enumerate(iterations):
            pending.append((run, position, setting, iteration))
    circuits = parallel.ordered_map(_circuit, [it["result_fields"]["computed_circuit"] for *_, it in pending], 1)
    selected = set(runs[0]["manifest"]["selected_modes"])
    modes = cert.MODES
    rows = []
    run_records: dict[str, dict[str, Any]] = {}
    for (run, position, setting, iteration), circuit in zip(pending, circuits, strict=True):
        manifest = run["manifest"]
        spec = manifest["job_spec"]
        source = run["source"]
        require(manifest["selected_modes"] == runs[0]["manifest"]["selected_modes"], "selected modes differ by run")
        ran = iteration["iteration"]
        fields = iteration["result_fields"]
        per_mode, zero, multi = one_click(iteration["counts"], modes)
        eligible = sum(per_mode)
        v = column(setting)
        weight = np.abs(v) ** 2
        support = [m for m in range(modes) if weight[m] > SUPPORT_FLOOR]
        on_support = sum(per_mode[m] for m in support)
        sel = sum(per_mode[m] for m in selected)
        t_out = np.array(run["submission"]["perfs_at_plan"]["Transmission per mode (%)"]["t_out"], dtype=float)
        u = circuit["unitary"]
        realized = u[:, source]
        echo = ran["circuit_params"]
        name = run["path"].name
        job = manifest["job"]
        if name not in run_records:
            perfs = run["submission"]["perfs_at_plan"]
            run_records[name] = {
                "run": f"results/quandela/runs/{name}",
                "job": job,
                "job_id": run["result"]["job_id"],
                "pair": spec["pair"],
                "processing": spec["processing"],
                "epoch": spec["epoch"],
                "requested_mitigations": run["requested_mitigations"],
                "effective_processing": run["effective_processing"],
                "submitted_utc": run["submission"]["submitted_utc"],
                "created_utc": run["result"]["data"]["created_date"],
                "start_utc": run["result"]["data"]["start_time"],
                "duration_s": run["result"]["data"]["duration"],
                "collected_utc": run["result"]["collected_utc"],
                "plan_source_figures": {
                    "HOM_percent": perfs["HOM (%)"],
                    "transmittance_percent": perfs["Transmittance (%)"],
                    "g2_percent": perfs["g2 (%)"],
                },
                "execution_noise_models": sorted({it["result_fields"]["noise"] for it in run["result"]["iterations"]}),
                "server_versions": {"pcvl_version": run["result"]["data"]["pcvl_version"]},
                "client_versions": run["submission"]["versions"],
            }
        rows.append(
            {
                "job": job,
                "setting": setting["name"],
                "pair": spec["pair"],
                "processing": spec["processing"],
                "epoch": spec["epoch"],
                "template": setting["preparation"],
                "label": next(label for label, tag in bdsc_cases.LABEL_TAGS.items() if setting["name"].endswith(tag)),
                "observation_index": setting["observation_index"],
                "position_in_job": position,
                "intended_support": support,
                "ideal_selected": rounded(sum(weight[m] for m in selected)),
                "seed_requested": setting["compilation_seed"],
                "seed_echoed": ran["compilation_seed"],
                "params_digest": sha256_text(json.dumps(setting["circuit_params"], sort_keys=True)),
                "params_echo_max_deviation": max(abs(echo[x] - y) for x, y in setting["circuit_params"].items()),
                "requested_mitigations": run["requested_mitigations"],
                "transformation": {
                    "computed_circuit_sha256": sha256_text(fields["computed_circuit"]),
                    "computed_experiment_sha256": sha256_text(fields["computed_experiment"]),
                    "structure_sha256": circuit["structure"],
                    "beam_splitter_model_sha256": hashlib.sha256(circuit["thetas"].tobytes()).hexdigest(),
                    "source_column_fidelity": rounded(abs(np.vdot(v, realized)) ** 2),
                    "source_intensity_distance": rounded(0.5 * float(np.sum(np.abs(np.abs(realized) ** 2 - weight)))),
                },
                "execution_noise_model": fields["noise"],
                "provider_perf": {"physical_perf": fields["physical_perf"], "global_perf": fields["global_perf"]},
                "samples": iteration["samples"],
                "one_click_counts": per_mode,
                "zero_click": zero,
                "multi_click": multi,
                "eligible": eligible,
                "selected": sel,
                "complementary": eligible - sel,
                "selected_fraction": rounded(sel / eligible),
                "outside_support_share": rounded(1 - on_support / eligible),
                "receipt_selected": rounded(
                    sum(t_out[m] * weight[m] for m in selected) / float(np.sum(t_out * weight))
                ),
                "_column": v,
                "_unitary": u,
                "_phases": circuit["phases"],
            }
        )
    for row in rows:
        require(row["samples"] == row["eligible"] + row["zero_click"] + row["multi_click"], f"{row['job']}: tally")
    return rows, list(run_records.values())


def reference_se(p: float, n: int) -> float:
    return math.sqrt(p * (1 - p) / n)


def half(p: dict[str, float], n: dict[str, int], a: str, b: str, sign: float) -> tuple[float, float]:
    """(p_a + sign p_b) / 2 and its reference standard error."""
    se = math.sqrt(reference_se(p[a], n[a]) ** 2 + reference_se(p[b], n[b]) ** 2) / 2
    return (p[a] + sign * p[b]) / 2, se


def cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Even and odd components and sum-rule residuals of every six-state cell, with reference standard errors."""
    groups: dict[tuple[str, str, int], dict[str, dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row["job"], row["template"], row["epoch"]), {})[row["label"]] = row
    out = []
    for (job, template, epoch), by_label in sorted(groups.items()):
        require(set(by_label) == set(LABELS), f"{job} {template}: incomplete cell")
        p = {label: by_label[label]["selected"] / by_label[label]["eligible"] for label in LABELS}
        n = {label: by_label[label]["eligible"] for label in LABELS}

        components = {
            "m_Z": half(p, n, "f", "g", 1),
            "m_X": half(p, n, "+", "-", 1),
            "m_Y": half(p, n, "+i", "-i", 1),
            "d_X": half(p, n, "+", "-", -1),
            "d_Y": half(p, n, "+i", "-i", -1),
        }
        residual = {}
        for key, (a, b) in (("delta_R", ("+", "-")), ("delta_I", ("+i", "-i"))):
            value = p[a] + p[b] - p["f"] - p["g"]
            se = math.sqrt(sum(reference_se(p[x], n[x]) ** 2 for x in (a, b, "f", "g")))
            residual[key] = {"value": rounded(value), "reference_se": rounded(se)}
        out.append(
            {
                "job": job,
                "template": template,
                "epoch": epoch,
                "components": {
                    k: {"value": rounded(v), "reference_se": rounded(s)} for k, (v, s) in components.items()
                },
                "sum_rules": residual,
                "outside_support_share": {label: by_label[label]["outside_support_share"] for label in LABELS},
            }
        )
    return out


def phase_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(np.angle(np.exp(1j * (a - b))))


def unitary_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Operator-norm distance after the global phase that best aligns b with a."""
    overlap = np.trace(b.conj().T @ a)
    phase = overlap / abs(overlap) if abs(overlap) > 0 else 1.0
    return float(np.linalg.norm(a - phase * b, 2))


def repeats(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every setting acquired in more than one epoch at one pair and policy, on the five repeat levels."""
    keyed: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        keyed.setdefault((row["pair"], row["processing"], row["setting"]), []).append(row)
    out = []
    for (pair, processing, setting), group in sorted(keyed.items()):
        if len(group) < 2:
            continue
        early, late = sorted(group, key=lambda r: r["epoch"])[:2]
        pe, pl = early["selected"] / early["eligible"], late["selected"] / late["eligible"]
        se = math.sqrt(reference_se(pe, early["eligible"]) ** 2 + reference_se(pl, late["eligible"]) ** 2)
        te, tl = early["transformation"], late["transformation"]
        shift = phase_difference(early["_phases"], late["_phases"])
        out.append(
            {
                "pair": pair,
                "processing": processing,
                "setting": setting,
                "epochs": [early["epoch"], late["epoch"]],
                "levels": {
                    "same_logical_target": early["intended_support"] == late["intended_support"],
                    "same_submitted_parameters": early["params_digest"] == late["params_digest"],
                    "same_seed": early["seed_echoed"] == late["seed_echoed"],
                    "same_returned_transformation": te["computed_circuit_sha256"] == tl["computed_circuit_sha256"],
                    "same_processing_request": early["requested_mitigations"] == late["requested_mitigations"],
                },
                "seeds": [early["seed_echoed"], late["seed_echoed"]],
                "same_beam_splitter_model": te["beam_splitter_model_sha256"] == tl["beam_splitter_model_sha256"],
                "phase_shifters_changed": int(np.sum(shift > 1e-9)),
                "phase_shift_median_rad": rounded(float(np.median(shift))),
                "unitary_distance_op": rounded(unitary_distance(early["_unitary"], late["_unitary"])),
                "source_column_fidelity": [te["source_column_fidelity"], tl["source_column_fidelity"]],
                "source_intensity_distance": [te["source_intensity_distance"], tl["source_intensity_distance"]],
                "noise_models": [early["execution_noise_model"], late["execution_noise_model"]],
                "selected_fraction": [rounded(pe), rounded(pl)],
                "shift": rounded(pl - pe),
                "reference_se": rounded(se),
                "outside_support_share": [early["outside_support_share"], late["outside_support_share"]],
            }
        )
    return out


def bloch(v: np.ndarray, f: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Bloch vector of v on the span of the orthonormal columns f and g."""
    a, b = np.vdot(f, v), np.vdot(g, v)
    require(abs(abs(a) ** 2 + abs(b) ** 2 - 1) < 1e-9, "a state leaves the span of f and g")
    c = np.conj(a) * b
    return np.array([2 * c.real, 2 * c.imag, abs(a) ** 2 - abs(b) ** 2])


def _unit(theta: float, phi: float) -> np.ndarray:
    return np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])


def _sigmoid(x: float) -> float:
    return 0.5 * (1 + math.tanh(x / 2))


def filtered(params: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Tr(G rho)/Tr(D rho) for G = g0 I + g.sigma, D = G + H, both PSD, trace of D fixed at 2."""
    g0 = _sigmoid(params[0])
    g = g0 * _sigmoid(params[1]) * _unit(params[2], params[3])
    h0 = 1 - g0
    h = h0 * _sigmoid(params[4]) * _unit(params[5], params[6])
    return (g0 + vectors @ g) / (1 + vectors @ (g + h))


def linear(params: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Tr(G rho) for 0 <= G <= I: a fixed linear effect with scalar acceptance."""
    g0 = _sigmoid(params[0])
    g = min(g0, 1 - g0) * _sigmoid(params[1]) * _unit(params[2], params[3])
    return g0 + vectors @ g


def intensity(params: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """The filtered ratio with G and D diagonal in the f, g basis: it reads only the output intensities |a|^2, |b|^2."""
    g0 = _sigmoid(params[0])
    gz = g0 * math.tanh(params[1])
    h0 = 1 - g0
    hz = h0 * math.tanh(params[2])
    return (g0 + vectors[:, 2] * gz) / (1 + vectors[:, 2] * (gz + hz))


MODELS = {"linear": (linear, 4), "intensity": (intensity, 3), "filtered": (filtered, 7)}


def deviance(p: np.ndarray, k: np.ndarray, n: np.ndarray) -> float:
    """Binomial deviance of predicted probabilities against selected and eligible counts."""
    p = np.clip(p, 1e-15, 1 - 1e-15)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(k > 0, k * np.log(k / (n * p)), 0.0)
        b = np.where(n - k > 0, (n - k) * np.log((n - k) / (n * (1 - p))), 0.0)
    return float(2 * np.sum(a + b))


def _fit(item: tuple[str, np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    """Best-deviance parameters of one model over deterministic multi-start L-BFGS-B."""
    model, vectors, k, n = item
    function, size = MODELS[model]
    rng = np.random.default_rng(FIT_SEED)
    best: tuple[float, np.ndarray] | None = None
    for _ in range(FIT_STARTS):
        start = rng.normal(0, 1.5, size)
        found = minimize(lambda x: deviance(function(x, vectors), k, n), start, method="L-BFGS-B")
        if best is None or found.fun < best[0]:
            best = (float(found.fun), found.x)
    require(best is not None, "no fit start")
    return best[1]  # type: ignore[index]


def models(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scenario and fitted models per job: shared and per-template fits, held-out template and epoch prediction."""
    by_job: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_job.setdefault(row["job"], []).append(row)
    designs = []
    for job, group in sorted(by_job.items()):
        f = next(r["_column"] for r in group if r["label"] == "f")
        g = next(r["_column"] for r in group if r["label"] == "g")
        for train, test in (
            ("both", "both"),
            ("outward-ladder", "reverse-ladder"),
            ("reverse-ladder", "outward-ladder"),
        ):
            designs.append((job, job, train, test, f, g))
    for job in by_job:
        early = job[:-1] + "1"
        if job.endswith("e2") and early in by_job:
            f = next(r["_column"] for r in by_job[early] if r["label"] == "f")
            g = next(r["_column"] for r in by_job[early] if r["label"] == "g")
            designs.append((early, job, "both", "both", f, g))

    def data(job: str, template: str, f: np.ndarray, g: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        chosen = [r for r in by_job[job] if template in ("both", r["template"])]
        chosen.sort(key=lambda r: (r["template"], LABELS.index(r["label"])))
        vectors = np.array([bloch(r["_column"], f, g) for r in chosen])
        k = np.array([r["selected"] for r in chosen], dtype=float)
        n = np.array([r["eligible"] for r in chosen], dtype=float)
        return vectors, k, n

    items = []
    for train_job, _, train, _, f, g in designs:
        vectors, k, n = data(train_job, train, f, g)
        for model in MODELS:
            items.append((model, vectors, k, n))
    fitted = parallel.ordered_map(_fit, items, 1)
    out = []
    for index, (train_job, test_job, train, test, f, g) in enumerate(designs):
        tv, tk, tn = data(test_job, test, f, g)
        observed = tk / tn
        entry: dict[str, Any] = {"train": [train_job, train], "test": [test_job, test], "fits": {}}
        for offset, model in enumerate(MODELS):
            function, size = MODELS[model]
            params = fitted[index * len(MODELS) + offset]
            predicted = function(params, tv)
            entry["fits"][model] = {
                "parameters": size,
                "reference_deviance": rounded(deviance(predicted, tk, tn), FIT_DIGITS - 3),
                "max_abs_residual": rounded(float(np.max(np.abs(observed - predicted))), FIT_DIGITS),
            }
        out.append(entry)
    return out


def scatter(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per job, the spread of the superposition settings within each template and the split between templates.

    The four superpositions of one template request one output intensity, so their spread within a template is the
    per-setting compilation response (seed and parameters together) plus sampling noise.
    """
    out = []
    for job in sorted({r["job"] for r in rows}):
        by_template: dict[str, dict[str, Any]] = {}
        for template in cert.PREPARATION_DESCRIPTIONS:
            chosen = [r for r in rows if r["job"] == job and r["template"] == template and r["label"] in LABELS[2:]]
            p = np.array([r["selected"] / r["eligible"] for r in chosen])
            se = [reference_se(float(x), r["eligible"]) for x, r in zip(p, chosen, strict=True)]
            by_template[template] = {
                "settings": len(chosen),
                "mean": rounded(float(np.mean(p))),
                "sd": rounded(float(np.std(p, ddof=1))),
                "range": [rounded(float(p.min())), rounded(float(p.max()))],
                "mean_reference_se": rounded(float(np.mean(se))),
            }
        means = [by_template[t]["mean"] for t in cert.PREPARATION_DESCRIPTIONS]
        out.append({"job": job, "templates": by_template, "template_split": rounded(means[0] - means[1])})
    return out


def determinism(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retained sim:belenos runs of a qualification job against the qpu:belenos run of the same job, per setting.

    Equal seed and parameters with an equal returned circuit across platforms and hours shows that compilation is a
    function of the request and the compiler's component model, which a matched-seed repeat then reproduces.
    """
    qpu = {(r["job"], r["setting"]): r for r in rows}
    out = []
    for path in sorted(RUNS.glob(SIM_GLOB)):
        result = json.loads((path / "results.json").read_text(encoding="utf-8"))
        if result.get("status", {}).get("status") != "completed" or "iterations" not in result:
            continue
        manifest = json.loads((path / "cases.json").read_text(encoding="utf-8"))
        for setting, iteration in zip(manifest["settings"], result["iterations"], strict=True):
            match = qpu.get((manifest["job"], setting["name"]))
            if match is None:
                continue
            ran = iteration["iteration"]
            out.append(
                {
                    "sim_run": f"results/quandela/runs/{path.name}",
                    "job": manifest["job"],
                    "setting": setting["name"],
                    "same_seed": ran["compilation_seed"] == match["seed_echoed"],
                    "same_parameters": sha256_text(json.dumps(setting["circuit_params"], sort_keys=True))
                    == match["params_digest"],
                    "same_returned_circuit": sha256_text(iteration["result_fields"]["computed_circuit"])
                    == match["transformation"]["computed_circuit_sha256"],
                    "noise_models": [iteration["result_fields"]["noise"], match["execution_noise_model"]],
                }
            )
    return out


def scenarios(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Model A (ideal column) and model B (plan-receipt t_out weights) against each observed selected fraction."""
    return [
        {
            "job": r["job"],
            "setting": r["setting"],
            "observed": r["selected_fraction"],
            "ideal": r["ideal_selected"],
            "receipt_weights": r["receipt_selected"],
            "processed": r["processing"] == "provider-defaults",
        }
        for r in rows
    ]


def planning(case: dict[str, Any]) -> dict[str, Any]:
    """Simultaneous Hoeffding radii of the qualification contrasts and the campaign-power lower bound they imply."""
    contrasts = cert.case_contrasts(case["observations"])
    families: dict[str, int] = {}
    for family, _, _ in contrasts:
        families[family] = families.get(family, 0) + 1
    count = len(contrasts)
    worst = max(sum(w * w for _, w in terms) for _, _, terms in contrasts)
    log_term = math.log(2 * count / PLAN_ALPHA)

    def radius(n: int) -> float:
        return math.sqrt(0.5 * worst / n * log_term)

    def power(n: int) -> float:
        gap = PLAN_MARGIN - PLAN_RESIDUAL - radius(n)
        if gap <= 0:
            return 0.0
        return max(0.0, 1 - 2 * count * math.exp(-2 * n * gap * gap / worst))

    low, high = 1, 10**8
    while low < high:
        mid = (low + high) // 2
        low, high = (low, mid) if power(mid) >= PLAN_POWER else (mid + 1, high)
    return {
        "contrasts": families,
        "count": count,
        "worst_coefficient_square_sum": worst,
        "alpha": PLAN_ALPHA,
        "margin": PLAN_MARGIN,
        "design_residual": PLAN_RESIDUAL,
        "rows": [
            {"trials": n, "radius": rounded(radius(n)), "power_lower_bound": rounded(power(n), 4)} for n in PLAN_TRIALS
        ],
        "minimum_trials_for_power": {"power": PLAN_POWER, "trials": low},
        "reference_se_half": {
            "one_fraction": rounded(reference_se(0.5, 300000), 6),
            "difference": rounded(math.sqrt(2) * reference_se(0.5, 300000), 6),
        },
        "premises": "independent bounded trials per returned sample; conditional on the declared observation law, "
        "nuisance model and dependence assumptions, not a universal bound on hardware power",
    }


def build() -> dict[str, Any]:
    runs = load_runs()
    rows, run_records = setting_rows(runs)
    case_path = bdsc_cases.CASE
    case = json.loads(case_path.read_text(encoding="utf-8"))
    record = {
        "schema": SCHEMA,
        "qualification_case_sha256": hashlib.sha256(case_path.read_bytes()).hexdigest(),
        "observation_law": "reference: independent Bernoulli trials per returned one-click sample, unestablished",
        "runs": run_records,
        "settings": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
        "cells": cells(rows),
        "repeats": repeats(rows),
        "scenarios": scenarios(rows),
        "superposition_scatter": scatter(rows),
        "compilation_determinism": determinism(rows),
        "models": models(rows),
        "planning": planning(case),
    }
    return record


def close(a: Any, b: Any, path: str = "") -> list[str]:
    """Paths at which two records differ beyond CHECK_TOL for floats, exactly otherwise."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return [f"{path}: keys {sorted(set(a) ^ set(b))}"]
        return [d for key in a for d in close(a[key], b[key], f"{path}/{key}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b, strict=True)) for d in close(x, y, f"{path}/{i}")]
    if isinstance(a, float) or isinstance(b, float):
        tol = FIT_TOL if path.startswith("/models/") else CHECK_TOL
        ok = isinstance(a, int | float) and isinstance(b, int | float) and math.isclose(a, b, rel_tol=tol, abs_tol=tol)
        return [] if ok else [f"{path}: {a} != {b}"]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(f"bdsc forensics: wrote {OUT.relative_to(ROOT)} from {len(record['runs'])} runs")
        return 0
    retained = json.loads(OUT.read_text(encoding="utf-8"))
    differences = close(record, retained)
    require(not differences, "bdsc forensics differ from the rebuild: " + "; ".join(differences[:8]))
    print(f"bdsc forensics: {len(record['settings'])} settings and {len(record['models'])} model designs rebuild")
    return 0


if __name__ == "__main__":
    sys.exit(main())
