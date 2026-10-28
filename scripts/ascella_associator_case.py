"""Ascella two-photon octonion-associator request: one qpu:ascella job of eight template iterations on twelve modes.

docs/design/ascella-two-photon-associator-case.md fixes the request. Two photons pass through L_a L_b or through
L_(ab), the left multiplications of the cd_core octonions. With a = (e6 + e7)/sqrt2 and b = (e5 + e7)/sqrt2 both
maps keep span(e0..e3); photons entering algebra modes 2 and 3 exit indistinguishable on the pairs {0,3}, {1,2}
after L_a L_b and on {0,2}, {1,3} after L_(ab), and distinguishable on the same uniform law after both. The
associative control takes a = (e1 + e2)/sqrt2 and b = (e1 + e3)/sqrt2 inside the quaternions, where the two
routes are the same operator. scripts/persona_corpus_checks.py derives these laws
(ascella_two_photon_associator).

Every iteration programs one 4 x 4 orthogonal block on logical modes 0..3 of the fixed four-mode Rx/phase
template of hypercomplex_cases.photonic_template, the identity on modes 4..11. ALGEBRA_TO_LOGICAL places
algebra modes 2 and 3 on logical modes 0 and 2, the connected source modes 0 and 2, so the twelve-entry input
holds photons on modes 0 and 2. The blocks run associator then control, each in the route order LaLb, Lab, Lab,
LaLb.

--check rebuilds the case in memory and compares it with the retained files, binds every iteration through
qd_platform.template_experiment (Perceval's unitary against the manifest operator), recomputes each iteration's
two-click law from that unitary by two-photon permanents, compares one iteration with Perceval's SLOS backend, and
requires the preregistered ideal endpoints. --analyze RUN reads a collected run's results.json and writes the
preregistered endpoints. Submission uses the generic runner, scripts/qd_platform.py plan/submit/collect, with the
written case's arguments.

Usage:
  "$PYTHON" scripts/ascella_associator_case.py [--check | --build | --analyze RUN]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

MODES = 12
LOGICAL = 4
CASE = ROOT / "results/quandela/cases/ascella_two_photon_associator/job-00"
DESIGN = "docs/design/ascella-two-photon-associator-case.md"
# Algebra basis index -> logical mode; the two photons enter algebra modes 2 and 3.
ALGEBRA_TO_LOGICAL = {2: 0, 0: 1, 3: 2, 1: 3}
PHOTON_ALGEBRA_MODES = (2, 3)
PAIRS = {"associator": ((6, 7), (5, 7)), "control": ((1, 2), (1, 3))}
ROUTE_ORDER = ("LaLb", "Lab", "Lab", "LaLb")
SAMPLES_PER_ITERATION = 2048
# Belenos's two-photon pair job needed 347113 shots for 5000 samples (69 per sample); 128 per sample leaves margin.
SHOTS_PER_ITERATION = 262144
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9
# Decision constants the design document preregisters.
MUTATION_TOLERANCE = 0.05
CALIBRATION_TOLERANCE = 0.05
# |Delta + 2 mean D_control| tolerance: the control block measures the same visibility factor f(V) in the job.
CLOSURE_TOLERANCE = 0.05
DETECTION_SIGMAS = 5


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def octonion_table() -> np.ndarray:
    table = np.zeros((8, 8, 8))
    for p in range(8):
        for q in range(8):
            table[p, q, p ^ q] = cd_sign(8, p, q)
    return table


def left(vector: np.ndarray) -> np.ndarray:
    """L_v with columns indexed by the input basis vector."""
    return np.einsum("p,pqr->rq", vector, octonion_table())


def route_operator(block: str, route: str) -> np.ndarray:
    """The logical 4 x 4 operator of one route: L_a L_b or L_(ab) restricted to span(e0..e3), relabelled."""
    eye = np.eye(8)
    (i, j), (k, m) = PAIRS[block]
    a = (eye[i] + eye[j]) / math.sqrt(2)
    b = (eye[k] + eye[m]) / math.sqrt(2)
    full = left(a) @ left(b) if route == "LaLb" else left(np.einsum("p,q,pqr->r", a, b, octonion_table()))
    require(np.allclose(full.T @ full, eye, atol=TOLERANCE), f"{block} {route} is not orthogonal")
    require(np.abs(full[4:, :4]).max() < TOLERANCE, f"{block} {route} leaves span(e0..e3)")
    logical = np.zeros((LOGICAL, LOGICAL))
    for row, column in itertools.product(range(LOGICAL), repeat=2):
        logical[ALGEBRA_TO_LOGICAL[row], ALGEBRA_TO_LOGICAL[column]] = full[row, column]
    return logical


def input_modes() -> tuple[int, int]:
    first, second = sorted(ALGEBRA_TO_LOGICAL[m] for m in PHOTON_ALGEBRA_MODES)
    return first, second


def pair_label(algebra_pair: tuple[int, int]) -> str:
    low, high = sorted(ALGEBRA_TO_LOGICAL[m] for m in algebra_pair)
    return f"{low}{high}"


# Two-click pairs of indistinguishable photons after each route, in logical labels.
PLUS_PAIRS = (pair_label((0, 3)), pair_label((1, 2)))
MINUS_PAIRS = (pair_label((0, 2)), pair_label((1, 3)))


def two_click_law(unitary: np.ndarray, visibility: float) -> dict[str, float]:
    """Unnormalized two-click probabilities over distinct logical modes for the mixture of visibility V.

    An indistinguishable pair exits (o1, o2) with |U_o1x U_o2y + U_o1y U_o2x|^2, a distinguishable one with
    |U_o1x U_o2y|^2 + |U_o1y U_o2x|^2.
    """
    x, y = input_modes()
    law = {}
    for o1, o2 in itertools.combinations(range(len(unitary)), 2):
        direct, exchange = unitary[o1, x] * unitary[o2, y], unitary[o1, y] * unitary[o2, x]
        law[f"{o1}{o2}"] = float(
            visibility * abs(direct + exchange) ** 2 + (1 - visibility) * (abs(direct) ** 2 + abs(exchange) ** 2)
        )
    return law


def endpoint(law: dict[str, float]) -> float:
    """D = P(PLUS_PAIRS | two clicks in the block) - P(MINUS_PAIRS | two clicks in the block)."""
    total = sum(law.values())
    return (sum(law[p] for p in PLUS_PAIRS) - sum(law[p] for p in MINUS_PAIRS)) / total


def predicted_difference(visibility: float) -> float:
    """D(LaLb) - D(Lab) on the associator block: 2 V / (V + 1.5 (1 - V)) under the mixture model."""
    return endpoint(two_click_law(route_operator("associator", "LaLb"), visibility)) - endpoint(
        two_click_law(route_operator("associator", "Lab"), visibility)
    )


def embed(matrix: np.ndarray) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    full[:LOGICAL, :LOGICAL] = matrix
    return full


def iteration_rows() -> list[dict[str, Any]]:
    return [
        {"block": block, "route": route, "arm": arm}
        for block in ("associator", "control")
        for arm, route in enumerate(ROUTE_ORDER)
    ]


def build_setting(item: tuple[int, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    index, row = item
    logical = route_operator(row["block"], row["route"]).astype(complex)
    mesh, parameters = photonic_template(logical)
    full = embed(logical)
    ideal = two_click_law(logical.real, 1.0)
    setting = {
        "name": f"{row['block']}-{row['route']}-arm{row['arm']}",
        "observation_index": index,
        **row,
        "ideal": {
            "two_click_law_indistinguishable": {k: round(v, 12) for k, v in ideal.items() if v > TOLERANCE},
            "D_indistinguishable": round(endpoint(ideal), 12),
            "D_distinguishable": round(endpoint(two_click_law(logical.real, 0.0)), 12),
        },
        "circuit_params": parameters,
        "column": [[float(value.real), float(value.imag)] for value in full[:, input_modes()[0]]],
        "operator": encoded(full),
    }
    return mesh, setting


def documents() -> dict[str, bytes]:
    built = ordered_map(build_setting, list(enumerate(iteration_rows())), min_items=1)
    template = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == template, f"iteration {index} needs another mesh than iteration 0")
    settings = [setting for _, setting in built]
    input_state = [0] * MODES
    for mode in input_modes():
        input_state[mode] = 1
    circuit = {**template, "modes": MODES, "input_state": input_state}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_two_photon_associator",
        "job": "job-00",
        "platforms": ["qpu:ascella", "sim:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 2,
        "max_samples": SAMPLES_PER_ITERATION * len(settings),
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(LOGICAL)),
        "algebra_to_logical": {str(k): v for k, v in sorted(ALGEBRA_TO_LOGICAL.items())},
        "eligibility": "exactly two occupied modes, both among logical modes 0..3",
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "plus_pairs": list(PLUS_PAIRS),
            "minus_pairs": list(MINUS_PAIRS),
            "primary_endpoint": "Delta = D(LaLb) - D(Lab) on the associator block",
            "mutation_endpoint": "Delta_control = D(LaLb) - D(Lab) on the control block",
            "detection_sigmas": DETECTION_SIGMAS,
            "mutation_tolerance": MUTATION_TOLERANCE,
            "closure_endpoint": "C = Delta + 2 mean(D_control): the control block's D is -f(V) for every V, so C = 0 "
            "for every visibility and a departure is route- or mesh-dependent error",
            "closure_tolerance": CLOSURE_TOLERANCE,
            "compensated_contrast": "Delta / (-2 mean D_control), 1 for every V under the two-photon mixture",
            "in_situ_visibility": "V_eff = 1.5 f / (1 + 0.5 f) with f = -mean D_control, compared with the HOM read",
            "hom_comparison": "descriptive: |Delta - Delta_pred(V_HOM)| with the HOM read's tolerance "
            "calibration_tolerance; no decision, since HOM visibility differs from the photon overlap through g2",
            "calibration_tolerance": CALIBRATION_TOLERANCE,
            "visibility_model": "Delta_pred = 2 V / (V + 1.5 (1 - V)), V the HOM fraction read at submission",
            "interpretation": "two-photon interference realisation of the octonion associator on the compiled mesh",
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def slos_law(unitary: np.ndarray, input_state: list[int]) -> dict[str, float]:
    """Two-click probabilities over all twelve modes from Perceval's SLOS backend, indistinguishable photons."""
    import perceval as pcvl

    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    backend.set_input_state(pcvl.BasicState(input_state))
    law: dict[str, float] = {}
    for state, probability in backend.prob_distribution().items():
        occupied = [mode for mode in range(len(input_state)) if state[mode] > 0]
        if len(occupied) == 2 and probability > TOLERANCE:
            law["".join(str(m) for m in occupied)] = float(probability)
    return law


