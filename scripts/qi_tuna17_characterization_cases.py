"""Tuna-17 per-qubit characterization: readout assignment, T1 and an X90 repetition ladder, with a QX twin.

The provider withholds its per-qubit calibration series (docs/evidence/quantum_inspire/status-sources-2026-11-15),
so this case measures three quantities on every qubit at once:

- readout-0 and readout-1: no gate, and X on every qubit; P(1|0) and P(1|1) per qubit, at the start and the end
  of the series;
- t1-N: X on every qubit, then wait(N) cycles of 20 ns on every qubit, N in T1_CYCLES; the corrected excited
  population (P1 - P(1|0)) / (P(1|1) - P(1|0)) against the delay gives T1 by a weighted fit of its logarithm;
- x90-K: 4K X90 pulses on every qubit, K in LADDER_TURNS, each sequence a whole number of full turns; the corrected
  ground population at 32, 128 and 256 pulses is a pass or fail endpoint, and 2 p0 - 1 against the pulse count
  gives a decay length in pulses when the contrast stays positive. P(0) is periodic in a coherent over-rotation
  (cos^2(n e / 2) after n pulses), so the ladder bounds no error, and it gives no randomized-benchmarking figure.

Profiles: tuna_17 (17 qubits; 16,384 shots per readout circuit, 8,192 per other circuit) and qx (the same texts
on 10 qubits at 1,024 shots, within the emulator's 10 qubits and 2,048 shots). Bit order: qubit 0 is the
rightmost character of a shot.

    --write ROOT        write ROOT/characterization_{tuna_17,qx}/ (batch-NN/ of at most 3 circuits, cases.json,
                        prediction.json)
    --check ROOT        regenerate and compare every file of both directories except CASE.md
    --local             run every circuit of the qx profile once on the local qxelarator emulator and require its
                        noiseless outcome; the tuna_17 texts come from the same builder at 17 qubits
    --sanity RUN_DIR    after a collection: every job completed with all its shots, and each circuit with a fixed
                        noiseless outcome (readout-0, readout-1, t1-0, x90-0) reads it on all but
                        SANITY_WRONG_QUBITS qubits; batches 02 and 04 hold no such circuit and get the job check only
    --analyze OUT RUN_DIR...   per-qubit readout, T1 and ladder rows with the verdicts of prediction.json;
                        --retained PATH names the retained rows of the readout verdict (default: this checkout's
                        docs/evidence/qi-status-context/retained-context.json, used when its profile has the
                        runs' qubit count)

Usage: "$QI_PYTHON" scripts/qi_tuna17_characterization_cases.py (--write ROOT | --check ROOT | --local |
       --sanity RUN_DIR | --analyze OUT RUN_DIR... [--retained PATH])
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

SCHEMA = "qi-tuna17-characterization-cases-v1"
ANALYSIS_SCHEMA = "qi-tuna17-characterization-analysis-v1"
CYCLE_SECONDS = 20e-9
T1_CYCLES = (0, 250, 500, 1000, 2000, 4000)
LADDER_TURNS = (0, 8, 32, 64)
BATCH_LIMIT = 3
PROFILES: dict[str, dict[str, Any]] = {
    "tuna_17": {"backend": "tuna_17", "backend_type_id": 7, "nqubits": 17, "readout_shots": 16384, "shots": 8192},
    "qx": {
        "backend": "QXsinglenodesimulator",
        "backend_type_id": 1,
        "nqubits": 10,
        "readout_shots": 1024,
        "shots": 1024,
    },
}
# Decision thresholds of prediction.json. The readout tolerance is the distance from the retained row of
# 2026-10-17; the population floor keeps the logarithm of a T1 point away from the assignment noise.
READOUT_TOLERANCE = 0.03
T1_CHI_SQUARE_PROBABILITY = 0.01
LADDER_MIN_P0 = 0.5
POPULATION_FLOOR = 0.05
# A readout pair whose two probabilities lie closer than this cannot correct a population.
MIN_READOUT_SPAN = 0.2
# sanity() stops a series when more qubits than this read the wrong side of 0.5 on a circuit whose noiseless
# outcome is fixed. Single weak qubits are the finding the series records and stop nothing.
SANITY_WRONG_QUBITS = 3
RETAINED_CONTEXT = Path(__file__).resolve().parents[1] / "docs/evidence/qi-status-context/retained-context.json"
# Seconds per job from docs/notes/quantum_inspire/usage.md ("Run on Tuna-17"): 2.6 s plus 0.53 ms per shot.
JOB_SECONDS, SHOT_SECONDS = 2.6, 0.53e-3


def circuit(nqubits: int, gate_lines: list[str]) -> str:
    body = "".join(f"{line}\n" for line in gate_lines)
    return f"version 3.0\n\nqubit[{nqubits}] q\nbit[{nqubits}] b\n\n{body}\nbarrier q\nb = measure q\n"


def circuits(nqubits: int) -> dict[str, tuple[str, str, dict[str, int]]]:
    """Circuit file name -> (text, kind, parameters), in series order."""
    every = range(nqubits)
    found: dict[str, tuple[str, str, dict[str, int]]] = {
        "readout-0.cq": (circuit(nqubits, []), "readout", {"prepared": 0}),
        "readout-1.cq": (circuit(nqubits, [f"X q[{q}]" for q in every]), "readout", {"prepared": 1}),
    }
    for cycles in T1_CYCLES:
        lines = [f"X q[{q}]" for q in every] + ([f"wait({cycles}) q[{q}]" for q in every] if cycles else [])
        found[f"t1-{cycles}.cq"] = (circuit(nqubits, lines), "t1", {"wait_cycles": cycles})
    for turns in LADDER_TURNS:
        lines = [f"X90 q[{q}]" for _ in range(4 * turns) for q in every]
        found[f"x90-{turns}.cq"] = (circuit(nqubits, lines), "x90", {"pulses": 4 * turns})
    return found


def batches() -> list[list[str]]:
    """The series: an opening readout pair, the T1 and ladder circuits in order, a closing readout pair."""
    readout = ["readout-0.cq", "readout-1.cq"]
    t1 = [f"t1-{cycles}.cq" for cycles in T1_CYCLES]
    ladder = [f"x90-{turns}.cq" for turns in LADDER_TURNS]
    return [readout, t1[:3], t1[3:], ladder[:2], ladder[2:], readout]


def job_seconds(profile: dict[str, Any], name: str) -> float:
    shots = profile["readout_shots"] if name.startswith("readout") else profile["shots"]
    wait = int(name[3:-3]) * CYCLE_SECONDS if name.startswith("t1-") else 0.0
    return float(JOB_SECONDS + shots * (SHOT_SECONDS + wait))


def expected_seconds(profile: dict[str, Any]) -> float:
    return round(sum(job_seconds(profile, name) for names in batches() for name in names), 1)


def files(profile_name: str) -> dict[str, str]:
    """Relative path -> text of every generated file of one profile's case directory."""
    profile = PROFILES[profile_name]
    texts = circuits(profile["nqubits"])
    out: dict[str, str] = {}
    names = []
    for index, batch in enumerate(batches()):
        name = f"batch-{index:02d}"
        names.append(name)
        shots = profile["readout_shots"] if batch[0].startswith("readout") else profile["shots"]
        rows = []
        for file_name in batch:
            text, kind, parameters = texts[file_name]
            out[f"{name}/{file_name}"] = text
            rows.append(
                {"file": file_name, "kind": kind, **parameters, "sha256": hashlib.sha256(text.encode()).hexdigest()}
            )
        manifest = {
            "schema": SCHEMA,
            "backend": profile["backend"],
            "backend_type_id": profile["backend_type_id"],
            "nqubits": profile["nqubits"],
            "shots": shots,
            "bit_order": "qubit 0 at the rightmost character",
            "circuits": rows,
        }
        out[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
    index_record = {
        "schema": SCHEMA,
        "profile": profile_name,
        "backend": profile["backend"],
        "cycle_seconds": CYCLE_SECONDS,
        "t1_wait_cycles": list(T1_CYCLES),
        "ladder_pulses": [4 * turns for turns in LADDER_TURNS],
        "batch_limit": BATCH_LIMIT,
        "circuits": sum(len(batch) for batch in batches()),
        "batches": names,
    }
    out["cases.json"] = json.dumps(index_record, indent=1) + "\n"
    prediction = {
        "schema": "qi-tuna17-characterization-prediction-v1",
        "profile": profile_name,
        "noiseless_outcome": {"readout-0": "all 0", "readout-1": "all 1", "t1": "all 1", "x90": "all 0"},
        "expected_execution_seconds": expected_seconds(profile),
        "seconds_model": "2.6 s per job plus 0.53 ms per shot plus the circuit's wait per shot",
        "thresholds": {
            "readout_tolerance_against_2026_10_17": READOUT_TOLERANCE,
            "t1_chi_square_probability": T1_CHI_SQUARE_PROBABILITY,
            "ladder_min_p0": LADDER_MIN_P0,
            "population_floor": POPULATION_FLOOR,
        },
        "verdicts": {
            "readout": "per qubit: both closing-pair probabilities within the tolerance of the retained row",
            "readout_stable": "per qubit: the closing pair within the tolerance of the opening pair",
            "t1": "per qubit: a single exponential fits the points above the population floor",
            "ladder": "per qubit: corrected P(0) at 32, 128 and 256 pulses each at or above the minimum",
        },
    }
    out["prediction.json"] = json.dumps(prediction, indent=1) + "\n"
    return out


def case_directory(root: Path, profile_name: str) -> Path:
    return root / f"characterization_{profile_name}"


def write(root: Path) -> None:
    for profile_name in PROFILES:
        for relative, text in files(profile_name).items():
            target = case_directory(root, profile_name) / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")


def check(root: Path) -> list[str]:
    """Every difference between the generated files and ROOT, CASE.md excepted."""
    problems = []
    for profile_name in PROFILES:
        directory = case_directory(root, profile_name)
        wanted = files(profile_name)
        for relative, text in wanted.items():
            target = directory / relative
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                problems.append(f"{target} differs from the generator")
        held = (
            {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
            if directory.is_dir()
            else set()
        )
        problems += [f"{directory / extra} is not generated" for extra in sorted(held - set(wanted) - {"CASE.md"})]
    return problems


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def p1(shots: list[str], nqubits: int) -> list[float]:
    return [sum(bit(shot, qubit) for shot in shots) / len(shots) for qubit in range(nqubits)]


def local() -> list[str]:
    """Run the qx profile's circuits once on the local emulator; the list names each outcome that is not noiseless.

    Every circuit is deterministic without noise, so one iteration decides it. The 17-qubit ladder circuits ran
    past five minutes on the build host (measured 2026-11-15, stopped), so the local run keeps to the 10-qubit twin.
    """
    import qxelarator  # noqa: PLC0415 - present in the Quantum Inspire environment only

    problems = []
    nqubits = PROFILES["qx"]["nqubits"]
    for name, (text, kind, parameters) in circuits(nqubits).items():
        result = qxelarator.execute_string(text, iterations=1)
        counts = getattr(result, "results", None)
        want = ("1" if kind == "t1" or parameters.get("prepared") == 1 else "0") * nqubits
        if counts != {want: 1}:
            problems.append(f"qx {name}: {str(counts if counts is not None else result)[:120]}, want all {want[0]}")
    return problems


def read_run(run: Path) -> tuple[dict[str, Any], dict[str, list[str]]]:
    cases = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    raw = {
        row["file"]: json.loads((run / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]
        if (run / "raw" / f"{row['file']}.json").is_file()
    }
    return cases, raw


def sanity(run: Path) -> list[str]:
    cases, raw = read_run(run)
    problems = []
    jobs = json.loads((run / "results.json").read_text(encoding="utf-8")).get("jobs") or []
    by_file = {entry["file"]: entry for entry in jobs}
    for row in cases["circuits"]:
        entry = by_file.get(row["file"])
        results = (entry or {}).get("results") or []
        if entry is None or entry["job"].get("status") != "completed" or not results:
            problems.append(f"{row['file']}: no completed job")
        elif results[0].get("shots_done") != cases["shots"] or len(raw.get(row["file"], [])) != cases["shots"]:
            problems.append(f"{row['file']}: {results[0].get('shots_done')} shots done of {cases['shots']}")
    if problems:
        return problems
    for row in cases["circuits"]:
        want = anchor(row)
        if want is None:
            continue
        wrong = [q for q, value in enumerate(p1(raw[row["file"]], cases["nqubits"])) if (value > 0.5) != (want == 1)]
        if len(wrong) > SANITY_WRONG_QUBITS:
            problems.append(f"{row['file']}: qubits {wrong} read the wrong side of 0.5, want all {want}")
    return problems


def anchor(row: dict[str, Any]) -> int | None:
    """The noiseless bit of a circuit that holds no wait and no pulse train, or None.

    Every circuit treats all qubits alike, so no check here detects a reversed bit order; bit() rests on the
    manifest's bit_order, which the retained Tuna-17 runs established.
    """
    if row["kind"] == "readout":
        return int(row["prepared"])
    if row["kind"] == "t1" and row["wait_cycles"] == 0:
        return 1
    if row["kind"] == "x90" and row["pulses"] == 0:
        return 0
    return None


def retained_rows(path: Path, nqubits: int) -> dict[int, dict[str, float]]:
    """Qubit -> retained readout pair of scripts/qi_retained_context.py's document, or {} for another register."""
    if not path.is_file():
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in document.get("qubits", []) if "readout" in row]
    if len(document.get("qubits", [])) != nqubits:
        return {}
    return {
        row["qubit"]: {"p1_given_0": row["readout"]["p1_given_0"], "p1_given_1": row["readout"]["p1_given_1"]}
        for row in rows
    }


def binomial_variance(p: float, count: int) -> float:
    """Variance of an observed fraction, with the quarter-count term that keeps it positive at p = 0 or 1."""
    return (p * (1 - p) + 0.25 / count) / count


def chi_square_probability(chi_square: float, freedom: int) -> float:
    """Upper tail of the chi-square distribution, by the regularized incomplete gamma function's series or fraction."""
    if freedom <= 0:
        return 1.0
    a, x = freedom / 2.0, chi_square / 2.0
    if x <= 0:
        return 1.0
    if x < a + 1.0:
        term = total = 1.0 / a
        for n in range(1, 500):
            term *= x / (a + n)
            total += term
        return max(0.0, 1.0 - total * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    tiny = 1e-300
    b = x + 1.0 - a
    c, d = 1.0 / tiny, 1.0 / b
    h = d
    for n in range(1, 500):
        an = -n * (n - a)
        b += 2.0
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        h *= d * c
    return min(1.0, h * math.exp(-x + a * math.log(x) - math.lgamma(a)))


def decay_fit(points: list[tuple[float, float, float]]) -> dict[str, Any] | None:
    """Weighted least squares of ln(value) = intercept - x / length over (x, value, standard error) points."""
    rows = [(x, math.log(value), error / value) for x, value, error in points if value > POPULATION_FLOOR and error > 0]
    if len(rows) < 3:
        return None
    weights = [1.0 / sigma**2 for _, _, sigma in rows]
    sw = sum(weights)
    sx = sum(w * x for w, (x, _, _) in zip(weights, rows, strict=True))
    sy = sum(w * y for w, (_, y, _) in zip(weights, rows, strict=True))
    sxx = sum(w * x * x for w, (x, _, _) in zip(weights, rows, strict=True))
    sxy = sum(w * x * y for w, (x, y, _) in zip(weights, rows, strict=True))
    determinant = sw * sxx - sx * sx
    slope = (sw * sxy - sx * sy) / determinant
    intercept = (sy - slope * sx) / sw
    chi_square = sum(w * (y - intercept - slope * x) ** 2 for w, (x, y, _) in zip(weights, rows, strict=True))
    freedom = len(rows) - 2
    found: dict[str, Any] = {"points": len(rows), "chi_square": chi_square, "freedom": freedom}
    found["chi_square_probability"] = chi_square_probability(chi_square, freedom)
    if slope < 0:
        found["length"] = -1.0 / slope
        found["length_se"] = math.sqrt(sw / determinant) / slope**2
    return found


def analyze(runs: list[Path], retained: dict[int, dict[str, float]] | None = None) -> dict[str, Any]:
    """Per-qubit readout, T1 and ladder rows from collected run directories, with the verdicts of prediction.json.

    A corrected population is (p - zero) / span with zero and span from the mean of the readout pairs. Its
    variance holds the binomial terms of p, zero and one; the covariance that the shared pair puts between two
    points is left out, so the chi-square probability is approximate where the readout terms dominate.
    """
    readouts: list[dict[str, Any]] = []
    t1_raw: dict[int, tuple[list[float], int]] = {}
    ladder_raw: dict[int, tuple[list[float], int]] = {}
    nqubits = 0
    for run in runs:
        cases, raw = read_run(run)
        nqubits = cases["nqubits"]
        rows = {row["file"]: row for row in cases["circuits"]}
        if {"readout-0.cq", "readout-1.cq"} <= set(raw):
            readouts.append(
                {
                    "p1_given_0": p1(raw["readout-0.cq"], nqubits),
                    "p1_given_1": p1(raw["readout-1.cq"], nqubits),
                    "shots": min(len(raw["readout-0.cq"]), len(raw["readout-1.cq"])),
                }
            )
        for name, shots in raw.items():
            if rows[name]["kind"] == "t1":
                t1_raw[rows[name]["wait_cycles"]] = (p1(shots, nqubits), len(shots))
            elif rows[name]["kind"] == "x90":
                ladder_raw[rows[name]["pulses"]] = (p1(shots, nqubits), len(shots))
    if not readouts:
        raise SystemExit("qi_tuna17_characterization_cases: no collected readout pair among the run directories")
    readout_shots = sum(pair["shots"] for pair in readouts)
    longest = 4 * max(LADDER_TURNS)
    qubits = []
    for qubit in range(nqubits):
        zero = sum(pair["p1_given_0"][qubit] for pair in readouts) / len(readouts)
        one = sum(pair["p1_given_1"][qubit] for pair in readouts) / len(readouts)
        span = one - zero
        row: dict[str, Any] = {
            "qubit": qubit,
            "readout": [
                {"p1_given_0": pair["p1_given_0"][qubit], "p1_given_1": pair["p1_given_1"][qubit]} for pair in readouts
            ],
        }
        last = readouts[-1]
        if retained and qubit in retained:
            moved = max(
                abs(last["p1_given_0"][qubit] - retained[qubit]["p1_given_0"]),
                abs(last["p1_given_1"][qubit] - retained[qubit]["p1_given_1"]),
            )
            row["readout_within_tolerance"] = moved <= READOUT_TOLERANCE
        if len(readouts) > 1:
            first = readouts[0]
            row["readout_drift"] = max(
                abs(last["p1_given_0"][qubit] - first["p1_given_0"][qubit]),
                abs(last["p1_given_1"][qubit] - first["p1_given_1"][qubit]),
            )
            row["readout_stable"] = row["readout_drift"] <= READOUT_TOLERANCE
        if span <= MIN_READOUT_SPAN:
            row["readout_unusable"] = True
            qubits.append(row)
            continue
        zero_variance, one_variance = binomial_variance(zero, readout_shots), binomial_variance(one, readout_shots)

        def corrected(p: float, count: int, zero: float = zero, span: float = span) -> tuple[float, float]:
            value = (p - zero) / span
            variance = binomial_variance(p, count) + (1 - value) ** 2 * zero_variance + value**2 * one_variance  # noqa: B023
            return value, math.sqrt(variance) / span

        points = [
            (cycles * CYCLE_SECONDS * 1e6, *corrected(values[qubit], count))
            for cycles, (values, count) in sorted(t1_raw.items())
        ]
        fit = decay_fit(points)
        if fit is None:
            if t1_raw:
                row["t1_unfitted"] = "fewer than three points above the population floor"
        else:
            row["t1"] = {
                "us": fit.get("length"),
                "us_se": fit.get("length_se"),
                **{k: fit[k] for k in ("points", "chi_square", "freedom", "chi_square_probability")},
            }
            row["t1_single_exponential"] = (
                fit.get("length") is not None and fit["chi_square_probability"] >= T1_CHI_SQUARE_PROBABILITY
            )
            if fit.get("length") is not None and points:
                # A decay this slow leaves the points flat within the window; the fitted value is a lower scale.
                row["t1_beyond_window"] = fit["length"] > 10 * points[-1][0]
        ladder_points = []
        ladder_p0 = {}
        for pulses, (values, count) in sorted(ladder_raw.items()):
            value, error = corrected(values[qubit], count)
            ladder_p0[pulses] = 1.0 - value
            ladder_points.append((float(pulses), 1 - 2 * value, 2 * error))
        if ladder_p0:
            row["ladder_p0"] = {str(pulses): p0 for pulses, p0 in ladder_p0.items()}
        if longest in ladder_p0:
            row["ladder_p0_at_longest"] = ladder_p0[longest]
        if {4 * turns for turns in LADDER_TURNS if turns} <= set(ladder_p0):
            row["ladder_clears"] = all(p0 >= LADDER_MIN_P0 for pulses, p0 in ladder_p0.items() if pulses)
        ladder_fit = decay_fit(ladder_points)
        # A point at or below the floor is a contrast an exponential cannot hold, so the decay length needs them all.
        if ladder_fit is not None and ladder_fit.get("length") and ladder_fit["points"] == len(ladder_points):
            row["ladder"] = {
                "decay_pulses": ladder_fit["length"],
                "decay_pulses_se": ladder_fit["length_se"],
                "chi_square_probability": ladder_fit["chi_square_probability"],
            }
        qubits.append(row)
    return {"schema": ANALYSIS_SCHEMA, "runs": [run.name for run in runs], "nqubits": nqubits, "qubits": qubits}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, metavar="ROOT")
    group.add_argument("--check", type=Path, metavar="ROOT")
    group.add_argument("--local", action="store_true")
    group.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    group.add_argument("--analyze", nargs="+", type=Path, metavar="PATH", help="OUT followed by the run directories")
    parser.add_argument("--retained", type=Path, default=RETAINED_CONTEXT, help="retained rows of the readout verdict")
    args = parser.parse_args(argv)
    if args.write:
        write(args.write)
        return 0
    if args.analyze:
        if len(args.analyze) < 2:
            parser.error("--analyze takes OUT and at least one RUN_DIR")
        nqubits = json.loads((args.analyze[1] / "cases.json").read_text(encoding="utf-8"))["nqubits"]
        found = analyze(args.analyze[1:], retained_rows(args.retained, nqubits))
        args.analyze[0].write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
        return 0
    problems = check(args.check) if args.check else local() if args.local else sanity(args.sanity)
    for problem in problems:
        print(f"qi_tuna17_characterization_cases: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
