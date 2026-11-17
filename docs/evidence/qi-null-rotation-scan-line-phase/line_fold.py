"""Per-job workers of the shot-order line analyses of the null rotation scan.

Each worker takes one (run directory name, raw file name) of the retained series, reads its ordered shots and
returns a JSON-ready row; the scripts map them through parallel.ordered_map and pool, print and write."""

import json
from datetime import datetime
from typing import Any

import numpy as np
from scan_forward import ROOT, rs

S = "2026-11-15T001929Z"
RUNS = ROOT / "results/quantum_inspire/runs"
BINS = 8
ANGLES = 2 * np.pi * (np.arange(BINS) + 0.5) / BINS
LINE_BAND = (0.02008, 0.02016)
OFF_LINE_BAND = (0.02350, 0.02358)
Job = tuple[str, str]


def data_jobs(arms: tuple[str, ...] | None = None) -> list[Job]:
    """Every data job of the Tuna-17 series in batch and file order, or those of the named arms."""
    out = []
    for d in sorted(RUNS.glob(f"{S}-pathion_null_rotation_scan_tuna_17-batch-*")):
        for f in sorted((d / "raw").iterdir()):
            if f.name.startswith("readout"):
                continue
            if arms is None or arm_of(f.name) in arms:
                out.append((d.name, f.name))
    return out


def arm_of(file_name: str) -> str:
    return str(rs.arm_of(file_name.removesuffix(".json")))


def load(job: Job) -> tuple[list[str], dict[str, int]]:
    directory = RUNS / job[0]
    roles = {
        k: int(v) for k, v in json.loads((directory / "cases.json").read_text())["templates"]["b0"]["roles"].items()
    }
    return json.loads((directory / "raw" / job[1]).read_text()), roles


def bit(shots: list[str], qubit: int) -> np.ndarray:
    return np.array([s[16 - qubit] == "1" for s in shots])


def locate(x: np.ndarray, n: np.ndarray, band: tuple[float, float]) -> tuple[float, float]:
    """Frequency and phase of the largest Fourier amplitude of x over the band (201 points, then 81 around the best)."""
    g = np.linspace(*band, 201)
    z = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g])
    f0 = g[np.abs(z).argmax()]
    g2 = np.linspace(f0 - 4e-7, f0 + 4e-7, 81)
    z2 = np.array([np.sum(x * np.exp(-2j * np.pi * f * n)) for f in g2])
    j = np.abs(z2).argmax()
    return float(g2[j]), float(-np.angle(z2[j]))


def phase_bins(frequency: float, phase: float, index: np.ndarray) -> np.ndarray:
    theta = (2 * np.pi * frequency * index - phase) % (2 * np.pi)
    return np.asarray((theta / (2 * np.pi) * BINS).astype(int) % BINS)


def fold(shots: list[str], index: np.ndarray, roles: dict[str, int], frequency: float, phase: float):
    """Selector contrast of the shots at `index` in the phase bins, its first and second harmonic and their error."""
    b = phase_bins(frequency, phase, index)
    arr = np.array(shots, dtype=object)[index]
    stats = [rs.circuit_statistics(list(arr[b == k]), roles) for k in range(BINS)]
    c = np.array([s["contrast"] for s in stats])
    e = np.array([s["se"] for s in stats])
    h1 = 2 * np.mean(c * np.exp(-1j * ANGLES))
    h2 = 2 * np.mean(c * np.exp(-2j * ANGLES))
    return c, h1, h2, float(np.sqrt(2 * np.mean(e**2) / BINS))


def polar(value: complex) -> list[float]:
    return [float(abs(value)), float(np.angle(value))]


def bins_job(job: Job) -> dict[str, Any]:
    """line_phase_bins.py: the fold of all shots at the phase of q4's bit, and at 0.0237 cycles per shot."""
    shots, roles = load(job)
    x4 = bit(shots, 4).astype(float)
    x4 -= x4.mean()
    n = np.arange(len(x4))
    coarse = np.linspace(*LINE_BAND, 1601)[::8]
    amp = np.array([np.abs(np.sum(x4 * np.exp(-2j * np.pi * fr * n))) for fr in coarse])
    f0 = coarse[amp.argmax()]
    fine = np.linspace(f0 - 4e-7, f0 + 4e-7, 81)
    z = np.array([np.sum(x4 * np.exp(-2j * np.pi * fr * n)) for fr in fine])
    j = np.abs(z).argmax()
    c, h1, h2, se = fold(shots, n, roles, fine[j], -np.angle(z[j]))
    _, g1, g2, _ = fold(shots, n, roles, 0.0237, 0.0)
    return {
        "batch": job[0][-8:],
        "file": job[1],
        "arm": arm_of(job[1]),
        "f": float(fine[j]),
        "q4_amp": float(2 * np.abs(z[j]) / len(x4)),
        "bins": c.round(4).tolist(),
        "h1": polar(h1),
        "h2": polar(h2),
        "se": se,
        "null_h1": float(abs(g1)),
        "null_h2": float(abs(g2)),
        "null_h1_phase": float(np.angle(g1)),
        "null_h2_phase": float(np.angle(g2)),
    }


