"""Belenos in-situ two-photon visibility: the Ascella associator closure design on two source pairs of qpu:belenos.

docs/design/belenos-associator-visibility-case.md fixes the request. Each job runs the eight template iterations of
scripts/ascella_associator_case.py (the octonion associator block and its quaternion control, each route in the order
LaLb, Lab, Lab, LaLb) on one four-mode window of the 24-mode chip, the two photons on the window's logical modes 0
and 2. Both control routes read D = -f(V), f(V) = V / (V + 1.5 (1 - V)), so the control block measures the photon
overlap V of that source pair in the compiled circuit, and the closure Delta + 2 mean D_control = 0 holds at every V
and tests route- or mesh-dependent error. WINDOWS places job-00 on chip modes 18 to 21 (sources 18 and 20, the input
and Bell photons the teleportation analyzer of qd_teleportation_rehearsal job-02 interferes) and job-01 on 20 to 23
(sources 20 and 22, its CNOT pair).

Each iteration carries its own compilation_seed: job-00 takes indices 0 to 7 and job-01 indices 8 to 15 of the ANU
QRNG draw docs/evidence/anu_qrng/draw-2026-10-31T040009Z.json, each in index order, registered in
docs/evidence/qrng_seeds/allocations.json.

--check rebuilds both cases and compares them with the retained bytes, binds every iteration through
qd_platform.template_experiment, recomputes each iteration's two-click law on the window from Perceval's unitary,
compares one iteration with Perceval's SLOS backend on all 24 modes, requires the ideal endpoints, and requires the
retained platform read to connect both photon modes and to keep every window mode at or below the dark-rate limit of
qd_teleportation_rehearsal; --check-live JOB repeats that read check on the live platform record between plan and
submit. --build JOB writes a case; retained bytes are never rewritten. --analyze RUN writes the
preregistered endpoints of a collected run. Submission uses scripts/qd_platform.py plan/submit/collect with the
written case's arguments.

Usage:
  "$PYTHON" scripts/belenos_associator_visibility.py [--check | --check-live JOB | --build JOB | --analyze RUN]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_associator_case as base  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402
from qd_teleportation_rehearsal import CONNECTED, DARK_LIMIT, read_perfs  # noqa: E402

from parallel import ordered_map  # noqa: E402

MODES = 24
LOGICAL = base.LOGICAL
FAMILY = "belenos_associator_visibility"
CASES = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/belenos-associator-visibility-case.md"
PLATFORM = "qpu:belenos"
# The first chip mode of each job's four-mode window.
WINDOWS = {"job-00": 18, "job-01": 20}
# The platform read the windows were chosen from: the teleportation job-02 read of 2026-10-31 03:39:51 UTC.
READ = ROOT / "results/quandela/cases/teleportation_rehearsal/job-02/platform-read/catalogue.json"
SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T040009Z.json"
JOB_00_COMPILATION_SEEDS = (21992, 60642, 22447, 48697, 62981, 32522, 49525, 33203)
JOB_01_COMPILATION_SEEDS = (65231, 43547, 10004, 41732, 19358, 21749, 33051, 43264)
CASE_SEEDS = {"job-00": JOB_00_COMPILATION_SEEDS, "job-01": JOB_01_COMPILATION_SEEDS}
SAMPLES_PER_ITERATION = base.SAMPLES_PER_ITERATION
SHOTS_PER_ITERATION = base.SHOTS_PER_ITERATION
MAX_DURATION = base.MAX_DURATION
TOLERANCE = base.TOLERANCE
BODY_TOLERANCE = base.BODY_TOLERANCE
OVERLAP_SIGMAS = 3
# V_eff that the Perceval NoiseModel (g2 0.014, per-mode transmission of READ) forecasts for each window at the source
# indistinguishability 0.846, which reproduces the pooled teleportation correctness on the job-02 layout.
TELEPORTATION_FIT_V_EFF = {"job-00": 0.824, "job-01": 0.8265}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def embed(matrix: np.ndarray, window: int) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    full[window : window + LOGICAL, window : window + LOGICAL] = matrix
    return full


def photon_modes(window: int) -> tuple[int, int]:
    first, second = base.input_modes()
    return window + first, window + second


def build_setting(item: tuple[int, dict[str, Any], str]) -> tuple[dict[str, Any], dict[str, Any]]:
    index, row, job = item
    window = WINDOWS[job]
    logical = base.route_operator(row["block"], row["route"]).astype(complex)
    mesh, parameters = photonic_template(logical)
    full = embed(logical, window)
    ideal = base.two_click_law(logical.real, 1.0)
    setting = {
        "name": f"{row['block']}-{row['route']}-arm{row['arm']}",
        "observation_index": index,
        **row,
        "ideal": {
            "two_click_law_indistinguishable": {k: round(v, 12) for k, v in ideal.items() if v > TOLERANCE},
            "D_indistinguishable": round(base.endpoint(ideal), 12),
            "D_distinguishable": round(base.endpoint(base.two_click_law(logical.real, 0.0)), 12),
        },
        "circuit_params": parameters,
        "compilation_seed": CASE_SEEDS[job][index],
        "column": [[float(value.real), float(value.imag)] for value in full[:, photon_modes(window)[0]]],
        "operator": encoded(full),
    }
    return mesh, setting


def documents(job: str) -> dict[str, bytes]:
    window = WINDOWS[job]
    rows = base.iteration_rows()
    require(len(CASE_SEEDS[job]) == len(rows), f"{job}: {len(CASE_SEEDS[job])} seeds for {len(rows)} iterations")
    built = ordered_map(build_setting, [(index, row, job) for index, row in enumerate(rows)], min_items=1)
    template = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == template, f"iteration {index} needs another mesh than iteration 0")
    settings = [setting for _, setting in built]
    input_state = [0] * MODES
    for mode in photon_modes(window):
        input_state[mode] = 1
    ops = [[kind, mode + window, index] for kind, mode, index in template["ops"]]
    circuit = {**template, "ops": ops, "modes": MODES, "input_state": input_state}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM, "sim:belenos"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 2,
        "max_samples": SAMPLES_PER_ITERATION * len(settings),
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "window": window,
        "logical_modes": list(range(window, window + LOGICAL)),
        "algebra_to_logical": {str(k): v for k, v in sorted(base.ALGEBRA_TO_LOGICAL.items())},
        "eligibility": f"exactly two occupied modes, both among chip modes {window}..{window + LOGICAL - 1}",
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "plus_pairs": list(base.PLUS_PAIRS),
            "minus_pairs": list(base.MINUS_PAIRS),
            "pair_labels": "logical modes, chip mode minus window",
            "primary_endpoint": "V_eff = 1.5 f / (1 + 0.5 f), f = -mean D_control over the two control routes",
            "associator_endpoint": "Delta = D(LaLb) - D(Lab) on the associator block",
            "mutation_endpoint": "Delta_control = D(LaLb) - D(Lab) on the control block",
            "detection_sigmas": base.DETECTION_SIGMAS,
            "mutation_tolerance": base.MUTATION_TOLERANCE,
            "closure_endpoint": "C = Delta + 2 mean(D_control), 0 at every visibility",
            "closure_tolerance": base.CLOSURE_TOLERANCE,
            "calibration_tolerance": base.CALIBRATION_TOLERANCE,
            "hom_comparison": "descriptive: |Delta - Delta_pred(V_HOM)|, V_HOM the HOM fraction read at submission",
            "hom_comparison_note": "Delta_pred(V_HOM) omits g2, so a source exactly at the read departs from it by "
            "about 0.06 under the Perceval noise model; the comparison carries no decision",
            "overlap_rule": {
                "statement": f"V_eff - {OVERLAP_SIGMAS} se_with_mesh_spread above the teleportation-fit V_eff reads "
                "overlap high; otherwise unresolved. Compiled-mesh error only lowers V_eff and the closure does not "
                "see error common to every route, so the rule is one-sided",
                "teleportation_fit_V_eff": TELEPORTATION_FIT_V_EFF,
                "teleportation_fit": "source indistinguishability 0.846 reproduces the pooled correctness 0.823 "
                "(1495 of 1816 accepted events) of teleportation job-02, job-03 and the job-02 replay on this layout "
                "under the teleportation model at g2 0.014 and the anchor read's per-mode transmission; the "
                "Perceval NoiseModel forecasts V_eff at that indistinguishability",
            },
            "interpretation": "photon overlap of one source pair in the compiled circuit; error common to every "
            "route lowers it and passes the closure",
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def check_read(job: str, catalogue: dict[str, Any] | None = None) -> list[float]:
    """Require both photon modes on connected source inputs and every window mode at or below DARK_LIMIT in the
    catalogue (the retained READ by default); return the window's dark rates."""
    t_out, dark, _ = read_perfs(catalogue or json.loads(READ.read_text(encoding="utf-8")))
    window = WINDOWS[job]
    for mode in photon_modes(window):
        require(mode in CONNECTED, f"{job}: photon mode {mode} is not a connected source input")
    hot = [mode for mode in range(window, window + LOGICAL) if dark[mode] > DARK_LIMIT]
    require(not hot, f"{job}: window modes {hot} read a dark rate above {DARK_LIMIT:g} per second")
    require(len(t_out) == MODES, f"{job}: the read carries {len(t_out)} output transmissions")
    return [dark[mode] for mode in range(window, window + LOGICAL)]


