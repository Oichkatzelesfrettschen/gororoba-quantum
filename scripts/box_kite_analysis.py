"""Preregistered analysis of box-kite runs on Tuna-17 and the Ry emulator, and its replay.

docs/notes/box_kites/experiment-program.md section 4(g) fixes the stages and
scripts/box_kite_cases.py writes their case directories; every threshold this
script applies comes from the `preregistered.thresholds` block of the run's
own cases.json. The standard library and the repository suffice, so CI
replays a retained analysis without the Quantum Inspire stack.

A run directory holds one submitted batch as qi_platform.py leaves it:
cases.json, the circuit files, submission.json, results.json and
raw/<file>.json (shot-ordered bit strings). load_batch() refuses a batch
whose cases.json differs from the retained case batch, whose circuit bytes
differ from their cases.json sha256, whose receipt names another cases.json,
whose jobs did not all complete with the manifest's shots (a failed Ry job
is data: it names the factor the emulator rejects), whose shot strings have
another width than the declared register, whose manifest states another bit
order than its backend's (Tuna and QX put qubit 0 at the rightmost
character, Ry at the leftmost), or, on Tuna-17, which lacks its readout-0 and
readout-1 pair. Those are integrity failures and raise SystemExit.

Per-batch sanity on the T0, T1, coherence and walk stages: readout-0 P1 at
most readout_0_p1_at_most and readout-1 P1 at least readout_1_p1_at_least
on every qubit a replica uses; raw P(selector = 0) of every bright or
reference replica (census P = 1) whose cz_depth is in bright_floor_cz_depths
at least bright_p_selector_zero_at_least;
every qubit the witness text leaves idle at P1 at most
idle_p1_above_readout_0_at_most above its own readout-0 P1, which a replica's
outcome moved onto an idle position by a reversed bit order violates. A
failed check records a stop for its stage; the estimators are still computed
and reported beside it.

Readout correction. Each replica is corrected with its own batch's pair:
e01 = P(read 1 | prepared 0) from readout-0, e10 = P(read 0 | prepared 1)
from readout-1, both of n0 and n1 shots, and

    Pc = (p - e10) / (1 - e01 - e10),    p = P(read 0) of n shots,

    Var Pc = [p(1 - p)/n + Pc^2 e01(1 - e01)/n0 + (1 - Pc)^2 e10(1 - e10)/n1] / (1 - e01 - e10)^2,

the delta method with the three binomial proportions independent (dPc/dp =
1/D, dPc/de01 = Pc/D, dPc/de10 = (Pc - 1)/D with D = 1 - e01 - e10). Replicas
in one circuit read different qubits and are taken as independent.

Estimators, exactly as preregistered:

- pre: raw P(1|0), P(1|1) and P(1|XX) per qubit with binomial errors; the
  fault precondition, the under-rotation or misassignment decision, the T0
  layout stop rule and the readout re-admission of each candidate.
- t0: C(n) = mean Pc(bright, n) - mean Pc(dark, n) per depth with its delta
  variance; the depth-1 bound C(1) + upper_bound_z SE against its floor;
  r = exp(slope) of the least-squares line of ln C(n) on n, weights
  C(n)^2 / Var C(n), and its percentile interval from a parametric bootstrap
  of every replica's selector count and each batch's readout counts.
- t1: D = Pc(y_sign -1) - Pc(y_sign +1) per pair, its class, the strut bias
  flag and the twist equality of each batch's edge and twist replicas; the
  pair-location allowance is the difference of the two pairs' depth-1 bright
  Pc in T0 runs analyzed in the same call, and stays undetermined when T0
  holds no such replica.
- coherence: P(d = 0 | a = 0) from the joint (a, d) counts corrected by the
  inverse of the tensor product of the two qubits' assignment matrices,
  <S_d | a = 0> = 2 P - 1, its standard error from a parametric bootstrap
  of the joint counts and the readout counts.
- walk: <Z_c> = 2 Pc(c = 0) - 1 with standard error 2 SE(Pc); the sign test
  against omega and the omit-last null test.
- ry_ladder: completion or failure per circuit and, for a completed one, the
  z of every expected outcome (qubit 0 leftmost) and the count of outcomes
  of probability 0; the gating factor's failure stops the smoke subset.
- ry_smoke: P(selector = 0) per replica, qubit 0 leftmost; a deterministic
  replica below the fraction floor of its ideal outcome stops the series.
- tuna_twins: each relabeled QX twin on the ideal emulator; a deterministic
  prediction (selector, control or the selector-0 conditional of a data
  qubit) admits no shot off it, a P = 1/2 prediction stays inside the z
  limit its manifest's falsifier states, and the double-X twin reads 0 on
  every qubit of every shot. Twin batches are judged one by one, so a
  record may hold only the twins of the stages that ran.

Bootstrap draws come from one seeded generator in a fixed order (batch,
readout qubit, replica), all drawn before the per-draw estimates run through
parallel.ordered_map, so a pooled run writes the bytes of a serial one.
Floats are written rounded to 12 decimals with sorted keys.

--analyze RUN_DIR... --out FILE writes the analysis; --replay FILE recomputes
it from the run directories it names and compares bytes; --analyze-self-test
synthesizes run directories in a temporary directory from ideal predictions,
a stated readout-error model and seeded shots, checks every verdict and
requires each integrity mutation to be refused for its own reason.

Usage: "$PYTHON" scripts/box_kite_analysis.py (--analyze RUN_DIR... --out FILE | --replay FILE | --analyze-self-test)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

CASES = ROOT / "results/quantum_inspire/cases"
SCHEMA = "box-kite-analysis-v1"
FAMILIES = {
    "tuna_pre": "box_kite_tuna_pre",
    "tuna_t0": "box_kite_tuna_t0",
    "tuna_t1": "box_kite_tuna_t1",
    "tuna_coherence": "box_kite_tuna_coherence",
    "tuna_walk": "box_kite_tuna_walk",
    "ry_ladder": "box_kite_ry_ladder",
    "ry_smoke": "box_kite_ry_smoke",
    "tuna_twins": "box_kite_tuna_twins_qx",
}
# Families whose batches each answer their own question; the others need every batch.
INDEPENDENT_BATCHES = ("tuna_twins",)
TWIN_Z_LIMIT = re.compile(r"\|z\| < ([0-9.]+)")
BIT_ORDER = {"tuna_17": "rightmost", "QXsinglenodesimulator": "rightmost", "Rydberg": "leftmost"}
SHARED_EXEMPT = {"batch", "stage", "group", "circuits"}
QUBIT_REF = re.compile(r"q\[(\d+)\]")
DECIMALS = 12

Batch = dict[str, Any]


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, DECIMALS) + 0.0
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    return value


def dump(analysis: dict[str, Any]) -> str:
    return json.dumps(rounded(analysis), indent=1, sort_keys=True) + "\n"


# ---------------------------------------------------------------- loading and integrity


def bit(shot: str, qubit: int, order: str) -> int:
    return int(shot[qubit] if order == "leftmost" else shot[len(shot) - 1 - qubit])


def zeros(shots: list[str], qubit: int, order: str) -> int:
    if order == "leftmost":
        return sum(s[qubit] == "0" for s in shots)
    return sum(s[len(s) - 1 - qubit] == "0" for s in shots)


def touched(text: str) -> set[int]:
    """Qubits a gate or per-qubit barrier of the circuit text names; the final register-wide lines name none."""
    used: set[int] = set()
    for line in text.splitlines():
        if line.startswith(("//", "version", "qubit[", "bit[")) or line in ("barrier q", "b = measure q"):
            continue
        used |= {int(q) for q in QUBIT_REF.findall(line)}
    return used


def relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        fail(f"{path} lies outside {base}; the analysis records run paths relative to it")


def load_batch(run: Path, base: Path, cases_root: Path = CASES) -> Batch:
    """One run directory, checked for integrity (module docstring); raises SystemExit on the first failure."""
    cases_bytes = (run / "cases.json").read_bytes()
    manifest = json.loads(cases_bytes)
    family = manifest.get("family")
    if family not in FAMILIES:
        fail(f"{run}: family {family!r} is not a box-kite Tuna-17 or Ry stage")
    retained = cases_root / FAMILIES[family] / manifest["batch"] / "cases.json"
    if not retained.exists() or retained.read_bytes() != cases_bytes:
        fail(f"{run}: cases.json differs from the retained case {retained.relative_to(cases_root.parent)}")
    order = BIT_ORDER.get(manifest["backend"])
    if order is None or order not in manifest["bit_order"]:
        fail(f"{run}: bit order {manifest['bit_order']!r} differs from the {manifest['backend']} convention ({order})")
    receipt = run / "submission.json"
    if receipt.exists() and json.loads(receipt.read_text(encoding="utf-8")).get("cases_sha256") != sha256(cases_bytes):
        fail(f"{run}: submission.json names another cases.json sha256")
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    jobs = {row["file"]: row for row in collected["jobs"]}
    texts: dict[str, str] = {}
    shots: dict[str, list[str]] = {}
    status: dict[str, dict[str, Any]] = {}
    ry = manifest["dialect"] == "ry"
    for row in manifest["circuits"]:
        file = row["file"]
        data = (run / file).read_bytes()
        if sha256(data) != row["sha256"]:
            fail(f"{run}/{file}: bytes differ from the cases.json sha256")
        texts[file] = data.decode()
        job = jobs.get(file)
        if job is None:
            fail(f"{run}: results.json holds no job for {file}")
        state = job["job"]["status"]
        status[file] = {"status": state, "message": job["job"].get("message", "")}
        if state != "completed":
            if not ry:
                fail(f"{run}/{file}: job {state}; every Tuna-17 job must complete before the batch is analyzed")
            continue
        done = sum(r["shots_done"] for r in job["results"])
        raw_path = run / "raw" / f"{file}.json"
        if not raw_path.exists():
            fail(f"{run}/{file}: completed job without raw shots")
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        if done != manifest["shots"] or len(raw) != manifest["shots"]:
            fail(f"{run}/{file}: {done} shots done and {len(raw)} raw shots against the manifest's {manifest['shots']}")
        width = row.get("nqubits", manifest["nqubits"])
        if any(len(s) != width for s in raw):
            fail(f"{run}/{file}: shot width differs from the declared register of {width}")
        shots[file] = raw
    if manifest["dialect"] == "tuna" and not {"readout-0.cq", "readout-1.cq"} <= shots.keys():
        fail(f"{run}: the Tuna-17 batch lacks its readout-0 and readout-1 shots")
    return {
        "run": relative(run, base),
        "manifest": manifest,
        "family": family,
        "batch": manifest["batch"],
        "order": order,
        "texts": texts,
        "shots": shots,
        "status": status,
    }


def assignment(batch: Batch, qubit: int) -> dict[str, Any]:
    zero, one = batch["shots"]["readout-0.cq"], batch["shots"]["readout-1.cq"]
    k01 = len(zero) - zeros(zero, qubit, batch["order"])
    k10 = zeros(one, qubit, batch["order"])
    return {"e01": k01 / len(zero), "e10": k10 / len(one), "k01": k01, "k10": k10, "n0": len(zero), "n1": len(one)}


def corrected(k: int, n: int, e01: float, e10: float, n0: int, n1: int) -> tuple[float, float]:
    """Pc and its delta-method variance (module docstring) from k zeros of n and the batch's assignment."""
    p = k / n
    d = 1 - e01 - e10
    if d <= 0:
        return math.nan, math.nan
    pc = (p - e10) / d
    var = (p * (1 - p) / n + pc * pc * e01 * (1 - e01) / n0 + (1 - pc) ** 2 * e10 * (1 - e10) / n1) / (d * d)
    return pc, var


