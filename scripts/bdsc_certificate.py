"""Belenos dark-subspace certificate: exact target, 24-mode measurement, preparation bank, controls and qualification.

The target is the binary effect E0 = L_x^T L_x / 2 of the sedenion zero
divisor x = (e1 + e10)/sqrt2 (gororoba_quantum/bdsc.py carries the frame,
the reconstruction, the confidence radii and the certificate theorem).
This script holds the exact layer and the retained records.

- Algebra. L_int = L_e1 + L_e10 is an integer signed-permutation sum, so
  E0 = L_int^T L_int / 4 and P = V_K V_K^T are rational. The frame vectors
  are kept unnormalized (integer w, |w|^2 in {1, 2}); E0 w = lambda w for
  all 16, mutual orthogonality and sum w w^T / |w|^2 = I establish the
  spectrum {0^4, (1/2)^8, 1^4} in Fractions. An independent recursive
  doubling (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) over Fractions
  reproduces cd_core.cd_sign on all 256 basis products.
- Measurement. U24 sends k_j to D_j, the bright partner b_j to A_j, each
  middle basis vector e_m to (A + D)/sqrt2 and ancilla j to (A - D)/sqrt2,
  with every entry in {0, +-1/sqrt2} in Q(sqrt2) ([a, b] = a + b sqrt2);
  U24^T U24 = I and the compression of U24^T Q_A U24 to the 16 logical
  inputs equals E0, both exactly. On a single-mode Belenos photon only the
  column U24 psi_s reaches the chip, so the records carry, per setting,
  that 24-vector, the source mode and the 12/12 selected-output mask.
- Assignment. A_1..A_12 are the twelve outputs with the lowest receipt dark
  rate (ties by mode) of the frozen qpu:belenos receipt
  (docs/evidence/bdsc/inputs/receipt.json, the catalogue retrieval of
  2026-10-17T17:53:31Z), D_1..D_12 the rest in mode order; the source is
  the connected input with the highest receipt t_in. Both receipt fields
  are dated planning inputs, and a later catalogue leaves them unchanged.

Records under docs/evidence/bdsc/: target.json (algebra, frames, U24,
mask), bank.json (the 160 settings with their states, chip columns and
exact ideal probabilities; the 88 real settings flagged), pilot.json,
controls.json (synthetic adversarial controls through bdsc.evaluate),
planning.json (radius table, zero-event trace route, five-space witness
and consistency plans, measured Belenos rates), qualification.json
(milestones M0 to M9 with the evidence that passes or blocks each),
provider_contract.json (each provider capability the certificate needs,
its status and its question) and qualification_case.json (the six-state
consistency case: banks, preparation descriptions, processing policies,
epochs, margin, trials, cost ceiling and stop conditions).

--write DIR writes the records; --check DIR regenerates them and compares
(floats within CHECK_TOLERANCE, everything else exactly); --self-test
requires algebra, unitary, mask, bank, record and premise mutations to be
rejected and checks the theorem and the confidence coverage on random
effects.

Usage: "$PYTHON" scripts/bdsc_certificate.py (--write DIR | --check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from qd_box_kite_cases import Q2, ZERO, Matrix, matmul, q, text, transpose  # noqa: E402

import bdsc  # noqa: E402
import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

# The qpu:belenos receipt the target was planned against, frozen from the catalogue retrieval of
# 2026-10-17T17:53:31Z: a catalogue refresh is new calibration, and a target planned from it is a new target.
RECEIPT = ROOT / "docs/evidence/bdsc/inputs/receipt.json"
RECEIPT_SCHEMA = "bdsc-receipt-v1"
EVIDENCE = ROOT / "docs/evidence/bdsc"
CHIP = "qpu:belenos"
MODES = 24
SCHEMA = "bdsc-records-v1"
FILES = (
    "target.json",
    "bank.json",
    "pilot.json",
    "controls.json",
    "planning.json",
    "qualification.json",
    "provider_contract.json",
    "qualification_case.json",
)
CHECK_TOLERANCE = 1e-9
HALF_ROOT: Q2 = (Fraction(0), Fraction(1, 2))
ALLOCATION = "two-block"
CONTROL_TRIALS = 100_000
DEEP_TRIALS = 1_000_000
IDEAL_TIERS = (3_000, 5_000, 7_500, 10_000, 30_000, 100_000)
BACKGROUNDS = (0.0, 0.002, 0.005, 0.01, 0.02)
COVERAGE_TRIALS = 10_000
COVERAGE_REPLICATES = 64
THEOREM_EFFECTS = 512
THEOREM_NONTRIVIAL_MIN = 800
# Historical qpu:belenos rates (docs/notes/quandela/strategy.md section 1a): an iterated job spends about 6.3 s
# per iteration plus 26 us per sample within the 300 s job limit, bills 1 credit plus 1e-6 per shot of its
# largest iteration, and runs one job at a time against 200 Explorer credits a month.
SECONDS_PER_ITERATION = 6.3
SECONDS_PER_SAMPLE = 26e-6
JOB_SECONDS = 300
MAX_ITERATIONS = 32
CREDITS_PER_JOB = 1.0
CREDITS_PER_SHOT = 1e-6
SHOT_HEADROOM = 2
MONTHLY_CREDITS = 200
# The handoff's dated snapshot against the retained catalogue; neither is a confidence-qualified calibration.
WITNESS_BRIGHT_LOWER = 0.9
WITNESS_ALPHA = 0.025
CASE_ALPHA = 0.01
CASE_EPOCHS = (1, 2)
CASE_MARGINS = {"sum_rule": 0.02, "completion": 0.02, "epoch": 0.02}
CASE_POWER_TARGET = 0.95
CASE_POWER_REPLICATES = 2000
CASE_POWER_SEED = 20261021
CASE_REFERENCE_TRIALS = 45_000
CASE_TRIAL_GRID = tuple(range(100_000, 400_001, 25_000))
# An iterated job runs SECONDS_PER_ITERATION plus SECONDS_PER_SAMPLE per sample for each iteration (strategy.md
# section 1: c1eb1cbb, 9 iterations and 166000 samples in 61 s; 46b810ae, 24 iterations and 240000 samples in
# 149 s) and bills 1 credit plus 1e-6 per shot of its largest iteration's max_shots. A job fills at most
# CASE_JOB_FILL of the per-job limit, leaving the rest for a slower acquisition rate.
CASE_JOB_FILL = 0.6
QRNG_VALUES = 192
CASE_PAIRS = {"target-complement": ("K", 0, "Q", 8), "middle-middle": ("Q", 1, "Q", 2)}
PREPARATION_DESCRIPTIONS = ("outward-ladder", "reverse-ladder")
PROCESSING_POLICIES: dict[str, list[str] | None] = {"provider-defaults": None, "empty-mitigation": []}
HANDOFF_SNAPSHOT = {"transmittance_percent": 6.06, "hom_percent": 88.5, "g2_percent": 0.9, "dark_mode5_per_s": 412.7}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# --- exact algebra -------------------------------------------------------------------------

FracMatrix = list[list[Fraction]]


def doubling_product(a: tuple[Any, ...], b: tuple[Any, ...]) -> tuple[Any, ...]:
    """(a0, a1)(b0, b1) = (a0 b0 - conj(b1) a1, b1 a0 + a1 conj(b0)) on flat Fraction tuples."""
    if len(a) == 1:
        return (a[0] * b[0],)
    h = len(a) // 2
    a0, a1, b0, b1 = a[:h], a[h:], b[:h], b[h:]

    def sub(x: tuple[Any, ...], y: tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(u - v for u, v in zip(x, y, strict=True))

    def plus(x: tuple[Any, ...], y: tuple[Any, ...]) -> tuple[Any, ...]:
        return tuple(u + v for u, v in zip(x, y, strict=True))

    first = sub(doubling_product(a0, b0), doubling_product(conj(b1), a1))
    second = plus(doubling_product(b1, a0), doubling_product(a1, conj(b0)))
    return first + second


def conj(a: tuple[Any, ...]) -> tuple[Any, ...]:
    return (a[0],) + tuple(-x for x in a[1:])


def doubling_matches_cd_core(sign: Any = cd_sign) -> bool:
    for p in range(bdsc.DIM):
        for r in range(bdsc.DIM):
            ep = tuple(Fraction(int(i == p)) for i in range(bdsc.DIM))
            er = tuple(Fraction(int(i == r)) for i in range(bdsc.DIM))
            product = doubling_product(ep, er)
            expected = [Fraction(0)] * bdsc.DIM
            expected[p ^ r] = Fraction(sign(bdsc.DIM, p, r))
            if list(product) != expected:
                return False
    return True


def left_int() -> FracMatrix:
    """L_e1 + L_e10 with (L_m)[m ^ col][col] = cd_sign(16, m, col)."""
    out = [[Fraction(0)] * bdsc.DIM for _ in range(bdsc.DIM)]
    for m in bdsc.X_LABELS:
        for col in range(bdsc.DIM):
            out[m ^ col][col] += cd_sign(bdsc.DIM, m, col)
    return out


def fmul(a: FracMatrix, b: FracMatrix) -> FracMatrix:
    return [
        [sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0)) for j in range(len(b[0]))] for i in range(len(a))
    ]


def ftranspose(a: FracMatrix) -> FracMatrix:
    return [list(col) for col in zip(*a, strict=True)]


def target_effect() -> FracMatrix:
    lint = left_int()
    return [[x / 4 for x in row] for row in fmul(ftranspose(lint), lint)]


def integer_frame() -> list[dict[str, Any]]:
    """The 16 frame vectors as integer w with their block, frame index, eigenvalue and |w|^2."""
    out = []

    def vec(*terms: tuple[int, int]) -> list[int]:
        v = [0] * bdsc.DIM
        for c, label in terms:
            v[label] = c
        return v

    for j, (a, b, s) in enumerate(bdsc.KERNEL_PAIRS):
        out.append({"name": f"k{j + 1}", "block": "A", "index": j, "eigenvalue": "0", "w": vec((1, a), (s, b))})
    for j, label in enumerate(bdsc.MIDDLE_LABELS):
        out.append({"name": f"f{j + 1}", "block": "C", "index": j, "eigenvalue": "1/2", "w": vec((1, label))})
    for j, (a, b, s) in enumerate(bdsc.KERNEL_PAIRS):
        out.append({"name": f"f{9 + j}", "block": "C", "index": 8 + j, "eigenvalue": "1", "w": vec((1, a), (-s, b))})
    return out


def exact_checks(effect: FracMatrix, frame: list[dict[str, Any]]) -> dict[str, bool]:
    lint = left_int()
    checks: dict[str, bool] = {}
    checks["doubling_matches_cd_core"] = doubling_matches_cd_core()
    checks["effect_symmetric"] = effect == ftranspose(effect)
    eigen = True
    for f in frame:
        w = [Fraction(x) for x in f["w"]]
        lam = Fraction(f["eigenvalue"])
        image = [sum((effect[i][k] * w[k] for k in range(bdsc.DIM)), Fraction(0)) for i in range(bdsc.DIM)]
        eigen = eigen and image == [lam * x for x in w]
        if f["block"] == "A":
            product = [sum((lint[i][k] * w[k] for k in range(bdsc.DIM)), Fraction(0)) for i in range(bdsc.DIM)]
            checks[f"L_x {f['name']} = 0"] = all(x == 0 for x in product)
    checks["frame_eigenvectors"] = eigen
    gram = [[sum(Fraction(a * b) for a, b in zip(f["w"], g["w"], strict=True)) for g in frame] for f in frame]
    checks["frame_orthogonal"] = all(gram[i][j] == 0 for i in range(16) for j in range(16) if i != j)
    checks["frame_norms_1_or_2"] = all(gram[i][i] in (1, 2) for i in range(16))
    resolution = [[Fraction(0)] * 16 for _ in range(16)]
    for f, n2 in zip(frame, (gram[i][i] for i in range(16)), strict=True):
        for i in range(16):
            for j in range(16):
                resolution[i][j] += Fraction(f["w"][i] * f["w"][j]) / n2
    checks["frame_complete"] = resolution == [[Fraction(int(i == j)) for j in range(16)] for i in range(16)]
    p = kernel_projector(frame)
    checks["P_idempotent"] = fmul(p, p) == p
    checks["P_trace_4"] = sum((p[i][i] for i in range(16)), Fraction(0)) == 4
    checks["E0 P = 0"] = all(x == 0 for row in fmul(effect, p) for x in row)
    return checks


def kernel_projector(frame: list[dict[str, Any]]) -> FracMatrix:
    p = [[Fraction(0)] * bdsc.DIM for _ in range(bdsc.DIM)]
    for f in frame:
        if f["block"] == "A":
            for i in range(bdsc.DIM):
                for j in range(bdsc.DIM):
                    p[i][j] += Fraction(f["w"][i] * f["w"][j], 2)
    return p


# --- measurement unitary -------------------------------------------------------------------


def load_catalogue() -> dict[str, Any]:
    """The frozen receipt, shaped as the catalogue slice the assignment and planning read."""
    data: dict[str, Any] = json.loads(RECEIPT.read_text(encoding="utf-8"))
    require(data.get("schema") == RECEIPT_SCHEMA and data.get("processor") == CHIP, "receipt identity differs")
    chip = data["processors"][CHIP]
    body = json.dumps(chip, sort_keys=True, separators=(",", ":")).encode()
    require(hashlib.sha256(body).hexdigest() == data["processor_sha256"], "receipt processor digest differs")
    return data


def assignment(catalogue: dict[str, Any]) -> dict[str, Any]:
    chip = catalogue["processors"][CHIP]
    perfs, specs = chip["perfs"], chip["specs"]
    dark = perfs["Dark counts (detection/s)"]
    t_in = perfs["Transmission per mode (%)"]["t_in"]
    connected = specs["connected_input_modes"]
    require(len(dark) == MODES, "the catalogue's dark-count list is not 24 modes")
    order = sorted(range(MODES), key=lambda m: (dark[m], m))
    selected = order[:12]
    complement = sorted(order[12:])
    source = max(connected, key=lambda m: (t_in[m], -m))
    return {
        "selected_modes": selected,
        "complement_modes": complement,
        "source_mode": source,
        "rule": "A_j: twelve lowest receipt dark rates, ties by mode; D_j: the rest in mode order; "
        "source: connected input with the highest receipt t_in",
        "receipt_dark_per_s": dark,
        "receipt_t_in_percent": t_in,
        "receipt_t_out_relative": perfs["Transmission per mode (%)"]["t_out"],
        "catalogue_retrieved_utc": catalogue["retrieved_utc"],
    }


def measurement_unitary(selected: list[int], complement: list[int]) -> Matrix:
    """U24 over Q(sqrt2): rows are output modes, columns e_0..e_15 then ancillas a_1..a_8."""
    u: Matrix = [[ZERO] * MODES for _ in range(MODES)]

    def put(row: int, column: int, value: Q2) -> None:
        u[row][column] = value

    def neg(x: Q2) -> Q2:
        return (-x[0], -x[1])

    for j, (a, b, s) in enumerate(bdsc.KERNEL_PAIRS):
        # k_j = (e_a + s e_b)/sqrt2 -> D_j and b_j = (e_a - s e_b)/sqrt2 -> A_j.
        d, sel = complement[j], selected[j]
        put(d, a, HALF_ROOT)
        put(d, b, HALF_ROOT if s > 0 else neg(HALF_ROOT))
        put(sel, a, HALF_ROOT)
        put(sel, b, neg(HALF_ROOT) if s > 0 else HALF_ROOT)
    for j, label in enumerate(bdsc.MIDDLE_LABELS):
        sel, d, ancilla = selected[4 + j], complement[4 + j], bdsc.DIM + j
        put(sel, label, HALF_ROOT)
        put(d, label, HALF_ROOT)
        put(sel, ancilla, HALF_ROOT)
        put(d, ancilla, neg(HALF_ROOT))
    return u


def unitary_checks(u: Matrix, selected: list[int], effect: FracMatrix) -> dict[str, bool]:
    identity = [[q(int(i == j)) for j in range(MODES)] for i in range(MODES)]
    mask = [[q(int(i == j and i in selected)) for j in range(MODES)] for i in range(MODES)]
    compressed = matmul(matmul(transpose(u), mask), u)
    return {
        "U24^T U24 = I": matmul(transpose(u), u) == identity,
        "compression = E0": all(
            compressed[i][j] == (effect[i][j], Fraction(0)) for i in range(bdsc.DIM) for j in range(bdsc.DIM)
        ),
    }


def numeric_unitary(u: Matrix) -> np.ndarray:
    return np.array([[float(a) + float(b) * math.sqrt(2) for a, b in row] for row in u])


# --- records -------------------------------------------------------------------------------


def fractions_text(m: FracMatrix) -> list[list[str]]:
    return [[str(x) for x in row] for row in m]


def complex_list(v: np.ndarray) -> list[list[float]]:
    return [[round(float(z.real), 15), round(float(z.imag), 15)] for z in v]


def target_record(catalogue: dict[str, Any]) -> dict[str, Any]:
    effect = target_effect()
    frame = integer_frame()
    plan = assignment(catalogue)
    u = measurement_unitary(plan["selected_modes"], plan["complement_modes"])
    checks = {**exact_checks(effect, frame), **unitary_checks(u, plan["selected_modes"], effect)}
    require(all(checks.values()), f"exact checks fail: {[k for k, v in checks.items() if not v]}")
    core = {
        "convention": "cd_core.cd_sign; (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)); e_0 = 1; L_x(y) = x y",
        "x": {"labels": list(bdsc.X_LABELS), "coefficients": ["1/sqrt2", "1/sqrt2"]},
        "effect": "E0 = L_x^T L_x / 2 = (L_e1 + L_e10)^T (L_e1 + L_e10) / 4",
        "E0": fractions_text(effect),
        "spectrum": {"0": 4, "1/2": 8, "1": 4},
        "frame": frame,
        "P": fractions_text(kernel_projector(frame)),
        "U24": [[text(x) for x in row] for row in u],
        "U24_columns": [f"e{i}" for i in range(bdsc.DIM)] + [f"a{j + 1}" for j in range(8)],
        "selected_modes": plan["selected_modes"],
        "complement_modes": plan["complement_modes"],
        "source_mode": plan["source_mode"],
    }
    return {
        "schema": SCHEMA,
        "record": "target",
        **core,
        "target_sha256": digest(core),
        "assignment": plan,
        "exact_checks": checks,
    }


def chip_column(u: np.ndarray, psi: np.ndarray) -> np.ndarray:
    return np.asarray(u[:, : bdsc.DIM] @ psi)


def ideal_probability(setting: bdsc.Setting) -> Fraction:
    """<psi|E0|psi> from the frame eigenvalues: lambda_i, or (lambda_i + lambda_j)/2 for a pair."""
    lam = [Fraction(0)] * 4 + [Fraction(1, 2)] * 8 + [Fraction(1)] * 4
    offset = 0 if setting.block == "A" else 4
    if setting.kind == "basis":
        return lam[offset + setting.i]
    return (lam[offset + setting.i] + lam[offset + setting.j]) / 2


def bank_record(target: dict[str, Any]) -> dict[str, Any]:
    u = numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    selected = target["selected_modes"]
    rows = []
    real = {s.name for s in bdsc.bank(real_only=True)}
    for s in bdsc.bank():
        psi = bdsc.state(s)
        column = chip_column(u, psi)
        exact = ideal_probability(s)
        share = float(np.sum(np.abs(column[selected]) ** 2))
        require(abs(share - float(exact)) < 1e-12, f"{s.name}: chip column selects {share}, frame gives {exact}")
        require(abs(float(np.vdot(column, column).real) - 1) < 1e-12, f"{s.name}: chip column is not normalized")
        rows.append(
            {
                "setting": s.name,
                "block": s.block,
                "kind": s.kind,
                "frame_indices": [s.i, s.j],
                "real_bank": s.name in real,
                "state_e_basis": complex_list(psi),
                "chip_column": complex_list(column),
                "ideal_selected": str(exact),
            }
        )
    body = {"settings": rows, "source_mode": target["source_mode"], "selected_modes": selected}
    return {
        "schema": SCHEMA,
        "record": "bank",
        "target_sha256": target["target_sha256"],
        "counts": {"A": 16, "C": 144, "total": len(rows), "real_bank": sum(r["real_bank"] for r in rows)},
        **body,
        "bank_sha256": digest(body),
    }


def pilot_record(target: dict[str, Any]) -> dict[str, Any]:
    u = numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    ideal = bdsc.pilot_probabilities(bdsc.ideal_effect())
    rows = []
    for s in bdsc.pilot_settings():
        rows.append(
            {
                "setting": s["name"],
                "pair": s["pair"],
                "angle": s["angle"],
                "state_e_basis": complex_list(s["state"]),
                "chip_column": complex_list(chip_column(u, s["state"])),
                "ideal_selected": round(ideal[s["name"]], 15),
            }
        )
    n = 10_000
    counts = {name: (int(round(p * n)), n) for name, p in ideal.items()}
    return {
        "schema": SCHEMA,
        "record": "pilot",
        "target_sha256": target["target_sha256"],
        "design": "y(theta) = cos(theta) k_i + phase sin(theta) f_j at 0, pi/2, +-pi/4 (estimator), +-pi/12 (held "
        "out) and pi/4 with phase +-i (imaginary response); pairs (k_1, f_9), (k_1, f_1), (k_1, f_10)",
        "implementation_equivalence": {
            "variants": [
                "the same chip column under compilation seeds drawn by scripts/anu_qrng.py at case generation",
                "the mirrored assignment: A and D roles of each output pair exchanged with the mask relabeled",
            ],
            "order": "randomized setting order with the k_1 and f_9 basis settings interleaved as references",
            "scope": "compares compilations of one label; label-dependent compilation remains the M4 premise",
        },
        "settings": rows,
        "ideal_readout_at_10000": bdsc.pilot_readout(counts, 0.01),
    }


# --- controls ------------------------------------------------------------------------------


def frozen_identity(target: dict[str, Any], n: int) -> dict[str, Any]:
    return {
        "target_sha256": target["target_sha256"],
        "bank_sha256": bank_record(target)["bank_sha256"],
        "selected_modes": target["selected_modes"],
        "alpha_allocation": ALLOCATION,
        "trials_per_setting": n,
    }


def conditioned_counts(target: dict[str, Any], n: int, seed: int, efficiency: list[float]) -> dict[str, Any]:
    """Detection-conditioned draws p_c = Tr(G rho)/Tr(D rho) under per-detector efficiencies."""
    u = numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    model = bdsc.acceptance(u, target["selected_modes"], efficiency)
    tau, delta = bdsc.scalar_deviation(model["D"])
    p = []
    for s in bdsc.bank():
        psi = bdsc.state(s)
        p.append(float(np.real(np.conj(psi) @ model["G"] @ psi) / np.real(np.conj(psi) @ model["D"] @ psi)))
    k = np.random.default_rng(seed).binomial(n, np.clip(p, 0, 1))
    counts = {s.name: (int(ki), n) for s, ki in zip(bdsc.bank(), k, strict=True)}
    return {"counts": counts, "tau": tau, "delta": delta, "effect": model["G"] / tau}


def perturbed_counts(effect: np.ndarray, n: int, seed: int, size: float) -> dict[str, tuple[int, int]]:
    """Label-dependent preparation error: each setting's state moves by a seeded vector of norm size."""
    rng = np.random.default_rng(seed)
    settings = bdsc.bank()
    draws = rng.normal(size=(len(settings), bdsc.DIM)) + 1j * rng.normal(size=(len(settings), bdsc.DIM))
    p = []
    for s, z in zip(settings, draws, strict=True):
        psi = bdsc.state(s) + size * z / np.linalg.norm(z)
        psi = psi / np.linalg.norm(psi)
        p.append(float(np.real(np.conj(psi) @ effect @ psi)))
    k = rng.binomial(n, np.clip(p, 0, 1))
    return {s.name: (int(ki), n) for s, ki in zip(settings, k, strict=True)}


