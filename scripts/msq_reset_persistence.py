"""Reset failure and its persistence across shots, read from the raw shot-ordered bits of measurement-sequence runs.

Each run holds the reset controls rc1 (x, measure into pre, reset, idle, measure into final, reset) and rc0 (the same
without the x) as consecutive fused PUBs, one member per layout qubit. The service executes a job column-wise, so shot
j of rc0 follows shot j of rc1 through the terminal reset, the repetition delay and the service's initialization,
and shot j + k (k >= 1) of rc0 follows it k full columns later
(docs/notes/ibm_quantum/repetition-rate-execution.md).

Per qubit and pooled the result reports:
- the reset failure: rc1's P(final 1 | pre 1), against rc0's ground baseline P(final 1 | pre 0);
- the reset-immune survival: among rc0 shots whose first read is 1, the fraction whose final read is 1;
- the double misread: rc1's P(final 1 | pre 0), which needs a true |1> misread by both pre and the reset;
- the persistence: rc0's first-read P1 at shot j + k after an rc1 final 1 at shot j, minus after a final 0, for
  k in LAGS; a qubit whose persistence at k = 0 reaches CARRIER_PERSISTENCE is a carrier;
- the coincidence: shots holding two or more events across qubits, against independent qubits.

A record whose collect.json carries the successor analysis (`pattern_crosscheck`, `screens`, `qubits`) also gets the
cross-shot model (pattern-row carryover against reset residue times persistence, no fitted parameter), the residue's
dependence on 1/T1, and the partial correlation of the measure arm's N = 16 transition excess with persistence given
the in-run assignment error and 1/T1, with each carrier left out and with every carrier left out. Small fits run in
pure Python, so the bytes do not depend on the BLAS build.

``--out FILE`` writes the result; ``--check FILE`` recomputes it and requires the retained bytes. No result here is a
preregistered verdict.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = "msq-reset-persistence-v1"
LAGS = (0, 1, 2, 10, 100)
CARRIER_PERSISTENCE = 0.1


def registers(path: Path) -> dict[str, np.ndarray]:
    """Every classical register of one raw PUB file as an integer array over shots."""
    data = json.loads(path.read_text())
    regs = data["registers"]
    if isinstance(regs, str):
        regs = ast.literal_eval(regs)
    return {name: np.array([int(bits, 2) for bits in body["bitstrings"]]) for name, body in regs.items()}


def rate(successes: int, trials: int) -> dict[str, Any]:
    return {"k": successes, "n": trials, "p": successes / trials if trials else None}


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting on a small dense system."""
    size = len(vector)
    rows = [list(matrix[i]) + [vector[i]] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(rows[r][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        if rows[col][col] == 0:
            raise ValueError("singular system")
        for r in range(size):
            if r != col:
                factor = rows[r][col] / rows[col][col]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[col], strict=True)]
    return [rows[i][size] / rows[i][i] for i in range(size)]


def ols(y: list[float], columns: list[list[float]]) -> tuple[list[float], list[float]]:
    """Least squares of y on the columns plus an intercept; the coefficients (intercept last) and residuals."""
    design = [[*(c[i] for c in columns), 1.0] for i in range(len(y))]
    width = len(design[0])
    normal = [[math.fsum(row[a] * row[b] for row in design) for b in range(width)] for a in range(width)]
    target = [math.fsum(row[a] * yi for row, yi in zip(design, y, strict=True)) for a in range(width)]
    beta = solve(normal, target)
    residual = [
        yi - math.fsum(b * x for b, x in zip(beta, row, strict=True)) for yi, row in zip(y, design, strict=True)
    ]
    return beta, residual


def corr(x: list[float], y: list[float]) -> float:
    mx, my = math.fsum(x) / len(x), math.fsum(y) / len(y)
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True))
    return sxy / math.sqrt(math.fsum((a - mx) ** 2 for a in x) * math.fsum((b - my) ** 2 for b in y))


def r_squared(y: list[float], residual: list[float]) -> float:
    my = math.fsum(y) / len(y)
    return 1 - math.fsum(r * r for r in residual) / math.fsum((v - my) ** 2 for v in y)


def partial_corr(y: list[float], x: list[float], controls: list[list[float]]) -> float:
    return corr(ols(y, controls)[1], ols(x, controls)[1])


