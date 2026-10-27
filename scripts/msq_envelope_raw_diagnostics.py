"""Shot-order diagnostics of a collected measurement-sequence envelope run, read from its raw shot-ordered bits.

The envelope job holds one fused dynamic PUB per member row, every row the same member on every layout qubit. The
service executes a job's circuits column-wise, every circuit once per shot index in submission order
(docs/notes/ibm_quantum/repetition-rate-execution.md), and gives no guarantee of that order; the run's executor
reports one chunk holding every PUB. If the order holds, shot j of PUB k follows shot j of PUB k - 1 by one circuit,
and shot j - 1 or j + 1 of PUB k - 1 lies a full column away. The adjacency section tests that: the conditional
difference P(final_k = 1 | final_prev = 1) - P(final_k = 1 | final_prev = 0) per row and qubit, at the same shot and at
the misaligned shots, which share the drift but not the predecessor.

Carryover. The ro0 row (measure only) follows a row ending near |1> in most shots, so its conditional difference reads
the excitation one previous end state leaves through the terminal reset, the repetition delay and the service's
initialization, scaled by the readout contrast.

T1 series. The analysis corrects the t1 rows through the ro0 and t1-0 brackets and fits y_k = q (1 - e_k) - e_k with
e_k = exp(-t_k / T1). This section fits four nuisance models per informative qubit with inverse binomial-variance
weights on the delays after the bracket: T1 and q free; calibrated T1 with q free; T1 free with q = 1 (decay to the
ground state); calibrated T1 with q = 1. It reports chi-square, degrees of freedom and p-value for each, and the free
fits on each quarter of the shot index, which execution order maps onto quarters of the job's time.

``--out FILE`` writes the result; ``--check FILE`` recomputes it and requires the retained bytes. No result here is a
preregistered verdict of the envelope case.
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
from scipy.optimize import minimize_scalar
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import measurement_sequence_analysis as msa  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "msq-envelope-raw-diagnostics-v1"
RESULT_METADATA = "result_metadata.json"
EXPLORATORY = ROOT / "docs/evidence/measurement_sequence/envelope-run-exploratory.json"
# Lags of the adjacency section: (rows back, shot offset). (1, 0) is the predecessor under column-wise order.
LAGS = ((1, 0), (2, 0), (5, 0), (1, -1), (1, 1))
QUARTERS = 4
# A conditional difference needs this many shots on each side of the conditioning bit to enter a summary.
MIN_SIDE = 50
LARGE_Z = 3.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def final_bits(item: tuple[Path, str, str, list[str]]) -> list[bytes]:
    """The shot-ordered final bits of one PUB, one bytes string per layout qubit, after the file's digest check."""
    path, digest, name, registers = item
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"{path}: sha256 differs from index.json")
    pub = json.loads(data)
    require(pub["pub_name"] == name, f"{path}: PUB {pub['pub_name']} where the record names {name}")
    out = []
    for register in registers:
        entry = pub["registers"][register]
        require(entry["num_bits"] == 1, f"{path}: {register} holds {entry['num_bits']} bits")
        out.append("".join(entry["bitstrings"]).encode())
    return out