def summary(result: dict[str, Any], truth: np.ndarray | None) -> dict[str, Any]:
    keep = ("a_U", "l_U", "gamma_L", "gamma_U", "a_L", "radius_A", "radius_C", "theta_max_bound_deg")
    out: dict[str, Any] = {"disposition": result["disposition"], "reasons": result.get("reasons", [])}
    for key in keep:
        if key in result:
            value = result[key]
            out[key] = None if value is None else round(float(value), 12)
    census = result.get("census")
    if census is not None:
        out["census"] = {
            "consistent": census["consistent"],
            "findings": census["findings"],
            **{key: round(float(census[key]), 12) for key in ("a_star", "c_L", "c_U", "U_5", "L_6", "U_6")},
        }
    if truth is not None and "a_U" in result:
        exact = bdsc.theorem_holds(truth)
        out["truth"] = {key: round(float(exact[key]), 12) for key in ("a", "gamma", "theta")}
        out["covered"] = bool(exact["a"] <= result["a_U"] + 1e-12 and exact["gamma"] >= result["gamma_L"] - 1e-12)
        upper = np.linalg.eigvalsh(truth)[bdsc.KERNEL_DIM :]
        intervals = result["census"]["lambda_5_to_16"]
        out["census_covered"] = bool(
            all(lo - 1e-12 <= x <= hi + 1e-12 for x, (lo, hi) in zip(upper, intervals, strict=True))
        )
    return out


