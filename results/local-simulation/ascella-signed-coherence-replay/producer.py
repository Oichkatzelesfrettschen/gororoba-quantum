"""Replay the frozen Ascella signed-coherence job body locally and run its registered estimators.

The retained job body of results/quandela/cases/ascella_signed_coherence/job-00
is deserialized and executed on local Perceval SLOS and Naive backends with
network connections forbidden: exact probabilities of every entry over all
twelve output modes, and the whole 64-entry iterator sampled at its budgets.
The registered estimators of scripts/ascella_coherence_analysis.py then run on
expected counts of the ideal response, on the sampled SLOS counts and on
synthetic responses built from the request's own analyzers: the equal-contrast
mutation counterexample, the sign-even counterexamples of twists 0.2 and 0.05,
a diagonal bright/dark mixture, complex conjugation, exchanged X and Y readouts,
a missing iteration and an iteration without eligible events. docs/evidence/ascella-order-coefficients/derivation.json
supplies the radii, coefficients and expected dispositions every case must
reproduce.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
from ascella_coherence_analysis import BASIS_NAMES, analyze  # noqa: E402
from bdsc_certificate import close  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASE = ROOT / "results/quandela/cases/ascella_signed_coherence/job-00"
DERIVATION = ROOT / "docs/evidence/ascella-order-coefficients/derivation.json"
SEED = 20261024
SAMPLES = 8192
MODES = 12
LOGICAL = 4
TOLERANCE = 1e-12
# Twelve-mode count rows of the 64 iterations; None marks an iteration without attributable counts.
Rows = list[list[float] | None]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def deny_connection(event: str, arguments: tuple[Any, ...]) -> None:
    if event in {"socket.connect", "socket.sendto", "socket.getaddrinfo"}:
        raise RuntimeError("Local replay forbids network connections")


def manifest() -> dict[str, Any]:
    return dict(json.loads((CASE / "cases.json").read_text(encoding="utf-8")))


@cache
def computations() -> list[Any]:
    """Every entry of the retained body's ComputationIterator with its parameters bound, decoded once per worker."""
    from perceval.serialization import deserialize

    body = json.loads((CASE / "job-body.json").read_text(encoding="utf-8"))
    return list(deserialize(body["payload"]["computation"]))


def mode_vector(states: dict[Any, float], label: str) -> list[float]:
    """Twelve per-mode weights of single-photon output states; any other state width or occupation raises."""
    vector = [0.0] * MODES
    for state, weight in states.items():
        occupations = list(state)
        require(len(occupations) == MODES, f"{label}: an output state spans {len(occupations)} modes, not {MODES}")
        require(sum(occupations) == 1, f"{label}: an output state holds {sum(occupations)} photons")
        vector[occupations.index(1)] += float(weight)
    return vector


def probability_row(task: tuple[str, int]) -> list[float]:
    """Exact twelve-mode output law of one entry; it must equal the manifest column squared within 1e-12."""
    import perceval as pcvl

    sys.addaudithook(deny_connection)
    backend, index = task
    setting = manifest()["settings"][index]
    result = pcvl.SimulatedComputer(backend).probs(computations()[index].experiment, precision=1e-14)
    measured = mode_vector(result["results"], f"{backend} entry {index}")
    expected = [real * real + imaginary * imaginary for real, imaginary in setting["column"]]
    residual = max(abs(a - b) for a, b in zip(measured, expected, strict=True))
    require(residual <= TOLERANCE, f"{backend} entry {index}: probabilities depart by {residual:.2e}")
    require(abs(sum(measured) - 1) <= TOLERANCE, f"{backend} entry {index}: probabilities sum to {sum(measured)}")
    require(sum(measured[LOGICAL:]) <= TOLERANCE, f"{backend} entry {index}: mass leaves the logical block")
    return measured


def sample_iterator(backend: str) -> list[list[float]]:
    """Twelve-mode single-photon counts of every entry of the whole iterator, sampled at its 8,192-sample budget."""
    import perceval as pcvl
    from perceval.serialization import deserialize

    sys.addaudithook(deny_connection)
    pcvl.random_seed(SEED)
    body = json.loads((CASE / "job-body.json").read_text(encoding="utf-8"))
    result = pcvl.SimulatedComputer(backend).execute(deserialize(body["payload"]["computation"]))
    rows = [
        mode_vector(row["results"], f"{backend} sample {index}") for index, row in enumerate(result["results_list"])
    ]
    require([sum(row) for row in rows] == [float(SAMPLES)] * 64, f"{backend}: iterator sample counts differ")
    return rows


def operator(setting: dict[str, Any]) -> np.ndarray:
    entry = setting["operator"]
    full = np.asarray(entry["real"], dtype=float) + 1j * np.asarray(entry["imaginary"], dtype=float)
    return np.asarray(full[:LOGICAL, :LOGICAL])


