"""Analysis of a collected coherence-window run: branch-signed work coherence per context.

Counts bind to the submission through patch_window_analysis._bound_counts
(record, raw ledger, PUB manifest and circuit archive digests). Two layers:

- Preregistered: the five precision endpoints of
  coherence_window.coherence_contracts, evaluated by
  experiment_optimizer.analyze_observations with the planner's grouped
  Hoeffding bounds, from the record's own contracts and PUB grouping.
- Descriptive: per context, C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 with
  S_PQ = E[(-1)^(b0 + a + b)], its modulus and argument, the rotation and
  modulus ratio between adjacent contexts, the branch-unsigned coherence (the
  negative control, zero on an ideal device), and the ZZ setting's one-hot
  and spectator-sector populations.
- Timing: each context's executed work exposure (free-precession time of
  the physical qubits read into the work clbits, from the record's
  readout_qubits map and the returned scheduler timing, averaged over the
  Pauli settings) and each job's execution timestamps. The idle-versus-
  immediate rotation per microsecond of extra exposure sets an idle
  detuning rate, and the measure_reset rotation net of that rate times its
  exposure excess over the matched idle is reported separately; it crosses
  jobs, so it bounds a measurement-induced phase only together with the
  jobs' execution times. Each +-1 score has per-shot variance
  1 - S^2, circuits are independent, and intervals are 95 percent normal
  (delta method); an argument is reported only where the modulus interval
  excludes zero.

Usage: "$PYTHON" scripts/coherence_window_analysis.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/coherence_window_analysis.py --self-check
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from coherence_window import (  # noqa: E402
    CLBITS,
    COHERENCE_PRECISION,
    CONTEXTS,
    PAULI_SETTINGS,
    READ_A,
    READ_B,
    SECTOR,
    coherence_circuit,
    coherence_contracts,
    signed_parity,
    unsigned_parity,
)
from experiment_optimizer import (  # noqa: E402
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    analyze_observations,
)
from patch_characterization import WORK_B  # noqa: E402

Z95 = 1.959963984540054


def _estimate(dist: np.ndarray, shots: int, score: tuple[float, ...]) -> tuple[float, float]:
    """Mean of a +-1 score and its variance over shots independent shots."""
    mean = float(np.asarray(score) @ dist)
    return mean, max(0.0, 1.0 - mean * mean) / shots


def context_coherence(
    dists: dict[str, np.ndarray], shots: dict[str, int], context: str, score: tuple[float, ...]
) -> dict[str, Any]:
    s = {
        p: _estimate(dists[f"coherence_{context}_{p}"], shots[f"coherence_{context}_{p}"], score)
        for p in PAULI_SETTINGS
    }
    re, im = (s["xx"][0] + s["yy"][0]) / 4, (s["xy"][0] - s["yx"][0]) / 4
    var_re, var_im = (s["xx"][1] + s["yy"][1]) / 16, (s["xy"][1] + s["yx"][1]) / 16
    modulus = math.hypot(re, im)
    var_mod = (re * re * var_re + im * im * var_im) / modulus**2 if modulus > 0 else var_re + var_im
    out: dict[str, Any] = {
        "re": re,
        "im": im,
        "re_ci": [re - Z95 * math.sqrt(var_re), re + Z95 * math.sqrt(var_re)],
        "im_ci": [im - Z95 * math.sqrt(var_im), im + Z95 * math.sqrt(var_im)],
        "modulus": modulus,
        "modulus_ci": [modulus - Z95 * math.sqrt(var_mod), modulus + Z95 * math.sqrt(var_mod)],
        "_var": (var_re, var_im),
    }
    if out["modulus_ci"][0] > 0:
        var_arg = (re * re * var_im + im * im * var_re) / modulus**4
        arg = math.atan2(im, re)
        out["argument"] = arg
        out["argument_ci"] = [arg - Z95 * math.sqrt(var_arg), arg + Z95 * math.sqrt(var_arg)]
        out["_var_arg"] = var_arg
    return out


def compare(later: dict[str, Any], earlier: dict[str, Any]) -> dict[str, Any]:
    """Rotation arg(C_later / C_earlier) and modulus ratio, where both arguments are defined."""
    if "argument" not in later or "argument" not in earlier:
        return {"rotation": None, "reason": "a modulus interval reaches zero; the argument is undefined"}
    rotation = cmath.phase(complex(later["re"], later["im"]) / complex(earlier["re"], earlier["im"]))
    half = Z95 * math.sqrt(later["_var_arg"] + earlier["_var_arg"])
    ratio = later["modulus"] / earlier["modulus"]
    var_ratio = ratio**2 * (
        ((later["modulus_ci"][1] - later["modulus"]) / Z95 / later["modulus"]) ** 2
        + ((earlier["modulus_ci"][1] - earlier["modulus"]) / Z95 / earlier["modulus"]) ** 2
    )
    return {
        "rotation": rotation,
        "rotation_ci": [rotation - half, rotation + half],
        "modulus_ratio": ratio,
        "modulus_ratio_ci": [ratio - Z95 * math.sqrt(var_ratio), ratio + Z95 * math.sqrt(var_ratio)],
    }


def excess_rotation(signed: dict[str, dict[str, Any]], exposure: dict[str, float]) -> dict[str, Any] | None:
    """measure_reset rotation net of the idle detuning rate times its exposure excess over the matched idle.

    With k the ratio of the measure_reset excess to the matched-idle excess, the
    value is arg C_mr - (1 + k) arg C_mi + k arg C_imm. Both comparisons contain
    the matched idle, so its argument variance enters once with weight
    (1 + k)^2: Var = v_mr + (1 + k)^2 v_mi + k^2 v_imm.
    """
    if any("argument" not in signed[context] for context in CONTEXTS):
        return None
    idle_extra = exposure["matched_idle"] - exposure["immediate"]
    window_extra = exposure["measure_reset"] - exposure["matched_idle"]
    if idle_extra <= 0.05:
        return None
    k = window_extra / idle_extra
    value_of = {context: complex(signed[context]["re"], signed[context]["im"]) for context in CONTEXTS}
    idle = cmath.phase(value_of["matched_idle"] / value_of["immediate"])
    window = cmath.phase(value_of["measure_reset"] / value_of["matched_idle"])
    value = window - k * idle
    variance = (
        signed["measure_reset"]["_var_arg"]
        + (1 + k) ** 2 * signed["matched_idle"]["_var_arg"]
        + k**2 * signed["immediate"]["_var_arg"]
    )
    half = Z95 * math.sqrt(variance)
    return {
        "idle_rate_rad_per_us": idle / idle_extra,
        "exposure_excess_us": window_extra,
        "excess_rotation": value,
        "excess_rotation_ci": [value - half, value + half],
    }


def populations(dist: np.ndarray) -> dict[str, float]:
    one_hot = sum(float(p) for o, p in enumerate(dist) if ((o >> READ_A) ^ (o >> READ_B)) & 1)
    sector = sum(float(p) for o, p in enumerate(dist) if not (o >> SECTOR) & 1)
    return {"one_hot": one_hot, "spectator_ground": sector}


def analyze(
    dists: dict[str, np.ndarray],
    shots: dict[str, int],
    contracts: tuple[ObservableContract, ...],
    pubs: dict[str, list[str]],
    exposure: dict[str, float] | None = None,
    jobs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    observed = tuple(
        ObservedPub(name, {member: (tuple(float(x) for x in dists[member]),) for member in members}, shots[members[0]])
        for name, members in pubs.items()
    )
    prereg = analyze_observations(observed, contracts)
    signed = {c: context_coherence(dists, shots, c, signed_parity()) for c in CONTEXTS}
    unsigned = {c: context_coherence(dists, shots, c, unsigned_parity()) for c in CONTEXTS}
    comparisons = {
        "matched_idle_vs_immediate": compare(signed["matched_idle"], signed["immediate"]),
        "measure_reset_vs_matched_idle": compare(signed["measure_reset"], signed["matched_idle"]),
    }
    result: dict[str, Any] = {
        "preregistered": [
            {"name": row.name, "estimate": row.estimate, "interval": [row.lo, row.hi], "alpha": row.alpha}
            for row in prereg.observables
        ],
        "signed_coherence": {c: {k: v for k, v in s.items() if not k.startswith("_")} for c, s in signed.items()},
        "comparisons": comparisons,
        "unsigned_coherence_negative_control": {
            c: {k: u[k] for k in ("re", "im", "re_ci", "im_ci")} for c, u in unsigned.items()
        },
        "zz_populations": {c: populations(dists[f"coherence_{c}_zz"]) for c in CONTEXTS},
        "executed_exposure_us": exposure,
        "jobs": jobs,
    }
    if exposure is not None:
        result["measure_reset_net_of_idle_detuning"] = excess_rotation(signed, exposure)
    return result


def from_run(run: Path) -> dict[str, Any]:
    from patch_window_analysis import _bound_counts, executed_idle_us

    record = json.loads((run / "record.json").read_text())
    counts = _bound_counts(run)
    configuration = record["family_configuration"]
    readout = configuration["readout_qubits"]
    work = (readout["read_a"], readout["read_b"])
    exposure: dict[str, float] | None = {}
    for context in CONTEXTS:
        values = [
            executed_idle_us(f"coherence_{context}_{setting}", qubit, configuration["dt_seconds"])
            for setting in PAULI_SETTINGS
            for qubit in work
        ]
        if exposure is not None and all(v is not None for v in values):
            exposure[context] = float(np.mean([v for v in values if v is not None]))
        else:
            exposure = None
    jobs = []
    for job in record["submission"]["jobs"]:
        metrics = sorted((run / "raw" / job["job_id"]).glob("job_metrics*.json"))
        timestamps = json.loads(metrics[-1].read_text()).get("timestamps") if metrics else None
        jobs.append({"job_id": job["job_id"], "kind": job["kind"], "members": job["members"], "timestamps": timestamps})
    dists, shots = {}, {}
    for member, counter in counts.items():
        total = sum(counter.values())
        vector = np.zeros(1 << CLBITS)
        for bits, n in counter.items():
            vector[int(bits, 2)] += n
        dists[member], shots[member] = vector / total, total
    contracts = tuple(
        ObservableContract(
            c["name"],
            tuple(ObservableTerm(t["member"], tuple(t["values"]), t["sign"]) for t in c["terms"]),
            c["null_value"],
            c["minimum_effect"],
            c["alpha"],
            c["power"],
            c["precision_half_width"],
        )
        for c in record["observable_contracts"]
    )
    pubs = {pub["name"]: [component["member"] for component in pub["components"]] for pub in record["execution_pubs"]}
    return analyze(dists, shots, contracts, pubs, exposure, jobs)


def self_check() -> None:
    from qiskit.circuit import CircuitInstruction
    from qiskit.circuit.library import RZGate

    from qpe_diagnostics import ideal_branch_probabilities

    rng = np.random.default_rng(20261014)
    rotation, shrink, epsilon, shots = 0.25, 0.8, 0.05, 400_000
    dists, sizes = {}, {}
    for context in CONTEXTS:
        for setting in (*PAULI_SETTINGS, "zz"):
            circuit = coherence_circuit(context, setting, 1000)
            if context == "measure_reset":
                index = next(i for i, op in enumerate(circuit.data) if op.operation.name == "reset")
                circuit.data.insert(index + 1, CircuitInstruction(RZGate(rotation), (circuit.qubits[WORK_B],)))
            law = np.asarray(ideal_branch_probabilities(circuit), dtype=float)
            if context != "immediate":
                # Dephasing shrinks the work coherence: mix toward the fully dephased law.
                law = shrink * law + (1 - shrink) * _dephased(law, setting)
            flipped = (1 - epsilon) * law
            for outcome, p in enumerate(law):
                flipped[outcome ^ 1] += epsilon * p
            name = f"coherence_{context}_{setting}"
            dists[name], sizes[name] = rng.multinomial(shots, flipped) / shots, shots
    contracts = coherence_contracts(COHERENCE_PRECISION, 0.05, 0.8)
    pubs = {name: [name] for name in dists}
    result = analyze(dists, sizes, contracts, pubs)
    scale = 1 - 2 * epsilon
    immediate = result["signed_coherence"]["immediate"]
    if abs(immediate["modulus"] - 0.5 * scale) > 0.01:
        raise RuntimeError(f"immediate |C| {immediate['modulus']} differs from {0.5 * scale}")
    idle = result["comparisons"]["matched_idle_vs_immediate"]
    window = result["comparisons"]["measure_reset_vs_matched_idle"]
    if abs(idle["rotation"]) > 0.02 or abs(idle["modulus_ratio"] - shrink) > 0.02:
        raise RuntimeError(f"pure dephasing should shrink without rotating: {idle}")
    if abs(abs(window["rotation"]) - rotation) > 0.02 or abs(window["modulus_ratio"] - 1.0) > 0.03:
        raise RuntimeError(f"a window rotation should rotate without shrinking: {window}")
    for control in result["unsigned_coherence_negative_control"].values():
        if abs(control["re"]) > 0.01 or abs(control["im"]) > 0.01:
            raise RuntimeError("the branch-unsigned coherence should vanish")
    if [row["name"] for row in result["preregistered"]] != [c.name for c in contracts]:
        raise RuntimeError("the preregistered endpoints differ from the contracts")
    # An idle detuning of 0.1 rad/us with 3.3 us of extra idle and 0.4 us more
    # exposure in measure_reset leaves no excess once the rate is subtracted;
    # distinct per-context variances fix the matched idle's (1 + k)^2 weight.
    variances = {"immediate": 1e-4, "matched_idle": 4e-4, "measure_reset": 9e-4}
    arguments = {"immediate": 0.0, "matched_idle": 0.33, "measure_reset": 0.37}
    signed = {
        c: {"re": math.cos(a), "im": math.sin(a), "argument": a, "_var_arg": variances[c]} for c, a in arguments.items()
    }
    detuned = excess_rotation(signed, {"immediate": 1.0, "matched_idle": 4.3, "measure_reset": 4.7})
    k = 0.4 / 3.3
    half = Z95 * math.sqrt(
        variances["measure_reset"] + (1 + k) ** 2 * variances["matched_idle"] + k**2 * variances["immediate"]
    )
    if (
        detuned is None
        or abs(detuned["excess_rotation"]) > 1e-12
        or abs(detuned["idle_rate_rad_per_us"] - 0.1) > 1e-12
        or abs(detuned["excess_rotation_ci"][1] - half) > 1e-12
    ):
        raise RuntimeError(f"the idle-detuning correction is wrong: {detuned}")


def _dephased(law: np.ndarray, setting: str) -> np.ndarray:
    """The law after full work dephasing: Pauli X/Y readouts of each work qubit become uniform."""
    if setting == "zz":
        return law
    out = np.zeros_like(law)
    for outcome, p in enumerate(law):
        for a in (0, 1):
            for b in (0, 1):
                moved = outcome & ~((1 << READ_A) | (1 << READ_B)) | (a << READ_A) | (b << READ_B)
                out[moved] += p / 4
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", nargs="?", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.self_check:
        self_check()
        print("coherence window analysis: dephasing shrinks, a window phase rotates, the unsigned control vanishes")
        return 0
    if args.run is None:
        parser.error("a collected run directory or --self-check is required")
    text = json.dumps(from_run(args.run), indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