def controls_record(target: dict[str, Any]) -> dict[str, Any]:
    n = CONTROL_TRIALS
    frozen = frozen_identity(target, n)
    jobs: list[ControlJob] = []

    def run(
        name: str,
        purpose: str,
        expected: str,
        record: dict[str, Any],
        truth: np.ndarray | None,
        identity: dict[str, Any] | None = None,
        findings: dict[str, str] | None = None,
    ) -> None:
        jobs.append((name, purpose, expected, record, truth, frozen if identity is None else identity, findings or {}))

    def counts(effect: np.ndarray, seed: int, real_only: bool = False) -> dict[str, tuple[int, int]]:
        return bdsc.sample_counts(effect, n, seed, real_only)

    e0 = bdsc.ideal_effect()
    no_fifth = {"target_alignment": "supported", "at_least_five_low": "refuted"}
    run("ideal", "E0 itself", "certified", bdsc.record_from_counts(counts(e0, 1), frozen), e0, findings=no_fifth)
    er = bdsc.extra_real_null()
    run(
        "extra_real_null",
        "E_R: a fifth null on (e1 - e2)/sqrt2",
        "alternative_structure",
        bdsc.record_from_counts(counts(er, 2), frozen),
        er,
        findings=FIVE_LOW,
    )
    ei = bdsc.extra_imag_null()
    run(
        "extra_imag_null",
        "E_I: a fifth null on (e1 + i e2)/sqrt2, complex bank",
        "alternative_structure",
        bdsc.record_from_counts(counts(ei, 3), frozen),
        ei,
        findings=FIVE_LOW,
    )
    real_counts = counts(ei, 3, real_only=True)
    support_but_real = {name: "supported" for name in bdsc.PREMISES}
    run(
        "extra_imag_null_real_bank",
        "E_I on the 88-setting bank without an established real effect",
        "inadmissible",
        bdsc.record_from_counts(real_counts, frozen, support_but_real, real_only=True),
        ei,
    )
    run(
        "extra_imag_null_real_bank_forced",
        "the same 88 settings with real_effect asserted: the false certificate the complex bank exists to prevent",
        "certified",
        bdsc.record_from_counts(real_counts, frozen, real_only=True),
        ei,
    )
    other = bdsc.kernel_other_spectrum()
    run(
        "kernel_other_spectrum",
        "exact kernel, complement spectrum 0.3..0.9",
        "certified",
        bdsc.record_from_counts(counts(other, 4), frozen),
        other,
    )
    small = bdsc.rotated(5.0)
    run(
        "rotated_5deg",
        "low space rotated 5 degrees toward f_9",
        "certified",
        bdsc.record_from_counts(counts(small, 5), frozen),
        small,
    )
    large = bdsc.rotated(30.0)
    run(
        "rotated_30deg",
        "low space rotated 30 degrees toward f_9",
        "alternative_structure",
        bdsc.record_from_counts(counts(large, 6), frozen),
        large,
        findings={"target_bright": "supported", "at_least_five_low": "refuted"},
    )
    dim = bdsc.attenuated(0.0606)
    run(
        "attenuated_unconditional",
        "F = 0.0606 E0 on an emitted-photon denominator",
        "not_certified",
        bdsc.record_from_counts(counts(dim, 7), frozen),
        dim,
    )
    deep = frozen_identity(target, DEEP_TRIALS)
    run(
        "attenuated_unconditional_deep",
        f"the same effect at {DEEP_TRIALS} trials: a common scale changes no disposition",
        "certified",
        bdsc.record_from_counts(bdsc.sample_counts(dim, DEEP_TRIALS, 7), deep),
        dim,
        deep,
    )
    for name, effect, expected, findings in (
        ("aligned_fifth_low", bdsc.diagonal_effect([0.05], 1.0), "certified", FIVE_LOW),
        ("five_designed_low", bdsc.diagonal_effect([0.02], 0.8), "certified", FIVE_LOW),
        ("six_designed_low", bdsc.diagonal_effect([0.02, 0.03], 0.8), "certified", SIX_LOW),
        ("coupled_complement_low", bdsc.coupled_complement_effect(), "not_certified", COUPLED_DEEP),
    ):
        run(
            f"{name}_deep",
            f"{name.replace('_', ' ')} at {DEEP_TRIALS} trials",
            expected,
            bdsc.record_from_counts(bdsc.sample_counts(effect, DEEP_TRIALS, 12), deep),
            effect,
            deep,
            findings,
        )
    fifth = bdsc.diagonal_effect([0.05], 1.0)
    run(
        "aligned_fifth_low",
        "diag(0^4, 0.05, 1^11) at the control n: eps_C does not resolve 0.05 against 0.1 c_L",
        "not_certified",
        bdsc.record_from_counts(counts(fifth, 12), frozen),
        fifth,
        findings={"at_least_five_low": "inconclusive"},
    )
    for beta, expected in ((0.002, "certified"), (0.05, "not_certified")):
        bg = bdsc.background(beta)
        run(
            f"background_{beta}",
            f"F = {beta} I + (1 - {beta}) E0: background stays in a",
            expected,
            bdsc.record_from_counts(counts(bg, 8), frozen),
            bg,
        )
    unsupported = {**support_but_real, "acceptance_model": "unsupported"}
    for floor, step, expected in ((0.98, 0.005, "certified"), (0.8, 0.05, "not_certified")):
        eta = [1.0] * MODES
        for j, mode in enumerate(target["selected_modes"][:4]):
            eta[mode] = floor + step * j
        conditioned = conditioned_counts(target, n, 9, eta)
        label = f"nonscalar_acceptance_{floor}"
        run(
            f"{label}_unbounded",
            f"bright-output efficiencies {floor}.. with the acceptance model unsupported",
            "inadmissible",
            bdsc.record_from_counts(conditioned["counts"], frozen, unsupported),
            None,
        )
        run(
            f"{label}_bounded",
            f"the same counts with the computed delta {conditioned['delta']:.6f}",
            expected,
            bdsc.record_from_counts(conditioned["counts"], frozen, conditioning_delta=conditioned["delta"]),
            conditioned["effect"],
        )
    for size, bound, expected in ((0.0005, 0.0011, "certified"), (0.02, 0.0404, "not_certified")):
        noisy = perturbed_counts(e0, n, 10, size)
        run(
            f"label_dependent_preparation_{size}",
            f"per-label state error of norm {size} with bias bound {bound}",
            expected,
            bdsc.record_from_counts(noisy, frozen, preparation_bias_bound=bound),
            e0,
        )
    base = bdsc.record_from_counts(counts(e0, 11), frozen)
    mutations = {
        "altered_detector_map": lambda r: r.__setitem__("selected_modes", list(reversed(r["selected_modes"]))),
        "missing_preparation": lambda r: r["rows"].pop(),
        "duplicated_preparation": lambda r: r["rows"].append(dict(r["rows"][0])),
        "invalid_trial_count": lambda r: r["rows"][0].__setitem__("selected", r["rows"][0]["eligible"] + 1),
        "changed_trial_count": lambda r: r["rows"][1].__setitem__("eligible", n - 1),
        "optional_stopping": lambda r: r.__setitem__("stopping", "until-certified"),
        "unbound_target": lambda r: r.__setitem__("target_sha256", "0" * 64),
        "unbound_bank": lambda r: r.__setitem__("bank_sha256", "0" * 64),
        "common_effect_unsupported": lambda r: r["premises"].__setitem__("common_effect", "unsupported"),
        "sampling_law_unsupported": lambda r: r["premises"].__setitem__("bernoulli_sampling", "unsupported"),
        "boolean_count": lambda r: r["rows"][2].__setitem__("selected", False),
        "nan_conditioning": lambda r: r.__setitem__("conditioning_delta", float("nan")),
        "negative_bias": lambda r: r.__setitem__("preparation_bias_bound", -0.5),
        "string_bias": lambda r: r.__setitem__("preparation_bias_bound", "0.1"),
        "row_not_object": lambda r: r["rows"].__setitem__(3, None),
        "premises_not_object": lambda r: r.__setitem__("premises", ["common_effect"]),
    }
    contradicted = bdsc.record_from_counts(
        {**counts(e0, 13), "C-basis-01": (0, n), "C-basis-02": (0, n), "C-real-01-02": (n, n)}, frozen
    )
    run(
        "range_contradiction",
        "p_1 = p_2 = 0 with p_(1+2) = 1: Re C_12 = 1 puts a C eigenvalue near -1, outside [0, 1] by more than eps_C",
        "inconsistent",
        contradicted,
        None,
        findings={"at_least_five_low": "unavailable", "target_alignment": "unavailable"},
    )
    for name, mutate in mutations.items():
        record = copy.deepcopy(base)
        mutate(record)
        run(name, "record or premise defect", "inadmissible", record, None)
    rows = parallel.ordered_map(_evaluate_control, jobs)
    for row in rows:
        require(row["disposition"] == row["expected"], f"control {row['control']} read {row['disposition']}")
        forced = row["control"].endswith("_forced")
        require(row.get("covered", True) or forced, f"control {row['control']} uncovered")
        require(row.get("census_covered", True) or forced, f"control {row['control']} census uncovered")
        for key, value in row.get("expected_findings", {}).items():
            got = row["census"]["findings"][key]
            require(got == value, f"control {row['control']}: {key} reads {got}, expected {value}")
    return {
        "schema": SCHEMA,
        "record": "controls",
        "target_sha256": target["target_sha256"],
        "bank_sha256": frozen["bank_sha256"],
        "trials_per_setting": n,
        "alpha_allocation": ALLOCATION,
        "dark_ratio": bdsc.DARK_RATIO,
        "target_ratio": bdsc.TARGET_RATIO,
        "low_ratio": bdsc.LOW_RATIO,
        "findings_schema": bdsc.FINDINGS_SCHEMA,
        "controls": rows,
        "exact_census": exact_census(),
        "coverage": coverage(target),
    }


ControlJob = tuple[str, str, str, dict[str, Any], np.ndarray | None, dict[str, Any], dict[str, str]]
FIVE_LOW = {"at_least_five_low": "supported", "exactly_five_low": "supported", "complement_low": "supported"}
SIX_LOW = {"at_least_five_low": "supported", "exactly_five_low": "refuted", "target_alignment": "supported"}
COUPLED_DEEP = {"at_least_five_low": "inconclusive", "target_alignment": "inconclusive"}