def prepared_states(settings: list[dict[str, Any]]) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Each entry's pre-analyzer source state and analyzer, both read from the request's own operators.

    A readout entry and the direct entry of its block share theta, phi and generator, so the direct operator's
    source column is the prepared state and O_readout O_direct^dagger is the analyzer, which must be H_X or H_Y
    on the mode pair (0, 3) and the identity elsewhere.
    """
    direct = {
        (s["theta_index"], s["arm"], s["generator"], s["block"] == "mutation"): operator(s)
        for s in settings
        if s["readout"] == "direct"
    }
    expected = {
        "direct": np.eye(2),
        "x": np.array([[1, 1], [1, -1]]) / math.sqrt(2),
        "y": np.array([[1, -1j], [1, 1j]]) / math.sqrt(2),
    }
    states, analyzers = [], []
    for setting in settings:
        prepared = direct[
            (setting["theta_index"], setting["arm"], setting["generator"], setting["block"] == "mutation")
        ]
        analyzer = operator(setting) @ prepared.conj().T
        reference = np.eye(LOGICAL, dtype=complex)
        reference[np.ix_([0, 3], [0, 3])] = expected[setting["readout"]]
        deviation = float(np.max(np.abs(analyzer - reference)))
        require(deviation <= TOLERANCE, f"{setting['name']}: the request's analyzer departs by {deviation:.2e}")
        states.append(prepared[:, 0])
        analyzers.append(analyzer)
    return states, analyzers


def twisted(state: np.ndarray, sign: int, twist: float) -> np.ndarray:
    """The sign-even counterexample state: coherence C_s (1 + s t i), bright population (1 + t^2)/2, p2 = 0."""
    coherence = 2 * np.conj(state[0]) * state[3] * (1 + sign * twist * 1j)
    bright = math.sqrt(0.5 * (1 + twist**2))
    dark = coherence / (2 * bright)
    remainder = 1 - bright**2 - abs(dark) ** 2
    require(remainder >= -TOLERANCE, f"twist {twist}: the counterexample state is not positive")
    return np.array([bright, math.sqrt(max(0.0, remainder)), 0, dark], dtype=complex)


def expected_counts(probabilities: list[np.ndarray]) -> Rows:
    rows: Rows = []
    for vector in probabilities:
        full = np.zeros(MODES)
        full[:LOGICAL] = vector
        rows.append([float(value) * SAMPLES for value in full])
    return rows


SYNTHETIC_CASES = (
    "ideal",
    "equal contrast",
    "sign-even 0.2",
    "sign-even 0.05",
    "conjugation",
    "diagonal mixture",
    "exchanged readouts",
    "missing iteration",
    "zero-eligible iteration",
)


@cache
def request_states() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """The prepared states and analyzers of the retained request, derived once per worker."""
    return prepared_states(manifest()["settings"])


def amplitudes(setting: dict[str, Any], state: np.ndarray, case: str, target: dict[str, float]) -> np.ndarray:
    """The pre-analyzer state a synthetic response assigns to one entry."""
    if case.startswith("sign-even") and setting["block"] != "mutation":
        return twisted(state, setting["phi_sign"], 0.2 if case == "sign-even 0.2" else 0.05)
    if case == "conjugation":
        return np.conj(state)
    if case == "equal contrast" and setting["block"] == "mutation":
        dark = target["target_dark"] if setting["generator"] == "j" else target["mutation_dark"]
        return np.array([math.sqrt(1 - dark), 0, 0, math.sqrt(dark)], dtype=complex)
    return state


def synthesize(case: str) -> tuple[str, Rows]:
    """Expected counts of one synthetic response through the request's own analyzers."""
    settings = manifest()["settings"]
    states, analyzers = request_states()
    target = json.loads(DERIVATION.read_text(encoding="utf-8"))["mutation"]["equal_contrast_counterexample"]
    if case == "diagonal mixture":
        # A bright/dark-dephased state keeps every direct intensity and loses the (0, 3) coherence.
        return case, expected_counts(
            [np.abs(h) ** 2 @ (np.abs(v) ** 2) for h, v in zip(analyzers, states, strict=True)]
        )
    modified = (
        states
        if case in SYNTHETIC_CASES[6:]
        else [amplitudes(setting, state, case, target) for setting, state in zip(settings, states, strict=True)]
    )
    rows = expected_counts([np.abs(h @ v) ** 2 for h, v in zip(analyzers, modified, strict=True)])
    if case == "exchanged readouts":
        position = {(s["readout"], s["theta_index"], s["arm"], s["block"]): i for i, s in enumerate(settings)}
        swapped: Rows = []
        for setting, row in zip(settings, rows, strict=True):
            other = {"x": "y", "y": "x"}.get(setting["readout"])
            key = (other, setting["theta_index"], setting["arm"], f"theta{setting['theta_index']}-{other}")
            swapped.append(row if other is None else rows[position[key]])
        return case, swapped
    if case == "missing iteration":
        rows[17] = None
    if case == "zero-eligible iteration":
        rows[17] = [0.0] * MODES
    return case, rows