def selector_estimate(batch: Batch, file: str, qubit: int) -> dict[str, Any]:
    shots = batch["shots"][file]
    k = zeros(shots, qubit, batch["order"])
    a = assignment(batch, qubit)
    pc, var = corrected(k, len(shots), a["e01"], a["e10"], a["n0"], a["n1"])
    return {
        "qubit": qubit,
        "zeros": k,
        "shots": len(shots),
        "p_zero_raw": k / len(shots),
        "e01": a["e01"],
        "e10": a["e10"],
        "p_zero_corrected": pc,
        "se": math.sqrt(var) if var >= 0 else math.nan,
    }


def witness_row(batch: Batch) -> dict[str, Any]:
    return batch["manifest"]["circuits"][0]


def sanity(batch: Batch, thresholds: dict[str, Any]) -> list[str]:
    """Per-batch sanity problems of a T0, T1, coherence or walk batch (module docstring)."""
    problems = []
    row = witness_row(batch)
    order = batch["order"]
    used = sorted(
        {q for r in row["replicas"] for v in r["roles"].values() for q in (v if isinstance(v, list) else [v])}
    )
    zero, one = batch["shots"]["readout-0.cq"], batch["shots"]["readout-1.cq"]
    for q in used:
        p0 = 1 - zeros(zero, q, order) / len(zero)
        p1 = 1 - zeros(one, q, order) / len(one)
        if p0 > thresholds["readout_0_p1_at_most"]:
            problems.append(f"readout-0 q{q} P1 {p0:.3f} above {thresholds['readout_0_p1_at_most']}")
        if p1 < thresholds["readout_1_p1_at_least"]:
            problems.append(f"readout-1 q{q} P1 {p1:.3f} below {thresholds['readout_1_p1_at_least']}")
    shots = batch["shots"][row["file"]]
    for replica in row["replicas"]:
        if replica.get("p_selector_zero") == "1" and replica.get("cz_depth") in thresholds["bright_floor_cz_depths"]:
            q = replica["roles"]["selector"]
            p = zeros(shots, q, order) / len(shots)
            if p < thresholds["bright_p_selector_zero_at_least"]:
                problems.append(
                    f"slot {replica['slot']} bright selector q{q} raw P(0) {p:.3f} below "
                    f"{thresholds['bright_p_selector_zero_at_least']}"
                )
    idle = sorted(set(range(batch["manifest"]["nqubits"])) - touched(batch["texts"][row["file"]]))
    for q in idle:
        base = 1 - zeros(zero, q, order) / len(zero)
        p = 1 - zeros(shots, q, order) / len(shots)
        if p > base + thresholds["idle_p1_above_readout_0_at_most"]:
            problems.append(
                f"idle q{q} P1 {p:.3f} exceeds its readout-0 P1 {base:.3f} by more than "
                f"{thresholds['idle_p1_above_readout_0_at_most']} (bit-order conformance)"
            )
    return problems


# ---------------------------------------------------------------- bootstrap


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    position = pct / 100 * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def wls_slope(xs: list[float], ys: list[float], ws: list[float]) -> float:
    total = sum(ws)
    xbar = sum(w * x for w, x in zip(ws, xs, strict=True)) / total
    ybar = sum(w * y for w, y in zip(ws, ys, strict=True)) / total
    num = sum(w * (x - xbar) * (y - ybar) for w, x, y in zip(ws, xs, ys, strict=True))
    den = sum(w * (x - xbar) ** 2 for w, x in zip(ws, xs, strict=True))
    return num / den


class ContrastFit:
    """Per-draw r of T0: draws hold each readout pair's counts, then each replica's selector zeros."""

    def __init__(self, layout: list[dict[str, Any]], depths: list[int], weights: list[float], qubits: list[Any]):
        self.layout, self.depths, self.weights, self.qubits = layout, depths, weights, qubits

    def __call__(self, draw: tuple[int, ...]) -> float | None:
        position = 0
        readout: dict[tuple[str, int], tuple[float, float]] = {}
        for batch, q, n0, n1 in self.qubits:
            readout[(batch, q)] = (draw[position] / n0, draw[position + 1] / n1)
            position += 2
        pcs: dict[int, dict[str, list[float]]] = {d: {"bright": [], "dark": []} for d in self.depths}
        for replica in self.layout:
            e01, e10 = readout[(replica["batch"], replica["qubit"])]
            d = 1 - e01 - e10
            if d <= 0:
                return None
            pcs[replica["depth"]][replica["role"]].append((draw[position] / replica["shots"] - e10) / d)
            position += 1
        contrasts = [statistics.fmean(pcs[n]["bright"]) - statistics.fmean(pcs[n]["dark"]) for n in self.depths]
        if min(contrasts) <= 0:
            return None
        return math.exp(wls_slope([float(n) for n in self.depths], [math.log(c) for c in contrasts], self.weights))