def load(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    (raw,) = sorted((run / "raw").iterdir())
    index = json.loads((raw / "index.json").read_text())
    metadata = (raw / RESULT_METADATA).read_bytes()
    require(hashlib.sha256(metadata).hexdigest() == index["files"][RESULT_METADATA], f"{raw}: metadata sha256 differs")
    chunks = json.loads(metadata)["executor"]["chunk_timing"]
    pubs = record["execution_pubs"]
    items = []
    for k, pub in enumerate(pubs):
        registers = []
        for component in pub["components"]:
            (replica,) = component["registers_by_replica"]
            finals = [r for r in replica if r.endswith("_final")]
            require(len(finals) == 1, f"{pub['name']}: {component['member']} has no single final register")
            registers.append(finals[0])
        name = f"pub_{k:02d}.json"
        items.append((raw / name, index["files"][name], pub["name"], registers))
    columns = ordered_map(final_bits, items, min_items=2)
    bits = np.array([[np.frombuffer(b, dtype=np.uint8) - ord("0") for b in row] for row in columns], dtype=np.int8)
    require(bool(np.all((bits == 0) | (bits == 1))), f"{raw}: a final bit is neither 0 nor 1")
    qubits = [int(component["physical_qubits"][0]) for component in pubs[0]["components"]]
    for pub in pubs:
        require(
            [int(c["physical_qubits"][0]) for c in pub["components"]] == qubits, f"{pub['name']}: layout order differs"
        )
    return {
        "record": record,
        "bits": bits,
        "members": [msa_class(pub["components"][0]["member"]) for pub in pubs],
        "qubits": qubits,
        "chunks": [[part["idx_item"] for part in chunk["parts"]] for chunk in chunks],
        "job_id": index["job_id"],
    }


def msa_class(member: str) -> str:
    """The member name without its qubit suffix, which names the row on every qubit."""
    head, _, tail = member.rpartition("_q")
    require(tail.isdigit(), f"{member}: no qubit suffix")
    return head


def conditional(current: np.ndarray, previous: np.ndarray) -> tuple[float, float] | None:
    """P(current = 1 | previous = 1) - P(current = 1 | previous = 0) and its binomial standard error.

    Each side's variance is at least that of one count in its shots, so a side that reads all zeros or all ones on a
    row near P1 = 0 or 1 cannot drive the standard error to zero.
    """
    ones, zeros = current[previous == 1], current[previous == 0]
    if ones.size < MIN_SIDE or zeros.size < MIN_SIDE:
        return None
    p1, p0 = float(ones.mean()), float(zeros.mean())
    se = math.sqrt(max(p1 * (1 - p1), 1.0 / ones.size) / ones.size + max(p0 * (1 - p0), 1.0 / zeros.size) / zeros.size)
    return p1 - p0, se


def lagged(bits: np.ndarray, k: int, g: int, back: int, offset: int) -> tuple[float, float] | None:
    current, previous = bits[k, g], bits[k - back, g]
    if offset > 0:
        current, previous = current[:-offset], previous[offset:]
    elif offset < 0:
        current, previous = current[-offset:], previous[:offset]
    return conditional(current, previous)


def adjacency(bits: np.ndarray, members: list[str]) -> dict[str, Any]:
    rows, groups = bits.shape[0], bits.shape[1]
    summaries = {}
    tables: dict[tuple[int, int], dict[int, list[float]]] = {}
    for back, offset in LAGS:
        cells = {}
        for k in range(back, rows):
            for g in range(groups):
                value = lagged(bits, k, g, back, offset)
                if value is not None:
                    cells[(k, g)] = value
        z = np.array([d / se for d, se in cells.values()])
        summaries[f"rows_back_{back}_shot_offset_{offset:+d}"] = {
            "cells": len(cells),
            "mean_z": float(z.mean()),
            "rms_z": float(math.sqrt(float((z * z).mean()))),
            "fraction_abs_z_above_3": float((np.abs(z) > LARGE_Z).mean()),
            "median_difference": float(np.median([d for d, _ in cells.values()])),
        }
        tables[(back, offset)] = {
            k: [cells[(k, g)][0] for g in range(groups) if (k, g) in cells] for k in range(back, rows)
        }
    per_row = []
    for k in range(1, rows):
        same, shifted = tables[(1, 0)][k], tables[(1, -1)][k]
        per_row.append(
            {
                "row": k,
                "member": members[k],
                "previous": members[k - 1],
                "p1": float(bits[k].mean()),
                "median_difference_same_shot": float(np.median(same)) if same else None,
                "median_difference_shot_minus_1": float(np.median(shifted)) if shifted else None,
            }
        )
    return {"lags": summaries, "per_row": per_row}


def carryover(bits: np.ndarray, members: list[str], qubits: list[int]) -> dict[str, Any]:
    (row,) = [k for k, m in enumerate(members) if m == "msq_ro0"]
    per_qubit = {}
    for g, qubit in enumerate(qubits):
        value = conditional(bits[row, g], bits[row - 1, g])
        if value is not None:
            per_qubit[str(qubit)] = {"difference": value[0], "se": value[1]}
    differences = [v["difference"] for v in per_qubit.values()]
    mean = float(np.mean(differences))
    se = math.sqrt(sum(v["se"] ** 2 for v in per_qubit.values())) / len(per_qubit)
    return {
        "row": row,
        "previous_member": members[row - 1],
        "previous_p1": float(bits[row - 1].mean()),
        "per_qubit": per_qubit,
        "median_difference": float(np.median(differences)),
        "mean_difference": mean,
        "mean_se": se,
    }


def series(ones: np.ndarray, shots: int) -> tuple[list[float], list[float]]:
    """The bracket-corrected t1 series and its standard errors from the ro0 and t1 rows' ones counts."""
    p = ones / shots
    z0, z1 = 1 - 2 * p[0], 1 - 2 * p[1]
    scale, offset = (z0 - z1) / 2, (z0 + z1) / 2
    y = [((1 - 2 * pk) - offset) / scale for pk in p[1:]]
    se = [2 * math.sqrt(max(pk * (1 - pk), 1.0 / shots) / shots) / abs(scale) for pk in p[1:]]
    return y, se


def fit(delays: list[float], y: list[float], se: list[float], t1: float | None, q: float | None) -> dict[str, Any]:
    """Weighted least squares of y_k = q (1 - e_k) - e_k over the delays after the bracket, T1 and q free or fixed."""
    t = np.array(delays[1:])
    ys = np.array(y[1:])
    w = 1 / np.array(se[1:]) ** 2

    def at(lifetime: float) -> tuple[float, float]:
        e = np.exp(-t / lifetime)
        plateau = q if q is not None else float(np.sum(w * (1 - e) * (ys + e)) / np.sum(w * (1 - e) ** 2))
        return plateau, float(np.sum(w * (ys + e - plateau * (1 - e)) ** 2))

    if t1 is None:
        best = minimize_scalar(
            lambda u: at(math.exp(u))[1],
            bounds=(math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1])),
            method="bounded",
            options={"xatol": 1e-10},
        )
        t1 = math.exp(float(best.x))
    plateau, statistic = at(t1)
    return {"t1_us": t1 * 1e6, "q": plateau, "chi2": statistic}