def check() -> int:
    retained = {name: (CASE / name).read_bytes() for name in ("cases.json", "circuit.json")}
    rebuilt = documents()
    for name, data in rebuilt.items():
        require(retained[name] == data, f"{CASE}/{name} differs from the builder's bytes")
    manifest = json.loads(retained["cases.json"])
    circuit = json.loads(retained["circuit.json"])
    experiment, settings = template_experiment(manifest, circuit)
    require(experiment is not None and len(settings) == 8, "the template experiment did not bind eight settings")
    import perceval as pcvl

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
        block = unitary[:LOGICAL, :LOGICAL]
        require(np.abs(block.imag).max() < BODY_TOLERANCE, f"{setting['name']}: compiled block is not real")
        law = two_click_law(block.real, 1.0)
        expected = setting["ideal"]["two_click_law_indistinguishable"]
        for pair, value in law.items():
            require(abs(value - expected.get(pair, 0.0)) < BODY_TOLERANCE, f"{setting['name']}: pair {pair}")
        sign = 1 if setting["route"] == "LaLb" else -1
        deltas[setting["block"]].append(sign * endpoint(law))
        if setting["observation_index"] == 0:
            slos = slos_law(unitary, circuit["input_state"])
            for pair, value in law.items():
                require(abs(slos.get(pair, 0.0) - value) < BODY_TOLERANCE, f"SLOS differs on pair {pair}")
            require(set(slos) <= {p for p, v in law.items() if v > TOLERANCE}, "SLOS clicks outside the ideal")
    associator = sum(deltas["associator"]) / 2  # two arms per route
    control = sum(deltas["control"]) / 2
    require(abs(associator - 2) < BODY_TOLERANCE, f"ideal associator Delta {associator}")
    require(abs(control) < BODY_TOLERANCE, f"ideal control Delta {control}")
    require(abs(predicted_difference(0.875) - 2 * 0.875 / (0.875 + 1.5 * 0.125)) < TOLERANCE, "visibility model")
    print(f"ascella_two_photon_associator: 8 iterations bound; Delta {associator:.12f}, control {control:.12f}")
    return 0