def matrix_inverse_2(e01: float, e10: float) -> list[list[float]] | None:
    """Inverse of the assignment matrix [[1 - e01, e10], [e01, 1 - e10]] (rows read, columns prepared)."""
    det = (1 - e01) * (1 - e10) - e10 * e01
    if det <= 0:
        return None
    return [[(1 - e10) / det, -e10 / det], [-e01 / det, (1 - e01) / det]]


def conditional_zero(counts: list[int], a: tuple[float, float], d: tuple[float, float]) -> float | None:
    """P(d = 0 | a = 0) of the joint counts indexed 2 a + d, corrected by inv(A_a) x inv(A_d)."""
    inv_a, inv_d = matrix_inverse_2(*a), matrix_inverse_2(*d)
    if inv_a is None or inv_d is None:
        return None
    total = sum(counts)
    observed = [c / total for c in counts]
    true = [
        sum(inv_a[ta][oa] * inv_d[td][od] * observed[2 * oa + od] for oa in (0, 1) for od in (0, 1))
        for ta in (0, 1)
        for td in (0, 1)
    ]
    branch = true[0] + true[1]
    return true[0] / branch if branch > 0 else None


class CoherenceDraw:
    """Per-draw corrected P(d = 0 | a = 0): draws hold e01, e10 of a, e01, e10 of d, then the four joint counts."""

    def __init__(self, n0: int, n1: int):
        self.n0, self.n1 = n0, n1

    def __call__(self, draw: tuple[int, ...]) -> float | None:
        a = (draw[0] / self.n0, draw[1] / self.n1)
        d = (draw[2] / self.n0, draw[3] / self.n1)
        return conditional_zero(list(draw[4:8]), a, d)


def multinomial(rng: random.Random, n: int, probs: list[float]) -> list[int]:
    out, left, mass = [], n, 1.0
    for p in probs[:-1]:
        k = rng.binomialvariate(left, min(1.0, max(0.0, p / mass))) if left > 0 and mass > 0 else 0
        out.append(k)
        left -= k
        mass -= p
    return [*out, left]


# ---------------------------------------------------------------- stages


def stage_batches(batches: list[Batch], family: str, cases_root: Path) -> tuple[dict[str, Batch], list[str]]:
    series = json.loads((cases_root / FAMILIES[family] / "cases.json").read_text(encoding="utf-8"))
    names = [b["batch"] for b in series["batches"]]
    present: dict[str, Batch] = {}
    shared = None
    for batch in batches:
        if batch["batch"] in present:
            fail(f"two runs of {family} {batch['batch']}: {present[batch['batch']]['run']} and {batch['run']}")
        fields = {k: v for k, v in batch["manifest"].items() if k not in SHARED_EXEMPT}
        if shared is not None and fields != shared:
            fail(f"{batch['run']}: its manifest differs from the other {family} batches")
        shared = fields
        present[batch["batch"]] = batch
    return dict(sorted(present.items())), [name for name in names if name not in present]


def thresholds_of(batches: dict[str, Batch]) -> dict[str, Any]:
    """The manifest's thresholds block; the twin manifests state their z limit in the falsifier text only."""
    prereg = next(iter(batches.values()))["manifest"]["preregistered"]
    if "thresholds" in prereg:
        return dict(prereg["thresholds"])
    match = TWIN_Z_LIMIT.search(prereg["falsifier"])
    if match is None:
        fail("the twin manifest's falsifier states no |z| limit")
    return {"deterministic_shots_off_at_most": 0, "z_limit": float(match[1])}