def check_live(job: str) -> int:
    """check_read against the live qpu:belenos record, run between plan and submit."""
    from qd_platform import get, platform_route

    record = get(platform_route(PLATFORM))
    rates = check_read(job, {"processors": {PLATFORM: record}})
    perfs = record.get("perfs") or {}
    print(
        f"{FAMILY} {job}: live status {record.get('status')}, HOM {perfs.get('HOM (%)')} %, window dark rates {rates}"
    )
    return 0


def check_job(job: str) -> str:
    case = CASES / job
    retained = {name: (case / name).read_bytes() for name in ("cases.json", "circuit.json")}
    for name, data in documents(job).items():
        require(retained[name] == data, f"{case.relative_to(ROOT)}/{name} differs from the builder's bytes")
    check_read(job)
    manifest = json.loads(retained["cases.json"])
    circuit = json.loads(retained["circuit.json"])
    experiment, settings = template_experiment(manifest, circuit)
    require(experiment is not None and len(settings) == 8, f"{job}: the template experiment did not bind 8 settings")
    import perceval as pcvl

    window = WINDOWS[job]
    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
    deltas: dict[str, list[float]] = {"associator": [], "control": []}
    for setting in settings:
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())
        outside = unitary.copy()
        outside[window : window + LOGICAL, window : window + LOGICAL] = np.eye(LOGICAL)
        require(np.abs(outside - np.eye(MODES)).max() < BODY_TOLERANCE, f"{setting['name']}: mesh leaves the window")
        block = unitary[window : window + LOGICAL, window : window + LOGICAL]
        require(np.abs(block.imag).max() < BODY_TOLERANCE, f"{setting['name']}: compiled block is not real")
        law = base.two_click_law(block.real, 1.0)
        expected = setting["ideal"]["two_click_law_indistinguishable"]
        for pair, value in law.items():
            require(abs(value - expected.get(pair, 0.0)) < BODY_TOLERANCE, f"{setting['name']}: pair {pair}")
        sign = 1 if setting["route"] == "LaLb" else -1
        deltas[setting["block"]].append(sign * base.endpoint(law))
        if setting["observation_index"] == 0:
            observed = slos_pairs(unitary, circuit["input_state"])
            shifted = {(int(p[0]) + window, int(p[1]) + window): v for p, v in law.items() if v > TOLERANCE}
            require(set(observed) == set(shifted), f"{job}: SLOS clicks {sorted(observed)} against {sorted(shifted)}")
            for modes, value in shifted.items():
                require(abs(observed[modes] - value) < BODY_TOLERANCE, f"{job}: SLOS differs on modes {modes}")
    associator = sum(deltas["associator"]) / 2
    control = sum(deltas["control"]) / 2
    require(abs(associator - 2) < BODY_TOLERANCE, f"{job}: ideal associator Delta {associator}")
    require(abs(control) < BODY_TOLERANCE, f"{job}: ideal control Delta {control}")
    return f"{FAMILY} {job}: window {window}, 8 iterations bound; Delta {associator:.12f}, control {control:.12f}"