def split_job(job: Job) -> dict[str, Any]:
    """line_phase_split.py: frequency and phase from the odd-indexed shots, the fold on the even-indexed ones."""
    shots, roles = load(job)
    n = np.arange(len(shots))
    odd, even = n[1::2], n[0::2]
    x = bit(shots, 4).astype(float)
    xo = x[odd] - x[odd].mean()
    fo, po = locate(xo, odd, LINE_BAND)
    _, h, _, se = fold(shots, even, roles, fo, po)
    fn, pn = locate(xo, odd, OFF_LINE_BAND)
    _, g, _, _ = fold(shots, even, roles, fn, pn)
    return {
        "batch": job[0][-8:],
        "arm": arm_of(job[1]),
        "f": fo,
        "h1": polar(h),
        "se": se,
        "off_line_h1": polar(g),
    }


CONDITIONALS = (
    "sel0_given_coin1",
    "sel0_given_coin0",
    "contrast",
    "sel0",
    "coin1",
    "contrast_q4_reads_0",
    "contrast_q4_reads_1",
)


def _contrast(sel0: np.ndarray, coin: np.ndarray, mask: np.ndarray) -> float:
    return float(sel0[mask & coin].mean() - sel0[mask & ~coin].mean())


def conditionals_job(job: Job) -> dict[str, list[float]]:
    """line_phase_conditionals.py: first harmonics (real, imaginary) of the statistics of CONDITIONALS."""
    shots, roles = load(job)
    q4 = bit(shots, 4)
    n = np.arange(len(shots))
    odd, even = n[1::2], n[0::2]
    x = q4[odd].astype(float)
    fo, po = locate(x - x.mean(), odd, LINE_BAND)
    b = phase_bins(fo, po, even)
    sel0, coin, q4e = ~bit(shots, roles["selector"])[even], bit(shots, roles["coin"])[even], q4[even]
    rows: dict[str, list[float]] = {k: [] for k in CONDITIONALS}
    for k in range(BINS):
        m = b == k
        rows["sel0_given_coin1"].append(sel0[m & coin].mean())
        rows["sel0_given_coin0"].append(sel0[m & ~coin].mean())
        rows["contrast"].append(_contrast(sel0, coin, m))
        rows["sel0"].append(sel0[m].mean())
        rows["coin1"].append(coin[m].mean())
        rows["contrast_q4_reads_0"].append(_contrast(sel0, coin, m & ~q4e))
        rows["contrast_q4_reads_1"].append(_contrast(sel0, coin, m & q4e))
    out = {}
    for key in CONDITIONALS:
        h = 2 * np.mean(np.array(rows[key]) * np.exp(-1j * ANGLES))
        out[key] = [float(h.real), float(h.imag)]
    return out


def _largest(x: np.ndarray, band: tuple[float, float]) -> float:
    n = np.arange(len(x))
    grid = np.linspace(*band, 201)
    return float(max(2 * abs(np.sum((x - x.mean()) * np.exp(-2j * np.pi * f * n))) / len(x) for f in grid))


def parity_job(job: Job) -> dict[str, Any]:
    """line_parity_amplitude.py: largest band amplitude of the selector-coin parity bit and of q4's bit."""
    shots, roles = load(job)
    q4 = bit(shots, 4).astype(float)
    parity = np.abs(bit(shots, roles["selector"]).astype(float) - bit(shots, roles["coin"]).astype(float))
    row: dict[str, Any] = {"batch": job[0][-8:], "arm": arm_of(job[1])}
    for name, band in (("line", LINE_BAND), ("off_line", OFF_LINE_BAND)):
        row[f"parity_{name}"] = _largest(parity, band)
        row[f"q4_{name}"] = _largest(q4, band)
    return row


def time_bins_job(job: Job) -> dict[str, Any]:
    """time_bins.py: selector contrast in 8 consecutive shot bins."""
    shots, roles = load(job)
    n = len(shots) // BINS
    vals = [rs.circuit_statistics(shots[i * n : (i + 1) * n], roles) for i in range(BINS)]
    return {"contrast": [v["contrast"] for v in vals], "se": [v["se"] for v in vals]}


REGISTER = (2, 4, 8, 11, 12)
DEPENDENCE_PAIRS = ((8, 12), (12, 8), (4, 8), (8, 4), (4, 12), (8, 11), (12, 11), (8, 2))


def bracket_job(batch: int) -> dict[str, Any]:
    """bracket_drift.py: one readout batch's midpoint, per-qubit error rates and read-value pair counts."""
    directory = RUNS / f"{S}-pathion_null_rotation_scan_tuna_17-batch-{batch:02d}"
    stamps = []
    for job in json.loads((directory / "results.json").read_text())["jobs"]:
        result = job["results"][0] if isinstance(job.get("results"), list) else job["results"]
        text = job.get("finished_at") or result.get("created_on")
        stamps.append(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    pair = {k: json.loads((directory / f"raw/readout-{k}.cq.json").read_text()) for k in (0, 1)}
    rates = {}
    for q in REGISTER:
        rates[f"q{q}_e01"] = sum(s[16 - q] == "1" for s in pair[0]) / len(pair[0])
        rates[f"q{q}_e10"] = 1 - sum(s[16 - q] == "1" for s in pair[1]) / len(pair[1])
    counts = {}
    for k in (0, 1):
        for a, b in DEPENDENCE_PAIRS:
            n = [0, 0]
            hit = [0, 0]
            for s in pair[k]:
                c = s[16 - b] == "1"
                n[c] += 1
                hit[c] += s[16 - a] == "1"
            counts[f"{k}:{a}:{b}"] = [n, hit]
    return {"midpoint": sum(stamps) / len(stamps), "rates": rates, "counts": counts}