def sanity_block(batches: dict[str, Batch], thresholds: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    block, stops = {}, []
    for name, batch in batches.items():
        problems = sanity(batch, thresholds)
        block[name] = {"run": batch["run"], "sanity": "pass" if not problems else "fail", "problems": problems}
        if problems:
            stops.append(f"sanity stop at {name}: {problems[0]}")
    return block, stops


def analyze_pre(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    batch = batches["batch-00"]
    order = batch["order"]
    n = batch["manifest"]["nqubits"]
    xx_file = witness_row(batch)["file"]

    def p1(file: str) -> dict[str, dict[str, float]]:
        shots = batch["shots"][file]
        out = {}
        for q in range(n):
            p = 1 - zeros(shots, q, order) / len(shots)
            out[str(q)] = {"p1": p, "se": math.sqrt(p * (1 - p) / len(shots))}
        return out

    table = {"p1_given_0": p1("readout-0.cq"), "p1_given_1": p1("readout-1.cq"), "p1_after_xx": p1(xx_file)}
    fault = {q: table["p1_given_1"][q]["p1"] < v for q, v in t["fault_p1_given_1_below"].items()}
    precondition = "fault-present" if all(fault.values()) else "fault-recovered"
    decision = None
    if precondition == "fault-present":
        xx = {q: table["p1_after_xx"][q]["p1"] for q in t["fault_p1_given_1_below"]}
        if all(xx[q] > v for q, v in t["under_rotation_p1_xx_above"].items()):
            decision = "under-rotation"
        elif all(xx[q] < v for q, v in t["misassignment_p1_xx_below"].items()):
            decision = "misassignment"
        else:
            decision = "unresolved"

    def readout_ok(q: int) -> bool:
        return bool(
            table["p1_given_0"][str(q)]["p1"] <= t["readout_0_p1_at_most"]
            and table["p1_given_1"][str(q)]["p1"] >= t["readout_1_p1_at_least"]
        )

    layout = sorted(set(t["t0_lcu_qubits"]) | set(t["t0_walk_qubits"]))
    failing = [q for q in layout if not readout_ok(q)]
    readmission = {}
    for q, basis in t["readmission"].items():
        if not readout_ok(int(q)):
            readmission[q] = "excluded: readout outside the limits"
        elif "visibility" in basis:
            readmission[q] = "readout-admissible; the Ramsey visibility exclusion stands"
        else:
            readmission[q] = "readout-admissible"
    stops = [f"re-plan the layout before T0: q{failing} outside the readout limits"] if failing else []
    return {
        "batches": {"batch-00": {"run": batch["run"], "sanity": "pass", "problems": []}},
        "per_qubit": table,
        "fault": {q: bool(v) for q, v in fault.items()},
        "precondition": precondition,
        "decision": decision,
        "t0_layout": {"qubits": layout, "failing": failing},
        "readmission": readmission,
        "stops": stops,
    }


def analyze_t0(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    depths = list(t["depths"])
    replicas = []
    for name, batch in batches.items():
        row = witness_row(batch)
        for r in row["replicas"]:
            role = {"1": "bright", "0": "dark"}[r["p_selector_zero"]]
            est = selector_estimate(batch, row["file"], r["roles"]["selector"])
            replicas.append({"batch": name, "slot": r["slot"], "depth": r["cz_depth"], "role": role, **est})
    contrast = {}
    for n in depths:
        bright = [r for r in replicas if r["depth"] == n and r["role"] == "bright"]
        dark = [r for r in replicas if r["depth"] == n and r["role"] == "dark"]
        value = statistics.fmean(r["p_zero_corrected"] for r in bright) - statistics.fmean(
            r["p_zero_corrected"] for r in dark
        )
        var = sum(r["se"] ** 2 for r in bright) / len(bright) ** 2 + sum(r["se"] ** 2 for r in dark) / len(dark) ** 2
        contrast[str(n)] = {"value": value, "se": math.sqrt(var)}
    c1 = contrast[str(depths[0])]
    upper = c1["value"] + t["upper_bound_z"] * c1["se"]
    positive = all(contrast[str(n)]["value"] > 0 for n in depths)
    weights = [contrast[str(n)]["value"] ** 2 / contrast[str(n)]["se"] ** 2 for n in depths] if positive else []
    r_point = (
        math.exp(wls_slope([float(n) for n in depths], [math.log(contrast[str(n)]["value"]) for n in depths], weights))
        if positive
        else None
    )
    interval = None
    undefined = None
    if positive:
        rng = random.Random(t["bootstrap_seed"])
        qubits = []
        for name, batch in batches.items():
            for r in witness_row(batch)["replicas"]:
                a = assignment(batch, r["roles"]["selector"])
                qubits.append((name, r["roles"]["selector"], a["n0"], a["n1"], a["e01"], a["e10"]))
        layout = [{"batch": r["batch"], "qubit": r["qubit"], "depth": r["depth"], "role": r["role"],
                   "shots": r["shots"], "p": r["p_zero_raw"]} for r in replicas]  # fmt: skip
        draws = []
        for _ in range(t["bootstrap_draws"]):
            draw: list[int] = []
            for _, _, n0, n1, e01, e10 in qubits:
                draw += [rng.binomialvariate(n0, e01), rng.binomialvariate(n1, e10)]
            draw += [rng.binomialvariate(r["shots"], r["p"]) for r in layout]
            draws.append(tuple(draw))
        fit = ContrastFit(layout, depths, weights, [q[:4] for q in qubits])
        values = parallel.ordered_map(fit, draws)
        defined = [v for v in values if v is not None]
        undefined = len(values) - len(defined)
        low_pct, high_pct = t["interval_percentiles"]
        if undefined <= len(values) * low_pct / 100:
            interval = [percentile(defined, low_pct), percentile(defined, high_pct)]
    stops = []
    if upper < t["depth_1_contrast_upper_bound_floor"]:
        stops.append(
            f"end the Tuna-17 program: C(1) upper bound {upper:.4f} below {t['depth_1_contrast_upper_bound_floor']}"
        )
    low, high = t["r_planning_range"]
    if interval is None:
        r_verdict = "undetermined: a contrast is not positive in the point estimate or in too many draws"
    elif interval[1] < low or interval[0] > high:
        r_verdict = "outside the planning range"
        stops.append(f"resize T1, coherence and walk: r interval {interval} disjoint from {[low, high]}")
    else:
        r_verdict = "inside the planning range"
    return {
        "replicas": replicas,
        "contrast": contrast,
        "depth_1_upper_bound": upper,
        "c1_in_prediction": t["c1_prediction"][0] <= c1["value"] <= t["c1_prediction"][1],
        "r": r_point,
        "r_interval": interval,
        "r_undefined_draws": undefined,
        "r_verdict": r_verdict,
        "stops": stops,
    }


CLASSES = {"edge_same": "same-sign", "edge_opposite": "opposite-sign", "strut": "strut"}


def analyze_t1(batches: dict[str, Batch], t: dict[str, Any], t0: dict[str, Any] | None) -> dict[str, Any]:
    by_pair: dict[int, dict[int, dict[str, Any]]] = {}
    rows = []
    for name, batch in batches.items():
        row = witness_row(batch)
        for r in row["replicas"]:
            est = selector_estimate(batch, row["file"], r["roles"]["selector"])
            record = {"batch": name, "slot": r["slot"], "relation": r["relation"], "y_sign": r["q"][2],
                      "census": r["census"], "data": r["roles"]["data"][0], **est}  # fmt: skip
            rows.append(record)
            by_pair.setdefault(r["roles"]["selector"], {})[r["q"][2]] = record
    classification = {}
    stops = []
    for selector, signs in sorted(by_pair.items()):
        minus, plus = signs[-1], signs[1]
        d = minus["p_zero_corrected"] - plus["p_zero_corrected"]
        se = math.sqrt(minus["se"] ** 2 + plus["se"] ** 2)
        if d > t["same_sign_above"]:
            found = "same-sign"
        elif d < t["opposite_sign_below"]:
            found = "opposite-sign"
        elif abs(d) < t["strut_abs_below"]:
            found = "strut"
        else:
            found = "unresolved"
        expected = CLASSES[plus["relation"]]
        entry = {"pair": [selector, plus["data"]], "relation": plus["relation"], "D": d, "se": se,
                 "class": found, "expected": expected,
                 "verdict": "classified" if found == expected else "refuted"}  # fmt: skip
        if expected == "strut":
            entry["bias_flag"] = abs(d) > t["null_offset"] + t["sigma"] * se
        if found != expected:
            stops.append(f"pair {entry['pair']}: D {d:.4f} reads {found}, census {expected}")
        classification[str(selector)] = entry
    allowance = None
    reason = "T0 runs were not analyzed with T1"
    edge_pair = next(s for s, v in by_pair.items() if v[1]["relation"] == "edge_opposite")
    twist_pair = next(s for s, v in by_pair.items() if v[1]["relation"] == "edge_same")
    if t0 is not None:
        bright1 = {
            r["qubit"]: r["p_zero_corrected"] for r in t0["replicas"] if r["depth"] == 1 and r["role"] == "bright"
        }
        missing = [q for q in (edge_pair, twist_pair) if q not in bright1]
        if missing:
            reason = f"T0 holds no depth-1 bright replica on selector q{missing}"
        else:
            allowance = abs(bright1[edge_pair] - bright1[twist_pair])
    twist = {}
    for name in batches:
        edge = next(r for r in rows if r["batch"] == name and r["relation"] == "edge_opposite")
        tw = next(r for r in rows if r["batch"] == name and r["relation"] == "edge_same")
        diff = edge["p_zero_corrected"] - tw["p_zero_corrected"]
        se = math.sqrt(edge["se"] ** 2 + tw["se"] ** 2)
        if allowance is None:
            verdict = f"undetermined: {reason}"
        else:
            verdict = "refuted" if abs(diff) > t["sigma"] * se + allowance else "consistent"
        twist[name] = {"edge_y_sign": edge["y_sign"], "twist_y_sign": tw["y_sign"], "difference": diff, "se": se,
                       "z": diff / se if se > 0 else None, "allowance": allowance, "verdict": verdict}  # fmt: skip
        if verdict == "refuted":
            stops.append(f"{name}: twist equality refuted")
    return {"replicas": rows, "classification": classification, "twist_equality": twist, "stops": stops}


def analyze_coherence(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(t["bootstrap_seed"])
    items = []
    for name, batch in batches.items():
        row = witness_row(batch)
        shots = batch["shots"][row["file"]]
        for r in row["replicas"]:
            if r["kind"] != "coherence":
                continue
            a_q, d_q = r["roles"]["selector"], r["roles"]["data"][0]
            counts = [0, 0, 0, 0]
            for s in shots:
                counts[2 * bit(s, a_q, batch["order"]) + bit(s, d_q, batch["order"])] += 1
            ra, rd = assignment(batch, a_q), assignment(batch, d_q)
            items.append((name, r, counts, ra, rd))
    draws: list[list[tuple[int, ...]]] = []
    for _, _, counts, ra, rd in items:
        total = sum(counts)
        block = []
        for _ in range(t["bootstrap_draws"]):
            block.append(
                (
                    rng.binomialvariate(ra["n0"], ra["e01"]),
                    rng.binomialvariate(ra["n1"], ra["e10"]),
                    rng.binomialvariate(rd["n0"], rd["e01"]),
                    rng.binomialvariate(rd["n1"], rd["e10"]),
                    *multinomial(rng, total, [c / total for c in counts]),
                )
            )
        draws.append(block)
    rows, stops = [], []
    for (name, r, counts, ra, rd), block in zip(items, draws, strict=True):
        values = parallel.ordered_map(CoherenceDraw(ra["n0"], ra["n1"]), block)
        defined = [2 * v - 1 for v in values if v is not None]
        point = conditional_zero(counts, (ra["e01"], ra["e10"]), (rd["e01"], rd["e10"]))
        value = 2 * point - 1 if point is not None else None
        se = statistics.stdev(defined) if len(defined) > 1 else None
        prediction = fraction(r["expectation_given_selector_zero"])
        branch = counts[0] + counts[1]
        raw = 2 * counts[0] / branch - 1 if branch else None
        verdict = "reported: the falsifier names the X setting only"
        if r["setting"] == "X" and value is not None and se:
            z = value / se
            if prediction != 0:
                signed = z * math.copysign(1.0, prediction)
                verdict = "refuted" if signed < -t["sigma"] else "supported" if signed > t["sigma"] else "unresolved"
            else:
                verdict = "refuted" if abs(value) > t["null_offset"] + t["sigma"] * se else "consistent"
        if verdict == "refuted":
            stops.append(f"{name} slot {r['slot']} {r['relation']} <X_d> {value:.4f} refutes {prediction}")
        rows.append({"batch": name, "slot": r["slot"], "relation": r["relation"], "setting": r["setting"],
                     "pair": [r["roles"]["selector"], r["roles"]["data"][0]], "joint_counts": counts,
                     "expectation_raw": raw, "expectation_corrected": value, "se": se,
                     "z": value / se if value is not None and se else None, "prediction": prediction,
                     "undefined_draws": len(values) - len(defined), "verdict": verdict})  # fmt: skip
    return {"settings": rows, "stops": stops}


def analyze_walk(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    rows, stops = [], []
    for name, batch in batches.items():
        row = witness_row(batch)
        for r in row["replicas"]:
            if r["kind"] != "walk":
                continue
            est = selector_estimate(batch, row["file"], r["roles"]["control"])
            z_c = 2 * est["p_zero_corrected"] - 1
            se = 2 * est["se"]
            if r["omit_last_block"]:
                verdict = "refuted" if abs(z_c) > t["null_offset"] + t["sigma"] * se else "consistent"
            else:
                signed = z_c / se * r["omega"]
                verdict = "refuted" if signed < -t["sigma"] else "supported" if signed > t["sigma"] else "unresolved"
            if verdict == "refuted":
                stops.append(f"{name} walk {r['triple']} omit_last {r['omit_last_block']}: <Z_c> {z_c:.4f} refutes")
            rows.append({"batch": name, "triple": r["triple"], "omega": r["omega"], "omit_last_block":
                         r["omit_last_block"], "control": est, "z_c": z_c, "se": se,
                         "z": z_c / se if se > 0 else None, "verdict": verdict})  # fmt: skip
    return {"walks": rows, "stops": stops}


def binomial_z(k: int, n: int, p: float) -> float | None:
    return (k - n * p) / math.sqrt(n * p * (1 - p)) if 0 < p < 1 else None


def fraction(text: str) -> float:
    num, _, den = text.partition("/")
    return float(num) / float(den or 1)


def analyze_ry_ladder(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    rows, stops = [], []
    for name, batch in batches.items():
        for row in batch["manifest"]["circuits"]:
            state = batch["status"][row["file"]]
            entry: dict[str, Any] = {"batch": name, "file": row["file"], "ladder": row["ladder"], **state}
            if state["status"] == "completed":
                shots = batch["shots"][row["file"]]
                counts: dict[str, int] = {}
                for s in shots:
                    counts[s] = counts.get(s, 0) + 1
                expected = row["expected_leftmost"]
                entry["stray"] = sum(c for key, c in counts.items() if key not in expected)
                entry["outcomes"] = {
                    key: {"count": counts.get(key, 0), "z": binomial_z(counts.get(key, 0), len(shots), fraction(p))}
                    for key, p in expected.items()
                }
                inside = all(o["z"] is None or abs(o["z"]) < t["z_limit"] for o in entry["outcomes"].values())
                entry["verdict"] = "conforms" if inside and not entry["stray"] else "emulator rate"
            else:
                entry["verdict"] = f"failed: names factor {row['ladder']}"
                if row["ladder"] == t["gating_factor"]:
                    stops.append(f"{row['ladder']} failed: the Ry smoke subset is stopped")
            rows.append(entry)
    return {"circuits": rows, "stops": stops}


def analyze_ry_smoke(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    rows, stops = [], []
    for name, batch in batches.items():
        for row in batch["manifest"]["circuits"]:
            state = batch["status"][row["file"]]
            if state["status"] != "completed":
                stops.append(f"{name}/{row['file']} {state['status']}: {state['message']}")
                continue
            shots = batch["shots"][row["file"]]
            for r in row["replicas"]:
                k = zeros(shots, r["roles"]["selector"], batch["order"])
                p = fraction(r["p_selector_zero"])
                entry: dict[str, Any] = {"batch": name, "file": row["file"], "slot": r["slot"],
                                         "pattern": r["pattern"], "prediction": r["p_selector_zero"], "zeros": k,
                                         "shots": len(shots), "p_zero": k / len(shots)}  # fmt: skip
                if p in (0.0, 1.0):
                    ideal = k / len(shots) if p == 1.0 else 1 - k / len(shots)
                    entry["ideal_fraction"] = ideal
                    entry["verdict"] = (
                        "conforms" if ideal >= t["deterministic_ideal_fraction_at_least"] else "emulator rate"
                    )
                    if entry["verdict"] != "conforms":
                        stops.append(f"{name}/{row['file']} slot {r['slot']}: ideal fraction {ideal:.4f}")
                else:
                    z = binomial_z(k, len(shots), p)
                    entry["z"] = z
                    entry["verdict"] = "conforms" if z is not None and abs(z) < t["z_limit"] else "emulator rate"
                rows.append(entry)
    return {"replicas": rows, "stops": stops}


def twin_checks(replica: dict[str, Any]) -> list[tuple[str, int, int | None, str]]:
    """(name, qubit, conditioning qubit or None, P(qubit = 0) prediction) of one twin replica."""
    roles = replica["roles"]
    if "p_control_zero" in replica:
        return [("p_control_zero", roles["control"], None, replica["p_control_zero"])]
    checks: list[tuple[str, int, int | None, str]] = [
        ("p_selector_zero", roles["selector"], None, replica["p_selector_zero"])
    ]
    if "p_data_zero_given_selector_zero" in replica:
        checks.append(
            ("p_data_zero_given_selector_zero", roles["data"][0], roles["selector"],
             replica["p_data_zero_given_selector_zero"])
        )  # fmt: skip
    return checks


def analyze_twins(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    """Each twin on the ideal QX emulator: a deterministic prediction admits no shot off it, P = 1/2 sits inside z."""
    rows, stops = [], []
    for name, batch in batches.items():
        order = batch["order"]
        for row in batch["manifest"]["circuits"]:
            shots = batch["shots"][row["file"]]
            if row.get("ideal_p1") == "0":
                off = sum("1" in s for s in shots)
                verdict = "pass" if off <= t["deterministic_shots_off_at_most"] else "refuted"
                rows.append({"batch": name, "file": row["file"], "check": "all qubits 0", "shots": len(shots),
                             "off": off, "verdict": verdict})  # fmt: skip
                if verdict == "refuted":
                    stops.append(f"{name}/{row['file']}: {off} shots read a 1")
                continue
            for replica in row["replicas"]:
                for check_name, qubit, given, want in twin_checks(replica):
                    kept = [s for s in shots if given is None or bit(s, given, order) == 0]
                    k = zeros(kept, qubit, order)
                    p = fraction(want)
                    entry: dict[str, Any] = {"batch": name, "file": row["file"], "slot": replica["slot"],
                                             "check": check_name, "prediction": want, "zeros": k,
                                             "shots": len(kept)}  # fmt: skip
                    if p in (0.0, 1.0):
                        entry["off"] = len(kept) - k if p == 1.0 else k
                        refuted = entry["off"] > t["deterministic_shots_off_at_most"]
                    else:
                        entry["z"] = binomial_z(k, len(kept), p) if kept else None
                        refuted = entry["z"] is None or abs(entry["z"]) >= t["z_limit"]
                    entry["verdict"] = "refuted" if refuted else "pass"
                    if refuted:
                        stops.append(f"{name}/{row['file']} slot {replica['slot']} {check_name} refuted")
                    rows.append(entry)
    return {"checks": rows, "stops": stops}


def analyze(runs: list[Path], base: Path = ROOT, cases_root: Path = CASES) -> dict[str, Any]:
    """The analysis of the given run directories, grouped by stage; run paths are recorded relative to base."""
    loaded = [load_batch(run, base, cases_root) for run in runs]
    stages: dict[str, Any] = {}
    families = [f for f in FAMILIES if any(b["family"] == f for b in loaded)]
    results: dict[str, Any] = {}
    for family in families:
        batches, missing = stage_batches([b for b in loaded if b["family"] == family], family, cases_root)
        t = thresholds_of(batches)
        out: dict[str, Any] = {"thresholds": t, "missing_batches": missing}
        sanity_stops: list[str] = []
        if family in ("tuna_t0", "tuna_t1", "tuna_coherence", "tuna_walk"):
            out["batches"], sanity_stops = sanity_block(batches, t)
        elif family != "tuna_pre":
            out["batches"] = {name: {"run": b["run"]} for name, b in batches.items()}
        if missing and family not in INDEPENDENT_BATCHES:
            estimates: dict[str, Any] = {"stops": []}
            out["verdict"] = f"incomplete: {', '.join(missing)} not analyzed"
        else:
            if family == "tuna_pre":
                estimates = analyze_pre(batches, t)
            elif family == "tuna_t0":
                estimates = analyze_t0(batches, t)
            elif family == "tuna_t1":
                estimates = analyze_t1(batches, t, results.get("tuna_t0"))
            elif family == "tuna_coherence":
                estimates = analyze_coherence(batches, t)
            elif family == "tuna_walk":
                estimates = analyze_walk(batches, t)
            elif family == "ry_ladder":
                estimates = analyze_ry_ladder(batches, t)
            elif family == "tuna_twins":
                estimates = analyze_twins(batches, t)
            else:
                estimates = analyze_ry_smoke(batches, t)
            results[family] = estimates
        stops = sanity_stops + estimates.pop("stops")
        out.update(estimates)
        out["stops"] = stops
        if "verdict" not in out:
            out["verdict"] = "stop" if stops else "continue"
        stages[family] = out
    return {
        "schema": SCHEMA,
        "runs": sorted(b["run"] for b in loaded),
        "stages": stages,
        "readout_correction": "Pc = (p - e10) / (1 - e01 - e10) with the batch's own readout pair; delta-method "
        "variance with the binomial variance of p, e01 and e10",
    }


def replay(record_path: Path, base: Path = ROOT, cases_root: Path = CASES) -> int:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    runs = [base / run for run in record["runs"]]
    if record_path.read_text(encoding="utf-8") != dump(analyze(runs, base, cases_root)):
        fail(f"{record_path} differs from its recomputation over {len(runs)} runs")
    return len(runs)


# ---------------------------------------------------------------- self-test

# Synthetic readout model: every qubit reads |0> as 1 with SYN_E01 and |1>
# as 0 with SYN_E10, independently per shot; a fault map overrides it per
# qubit and circuit.
SYN_E01 = 0.02
SYN_E10 = 0.06
SYN_VISIBILITY = 0.85


def column(rng: random.Random, n: int, p_one: float) -> list[str]:
    """n bits with exactly Binomial(n, p_one) ones at uniformly drawn positions."""
    ones = rng.binomialvariate(n, p_one)
    out = ["0"] * n
    for position in rng.sample(range(n), ones):
        out[position] = "1"
    return out


def read(rng: random.Random, true: list[str], e01: float, e10: float) -> list[str]:
    out = list(true)
    for position, value in enumerate(true):
        flip = e01 if value == "0" else e10
        if flip and rng.random() < flip:
            out[position] = "1" if value == "0" else "0"
    return out


def synthetic_shots(item: tuple[int, int, int, dict[int, Any], dict[int, tuple[float, float]]]) -> list[str]:
    """Pool worker: shots of one circuit from its seed, width, shot count, true model and readout model.

    model maps a qubit to its P(true 1), or a group key (a, d) to the four
    joint probabilities indexed 2 a + d; unnamed qubits stay in |0>.
    """
    seed, width, n, model, readout = item
    rng = random.Random(seed)
    columns = {q: ["0"] * n for q in range(width)}
    for key, value in sorted(model.items(), key=lambda kv: str(kv[0])):
        if isinstance(key, tuple):
            a, d = key
            for s in range(n):
                u, acc, outcome = rng.random(), 0.0, 3
                for index, p in enumerate(value):
                    acc += p
                    if u < acc:
                        outcome = index
                        break
                columns[a][s], columns[d][s] = str(outcome >> 1), str(outcome & 1)
        else:
            columns[key] = column(rng, n, value)
    for q in range(width):
        e01, e10 = readout.get(q, (SYN_E01, SYN_E10))
        columns[q] = read(rng, columns[q], e01, e10)
    order = list(range(width - 1, -1, -1))
    return ["".join(columns[q][s] for q in order) for s in range(n)]


def lcu_model(replica: dict[str, Any], contrast: float) -> dict[Any, Any]:
    p0 = fraction(replica["p_selector_zero"])
    return {replica["roles"]["selector"]: 1 - (0.5 + (p0 - 0.5) * contrast), replica["roles"]["data"][0]: 0.5}


def tuna_model(row: dict[str, Any], scenario: dict[str, Any]) -> dict[Any, Any]:
    visibility = scenario.get("visibility", SYN_VISIBILITY)
    model: dict[Any, Any] = {}
    for r in row["replicas"]:
        if r["kind"] == "walk":
            omega = -r["omega"] if scenario.get("walk_sign_flipped") else r["omega"]
            p0 = scenario.get("control_p0", 0.5) if r["omit_last_block"] else 0.5 + 0.5 * visibility * omega
            model[r["roles"]["control"]] = 1 - p0
            continue
        if r["kind"] == "coherence":
            pa0 = 0.5 + (fraction(r["p_selector_zero"]) - 0.5) * visibility
            pd0 = 0.5 + 0.5 * visibility * fraction(r["expectation_given_selector_zero"])
            if scenario.get("coherence_flipped") and r["setting"] == "X":
                pd0 = 1 - pd0
            model[(r["roles"]["selector"], r["roles"]["data"][0])] = [
                pa0 * pd0, pa0 * (1 - pd0), (1 - pa0) / 2, (1 - pa0) / 2]  # fmt: skip
            continue
        depth = r.get("cz_depth", 1)
        contrast = scenario.get("amplitude", visibility) * scenario.get("r", 1.0) ** depth
        model.update(lcu_model(r, contrast))
    return model


def write_run(root: Path, family: str, batch: str, shots: dict[str, list[str]], failed: dict[str, str]) -> Path:
    source = CASES / FAMILIES[family] / batch
    run = root / "results/quantum_inspire/runs" / f"synthetic-{family}-{batch}"
    (run / "raw").mkdir(parents=True)
    manifest = json.loads((source / "cases.json").read_text(encoding="utf-8"))
    for name in ["cases.json", *(row["file"] for row in manifest["circuits"])]:
        shutil.copyfile(source / name, run / name)
    jobs = []
    for index, row in enumerate(manifest["circuits"]):
        file = row["file"]
        state = "failed" if file in failed else "completed"
        results = [] if file in failed else [{"shots_requested": manifest["shots"], "shots_done": manifest["shots"]}]
        jobs.append({"file": file, "job": {"id": index, "status": state, "message": failed.get(file, "")},
                     "results": results, "logs": None})  # fmt: skip
        if file not in failed:
            (run / "raw" / f"{file}.json").write_text(json.dumps(shots[file]), encoding="utf-8")
    (run / "results.json").write_text(json.dumps({"schema": "qi-collection-v1", "jobs": jobs}), encoding="utf-8")
    receipt = {"cases_sha256": sha256((run / "cases.json").read_bytes())}
    (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    return run


def scenario_jobs(name: str, scenario: dict[str, Any], seed: int) -> list[tuple[str, str, str, Any, dict[str, str]]]:
    """(family, batch, file, synthetic_shots item or None, failures) per circuit of the scenario's stages."""
    jobs = []
    for family in scenario["families"]:
        series = json.loads((CASES / FAMILIES[family] / "cases.json").read_text(encoding="utf-8"))
        for entry in series["batches"]:
            manifest = json.loads((CASES / FAMILIES[family] / entry["batch"] / "cases.json").read_text("utf-8"))
            width, n = manifest["nqubits"], manifest["shots"]
            for row in manifest["circuits"]:
                seed += 1
                file = row["file"]
                failures = scenario.get("ry_failed", {}) if family.startswith("ry") else {}
                readout = dict(scenario.get("readout", {}))
                if family.startswith("ry"):
                    jobs.append((family, entry["batch"], file, ry_item(seed, manifest, row, scenario), failures))
                    continue
                if row["kind"] == "readout":
                    model = {q: float(row["prepared"]) for q in range(width)}
                    item = (seed, width, n, model, {**readout, **scenario.get(f"readout_{file}", {})})
                elif family == "tuna_pre" or row.get("ideal_p1") == "0":
                    model = {q: 0.0 for q in range(width)}
                    item = (seed, width, n, model, {**readout, **scenario.get("xx", {})})
                else:
                    item = (seed, width, n, tuna_model(row, scenario), readout)
                jobs.append((family, entry["batch"], file, item, failures))
    return jobs


def ry_item(seed: int, manifest: dict[str, Any], row: dict[str, Any], scenario: dict[str, Any]) -> Any:
    width = row.get("nqubits", manifest["nqubits"])
    if row["kind"] == "diagnostic":
        return ("ladder", seed, width, manifest["shots"], row["expected_leftmost"])
    model = {}
    for r in row["replicas"]:
        p0 = fraction(r["p_selector_zero"])
        if p0 in (0.0, 1.0):
            p0 = p0 * scenario.get("ry_fidelity", 1.0) + (1 - p0) * (1 - scenario.get("ry_fidelity", 1.0))
        model[r["roles"]["selector"]] = 1 - p0
    return ("smoke", seed, width, manifest["shots"], model)


def synthesize(item: Any) -> list[str]:
    """Pool worker: shots of one synthetic circuit (Tuna items from synthetic_shots, Ry items leftmost)."""
    if item[0] == "ladder":
        _, seed, width, n, expected = item
        rng = random.Random(seed)
        keys, weights = list(expected), [fraction(p) for p in expected.values()]
        return rng.choices(keys, weights, k=n)
    if item[0] == "smoke":
        _, seed, width, n, model = item
        shots = synthetic_shots((seed, width, n, model, {q: (0.0, 0.0) for q in range(width)}))
        return [s[::-1] for s in shots]
    return synthetic_shots(item)


def build(root: Path, name: str, scenario: dict[str, Any], seed: int) -> list[Path]:
    jobs = scenario_jobs(name, scenario, seed)
    shots = parallel.ordered_map(synthesize, [job[3] for job in jobs], min_items=1)
    grouped: dict[tuple[str, str], dict[str, list[str]]] = {}
    failures: dict[tuple[str, str], dict[str, str]] = {}
    for (family, batch, file, _, failed), values in zip(jobs, shots, strict=True):
        grouped.setdefault((family, batch), {})[file] = values
        failures[(family, batch)] = failed
    scenario_root = root / name
    return [
        write_run(scenario_root, family, batch, files, failures[(family, batch)])
        for (family, batch), files in grouped.items()
    ]


FAULT = {0: (0.04, 0.61), 6: (0.015, 0.86), 9: (0.27, 0.06)}
UNDER_ROTATION_XX = {0: (0.98, 0.98), 6: (0.52, 0.52)}
MISASSIGNMENT_XX = {0: (0.038, 0.038), 6: (0.013, 0.013)}
IDEAL_QX = {q: (0.0, 0.0) for q in range(10)}
HEALTHY = {0: (0.02, 0.06), 6: (0.02, 0.06), 9: (0.02, 0.06)}
SCENARIOS: dict[str, dict[str, Any]] = {
    "pass": {
        "families": [f for f in FAMILIES if f != "tuna_twins"], "readout": FAULT, "xx": UNDER_ROTATION_XX,
        "amplitude": 0.821, "r": 0.95,
        "ry_failed": {"r9-teleport-bare.cq": "Quantum backend error: error interpreting cQASM script"},
    },
    "twins": {"families": ["tuna_twins"], "readout": IDEAL_QX, "visibility": 1.0},
    "twins_refuted": {"families": ["tuna_twins"], "readout": IDEAL_QX, "visibility": 0.995},
    "t0_end": {"families": ["tuna_t0"], "readout": {}, "amplitude": 0.316, "r": 0.95},
    "t0_resize": {"families": ["tuna_t0"], "readout": {}, "amplitude": 0.975, "r": 0.80},
    "walk_refuted": {"families": ["tuna_walk"], "readout": {}, "control_p0": 0.8, "walk_sign_flipped": True},
    "coherence_refuted": {"families": ["tuna_coherence"], "readout": {}, "coherence_flipped": True},
    "pre_recovered": {"families": ["tuna_pre"], "readout": {**HEALTHY, 13: (0.02, 0.3)}, "xx": {}},
    "pre_misassignment": {"families": ["tuna_pre"], "readout": FAULT, "xx": MISASSIGNMENT_XX},
    "ry_stopped": {"families": ["ry_ladder", "ry_smoke"], "ry_fidelity": 0.85,
                   "ry_failed": {"r1-width-9.cq": "Quantum backend error: error interpreting cQASM script"}},
}  # fmt: skip


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def expect_exit(label: str, action: Any, reason: str) -> None:
    try:
        action()
    except SystemExit as error:
        if reason not in str(error):
            raise AssertionError(f"{label} was refused for another reason: {error}") from error
        return
    raise AssertionError(f"{label} was accepted")


def analyze_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="box-kite-analysis-") as scratch:
        root = Path(scratch)
        runs = {name: build(root, name, s, 1000 * n) for n, (name, s) in enumerate(SCENARIOS.items())}

        def stages(name: str) -> dict[str, Any]:
            return analyze(runs[name], root / name)["stages"]

        good = stages("pass")
        pre = good["tuna_pre"]
        check(pre["precondition"] == "fault-present" and pre["decision"] == "under-rotation", "pre under-rotation")
        check(pre["readmission"]["9"].startswith("excluded"), "q9 idle misassignment keeps q9 out")
        check(pre["readmission"]["5"].endswith("visibility exclusion stands"), "q5 keeps its visibility exclusion")
        check(pre["verdict"] == "continue", f"pre stops: {pre['stops']}")
        t0 = good["tuna_t0"]
        check(t0["verdict"] == "continue" and t0["r_verdict"] == "inside the planning range", f"t0: {t0['stops']}")
        check(t0["r_interval"][0] <= 0.95 <= t0["r_interval"][1], f"t0 r interval {t0['r_interval']} misses 0.95")
        check(t0["c1_in_prediction"], f"t0 C(1) {t0['contrast']['1']}")
        t1 = good["tuna_t1"]
        check(all(c["verdict"] == "classified" for c in t1["classification"].values()), "t1 classification")
        check(t1["verdict"] == "continue", f"t1 stops: {t1['stops']}")
        check(
            all(
                v["verdict"].startswith("undetermined: T0 holds no depth-1 bright")
                for v in t1["twist_equality"].values()
            ),
            "the T1 twist allowance needs a depth-1 bright replica on (1, 4), which T0 lacks",
        )
        coherence = good["tuna_coherence"]
        x_verdicts = sorted(s["verdict"] for s in coherence["settings"] if s["setting"] == "X")
        check(x_verdicts == ["consistent", "supported"], f"coherence X verdicts {x_verdicts}")
        walk = good["tuna_walk"]
        check(sorted(w["verdict"] for w in walk["walks"]) == ["consistent", "supported", "supported"], "walk verdicts")
        ladder = good["ry_ladder"]
        check([c["verdict"] for c in ladder["circuits"]][:2] == ["conforms", "conforms"], "ry ladder R1, R2")
        check(ladder["circuits"][2]["verdict"].startswith("failed") and ladder["verdict"] == "continue", "ry R9")
        check(good["ry_smoke"]["verdict"] == "continue", f"ry smoke: {good['ry_smoke']['stops']}")

        ended = stages("t0_end")["tuna_t0"]
        check(any(s.startswith("end the Tuna-17 program") for s in ended["stops"]), f"t0 end: {ended['stops']}")
        check(any(s.startswith("sanity stop") for s in ended["stops"]), "the bright floor stops a C(1) 0.3 batch")
        resized = stages("t0_resize")["tuna_t0"]
        check(resized["r_verdict"] == "outside the planning range", f"t0 resize: {resized['r_verdict']}")
        check(
            not any(s.startswith("sanity stop") for s in resized["stops"]),
            f"the bright floor reads depth 1 only, yet a low depth-9 bright replica stopped T0: {resized['stops']}",
        )
        refuted = stages("walk_refuted")["tuna_walk"]
        check([w["verdict"] for w in refuted["walks"]] == ["refuted", "refuted", "refuted"], "walk refutation")
        flipped = stages("coherence_refuted")["tuna_coherence"]
        check(any(s["verdict"] == "refuted" for s in flipped["settings"]), "coherence sign refutation")
        recovered = stages("pre_recovered")["tuna_pre"]
        check(recovered["precondition"] == "fault-recovered" and recovered["decision"] is None, "pre recovered")
        check(recovered["t0_layout"]["failing"] == [13] and recovered["verdict"] == "stop", "pre T0 layout stop")
        check(recovered["readmission"]["9"] == "readout-admissible", "a healthy q9 is readout-admissible")
        mis = stages("pre_misassignment")["tuna_pre"]
        check(mis["decision"] == "misassignment", f"pre misassignment: {mis['decision']}")
        twins = stages("twins")["tuna_twins"]
        check(twins["verdict"] == "continue" and twins["missing_batches"] == [], f"ideal twins: {twins['stops']}")
        check(
            any(c["check"] == "all qubits 0" and c["verdict"] == "pass" for c in twins["checks"]),
            "the double-X twin was not judged",
        )
        noisy = stages("twins_refuted")["tuna_twins"]
        check(
            noisy["verdict"] == "stop" and any("p_selector_zero refuted" in s for s in noisy["stops"]),
            "a twin replica off its deterministic prediction passed",
        )
        partial_twins = analyze(
            [r for r in runs["twins"] if r.name.endswith(("batch-00", "batch-04"))], root / "twins"
        )["stages"]["tuna_twins"]
        check(
            partial_twins["missing_batches"] == ["batch-01", "batch-02", "batch-03"]
            and partial_twins["verdict"] == "continue",
            "twin batches are judged one by one",
        )
        ry = stages("ry_stopped")
        check(ry["ry_ladder"]["verdict"] == "stop" and ry["ry_smoke"]["verdict"] == "stop", "ry stop rules")

        # Replay: an exact record reproduces; a changed byte does not.
        record = root / "analysis.json"
        record.write_text(dump(analyze(runs["pass"], root / "pass")), encoding="utf-8")
        check(replay(record, root / "pass") == len(runs["pass"]), "replay run count")
        # The bootstrap's pooled estimates equal the serial loop's.
        saved = os.environ.get("GOROROBA_WORKERS")
        os.environ["GOROROBA_WORKERS"] = "1"
        try:
            serial = dump(analyze(runs["pass"], root / "pass"))
        finally:
            if saved is None:
                del os.environ["GOROROBA_WORKERS"]
            else:
                os.environ["GOROROBA_WORKERS"] = saved
        check(serial == record.read_text(encoding="utf-8"), "a serial analysis differs from the pooled one")
        record.write_text(record.read_text(encoding="utf-8").replace('"continue"', '"stop"', 1), encoding="utf-8")
        expect_exit("an edited analysis", lambda: replay(record, root / "pass"), "differs from its recomputation")

        # Integrity mutations, each on a copy of one passing batch.
        mutations = 0
        source = next(r for r in runs["pass"] if r.name.endswith("tuna_t0-batch-00"))

        def mutated(edit: Any) -> Path:
            nonlocal mutations
            mutations += 1
            target = root / "mutations" / f"m{mutations}" / "results/quantum_inspire/runs" / source.name
            shutil.copytree(source, target)
            edit(target)
            return target

        def rewrite(path: Path, change: Any) -> None:
            path.write_text(json.dumps(change(json.loads(path.read_text(encoding="utf-8")))), encoding="utf-8")

        def mutation_root(run: Path) -> Path:
            return run.parents[3]

        cases = [
            ("a circuit digest mismatch", lambda r: (r / "t0-1.cq").write_text("version 3.0\n"), "sha256"),
            (
                "a wrong shot count",
                lambda r: rewrite(r / "raw/t0-1.cq.json", lambda s: s[:-1]),
                "raw shots against the manifest",
            ),
            (
                "a results.json shot count",
                lambda r: rewrite(
                    r / "results.json",
                    lambda c: {**c, "jobs": [{**j, "results": [{"shots_done": 1}]} for j in c["jobs"]]},
                ),
                "shots done",
            ),
            (
                "a missing readout circuit",
                lambda r: (r / "raw/readout-1.cq.json").unlink(),
                "completed job without raw shots",
            ),
            (
                "a receipt for another cases.json",
                lambda r: (r / "submission.json").write_text(json.dumps({"cases_sha256": "0" * 64})),
                "submission.json",
            ),
            (
                "a short shot string",
                lambda r: rewrite(r / "raw/readout-0.cq.json", lambda s: [x[1:] for x in s]),
                "shot width",
            ),
        ]
        for label, edit, reason in cases:
            run = mutated(edit)
            expect_exit(label, lambda r=run: load_batch(r, mutation_root(r)), reason)
        partial = [r for r in runs["pass"] if "tuna_t0" in r.name]
        expect_exit("two runs of one batch", lambda: analyze([*partial, partial[0]], root / "pass"), "two runs")
        mutations += 1

        # A run whose readout-1 job is absent from the record is refused.
        def drop_readout(r: Path) -> None:
            (r / "raw/readout-1.cq.json").unlink()
            rewrite(r / "results.json", lambda c: {**c, "jobs": [j for j in c["jobs"] if j["file"] != "readout-1.cq"]})

        run = mutated(drop_readout)
        expect_exit("a batch without its readout-1 job", lambda: load_batch(run, mutation_root(run)), "no job")

        # Sanity mutations record a stop instead of an error.
        def reverse(r: Path) -> None:
            for name in ("t0-1.cq", "readout-0.cq", "readout-1.cq"):
                rewrite(r / "raw" / f"{name}.json", lambda s: [x[::-1] for x in s])

        run = mutated(reverse)
        others = [r for r in runs["pass"] if "tuna_t0" in r.name and r != source]
        mirror = mutation_root(run)
        for other in others:
            shutil.copytree(other, mirror / "results/quantum_inspire/runs" / other.name)
        swapped = analyze([run, *(mirror / "results/quantum_inspire/runs" / o.name for o in others)], mirror)
        problems = swapped["stages"]["tuna_t0"]["batches"]["batch-00"]["problems"]
        check(any("bit-order conformance" in p for p in problems), f"a reversed bit order passed: {problems}")

        def bad_readout(r: Path) -> None:
            def edit(shots: list[str]) -> list[str]:
                return [s[:12] + "0" + s[13:] if n % 4 == 0 else s for n, s in enumerate(shots)]

            rewrite(r / "raw/readout-1.cq.json", edit)

        run = mutated(bad_readout)
        mirror = mutation_root(run)
        for other in others:
            shutil.copytree(other, mirror / "results/quantum_inspire/runs" / other.name)
        limited = analyze([run, *(mirror / "results/quantum_inspire/runs" / o.name for o in others)], mirror)
        problems = limited["stages"]["tuna_t0"]["batches"]["batch-00"]["problems"]
        check(any(p.startswith("readout-1 q4") for p in problems), f"a readout-1 outside the limits passed: {problems}")
        check(limited["stages"]["tuna_t0"]["verdict"] == "stop", "a readout failure leaves the stage running")
        mutations += 2
    print(
        f"box-kite analysis: {len(SCENARIOS)} synthetic scenarios give their preregistered verdicts and replay; "
        f"{mutations} run mutations rejected"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--replay", type=Path, metavar="FILE")
    mode.add_argument("--analyze-self-test", action="store_true")
    parser.add_argument("--out", type=Path, help="with --analyze: the analysis file")
    args = parser.parse_args()
    if args.analyze_self_test:
        analyze_self_test()
        return 0
    if args.replay:
        count = replay(args.replay)
        print(f"{args.replay}: {count} runs reproduce the analysis")
        return 0
    if args.out is None:
        parser.error("--analyze needs --out")
    text = dump(analyze(args.analyze))
    args.out.write_text(text, encoding="utf-8")
    print(f"box-kite analysis: {len(args.analyze)} runs -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