def analyse(run_dir: Path) -> dict[str, Any]:
    record = json.loads((run_dir / "record.json").read_text())
    pubs = record["execution_pubs"]
    raw_dirs = sorted(p for p in (run_dir / "raw").iterdir() if p.is_dir())
    if len(raw_dirs) != 1:
        raise ValueError(f"{run_dir} holds {len(raw_dirs)} raw job directories, not one")
    raw = raw_dirs[0]

    def find(prefix: str) -> int:
        return next(i for i, pub in enumerate(pubs) if pub["components"][0]["member"].startswith(prefix))

    def prefixes(index: int) -> dict[str, str]:
        return {str(c["physical_qubits"][0]): c["register_prefix"] for c in pubs[index]["components"]}

    i1 = find("msqe_rc1_")
    if not pubs[i1 + 1]["components"][0]["member"].startswith("msqe_rc0_"):
        raise ValueError(f"{run_dir}: rc0 does not follow rc1")
    r1, r0 = registers(raw / f"pub_{i1:02d}.json"), registers(raw / f"pub_{i1 + 1:02d}.json")
    p1, p0 = prefixes(i1), prefixes(i1 + 1)
    qubits = sorted(p1, key=int)
    bits = {
        q: (r1[p1[q] + "r0_pre"], r1[p1[q] + "r0_final"], r0[p0[q] + "r0_pre"], r0[p0[q] + "r0_final"]) for q in qubits
    }
    per: dict[str, Any] = {}
    for q in qubits:
        a, f, b, g = bits[q]
        failed = f == 1
        lags = {}
        for k in LAGS:
            ev, target = failed[: len(failed) - k], b[k:]
            lags[str(k)] = {
                "after_failure": rate(int(target[ev].sum()), int(ev.sum())),
                "after_success": rate(int(target[~ev].sum()), int((~ev).sum())),
            }
        lag0 = lags["0"]
        per[q] = {
            "reset_failure": rate(int(f[a == 1].sum()), int((a == 1).sum())),
            "ground_baseline": rate(int(g[b == 0].sum()), int((b == 0).sum())),
            "immune_survival": rate(int(g[b == 1].sum()), int((b == 1).sum())),
            "double_misread": rate(int(f[a == 0].sum()), int((a == 0).sum())),
            "persistence": lag0["after_failure"]["p"] - lag0["after_success"]["p"],
            "lags": lags,
        }
    carriers = [q for q in qubits if per[q]["persistence"] >= CARRIER_PERSISTENCE]

    def pooled(key: str, group: list[str]) -> dict[str, Any]:
        return rate(sum(per[q][key]["k"] for q in group), sum(per[q][key]["n"] for q in group))

    groups = {"all": qubits, "carriers": carriers, "others": [q for q in qubits if q not in carriers]}
    summary: dict[str, Any] = {}
    for name, group in groups.items():
        if not group:
            continue
        entry: dict[str, Any] = {
            key: pooled(key, group) for key in ("reset_failure", "ground_baseline", "immune_survival", "double_misread")
        }
        lag_table = {}
        for k in LAGS:
            s = sum(per[q]["lags"][str(k)]["after_failure"]["k"] for q in group)
            n = sum(per[q]["lags"][str(k)]["after_failure"]["n"] for q in group)
            sb = sum(per[q]["lags"][str(k)]["after_success"]["k"] for q in group)
            nb = sum(per[q]["lags"][str(k)]["after_success"]["n"] for q in group)
            base = sb / nb
            lag_table[str(k)] = {
                "after_failure": rate(s, n),
                "after_success": rate(sb, nb),
                "z": (s / n - base) / math.sqrt(base * (1 - base) / n),
            }
        entry["lags"] = lag_table
        summary[name] = entry

    coincidence = {}
    for name, events in (
        ("immune", [(bits[q][2] == 1) & (bits[q][3] == 1) for q in qubits]),
        ("reset_failure", [bits[q][1] == 1 for q in qubits]),
    ):
        matrix = np.array(events)
        rates = [float(row.mean()) for row in matrix]
        none = math.prod(1 - r for r in rates)
        one = math.fsum(r * math.prod(1 - s for j, s in enumerate(rates) if j != i) for i, r in enumerate(rates))
        per_shot = matrix.sum(axis=0)
        coincidence[name] = {
            "events": int(matrix.sum()),
            "shots": int(matrix.shape[1]),
            "shots_with_two_or_more": int((per_shot >= 2).sum()),
            "expected_independent": (1 - none - one) * matrix.shape[1],
            "max_per_shot": int(per_shot.max()),
        }
    result: dict[str, Any] = {
        "run": run_dir.name,
        "shots": int(len(bits[qubits[0]][0])),
        "carrier_rule": f"persistence at k = 0 at least {CARRIER_PERSISTENCE}",
        "carriers": carriers,
        "pooled": summary,
        "coincidence": coincidence,
        "per_qubit": per,
    }
    collect = json.loads((run_dir / "collect.json").read_text())[0].get("family_analysis", {}).get("relaxation")
    if isinstance(collect, dict) and "pattern_crosscheck" in collect:
        result["successor_analysis"] = successor_links(record, collect, registers, raw, find, prefixes, per, carriers)
    return result


