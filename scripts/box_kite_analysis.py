"""Preregistered analysis of box-kite runs on Tuna-17 and the Ry emulator, and its replay.

docs/notes/box_kites/experiment-program.md section 4(g) fixes the stages and
scripts/box_kite_cases.py writes their case directories; every threshold this
script applies comes from the `preregistered.thresholds` block of the run's
own cases.json. The standard library, numpy and the repository suffice, so
CI replays a retained analysis without the Quantum Inspire stack.

A run directory holds one submitted batch as qi_platform.py leaves it:
cases.json, the circuit files, submission.json, results.json and
raw/<file>.json (shot-ordered bit strings). load_batch() refuses a batch
whose cases.json differs from the retained case batch, whose circuit bytes
differ from their cases.json sha256, whose submission.json receipt is
missing or names another cases.json, backend, shots, circuit set, circuit
digest, job id or batch job than cases.json and results.json (checked
before any shot is read), whose jobs did not all complete with the
manifest's shots (a failed Ry job is data: it names the factor the emulator
rejects; a cancelled or other non-completed job is refused), whose shot strings have
another width than the declared register or a character other than 0 and 1,
whose manifest states another bit order than its backend's (Tuna and QX put
qubit 0 at the rightmost character, Ry at the leftmost), or, on Tuna-17,
which lacks its readout-0 and readout-1 pair. A bracketed series
(readout_calibration "bracketed") carries that pair only in the batches its
manifest lists it in, never one circuit of it alone, and every job of it
names its finished_at. Those are integrity failures and raise SystemExit.

Per-batch sanity on the T0 stage: readout-0 P1 at
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
- follow: readout-0 and readout-1 bracket the series in batches 0, 3 and 6.
  Each bracket gives every qubit's e01 and e10; at a witness job they are
  interpolated linearly in job finish time between the two nearest
  brackets, e01 on the readout-0 and e10 on the readout-1 finish times, a
  job outside the bracket span taking the nearest bracket, with variance
  (1 - w)^2 Var_a + w^2 Var_b of the two brackets' binomial terms. Every
  bracket holds the readout limits on every qubit the layout uses, no used
  qubit's e01 or e10 moves more than bracket_drift_max between consecutive
  brackets, and at most bracket_span witness-only batches run without a
  bracket; each bracket difference is reported, and so is each replica's
  bracket systematic |Pc(bracket b) - Pc(bracket a)|. These bracket rules
  also judge an incomplete series. Per-batch sanity: each depth-1
  deterministic LCU replica within deterministic_floor_margin of its ideal
  raw P(selector = 0), each walk read in X (last block kept) with at least
  1 - deterministic_floor_margin of its shots on the ideal control outcome,
  each idle qubit of each witness at P1 at most
  idle_p1_above_readout_0_at_most above its interpolated readout-0 P1.
  Estimators, each with the interpolated readout: Pc of each selector;
  E_b = 2 P(d = 0 | a = b) - 1 of each populated branch from the joint
  (a, d) frequencies corrected by inv(A_a) x inv(A_d); D = Pc(y_sign -1) -
  Pc(y_sign +1) per row (edge, twist, strut) and pair at depth 1, the X and
  Y replicas averaged, against same_sign_above, opposite_sign_below and
  strut_abs_below; the crossover Delta per block and setting, refuted at
  |Delta| > sigma SE; the strut D per setting against null_offset + sigma
  SE; the X sign of each depth-1 edge and twist E_b at |z| > sigma, every
  strut |E_b| against null_offset + sigma SE, and the depth-1 |E_X| against
  t0_c1 within cross_prediction_band (reported); per pair, the bright edge
  at depths 1, 5 and 9 with its X and Y replicas paired by (label, pair,
  depth): conditional magnitude m(n), phase atan2(E_Y, -E_X), population
  Pc(n) (X and Y averaged), and unweighted least-squares slopes on n giving
  r_coh = exp(slope ln J) of the joint coherence J(n) = Pc(n) m(n), r_pop =
  exp(slope ln(2 Pc(n) - 1)), their ratio (1 under a global depolarizing
  channel, where both equal lambda^n) and the phase per CZ, each reported
  with its 99% interval; the phase is unwrapped along depth before its fit,
  which identifies a phase per CZ below pi / 4 in magnitude (adjacent depths
  lie four CZs apart); per walk, the sign of <X_c>
  against omega, each omit control against null_offset + sigma SE, <Y_c>,
  and the magnitude sqrt(<X_c>^2 + <Y_c>^2) against t0_r^n_CZ within
  cross_prediction_band and the phase atan2(<Y_c>, -<X_c>), both reported;
  the depth-5 and depth-9 bright edge populations against T0's bright
  replica on the same selector and depth, reported as drift. Standard
  errors and intervals come from one numpy parametric bootstrap
  (bootstrap_draws, bootstrap_seed): a draw redraws every bracket's readout
  counts once, so replicas reading one qubit share it, then each replica's
  joint or control counts; the point estimate runs through the same array
  code as a one-row sample. All draws come first, in that fixed order, and
  the per-row estimates then run in blocks through parallel.ordered_map. Stops halt or invalidate the series: sanity,
  bracket limits, drift, span and T0's carried gate. A refuted
  classification, twist equality, X sign, strut D, strut E_b, walk sign or
  omit control enters the separate refutations list and gives the stage the
  verdict "refuted" when no stop stands; it never stops the series.
- ladder: the follow series' brackets (batches 0, 3 and 6) on the LCU pair
  qubits, plus each context readout's P1 floor on the iso qubits, and the
  follow series' per-batch sanity on each Latin circuit's depth-1 replica and
  idle qubits. Per pair and Latin batch, from that batch alone: C(n) =
  2 Pc(n) - 1 and, in X, J(n) = Pc(n) |E_0(n)|, r_pop and r_coh from
  unweighted least-squares slopes of their logs on n, rho = r_coh / r_pop
  with its interval, decided per pair from the two X batches; in Y, the
  phase atan2(E_Y, -E_X) per depth with E_X from the preceding X batch. Per
  Latin job: the shot-record line scan of scripts/qi_shot_record_line.scan,
  each selector's lock-in amplitude and phase at the peak, the depth-9 over
  depth-1 amplitude margin against amplitude_sigmas standard errors, the
  phase resultant of the depth-5 and depth-9 selectors, the third-harmonic
  amplitude, and the readout-corrected contrast in line_phase_bins bins of
  the line's phase (bin 0 where the depth-9 selector's P1 peaks); a job
  without the line or without the margin is a refutation. Readout context
  per iso qubit: e10 from readout-1 against readout-iso-x in batches 0 and 6
  (neighbor context), e10 from readout-iso-hzh against readout-iso-x
  interpolated in time (preparation path), each against context_min and
  amplitude_sigmas binomial standard errors, and the e01 of each pair's
  other qubit beside its excited partner. The depth-1 X E_0 of each pair
  whose data qubit is an iso qubit is corrected twice, with the readout-1
  brackets and with brackets whose iso e10 comes from readout-iso-x (its
  own bootstrap stream). The depth-5 and depth-9 populations are compared
  with the retained follow analysis as drift.
- T0 gate: the follow series analyzed in the same call as T0 carries T0's
  end-program or resize stop first in its stops, with its estimates still
  computed; analyzed without T0 it records the gate as unverified.
  T0 reports r against its decision band (the falsifier's [0.87, 0.97]) and,
  separately, against its prediction (the predictions text's range, read
  from the manifest).
- ry_ladder: completion or failure per circuit and, for a completed one, the
  z of every expected outcome (qubit 0 leftmost) and the count of outcomes
  of probability 0; the gating factor's failure stops the smoke subset, and
  ry_smoke analyzed in the same call carries that stop (alone, it records
  the gate as unverified).
- ry_smoke: P(selector = 0) per replica, qubit 0 leftmost; a deterministic
  replica below the fraction floor of its ideal outcome, judged on the point
  estimate, stops the series. Every Ry fraction carries its count, shots,
  binomial standard error and Wilson 95% interval.
- tuna_twins: each relabeled QX twin on the ideal emulator; a deterministic
  prediction (selector, control or a selector-0 or selector-1 conditional of
  a data qubit) admits no shot off it, a P = 1/2 prediction stays inside the z
  limit its manifest's falsifier states, and the double-X twin reads 0 on
  every qubit of every shot. Twin batches are judged one by one, so a
  record may hold only the twins of the stages that ran.

T0's bootstrap draws come from one seeded generator in a fixed order (batch,
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
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, NoReturn

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_shot_record_line import scan  # noqa: E402

import parallel  # noqa: E402

CASES = ROOT / "results/quantum_inspire/cases"
# The receipt schema scripts/qi_platform.py submit writes.
SUBMISSION_SCHEMA = "qi-submission-v2"
SCHEMA = "box-kite-analysis-v1"
FAMILIES = {
    "tuna_pre": "box_kite_tuna_pre",
    "tuna_t0": "box_kite_tuna_t0",
    "tuna_follow": "box_kite_tuna_follow",
    "ry_ladder": "box_kite_ry_ladder",
    "ry_smoke": "box_kite_ry_smoke",
    "tuna_twins": "box_kite_tuna_twins_qx",
    "tuna_ladder": "box_kite_tuna_ladder",
    "tuna_ladder_twins": "box_kite_tuna_ladder_twins_qx",
}
# Stages that run only after T0; T0's stops carry into them when analyzed together.
T0_DEPENDENT = ("tuna_follow",)
# Families whose batches each answer their own question; the others need every batch.
INDEPENDENT_BATCHES = ("tuna_twins", "tuna_ladder_twins")
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


def bit_matrix(shots: list[str], width: int, order: str) -> np.ndarray | None:
    """Shots as an (n, width) array of 0 and 1 whose column q is qubit q; None when a character is neither."""
    try:
        data = np.frombuffer("".join(shots).encode("ascii"), dtype=np.uint8).reshape(len(shots), width) - 48
    except (UnicodeEncodeError, ValueError):
        return None
    if bool((data > 1).any()):
        return None
    return data if order == "leftmost" else data[:, ::-1]


def zeros(batch: Batch, file: str, qubit: int) -> int:
    return int(batch["bits"][file].shape[0] - batch["bits"][file][:, qubit].sum(dtype=np.int64))


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


def check_receipt(run: Path, manifest: dict[str, Any], cases_bytes: bytes, collected: dict[str, Any]) -> dict[str, Any]:
    """results.json's jobs by file, after binding them to the submission receipt that qi_platform.py submit writes.

    The receipt (schema qi-submission-v2) must name this cases.json by sha256,
    its backend, backend type and shots, exactly the manifest's circuit files
    with their sha256, and one job id per file; results.json must hold one
    job per file with that id and the receipt's batch_job as batch_job_id.
    """
    path = run / "submission.json"
    if not path.exists():
        fail(f"{run}: no submission.json receipt binds the run to its submitted batch")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("schema") != SUBMISSION_SCHEMA:
        fail(f"{run}: submission.json schema {receipt.get('schema')!r} is not {SUBMISSION_SCHEMA}")
    if receipt.get("cases_sha256") != sha256(cases_bytes):
        fail(f"{run}: submission.json names another cases.json sha256")
    if any(receipt.get(key) != manifest[key] for key in ("backend", "backend_type_id", "shots")):
        fail(f"{run}: submission.json backend, backend type or shots differ from cases.json")
    digests = {row["file"]: row["sha256"] for row in manifest["circuits"]}
    submitted = {row["file"]: row for row in receipt.get("jobs", [])}
    if len(submitted) != len(receipt.get("jobs", [])) or set(submitted) != set(digests):
        fail(f"{run}: submission.json jobs name other circuit files than cases.json")
    if any(row.get("sha256") != digests[file] for file, row in submitted.items()):
        fail(f"{run}: a submission.json circuit sha256 differs from cases.json")
    jobs = {row["file"]: row for row in collected["jobs"]}
    if len(jobs) != len(collected["jobs"]) or set(jobs) != set(digests):
        fail(f"{run}: results.json jobs name other circuit files than cases.json")
    for file, row in jobs.items():
        if row["job"]["id"] != submitted[file]["job"]:
            fail(
                f"{run}/{file}: results.json job id {row['job']['id']} differs from the receipt's "
                f"{submitted[file]['job']}"
            )
        if row["job"].get("batch_job_id") != receipt.get("batch_job"):
            fail(
                f"{run}/{file}: results.json batch job differs from the receipt's batch_job {receipt.get('batch_job')}"
            )
    return jobs


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
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    jobs = check_receipt(run, manifest, cases_bytes, collected)
    texts: dict[str, str] = {}
    shots: dict[str, list[str]] = {}
    bits: dict[str, np.ndarray] = {}
    finished: dict[str, str] = {}
    status: dict[str, dict[str, Any]] = {}
    ry = manifest["dialect"] == "ry"
    bracketed = manifest.get("readout_calibration") == "bracketed"
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
            if not ry or state != "failed":
                fail(
                    f"{run}/{file}: job {state}; only a completed job, or a failed Ry job naming the construct the "
                    "emulator rejects, enters the analysis"
                )
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
        matrix = bit_matrix(raw, width, order)
        if matrix is None:
            fail(f"{run}/{file}: a shot string holds a character other than 0 and 1")
        if bracketed:
            stamp = job["job"].get("finished_at")
            try:
                datetime.fromisoformat(stamp)
            except (TypeError, ValueError):
                fail(f"{run}/{file}: the bracketed series interpolates in job finish time; finished_at is {stamp!r}")
            finished[file] = stamp
        shots[file] = raw
        bits[file] = matrix
    readouts = {"readout-0.cq", "readout-1.cq"}
    listed = readouts & {row["file"] for row in manifest["circuits"]}
    if bracketed and listed not in (set(), readouts):
        fail(f"{run}: a readout bracket lists {sorted(listed)} without its pair")
    if manifest["dialect"] == "tuna" and not (listed if bracketed else readouts) <= shots.keys():
        fail(f"{run}: the Tuna-17 batch lacks its readout-0 and readout-1 shots")
    return {
        "run": relative(run, base),
        "manifest": manifest,
        "family": family,
        "batch": manifest["batch"],
        "order": order,
        "texts": texts,
        "shots": shots,
        "bits": bits,
        "finished": finished,
        "status": status,
    }


def assignment(batch: Batch, qubit: int) -> dict[str, Any]:
    n0, n1 = len(batch["shots"]["readout-0.cq"]), len(batch["shots"]["readout-1.cq"])
    k01 = n0 - zeros(batch, "readout-0.cq", qubit)
    k10 = zeros(batch, "readout-1.cq", qubit)
    return {"e01": k01 / n0, "e10": k10 / n1, "k01": k01, "k10": k10, "n0": n0, "n1": n1}


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
    k = zeros(batch, file, qubit)
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
    """Per-batch sanity problems of a T0 batch (module docstring)."""
    problems = []
    row = witness_row(batch)
    used = sorted(
        {q for r in row["replicas"] for v in r["roles"].values() for q in (v if isinstance(v, list) else [v])}
    )
    zero, one = batch["shots"]["readout-0.cq"], batch["shots"]["readout-1.cq"]
    for q in used:
        p0 = 1 - zeros(batch, "readout-0.cq", q) / len(zero)
        p1 = 1 - zeros(batch, "readout-1.cq", q) / len(one)
        if p0 > thresholds["readout_0_p1_at_most"]:
            problems.append(f"readout-0 q{q} P1 {p0:.3f} above {thresholds['readout_0_p1_at_most']}")
        if p1 < thresholds["readout_1_p1_at_least"]:
            problems.append(f"readout-1 q{q} P1 {p1:.3f} below {thresholds['readout_1_p1_at_least']}")
    shots = batch["shots"][row["file"]]
    for replica in row["replicas"]:
        if replica.get("p_selector_zero") == "1" and replica.get("cz_depth") in thresholds["bright_floor_cz_depths"]:
            q = replica["roles"]["selector"]
            p = zeros(batch, row["file"], q) / len(shots)
            if p < thresholds["bright_p_selector_zero_at_least"]:
                problems.append(
                    f"slot {replica['slot']} bright selector q{q} raw P(0) {p:.3f} below "
                    f"{thresholds['bright_p_selector_zero_at_least']}"
                )
    idle = sorted(set(range(batch["manifest"]["nqubits"])) - touched(batch["texts"][row["file"]]))
    for q in idle:
        base = 1 - zeros(batch, "readout-0.cq", q) / len(zero)
        p = 1 - zeros(batch, row["file"], q) / len(shots)
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
    n = batch["manifest"]["nqubits"]
    xx_file = witness_row(batch)["file"]

    def p1(file: str) -> dict[str, dict[str, float]]:
        shots = batch["shots"][file]
        out = {}
        for q in range(n):
            p = 1 - zeros(batch, file, q) / len(shots)
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


R_PREDICTION = re.compile(r"with r in \[([0-9.]+), ([0-9.]+)\]")


def r_prediction(text: str) -> list[float]:
    """The predicted range of r from the T0 manifest's predictions text, which carries it in prose only."""
    match = R_PREDICTION.search(text)
    if match is None:
        fail("the T0 manifest's predictions state no range of r")
    return [float(match[1]), float(match[2])]