def synthetic_cases() -> dict[str, Rows]:
    """Expected counts of every synthetic response, keyed by case name in registered order."""
    return dict(ordered_map(synthesize, list(SYNTHETIC_CASES), min_items=1))


def analyze_case(item: tuple[str, Rows]) -> tuple[str, dict[str, Any]]:
    name, counts = item
    return name, analyze(manifest(), counts)


def by_name(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["name"]: row for row in result["endpoints"]}


def registered_name(entry: dict[str, Any]) -> str:
    return f"{entry['row']}_even {entry['basis']}"


def require_dispositions(results: dict[str, dict[str, Any]], derivation: dict[str, Any]) -> None:
    """The acceptance of plan step replay-request-locally and the design's named alternatives."""
    ideal = by_name(results["ideal"])
    radii = derivation["hoeffding_radii_at_8192"]
    coefficient_rows = {"X_odd": 0, "Y_odd": 1, "dark": 2}
    for name, row in ideal.items():
        require(row["verdict"] == "qualifies" and not row["ideal_excluded"], f"ideal: {name} is {row['verdict']}")
        require(abs(row["value"] - row["ideal"]) <= TOLERANCE, f"ideal: {name} departs from its registered ideal")
        if row["parity"] in ("odd", "even", "dark"):
            index = BASIS_NAMES.index(row["basis"])
            key = {
                "odd": "analyzer_coefficients",
                "even": "sign_even_analyzer_coefficients",
                "dark": "dark_coefficients",
            }
            require(abs(row["radius"] - radii[key[row["parity"]]][index]) <= TOLERANCE, f"ideal: {name} radius")
            prefix = name.split(" ")[0]
            if prefix in coefficient_rows:
                closed = derivation["coefficients"][coefficient_rows[prefix]][index]
                require(abs(row["ideal"] - closed) <= TOLERANCE, f"ideal: {name} differs from the derivation")
            else:
                require(row["ideal"] == 0.0, f"ideal: {name} is not the registered zero")
    require(abs(ideal["mutation difference"]["radius"] - radii["mutation_difference"]) <= TOLERANCE, "contrast radius")
    require(abs(ideal["mutation dark"]["radius"] - radii["mutation_dark"]) <= TOLERANCE, "closure radius")
    require(
        abs(ideal["mutation difference"]["ideal"] - derivation["mutation"]["ideal_contrast"]) <= TOLERANCE,
        "the mutation difference ideal differs from the derivation",
    )
    sampled = by_name(results["sampled SLOS"])
    for name, row in sampled.items():
        require(row["verdict"] == "qualifies" and not row["ideal_excluded"], f"sampled: {name} is {row['verdict']}")
    contrast = by_name(results["equal contrast"])
    require(contrast["mutation difference"]["verdict"] == "qualifies", "equal contrast: the difference fails")
    require(contrast["mutation dark"]["verdict"] == "falsified", "equal contrast: mutation closure is not falsified")
    strong = by_name(results["sign-even 0.2"])
    for name, row in strong.items():
        if row["parity"] in ("odd", "dark"):
            require(abs(row["value"] - ideal[name]["value"]) <= TOLERANCE, f"sign-even 0.2: {name} leaves its ideal")
    falsified = sorted(name for name, row in strong.items() if row["verdict"] == "falsified")
    named = sorted(registered_name(e) for e in derivation["sign_even_counterexample"]["rejected_at_expected_counts"])
    require(falsified == named, f"sign-even 0.2 falsifies {falsified}, not the derivation's {named}")
    for entry in derivation["sign_even_counterexample"]["rejected_at_expected_counts"]:
        require(abs(strong[registered_name(entry)]["value"] - entry["value"]) <= TOLERANCE, f"{entry} value")
    weak = by_name(results["sign-even 0.05"])
    require(all(row["verdict"] == "qualifies" for row in weak.values()), "sign-even 0.05 fails the tolerance")
    excluded = sorted(results["sign-even 0.05"]["ideal_excluded"])
    named = sorted(registered_name(e) for e in derivation["weak_sign_even_case"]["ideal_excluded_at_expected_counts"])
    require(excluded == named, f"sign-even 0.05 excludes {excluded}, not the derivation's {named}")
    mixture = by_name(results["diagonal mixture"])
    for name in ("X_odd constant", "X_odd cos(2 theta)", "Y_odd sin(2 theta)"):
        require(mixture[name]["verdict"] == "falsified", f"diagonal mixture: {name} is not falsified")
    require(all(mixture[f"dark {basis}"]["verdict"] == "qualifies" for basis in BASIS_NAMES), "mixture: dark moves")
    conjugate = by_name(results["conjugation"])
    require(conjugate["Y_odd sin(2 theta)"]["verdict"] == "falsified", "conjugation: Y sin(2 theta) survives")
    require(conjugate["X_odd constant"]["verdict"] == "qualifies", "conjugation: X constant moves")
    exchanged = by_name(results["exchanged readouts"])
    for name in ("X_odd constant", "Y_odd sin(2 theta)"):
        require(exchanged[name]["verdict"] == "falsified", f"exchanged readouts: {name} is not falsified")
    for name in ("missing iteration", "zero-eligible iteration"):
        require(not results[name]["complete"], f"a {name} still yields a complete inference")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report() -> dict[str, Any]:
    sys.addaudithook(deny_connection)
    settings = manifest()["settings"]
    derivation = json.loads(DERIVATION.read_text(encoding="utf-8"))
    tasks = [(backend, index) for backend in ("SLOS", "Naive") for index in range(len(settings))]
    probabilities = ordered_map(probability_row, tasks, min_items=1)
    slos, naive = probabilities[: len(settings)], probabilities[len(settings) :]
    agreement = float(np.max(np.abs(np.array(slos) - np.array(naive))))
    require(agreement <= TOLERANCE, f"SLOS and Naive probabilities differ by {agreement:.2e}")
    sampled = ordered_map(sample_iterator, ["SLOS", "Naive"], min_items=1)
    cases = synthetic_cases()
    replay_counts: Rows = [[value * SAMPLES for value in row] for row in slos]
    synthesized = float(np.max(np.abs(np.array(replay_counts) - np.array(cases["ideal"]))))
    require(synthesized <= TOLERANCE * SAMPLES, f"the synthesized ideal departs from SLOS by {synthesized:.2e} counts")
    cases["ideal"] = replay_counts
    cases["sampled SLOS"] = list(sampled[0])
    results = dict(ordered_map(analyze_case, list(cases.items()), min_items=1))
    require_dispositions(results, derivation)
    paths = [
        Path(__file__).resolve(),
        ROOT / "scripts/ascella_coherence_analysis.py",
        ROOT / "gororoba_quantum/parallel.py",
        ROOT / "scripts/bdsc_certificate.py",
        CASE / "cases.json",
        CASE / "job-body.json",
        DERIVATION,
    ]
    return {
        "schema": "ascella-signed-coherence-replay-v1",
        "boundary": (
            "Ideal local Perceval simulation of the retained job body and registered estimators on expected and "
            "sampled counts; hardware instruments and their configuration are absent."
        ),
        "seed": SEED,
        "versions": {name: importlib.metadata.version(name) for name in ("perceval-quandela", "exqalibur", "numpy")},
        "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in paths},
        "probability_checks": {
            "entries": len(settings),
            "backends": ["SLOS", "Naive"],
            "output_modes": MODES,
            "slos_naive_max_difference": agreement,
        },
        "iterator_checks": [
            {"backend": backend, "samples_per_entry": [sum(row) for row in rows], "samples_total": sum(map(sum, rows))}
            for backend, rows in zip(("SLOS", "Naive"), sampled, strict=True)
        ],
        "cases": {
            name: {
                "complete": result["complete"],
                **(
                    {
                        "verdicts": result["verdicts"],
                        "ideal_excluded": result["ideal_excluded"],
                        "endpoints": [
                            {key: row[key] for key in ("name", "value", "ideal", "radius", "interval", "verdict")}
                            for row in result["endpoints"]
                        ],
                    }
                    if result["complete"]
                    else {"reason": result["reason"]}
                ),
            }
            for name, result in results.items()
            if name != "sampled SLOS"
        }
        | {
            "sampled SLOS": {
                "complete": results["sampled SLOS"]["complete"],
                "verdicts": results["sampled SLOS"]["verdicts"],
                "ideal_excluded": results["sampled SLOS"]["ideal_excluded"],
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the frozen Ascella signed-coherence body locally.")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("replay-ordered-map-cancel.json"))
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    evidence = report()
    if arguments.check:
        retained = json.loads(arguments.out.read_text(encoding="utf-8"))
        # Tool versions describe the writing host; the dispositions above are the decisive content.
        close(
            {k: v for k, v in retained.items() if k != "versions"},
            {k: v for k, v in evidence.items() if k != "versions"},
            "Ascella signed-coherence replay",
        )
    else:
        arguments.out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verdicts = {name: case.get("verdicts") for name, case in evidence["cases"].items()}
    print(f"Replayed 128 probability checks and two iterators; case verdicts {verdicts}")


if __name__ == "__main__":
    main()