def analyze(run: Path) -> dict[str, Any]:
    """Preregistered endpoints of a collected run: per-block Delta with its standard error, and the decisions."""
    manifest = json.loads((run / "cases.json").read_text())
    results = json.loads((run / "results.json").read_text())
    entries = results.get("iterations") or []
    tallies: dict[str, dict[str, list[int]]] = {b: {"LaLb": [0, 0, 0], "Lab": [0, 0, 0]} for b in PAIRS}
    excluded = 0
    counted = {block: 0 for block in PAIRS}
    for setting, entry in zip(manifest["settings"], entries, strict=False):
        counts = entry.get("counts") if isinstance(entry, dict) else None
        if not counts:
            continue
        counted[setting["block"]] += 1
        tally = tallies[setting["block"]][setting["route"]]
        for state, count in counts.items():
            occupation = [int(c) for c in state.strip("|>").split(",")]
            occupied = [m for m, n in enumerate(occupation) if n > 0]
            if len(occupied) != 2 or max(occupied) >= LOGICAL:
                excluded += count
                continue
            pair = f"{occupied[0]}{occupied[1]}"
            tally[0] += count if pair in PLUS_PAIRS else 0
            tally[1] += count if pair in MINUS_PAIRS else 0
            tally[2] += count
    out: dict[str, Any] = {"excluded_events": excluded}
    for block, routes in tallies.items():
        # A block decides only when all four ABBA iterations returned counts; a partial block stays descriptive.
        out[f"{block}_counted_iterations"] = counted[block]
        estimates: dict[str, dict[str, float] | None] = {}
        for route, (plus, minus, total) in routes.items():
            if total == 0:
                estimates[route] = None
                continue
            d = (plus - minus) / total
            q = (plus + minus) / total
            estimates[route] = {"D": d, "se": math.sqrt(max(q - d * d, 0.0) / total), "events": total}
        first, second = estimates["LaLb"], estimates["Lab"]
        if first is not None and second is not None:
            out[block] = {
                "routes": estimates,
                "Delta": first["D"] - second["D"],
                "se": math.hypot(first["se"], second["se"]),
            }
        else:
            out[block] = {"routes": estimates, "Delta": None}
    out["decisions"] = decisions(out, submission_visibility(run))
    return out


