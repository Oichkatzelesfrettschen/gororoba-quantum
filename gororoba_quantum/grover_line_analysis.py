r"""Analysis of a retained run of the line-native CCZ Grover case built by scripts/iqm_grover_line.py.

The case runs three-qubit Grover search: marked strings 101 and 011 at one and two iterations, the generic
compile of one iteration in ABBA copies, the uniform reference k0 and the eight readout preparations ro-xyz.
Every outcome key reads logical qubit q at character q, and basis index x = sum b_q 2^q.

- Readout correction. The ro circuits give the 8 x 8 assignment matrix A[measured, prepared] in their own
  measurement order; each circuit is corrected by A permuted into its measurement order (the generic compile
  measures its qubits in another physical order), with delta-method variances over the circuit's counts and
  every ro circuit's counts.
- Walsh spectrum. The ideal output is a peak on the marked string m over a uniform floor, so each parity
  correlator <Z_S>, S in F_2^3 \ {0}, equals chi_S(m) (8 P_k - 1) / 7. The ratio r_S of a measured correlator
  to that value is one number for every S under global depolarizing noise and falls as f^|S| under
  independent bit flips of retention f. Raw ratios (walsh_counts.parity_numerators of the pooled counts) are
  compared with the model's prediction, which includes readout error; corrected ratios are compared with the
  model's prediction before its readout channel.
- Hamming profile: the unmarked mass at distance 1, 2, 3 from m, against 3/7, 3/7, 1/7 for uniform error.
- Retention lambda_k = (P_k - 1/8) / (P_k^ideal - 1/8) of the corrected marked probability.

analyze takes explicit inputs: the acquisition (read_acquisition validates the run through
iqm_records.read_run) and the model's per-qubit readout errors, which the case script reads from the run's
calibration copy. Every value is rounded to 6 digits.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from boolean_anf import anf_degree
from cd_core import cd_sign
from iqm_records import ROOT, read_run
from walsh_counts import parity_numerators

MARKS = ("101", "011")
# Preregistered decision: a difference resolves when it lies Z_RESOLVE binomial standard errors from zero.
Z_RESOLVE = 3.0
GROVER_ARMS = (
    ("m101-k1", "101", 1),
    ("m101-k1-generic", "101", 1),
    ("m101-k2", "101", 2),
    ("m011-k1", "011", 1),
    ("m011-k2", "011", 2),
)
WALSH = np.array([[(-1) ** bin(s & x).count("1") for x in range(8)] for s in range(8)], dtype=float)


def ideal_probability(k: int) -> float:
    return math.sin((2 * k + 1) * math.asin(1 / math.sqrt(8))) ** 2


def key_of(index: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(3))


def index_of(key: str) -> int:
    return sum(int(key[q]) << q for q in range(3))


def move_matrix(order: list[str], target: list[str]) -> np.ndarray:
    """Permutation taking an outcome index read in measurement order `target` to the index of the same physical
    outcome read in measurement order `order`."""
    move = np.zeros((8, 8))
    for x in range(8):
        move[sum(((x >> j) & 1) << order.index(target[j]) for j in range(3)), x] = 1
    return move


def relabel(matrix: np.ndarray, order: list[str], target: list[str]) -> np.ndarray:
    """An 8 x 8 matrix on outcomes read in measurement order `order`, re-expressed on outcomes read in `target`."""
    move = move_matrix(order, target)
    return move.T @ matrix @ move


def product_confusion(order: list[str], readout: dict[str, tuple[float, float]]) -> np.ndarray:
    """The independent per-qubit readout channel C[measured, true] of a circuit measured in `order`, from each
    qubit's (P(read 1 | 0), P(read 0 | 1))."""
    out = np.ones((1, 1))
    for qubit in reversed(order):
        e01, e10 = readout[qubit]
        out = np.kron(out, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    return out


def walsh_ratios(spectrum: np.ndarray, marked: str, k: int) -> list[float]:
    """<Z_S> over its ideal value chi_S(marked) (8 P_k - 1) / 7, for S = 1 to 7, from the normalized spectrum."""
    scale = (8 * ideal_probability(k) - 1) / 7
    m = index_of(marked)
    return [float(spectrum[s] / ((-1) ** bin(s & m).count("1") * scale)) for s in range(1, 8)]


def by_weight(ratios: list[float]) -> dict[str, float]:
    return {str(w): r6(np.mean([ratios[s - 1] for s in range(1, 8) if bin(s).count("1") == w])) for w in (1, 2, 3)}


def hamming_profile(q: np.ndarray, marked: str) -> list[float]:
    """Share of the unmarked mass at Hamming distance 1, 2, 3 from the marked string."""
    m = index_of(marked)
    wrong = 1 - q[m]
    return [float(sum(q[x] for x in range(8) if bin(x ^ m).count("1") == h) / wrong) for h in (1, 2, 3)]


def r6(x: float) -> float:
    return round(float(x), 6)


@dataclass(frozen=True)
class Acquisition:
    """Counts per circuit in job order, each circuit's measurement order, and the case's prediction."""

    run: str
    names: list[str]
    counts: dict[str, np.ndarray]
    orders: dict[str, list[str]]
    prediction: dict[str, Any]


def read_acquisition(run_dir: Path) -> Acquisition:
    run = read_run(run_dir)
    files = [c["file"] for c in run.row["circuits"]]
    names = [Path(f).stem for f in files]
    raw = json.loads(run.raw["measurement_counts.json"])
    if len(raw) != len(files):
        raise ValueError(f"{run_dir}: {len(raw)} count records for {len(files)} circuits")
    counts = {}
    for name, record in zip(names, raw, strict=True):
        vector = np.zeros(8, dtype=np.int64)
        for key, n in record["counts"].items():
            vector[index_of(key)] += n
        counts[name] = vector
    orders = {}
    for name, rel in zip(names, files, strict=True):
        circuit = json.loads((run_dir / rel).read_text(encoding="utf-8"))
        orders[name] = next(op["locus"] for op in circuit["instructions"] if op["name"] == "measure")
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    return Acquisition(run_dir.resolve().relative_to(ROOT).as_posix(), names, counts, orders, prediction)


class Readout:
    """The assignment matrix of the ro circuits and the delta-method variance of a corrected linear statistic."""

    def __init__(self, acquisition: Acquisition) -> None:
        self.acquisition = acquisition
        self.order = acquisition.orders["ro-000"]
        self.shots = np.array([acquisition.counts["ro-" + key_of(c)].sum() for c in range(8)], dtype=float)
        self.matrix = np.column_stack([acquisition.counts["ro-" + key_of(c)] / self.shots[c] for c in range(8)])

    def copies(self, base: str) -> list[str]:
        return [n for n in self.acquisition.names if n == base or n.startswith(base + "-c")]

    def marked(self, base: str, marked: str) -> tuple[float, dict[str, np.ndarray], np.ndarray]:
        """Corrected pooled marked probability with its gradients in every circuit's frequencies and in every
        column of the assignment matrix."""
        names = self.copies(base)
        counts = self.acquisition.counts
        total = sum(counts[n].sum() for n in names)
        m = index_of(marked)
        value = 0.0
        grad_p: dict[str, np.ndarray] = {}
        grad_a = np.zeros((8, 8))
        for n in names:
            weight = counts[n].sum() / total
            move = move_matrix(self.order, self.acquisition.orders[n])
            local = move.T @ self.matrix @ move
            q = np.linalg.solve(local, counts[n] / counts[n].sum())
            u = np.linalg.solve(local.T, np.eye(8)[m])
            value += weight * q[m]
            grad_p[n] = weight * u
            grad_a -= weight * np.outer(move @ u, move @ q)
        return float(value), grad_p, grad_a

    def variance(self, grad_p: dict[str, np.ndarray], grad_a: np.ndarray) -> float:
        out = 0.0
        for n, g in grad_p.items():
            c = self.acquisition.counts[n]
            p = c / c.sum()
            out += float(g @ ((np.diag(p) - np.outer(p, p)) / c.sum()) @ g)
        for col in range(8):
            a = self.matrix[:, col]
            out += float(grad_a[:, col] @ ((np.diag(a) - np.outer(a, a)) / self.shots[col]) @ grad_a[:, col])
        return out

    def corrected(self, base: str) -> np.ndarray:
        names = self.copies(base)
        counts = self.acquisition.counts
        total = sum(counts[n].sum() for n in names)
        out = np.zeros(8)
        for n in names:
            local = relabel(self.matrix, self.order, self.acquisition.orders[n])
            out += np.linalg.solve(local, counts[n] / counts[n].sum()) * counts[n].sum() / total
        return out


def analyze(acquisition: Acquisition, model_readout: dict[str, tuple[float, float]]) -> dict[str, Any]:
    """Every arm's raw and corrected marked probability, spectra, profile and retention, the preregistered
    decisions and the k0 uniformity test; model_readout is the per-qubit readout error the prediction used."""
    readout = Readout(acquisition)
    counts = acquisition.counts
    arms: dict[str, Any] = {}
    terms: dict[str, tuple[dict[str, np.ndarray], np.ndarray]] = {}
    for base, marked, k in GROVER_ARMS:
        names = readout.copies(base)
        pooled_counts = np.sum([counts[n] for n in names], axis=0)
        kept = int(pooled_counts.sum())
        pooled = pooled_counts / kept
        raw = float(pooled[index_of(marked)])
        corrected, grad_p, grad_a = readout.marked(base, marked)
        terms[base] = (grad_p, grad_a)
        q = readout.corrected(base)
        predicted = acquisition.prediction["arms"][base]["predicted"]
        model = np.array([predicted[key_of(x)] for x in range(8)])
        model_true = np.linalg.solve(product_confusion(acquisition.orders[names[0]], model_readout), model)
        raw_ratios = walsh_ratios(parity_numerators(pooled_counts) / kept, marked, k)
        corrected_ratios = walsh_ratios(WALSH @ q, marked, k)
        arms[base] = {
            "copies": names,
            "kept_shots": kept,
            "measured_on": acquisition.orders[names[0]],
            "raw_marked": r6(raw),
            "corrected_marked": r6(corrected),
            "corrected_marked_se": r6(math.sqrt(readout.variance(grad_p, grad_a))),
            "predicted_marked": predicted[marked],
            "predicted_marked_before_readout": r6(model_true[index_of(marked)]),
            "ideal_marked": r6(ideal_probability(k)),
            "raw_excess_over_predicted": r6((raw - 0.125) / (predicted[marked] - 0.125)),
            "corrected_retention": r6((corrected - 0.125) / (ideal_probability(k) - 0.125)),
            "tvd_raw_to_model": r6(0.5 * float(np.abs(pooled - model).sum())),
            "hellinger_fidelity_raw_to_model": r6(float(np.sqrt(pooled * model).sum()) ** 2),
            "most_frequent": key_of(int(np.argmax(pooled))),
            "raw_walsh_ratio_by_weight": by_weight(raw_ratios),
            "model_walsh_ratio_by_weight": by_weight(walsh_ratios(WALSH @ model, marked, k)),
            "corrected_walsh_ratio": {key_of(s): r6(corrected_ratios[s - 1]) for s in range(1, 8)},
            "corrected_walsh_ratio_by_weight": by_weight(corrected_ratios),
            "model_before_readout_walsh_ratio_by_weight": by_weight(walsh_ratios(WALSH @ model_true, marked, k)),
            "hamming_profile": [r6(x) for x in hamming_profile(q, marked)],
            "logical_bit_error": [r6(sum(q[x] for x in range(8) if (x ^ index_of(marked)) >> b & 1)) for b in range(3)],
        }
        if len(names) > 1:
            freqs = [counts[n][index_of(marked)] / counts[n].sum() for n in names]
            chi2 = sum((f - raw) ** 2 / (raw * (1 - raw) / counts[n].sum()) for f, n in zip(freqs, names, strict=True))
            positions = [acquisition.names.index(n) for n in names]
            arms[base]["copy_frequencies"] = [r6(f) for f in freqs]
            arms[base]["copy_positions"] = positions
            arms[base]["copy_chi2"] = r6(chi2)
            arms[base]["copy_slope_per_position"] = r6(np.polyfit(positions, freqs, 1)[0])

    def difference(first: str, second: str) -> dict[str, Any]:
        a, b = arms[first], arms[second]
        raw = a["raw_marked"] - b["raw_marked"]
        se = math.sqrt(sum(x["raw_marked"] * (1 - x["raw_marked"]) / x["kept_shots"] for x in (a, b)))
        pa, ga = terms[first]
        pb, gb = terms[second]
        grads = dict(pa)
        for n, g in pb.items():
            grads[n] = grads.get(n, np.zeros(8)) - g
        z = raw / se
        return {
            "raw": r6(raw),
            "se": r6(se),
            "z": r6(z),
            "verdict": "positive" if z >= Z_RESOLVE else "negative" if z <= -Z_RESOLVE else "unresolved",
            "corrected": r6(a["corrected_marked"] - b["corrected_marked"]),
            "corrected_se": r6(math.sqrt(readout.variance(grads, ga - gb))),
        }

    retention = {}
    for m in MARKS:
        one = arms[f"m{m}-k1"]["corrected_retention"]
        two = arms[f"m{m}-k2"]["corrected_retention"]
        retention[m] = {"k1": one, "k2": two, "per_iteration": r6(two / one)}
    k0_counts = counts["k0"]
    k0 = k0_counts / k0_counts.sum()
    k0_corrected = np.linalg.solve(relabel(readout.matrix, readout.order, acquisition.orders["k0"]), k0)
    return {
        "run": acquisition.run,
        "readout_assignment_diagonal": {key_of(c): r6(readout.matrix[c, c]) for c in range(8)},
        "arms": arms,
        "decisions": {
            "line_vs_generic": difference("m101-k1", "m101-k1-generic"),
            "second_iteration": {m: difference(f"m{m}-k2", f"m{m}-k1") for m in MARKS},
            "bit_order": {n: arms[n]["most_frequent"] for n in ("m011-k1", "m011-k2")},
        },
        "retention": retention,
        "generic_retention_over_line": r6(
            arms["m101-k1-generic"]["corrected_retention"] / arms["m101-k1"]["corrected_retention"]
        ),
        "k0": {
            "raw": {key_of(x): r6(k0[x]) for x in range(8)},
            "corrected": {key_of(x): r6(k0_corrected[x]) for x in range(8)},
            # Pearson's multinomial statistic against 1/8 each, 7 degrees of freedom.
            "pearson_chi2_uniform_raw": r6(float(k0_counts.sum() * ((k0 - 0.125) ** 2 / 0.125).sum())),
        },
    }


def self_test() -> str:
    for marked, k in (("101", 1), ("011", 2)):
        ideal = np.full(8, (1 - ideal_probability(k)) / 7)
        ideal[index_of(marked)] = ideal_probability(k)
        if max(abs(r - 1) for r in walsh_ratios(WALSH @ ideal, marked, k)) > 1e-12:
            raise AssertionError("the ideal Grover distribution has a Walsh ratio other than 1")
        noisy = 0.8 * ideal + 0.2 / 8
        if max(abs(r - 0.8) for r in walsh_ratios(WALSH @ noisy, marked, k)) > 1e-12:
            raise AssertionError("global depolarizing noise does not scale every parity alike")
        if max(abs(a - b) for a, b in zip(hamming_profile(noisy, marked), (3 / 7, 3 / 7, 1 / 7), strict=True)) > 1e-12:
            raise AssertionError("uniform error does not spread 3/7, 3/7, 1/7 over the Hamming shells")
        integer = np.round(ideal * 2**20).astype(np.int64)
        if not np.allclose(parity_numerators(integer), WALSH @ integer):
            raise AssertionError("walsh_counts and the parity matrix disagree on one histogram")
    flip = np.array([[0.9, 0.2], [0.1, 0.8]])
    product = np.kron(np.kron(np.eye(2), flip), np.eye(2))
    if not np.allclose(relabel(product, ["A", "B", "C"], ["B", "C", "A"]), np.kron(np.eye(4), flip)):
        raise AssertionError("relabel does not carry qubit B's readout to its new measurement position")
    channel = product_confusion(["A", "B", "C"], {"A": (0.0, 0.0), "B": (0.1, 0.2), "C": (0.0, 0.0)})
    if not np.allclose(channel, product):
        raise AssertionError("product_confusion does not put qubit q at index bit q")
    for n in (3, 4, 5):
        degrees = {anf_degree([(1 - cd_sign(2**n, m, q)) // 2 for q in range(2**n)]) for m in range(1, 2**n)}
        if degrees != {n - 1}:
            raise AssertionError(f"left-multiplication signs of dimension {2**n} have degrees {degrees}, not {n - 1}")
    return "grover_line_analysis self-test passed"