def successor_links(
    record: dict[str, Any],
    collect: dict[str, Any],
    load: Callable[[Path], dict[str, np.ndarray]],
    raw: Path,
    find: Callable[[str], int],
    prefixes: Callable[[int], dict[str, str]],
    per: dict[str, Any],
    carriers: list[str],
) -> dict[str, Any]:
    """The cross-shot model, the residue's 1/T1 dependence and the transition-excess links of a successor run."""
    calibration: dict[str, Any] = {}
    for group in record["groups"]:
        calibration.update(group.get("placed_qubit_calibration", {}))
    iro = find("msq_ro0_")
    ro0, pro = load(raw / f"pub_{iro:02d}.json"), prefixes(iro)
    screens, rows, cross = collect["screens"], collect["qubits"], collect["pattern_crosscheck"]["per_qubit"]
    qubits = sorted(per, key=int)
    residue = [per[q]["reset_failure"]["p"] - per[q]["ground_baseline"]["p"] for q in qubits]
    persistence = [per[q]["persistence"] for q in qubits]
    predicted = [screens[q]["reset_diagnostic"]["difference"] * per[q]["persistence"] for q in qubits]
    observed = [cross[q]["d"] for q in qubits]
    se = [cross[q]["se"] for q in qubits]
    scale = math.fsum(p * o / s**2 for p, o, s in zip(predicted, observed, se, strict=True)) / math.fsum(
        p * p / s**2 for p, s in zip(predicted, se, strict=True)
    )
    chi = math.fsum(((o - p) / s) ** 2 for p, o, s in zip(predicted, observed, se, strict=True))
    inv_t1_cal = [1 / calibration[q]["T1"] for q in qubits]
    inv_t1_fit = [1e-6 / rows[q]["fitted"]["t1_s"] for q in qubits]
    fits = {}
    for label, inv in (("calibrated_t1", inv_t1_cal), ("fitted_t1", inv_t1_fit)):
        beta, res = ols(residue, [inv])
        fits[label] = {"slope_us": beta[0], "intercept": beta[1], "r_squared": r_squared(residue, res)}
    excess = [rows[q]["transitions"]["16"]["rate"] - rows[q]["transitions"]["16"]["ideal"] for q in qubits]
    ground = [float(ro0[pro[q] + "r0_final"].mean()) for q in qubits]
    assignment = [g + rows[q]["readout"]["offset"] + g for g, q in zip(ground, qubits, strict=True)]
    controls = [assignment, inv_t1_cal]
    left_out = {}
    for drop in carriers:
        keep = [i for i, q in enumerate(qubits) if q != drop]
        left_out[drop] = partial_corr(
            [excess[i] for i in keep], [persistence[i] for i in keep], [[c[i] for i in keep] for c in controls]
        )
    keep = [i for i, q in enumerate(qubits) if q not in carriers]
    departure = [rows[q]["departure_n16"]["difference"] for q in qubits]
    return {
        "cross_shot_model": {
            "corr": corr(predicted, observed),
            "chi2_model": chi,
            "chi2_zero": math.fsum((o / s) ** 2 for o, s in zip(observed, se, strict=True)),
            "best_scale": scale,
            "dof": len(qubits) - 1,
        },
        "residue_vs_inverse_t1": fits,
        "transition_excess": {
            "median_excess": float(np.median(excess)),
            "partial_corr_with_persistence": partial_corr(excess, persistence, controls),
            "leave_one_carrier_out": left_out,
            "without_carriers": partial_corr(
                [excess[i] for i in keep], [persistence[i] for i in keep], [[c[i] for i in keep] for c in controls]
            ),
        },
        "departure_n16_corr_with_persistence": corr(departure, persistence),
    }


def render(results: list[dict[str, Any]]) -> str:
    return json.dumps({"schema": SCHEMA, "runs": results}, indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path, help="collected run directories holding raw/")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    text = render([analyse(run) for run in args.runs])
    if args.out is not None:
        args.out.write_text(text)
        return 0
    if args.check.read_text() != text:
        print(f"{args.check} differs from the recomputed result", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