def submission_visibility(run: Path) -> float | None:
    """The HOM fraction submission.json recorded at plan time (perfs_at_plan["HOM (%)"] / 100), else None."""
    path = run / "submission.json"
    if not path.exists():
        return None
    hom = json.loads(path.read_text()).get("perfs_at_plan", {}).get("HOM (%)")
    if isinstance(hom, bool) or not isinstance(hom, int | float) or not 0 < hom <= 100:
        return None
    return float(hom) / 100


def visibility_from_contrast(f: float) -> float:
    """Inverse of f(V) = V / (V + 1.5 (1 - V)): V = 1.5 f / (1 + 0.5 f)."""
    return 1.5 * f / (1 + 0.5 * f)


def decisions(record: dict[str, Any], visibility: float | None) -> dict[str, Any]:
    """The design's two preregistered decisions and the descriptive HOM comparison.

    Associator realised: Delta > DETECTION_SIGMAS se and |Delta_control| <= max(MUTATION_TOLERANCE, 3 se_control).
    Visibility closure: |Delta + 2 mean D_control| <= max(CLOSURE_TOLERANCE, 3 se). Both control routes measure
    -f(V), so the closure holds at every photon overlap and needs no HOM figure; it uses both complete blocks. A
    decision stays undecided when a block it needs lacks any of its four ABBA iterations. The HOM comparison
    |Delta - Delta_pred(V_HOM)| is descriptive.
    """
    associator, control = record.get("associator", {}), record.get("control", {})
    complete = {block: record.get(f"{block}_counted_iterations") == len(ROUTE_ORDER) for block in PAIRS}
    out: dict[str, Any] = {"visibility_hom": visibility, "complete_blocks": complete}
    both = complete["associator"] and complete["control"]
    if not both or None in (associator.get("Delta"), control.get("Delta")):
        out["associator_realised"] = "undecided"
        out["visibility_closure"] = "undecided"
    else:
        detected = associator["Delta"] > DETECTION_SIGMAS * associator["se"]
        null = abs(control["Delta"]) <= max(MUTATION_TOLERANCE, 3 * control["se"])
        out["associator_realised"] = detected and null
        first, second = control["routes"]["LaLb"], control["routes"]["Lab"]
        mean_control = (first["D"] + second["D"]) / 2
        closure = associator["Delta"] + 2 * mean_control
        closure_se = math.sqrt(associator["se"] ** 2 + first["se"] ** 2 + second["se"] ** 2)
        out["closure"] = closure
        out["closure_se"] = closure_se
        out["visibility_closure"] = abs(closure) <= max(CLOSURE_TOLERANCE, 3 * closure_se)
        out["compensated_contrast"] = associator["Delta"] / (-2 * mean_control) if mean_control < 0 else None
        out["in_situ_visibility"] = visibility_from_contrast(-mean_control) if mean_control < 0 else None
    if complete["associator"] and associator.get("Delta") is not None and visibility is not None:
        predicted = predicted_difference(visibility)
        out["hom_comparison"] = {
            "Delta_predicted": predicted,
            "departure": abs(associator["Delta"] - predicted),
            "within_tolerance": abs(associator["Delta"] - predicted)
            <= max(CALIBRATION_TOLERANCE, 3 * associator["se"]),
        }
    else:
        out["hom_comparison"] = None
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", action="store_true")
    group.add_argument("--analyze", type=Path)
    args = parser.parse_args()
    if args.build:
        CASE.mkdir(parents=True, exist_ok=True)
        for name, data in documents().items():
            (CASE / name).write_bytes(data)
        return 0
    if args.analyze:
        record = analyze(args.analyze)
        (args.analyze / "analysis.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
