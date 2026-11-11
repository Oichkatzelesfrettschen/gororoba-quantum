"""Shared readers and analytic statistics for the IBM Heron r2 residual-structure scans.

Run every script from the repository root with the repository interpreter:

    GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 \
      systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 "$PYTHON" SCRIPT

Reader contract (the retained raw layout `results/live/<run>/raw/<job>/`):

- `pub_NN.json` holds `registers.<name>.bitstrings`, one string per shot in the returned order; the
  character at string position `-1 - b` is classical bit `b`. `load_pub` checks each file against the
  sha256 that the job's `index.json` lists under `files`, the same custody rule as
  `n21_exact_planning.retained_registers`. That function drops the per-PUB metadata (scheduler timing) and the
  job identity that the timing model needs, so `load_pub` repeats its digest rule per file;
  `reader_crosscheck.py` confirms every register of four runs (104 registers) is identical in both readers.
- `result_metadata.json` key `executor.chunk_timing` goes through `adjudicate.pub_chunks`.
- `job_metrics.json` key `circuits_execution_time_ns` is the service's execution time.

Timing model. IBM documents column-wise execution (docs/notes/ibm_quantum/repetition-rate-execution.md):
the circuits of a job run in PUB order for shot 0, then in PUB order for shot 1. Consecutive shots of
one PUB are therefore `slot_s = sum over the job's PUBs of (rep_delay + circuit_duration_dt * dt)` apart.
The documented order is not guaranteed, and the raw record carries only chunk start and stop times, so
every frequency in Hz is a conversion of a list-position frequency under that documented reading.
`catalog` gates the reading per job: the predicted execution time must equal
`circuits_execution_time_ns` within 1 percent.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path.cwd()
if not (ROOT / "gororoba_quantum").is_dir():
    raise SystemExit("run from the repository root")
sys.path[:0] = [str(ROOT / "gororoba_quantum"), str(ROOT / "scripts")]
import adjudicate  # noqa: E402
from parallel import ordered_map  # noqa: E402,F401

LIVE = ROOT / "results/live"
OUT = ROOT / "docs/evidence/hardware-residuals/ibm"
DT = 4e-9
DEFAULT_REP_DELAY = 2.5e-4
CATALOG = OUT / "catalog.json"


def rel(path: Path | str) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def finite(obj: Any) -> Any:
    """Replace non-finite floats so the files are standard JSON.

    -inf -> -300 (a log10 p-value floor), +inf -> 300, nan -> null.
    """
    if isinstance(obj, (float, np.floating)):
        value = float(obj)
        if math.isnan(value):
            return None
        if math.isinf(value):
            return -300.0 if value < 0 else 300.0
        return value
    if isinstance(obj, dict):
        return {k: finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [finite(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return finite(obj.tolist())
    return obj


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(finite(obj), indent=1, sort_keys=True, default=_default) + "\n")


def write_json_gz(path: Path, obj: Any) -> None:
    with gzip.open(path, "wt", compresslevel=6) as handle:
        json.dump(finite(obj), handle, default=_default, separators=(",", ":"))


def _default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value))


# --- retained records ---------------------------------------------------------------------


def run_dirs() -> list[Path]:
    """Every results/live run directory that retains shot-ordered PUB files (64 at the time of writing)."""
    return sorted({p.parent.parent.parent for p in LIVE.glob("*/raw/*/pub_*.json")})


_INDEX_CACHE: dict[str, dict[str, str]] = {}


def job_index(job: Path) -> dict[str, str]:
    key = str(job)
    if key not in _INDEX_CACHE:
        _INDEX_CACHE[key] = json.loads((job / "index.json").read_text())["files"]
    return _INDEX_CACHE[key]


def load_pub_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    digest = job_index(path.parent).get(path.name)
    if digest is None or hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError(f"{path} differs from its indexed digest")
    return json.loads(payload)


def decode(bitstrings: list[str], nbits: int) -> np.ndarray:
    """(shots, nbits) uint8 matrix, column b = classical bit b (string position -1 - b)."""
    n = len(bitstrings)
    flat = np.frombuffer("".join(bitstrings).encode("ascii"), dtype=np.uint8)
    if flat.size != n * nbits:
        raise ValueError("bitstring width differs from num_bits")
    matrix = flat.reshape(n, nbits)
    if not np.all((matrix == 48) | (matrix == 49)):
        raise ValueError("non-binary bitstring")
    return (matrix[:, ::-1] - 48).astype(np.uint8)


def load_pub(path: Path | str) -> dict[str, Any]:
    """PUB name, index and {register: (shots, bits) uint8 matrix} for one digest-checked PUB file."""
    path = Path(path)
    raw = load_pub_json(path)
    regs = {name: decode(entry["bitstrings"], entry["num_bits"]) for name, entry in raw["registers"].items()}
    timing = raw.get("metadata", {}).get("compilation", {}).get("scheduler_timing", {})
    return {
        "name": raw["pub_name"],
        "index": raw["pub_index"],
        "regs": regs,
        "dur_dt": timing.get("circuit_duration"),
        "path": rel(path),
    }


def _parse_time(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _catalog_job(job_str: str) -> dict[str, Any]:
    job = Path(job_str)
    run = job.parent.parent
    meta = json.loads((job / "result_metadata.json").read_text())
    metrics = json.loads((job / "job_metrics.json").read_text())
    rep = meta.get("options", {}).get("execution", {}).get("rep_delay")
    pubs = []
    for path in sorted(job.glob("pub_*.json")):
        raw = load_pub_json(path)
        timing = raw.get("metadata", {}).get("compilation", {}).get("scheduler_timing", {})
        regs = {name: [e["num_bits"], e["num_shots"]] for name, e in raw["registers"].items()}
        pubs.append(
            {
                "file": rel(path),
                "index": raw["pub_index"],
                "name": raw["pub_name"],
                "regs": regs,
                "shots": max(v[1] for v in regs.values()),
                "dur_dt": timing.get("circuit_duration"),
            }
        )
    rep_used = DEFAULT_REP_DELAY if rep is None else float(rep)
    slot_s = sum(rep_used + p["dur_dt"] * DT for p in pubs)
    predicted_ns = sum(p["shots"] * (rep_used + p["dur_dt"] * DT) for p in pubs) * 1e9
    exec_ns = metrics.get("circuits_execution_time_ns")
    windows = adjudicate.pub_chunks(meta, max(p["index"] for p in pubs) + 1)
    chunks = [[[a.isoformat(), b.isoformat()] for a, b in windows[p["index"]]] for p in pubs]
    return {
        "run": rel(run),
        "job": job.name,
        "rep_delay_s": rep_used,
        "rep_delay_from_metadata": rep is not None,
        "exec_ns": exec_ns,
        "predicted_over_exec": None if not exec_ns else predicted_ns / exec_ns,
        "slot_s": slot_s,
        "equal_shots": len({p["shots"] for p in pubs}) == 1,
        "n_chunks": len(meta.get("executor", {}).get("chunk_timing") or []),
        "pub_chunk_windows": chunks,
        "running": metrics.get("timestamps", {}).get("running"),
        "pubs": pubs,
    }


def build_catalog() -> dict[str, Any]:
    jobs = [str(j) for run in run_dirs() for j in sorted((run / "raw").glob("*/")) if list(j.glob("pub_*.json"))]
    entries = ordered_map(_catalog_job, jobs, min_items=1)
    runs: dict[str, Any] = {}
    for run in run_dirs():
        record_path = run / "record.json"
        record = json.loads(record_path.read_text()) if record_path.exists() else None
        info: dict[str, Any] = {"record": record is not None, "backends": {}, "schema": None}
        if record:
            info["schema"] = record.get("schema_version")
            for name, value in (record.get("backends") or {}).items():
                info["backends"][name] = value.get("calibration")
            info["pub_backend"] = {e["name"]: e.get("backend") for e in record.get("execution_pubs") or []}
            fc = record.get("family_configuration")
            info["family"] = fc.get("name") if isinstance(fc, dict) else fc
        runs[rel(run)] = info
    for entry in entries:
        info = runs[entry["run"]]
        names = {p["name"] for p in entry["pubs"]}
        backs = {info.get("pub_backend", {}).get(n) for n in names} - {None}
        if len(backs) == 1:
            entry["backend"] = backs.pop()
        elif not backs and len(info["backends"]) == 1:
            entry["backend"] = next(iter(info["backends"]))
        elif not backs and not info["record"]:
            entry["backend"] = "ibm_kingston"  # directory name kingston-wide-control-result; no record.json
        else:
            entry["backend"] = None
    return {
        "dt_s": DT,
        "n_runs": len(runs),
        "n_jobs": len(entries),
        "n_pubs": sum(len(e["pubs"]) for e in entries),
        "runs": runs,
        "jobs": entries,
    }


def catalog() -> dict[str, Any]:
    if CATALOG.exists():
        return json.loads(CATALOG.read_text())
    cat = build_catalog()
    write_json(CATALOG, cat)
    return cat


def job_of(cat: dict[str, Any], pub_file: str) -> dict[str, Any]:
    for job in cat["jobs"]:
        if any(p["file"] == pub_file for p in job["pubs"]):
            return job
    raise KeyError(pub_file)


# --- ground-prepared selections -----------------------------------------------------------

ACTOR_RUN = "results/live/2026-10-29T191606.826758Z"


def record_of(run: str) -> dict[str, Any] | None:
    path = ROOT / run / "record.json"
    return json.loads(path.read_text()) if path.exists() else None


def state_prep_columns(run: str) -> list[dict[str, Any]]:
    """Per PUB of a state-prep-control run: arm, and (register, bit, physical qubit) of every ground-prepared read.

    prep0 is (init, measure): bit 0 of every register is a ground-prepared read. x_history is (init, measure,
    x): the measured bit is the ground-prepared read before the x. remeasure is (init, measure, measure):
    bit 0 is the ground-prepared first read. x_remeasure starts from x and is excluded.
    """
    record = record_of(run)
    if not record or not isinstance(record.get("family_configuration"), dict):
        return []
    if record["family_configuration"].get("name") != "state-prep-control":
        return []
    out = []
    for pub in record["execution_pubs"]:
        cols = []
        arm = None
        for comp in pub["components"]:
            member = comp["member"]
            for prefix in ("spc_prep0_", "spc_x_history_", "spc_remeasure_", "spc_x_remeasure_"):
                if member.startswith(prefix):
                    arm = prefix[4:-1]
            if arm == "x_remeasure":
                continue
            (register,) = comp["registers_by_replica"][0]
            (qubit,) = comp["physical_qubits"]
            cols.append((register, 0, int(qubit)))
        if arm and arm != "x_remeasure":
            out.append({"pub_name": pub["name"], "arm": arm, "backend": pub["backend"], "columns": cols})
    return out


def pilot_sensor_ids() -> list[int]:
    return [q for q in range(156) if q not in (0, 1, 2)]


def pilot_prepared(pub_file: str) -> np.ndarray:
    """Prepared bit of each of the 156 pilot qubits for one PUB, from its projection manifest."""
    job = (ROOT / pub_file).parent
    raw = load_pub_json(ROOT / pub_file)
    name = raw["pub_name"]
    for path in sorted(job.glob("projection-*.json")):
        digest = path.name[len("projection-") : -len(".json")]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError(f"{path} differs from its content digest")
        manifest = json.loads(payload)
        if manifest["pub_name"] == name:
            prepared = np.zeros(156, dtype=np.uint8)
            for bit in manifest["bits"]:
                if bit["logical"] != bit["index"] or bit["physical"] != bit["index"]:
                    raise ValueError("identity mapping expected")
                prepared[bit["index"]] = bit["prepared"]
            return prepared
    raise KeyError(name)


def coupling_graph(backend: str) -> dict[int, set[int]]:
    """Undirected coupler graph of one backend from docs/evidence/heron_platform/targets.json (cz qargs)."""
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    edges: set[tuple[int, int]] = set()
    for a, b in targets["backends"][backend]["instructions"]["cz"]["qargs"]:
        edges.add((min(a, b), max(a, b)))
    graph: dict[int, set[int]] = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph


def graph_distances(graph: dict[int, set[int]], n: int = 156) -> np.ndarray:
    """All-pairs hop distance by breadth-first search; -1 where unreachable."""
    dist = -np.ones((n, n), dtype=np.int32)
    for s in range(n):
        dist[s, s] = 0
        frontier = [s]
        d = 0
        while frontier:
            d += 1
            nxt = []
            for u in frontier:
                for v in graph.get(u, ()):
                    if dist[s, v] < 0:
                        dist[s, v] = d
                        nxt.append(v)
            frontier = nxt
    return dist


# --- analytic statistics ---------------------------------------------------------------


def log10_fisher_p(c_max: np.ndarray | float, m: int) -> np.ndarray | float:
    """log10 P(max of m iid Exp(1) >= c_max), stable for tiny p (Fisher's g test for a periodogram)."""
    c = np.asarray(c_max, dtype=float)
    single = -c / math.log(10)
    with np.errstate(over="ignore", under="ignore", divide="ignore"):
        small = np.log10(m) + single
        exact = np.log10(-np.expm1(m * np.log1p(-np.exp(-c))))
    return np.where(m * np.exp(-c) < 1e-6, small, exact)


def log10_gamma_sf(x: float, k: int) -> float:
    from scipy.stats import gamma

    return float(gamma.logsf(x, k) / math.log(10))


def log10_poisson_two_sided(observed: int, mean: float) -> float:
    """log10 of the two-sided exact Poisson p-value min(1, 2 min(P(X>=k), P(X<=k)))."""
    from scipy.stats import poisson

    if mean <= 0:
        return 0.0 if observed == 0 else -300.0
    upper = poisson.logsf(observed - 1, mean) / math.log(10)
    lower = poisson.logcdf(observed, mean) / math.log(10)
    return float(min(0.0, math.log10(2) + min(upper, lower)))


def log10_poisson_upper(observed: int, mean: float) -> float:
    from scipy.stats import poisson

    if mean <= 0:
        return 0.0 if observed == 0 else -300.0
    return float(min(0.0, poisson.logsf(observed - 1, mean) / math.log(10)))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    from scipy.stats import beta

    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def garwood(k: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact Poisson interval for a count k."""
    from scipy.stats import chi2

    lo = 0.0 if k == 0 else float(chi2.ppf(alpha / 2, 2 * k) / 2)
    hi = float(chi2.ppf(1 - alpha / 2, 2 * k + 2) / 2)
    return lo, hi


def global_corrections(tests: list[tuple[str, str, float]], alpha: float = 0.05) -> dict[str, Any]:
    """Bonferroni and Benjamini-Hochberg over (id, family, log10 p) tests, in log10 space."""
    n = len(tests)
    if n == 0:
        return {"n_tests": 0}
    order = sorted(range(n), key=lambda i: tests[i][2])
    log_alpha = math.log10(alpha)
    bonf_thr = log_alpha - math.log10(n)
    bh_cut = -1
    for rank, i in enumerate(order, start=1):
        if tests[i][2] <= log_alpha + math.log10(rank) - math.log10(n):
            bh_cut = rank
    return {
        "n_tests": n,
        "alpha": alpha,
        "bonferroni_log10_threshold": bonf_thr,
        "n_bonferroni": sum(1 for _, _, lp in tests if lp <= bonf_thr),
        "n_bh": bh_cut if bh_cut > 0 else 0,
        "_bh_member_ids": [tests[i][0] for i in order[: max(bh_cut, 0)]],
    }


# --- ground-prepared datasets (error matrices) -------------------------------------------------


def ground_datasets(cat: dict[str, Any]) -> list[dict[str, Any]]:
    """Datasets whose ideal outcome is a known 0 on every listed column.

    pilot: the 153 sensor qubits of each of the 24 readout-actor PUBs (error = outcome xor prepared bit, and the
    manifests prepare every sensor in |0>). state_prep: the ground-prepared first read of every qubit in each
    state-prep-control PUB with arm prep0, x_history or remeasure.
    """
    out: list[dict[str, Any]] = []
    for job in cat["jobs"]:
        if job["run"] == ACTOR_RUN:
            for pub in job["pubs"]:
                out.append(
                    {
                        "kind": "pilot",
                        "id": f"pilot:{pub['name']}",
                        "file": pub["file"],
                        "run": job["run"],
                        "job": job["job"],
                        "backend": "ibm_fez",
                        "arm": pub["name"],
                        "n": pub["shots"],
                        "slot_s": job["slot_s"],
                        "pub_in_job": len(job["pubs"]),
                    }
                )
    for run in sorted(cat["runs"]):
        for spec in state_prep_columns(run):
            for job in cat["jobs"]:
                if job["run"] != run:
                    continue
                for pub in job["pubs"]:
                    if pub["name"] == spec["pub_name"]:
                        out.append(
                            {
                                "kind": "state_prep",
                                "id": f"state_prep:{run[-27:]}:{spec['arm']}",
                                "file": pub["file"],
                                "pub_name": pub["name"],
                                "run": run,
                                "job": job["job"],
                                "backend": spec["backend"],
                                "arm": spec["arm"],
                                "columns": spec["columns"],
                                "n": pub["shots"],
                                "slot_s": job["slot_s"],
                                "pub_in_job": len(job["pubs"]),
                                "rep_delay_s": job["rep_delay_s"],
                            }
                        )
    return out


def load_errors(ds: dict[str, Any]) -> tuple[np.ndarray, list[int]]:
    """(shots, Q) uint8 error matrix and the physical qubit of each column."""
    pub = load_pub(ds["file"])
    if ds["kind"] == "pilot":
        measured = pub["regs"]["c"]
        prepared = pilot_prepared(ds["file"])
        ids = pilot_sensor_ids()
        if np.any(prepared[ids] != 0):
            raise ValueError("pilot sensors are expected in |0>")
        return (measured[:, ids] ^ prepared[ids]).astype(np.uint8), ids
    cols = ds["columns"]
    matrix = np.stack([pub["regs"][reg][:, bit] for reg, bit, _ in cols], axis=1)
    return matrix.astype(np.uint8), [q for _, _, q in cols]