def slos_pairs(unitary: np.ndarray, input_state: list[int]) -> dict[tuple[int, int], float]:
    """Two-click probabilities over all 24 modes from Perceval's SLOS backend, indistinguishable photons, keyed by the
    occupied chip modes."""
    import perceval as pcvl

    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    backend.set_input_state(pcvl.BasicState(input_state))
    law: dict[tuple[int, int], float] = {}
    for state, probability in backend.prob_distribution().items():
        occupied = [mode for mode in range(len(input_state)) if state[mode] > 0]
        if len(occupied) == 2 and probability > TOLERANCE:
            law[(occupied[0], occupied[1])] = float(probability)
    return law


def check() -> int:
    for line in ordered_map(check_job, sorted(WINDOWS), min_items=1):
        print(line)
    return 0


def build(job: str) -> int:
    out = CASES / job
    out.mkdir(parents=True, exist_ok=True)
    for name, data in documents(job).items():
        path = out / name
        require(not path.exists() or path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        if not path.exists():
            path.write_bytes(data)
    print(f"{FAMILY} {job}: {out.relative_to(ROOT)} cases.json {sha256_bytes(documents(job)['cases.json'])}")
    return 0


def analyze(run: Path) -> dict[str, Any]:
    """Preregistered endpoints of a collected run on its window: per-block Delta with its standard error, the in-situ
    visibility from the control block, and the decisions of scripts/ascella_associator_case.py."""
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    window = int(manifest["window"])
    entries = results.get("iterations") or []
    tallies: dict[str, dict[str, list[int]]] = {b: {"LaLb": [0, 0, 0], "Lab": [0, 0, 0]} for b in base.PAIRS}
    excluded = {"three_or_more_clicks": 0, "two_clicks_outside_window": 0, "fewer_than_two_clicks": 0}
    accepted = 0
    counted = dict.fromkeys(base.PAIRS, 0)
    by_seed = {setting["compilation_seed"]: setting for setting in manifest["settings"]}
    bound: set[int] = set()
    per_iteration: dict[str, list[dict[str, Any]]] = {b: [] for b in base.PAIRS}
    for entry in entries:
        counts = entry.get("counts") if isinstance(entry, dict) else None
        if not counts:
            continue
        echoed = entry.get("iteration") or {}
        seed = echoed.get("compilation_seed")
        require(seed in by_seed, f"a result iteration carries compilation_seed {seed!r} outside the case")
        require(seed not in bound, f"compilation_seed {seed} binds a second result iteration")
        setting = by_seed[seed]
        require(
            echoed.get("circuit_params") == setting["circuit_params"],
            f"the result iteration of compilation_seed {seed} echoes other circuit_params than {setting['name']}",
        )
        bound.add(setting["compilation_seed"])
        counted[setting["block"]] += 1
        tally = tallies[setting["block"]][setting["route"]]
        own = [0, 0, 0]
        for state, count in counts.items():
            occupation = [int(c) for c in state.strip("|>").split(",")]
            occupied = [m for m, n in enumerate(occupation) if n > 0]
            if len(occupied) != 2 or not all(window <= m < window + LOGICAL for m in occupied):
                cause = (
                    "three_or_more_clicks"
                    if len(occupied) > 2
                    else "two_clicks_outside_window"
                    if len(occupied) == 2
                    else "fewer_than_two_clicks"
                )
                excluded[cause] += count
                continue
            accepted += count
            pair = f"{occupied[0] - window}{occupied[1] - window}"
            for target in (tally, own):
                target[0] += count if pair in base.PLUS_PAIRS else 0
                target[1] += count if pair in base.MINUS_PAIRS else 0
                target[2] += count
        if own[2]:
            sign = 1 if setting["route"] == "LaLb" or setting["block"] == "control" else -1
            d, se = binomial_endpoint(*own)
            per_iteration[setting["block"]].append(
                {"name": setting["name"], "route": setting["route"], "D": d, "se": se, "signed_D": sign * d}
            )
    out: dict[str, Any] = {
        "window": window,
        "photon_modes": list(photon_modes(window)),
        "excluded_events": sum(excluded.values()),
        "excluded_by_cause": excluded,
        "accepted_two_click_events": accepted,
        "multiphoton_estimate": base.multiphoton_estimate(
            excluded["three_or_more_clicks"], accepted, base.submission_perf(run, "Transmittance (%)")
        ),
    }
    for block, routes in tallies.items():
        out[f"{block}_counted_iterations"] = counted[block]
        estimates: dict[str, dict[str, float] | None] = {}
        for route, (plus, minus, total) in routes.items():
            if total == 0:
                estimates[route] = None
                continue
            d, se = binomial_endpoint(plus, minus, total)
            estimates[route] = {"D": d, "se": se, "events": total}
        first, second = estimates["LaLb"], estimates["Lab"]
        if first is not None and second is not None:
            out[block] = {
                "routes": estimates,
                "Delta": first["D"] - second["D"],
                "se": math.hypot(first["se"], second["se"]),
            }
        else:
            out[block] = {"routes": estimates, "Delta": None}
        out[block]["iterations"] = per_iteration[block]
        out[block]["mesh_heterogeneity"] = heterogeneity(per_iteration[block])
    out["decisions"] = base.decisions(out, base.submission_visibility(run))
    control = out["control"]
    if counted["control"] == len(base.ROUTE_ORDER) and control.get("Delta") is not None:
        routes = control["routes"]
        f = -(routes["LaLb"]["D"] + routes["Lab"]["D"]) / 2
        se_f = math.hypot(routes["LaLb"]["se"], routes["Lab"]["se"]) / 2
        slope = 1.5 / (1 + 0.5 * f) ** 2
        birge = control["mesh_heterogeneity"]["birge_ratio"]
        v_eff = base.visibility_from_contrast(f)
        se_mesh = slope * se_f * max(1.0, birge)
        out["in_situ_visibility"] = {"V_eff": v_eff, "se": slope * se_f, "se_with_mesh_spread": se_mesh, "f": f}
        out["overlap_reading"] = overlap_reading(manifest, v_eff, se_mesh)
    else:
        out["in_situ_visibility"] = None
        out["overlap_reading"] = "undecided: the control block lacks one of its four iterations"
    return out


def binomial_endpoint(plus: int, minus: int, total: int) -> tuple[float, float]:
    """D = (plus - minus) / total and its multinomial standard error over total accepted events."""
    d = (plus - minus) / total
    q = (plus + minus) / total
    return d, math.sqrt(max(q - d * d, 0.0) / total)


def heterogeneity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Chi-square of a block's sign-aligned iteration endpoints about their inverse-variance mean.

    Under the two-photon mixture model every control iteration reads -f(V) and every associator iteration reads +f(V)
    after the Lab sign flip, so the iterations of one block share one expectation and their spread beyond binomial
    error is the error of their separately compiled meshes. The Birge ratio sqrt(chi2 / dof) scales the visibility's
    standard error when it exceeds 1.
    """
    from scipy.stats import chi2

    usable = [row for row in rows if row["se"] > 0]
    if len(usable) < 2:
        return {"dof": 0, "chi2": None, "p": None, "birge_ratio": 1.0}
    weights = [1 / row["se"] ** 2 for row in usable]
    mean = sum(w * row["signed_D"] for w, row in zip(weights, usable, strict=True)) / sum(weights)
    statistic = sum(w * (row["signed_D"] - mean) ** 2 for w, row in zip(weights, usable, strict=True))
    dof = len(usable) - 1
    return {
        "dof": dof,
        "chi2": statistic,
        "p": float(chi2.sf(statistic, dof)),
        "birge_ratio": math.sqrt(statistic / dof),
    }


def overlap_reading(manifest: dict[str, Any], v_eff: float, se: float) -> str:
    """The preregistered one-sided reading: mesh error only lowers V_eff, so a V_eff above the teleportation-fit
    forecast by OVERLAP_SIGMAS standard errors rules out low photon overlap as the teleportation shortfall, while a
    lower V_eff leaves overlap and mesh error unresolved."""
    threshold = manifest["preregistered"]["overlap_rule"]["teleportation_fit_V_eff"][manifest["job"]]
    if v_eff - OVERLAP_SIGMAS * se > threshold:
        return "overlap high: low photon overlap does not explain the teleportation shortfall on this pair"
    return "unresolved: photon overlap and compiled-mesh error both remain candidates"


def simulated_iteration(item: tuple[dict[str, Any], dict[str, Any], float, float, tuple[float, ...]]) -> dict[str, Any]:
    """One results.json iteration: Perceval's photon distribution under NoiseModel(indistinguishability, g2), threshold
    clicks at per-mode detection probabilities, scaled to SAMPLES_PER_ITERATION two-or-more-click samples."""
    import perceval as pcvl
    from qd_teleportation_rehearsal import detected_clicks, perceval_circuit

    setting, circuit, hom, g2, transmission = item
    noise = pcvl.NoiseModel(indistinguishability=hom, g2=g2)
    processor = pcvl.Processor("SLOS", perceval_circuit(circuit, setting["circuit_params"]), noise=noise)
    processor.min_detected_photons_filter(1)
    processor.with_input(pcvl.BasicState(circuit["input_state"]))
    photons = {tuple(int(c) for c in state): float(p) for state, p in processor.probs()["results"].items()}
    clicks = {vector: p for vector, p in detected_clicks(photons, transmission).items() if sum(vector) >= 2}
    total = sum(clicks.values())
    counts = {
        "|" + ",".join(str(c) for c in vector) + ">": round(SAMPLES_PER_ITERATION * p / total)
        for vector, p in clicks.items()
    }
    return {
        "iteration": {"circuit_params": setting["circuit_params"], "compilation_seed": setting["compilation_seed"]},
        "counts": {state: n for state, n in sorted(counts.items()) if n},
    }


def simulate(out: Path, job: str, hom: float, g2: float, per_mode: bool) -> int:
    """Stage the case into OUT and write the local noise simulation's results.json beside it; per_mode applies the
    read's output transmissions (normalized to the largest, times the read's transmittance), else ideal detection."""
    from qd_teleportation_rehearsal import detection_efficiency

    held = [name for name in ("cases.json", "results.json") if (out / name).exists()]
    require(not held, f"{out} already holds {', '.join(held)}")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("cases.json", "circuit.json"):
        (out / name).write_bytes((CASES / job / name).read_bytes())
    manifest = json.loads((out / "cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((out / "circuit.json").read_text(encoding="utf-8"))
    t_out, _, figures = read_perfs(json.loads(READ.read_text(encoding="utf-8")))
    transmission = tuple(detection_efficiency(t_out, figures["transmittance"])) if per_mode else (1.0,) * MODES
    items = [(setting, circuit, hom, g2, transmission) for setting in manifest["settings"]]
    results = {"partial": False, "iterations": ordered_map(simulated_iteration, items, min_items=1)}
    (out / "results.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", choices=sorted(WINDOWS))
    group.add_argument("--analyze", type=Path)
    group.add_argument("--simulate", nargs=2, metavar=("OUT", "JOB"))
    group.add_argument("--check-live", choices=sorted(WINDOWS))
    parser.add_argument("--hom", type=float, default=1.0)
    parser.add_argument("--g2", type=float, default=0.0)
    parser.add_argument("--per-mode", action="store_true")
    args = parser.parse_args()
    if args.simulate:
        out, job = args.simulate
        require(job in WINDOWS, f"{job} is not a case of {sorted(WINDOWS)}")
        return simulate(Path(out), job, args.hom, args.g2, args.per_mode)
    if args.build:
        return build(args.build)
    if args.check_live:
        return check_live(args.check_live)
    if args.analyze:
        record = analyze(args.analyze)
        (args.analyze / "analysis.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