def _evaluate_control(job: ControlJob) -> dict[str, Any]:
    name, purpose, expected, record, truth, identity, findings = job
    result = bdsc.evaluate(record, identity)
    out = {"control": name, "purpose": purpose, "expected": expected, **summary(result, truth)}
    if findings:
        out["expected_findings"] = findings
    return out


def exact_census() -> list[dict[str, Any]]:
    """The algebraic layer: census findings on exact blocks at zero radius, independent of sampling."""
    fixtures: list[tuple[str, np.ndarray, float, dict[str, str]]] = [
        ("ideal", bdsc.ideal_effect(), 1.0, {"at_least_five_low": "refuted", "exactly_five_low": "refuted"}),
        ("extra_real_null", bdsc.extra_real_null(), 1.0, FIVE_LOW),
        ("extra_imag_null", bdsc.extra_imag_null(), 1.0, FIVE_LOW),
        (
            "coupled_complement_low",
            bdsc.coupled_complement_effect(),
            1.0,
            {"complement_low": "supported", "at_least_five_low": "inconclusive"},
        ),
        ("aligned_fifth_low", bdsc.diagonal_effect([0.05], 1.0), 1.0, FIVE_LOW),
        ("five_designed_low", bdsc.diagonal_effect([0.02], 0.5), 1.0, FIVE_LOW),
        ("six_designed_low", bdsc.diagonal_effect([0.02, 0.03], 0.5), 1.0, SIX_LOW),
        ("aligned_fifth_low_scaled", 0.0606 * bdsc.diagonal_effect([0.05], 1.0), 1.0, FIVE_LOW),
        ("above_unit_range", bdsc.diagonal_effect([0.05], 1.15), 1.2, FIVE_LOW),
        ("above_unit_range_capped_at_1", bdsc.diagonal_effect([0.05], 1.15), 1.0, {}),
    ]
    rows = []
    for name, effect, top, expected in fixtures:
        a, c = bdsc.blocks(effect)
        census = bdsc.certificate(bdsc.exact_bound(a), bdsc.exact_bound(c), top)["census"]
        eig = np.linalg.eigvalsh(effect)
        row = {
            "fixture": name,
            "effect_upper": top,
            "lambda_5": round(float(eig[4]), 12),
            "lambda_6": round(float(eig[5]), 12),
            "U_5": round(census["U_5"], 12),
            "L_6": round(census["L_6"], 12),
            "consistent": census["consistent"],
            "findings": census["findings"],
        }
        for key, value in expected.items():
            require(census["findings"][key] == value, f"exact census {name}: {key} reads {census['findings'][key]}")
        if census["consistent"]:
            intervals = census["lambda_5_to_16"]
            require(
                all(lo - 1e-12 <= x <= hi + 1e-12 for x, (lo, hi) in zip(eig[4:], intervals, strict=True)),
                f"exact census {name}: an eigenvalue leaves its interval",
            )
        rows.append(row)
    require(rows[3]["U_5"] == rows[3]["lambda_5"] == 0.18, "the coupled example attains lambda_5 = a + mu_1")
    require(rows[4]["findings"] == rows[7]["findings"], "a common scale changes an exact census finding")
    require(not rows[9]["consistent"] and all(v == "unavailable" for v in rows[9]["findings"].values()), "cap")
    return rows


def _coverage_replicate(item: tuple[str, int, int]) -> tuple[bool, bool]:
    name, n, seed = item
    effect = bdsc.background(0.01) if name == "background_0.01" else bdsc.ideal_effect()
    result = bdsc.analyze(bdsc.sample_counts(effect, n, seed), bdsc.ALPHA_ALLOCATIONS[ALLOCATION])
    exact = bdsc.theorem_holds(effect)
    return exact["a"] <= result["a_U"] + 1e-12, exact["gamma"] >= result["gamma_L"] - 1e-12


def coverage(target: dict[str, Any]) -> dict[str, Any]:
    items = [
        (name, COVERAGE_TRIALS, 1000 + r) for name in ("ideal", "background_0.01") for r in range(COVERAGE_REPLICATES)
    ]
    hits = parallel.ordered_map(_coverage_replicate, items)
    out: dict[str, Any] = {"trials_per_setting": COVERAGE_TRIALS, "replicates": COVERAGE_REPLICATES}
    for name in ("ideal", "background_0.01"):
        rows = [h for (label, _, _), h in zip(items, hits, strict=True) if label == name]
        out[name] = {"a_covered": sum(a for a, _ in rows), "gamma_covered": sum(g for _, g in rows)}
        require(out[name]["a_covered"] == out[name]["gamma_covered"] == COVERAGE_REPLICATES, f"{name} coverage")
    return out


# --- planning ------------------------------------------------------------------------------


def expected_counts(effect: np.ndarray, n: int) -> dict[str, tuple[int, int]]:
    p = bdsc.probabilities(effect, bdsc.bank())
    return {s.name: (int(round(pk * n)), n) for s, pk in zip(bdsc.bank(), p, strict=True)}


def _expected_reading(item: tuple[str, int, float]) -> dict[str, Any]:
    """The certificate of beta I + (1 - beta) E0 at expected counts under one allocation and trial count."""
    allocation, n, beta = item
    effect = bdsc.background(beta) if beta else bdsc.ideal_effect()
    return bdsc.analyze(expected_counts(effect, n), bdsc.ALPHA_ALLOCATIONS[allocation])


def _systematic_limit(item: tuple[int, str]) -> float:
    """The largest per-setting bias bound or acceptance delta under which E0's expected counts still certify."""
    n, key = item
    counts = expected_counts(bdsc.ideal_effect(), n)
    low, high = 0.0, 0.1
    for _ in range(40):
        mid = (low + high) / 2
        bias, conditioning = (mid, 0.0) if key == "preparation_bias_bound" else (0.0, mid)
        result = bdsc.analyze(counts, bdsc.ALPHA_ALLOCATIONS[ALLOCATION], bias=bias, conditioning=conditioning)
        low, high = (mid, high) if result["disposition"] == "certified" else (low, mid)
    return round(low, 9)