def analyze_t0(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    predictions = next(iter(batches.values()))["manifest"]["preregistered"]["predictions"]
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
    band = f"[{low}, {high}]"
    resize = False
    if interval is None:
        r_verdict = "undetermined: a contrast is not positive in the point estimate or in too many draws"
    elif interval[1] < low or interval[0] > high:
        r_verdict = f"outside the decision band {band}"
        resize = True
        stops.append(f"resize the follow series: r interval {interval} disjoint from {band}")
    else:
        r_verdict = f"inside the decision band {band}"
    prediction = r_prediction(predictions)
    return {
        "gate": {"end_program": upper < t["depth_1_contrast_upper_bound_floor"], "resize": resize},
        "r_prediction": prediction,
        "r_in_prediction": r_point is not None and prediction[0] <= r_point <= prediction[1],
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
READOUT_FILES = ("readout-0.cq", "readout-1.cq")
Values = dict[str, Any]


def job_time(batch: Batch, file: str) -> float:
    return datetime.fromisoformat(batch["finished"][file]).timestamp()


def witness_rows(batch: Batch) -> list[dict[str, Any]]:
    return [row for row in batch["manifest"]["circuits"] if row["kind"] == "witness"]


def follow_used(batches: dict[str, Batch]) -> list[int]:
    """Every qubit the follow layout gives a role: both qubits of each LCU pair, each walk's control and data."""
    layout = next(iter(batches.values()))["manifest"]["layout"]
    used = {q for pair in layout["lcu_pairs"] for q in pair}
    used |= {q for walk in layout["walks"].values() for q in [walk["control"], *walk["data"]]}
    return sorted(used)


def follow_brackets(batches: dict[str, Batch]) -> list[dict[str, Any]]:
    """Readout brackets in batch order: per qubit k01 of n0 and k10 of n1, and each readout job's finish time."""
    out: list[dict[str, Any]] = []
    for name, batch in batches.items():
        if READOUT_FILES[0] not in batch["bits"]:
            continue
        zero, one = batch["bits"][READOUT_FILES[0]], batch["bits"][READOUT_FILES[1]]
        out.append({
            "batch": name, "time_e01": job_time(batch, READOUT_FILES[0]), "time_e10": job_time(batch, READOUT_FILES[1]),
            "k01": [int(v) for v in zero.sum(axis=0, dtype=np.int64)],
            "k10": [int(v) for v in (one == 0).sum(axis=0, dtype=np.int64)],
            "n0": int(zero.shape[0]), "n1": int(one.shape[0]),
        })  # fmt: skip
    for kind in ("time_e01", "time_e10"):
        times = [b[kind] for b in out]
        if any(later <= earlier for earlier, later in zip(times, times[1:], strict=False)):
            fail(f"the follow readout brackets {[b['batch'] for b in out]} did not finish in batch order")
    return out


def bracket_weight(t: float, times: list[float]) -> tuple[int, int, float]:
    """The two nearest brackets (a, b) and the weight w of b in (1 - w) e_a + w e_b; w clamps to [0, 1]."""
    if len(times) == 1:
        return 0, 0, 0.0
    k = 0
    while k < len(times) - 2 and t > times[k + 1]:
        k += 1
    return k, k + 1, min(1.0, max(0.0, (t - times[k]) / (times[k + 1] - times[k])))


def interpolated(brackets: list[dict[str, Any]], weights: dict[str, tuple[int, int, float]], q: int) -> dict[str, Any]:
    """e01 and e10 of qubit q at a job, with the variance (1 - w)^2 e_a(1 - e_a)/n_a + w^2 e_b(1 - e_b)/n_b."""
    out: dict[str, Any] = {}
    for kind, count, n in (("e01", "k01", "n0"), ("e10", "k10", "n1")):
        a, b, w = weights[kind]
        ea, eb = brackets[a][count][q] / brackets[a][n], brackets[b][count][q] / brackets[b][n]
        var = (1 - w) ** 2 * ea * (1 - ea) / brackets[a][n] + w**2 * eb * (1 - eb) / brackets[b][n]
        out |= {kind: (1 - w) * ea + w * eb, f"{kind}_se": math.sqrt(var), f"{kind}_brackets": [a, b, w]}
    return out


def bracket_block(
    batches: dict[str, Batch], t: dict[str, Any], used: list[int] | None = None
) -> tuple[dict[str, Any], list[str]]:
    """Each bracket's rates on the used qubits, their differences, readout limits, drift and bracket span."""
    brackets = follow_brackets(batches)
    used = follow_used(batches) if used is None else used
    problems = []
    rates: dict[str, list[dict[str, Any]]] = {str(q): [] for q in used}
    for b in brackets:
        for q in used:
            e01, e10 = b["k01"][q] / b["n0"], b["k10"][q] / b["n1"]
            rates[str(q)].append({"batch": b["batch"], "e01": e01, "e10": e10,
                                  "e01_se": math.sqrt(e01 * (1 - e01) / b["n0"]),
                                  "e10_se": math.sqrt(e10 * (1 - e10) / b["n1"])})  # fmt: skip
            if e01 > t["readout_0_p1_at_most"]:
                problems.append(f"{b['batch']} readout-0 q{q} P1 {e01:.3f} above {t['readout_0_p1_at_most']}")
            if 1 - e10 < t["readout_1_p1_at_least"]:
                problems.append(f"{b['batch']} readout-1 q{q} P1 {1 - e10:.3f} below {t['readout_1_p1_at_least']}")
    differences = []
    for a, b in zip(brackets, brackets[1:], strict=False):
        for q in used:
            d01 = b["k01"][q] / b["n0"] - a["k01"][q] / a["n0"]
            d10 = b["k10"][q] / b["n1"] - a["k10"][q] / a["n1"]
            differences.append({"from": a["batch"], "to": b["batch"], "qubit": q, "e01": d01, "e10": d10})
            if max(abs(d01), abs(d10)) > t["bracket_drift_max"]:
                problems.append(
                    f"q{q} moved e01 {d01:+.4f}, e10 {d10:+.4f} from {a['batch']} to {b['batch']}, beyond "
                    f"{t['bracket_drift_max']}"
                )
    names = list(batches)
    marks = [n for n, name in enumerate(names) if any(b["batch"] == name for b in brackets)]
    gaps = [later - earlier - 1 for earlier, later in zip([-1, *marks], [*marks, len(names)], strict=True)]
    if max(gaps) > t["bracket_span"]:
        problems.append(f"{max(gaps)} witness-only batches without a readout bracket, above {t['bracket_span']}")
    block = {"batches": [b["batch"] for b in brackets], "qubits": used, "rates": rates,
             "differences": differences, "problems": problems}  # fmt: skip
    return block, [f"bracket stop: {p}" for p in problems]


def follow_items(batches: dict[str, Batch], brackets: list[dict[str, Any]]) -> tuple[list[Any], list[Any]]:
    """LCU replicas with their joint (a, d) counts and walks with their control zeros, in batch, file, slot order."""
    times = {kind: [b[f"time_{kind}"] for b in brackets] for kind in ("e01", "e10")}
    lcu, walks = [], []
    for name, batch in batches.items():
        for row in witness_rows(batch):
            stamp = job_time(batch, row["file"])
            bits = batch["bits"][row["file"]]
            weights = {kind: bracket_weight(stamp, times[kind]) for kind in times}
            for r in row["replicas"]:
                place = {"batch": name, "file": row["file"], "weights": weights, "replica": r, "shots": bits.shape[0]}
                if r["kind"] == "walk":
                    walks.append({**place, "zeros": int((bits[:, r["roles"]["control"]] == 0).sum())})
                else:
                    a, d = r["roles"]["selector"], r["roles"]["data"][0]
                    joint = np.bincount(2 * bits[:, a].astype(np.int64) + bits[:, d], minlength=4)
                    lcu.append({**place, "joint": [int(v) for v in joint]})
    return lcu, walks


def follow_sample(brackets: list[Any], lcu: list[Any], walks: list[Any], rng: Any = None, draws: int = 1) -> Values:
    """Readout rates per bracket and replica frequencies: the observed values as one row, or parametric draws.

    The draw order is fixed: each bracket's e01 then e10 counts over all qubits, then each LCU replica's
    multinomial joint (a, d) counts, then each walk's binomial control zeros.
    """

    def rates(k: list[int], n: int) -> np.ndarray:
        p = np.asarray(k, dtype=float) / n
        return p[np.newaxis, :] if rng is None else rng.binomial(n, p, size=(draws, p.size)) / n

    e01, e10 = [], []
    for b in brackets:
        e01.append(rates(b["k01"], b["n0"]))
        e10.append(rates(b["k10"], b["n1"]))
    joint = []
    for item in lcu:
        p = np.asarray(item["joint"], dtype=float) / item["shots"]
        joint.append(p[np.newaxis, :] if rng is None else rng.multinomial(item["shots"], p, size=draws) / item["shots"])
    control = []
    for item in walks:
        p = item["zeros"] / item["shots"]
        control.append(np.array([p]) if rng is None else rng.binomial(item["shots"], p, size=draws) / item["shots"])
    return {"e01": e01, "e10": e10, "joint": joint, "control": control}


def rates_at(sample: Values, item: dict[str, Any], q: int, force: float | None = None) -> tuple[Any, Any]:
    """Qubit q's e01 and e10 at the item's job; an item's qubit_weights override its bracket weights for one qubit."""
    weights = item.get("qubit_weights", {}).get(q, item["weights"])
    out = []
    for kind in ("e01", "e10"):
        a, b, w = weights[kind]
        w = w if force is None else force
        out.append((1 - w) * sample[kind][a][:, q] + w * sample[kind][b][:, q])
    return out[0], out[1]


def corrected_zero(p: Any, e01: Any, e10: Any) -> Any:
    d = 1 - e01 - e10
    return np.where(d > 0, (p - e10) / np.where(d > 0, d, 1.0), np.nan)


def conditional_expectation(sample: Values, item: dict[str, Any], index: int, branch: int, force: Any = None) -> Any:
    """E_b = 2 P(d = 0 | a = b) - 1 of the joint frequencies corrected by inv(A_a) x inv(A_d), A = [[1 - e01, e10],
    [e01, 1 - e10]] (rows read, columns prepared)."""
    inverses = []
    for q in (item["replica"]["roles"]["selector"], item["replica"]["roles"]["data"][0]):
        e01, e10 = rates_at(sample, item, q, force)
        det = 1 - e01 - e10
        det = np.where(det > 0, det, np.nan)
        inverses.append([[(1 - e10) / det, -e10 / det], [-e01 / det, (1 - e01) / det]])
    inv_a, inv_d = inverses
    q = sample["joint"][index]
    true = [
        sum(inv_a[branch][oa] * inv_d[td][od] * q[:, 2 * oa + od] for oa in (0, 1) for od in (0, 1)) for td in (0, 1)
    ]
    total = true[0] + true[1]
    return np.where(total > 0, 2 * true[0] / np.where(total > 0, total, 1.0) - 1, np.nan)


def branches(replica: dict[str, Any]) -> list[int]:
    return [b for b, name in enumerate(("zero", "one")) if f"expectation_given_selector_{name}" in replica]


def follow_values(sample: Values, lcu: list[Any], walks: list[Any]) -> Values:
    """Per row of the sample: every LCU replica's Pc and populated-branch E_b, and every walk's 2 Pc(c = 0) - 1."""
    pc, expectation, walk = [], {}, []
    with np.errstate(all="ignore"):
        for index, item in enumerate(lcu):
            e01, e10 = rates_at(sample, item, item["replica"]["roles"]["selector"])
            pc.append(corrected_zero(sample["joint"][index][:, 0] + sample["joint"][index][:, 1], e01, e10))
            for b in branches(item["replica"]):
                expectation[(index, b)] = conditional_expectation(sample, item, index, b)
        for index, item in enumerate(walks):
            e01, e10 = rates_at(sample, item, item["replica"]["roles"]["control"])
            walk.append(2 * corrected_zero(sample["control"][index], e01, e10) - 1)
    return {"pc": pc, "e": expectation, "walk": walk}


# Bootstrap rows per block that parallel.ordered_map hands one worker.
FOLLOW_BLOCK_DRAWS = 250


class FollowValues:
    """follow_values on one block of sample rows, picklable for parallel.ordered_map."""

    def __init__(self, lcu: list[Any], walks: list[Any]):
        self.lcu, self.walks = lcu, walks

    def __call__(self, block: Values) -> Values:
        return follow_values(block, self.lcu, self.walks)


def sample_rows(sample: Values, start: int, stop: int) -> Values:
    return {kind: [array[start:stop] for array in arrays] for kind, arrays in sample.items()}


def pooled_follow_values(sample: Values, lcu: list[Any], walks: list[Any]) -> Values:
    """follow_values over the rows of a pre-drawn sample, mapped in FOLLOW_BLOCK_DRAWS blocks and concatenated.

    follow_values is elementwise in the rows (sums, products, quotients and selections), so every block returns the
    bits its rows have in one call over the whole sample, and the pooled result equals the serial one.
    """
    rows = len(sample["joint"][0]) if sample["joint"] else len(sample["control"][0])
    blocks = [sample_rows(sample, start, start + FOLLOW_BLOCK_DRAWS) for start in range(0, rows, FOLLOW_BLOCK_DRAWS)]
    parts = parallel.ordered_map(FollowValues(lcu, walks), blocks, min_items=1)
    return {
        "pc": [np.concatenate([part["pc"][i] for part in parts]) for i in range(len(parts[0]["pc"]))],
        "e": {key: np.concatenate([part["e"][key] for part in parts]) for key in parts[0]["e"]},
        "walk": [np.concatenate([part["walk"][i] for part in parts]) for i in range(len(parts[0]["walk"]))],
    }


def summary(point: Any, draws: Any, percentiles: list[float] | None = None) -> dict[str, Any]:
    """Point value, bootstrap standard deviation, undefined-draw count and, when asked, the percentile interval."""
    value = float(np.asarray(point).reshape(-1)[0])
    draws = np.asarray(draws, dtype=float)
    finite = draws[np.isfinite(draws)]
    undefined = int(draws.size - finite.size)
    out: dict[str, Any] = {
        "value": value if math.isfinite(value) else None,
        "se": float(np.std(finite, ddof=1)) if finite.size > 1 else None,
        "undefined_draws": undefined,
    }
    if percentiles is not None:
        low, high = percentiles
        enough = finite.size > 0 and undefined <= draws.size * low / 100
        out["interval"] = [float(np.percentile(finite, low)), float(np.percentile(finite, high))] if enough else None
    return out


def ols_slope(depths: list[int], values: list[Any]) -> Any:
    """Least-squares slope of values (one array per depth, each over the sample rows) on depth, per row."""
    x = np.asarray(depths, dtype=float)
    x = x - x.mean()
    stacked = np.stack(values, axis=-1)
    return (stacked - stacked.mean(axis=-1, keepdims=True)) @ x / (x @ x)


def signed_verdict(value: float | None, se: float | None, sign: float, sigma: float) -> str:
    if value is None or not se:
        return "undetermined"
    z = value / se * sign
    return "refuted" if z < -sigma else "supported" if z > sigma else "unresolved"


def analyze_follow(batches: dict[str, Batch], t: dict[str, Any], t0: dict[str, Any] | None) -> dict[str, Any]:
    """The follow series (module docstring): brackets, sanity, classification, twist, strut, coherence, ladder."""
    block, stops = bracket_block(batches, t)
    # Stops halt or invalidate the series; refutations are verdicts on the census predictions.
    refutations: list[str] = []
    brackets = follow_brackets(batches)
    lcu, walks = follow_items(batches, brackets)
    rng = np.random.default_rng(t["bootstrap_seed"])
    observed = follow_sample(brackets, lcu, walks)
    point = follow_values(observed, lcu, walks)
    boot = pooled_follow_values(follow_sample(brackets, lcu, walks, rng, t["bootstrap_draws"]), lcu, walks)
    pct = t["interval_percentiles"]
    sigma, null = t["sigma"], t["null_offset"]

    def both(fn: Any, percentiles: list[float] | None = None) -> dict[str, Any]:
        with np.errstate(all="ignore"):
            return summary(fn(point), fn(boot), percentiles)

    # Per-batch sanity on raw frequencies and the interpolated readout-0 P1.
    margin = t["deterministic_floor_margin"]
    times = [b["time_e01"] for b in brackets]
    batch_block: dict[str, Any] = {}
    for name, batch in batches.items():
        problems = []
        for row in witness_rows(batch):
            bits = batch["bits"][row["file"]]
            n = bits.shape[0]
            for r in row["replicas"]:
                if r["kind"] == "walk":
                    deterministic = r["readout"] == "X" and not r["omit_last_block"] and r["p_control_zero"] in "01"
                    if deterministic:
                        ideal = int(r["p_control_zero"] == "0")
                        p = int((bits[:, r["roles"]["control"]] == ideal).sum()) / n
                        if p < 1 - margin:
                            problems.append(f"{row['file']} walk {r['triple']} raw P(c = {ideal}) {p:.3f} below "
                                            f"{1 - margin:g}")  # fmt: skip
                elif r["cz_depth"] in t["bright_floor_cz_depths"] and r["p_selector_zero"] in ("0", "1"):
                    p = int((bits[:, r["roles"]["selector"]] == 0).sum()) / n
                    if abs(p - float(r["p_selector_zero"])) > margin:
                        problems.append(f"{row['file']} slot {r['slot']} {r['label']} raw P(a = 0) {p:.3f} beyond "
                                        f"{margin:g} of {r['p_selector_zero']}")  # fmt: skip
            a, b, w = bracket_weight(job_time(batch, row["file"]), times)
            for q in sorted(set(range(batch["manifest"]["nqubits"])) - touched(batch["texts"][row["file"]])):
                base = (1 - w) * brackets[a]["k01"][q] / brackets[a]["n0"] + w * brackets[b]["k01"][q] / brackets[b][
                    "n0"
                ]
                p = int(bits[:, q].sum()) / n
                if p > base + t["idle_p1_above_readout_0_at_most"]:
                    problems.append(
                        f"{row['file']} idle q{q} P1 {p:.3f} exceeds its interpolated readout-0 P1 {base:.3f} by more "
                        f"than {t['idle_p1_above_readout_0_at_most']} (bit-order conformance)"
                    )
        batch_block[name] = {"run": batch["run"], "sanity": "pass" if not problems else "fail", "problems": problems}
        if problems:
            stops.append(f"sanity stop at {name}: {problems[0]}")

    replicas = []
    for index, item in enumerate(lcu):
        r = item["replica"]
        a, d = r["roles"]["selector"], r["roles"]["data"][0]
        n = item["shots"]
        raw = (item["joint"][0] + item["joint"][1]) / n
        ends = [float(corrected_zero(raw, *rates_at(observed, item, a, force))[0]) for force in (0.0, 1.0)]
        replicas.append({
            "batch": item["batch"], "file": item["file"], "slot": r["slot"], "label": r["label"],
            "relation": r["relation"], "setting": r["setting"], "cz_depth": r["cz_depth"], "pair": [a, d],
            "joint_counts": item["joint"], "p_zero_raw": raw,
            "readout": {"selector": interpolated(brackets, item["weights"], a),
                        "data": interpolated(brackets, item["weights"], d)},
            "p_zero_corrected": both(lambda v, i=index: v["pc"][i]),
            "bracket_systematic": abs(ends[1] - ends[0]),
        })  # fmt: skip

    def pick(**want: Any) -> list[int]:
        return [i for i, item in enumerate(lcu) if all(item["replica"].get(k) == v for k, v in want.items())]

    def one(**want: Any) -> int:
        found = pick(**want)
        if len(found) != 1:
            fail(f"the follow design holds {len(found)} LCU replicas with {want}, not one")
        return found[0]

    def mean(v: Values, indices: list[int]) -> Any:
        return sum(v["pc"][i] for i in indices) / len(indices)

    # Classification: D = Pc(y_sign -1) - Pc(y_sign +1) per row and pair at CZ depth 1, settings pooled by mean.
    classification = []
    groups: dict[tuple[str, int], dict[int, list[int]]] = {}
    for i in pick(cz_depth=1):
        r = lcu[i]["replica"]
        groups.setdefault((r["label"][:-1], r["roles"]["selector"]), {}).setdefault(r["q"][2], []).append(i)
    for (row_name, selector), signs in sorted(groups.items()):
        if set(signs) != {-1, 1}:
            fail(f"the follow {row_name} on selector q{selector} lacks a y_sign")
        stat = both(lambda v, s=signs: mean(v, s[-1]) - mean(v, s[1]))
        value = stat["value"]
        if value is None:
            reading = "undetermined"
        elif value > t["same_sign_above"]:
            reading = "same-sign"
        elif value < t["opposite_sign_below"]:
            reading = "opposite-sign"
        elif abs(value) < t["strut_abs_below"]:
            reading = "strut"
        else:
            reading = "unresolved"
        first = lcu[signs[1][0]]["replica"]
        expected = CLASSES[first["relation"]]
        verdict = "classified" if reading == expected else "refuted"
        classification.append({"row": row_name, "pair": [selector, first["roles"]["data"][0]],
                               "relation": first["relation"], "settings": sorted({lcu[i]["replica"]["setting"]
                               for s in signs.values() for i in s}), "D": stat, "class": reading,
                               "expected": expected, "verdict": verdict})  # fmt: skip
        if verdict == "refuted":
            refutations.append(
                f"{row_name} on q{[selector, first['roles']['data'][0]]}: D reads {reading}, census {expected}"
            )

    # Twist crossover per block and setting; pair and circuit offsets cancel in Delta.
    twist = []
    for block_name, edge, tw in (("bright", "edge+", "twist-"), ("dark", "edge-", "twist+")):
        for setting in ("X", "Y"):
            c1, c2 = (f"lcu-{block_name}-{setting.lower()}-{k}.cq" for k in (1, 2))
            slots = {
                key: one(label=label, slot=slot, setting=setting, cz_depth=1)
                for key, label, slot in (("e0", edge, 0), ("t0", tw, 0), ("e1", edge, 1), ("t1", tw, 1))
            }
            files = {key: lcu[i]["file"] for key, i in slots.items()}
            if files != {"e0": c1, "t0": c2, "e1": c2, "t1": c1}:
                fail(f"the {block_name} {setting} crossover places its replicas in {files}")
            stat = both(
                lambda v, x=slots: ((v["pc"][x["e0"]] - v["pc"][x["t0"]]) + (v["pc"][x["e1"]] - v["pc"][x["t1"]])) / 2
            )
            value, se = stat["value"], stat["se"]
            verdict = (
                "undetermined" if value is None or not se else "refuted" if abs(value) > sigma * se else "consistent"
            )
            twist.append({"block": block_name, "setting": setting, "edge": edge, "twist": tw, "delta": stat,
                          "z": value / se if value is not None and se else None, "verdict": verdict})  # fmt: skip
            if verdict == "refuted":
                refutations.append(f"twist equality refuted in the {block_name} block, setting {setting}")

    # Strut D per setting against the null offset.
    strut = []
    for setting in ("X", "Y"):
        plus = pick(relation="strut", setting=setting, cz_depth=1, label="strut+")
        minus = pick(relation="strut", setting=setting, cz_depth=1, label="strut-")
        if len(plus) != 1 or len(minus) != 1:
            fail(f"the follow strut in setting {setting} needs one replica per y_sign")
        stat = both(lambda v, m=minus[0], p=plus[0]: v["pc"][m] - v["pc"][p])
        limit = null + sigma * stat["se"] if stat["se"] is not None else None
        flag = stat["value"] is None or limit is None or abs(stat["value"]) > limit
        roles = lcu[plus[0]]["replica"]["roles"]
        strut.append({"setting": setting, "pair": [roles["selector"], roles["data"][0]], "D": stat,
                      "bias_limit": limit, "bias_flag": flag})  # fmt: skip
        if flag:
            refutations.append(f"strut setting {setting}: |D| above the bias limit (pair-dependent bias)")

    # Conditional coherence per replica and populated branch.
    coherence = []
    for index, item in enumerate(lcu):
        r = item["replica"]
        for b in branches(r):
            name = ("zero", "one")[b]
            prediction = fraction(r[f"expectation_given_selector_{name}"])
            stat = both(lambda v, k=(index, b): v["e"][k])
            value, se = stat["value"], stat["se"]
            kept = item["joint"][2 * b : 2 * b + 2]
            entry: dict[str, Any] = {"batch": item["batch"], "file": item["file"], "slot": r["slot"],
                                     "label": r["label"], "setting": r["setting"], "cz_depth": r["cz_depth"],
                                     "branch": b, "prediction": prediction,
                                     "expectation_raw": 2 * kept[0] / sum(kept) - 1 if sum(kept) else None,
                                     "expectation_corrected": stat,
                                     "z": value / se if value is not None and se else None}  # fmt: skip
            if r["relation"] == "strut":
                limit = null + sigma * se if se is not None else None
                entry["bound"] = limit
                refuted = value is None or limit is None or abs(value) > limit
                entry["verdict"] = "refuted" if refuted else "consistent"
            elif r["cz_depth"] != 1:
                entry["verdict"] = "depth ladder"
            elif r["setting"] == "X" and prediction != 0:
                entry["verdict"] = signed_verdict(value, se, math.copysign(1.0, prediction), sigma)
                if value is not None:
                    band = t["cross_prediction_band"]
                    entry["cross_prediction"] = {"magnitude": abs(value), "target": t["t0_c1"], "band": band,
                                                 "inside": abs(abs(value) - t["t0_c1"]) <= band}  # fmt: skip
            else:
                entry["verdict"] = "reported: the census predicts 0 and the falsifier names the X setting"
            if entry["verdict"] == "refuted":
                refutations.append(
                    f"{item['file']} slot {r['slot']} {r['label']} branch {b}: E_b refutes {prediction:g}"
                )
            coherence.append(entry)

    # Depth ladder per pair from the bright edge; X and Y replicas pair by (label, pair, depth).
    depths = list(t["depths"])
    ladder: list[dict[str, Any]] = []
    for selector in sorted({lcu[i]["replica"]["roles"]["selector"] for i in pick(label="edge+")}):
        cell: dict[tuple[int, str], int] = {}
        for n in depths:
            for s in ("X", "Y"):
                matches = [
                    i
                    for i in pick(label="edge+", cz_depth=n, setting=s)
                    if lcu[i]["replica"]["roles"]["selector"] == selector
                ]
                if len(matches) != 1:
                    fail(f"the follow ladder holds {len(matches)} edge+ replicas on q{selector} at depth {n} in {s}")
                cell[(n, s)] = matches[0]

        def ex(v: Values, n: int, c: dict[tuple[int, str], int] = cell) -> Any:
            return v["e"][(c[(n, "X")], 0)]

        def ey(v: Values, n: int, c: dict[tuple[int, str], int] = cell) -> Any:
            return v["e"][(c[(n, "Y")], 0)]

        def magnitude(v: Values, n: int) -> Any:
            return np.sqrt(ex(v, n) ** 2 + ey(v, n) ** 2)

        def phase(v: Values, n: int) -> Any:
            return np.arctan2(ey(v, n), -ex(v, n))

        def population(v: Values, n: int, c: dict[tuple[int, str], int] = cell) -> Any:
            return (v["pc"][c[(n, "X")]] + v["pc"][c[(n, "Y")]]) / 2

        def joint_coherence(v: Values, n: int) -> Any:
            return population(v, n) * magnitude(v, n)

        def contrast(v: Values, n: int) -> Any:
            return 2 * population(v, n) - 1

        points = [{"cz_depth": n, "E_X": both(lambda v, n=n: ex(v, n)), "E_Y": both(lambda v, n=n: ey(v, n)),
                   "magnitude": both(lambda v, n=n: magnitude(v, n)), "phase": both(lambda v, n=n: phase(v, n)),
                   "population": both(lambda v, n=n: population(v, n)),
                   "joint_coherence": both(lambda v, n=n: joint_coherence(v, n)),
                   "population_contrast": both(lambda v, n=n: contrast(v, n))} for n in depths]  # fmt: skip

        def unwrapped(v: Values) -> list[Any]:
            # np.unwrap along depth carries the phase across the atan2 branch cut, row by row.
            rows = np.unwrap(np.stack([phase(v, n) for n in depths], axis=-1), axis=-1)
            return [rows[..., k] for k in range(len(depths))]

        def log_slope(v: Values, fn: Any) -> Any:
            return ols_slope(depths, [np.log(fn(v, n)) for n in depths])

        data = lcu[cell[(depths[0], "X")]]["replica"]["roles"]["data"][0]
        ladder.append({
            "pair": [selector, data], "points": points,
            "r_coh": both(lambda v: np.exp(log_slope(v, joint_coherence)), pct),
            "r_pop": both(lambda v: np.exp(log_slope(v, contrast)), pct),
            "r_coh_over_r_pop": both(lambda v: np.exp(log_slope(v, joint_coherence) - log_slope(v, contrast)), pct),
            "phase_slope_per_cz": both(lambda v: ols_slope(depths, unwrapped(v)), pct),
        })  # fmt: skip

    # Walks: control expectations, falsifiers, magnitude and phase per walk.
    walk_rows = []
    for index, item in enumerate(walks):
        r = item["replica"]
        stat = both(lambda v, j=index: v["walk"][j])
        value, se = stat["value"], stat["se"]
        if r["readout"] == "Y":
            verdict = "reported: the census predicts 0 and the falsifier names the X readout"
        elif r["omit_last_block"]:
            bound = null + sigma * se if se is not None else None
            verdict = "refuted" if value is None or bound is None or abs(value) > bound else "consistent"
        else:
            verdict = signed_verdict(value, se, float(r["omega"]), sigma)
        observable = "<Y_c>" if r["readout"] == "Y" else "<X_c>"
        walk_rows.append({"batch": item["batch"], "file": item["file"], "triple": r["triple"], "layout": r["layout"],
                          "omega": r["omega"], "omit_last_block": r["omit_last_block"], "readout": r["readout"],
                          "cz": r["cz"], "zeros": item["zeros"], "shots": item["shots"],
                          "readout_rates": interpolated(brackets, item["weights"], r["roles"]["control"]),
                          "observable": observable, "expectation": stat,
                          "z": value / se if value is not None and se else None, "verdict": verdict})  # fmt: skip
        if verdict == "refuted":
            refutations.append(f"{item['file']} walk {r['triple']}: {observable} refutes omega {r['omega']}")
    walk_pairs = []
    for layout in sorted({w["replica"]["layout"] for w in walks}):
        same = [j for j, w in enumerate(walks) if w["replica"]["layout"] == layout]
        x = [j for j in same if walks[j]["replica"]["readout"] == "X" and not walks[j]["replica"]["omit_last_block"]]
        y = [j for j in same if walks[j]["replica"]["readout"] == "Y"]
        if len(x) != 1 or len(y) != 1:
            fail(f"the follow walk on {layout} needs one X and one Y readout")
        jx, jy = x[0], y[0]
        mag = both(lambda v, a=jx, b=jy: np.sqrt(v["walk"][a] ** 2 + v["walk"][b] ** 2))
        target = t["t0_r"] ** walks[jx]["replica"]["cz"]
        band = t["cross_prediction_band"]
        walk_pairs.append({"layout": layout, "triple": walks[jx]["replica"]["triple"], "magnitude": mag,
                           "prediction": target, "band": band,
                           "inside": mag["value"] is not None and abs(mag["value"] - target) <= band,
                           "phase": both(lambda v, a=jx, b=jy: np.arctan2(v["walk"][b], -v["walk"][a]))})  # fmt: skip

    # Replication of the deeper bright edge populations against T0's.
    replication: Any
    if t0 is None:
        replication = {"undetermined": "T0 runs were not analyzed with the follow series"}
    else:
        bright = {(r["qubit"], r["depth"]): r for r in t0["replicas"] if r["role"] == "bright"}
        replication = []
        for rung in ladder:
            for point_entry in rung["points"]:
                n = point_entry["cz_depth"]
                if n == 1:
                    continue
                follow = point_entry["population"]
                record: dict[str, Any] = {"pair": rung["pair"], "cz_depth": n, "follow": follow}
                prior = bright.get((rung["pair"][0], n))
                if prior is None or follow["value"] is None or follow["se"] is None:
                    record["t0"] = "no T0 bright replica at this pair and depth"
                else:
                    record["t0"] = {"batch": prior["batch"], "p_zero_corrected": prior["p_zero_corrected"],
                                    "se": prior["se"]}  # fmt: skip
                    record["drift"] = follow["value"] - prior["p_zero_corrected"]
                    record["drift_se"] = math.sqrt(follow["se"] ** 2 + prior["se"] ** 2)
                replication.append(record)
    return {
        "batches": batch_block,
        "brackets": block,
        "replicas": replicas,
        "classification": classification,
        "twist": twist,
        "strut": strut,
        "coherence": coherence,
        "depth_ladder": ladder,
        "walks": walk_rows,
        "walk_pairs": walk_pairs,
        "replication": replication,
        "uncertainty": f"standard errors are standard deviations and intervals the {pct[0]} and {pct[1]} "
        f"percentiles of a parametric bootstrap ({t['bootstrap_draws']} draws, numpy seed {t['bootstrap_seed']}); "
        "each draw redraws every bracket's readout counts once, so replicas reading one qubit share that draw, "
        "and each replica's joint (a, d) or control counts",
        "refutations": refutations,
        "stops": stops,
    }


# ---------------------------------------------------------------- ladder series

LADDER_LINE_SEED = 1
FOLLOW_RECORD = ROOT / "results/quantum_inspire/box_kite_tuna_17_follow_analysis.json"


def ladder_used(batches: dict[str, Batch]) -> list[int]:
    layout = next(iter(batches.values()))["manifest"]["layout"]
    return sorted(q for pair in layout["lcu_pairs"] for q in pair)


def context_files(batch: Batch) -> list[str]:
    return [row["file"] for row in batch["manifest"]["circuits"] if row["kind"] == "readout" and "excited" in row]


def idle_problems(batch: Batch, row: dict[str, Any], brackets: list[dict[str, Any]], margin: float) -> list[str]:
    """Idle qubits of a witness job above the interpolated readout-0 P1 by more than margin (bit-order conformance)."""
    bits = batch["bits"][row["file"]]
    a, b, w = bracket_weight(job_time(batch, row["file"]), [x["time_e01"] for x in brackets])
    problems = []
    for q in sorted(set(range(batch["manifest"]["nqubits"])) - touched(batch["texts"][row["file"]])):
        base = (1 - w) * brackets[a]["k01"][q] / brackets[a]["n0"] + w * brackets[b]["k01"][q] / brackets[b]["n0"]
        p = int(bits[:, q].sum()) / bits.shape[0]
        if p > base + margin:
            problems.append(
                f"{row['file']} idle q{q} P1 {p:.3f} exceeds its interpolated readout-0 P1 {base:.3f} by more than "
                f"{margin} (bit-order conformance)"
            )
    return problems


def lockin(bits: np.ndarray, frequency: float, columns: list[int]) -> list[dict[str, float]]:
    """First-harmonic amplitude, phase at the middle shot and standard error sqrt(2 var / n) of each column at f."""
    n = bits.shape[0]
    t = np.arange(n) - (n - 1) / 2
    design = np.stack([np.cos(2 * np.pi * frequency * t), np.sin(2 * np.pi * frequency * t)], axis=1)
    x = bits[:, columns].astype(np.float64)
    p = x.mean(axis=0)
    coefficients = np.linalg.lstsq(design, x - p, rcond=None)[0]
    amplitude = np.hypot(coefficients[0], coefficients[1])
    phase = np.arctan2(-coefficients[1], coefficients[0])
    se = np.sqrt(2 * p * (1 - p) / n)
    return [
        {"amplitude": float(a), "phase": float(f), "se": float(e)} for a, f, e in zip(amplitude, phase, se, strict=True)
    ]


def iso_brackets(batches: dict[str, Batch], brackets: list[dict[str, Any]], iso: list[int]) -> list[dict[str, Any]]:
    """The brackets holding readout-iso-x, with each iso qubit's e10 counts and time taken from that circuit.

    Only the iso qubits read their e10 from these brackets (qubit_weights in the cross-check); every other
    qubit keeps the readout-0 and readout-1 brackets and their finish times.
    """
    out = []
    for b in brackets:
        batch = batches[b["batch"]]
        if "readout-iso-x.cq" not in batch["bits"]:
            continue
        bits = batch["bits"]["readout-iso-x.cq"]
        if bits.shape[0] != b["n1"]:
            fail(f"{b['batch']}: readout-iso-x and readout-1 differ in shots")
        k10 = list(b["k10"])
        for q in iso:
            k10[q] = int((bits[:, q] == 0).sum())
        out.append({**b, "k10": k10, "time_e10": job_time(batch, "readout-iso-x.cq")})
    return out


def ladder_stops(batches: dict[str, Batch], t: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    """The stop rules a ladder batch is judged by before the next one: brackets, context floor, per-batch sanity.

    They read only the batches run so far, so an incomplete series is judged by the same rules.
    """
    block, stops = bracket_block(batches, t, ladder_used(batches))
    brackets = follow_brackets(batches)
    batch_block: dict[str, Any] = {}
    for name, batch in batches.items():
        problems = []
        for file in context_files(batch):
            for q in t["iso_qubits"]:
                p1 = int(batch["bits"][file][:, q].sum()) / batch["bits"][file].shape[0]
                if p1 < t["readout_1_p1_at_least"]:
                    stops.append(f"bracket stop: {name} {file} q{q} P1 {p1:.3f} below {t['readout_1_p1_at_least']}")
        for row in witness_rows(batch):
            if not brackets:
                fail(f"{name}: a Latin batch before any readout bracket")
            bits = batch["bits"][row["file"]]
            for r in row["replicas"]:
                if r["cz_depth"] in t["bright_floor_cz_depths"] and r["p_selector_zero"] == "1":
                    p = int((bits[:, r["roles"]["selector"]] == 0).sum()) / bits.shape[0]
                    if p < t["bright_p_selector_zero_at_least"]:
                        problems.append(f"{row['file']} slot {r['slot']} raw P(a = 0) {p:.3f} below "
                                        f"{t['bright_p_selector_zero_at_least']}")  # fmt: skip
            problems += idle_problems(batch, row, brackets, t["idle_p1_above_readout_0_at_most"])
        batch_block[name] = {"run": batch["run"], "sanity": "pass" if not problems else "fail", "problems": problems}
        if problems:
            stops.append(f"sanity stop at {name}: {problems[0]}")
    return block, batch_block, stops


def replica_columns(row: dict[str, Any]) -> list[int]:
    """The selector and data qubits of a witness row's replicas, the columns its preregistered line scan reads."""
    return sorted(q for r in row["replicas"] for q in [r["roles"]["selector"], *r["roles"]["data"]])


class LineScan:
    """qi_shot_record_line.scan in the manifest's band and threshold, picklable for parallel.ordered_map."""

    def __init__(self, band: tuple[float, float], detection_p: float):
        self.band, self.detection_p = band, detection_p

    def __call__(self, bits: np.ndarray) -> dict[str, Any]:
        return scan(bits.astype(np.float64), self.band, self.detection_p)


def analyze_ladder(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    """The ladder series (module docstring): brackets, sanity, within-batch ladder, line lock-in, readout context."""
    iso = list(t["iso_qubits"])
    block, batch_block, stops = ladder_stops(batches, t)
    refutations: list[str] = []
    brackets = follow_brackets(batches)
    lcu, walks = follow_items(batches, brackets)
    if walks:
        fail("the ladder design holds no walk")
    rng = np.random.default_rng(t["bootstrap_seed"])
    observed = follow_sample(brackets, lcu, walks)
    point = follow_values(observed, lcu, walks)
    boot = pooled_follow_values(follow_sample(brackets, lcu, walks, rng, t["bootstrap_draws"]), lcu, walks)
    pct = t["interval_percentiles"]
    sigma = t["sigma"]

    def both(fn: Any, percentiles: list[float] | None = None) -> dict[str, Any]:
        with np.errstate(all="ignore"):
            return summary(fn(point), fn(boot), percentiles)

    replicas = []
    for index, item in enumerate(lcu):
        r = item["replica"]
        a, d = r["roles"]["selector"], r["roles"]["data"][0]
        replicas.append({
            "batch": item["batch"], "file": item["file"], "slot": r["slot"], "setting": r["setting"],
            "cz_depth": r["cz_depth"], "pair": [a, d], "joint_counts": item["joint"],
            "p_zero_raw": (item["joint"][0] + item["joint"][1]) / item["shots"],
            "readout": {"selector": interpolated(brackets, item["weights"], a),
                        "data": interpolated(brackets, item["weights"], d)},
            "p_zero_corrected": both(lambda v, i=index: v["pc"][i]),
            "expectation_corrected": both(lambda v, i=index: v["e"][(i, 0)]),
        })  # fmt: skip

    # The within-batch ladder: every pair at every depth inside one batch.
    depths = list(t["depths"])
    cells: dict[str, dict[int, dict[int, int]]] = {}
    for index, item in enumerate(lcu):
        selector = item["replica"]["roles"]["selector"]
        cell = cells.setdefault(item["batch"], {}).setdefault(selector, {})
        if item["replica"]["cz_depth"] in cell:
            fail(f"{item['batch']} holds two depth-{item['replica']['cz_depth']} replicas on q{selector}")
        cell[item["replica"]["cz_depth"]] = index
    names = list(cells)
    setting_of = {
        name: lcu[next(iter(next(iter(c.values())).values()))]["replica"]["setting"] for name, c in cells.items()
    }
    ladder = []
    for name in names:
        for selector, cell in sorted(cells[name].items()):
            if sorted(cell) != depths:
                fail(f"{name} q{selector} holds depths {sorted(cell)}, not {depths}")

            def contrast(v: Values, n: int, c: dict[int, int] = cell) -> Any:
                return 2 * v["pc"][c[n]] - 1

            def joint(v: Values, n: int, c: dict[int, int] = cell) -> Any:
                return v["pc"][c[n]] * np.abs(v["e"][(c[n], 0)])

            def log_slope(v: Values, fn: Any) -> Any:
                return ols_slope(depths, [np.log(fn(v, n)) for n in depths])

            entry: dict[str, Any] = {
                "batch": name, "setting": setting_of[name], "pair": lcu[cell[1]]["replica"]["roles"]["selector"],
                "data": lcu[cell[1]]["replica"]["roles"]["data"][0],
                "files": {str(n): lcu[cell[n]]["file"] for n in depths},
                "population_contrast": {str(n): both(lambda v, n=n: contrast(v, n)) for n in depths},
                "r_pop": both(lambda v: np.exp(log_slope(v, contrast)), pct),
            }  # fmt: skip
            entry["pair"] = [entry.pop("pair"), entry.pop("data")]
            if setting_of[name] == "X":
                entry["joint_coherence"] = {str(n): both(lambda v, n=n: joint(v, n)) for n in depths}
                entry["r_coh"] = both(lambda v: np.exp(log_slope(v, joint)), pct)
                entry["rho"] = both(lambda v: np.exp(log_slope(v, joint) - log_slope(v, contrast)), pct)
            else:
                partner = names[names.index(name) - 1]
                x_cell = cells[partner][selector]
                entry["phase_against"] = partner
                entry["phase"] = {
                    str(n): both(lambda v, n=n, y=cell, x=x_cell: np.arctan2(v["e"][(y[n], 0)], -v["e"][(x[n], 0)]))
                    for n in depths
                }
            ladder.append(entry)
    decisions = []
    for selector in sorted({tuple(e["pair"]) for e in ladder}):
        x_rows = [e for e in ladder if tuple(e["pair"]) == selector and e["setting"] == "X"]
        intervals = [e["rho"]["interval"] for e in x_rows]
        if any(i is None for i in intervals):
            verdict = "undetermined"
        elif all(i[1] < 1 for i in intervals):
            verdict = "below 1"
        elif all(i[0] > 1 for i in intervals):
            verdict = "above 1"
        elif all(i[0] <= 1 <= i[1] for i in intervals):
            verdict = "consistent with 1"
        else:
            verdict = "replicate-split"
        values = [e["rho"]["value"] for e in x_rows]
        ses = [e["rho"]["se"] for e in x_rows]
        z = None
        if len(x_rows) == 2 and None not in values and None not in ses and (ses[0] ** 2 + ses[1] ** 2) > 0:
            z = (values[0] - values[1]) / math.sqrt(ses[0] ** 2 + ses[1] ** 2)
        decisions.append({"pair": list(selector), "batches": [e["batch"] for e in x_rows], "rho": values,
                          "verdict": verdict, "replicate_z": z,
                          "replicate_scatter": z is not None and abs(z) > sigma})  # fmt: skip

    # The 50 Hz line per Latin job: detection on the replica qubits, selector lock-in by depth, phase-binned contrast.
    line = []
    bins = t["line_phase_bins"]
    jobs = [(name, batch, row) for name, batch in batches.items() for row in witness_rows(batch)]
    scans = parallel.ordered_map(
        LineScan(tuple(t["line_band"]), t["line_detection_p"]),
        [batch["bits"][row["file"]][:, replica_columns(row)] for _, batch, row in jobs],
    )
    for (name, batch, row), scanned in zip(jobs, scans, strict=True):
        bits = batch["bits"][row["file"]]
        by_depth = {r["cz_depth"]: r for r in row["replicas"]}
        entry = {"batch": name, "file": row["file"], "detected": scanned["detected"],
                 "log10_p": scanned.get("log10_p"), "cycles_per_shot": scanned.get("cycles_per_shot")}  # fmt: skip
        if scanned.get("cycles_per_shot") is None:
            line.append(entry)
            refutations.append(f"{name} {row['file']}: no line scanned")
            continue
        f = scanned["cycles_per_shot"]
        selectors = [by_depth[n]["roles"]["selector"] for n in depths]
        locks = dict(zip(depths, lockin(bits, f, selectors), strict=True))
        entry["selectors"] = {str(n): {"qubit": by_depth[n]["roles"]["selector"], **locks[n]} for n in depths}
        entry["third_harmonic"] = {
            str(n): lockin(bits, 3 * f, [by_depth[n]["roles"]["selector"]])[0]["amplitude"] for n in depths
        }
        deep, shallow = locks[max(depths)], locks[min(depths)]
        margin = deep["amplitude"] - shallow["amplitude"]
        margin_se = math.sqrt(deep["se"] ** 2 + shallow["se"] ** 2)
        grows = margin > t["amplitude_sigmas"] * margin_se
        entry["depth_growth"] = {"difference": margin, "se": margin_se, "holds": grows}
        phases = [locks[n]["phase"] for n in depths if n != min(depths)]
        entry["phase_resultant"] = float(abs(np.exp(1j * np.array(phases)).mean()))
        # Bin 0 holds the line phase where the deepest selector's P1 peaks.
        n_shots = bits.shape[0]
        theta = 2 * np.pi * f * (np.arange(n_shots) - (n_shots - 1) / 2) + deep["phase"]
        index_bin = np.floor(np.mod(theta + np.pi / bins, 2 * np.pi) / (2 * np.pi / bins)).astype(np.int64) % bins
        binned = {}
        for n in depths:
            item_index = next(i for i, it in enumerate(lcu) if it["batch"] == name and it["file"] == row["file"]
                              and it["replica"]["cz_depth"] == n)  # fmt: skip
            q = by_depth[n]["roles"]["selector"]
            e01, e10 = (float(x[0]) for x in rates_at(observed, lcu[item_index], q))
            counts = np.bincount(index_bin, minlength=bins)
            zeros_in = np.bincount(index_bin, weights=(bits[:, q] == 0).astype(np.float64), minlength=bins)
            raw = zeros_in / counts
            pc = (raw - e10) / (1 - e01 - e10)
            binned[str(n)] = {"contrast": [float(2 * v - 1) for v in pc],
                              "se": [float(2 * math.sqrt(r * (1 - r) / c) / (1 - e01 - e10))
                                     for r, c in zip(raw, counts, strict=True)]}  # fmt: skip
        entry["phase_binned_contrast"] = binned
        line.append(entry)
        if not scanned["detected"]:
            refutations.append(f"{name} {row['file']}: no 50 Hz line at p below {t['line_detection_p']}")
        elif not grows:
            refutations.append(f"{name} {row['file']}: the depth-9 line amplitude does not exceed depth 1's")

    # Readout context on the iso qubits, and the e01 of each pair's other qubit beside an excited neighbor.
    def rate(batch: Batch, file: str, q: int, state: int) -> tuple[float, float, int]:
        bits = batch["bits"][file]
        k = int((bits[:, q] != state).sum())
        n = bits.shape[0]
        return k / n, k * (n - k) / n**3, n

    context = []
    iso_runs = [(name, b) for name, b in batches.items() if "readout-iso-x.cq" in b["bits"]]
    hzh_runs = [(name, b) for name, b in batches.items() if "readout-iso-hzh.cq" in b["bits"]]
    partners = {q: next(p for pair in next(iter(batches.values()))["manifest"]["layout"]["lcu_pairs"]
                        for p in pair if q in pair and p != q) for q in iso}  # fmt: skip
    for q in iso:
        rows: list[dict[str, float | str]] = []
        for name, b in iso_runs:
            e_all, v_all, _ = rate(b, "readout-1.cq", q, 1)
            e_iso, v_iso, _ = rate(b, "readout-iso-x.cq", q, 1)
            rows.append({"batch": name, "e10_all": e_all, "e10_iso": e_iso, "difference": e_all - e_iso,
                         "se": math.sqrt(v_all + v_iso)})  # fmt: skip
        minimum, k = t["context_min"], t["amplitude_sigmas"]
        if len(rows) < 2:
            neighbor = "undetermined"
        elif all(float(r["difference"]) > minimum and float(r["difference"]) > k * float(r["se"]) for r in rows):
            neighbor = "established"
        elif all(abs(float(r["difference"])) < minimum for r in rows):
            neighbor = "absent"
        else:
            neighbor = "unresolved"
        preparation: dict[str, Any] = {"verdict": "undetermined"}
        if len(iso_runs) >= 2 and hzh_runs:
            b0, b6 = iso_runs[0][1], iso_runs[-1][1]
            name3, b3 = hzh_runs[0]
            t0_, t6_ = job_time(b0, "readout-iso-x.cq"), job_time(b6, "readout-iso-x.cq")
            t3_ = job_time(b3, "readout-iso-hzh.cq")
            w = min(1.0, max(0.0, (t3_ - t0_) / (t6_ - t0_)))
            e0, v0, _ = rate(b0, "readout-iso-x.cq", q, 1)
            e6, v6, _ = rate(b6, "readout-iso-x.cq", q, 1)
            e3, v3, _ = rate(b3, "readout-iso-hzh.cq", q, 1)
            interp = (1 - w) * e0 + w * e6
            diff = e3 - interp
            se = math.sqrt(v3 + (1 - w) ** 2 * v0 + w**2 * v6)
            verdict = (
                "established" if abs(diff) > minimum and abs(diff) > k * se
                else "absent" if abs(diff) < minimum else "unresolved"
            )  # fmt: skip
            preparation = {"batch": name3, "e10_hzh": e3, "e10_iso_interpolated": interp, "weight": w,
                           "difference": diff, "se": se, "verdict": verdict}  # fmt: skip
        partner = partners[q]
        beside = []
        for name, b in iso_runs:
            e_ctx, v_ctx, _ = rate(b, "readout-iso-x.cq", partner, 0)
            e_0, v_0, _ = rate(b, "readout-0.cq", partner, 0)
            beside.append({"batch": name, "qubit": partner, "e01_beside_excited": e_ctx, "e01_readout_0": e_0,
                           "difference": e_ctx - e_0, "se": math.sqrt(v_ctx + v_0)})  # fmt: skip
        context.append({"qubit": q, "neighbor_context": {"rows": rows, "verdict": neighbor},
                        "preparation_path": preparation, "partner_e01": beside})  # fmt: skip

    # Witness cross-check: the depth-1 X E_0 on the pair whose data qubit is an iso qubit, both corrections.
    cross = []
    alternative = iso_brackets(batches, brackets, iso)
    if len(alternative) >= 2:
        combined = brackets + alternative
        iso_times = [b["time_e10"] for b in alternative]
        cross_rng = np.random.default_rng([t["bootstrap_seed"], LADDER_LINE_SEED])
        for index, item in enumerate(lcu):
            r = item["replica"]
            data = r["roles"]["data"][0]
            if r["setting"] != "X" or r["cz_depth"] != 1 or data not in iso:
                continue
            near, far, weight = bracket_weight(job_time(batches[item["batch"]], item["file"]), iso_times)
            shift = len(brackets)
            iso_e10 = (near + shift, far + shift, weight)
            moved = {**item, "qubit_weights": {data: {"e01": item["weights"]["e01"], "e10": iso_e10}}}
            alt_point = follow_values(follow_sample(combined, [moved], []), [moved], [])
            alt_boot = follow_values(follow_sample(combined, [moved], [], cross_rng, t["bootstrap_draws"]),
                                     [moved], [])  # fmt: skip
            with np.errstate(all="ignore"):
                iso_stat = summary(alt_point["e"][(0, 0)], alt_boot["e"][(0, 0)])
            primary = both(lambda v, i=index: v["e"][(i, 0)])
            cross.append({"batch": item["batch"], "file": item["file"], "pair": [r["roles"]["selector"],
                          r["roles"]["data"][0]], "readout_1_corrected": primary, "iso_corrected": iso_stat,
                          "iso_within_unit": iso_stat["value"] is not None and iso_stat["se"] is not None
                          and abs(iso_stat["value"]) - 1 <= 3 * iso_stat["se"],
                          "readout_1_above_unit": primary["value"] is not None
                          and abs(primary["value"]) > 1})  # fmt: skip

    # Replication against the follow series' populations on the same pair and depth.
    replication: Any
    if not FOLLOW_RECORD.exists():
        replication = {"undetermined": "the follow analysis record is absent"}
    else:
        follow = json.loads(FOLLOW_RECORD.read_text(encoding="utf-8"))["stages"]["tuna_follow"]["depth_ladder"]
        replication = {"follow_record_sha256": sha256(FOLLOW_RECORD.read_bytes()), "rows": []}
        for rung in follow:
            for entry_f in rung["points"]:
                n = entry_f["cz_depth"]
                if n == 1:
                    continue
                indices = [i for i, it in enumerate(lcu) if it["replica"]["roles"]["selector"] == rung["pair"][0]
                           and it["replica"]["cz_depth"] == n]  # fmt: skip
                stat = both(lambda v, ids=indices: sum(v["pc"][i] for i in ids) / len(ids))
                prior = entry_f["population"]
                row_r: dict[str, Any] = {"pair": rung["pair"], "cz_depth": n, "ladder": stat, "follow": prior}
                if stat["value"] is not None and prior["value"] is not None and stat["se"] and prior["se"]:
                    row_r["drift"] = stat["value"] - prior["value"]
                    row_r["drift_se"] = math.sqrt(stat["se"] ** 2 + prior["se"] ** 2)
                replication["rows"].append(row_r)
    return {
        "batches": batch_block,
        "brackets": block,
        "replicas": replicas,
        "within_batch_ladder": ladder,
        "rho_decisions": decisions,
        "line": line,
        "readout_context": context,
        "witness_cross_check": cross,
        "replication": replication,
        "uncertainty": f"standard errors are standard deviations and intervals the {pct[0]} and {pct[1]} "
        f"percentiles of a parametric bootstrap ({t['bootstrap_draws']} draws, numpy seed {t['bootstrap_seed']}) "
        "of every bracket's readout counts and each replica's joint (a, d) counts; the witness cross-check draws "
        f"from numpy seed [{t['bootstrap_seed']}, {LADDER_LINE_SEED}]; line and context errors are binomial",
        "refutations": refutations,
        "stops": stops,
    }


def binomial_z(k: int, n: int, p: float) -> float | None:
    return (k - n * p) / math.sqrt(n * p * (1 - p)) if 0 < p < 1 else None


WILSON_Z = 1.959963984540054


def proportion(k: int, n: int) -> dict[str, Any]:
    """k of n with its binomial standard error and Wilson 95% interval."""
    p = k / n
    centre = (p + WILSON_Z**2 / (2 * n)) / (1 + WILSON_Z**2 / n)
    half = WILSON_Z * math.sqrt(p * (1 - p) / n + WILSON_Z**2 / (4 * n * n)) / (1 + WILSON_Z**2 / n)
    return {
        "count": k,
        "shots": n,
        "value": p,
        "se": math.sqrt(p * (1 - p) / n),
        "wilson95": [centre - half, centre + half],
    }


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
                entry["stray_fraction"] = proportion(entry["stray"], len(shots))
                entry["outcomes"] = {
                    key: {
                        **proportion(counts.get(key, 0), len(shots)),
                        "prediction": p,
                        "z": binomial_z(counts.get(key, 0), len(shots), fraction(p)),
                    }
                    for key, p in expected.items()
                }
                inside = all(o["z"] is None or abs(o["z"]) < t["z_limit"] for o in entry["outcomes"].values())
                entry["verdict"] = "conforms" if inside and not entry["stray"] else "emulator rate"
            else:
                entry["verdict"] = f"failed: names factor {row['ladder']}"
                if row["ladder"] == t["gating_factor"]:
                    stops.append(f"{row['ladder']} failed: the Ry smoke subset is stopped")
            rows.append(entry)
    gating = [r for r in rows if r["ladder"] == t["gating_factor"]]
    return {
        "circuits": rows,
        "gating_factor": {"factor": t["gating_factor"], "failed": any(r["status"] != "completed" for r in gating)},
        "stops": stops,
    }


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
                k = zeros(batch, row["file"], r["roles"]["selector"])
                p = fraction(r["p_selector_zero"])
                entry: dict[str, Any] = {"batch": name, "file": row["file"], "slot": r["slot"],
                                         "pattern": r["pattern"], "prediction": r["p_selector_zero"], "zeros": k,
                                         "shots": len(shots), "p_zero": k / len(shots),
                                         "p_zero_uncertainty": proportion(k, len(shots))}  # fmt: skip
                if p in (0.0, 1.0):
                    ideal_count = k if p == 1.0 else len(shots) - k
                    ideal = ideal_count / len(shots)
                    entry["ideal_fraction"] = ideal
                    entry["ideal_fraction_uncertainty"] = proportion(ideal_count, len(shots))
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


def twin_checks(replica: dict[str, Any]) -> list[tuple[str, int, int | None, int, str]]:
    """(name, qubit, conditioning qubit or None, its conditioning value, P(qubit = 0) prediction) of one twin."""
    roles = replica["roles"]
    if "p_control_zero" in replica:
        return [("p_control_zero", roles["control"], None, 0, replica["p_control_zero"])]
    checks: list[tuple[str, int, int | None, int, str]] = [
        ("p_selector_zero", roles["selector"], None, 0, replica["p_selector_zero"])
    ]
    for value, name in enumerate(("zero", "one")):
        key = f"p_data_zero_given_selector_{name}"
        if key in replica:
            checks.append((key, roles["data"][0], roles["selector"], value, replica[key]))
    return checks


def analyze_twins(batches: dict[str, Batch], t: dict[str, Any]) -> dict[str, Any]:
    """Each twin on the ideal QX emulator: a deterministic prediction admits no shot off it, P = 1/2 sits inside z."""
    rows, stops = [], []
    for name, batch in batches.items():
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
                bits = batch["bits"][row["file"]]
                for check_name, qubit, given, value, want in twin_checks(replica):
                    column = bits[:, qubit] if given is None else bits[bits[:, given] == value, qubit]
                    kept = int(column.size)
                    k = int((column == 0).sum())
                    p = fraction(want)
                    entry: dict[str, Any] = {"batch": name, "file": row["file"], "slot": replica["slot"],
                                             "check": check_name, "prediction": want, "zeros": k,
                                             "shots": kept}  # fmt: skip
                    if p in (0.0, 1.0):
                        entry["off"] = kept - k if p == 1.0 else k
                        refuted = entry["off"] > t["deterministic_shots_off_at_most"]
                    else:
                        entry["z"] = binomial_z(k, kept, p) if kept else None
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
        gate_stops: list[str] = []
        if family == "tuna_t0":
            out["batches"], sanity_stops = sanity_block(batches, t)
        elif family != "tuna_pre":
            out["batches"] = {name: {"run": b["run"]} for name, b in batches.items()}
        if missing and family not in INDEPENDENT_BATCHES:
            estimates: dict[str, Any] = {"stops": []}
            if family == "tuna_follow":
                # The bracket stop rule decides before each later batch, so the brackets run so far are judged.
                estimates["brackets"], estimates["stops"] = bracket_block(batches, t)
            elif family == "tuna_ladder":
                # Every ladder stop rule decides before the next batch, so the batches run so far are judged.
                estimates["brackets"], out["batches"], estimates["stops"] = ladder_stops(batches, t)
            out["verdict"] = f"incomplete: {', '.join(missing)} not analyzed"
        else:
            if family == "tuna_pre":
                estimates = analyze_pre(batches, t)
            elif family == "tuna_t0":
                estimates = analyze_t0(batches, t)
            elif family == "tuna_follow":
                estimates = analyze_follow(batches, t, results.get("tuna_t0"))
            elif family == "ry_ladder":
                estimates = analyze_ry_ladder(batches, t)
            elif family == "tuna_ladder":
                estimates = analyze_ladder(batches, t)
            elif family in ("tuna_twins", "tuna_ladder_twins"):
                estimates = analyze_twins(batches, t)
            else:
                estimates = analyze_ry_smoke(batches, t)
                ladder = results.get("ry_ladder")
                if ladder is None:
                    estimates["ladder_gate"] = "unverified: the ry_ladder runs were not analyzed in this call"
                elif ladder["gating_factor"]["failed"]:
                    factor = ladder["gating_factor"]["factor"]
                    estimates["ladder_gate"] = f"stopped: {factor} failed in the ladder"
                    estimates["stops"].insert(0, f"ladder gate: {factor} failed, which stops the Ry smoke subset")
                else:
                    estimates["ladder_gate"] = f"passed: {ladder['gating_factor']['factor']} completed"
            if family in T0_DEPENDENT:
                t0 = results.get("tuna_t0")
                if t0 is None:
                    estimates["t0_gate"] = (
                        "unverified: T0 runs incomplete in this call"
                        if "tuna_t0" in stages
                        else "unverified: T0 runs not analyzed in this call"
                    )
                else:
                    gate = [
                        message
                        for flag, message in (
                            ("end_program", "T0 gate: the depth-1 bound ended the Tuna program"),
                            ("resize", "T0 gate: resize before running"),
                        )
                        if t0["gate"][flag]
                    ]
                    estimates["t0_gate"] = "; ".join(gate) if gate else "passed"
                    gate_stops = gate
            results[family] = estimates
        stops = gate_stops + sanity_stops + estimates.pop("stops")
        out.update(estimates)
        out["stops"] = stops
        if "verdict" not in out:
            out["verdict"] = "stop" if stops else "refuted" if out.get("refutations") else "continue"
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
# qubit and circuit, and a batch map per qubit and batch.
SYN_E01 = 0.02
SYN_E10 = 0.06
SYN_VISIBILITY = 0.85


def synthetic_shots(item: tuple[int, int, int, dict[Any, Any], dict[int, tuple[float, float]]]) -> list[str]:
    """Pool worker: shots of one circuit from its seed, width, shot count, true model and readout model.

    model maps a qubit to its P(true 1), or a group key (a, d) to the four
    joint probabilities indexed 2 a + d; unnamed qubits stay in |0>. Each
    qubit then reads |0> as 1 with its e01 and |1> as 0 with its e10.
    """
    seed, width, n, model, readout = item
    rng = np.random.default_rng(seed)
    true = np.zeros((n, width), dtype=np.uint8)
    for key, value in sorted(model.items(), key=lambda kv: str(kv[0])):
        if isinstance(key, tuple):
            outcome = np.minimum(np.searchsorted(np.cumsum(value), rng.random(n), side="right"), 3)
            true[:, key[0]], true[:, key[1]] = outcome >> 1, outcome & 1
        else:
            true[:, key] = rng.random(n) < value
    rates = np.array([readout.get(q, (SYN_E01, SYN_E10)) for q in range(width)])
    flip = rng.random((n, width)) < np.where(true == 0, rates[:, 0], rates[:, 1])
    text = ((true ^ flip)[:, ::-1] + 48).astype(np.uint8).tobytes().decode("ascii")
    return [text[s * width : (s + 1) * width] for s in range(n)]


def lcu_model(replica: dict[str, Any], scenario: dict[str, Any], visibility: float) -> dict[Any, Any]:
    """An LCU replica under a global depolarizing channel: lambda = amplitude r^n mixes the ideal state with I / 4.

    Without a setting the selector alone carries P(a = 0) = 1/2 + (P - 1/2) lambda. With one, the ideal joint (a, d)
    distribution has P(a = 0) = P and, on a populated branch with census X expectation e (2 x coherence),
    E_X = e cos(theta), E_Y = -e sin(theta) for theta = phase_per_cz n, so atan2(E_Y, -E_X) = theta on the bright
    edge; then P(a = 0) J and 2 P(a = 0) - 1 both decay as lambda. A strut or twist shift moves selector mass
    between the branches after the channel.
    """
    depth = replica.get("cz_depth", 1)
    decay = scenario.get("amplitude", visibility) * scenario.get("r", 1.0) ** depth
    p0 = fraction(replica["p_selector_zero"])
    shift = 0.0
    if replica.get("relation") == "strut" and replica["q"][2] == -1:
        shift += scenario.get("strut_shift", 0.0)
    if replica.get("label") == "twist-":
        shift -= scenario.get("twist_shift", 0.0)
    a, d = replica["roles"]["selector"], replica["roles"]["data"][0]
    if "setting" not in replica:
        return {a: 1 - (0.5 + (p0 - 0.5) * decay + shift), d: 0.5}
    theta = scenario.get("phase_per_cz", 0.0) * depth
    ideal = []
    for branch, mass in (("0", p0), ("1", 1 - p0)):
        coherence = replica.get(f"coherence_selector_{branch}")
        value = 0.0
        if coherence is not None:
            e = 2 * fraction(coherence)
            value = e * math.cos(theta) if replica["setting"] == "X" else -e * math.sin(theta)
            if scenario.get("coherence_flipped") and replica["setting"] == "X" and depth == 1:
                value = -value
        ideal += [mass * (1 + value) / 2, mass * (1 - value) / 2]
    joint = [decay * p + (1 - decay) / 4 for p in ideal]
    if shift:
        pa0 = joint[0] + joint[1]
        scale = [(pa0 + shift) / pa0] * 2 + [(1 - pa0 - shift) / (1 - pa0)] * 2
        joint = [p * k for p, k in zip(joint, scale, strict=True)]
    return {(a, d): joint}


def tuna_model(row: dict[str, Any], scenario: dict[str, Any]) -> dict[Any, Any]:
    visibility = scenario.get("visibility", SYN_VISIBILITY)
    model: dict[Any, Any] = {}
    for r in row["replicas"]:
        if r["kind"] == "walk":
            omega = -r["omega"] if scenario.get("walk_sign_flipped") else r["omega"]
            g = scenario["walk_r"] ** r["cz"] if "walk_r" in scenario else visibility
            if r["omit_last_block"]:
                p0 = scenario.get("control_p0", 0.5)
            elif r.get("readout", "X") == "Y":
                p0 = 0.5 - 0.5 * omega * g * math.sin(scenario.get("walk_phase", 0.0))
            else:
                p0 = 0.5 + 0.5 * omega * g * math.cos(scenario.get("walk_phase", 0.0))
            model[r["roles"]["control"]] = 1 - p0
            continue
        model.update(lcu_model(r, scenario, visibility))
    return model


def write_run(root: Path, family: str, batch: str, shots: dict[str, list[str]], failed: dict[str, str]) -> Path:
    source = CASES / FAMILIES[family] / batch
    run = root / "results/quantum_inspire/runs" / f"synthetic-{family}-{batch}"
    (run / "raw").mkdir(parents=True)
    manifest = json.loads((source / "cases.json").read_text(encoding="utf-8"))
    for name in ["cases.json", *(row["file"] for row in manifest["circuits"])]:
        shutil.copyfile(source / name, run / name)
    batch_job = int(sha256(f"{family}/{batch}".encode())[:6], 16)
    jobs, submitted = [], []
    # Jobs finish 10 s apart within a batch and batches 600 s apart, in batch order.
    start = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=600 * int(batch.rsplit("-", 1)[1]))
    for index, row in enumerate(manifest["circuits"]):
        file = row["file"]
        job_id = batch_job * 10 + index
        state = "failed" if file in failed else "completed"
        results = [] if file in failed else [{"shots_requested": manifest["shots"], "shots_done": manifest["shots"]}]
        finished = (start + timedelta(seconds=10 * index)).isoformat().replace("+00:00", "Z")
        jobs.append({"file": file, "job": {"id": job_id, "batch_job_id": batch_job, "status": state,
                     "message": failed.get(file, ""), "finished_at": finished}, "results": results,
                     "logs": None})  # fmt: skip
        submitted.append({"file": file, "job": job_id, "sha256": row["sha256"]})
        if file not in failed:
            (run / "raw" / f"{file}.json").write_text(json.dumps(shots[file]), encoding="utf-8")
    (run / "results.json").write_text(json.dumps({"schema": "qi-collection-v1", "jobs": jobs}), encoding="utf-8")
    receipt = {"schema": SUBMISSION_SCHEMA, "state": "enqueued", "backend": manifest["backend"],
               "backend_type_id": manifest["backend_type_id"], "shots": manifest["shots"],
               "cases_sha256": sha256((run / "cases.json").read_bytes()), "batch_job": batch_job,
               "jobs": submitted}  # fmt: skip
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
                readout = {
                    **scenario.get("readout", {}),
                    **scenario.get("batch_readout", {}).get(f"{family}/{entry['batch']}", {}),
                }
                if family.startswith("ry"):
                    jobs.append((family, entry["batch"], file, ry_item(seed, manifest, row, scenario), failures))
                    continue
                item: Any
                if row["kind"] == "readout" and "excited" in row:
                    model = {q: float(q in row["excited"]) for q in range(width)}
                    item = (seed, width, n, model, {**readout, **scenario.get(f"readout_{file}", {})})
                elif row["kind"] == "readout":
                    model = {q: float(row["prepared"]) for q in range(width)}
                    item = (seed, width, n, model, {**readout, **scenario.get(f"readout_{file}", {})})
                elif family == "tuna_pre" or row.get("ideal_p1") == "0":
                    model = {q: 0.0 for q in range(width)}
                    item = (seed, width, n, model, {**readout, **scenario.get("xx", {})})
                elif "line" in scenario and family == "tuna_ladder":
                    item = ("line", seed, width, n, line_groups(row, scenario), readout, scenario["line"])
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


def line_groups(row: dict[str, Any], scenario: dict[str, Any]) -> list[tuple[int, int, list[float], float, int]]:
    """Per LCU replica: selector, data, the ideal joint (a, d) distribution, its depolarizing decay and depth."""
    ideal_scenario = {**scenario, "amplitude": 1.0, "r": 1.0}
    out = []
    for r in row["replicas"]:
        ((a, d), ideal), *_ = lcu_model(r, ideal_scenario, 1.0).items()
        decay = scenario.get("amplitude", SYN_VISIBILITY) * scenario.get("r", 1.0) ** r["cz_depth"]
        out.append((a, d, ideal, decay, r["cz_depth"]))
    return out


def line_shots(item: Any) -> list[str]:
    """Shots whose depolarizing decay oscillates at f cycles per shot with relative depth depth / 9 times m."""
    _, seed, width, n, groups, readout, (frequency, modulation) = item
    rng = np.random.default_rng(seed)
    true = np.zeros((n, width), dtype=np.uint8)
    wave = np.cos(2 * np.pi * frequency * np.arange(n))
    for a, d, ideal, decay, depth in groups:
        lam = np.minimum(1.0, decay * (1 + modulation * depth / 9 * wave))
        joint = lam[:, None] * np.asarray(ideal)[None, :] + (1 - lam[:, None]) / 4
        outcome = np.minimum((np.cumsum(joint, axis=1) < rng.random(n)[:, None]).sum(axis=1), 3)
        true[:, a], true[:, d] = outcome >> 1, outcome & 1
    rates = np.array([readout.get(q, (SYN_E01, SYN_E10)) for q in range(width)])
    flip = rng.random((n, width)) < np.where(true == 0, rates[:, 0], rates[:, 1])
    text = ((true ^ flip)[:, ::-1] + 48).astype(np.uint8).tobytes().decode("ascii")
    return [text[s * width : (s + 1) * width] for s in range(n)]


def synthesize(item: Any) -> list[str]:
    """Pool worker: shots of one synthetic circuit (Tuna items from synthetic_shots, Ry items leftmost)."""
    if item[0] == "line":
        return line_shots(item)
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
# Follow model: global depolarizing at T0's amplitude and decay, lambda(1) = 0.78, whose depth-1 conditional
# |E_X| = 2 lambda / (1 + lambda) = 0.876 lies inside the cross-prediction band of 0.954, and walk magnitudes
# r^n_CZ at T0's r.
FOLLOW_MODEL = {"amplitude": 0.821, "r": 0.95, "walk_r": 0.9654}
FOLLOW_ONLY = {"families": ["tuna_follow"], "readout": {}, **FOLLOW_MODEL}
# Ladder model: the follow model's depolarizing decay, with a line at the follow series' 0.020036 cycles per
# shot that modulates the decay by 0.3 n / 9 at CZ depth n, and readout-1 alone overstating q13's e10.
LADDER_FAMILIES = ("tuna_ladder", "tuna_ladder_twins")
LADDER_ONLY = {"families": ["tuna_ladder"], "readout": {}, "amplitude": 0.821, "r": 0.95}
LADDER_LINE = (0.020036, 0.3)
# 0.4 rad per CZ puts depth 9 at 3.6 rad, past the atan2 branch cut, so the phase fit must unwrap.
INJECTED_PHASE = 0.4
SCENARIOS: dict[str, dict[str, Any]] = {
    "pass": {
        "families": [f for f in FAMILIES if f not in ("tuna_twins", *LADDER_FAMILIES)], "readout": FAULT,
        "xx": UNDER_ROTATION_XX,
        **FOLLOW_MODEL,
        "ry_failed": {"r9-teleport-bare.cq": "Quantum backend error: error interpreting cQASM script"},
    },
    "twins": {"families": ["tuna_twins"], "readout": IDEAL_QX, "visibility": 1.0},
    "twins_refuted": {"families": ["tuna_twins"], "readout": IDEAL_QX, "visibility": 0.995},
    "t0_end": {"families": ["tuna_t0", "tuna_follow"], "readout": {}, "amplitude": 0.316, "r": 0.95},
    "t0_resize": {"families": ["tuna_t0", "tuna_follow"], "readout": {}, "amplitude": 0.975, "r": 0.80},
    "follow_twist": {**FOLLOW_ONLY, "twist_shift": 0.06},
    "follow_drift": {**FOLLOW_ONLY, "batch_readout": {"tuna_follow/batch-03": {13: (0.02, 0.10)}}},
    "follow_coherence": {**FOLLOW_ONLY, "coherence_flipped": True},
    "follow_walk": {**FOLLOW_ONLY, "walk_sign_flipped": True},
    "follow_strut": {**FOLLOW_ONLY, "strut_shift": 0.16},
    "follow_phase": {**FOLLOW_ONLY, "phase_per_cz": INJECTED_PHASE},
    "follow_omit": {**FOLLOW_ONLY, "control_p0": 0.8},
    "pre_recovered": {"families": ["tuna_pre"], "readout": {**HEALTHY, 13: (0.02, 0.3)}, "xx": {}},
    "pre_misassignment": {"families": ["tuna_pre"], "readout": FAULT, "xx": MISASSIGNMENT_XX},
    "ry_gate": {"families": ["ry_ladder", "ry_smoke"],
                "ry_failed": {"r1-width-9.cq": "Quantum backend error: error interpreting cQASM script"}},
    "ladder": {**LADDER_ONLY, "line": LADDER_LINE, "readout_readout-1.cq": {13: (0.02, 0.10)}},
    "ladder_flat": {**LADDER_ONLY},
    "ladder_context_low": {**LADDER_ONLY, "readout_readout-iso-x.cq": {13: (0.02, 0.4)}},
    "ladder_twins": {"families": ["tuna_ladder_twins"], "readout": IDEAL_QX, "visibility": 1.0},
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

        def refuted_only(stage: dict[str, Any], marker: str) -> bool:
            """A refutation verdict whose list names the marker and which stops nothing."""
            return (
                stage["verdict"] == "refuted"
                and not stage["stops"]
                and any(marker in entry for entry in stage["refutations"])
            )

        def stages(name: str) -> dict[str, Any]:
            return analyze(runs[name], root / name)["stages"]

        good = stages("pass")
        pre = good["tuna_pre"]
        check(pre["precondition"] == "fault-present" and pre["decision"] == "under-rotation", "pre under-rotation")
        check(pre["readmission"]["9"].startswith("excluded"), "q9 idle misassignment keeps q9 out")
        check(pre["readmission"]["5"].endswith("visibility exclusion stands"), "q5 keeps its visibility exclusion")
        check(pre["verdict"] == "continue", f"pre stops: {pre['stops']}")
        t0 = good["tuna_t0"]
        check(
            t0["verdict"] == "continue" and t0["r_verdict"] == "inside the decision band [0.87, 0.97]",
            f"t0: {t0['stops']}",
        )
        check(t0["r_prediction"] == [0.87, 0.96] and t0["r_in_prediction"], "r 0.95 lies inside its prediction")
        check(good["tuna_follow"]["t0_gate"] == "passed", f"follow T0 gate: {good['tuna_follow']['t0_gate']}")
        check(t0["r_interval"][0] <= 0.95 <= t0["r_interval"][1], f"t0 r interval {t0['r_interval']} misses 0.95")
        check(t0["c1_in_prediction"], f"t0 C(1) {t0['contrast']['1']}")
        follow = good["tuna_follow"]
        check(
            follow["verdict"] == "continue" and not follow["refutations"],
            f"follow stops {follow['stops']}, refutations {follow['refutations']}",
        )
        check(not follow["brackets"]["problems"] and len(follow["brackets"]["batches"]) == 3, "follow brackets")
        check(all(c["verdict"] == "classified" for c in follow["classification"]), "follow classification")
        check(len(follow["classification"]) == 6, "edge on three pairs, twist on two, strut on one")
        check(all(x["verdict"] == "consistent" for x in follow["twist"]) and len(follow["twist"]) == 4, "twist")
        check(not any(x["bias_flag"] for x in follow["strut"]), "a strut bias flag without a bias")
        x_depth_1 = [c for c in follow["coherence"] if c["verdict"] in ("supported", "unresolved", "refuted")]
        check(
            len(x_depth_1) == 10 and all(c["verdict"] == "supported" for c in x_depth_1),
            f"coherence X signs {[(c['file'], c['slot'], c['verdict']) for c in x_depth_1]}",
        )
        check(all(c["cross_prediction"]["inside"] for c in x_depth_1), "depth-1 |E_X| inside the C(1) band")
        check(
            all(c["verdict"] == "consistent" for c in follow["coherence"] if c["label"].startswith("strut")),
            "strut coherence bound",
        )
        check(
            sorted(w["verdict"][:9] for w in follow["walks"])
            == ["consisten", "consisten", "reported:", "reported:", "supported", "supported"],
            f"walk verdicts {[w['verdict'] for w in follow['walks']]}",
        )
        check(all(w["inside"] for w in follow["walk_pairs"]), "walk magnitudes inside r^n_CZ")
        for entry in follow["depth_ladder"]:
            low, high = entry["phase_slope_per_cz"]["interval"]
            check(low <= 0 <= high, f"pair {entry['pair']} phase slope interval {low, high} misses 0")
            # Global depolarizing at r = 0.95 per CZ: J(n) and 2 Pc(n) - 1 both decay as r^n.
            for key, value in (("r_coh", 0.95), ("r_pop", 0.95), ("r_coh_over_r_pop", 1.0)):
                low, high = entry[key]["interval"]
                check(low <= value <= high, f"pair {entry['pair']} {key} interval {low, high} misses {value}")
        drifts = [r for r in follow["replication"] if "drift" in r]
        check(
            len(drifts) == 4
            and len(follow["replication"]) == 6
            and all(abs(r["drift"]) < 5 * r["drift_se"] for r in drifts),
            "replication against T0's four bright depth-5 and depth-9 cells",
        )
        ladder = good["ry_ladder"]
        check([c["verdict"] for c in ladder["circuits"]][:2] == ["conforms", "conforms"], "ry ladder R1, R2")
        check(ladder["circuits"][2]["verdict"].startswith("failed") and ladder["verdict"] == "continue", "ry R9")
        check(good["ry_smoke"]["verdict"] == "continue", f"ry smoke: {good['ry_smoke']['stops']}")

        ended_stages = stages("t0_end")
        ended = ended_stages["tuna_t0"]
        ended_follow = ended_stages["tuna_follow"]
        check(
            ended_follow["verdict"] == "stop"
            and ended_follow["stops"][0] == "T0 gate: the depth-1 bound ended the Tuna program"
            and ended_follow["classification"],
            f"a T0 end-program stop left the follow series running or unestimated: {ended_follow['stops'][:2]}",
        )
        check(any(s.startswith("end the Tuna-17 program") for s in ended["stops"]), f"t0 end: {ended['stops']}")
        check(any(s.startswith("sanity stop") for s in ended["stops"]), "the bright floor stops a C(1) 0.3 batch")
        resized_stages = stages("t0_resize")
        resized = resized_stages["tuna_t0"]
        check(
            resized["r_verdict"] == "outside the decision band [0.87, 0.97]" and not resized["r_in_prediction"],
            f"t0 resize: {resized['r_verdict']}",
        )
        resized_follow = resized_stages["tuna_follow"]
        check(
            resized_follow["verdict"] == "stop"
            and resized_follow["stops"][0] == "T0 gate: resize before running"
            and resized_follow["walks"],
            f"a T0 resize left the follow series running or unestimated: {resized_follow['stops'][:2]}",
        )
        check(
            not any(s.startswith("sanity stop") for s in resized["stops"]),
            f"the bright floor reads depth 1 only, yet a low depth-9 bright replica stopped T0: {resized['stops']}",
        )
        twisted = stages("follow_twist")["tuna_follow"]
        check(
            [x["verdict"] for x in twisted["twist"]] == ["refuted", "refuted", "consistent", "consistent"]
            and refuted_only(twisted, "twist equality refuted"),
            f"a 0.06 twist shift in the bright block: {[x['verdict'] for x in twisted['twist']]}",
        )
        drifted = stages("follow_drift")["tuna_follow"]
        check(
            sum("q13 moved" in p for p in drifted["brackets"]["problems"]) == 2
            and any(s.startswith("bracket stop: q13 moved") for s in drifted["stops"])
            and drifted["verdict"] == "stop",
            f"a 0.04 e10 drift at the middle bracket: {drifted['brackets']['problems']}",
        )
        flipped = stages("follow_coherence")["tuna_follow"]
        check(
            sum(c["verdict"] == "refuted" for c in flipped["coherence"]) == 10 and refuted_only(flipped, "E_b refutes"),
            "coherence sign refutation",
        )
        walked = stages("follow_walk")["tuna_follow"]
        check(
            sorted(w["verdict"] for w in walked["walks"] if w["readout"] == "X" and not w["omit_last_block"])
            == ["refuted", "refuted"]
            and any("<X_c> refutes" in entry for entry in walked["refutations"])
            # A flipped X walk also leaves the raw P(c = 1) floor, a sanity stop.
            and walked["verdict"] == "stop"
            and any(re.match(r"sanity stop at batch-\d\d: walk-x\.cq walk ", entry) for entry in walked["stops"]),
            f"walk sign refutation: {walked['stops']}",
        )
        biased = stages("follow_strut")["tuna_follow"]
        check(
            all(x["bias_flag"] for x in biased["strut"])
            and all(c["class"] == "strut" for c in biased["classification"] if c["row"] == "strut")
            and refuted_only(biased, "pair-dependent bias"),
            f"a strut bias above 0.1 + 3 SE left the follow series running: {biased['strut']}",
        )
        phased = stages("follow_phase")["tuna_follow"]
        for entry in phased["depth_ladder"]:
            low, high = entry["phase_slope_per_cz"]["interval"]
            check(low <= INJECTED_PHASE <= high, f"pair {entry['pair']} phase slope {low, high} misses the injection")
        check(phased["verdict"] == "continue", f"a phase per CZ stops or refutes: {phased['refutations']}")
        ladder = stages("ladder")["tuna_ladder"]
        check(ladder["verdict"] == "continue", f"ladder stops {ladder['stops']}, refutations {ladder['refutations']}")
        check(len(ladder["line"]) == 12 and all(e["detected"] for e in ladder["line"]), "a ladder job lost its line")
        check(all(e["depth_growth"]["holds"] for e in ladder["line"]), "the injected line does not grow with depth")
        check(all(e["phase_resultant"] > 0.99 for e in ladder["line"]), "the injected line is not common-mode")
        check(len(ladder["within_batch_ladder"]) == 12, "three pairs in four Latin batches")
        for decision in ladder["rho_decisions"]:
            # Global depolarizing at r = 0.95: J(n) and 2 Pc(n) - 1 decay alike, so rho = 1. The overstated q13
            # e10 adds an offset to the corrected E_0 on (10, 13), which the slope of ln J does not cancel.
            if decision["pair"] != [10, 13]:
                check(decision["verdict"] in ("consistent with 1", "replicate-split"), f"rho decision {decision}")
        for rung in ladder["within_batch_ladder"]:
            if rung["setting"] == "X" and rung["pair"] != [10, 13]:
                rho = rung["rho"]
                check(abs(rho["value"] - 1) < 4 * rho["se"], f"{rung['batch']} {rung['pair']} rho {rho}")
        for rung in ladder["within_batch_ladder"]:
            low, high = rung["r_pop"]["interval"]
            check(low <= 0.95 <= high, f"{rung['batch']} {rung['pair']} r_pop {low, high} misses 0.95")
        for entry in ladder["readout_context"]:
            # readout-1 alone overstates q13's e10 by 0.04; q1 and q14 read alike in every context.
            want = "established" if entry["qubit"] == 13 else "absent"
            check(entry["neighbor_context"]["verdict"] == want, f"q{entry['qubit']} context: {entry}")
            check(entry["preparation_path"]["verdict"] == "absent", f"preparation without a cause: {entry}")
        check(len(ladder["witness_cross_check"]) == 4, "the cross-check needs two pairs in both X Latin batches")
        check(all(c["iso_within_unit"] for c in ladder["witness_cross_check"]), "iso-corrected E_0 beyond 1")
        flat = stages("ladder_flat")["tuna_ladder"]
        check(
            flat["verdict"] == "refuted" and not flat["stops"] and len(flat["refutations"]) == 12,
            f"i.i.d. shots carry a line: {flat['refutations']}",
        )
        low = runs["ladder_context_low"]
        first = analyze([run for run in low if run.name.endswith("batch-00")], root / "ladder_context_low")
        partial = first["stages"]["tuna_ladder"]
        check(
            partial["verdict"].startswith("incomplete") and any("readout-iso-x.cq q13" in s for s in partial["stops"]),
            f"a context readout below its floor did not stop the incomplete series: {partial['stops']}",
        )
        ladder_twins = stages("ladder_twins")["tuna_ladder_twins"]
        check(ladder_twins["verdict"] == "continue", f"ideal ladder twins: {ladder_twins['stops']}")
        omitted = stages("follow_omit")["tuna_follow"]
        check(
            [w["verdict"] for w in omitted["walks"] if w["omit_last_block"]] == ["refuted", "refuted"]
            and refuted_only(omitted, "<X_c> refutes"),
            "an omit-last control above its bound passed",
        )
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
        check(
            any(c["check"] == "p_data_zero_given_selector_one" and c["verdict"] == "pass" for c in twins["checks"]),
            "the selector-1 conditional twin check was not judged",
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
            partial_twins["missing_batches"] == ["batch-01", "batch-02", "batch-03", "batch-05", "batch-06"]
            and partial_twins["verdict"] == "continue",
            "twin batches are judged one by one",
        )
        ry = stages("ry_stopped")
        check(ry["ry_ladder"]["verdict"] == "stop" and ry["ry_smoke"]["verdict"] == "stop", "ry stop rules")
        gated = stages("ry_gate")["ry_smoke"]
        check(
            gated["verdict"] == "stop"
            and gated["stops"] == ["ladder gate: R1 failed, which stops the Ry smoke subset"],
            f"an R1 failure left the smoke subset running: {gated['stops']}",
        )
        lone_smoke = analyze([r for r in runs["pass"] if "ry_smoke" in r.name], root / "pass")["stages"]["ry_smoke"]
        check(lone_smoke["ladder_gate"].startswith("unverified"), "smoke alone read the ladder gate as passed")
        check(good["ry_smoke"]["ladder_gate"] == "passed: R1 completed", "the passed ladder gate is not recorded")
        for r in good["ry_smoke"]["replicas"]:
            u = r["p_zero_uncertainty"]
            check(u["wilson95"][0] <= r["p_zero"] <= u["wilson95"][1] and u["se"] >= 0, "Ry smoke uncertainty")
            if "ideal_fraction" in r:
                w = r["ideal_fraction_uncertainty"]["wilson95"]
                check(w[0] <= r["ideal_fraction"] <= w[1], "Ry ideal-fraction interval")
        for c in good["ry_ladder"]["circuits"]:
            if c["status"] == "completed":
                check("stray_fraction" in c and all("wilson95" in o for o in c["outcomes"].values()), "Ry ladder")
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
        # Each pooled follow row carries the bits of follow_values on that row alone, the scalar reference.
        loaded = [load_batch(run, root / "pass") for run in runs["pass"]]
        follow_batches, _ = stage_batches([b for b in loaded if b["family"] == "tuna_follow"], "tuna_follow", CASES)
        t = thresholds_of(follow_batches)
        brackets = follow_brackets(follow_batches)
        lcu, walks = follow_items(follow_batches, brackets)
        drawn = follow_sample(brackets, lcu, walks, np.random.default_rng(t["bootstrap_seed"]), t["bootstrap_draws"])
        pooled = pooled_follow_values(drawn, lcu, walks)
        for row in (0, FOLLOW_BLOCK_DRAWS - 1, FOLLOW_BLOCK_DRAWS, t["bootstrap_draws"] - 1):
            alone = follow_values(sample_rows(drawn, row, row + 1), lcu, walks)
            same = all(
                pooled[kind][key][row : row + 1].tobytes() == alone[kind][key].tobytes()
                for kind in ("pc", "e", "walk")
                for key in (pooled[kind] if kind == "e" else range(len(pooled[kind])))
            )
            check(same, f"pooled follow row {row} differs from follow_values on that row")
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
        expect_exit(
            "a batch without its readout-1 job",
            lambda: load_batch(run, mutation_root(run)),
            "results.json jobs name other circuit files",
        )

        def swap_job_ids(r: Path) -> None:
            def edit(receipt: dict[str, Any]) -> dict[str, Any]:
                jobs = receipt["jobs"]
                jobs[0]["job"], jobs[1]["job"] = jobs[1]["job"], jobs[0]["job"]
                return receipt

            rewrite(r / "submission.json", edit)

        for label, edit, reason in (
            ("a missing receipt", lambda r: (r / "submission.json").unlink(), "no submission.json receipt"),
            ("a swapped job id", swap_job_ids, "differs from the receipt's"),
            (
                "a foreign batch id",
                lambda r: rewrite(r / "submission.json", lambda c: {**c, "batch_job": c["batch_job"] + 1}),
                "batch job differs from the receipt",
            ),
        ):
            run = mutated(edit)
            expect_exit(label, lambda r=run: load_batch(r, mutation_root(r)), reason)
        ry_source = next(r for r in runs["pass"] if r.name.endswith("ry_ladder-batch-00"))
        cancelled = root / "mutations" / "cancelled" / "results/quantum_inspire/runs" / ry_source.name
        shutil.copytree(ry_source, cancelled)
        rewrite(
            cancelled / "results.json",
            lambda c: {
                **c,
                "jobs": [
                    {**j, "job": {**j["job"], "status": "cancelled"}} if j["file"] == "r9-teleport-bare.cq" else j
                    for j in c["jobs"]
                ],
            },
        )
        expect_exit("a cancelled Ry job", lambda: load_batch(cancelled, cancelled.parents[3]), "job cancelled")
        mutations += 1
        lone = analyze([r for r in runs["pass"] if "tuna_follow" in r.name], root / "pass")["stages"]["tuna_follow"]
        check(lone["t0_gate"] == "unverified: T0 runs not analyzed in this call", "follow alone read the T0 gate")
        check("undetermined" in lone["replication"], "follow alone replicated T0")
        early = analyze(
            [r for r in runs["follow_drift"] if r.name.endswith(("batch-00", "batch-01", "batch-02", "batch-03"))],
            root / "follow_drift",
        )["stages"]["tuna_follow"]
        check(
            early["verdict"].startswith("incomplete")
            and any(s.startswith("bracket stop: q13") for s in early["stops"]),
            "the bracket rule judges a partial follow series",
        )
        for last in ("batch-02", "batch-05"):
            head = [r for r in runs["pass"] if "tuna_follow" in r.name and r.name[-8:] <= last]
            partial_follow = analyze(head, root / "pass")["stages"]["tuna_follow"]
            check(
                partial_follow["verdict"].startswith("incomplete")
                and not any(s.startswith("bracket stop") for s in partial_follow["stops"]),
                f"a follow series through {last} read a bracket stop: {partial_follow['stops']}",
            )
        follow_source = next(r for r in runs["pass"] if r.name.endswith("tuna_follow-batch-01"))
        unstamped = root / "mutations" / "unstamped" / "results/quantum_inspire/runs" / follow_source.name
        shutil.copytree(follow_source, unstamped)
        rewrite(
            unstamped / "results.json",
            lambda c: {
                **c,
                "jobs": [{**j, "job": {k: v for k, v in j["job"].items() if k != "finished_at"}} for j in c["jobs"]],
            },
        )
        expect_exit(
            "a follow job without finished_at", lambda: load_batch(unstamped, unstamped.parents[3]), "finished_at"
        )
        mutations += 1

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