def t1_models(item: tuple[int, list[float], float, np.ndarray]) -> dict[str, Any]:
    qubit, delays, t1_cal, ones = item
    shots = ones.shape[1]
    y, se = series(ones.sum(axis=1), shots)
    models = {}
    for label, t1, q, free in (
        ("t1_free_q_free", None, None, 2),
        ("t1_calibrated_q_free", t1_cal, None, 1),
        ("t1_free_q_1", None, 1.0, 1),
        ("t1_calibrated_q_1", t1_cal, 1.0, 0),
    ):
        result = fit(delays, y, se, t1, q)
        dof = len(delays) - 1 - free
        models[label] = {**result, "dof": dof, "p_value": float(chi2.sf(result["chi2"], dof))}
    quarters = []
    for part in range(QUARTERS):
        window = ones[:, part * shots // QUARTERS : (part + 1) * shots // QUARTERS]
        qy, qse = series(window.sum(axis=1), window.shape[1])
        quarters.append(
            {"t1_free_q_free": fit(delays, qy, qse, None, None), "t1_free_q_1": fit(delays, qy, qse, None, 1.0)}
        )
    return {"qubit": qubit, "t1_calibrated_us": t1_cal * 1e6, "models": models, "quarters": quarters}


def t1_section(loaded: dict[str, Any], run: Path) -> dict[str, Any]:
    record, bits, members, qubits = loaded["record"], loaded["bits"], loaded["members"], loaded["qubits"]
    collected = json.loads((run / "collect.json").read_text())
    executed: dict[str, Any] = {}
    for entry in collected[1:]:
        executed.update(entry["executed"])
    contexts = msa.contexts_from_record(record, executed)
    uninformative = {int(q) for q in json.loads(EXPLORATORY.read_text())["analysis"]["device"]["uninformative_qubits"]}
    (ro0,) = [k for k, m in enumerate(members) if m == "msq_ro0"]
    rows = [ro0]
    for k in range(msa.T1_COUNT):
        (row,) = [i for i, m in enumerate(members) if m == msa_class(msa.t1_names(0)[k])]
        rows.append(row)
    items = [
        (q, list(contexts[q]["t1_delays_s"]), float(contexts[q]["t1_cal_s"]), bits[rows, g])
        for g, q in enumerate(qubits)
        if q not in uninformative
    ]
    fits = ordered_map(t1_models, items, min_items=2)
    admitted = {label: sum(1 for f in fits if f["models"][label]["p_value"] >= 0.01) for label in fits[0]["models"]}
    return {
        "delays_us": [d * 1e6 for d in items[0][1]],
        "uninformative": sorted(uninformative),
        "per_qubit": {str(f["qubit"]): f for f in fits},
        "admitted_at_p_0_01": admitted,
        "informative": len(fits),
    }


def run(path: Path) -> dict[str, Any]:
    loaded = load(path)
    bits, members, qubits = loaded["bits"], loaded["members"], loaded["qubits"]
    return {
        "schema": SCHEMA,
        "run": path.relative_to(ROOT).as_posix(),
        "job_id": loaded["job_id"],
        "rows": int(bits.shape[0]),
        "qubits": qubits,
        "shots": int(bits.shape[2]),
        "executor_chunks": loaded["chunks"],
        "adjacency": adjacency(bits, members),
        "carryover": carryover(bits, members, qubits),
        "t1_series": t1_section(loaded, path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    text = json.dumps(run(args.run.resolve()), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        return 0
    if args.check.read_text() != text:
        raise SystemExit(f"{args.check} differs from the recomputed diagnostics")
    print(f"{args.check}: reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