def resource_row(n: int) -> dict[str, Any]:
    per_setting = SECONDS_PER_ITERATION + SECONDS_PER_SAMPLE * n
    per_job = min(MAX_ITERATIONS, int(JOB_SECONDS // per_setting))
    settings = len(bdsc.bank())
    jobs = math.ceil(settings / per_job) if per_job else None
    credits = None if jobs is None else jobs * (CREDITS_PER_JOB + CREDITS_PER_SHOT * SHOT_HEADROOM * n)
    return {
        "eligible_trials_per_setting": n,
        "settings": settings,
        "seconds_per_setting": round(per_setting, 6),
        "settings_per_job": per_job,
        "jobs": jobs,
        "qpu_seconds": round(settings * per_setting, 3),
        "credits": None if credits is None else round(credits, 6),
        "months_at_explorer_credits": None if credits is None else math.ceil(credits / MONTHLY_CREDITS),
    }


def planning_record(target: dict[str, Any], catalogue: dict[str, Any]) -> dict[str, Any]:
    rows = bdsc.block_settings("C")
    d = bdsc.coefficients(rows)
    table = []
    for n, published in zip(bdsc.PLANNING_TRIALS, bdsc.PLANNING_RADII, strict=True):
        radius = bdsc.bernstein_radius(d, np.full(len(d), float(n)), bdsc.ALPHA_ALLOCATIONS["two-block"]["C"] / 2)
        require(round(radius, 6) == published, f"radius at n = {n} is {radius:.6f}, handoff {published}")
        table.append({"n": n, "total": n * len(d), "radius": round(radius, 12), "handoff": published})
    sin2 = math.sin(math.radians(bdsc.ANGLE_LIMIT_DEG)) ** 2
    n_min = math.ceil(math.log(0.025) / math.log(1 - 0.45 * sin2 / 4))
    require(n_min == 1086, f"zero-event trace route needs {n_min} trials, handoff 1086")
    ideal_items = [(allocation, n, 0.0) for allocation in bdsc.ALPHA_ALLOCATIONS for n in IDEAL_TIERS]
    background_items = [(ALLOCATION, n, beta) for beta in BACKGROUNDS for n in bdsc.PLANNING_TRIALS]
    floor_items = [(ALLOCATION, n, 0.0) for n in bdsc.PLANNING_TRIALS]
    readings = parallel.ordered_map(_expected_reading, ideal_items + background_items + floor_items)
    ideal_readings = readings[: len(ideal_items)]
    background_readings = readings[len(ideal_items) : len(ideal_items) + len(background_items)]
    floor_readings = readings[len(ideal_items) + len(background_items) :]
    ideal_rows = []
    for (allocation, n, _), r in zip(ideal_items, ideal_readings, strict=True):
        ideal_rows.append(
            {
                "allocation": allocation,
                "n": n,
                "a_U": round(r["a_U"], 12),
                "l_U": round(r["l_U"], 12),
                "gamma_L": round(r["gamma_L"], 12),
                "theta_max_bound_deg": None if r["theta_max_bound_deg"] is None else round(r["theta_max_bound_deg"], 9),
                "disposition": r["disposition"],
            }
        )
    background_rows = []
    for beta in BACKGROUNDS:
        tiers = [
            n
            for (_, n, b), r in zip(background_items, background_readings, strict=True)
            if b == beta and r["disposition"] == "certified"
        ]
        background_rows.append({"beta": beta, "smallest_certifying_n": tiers[0] if tiers else None})
    tolerance_items = [
        (n, key) for n in bdsc.PLANNING_TRIALS for key in ("preparation_bias_bound", "conditioning_delta")
    ]
    limits = parallel.ordered_map(_systematic_limit, tolerance_items)
    tolerance_rows = []
    for n in bdsc.PLANNING_TRIALS:
        row: dict[str, Any] = {"n": n}
        for (item_n, key), limit in zip(tolerance_items, limits, strict=True):
            if item_n == n:
                row[f"max_{key}"] = limit
        tolerance_rows.append(row)
    floors = [
        {"n": n, "min_lambda_min_C": round(min(r["a_U"], r["l_U"]) / sin2 + r["radius_C"], 12)}
        for (_, n, _), r in zip(floor_items, floor_readings, strict=True)
    ]
    witness_threshold = bdsc.LOW_RATIO * WITNESS_BRIGHT_LOWER
    witness_n = bdsc.zero_event_five_space_trials(witness_threshold, WITNESS_ALPHA)
    witness_bound = bdsc.five_space_witness(0, witness_n, WITNESS_ALPHA)["lambda_5_upper"]
    require(witness_n == 204 and round(witness_bound, 7) == 0.0896012, f"five-space witness {witness_n}")
    hoeffding = bdsc.hoeffding_consistency_trials(bdsc.CONSISTENCY_MARGIN, CASE_ALPHA)
    require(hoeffding == 22_689, f"Hoeffding consistency plan reads {hoeffding}")
    chip = catalogue["processors"][CHIP]["perfs"]
    u = numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    t_out = chip["Transmission per mode (%)"]["t_out"]
    _, delta_receipt = bdsc.scalar_deviation(bdsc.acceptance(u, target["selected_modes"], t_out)["D"])
    return {
        "schema": SCHEMA,
        "record": "planning",
        "target_sha256": target["target_sha256"],
        "confidence": {
            "allocations": bdsc.ALPHA_ALLOCATIONS,
            "frozen_allocation": ALLOCATION,
            "split": "each block's alpha divides evenly between Clopper-Pearson propagation and matrix Bernstein; "
            "the smaller radius is reported, and the union bound covers that choice",
        },
        "complement_radius_table": table,
        "complement_radius_note": "the handoff table is matrix Bernstein on the 144 C settings at alpha_B = 0.0125, "
        "half of alpha_C = 0.025, m = 12",
        "trace_route": {
            "n_min": n_min,
            "alpha_K": 0.025,
            "gamma_L": 0.45,
            "premise": "zero selected events among n eligible trials of the randomized kernel ensemble",
            "belenos_status": "implausible on qpu:belenos: off-cone one-click samples on modes 0, 1 and 5 come and go "
            "at up to thousands per 40000-sample iteration (strategy.md section 2), and the 12/12 mask uses all 24 "
            "detectors, so a zero-event record cannot be planned for",
        },
        "five_space_witness": {
            "bound": "lambda_5(F) <= lambda_max(S F S) <= Tr(S F) = 5 r_5, S = P + |q><q| for a unit q in Q",
            "bright_reference_lower": WITNESS_BRIGHT_LOWER,
            "threshold": round(witness_threshold, 12),
            "alpha_one_sided": WITNESS_ALPHA,
            "zero_event_trials": witness_n,
            "lambda_5_upper_at_zero_events": round(witness_bound, 12),
            "scope": "conditional on genuine Bernoulli trials of one effect and an independently measured bright "
            "reference; excludes the reference acquisition, preparation calibration and qualification; zero events "
            "on qpu:belenos cannot be promised, and approximate conditioning adds (1 + delta) and the bias bound",
        },
        "consistency_hoeffding": {
            "margin": bdsc.CONSISTENCY_MARGIN,
            "alpha": CASE_ALPHA,
            "trials_per_preparation": hoeffding,
            "rule": "n >= 8 log(12 / alpha) / m^2: six probabilities under a union bound, four per residual",
            "scope": "the n at which the residual half-width equals the margin, a floor with no power: a compatible "
            "reading also needs the estimate inside the remaining band; qualification_case.json's power table sets n",
        },
        "ideal_effect_expected_counts": ideal_rows,
        "required_complement_floor": floors,
        "systematic_tolerance": {
            "model": "E0 at expected counts; the largest per-setting bias bound, or acceptance delta, that still "
            "certifies; both propagate as independent worst-case shifts through the |D_s| row sums",
            "rows": tolerance_rows,
        },
        "background_sensitivity": {
            "model": "F = beta I + (1 - beta) E0, expected counts, frozen allocation, planning tiers",
            "rows": background_rows,
        },
        "resources_historical": {
            "rates": {
                "seconds_per_iteration": SECONDS_PER_ITERATION,
                "seconds_per_sample": SECONDS_PER_SAMPLE,
                "job_seconds": JOB_SECONDS,
                "max_iterations": MAX_ITERATIONS,
                "credits": "1 per job plus 1e-6 per shot of the largest iteration, max_shots = 2 x samples",
                "monthly_credits": MONTHLY_CREDITS,
                "source": "docs/notes/quandela/strategy.md section 1a (jobs c2eea262, c1eb1cbb, b8e2ec0c)",
            },
            "rows": [resource_row(n) for n in bdsc.PLANNING_TRIALS],
            "caveat": "detection-conditioned samples whose independence, processing (DetectorBalancing) and trial "
            "semantics are unqualified (M3); historical rates, not a current quote",
        },
        "snapshot_comparison": {
            "handoff": HANDOFF_SNAPSHOT,
            "retained_catalogue": {
                "retrieved_utc": catalogue["retrieved_utc"],
                "transmittance_percent": chip["Transmittance (%)"],
                "hom_percent": chip["HOM (%)"],
                "g2_percent": chip["g2 (%)"],
                "dark_mode5_per_s": chip["Dark counts (detection/s)"][5],
            },
            "note": "sim:belenos's default noise model carries transmittance 0.06 (strategy.md section 2); "
            "neither snapshot bounds gamma",
        },
        "acceptance_under_receipt_t_out": {
            "delta": round(delta_receipt, 12),
            "reading": "taking the receipt t_out as relative detector efficiencies, the acceptance effect deviates "
            "from scalar by this delta; the receipt contradicts the detected light (strategy.md section 2), so the "
            "acceptance model stays unqualified",
        },
    }


# --- qualification -------------------------------------------------------------------------


def qualification_record(target: dict[str, Any], controls: dict[str, Any], planning: dict[str, Any]) -> dict[str, Any]:
    strategy = "docs/notes/quandela/strategy.md"
    conversion = json.loads((ROOT / "docs/evidence/bdsc/packages/packages.json").read_text(encoding="utf-8"))[
        "conversion"
    ]
    converted_zero = conversion["zero_draws"] / conversion["draws"]
    binomial_zero = (1 - conversion["p"]) ** conversion["count"]
    milestones = [
        {"milestone": "M0", "status": "passed", "evidence": "target.json exact_checks (Fractions)"},
        {
            "milestone": "M1",
            "status": "passed",
            "evidence": "target.json U24^T U24 = I and compression = E0 in Q(sqrt2)",
        },
        {
            "milestone": "M2",
            "status": "blocked",
            "evidence": f"{strategy} sections 4 and 7: the service re-transpiles every circuit (jobs 1d7160c1, "
            "e5b74123): all 574 phases change and only the occupied column survives",
            "consequence": "a one-photon setting reaches the chip as the column U24 psi_s alone; no fixed measurement "
            "stage exists to separate from the preparation",
        },
        {
            "milestone": "M3",
            "status": "blocked",
            "evidence": f"{strategy} section 2: DetectorBalancing is the default mitigation; physical_perf follows "
            "the requested budget; off-cone clicks on modes 0, 1 and 5 have no model; the receipt t_out and dark rates "
            "contradict the detected light. docs/evidence/bdsc/packages/packages.json: Perceval 1.3.1's "
            "probs_to_sample_count, the conversion DetectorBalancing ends in, reads a zero-count frequency of "
            f"{converted_zero:.3f} against the binomial {binomial_zero:.3f} at p = {conversion['p']:g} and "
            f"n = {conversion['count']}, so converted counts are not Bernoulli trials",
            "acceptance_delta_under_receipt": planning["acceptance_under_receipt_t_out"]["delta"],
        },
        {
            "milestone": "M4",
            "status": "blocked",
            "evidence": "the compiled mesh, and with it the chip's error channel, is a function of the target column, "
            "which is a function of the preparation label; the label-independent weights of a common averaged effect "
            "fail by construction, and compilation seeds randomize within a label only",
        },
        {
            "milestone": "M5",
            "status": "not_started",
            "evidence": "pilot.json design; acquisition needs an approved case",
        },
        {"milestone": "M6", "status": "not_started", "evidence": "requires M3 and M4"},
        {"milestone": "M7", "status": "not_started", "evidence": "requires M3 and M4"},
        {"milestone": "M8", "status": "not_started", "evidence": "requires M6 and M7"},
        {"milestone": "M9", "status": "not_started", "evidence": "requires M8"},
    ]
    return {
        "schema": SCHEMA,
        "record": "qualification",
        "target_sha256": target["target_sha256"],
        "milestones": milestones,
        "first_unsupported_premise": "M2",
        "provider_contract": "provider_contract.json",
        "next_case": "qualification_case.json",
        "synthetic_validation": {
            "controls": len(controls["controls"]),
            "all_expected": all(r["disposition"] == r["expected"] for r in controls["controls"]),
            "scope": "the analysis procedure under its assumptions; no hardware certificate",
        },
        "authorization": "no acquisition, upload or cloud submission is authorized by these records",
    }


# --- provider contract and qualification case ---------------------------------------------


def provider_contract_record(target: dict[str, Any]) -> dict[str, Any]:
    """Each capability the certificate needs from the provider, its status on this account and its question."""
    strategy = "docs/notes/quandela/strategy.md"
    items = [
        (
            "full_transform_preservation",
            "M2",
            "unsupported on the tested routes",
            f"{strategy} sections 4 and 9: sim:belenos jobs 1d7160c1 and e5b74123 kept only the occupied column; "
            "qpu:belenos meshes follow the body and the compilation seed",
            "Can a requested 24-mode transformation, or the induced effect J^dagger T^dagger Q_A T J on the logical "
            "inputs, be preserved through compilation on qpu:belenos?",
        ),
        (
            "native_configuration_replay",
            "M2",
            "unresolved",
            "no documented no_transpile parameter; none is assumed",
            "Can a native architecture configuration (phase settings) run without state-specific optimization, and "
            "be replayed unchanged across jobs?",
        ),
        (
            "preparation_control",
            "M2, M4",
            "unresolved",
            "a one-photon body reaches the chip as its occupied column, so preparation and readout are one request",
            "Can coherent inputs be prepared independently of a fixed readout stage, and how is the preparation "
            "error bounded?",
        ),
        (
            "returned_circuit_semantics",
            "M2",
            "unresolved",
            "returned meshes are compared as declared matrices; their physical realization is uncalibrated",
            "What does a returned compiled circuit describe: the configuration applied, a nominal model, or a "
            "post-hoc fit?",
        ),
        (
            "uncorrected_observations",
            "M3",
            "unresolved",
            "Perceval 1.3 documents mitigations=[] as disabling remote mitigation; the empty list reaching the server "
            "is shown for Perceval 1.3.1 PayloadGenerator, its effect on this account is untested",
            "Does an empty mitigation list return aggregated genuine detector events, and which filtering precedes "
            "them?",
        ),
        (
            "count_provenance",
            "M3",
            "unsupported under defaults",
            "docs/evidence/bdsc/packages/packages.json: the default DetectorBalancing path ends in a probability to "
            "count conversion whose zero-count law differs from the binomial",
            "Are returned counts aggregated events or reconstructed from probabilities; are samples in physical order; "
            "what do shot, sample and eligible trial mean; which rejected and no-click categories exist?",
        ),
        (
            "processing_versions",
            "M3",
            "partially recorded",
            "the frozen receipt names server Perceval 1.3.0; the server route of a run is bound per run",
            "Which server software version and correction calibration produced each result?",
        ),
        (
            "processor_record_completeness",
            "M2, M3",
            "unsupported since 2026-10-20",
            "qpu:belenos records of 2026-10-20 and 2026-10-21 lack specs.architecture, commands, default_mitigations, "
            "known_mitigations and type at unchanged software versions, while qpu:ascella and sim:belenos carry them "
            "(docs/notes/quandela/calibration.md open item 1); Perceval then treats requested mitigations as unknown "
            "and the server default as none",
            "Why does the qpu:belenos processor record omit these five fields, and which mitigations does the server "
            "apply when a request carries none?",
        ),
        (
            "acceptance_calibration",
            "M3",
            "unsupported",
            "the receipt t_out taken as efficiencies gives delta about 0.97 and contradicts the detected light; "
            "off-cone clicks have no model",
            "Are per-detector efficiencies, dark counts, dead time and multi-photon threshold behavior available "
            "for the selected outputs, at the run's calibration?",
        ),
    ]
    return {
        "schema": SCHEMA,
        "record": "provider_contract",
        "target_sha256": target["target_sha256"],
        "platform": CHIP,
        "capabilities": [
            {"capability": name, "milestones": milestones, "status": status, "evidence": evidence, "question": q}
            for name, milestones, status, evidence, q in items
        ],
        "resolution": "a capability reads supported only from a provider statement bound to this account or a "
        "qualification run; the abstract Experiment representation and local SLOS execution establish none",
    }


# A template is a fixed 24-mode circuit of beam splitters on adjacent modes and phase shifters whose parameters each
# iteration of a job binds: ("BS", m, k) acts on modes (m, m + 1) with angle params[k], ("BS", m, None) with angle pi,
# and ("PS", m, k) multiplies mode m by exp(i params[k]). BS(theta) is [[cos(theta/2), i sin(theta/2)],
# [i sin(theta/2), cos(theta/2)]], Perceval's BS.Rx convention, which the case builder checks against Perceval.
TemplateOp = tuple[str, int, int | None]


def template_ops(name: str, source: int) -> list[TemplateOp]:
    """outward-ladder splits the photon from the source to its left and right neighbours in turn; reverse-ladder
    swaps two unused inputs, transfers the photon to mode 0 through fixed full splitters and then ladders it
    rightward across every mode."""
    ops: list[TemplateOp] = []
    count = 0

    def bs(m: int, fixed: bool = False) -> None:
        nonlocal count
        ops.append(("BS", m, None if fixed else count))
        count += 0 if fixed else 1

    if name == "outward-ladder":
        if source > 0:
            bs(source - 1)
        for m in range(source - 1, 0, -1):
            bs(m - 1)
        for m in range(source, MODES - 1):
            bs(m)
    elif name == "reverse-ladder":
        # A fixed full splitter on two unused inputs comes first: it moves no photon, and it keeps the template's
        # action on the unused columns distinct from outward-ladder even where both ladders reduce to transfers.
        bs(0 if source > 1 else MODES - 2, fixed=True)
        for m in range(source, 0, -1):
            bs(m - 1, fixed=True)
        for m in range(MODES - 1):
            bs(m)
    else:
        raise ValueError(f"unknown template {name}")
    for m in range(MODES):
        ops.append(("PS", m, count))
        count += 1
    return ops


def template_unitary(ops: list[TemplateOp], params: np.ndarray) -> np.ndarray:
    u = np.eye(MODES, dtype=complex)
    for kind, m, k in ops:
        g = np.eye(MODES, dtype=complex)
        if kind == "BS":
            t = math.pi if k is None else float(params[k])
            c, sn = math.cos(t / 2), math.sin(t / 2)
            g[m, m], g[m, m + 1], g[m + 1, m], g[m + 1, m + 1] = c, 1j * sn, 1j * sn, c
        else:
            g[m, m] = complex(math.cos(float(params[k])), math.sin(float(params[k])))
        u = g @ u
    return u


def template_params(name: str, column: np.ndarray, source: int) -> np.ndarray:
    """Angles that put |column_m|^2 on every mode m, then phases that give each mode the column's argument.

    A ladder splitter keeps cos^2(theta/2) of its carrier's weight on mode m and passes sin^2(theta/2) on, so
    theta = 2 atan2(sqrt(passed), sqrt(kept)) with both weights summed directly from the column; the left split of
    outward-ladder passes the weight of every mode below the source. atan2 of the two square roots keeps full
    precision where acos or asin of a ratio near 1 would lose half its digits.
    """
    weight = np.abs(column) ** 2
    ops = template_ops(name, source)
    params = np.zeros(sum(1 for _, _, k in ops if k is not None))

    def angle(passed: float, kept: float) -> float:
        return 2 * math.atan2(math.sqrt(passed), math.sqrt(kept)) if passed + kept > 0 else 0.0

    slots = iter(k for kind, _, k in ops if kind == "BS" and k is not None)
    if name == "outward-ladder":
        if source > 0:
            params[next(slots)] = angle(float(weight[:source].sum()), float(weight[source:].sum()))
        for m in range(source - 1, 0, -1):
            params[next(slots)] = angle(float(weight[:m].sum()), float(weight[m]))
        for m in range(source, MODES - 1):
            params[next(slots)] = angle(float(weight[m + 1 :].sum()), float(weight[m]))
    else:
        for m in range(MODES - 1):
            params[next(slots)] = angle(float(weight[m + 1 :].sum()), float(weight[m]))
    reached = template_unitary(ops, params)[:, source]
    for kind, m, k in ops:
        if kind == "PS" and k is not None and abs(column[m]) > 1e-12:
            params[k] = float(np.angle(column[m]) - np.angle(reached[m]))
    return params


CaseItem = tuple[str, np.ndarray, int]


def _case_bank(item: CaseItem) -> dict[str, Any]:
    """One pair's six states with chip columns, the distance between the two completions on the unused columns,
    and the ideal responses of E0, E_R and E_I; every variant cell of the pair prepares these states."""
    pair, u, source = item
    frames = {"K": bdsc.kernel_frame(), "Q": bdsc.complement_frame()}
    fb, fi, gb, gi = CASE_PAIRS[pair]
    f, g = frames[fb][:, fi].astype(complex), frames[gb][:, gi].astype(complex)
    rows: list[dict[str, Any]] = []
    for label, psi in bdsc.consistency_states(f, g).items():
        column = chip_column(u, psi)
        body = {}
        for name in PREPARATION_DESCRIPTIONS:
            w = template_unitary(template_ops(name, source), template_params(name, column, source))
            require(np.allclose(w[:, source], column, rtol=0, atol=1e-12), f"{name} template misses the column")
            body[name] = np.delete(w, source, axis=1)
        rows.append(
            {
                "label": label,
                "state_e_basis": complex_list(psi),
                "chip_column": complex_list(column),
                "unused_column_distance": round(
                    float(np.linalg.norm(body[PREPARATION_DESCRIPTIONS[0]] - body[PREPARATION_DESCRIPTIONS[1]])), 9
                ),
                "ideal_selected": {
                    name: round(float(np.real(np.conj(psi) @ effect @ psi)), 12)
                    for name, effect in (
                        ("E0", bdsc.ideal_effect()),
                        ("E_R", bdsc.extra_real_null()),
                        ("E_I", bdsc.extra_imag_null()),
                    )
                },
            }
        )
    for name in ("E0", "E_R", "E_I"):
        p = {r["label"]: r["ideal_selected"][name] for r in rows}
        require(abs(p["+"] + p["-"] - p["f"] - p["g"]) < 1e-12, f"{pair} {name}: real sum rule")
        require(abs(p["+i"] + p["-i"] - p["f"] - p["g"]) < 1e-12, f"{pair} {name}: imaginary sum rule")
    return {"pair": pair, "f_g": [f"{fb}{fi + 1}", f"{gb}{gi + 1}"], "settings": rows}


def case_jobs(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One job per (template, policy, epoch): a job fixes its circuit and its mitigation list, and its iterations
    bind each observation's template parameters, so the 12 states of both pairs share it."""
    out = []
    for d in PREPARATION_DESCRIPTIONS:
        for policy in PROCESSING_POLICIES:
            for epoch in CASE_EPOCHS:
                members = [
                    j
                    for j, o in enumerate(observations)
                    if (o["preparation"], o["processing"], o["epoch"]) == (d, policy, epoch)
                ]
                out.append({"template": d, "processing": policy, "epoch": epoch, "iterations": members})
    return out


def case_observations() -> list[dict[str, Any]]:
    """Every acquired setting, ordered pair, completion, policy, epoch, label: both epochs repeat all six states, so
    the epoch comparison reaches the off-diagonal response that f and g alone cannot see."""
    return [
        {"pair": pair, "preparation": d, "processing": policy, "epoch": epoch, "label": label}
        for pair in CASE_PAIRS
        for d in PREPARATION_DESCRIPTIONS
        for policy in PROCESSING_POLICIES
        for epoch in CASE_EPOCHS
        for label in bdsc.CONSISTENCY_LABELS
    ]


def case_contrasts(observations: list[dict[str, Any]]) -> list[bdsc.Contrast]:
    """Within-cell sum rules, cross-completion differences at one policy and epoch, and cross-epoch differences at
    one completion and policy. No contrast compares processing policies, whose means may differ by design."""
    index = {
        (o["pair"], o["preparation"], o["processing"], o["epoch"], o["label"]): j for j, o in enumerate(observations)
    }
    out: list[bdsc.Contrast] = []
    for pair in CASE_PAIRS:
        for d in PREPARATION_DESCRIPTIONS:
            for policy in PROCESSING_POLICIES:
                for epoch in CASE_EPOCHS:

                    def at(label: str, pair: str = pair, d: str = d, policy: str = policy, epoch: int = epoch) -> int:
                        return index[(pair, d, policy, epoch, label)]

                    for plus, minus in (("+", "-"), ("+i", "-i")):
                        terms = ((at(plus), 1.0), (at(minus), 1.0), (at("f"), -1.0), (at("g"), -1.0))
                        out.append(("sum_rule", CASE_MARGINS["sum_rule"], terms))
        for policy in PROCESSING_POLICIES:
            for epoch in CASE_EPOCHS:
                for label in bdsc.CONSISTENCY_LABELS:
                    h = index[(pair, PREPARATION_DESCRIPTIONS[0], policy, epoch, label)]
                    g = index[(pair, PREPARATION_DESCRIPTIONS[1], policy, epoch, label)]
                    out.append(("completion", CASE_MARGINS["completion"], ((h, 1.0), (g, -1.0))))
        for d in PREPARATION_DESCRIPTIONS:
            for policy in PROCESSING_POLICIES:
                for label in bdsc.CONSISTENCY_LABELS:
                    late, early = (index[(pair, d, policy, e, label)] for e in (2, 1))
                    out.append(("epoch", CASE_MARGINS["epoch"], ((late, 1.0), (early, -1.0))))
    return out


PowerItem = tuple[int, tuple[float, ...], tuple[bdsc.Contrast, ...]]


def _case_power(item: PowerItem) -> int:
    """Replicates of CASE_POWER_REPLICATES ideal records at n trials whose every contrast reads compatible.

    The record draws from its own generator seeded by (CASE_POWER_SEED, n), so the pool and the serial loop agree.
    """
    n, probabilities, contrasts = item
    rng = np.random.default_rng([CASE_POWER_SEED, n])
    k = rng.binomial(n, np.broadcast_to(probabilities, (CASE_POWER_REPLICATES, len(probabilities))))
    status = bdsc.contrast_readout(k, np.full(k.shape, n), contrasts, CASE_ALPHA)["status"]
    return int(np.sum(np.all(status == "compatible", axis=1)))


def qualification_case_record(target: dict[str, Any]) -> dict[str, Any]:
    u = numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    banks = parallel.ordered_map(_case_bank, [(pair, u, target["source_mode"]) for pair in CASE_PAIRS])
    for bank in banks:
        for row in bank["settings"]:
            require(row["unused_column_distance"] > 0.1, f"{bank['pair']} {row['label']}: the completions coincide")
    ideal = {(b["pair"], r["label"]): r["ideal_selected"]["E0"] for b in banks for r in b["settings"]}
    observations = case_observations()
    contrasts = case_contrasts(observations)
    probabilities = tuple(ideal[(o["pair"], o["label"])] for o in observations)
    grid = (CASE_REFERENCE_TRIALS, *CASE_TRIAL_GRID)
    # Each item is a whole replicate batch of Clopper-Pearson quantiles, so one item already repays a worker.
    passes = parallel.ordered_map(_case_power, [(n, probabilities, tuple(contrasts)) for n in grid], min_items=1)
    power = {n: hits / CASE_POWER_REPLICATES for n, hits in zip(grid, passes, strict=True)}
    chosen = [n for n in CASE_TRIAL_GRID if power[n] >= CASE_POWER_TARGET]
    require(bool(chosen), "no trial count on the grid reaches the power target")
    trials = chosen[0]
    settings = len(observations)
    max_shots = SHOT_HEADROOM * trials
    jobs = case_jobs(observations)
    iterations = max(len(job["iterations"]) for job in jobs)
    seconds_per_job = iterations * (SECONDS_PER_ITERATION + SECONDS_PER_SAMPLE * trials)
    require(
        seconds_per_job <= CASE_JOB_FILL * JOB_SECONDS, f"a job of {iterations} iterations needs {seconds_per_job} s"
    )
    credits = len(jobs) * (CREDITS_PER_JOB + CREDITS_PER_SHOT * max_shots)
    credits_one_job_per_setting = settings * (CREDITS_PER_JOB + CREDITS_PER_SHOT * max_shots)
    families = {f: sum(c[0] == f for c in contrasts) for f in CASE_MARGINS}
    return {
        "schema": SCHEMA,
        "record": "qualification_case",
        "target_sha256": target["target_sha256"],
        "question": "do the returned observations behave as one fixed linear effect on independently prepared "
        "states, at a declared observation level, across preparation descriptions and across a calibration change",
        "claims": {
            "findings_schema": bdsc.FINDINGS_SCHEMA,
            "alpha": CASE_ALPHA,
            "confidence_event": "Clopper-Pearson at alpha / P on each of the P observations; every contrast "
            "interval follows from the same event, so false certification of any contrast family is bounded by alpha",
            "margins": CASE_MARGINS,
            "contrast_families": families,
            "outcomes": ["compatible", "violated", "inconclusive", "not_admitted"],
            "admission": "an observation enters the event only when its policy's observation contract supports "
            "Bernoulli trials; the alpha split counts every observation, so admission never re-allocates error, and "
            "a contrast touching an unadmitted observation reads not_admitted",
            "policies": "no contrast compares provider defaults with the empty list: correction may change the mean; "
            "the live qpu:belenos record declares no default mitigation, so the default policy's processing is read "
            "from each result's metadata, not from the record",
            "epochs": "epoch 2 follows at least one platform calibration cycle, so the epoch family tests "
            "reproducibility across a calibration change; within-epoch stability rests on the randomized order alone, "
            "and the epochs are never pooled into one stationary reconstruction",
            "scope": "passing every family is necessary and not sufficient: a service that prepares "
            "sqrt(p_s)|A> + sqrt(1 - p_s)|D> for each requested p_s passes them without a fixed measurement",
        },
        "banks": banks,
        "preparation_descriptions": {
            "outward-ladder": "adjacent splitters fan the photon from the source mode to its left and right "
            "neighbours in turn, then one phase per mode; 47 parameters",
            "reverse-ladder": "a fixed full splitter on two unused inputs, fixed full splitters that carry the "
            "photon to mode 0, adjacent splitters that ladder it rightward across every mode, then one phase per "
            "mode; 47 parameters",
        },
        "observations": observations,
        "power": {
            "model": "the acceptable implementation: E0 itself, one effect across completions, policies and epochs, "
            "independent fixed-n Bernoulli trials at every observation",
            "decision": "every contrast of every family reads compatible",
            "target": CASE_POWER_TARGET,
            "replicates": CASE_POWER_REPLICATES,
            "seed": CASE_POWER_SEED,
            "rows": [{"trials_per_setting": n, "power": power[n]} for n in grid],
            "chosen_trials": trials,
            "scope": "power under this model only; drift, preparation error or a corrected sampling law lower it",
        },
        "acquisition": {
            "trials_per_setting": trials,
            "epochs": [
                {"epoch": e, "settings": settings // len(CASE_EPOCHS), "content": "all six states of every cell"}
                for e in CASE_EPOCHS
            ],
            "randomized_and_retained": [
                "preparation label",
                "compilation seed",
                "processing policy",
                "acquisition order",
                "epoch",
            ],
            "stopping": bdsc.STOPPING,
        },
        "jobs": jobs,
        "resources": {
            "settings": settings,
            "jobs": len(jobs),
            "iterations_per_job": iterations,
            "eligible_trials_per_setting": trials,
            "eligible_trials_total": settings * trials,
            "max_shots_per_iteration": max_shots,
            "max_shots_total": settings * max_shots,
            "credits": round(credits, 6),
            "credits_if_one_job_per_setting": round(credits_one_job_per_setting, 6),
            "seconds_per_job_estimate": round(seconds_per_job, 3),
            "seconds_estimate": round(len(jobs) * seconds_per_job, 3),
            "seconds_ceiling": len(jobs) * JOB_SECONDS,
            "billing_rule": "1 credit per job plus 1e-6 per shot of the job's largest iteration max_shots, measured "
            "on every retained qpu:belenos job (docs/runbooks/quandela-credit-optimization.md)",
            "timing_rule": f"{SECONDS_PER_ITERATION} s plus {SECONDS_PER_SAMPLE} s per sample for each iteration, "
            f"each job within {CASE_JOB_FILL} of the {JOB_SECONDS} s per-job limit; the written case restates "
            "both from the live plan output",
        },
        "qrng": {
            "service": "ANU Quantum Numbers (aqn, keyed), scripts/anu_qrng.py draw",
            "requests": 1,
            "values": QRNG_VALUES,
            "type": "uint16",
            "use": "the first settings values seed each setting's compilation_seed in observation order; the next "
            "settings values sort each epoch's acquisition order",
            "expected_seconds": 2,
            "credits": 0,
            "quota": "1 of the free tier's 100 requests per calendar month",
            "why_not_simulated": "the seed rule of strategy.md section 1 takes compilation seeds from a retained "
            "quantum draw so that neither the operator nor a pseudorandom stream fixes which meshes the case meets",
        },
        "stop_conditions": [
            "scripts/qd_platform.py plan refuses the platform",
            "a returned result's processing differs from the requested policy",
            "a job fails or returns fewer eligible trials than the frozen n",
            "the per-run server version or calibration identity cannot be recorded",
            "spent credits or seconds reach the approved ceiling",
        ],
        "interpretation": [
            {"family": "completion", "implicates": "preparation, compilation or both"},
            {"family": "epoch", "implicates": "reproducibility across the calibration change"},
            {
                "family": "sum_rule",
                "implicates": "the combined linear-effect, preparation and conditioning model, without a unique cause",
            },
            {"family": "policies", "implicates": "what each output represents, read from metadata, not means"},
        ],
        "authorization": "none: the case waits for its written-case approval; a pass supports proposing the "
        "160-setting run, never running it",
    }


# --- documents -----------------------------------------------------------------------------


def documents() -> dict[str, str]:
    catalogue = load_catalogue()
    target = target_record(catalogue)
    bank = bank_record(target)
    pilot = pilot_record(target)
    controls = controls_record(target)
    planning = planning_record(target, catalogue)
    qualification = qualification_record(target, controls, planning)
    contract = provider_contract_record(target)
    case = qualification_case_record(target)
    records = {
        "target.json": target,
        "bank.json": bank,
        "pilot.json": pilot,
        "controls.json": controls,
        "planning.json": planning,
        "qualification.json": qualification,
        "provider_contract.json": contract,
        "qualification_case.json": case,
    }
    return {name: json.dumps(value, indent=1, sort_keys=True) + "\n" for name, value in records.items()}


def close(a: Any, b: Any, path: str = "") -> None:
    if isinstance(a, float) or isinstance(b, float):
        require(isinstance(a, int | float) and isinstance(b, int | float), f"{path}: {a!r} against {b!r}")
        require(abs(a - b) <= CHECK_TOLERANCE * max(1.0, abs(a), abs(b)), f"{path}: {a} against {b}")
    elif isinstance(a, dict):
        require(isinstance(b, dict) and sorted(a) == sorted(b), f"{path}: keys differ")
        for key in a:
            close(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list):
        require(isinstance(b, list) and len(a) == len(b), f"{path}: lengths differ")
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            close(x, y, f"{path}[{i}]")
    else:
        require(a == b, f"{path}: {a!r} against {b!r}")


def write(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in documents().items():
        (directory / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(FILES)} bdsc records under {directory}")


def check(directory: Path) -> None:
    fresh = documents()
    retained = sorted(p.name for p in directory.glob("*.json"))
    require(retained == sorted(FILES), f"record set differs: {retained}")
    for name in FILES:
        close(json.loads(fresh[name]), json.loads((directory / name).read_text(encoding="utf-8")), name)
    target = json.loads((directory / "target.json").read_text(encoding="utf-8"))
    core = {
        key: target[key]
        for key in target
        if key not in ("schema", "record", "target_sha256", "assignment", "exact_checks")
    }
    require(digest(core) == target["target_sha256"], "target_sha256 does not match the retained target")
    print(f"bdsc records: {len(FILES)} files match; target {target['target_sha256'][:12]}")


# --- self-test -----------------------------------------------------------------------------


def _random_effect(seed: int) -> np.ndarray:
    """A random effect near E0: a random unitary tilt of its frame and random eigenvalues in [0, 1]."""
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(bdsc.DIM, bdsc.DIM)) + 1j * rng.normal(size=(bdsc.DIM, bdsc.DIM))
    h = (z + z.conj().T) * rng.uniform(0.0, 0.05)
    w, v = np.linalg.eigh(h)
    tilt = v @ np.diag(np.exp(1j * w)) @ v.conj().T
    low = rng.uniform(0.0, 0.1, size=4)
    high = rng.uniform(0.2, 1.0, size=12)
    frame = tilt @ bdsc.full_frame()
    return np.asarray(frame @ np.diag(np.concatenate([low, high])) @ frame.conj().T)


def _tight_effect(seed: int) -> np.ndarray:
    """F = gamma (I - P~) + eps P~ with P~ the kernel rotated toward the bright partners: sin^2 theta near a/gamma."""
    rng = np.random.default_rng(seed)
    k, q = bdsc.kernel_frame(), bdsc.complement_frame()
    low = np.zeros((bdsc.DIM, bdsc.KERNEL_DIM))
    for j in range(bdsc.KERNEL_DIM):
        t = math.radians(rng.uniform(0.0, 20.0))
        low[:, j] = math.cos(t) * k[:, j] + math.sin(t) * q[:, 8 + j]
    p = low @ low.T
    gamma, eps = rng.uniform(0.2, 1.0), rng.uniform(0.0, 1e-6)
    return np.asarray(gamma * (np.eye(bdsc.DIM) - p) + eps * p, dtype=complex)


def _theorem_item(item: tuple[str, int]) -> tuple[bool, bool, float]:
    """(theorem holds, a < gamma, sin^2 theta / (a / gamma)) for one random or near-tight effect."""
    family, seed = item
    exact = bdsc.theorem_holds(_random_effect(seed) if family == "random" else _tight_effect(seed))
    nontrivial = exact["a"] < exact["gamma"]
    ratio = math.sin(math.radians(exact["theta"])) ** 2 / (exact["a"] / exact["gamma"]) if nontrivial else 0.0
    return bool(exact["ok"]), nontrivial, ratio


CENSUS_EFFECTS = 128
# The five-space and sum-rule checks run on the first WITNESS_SEEDS census effects.
WITNESS_SEEDS = 8


def _general_effect(seed: int) -> np.ndarray:
    """A random effect: Haar unitary from the QR of a complex Gaussian, eigenvalues uniform in [0, 1]."""
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(bdsc.DIM, bdsc.DIM)) + 1j * rng.normal(size=(bdsc.DIM, bdsc.DIM))
    q, r = np.linalg.qr(z)
    q = q @ np.diag(np.diag(r) / np.abs(np.diag(r)))
    return np.asarray(q @ np.diag(rng.uniform(0.0, 1.0, size=bdsc.DIM)) @ q.conj().T)


def _census_item(seed: int) -> tuple[int, int, int]:
    """Violations on one random effect, built and diagonalized once: mu_j <= lambda_(4+j)(F) <= a + mu_j over
    j = 1..12; and, for seed < WITNESS_SEEDS, lambda_5(F) <= Tr(S F) for both candidate directions and the real and
    imaginary sum rules on (e1, e2)."""
    effect = _general_effect(seed)
    a_block, c_block = bdsc.blocks(effect)
    a = float(np.linalg.eigvalsh(a_block)[-1])
    mu = np.linalg.eigvalsh(c_block)
    spectrum = np.linalg.eigvalsh(effect)
    lam = spectrum[bdsc.KERNEL_DIM :]
    census = int(np.sum((lam < mu - 1e-12) | (lam > a + mu + 1e-12)))
    if seed >= WITNESS_SEEDS:
        return census, 0, 0
    witness = sum(
        int(spectrum[4] > bdsc.five_space_trace(effect, q) + 1e-12) for q in bdsc.candidate_directions().values()
    )
    frame = bdsc.complement_frame().astype(complex)
    states = bdsc.consistency_states(frame[:, 1], frame[:, 2])
    pr = {x: float(np.real(np.conj(v) @ effect @ v)) for x, v in states.items()}
    rules = int(abs(pr["+"] + pr["-"] - pr["f"] - pr["g"]) >= 1e-12) + int(
        abs(pr["+i"] + pr["-i"] - pr["f"] - pr["g"]) >= 1e-12
    )
    return census, witness, rules


def self_test() -> int:
    catalogue = load_catalogue()
    target = target_record(catalogue)
    effect, frame = target_effect(), integer_frame()

    def rejected(label: str, condition: bool) -> None:
        require(condition, f"self-test: {label} was not rejected")

    flipped = copy.deepcopy(effect)
    flipped[4][15] = -flipped[4][15]
    rejected("an E0 sign flip", not all(exact_checks(flipped, frame).values()))
    bad_frame = copy.deepcopy(frame)
    bad_frame[0]["w"][12] = -bad_frame[0]["w"][12]
    rejected("a kernel-vector sign flip", not all(exact_checks(effect, bad_frame).values()))
    rejected(
        "a perturbed sign table",
        not doubling_matches_cd_core(lambda d, p, r: -cd_sign(d, p, r) if (p, r) == (3, 5) else cd_sign(d, p, r)),
    )
    u = measurement_unitary(target["selected_modes"], target["complement_modes"])
    broken = copy.deepcopy(u)
    broken[target["selected_modes"][0]][7] = (
        -broken[target["selected_modes"][0]][7][0],
        -broken[target["selected_modes"][0]][7][1],
    )
    rejected("a U24 entry flip", not all(unitary_checks(broken, target["selected_modes"], effect).values()))
    swapped = [target["complement_modes"][0], *target["selected_modes"][1:]]
    rejected("a swapped selected mode", not unitary_checks(u, swapped, effect)["compression = E0"])
    rejected(
        "a mirrored k_1 row",
        not unitary_checks(
            measurement_unitary(target["complement_modes"], target["selected_modes"]), target["selected_modes"], effect
        )["compression = E0"],
    )
    # Reconstruction identities on a generic complex effect.
    generic = _random_effect(7)
    for block in ("A", "C"):
        rows = bdsc.block_settings(block)
        estimate = bdsc.reconstruct(bdsc.probabilities(generic, rows), bdsc.coefficients(rows))
        truth = bdsc.blocks(generic)[0 if block == "A" else 1]
        require(np.allclose(estimate, truth, atol=1e-12), f"self-test: block {block} reconstruction")
    imag_rows = bdsc.block_settings("C", real_only=True)
    blind = bdsc.reconstruct(bdsc.probabilities(bdsc.extra_imag_null(), imag_rows), bdsc.coefficients(imag_rows, True))
    require(abs(np.linalg.eigvalsh(blind)[0] - 0.5) < 1e-12, "self-test: the real bank should read E_I as 1/2")
    exposed = [
        s.name
        for s in bdsc.block_settings("C")
        if abs(bdsc.probabilities(bdsc.extra_imag_null(), [s])[0] - bdsc.probabilities(bdsc.ideal_effect(), [s])[0])
        > 1e-12
    ]
    require(exposed == ["C-imag-01-02"], f"self-test: E_I differs from E0 on {exposed}")
    exposed_r = [
        s.name
        for s in bdsc.block_settings("C")
        if abs(bdsc.probabilities(bdsc.extra_real_null(), [s])[0] - bdsc.probabilities(bdsc.ideal_effect(), [s])[0])
        > 1e-12
    ]
    require(exposed_r == ["C-real-01-02"], f"self-test: E_R differs from E0 on {exposed_r}")
    # Pilot recovers an imaginary k_1 / f_9 coupling.
    k1, f9 = bdsc.kernel_frame()[:, 0], bdsc.complement_frame()[:, 8]
    coupled = bdsc.ideal_effect() * 0.8 + 0.1 * np.eye(bdsc.DIM) + 0.05j * (np.outer(k1, f9) - np.outer(f9, k1))
    require(bdsc.is_effect(coupled), "self-test: the coupled pilot effect is not an effect")
    pilot = bdsc.pilot_probabilities(coupled)
    readout = bdsc.pilot_readout({k: (int(round(v * 10**9)), 10**9) for k, v in pilot.items()}, 0.01)[0]
    expected_im = float(np.imag(k1 @ coupled @ f9))
    require(abs(readout["im_d_q"] - expected_im) < 1e-6, f"self-test: pilot Im d {readout['im_d_q']} vs {expected_im}")
    # Certificate theorem on random effects.
    items = [(family, seed) for family in ("random", "tight") for seed in range(THEOREM_EFFECTS)]
    outcomes = parallel.ordered_map(_theorem_item, items)
    require(all(ok for ok, _, _ in outcomes), "self-test: the certificate theorem fails on an effect")
    nontrivial = sum(flag for _, flag, _ in outcomes)
    tightest = max(ratio for _, _, ratio in outcomes)
    require(nontrivial >= THEOREM_NONTRIVIAL_MIN, f"self-test: only {nontrivial} effects have a < gamma")
    require(tightest > 0.99, f"self-test: the angle bound is never approached (ratio {tightest})")
    # Low-eigenvalue census: interlacing and the positivity bound on 12 indexed pairs per random effect.
    violations = parallel.ordered_map(_census_item, list(range(CENSUS_EFFECTS)))
    for index, label in enumerate(("census inequalities", "five-space bounds", "sum rules")):
        failures = sum(v[index] for v in violations)
        require(failures == 0, f"self-test: the {label} fail {failures} times")
    coupled = bdsc.coupled_complement_effect()
    require(bdsc.is_effect(coupled), "self-test: the coupled census example is not an effect")
    require(abs(np.linalg.eigvalsh(coupled)[4] - 0.18) < 1e-12, "self-test: the coupled example misses a + mu_1")
    a_block, c_block = bdsc.blocks(bdsc.diagonal_effect([0.05], 1.15))
    clipped = bdsc.spectral_census(bdsc.exact_bound(a_block), bdsc.exact_bound(c_block), 1.0)
    require(not clipped["consistent"], "self-test: an effect above its declared range reads consistent")
    # Five-space witness: Tr(S F) vanishes on the matching extra null (the bound itself runs in _census_item).
    for name, direction in bdsc.candidate_directions().items():
        er = bdsc.extra_real_null() if name == "q_R" else bdsc.extra_imag_null()
        require(abs(bdsc.five_space_trace(er, direction)) < 1e-12, f"self-test: {name} is not the extra null")
    # A 0.1 excess on one consistency state reads violated; an interval around zero alone establishes nothing.
    states = bdsc.CONSISTENCY_LABELS
    n_big = 10**7
    linear = bdsc.consistency_readout({x: (int(round(0.5 * n_big)), n_big) for x in states}, 0.01)
    require(linear["delta_R_status"] == linear["delta_I_status"] == "compatible", "self-test: consistency margin")
    broken_counts = {x: (int(round((0.6 if x == "+" else 0.5) * n_big)), n_big) for x in states}
    excess = bdsc.consistency_readout(broken_counts, 0.01)
    require(excess["delta_R_status"] == "violated", "self-test: a 0.1 sum-rule violation is not caught")
    near = bdsc.consistency_readout({x: (50, 100) for x in states}, 0.01)
    require(near["delta_R_status"] == "inconclusive", "self-test: an interval around zero alone established a rule")
    # Case contrasts: on (e1, e2) the outward-ladder cells answer I/2 + X/4 in epoch 1 and I/2 + Y/4 in epoch 2, the
    # reverse-ladder cells I/2 throughout. Every sum rule holds and f, g never move, so only the completion and epoch
    # families see the coherent difference; the batched readout matches the single record row by row.
    observations = case_observations()
    contrasts = case_contrasts(observations)
    reloaded = json.loads(json.dumps(observations, sort_keys=True))
    require(case_contrasts(reloaded) == contrasts, "self-test: contrasts depend on observation key order")
    coherent = {1: {"+": 0.25, "-": -0.25}, 2: {"+i": 0.25, "-i": -0.25}}
    n_exact = 10**7
    probabilities = []
    for o in observations:
        p = 0.5
        if o["pair"] == "middle-middle" and o["preparation"] == PREPARATION_DESCRIPTIONS[0]:
            p += coherent[o["epoch"]].get(o["label"], 0.0)
        probabilities.append(p)
    k = np.array([round(p * n_exact) for p in probabilities])
    status = bdsc.contrast_readout(k, np.full(k.shape, n_exact), contrasts, CASE_ALPHA)["status"]
    by_family = {f: {str(x) for x, c in zip(status, contrasts, strict=True) if c[0] == f} for f in CASE_MARGINS}
    require(by_family["sum_rule"] == {"compatible"}, f"self-test: the sum rules read {by_family['sum_rule']}")
    require("violated" in by_family["completion"], "self-test: the completion family misses F_G")
    require("violated" in by_family["epoch"], "self-test: the epoch family misses the X to Y change")
    admitted = np.array([o["processing"] == "empty-mitigation" for o in observations])
    gated = bdsc.contrast_readout(k, np.full(k.shape, n_exact), contrasts, CASE_ALPHA, admitted)["status"]
    for c, plain, masked in zip(contrasts, status, gated, strict=True):
        inside = all(admitted[j] for j, _ in c[2])
        require(masked == (plain if inside else "not_admitted"), "self-test: admission mask")
    rng = np.random.default_rng(7)
    batch = rng.binomial(30_000, np.broadcast_to(probabilities, (4, len(probabilities))))
    batched = bdsc.contrast_readout(batch, np.full(batch.shape, 30_000), contrasts, CASE_ALPHA)
    for row in range(len(batch)):
        single = bdsc.contrast_readout(batch[row], np.full(batch.shape[1], 30_000), contrasts, CASE_ALPHA)
        require(
            np.array_equal(single["lower"], batched["lower"][row])
            and np.array_equal(single["upper"], batched["upper"][row])
            and np.array_equal(single["status"], batched["status"][row]),
            "self-test: the batched contrast readout differs from the single record",
        )
    # Templates: both ladders reach any column from any source mode, with unitaries that differ off the source.
    for source in (0, 6, 23):
        for trial in range(4):
            z = rng.normal(size=MODES) + 1j * rng.normal(size=MODES)
            if trial == 0:
                z[: MODES // 2] = 0
            column = z / np.linalg.norm(z)
            reached = {}
            for name in PREPARATION_DESCRIPTIONS:
                w = template_unitary(template_ops(name, source), template_params(name, column, source))
                require(
                    np.allclose(w.conj().T @ w, np.eye(MODES), rtol=0, atol=1e-12), f"self-test: {name} not unitary"
                )
                require(np.allclose(w[:, source], column, rtol=0, atol=1e-12), f"self-test: {name} misses the column")
                reached[name] = w
            first, second = reached.values()
            require(not np.allclose(first, second), "self-test: the two templates coincide")
    # Thinning equalizes terminal efficiencies and leaves internal loss: D = eta_* T^dagger T.
    lossless = numeric_unitary(u)[:, : bdsc.DIM]
    eta_t = np.linspace(0.6, 0.95, MODES)
    require(bdsc.scalar_deviation(bdsc.thinned_acceptance(lossless, eta_t))[1] < 1e-12, "self-test: thinned lossless")
    histogram = np.array([0, 1, 1000, 10**6])
    require(np.array_equal(bdsc.thin_histogram(histogram, np.ones(4), rng), histogram), "self-test: q = 1 thinning")
    require(not bdsc.thin_histogram(histogram, np.zeros(4), rng).any(), "self-test: q = 0 thinning")
    kept = bdsc.thin_histogram(np.full(1000, 10**4), np.full(1000, 0.3), rng)
    require(bool(abs(kept.mean() / 3000 - 1) < 0.01 and kept.max() <= 10**4), "self-test: binomial thinning mean")
    lossy = np.diag(np.linspace(0.7, 1.0, MODES)) @ lossless
    require(bdsc.scalar_deviation(bdsc.thinned_acceptance(lossy, eta_t))[1] > 0.1, "self-test: internal loss hidden")
    # Acceptance: uniform efficiency is scalar, a pair imbalance is not.
    un = numeric_unitary(u)
    require(
        bdsc.scalar_deviation(bdsc.acceptance(un, target["selected_modes"], [1.0] * MODES)["D"])[1] < 1e-12,
        "self-test: uniform acceptance",
    )
    eta = [1.0] * MODES
    eta[target["selected_modes"][0]] = 0.5
    require(
        bdsc.scalar_deviation(bdsc.acceptance(un, target["selected_modes"], eta)["D"])[1] > 0.1, "self-test: imbalance"
    )
    print(
        f"bdsc self-test: exact, unitary, bank, pilot, witness, consistency, thinning and acceptance checks pass; "
        f"theorem on {len(items)} effects, {nontrivial} with a < gamma, tightest sin^2 theta / (a / gamma) = "
        f"{tightest:.6f}; census on {CENSUS_EFFECTS} effects, {CENSUS_EFFECTS * bdsc.COMPLEMENT_DIM} indexed pairs"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.write:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
