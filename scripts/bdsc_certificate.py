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
  rate (ties by mode) of the retained qpu:belenos catalogue, D_1..D_12 the
  rest in mode order; the source is the connected input with the highest
  receipt t_in. Both receipt fields are dated planning inputs.

Records under docs/evidence/bdsc/: target.json (algebra, frames, U24,
mask), bank.json (the 160 settings with their states, chip columns and
exact ideal probabilities; the 88 real settings flagged), pilot.json,
controls.json (synthetic adversarial controls through bdsc.evaluate),
planning.json (radius table, zero-event trace route, measured Belenos
rates) and qualification.json (milestones M0 to M9 with the evidence that
passes or blocks each).

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

CATALOGUE = ROOT / "docs/evidence/quandela/catalogue.json"
EVIDENCE = ROOT / "docs/evidence/bdsc"
CHIP = "qpu:belenos"
MODES = 24
SCHEMA = "bdsc-records-v1"
FILES = ("target.json", "bank.json", "pilot.json", "controls.json", "planning.json", "qualification.json")
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
    data: dict[str, Any] = json.loads(CATALOGUE.read_text(encoding="utf-8"))
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
    if truth is not None and "a_U" in result:
        exact = bdsc.theorem_holds(truth)
        out["truth"] = {key: round(float(exact[key]), 12) for key in ("a", "gamma", "theta")}
        out["covered"] = bool(exact["a"] <= result["a_U"] + 1e-12 and exact["gamma"] >= result["gamma_L"] - 1e-12)
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
    ) -> None:
        jobs.append((name, purpose, expected, record, truth, frozen if identity is None else identity))

    def counts(effect: np.ndarray, seed: int, real_only: bool = False) -> dict[str, tuple[int, int]]:
        return bdsc.sample_counts(effect, n, seed, real_only)

    e0 = bdsc.ideal_effect()
    run("ideal", "E0 itself", "certified", bdsc.record_from_counts(counts(e0, 1), frozen), e0)
    er = bdsc.extra_real_null()
    run(
        "extra_real_null",
        "E_R: a fifth null on (e1 - e2)/sqrt2",
        "alternative_structure",
        bdsc.record_from_counts(counts(er, 2), frozen),
        er,
    )
    ei = bdsc.extra_imag_null()
    run(
        "extra_imag_null",
        "E_I: a fifth null on (e1 + i e2)/sqrt2, complex bank",
        "alternative_structure",
        bdsc.record_from_counts(counts(ei, 3), frozen),
        ei,
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
        "common_effect_unsupported": lambda r: r["premises"].__setitem__("common_effect", "unsupported"),
        "sampling_law_unsupported": lambda r: r["premises"].__setitem__("bernoulli_sampling", "unsupported"),
        "boolean_count": lambda r: r["rows"][2].__setitem__("selected", False),
        "nan_conditioning": lambda r: r.__setitem__("conditioning_delta", float("nan")),
        "negative_bias": lambda r: r.__setitem__("preparation_bias_bound", -0.5),
        "string_bias": lambda r: r.__setitem__("preparation_bias_bound", "0.1"),
        "row_not_object": lambda r: r["rows"].__setitem__(3, None),
        "premises_not_object": lambda r: r.__setitem__("premises", ["common_effect"]),
    }
    for name, mutate in mutations.items():
        record = copy.deepcopy(base)
        mutate(record)
        run(name, "record or premise defect", "inadmissible", record, None)
    rows = parallel.ordered_map(_evaluate_control, jobs)
    for row in rows:
        require(row["disposition"] == row["expected"], f"control {row['control']} read {row['disposition']}")
        require(row.get("covered", True) or row["control"].endswith("_forced"), f"control {row['control']} uncovered")
    return {
        "schema": SCHEMA,
        "record": "controls",
        "target_sha256": target["target_sha256"],
        "trials_per_setting": n,
        "alpha_allocation": ALLOCATION,
        "dark_ratio": bdsc.DARK_RATIO,
        "target_ratio": bdsc.TARGET_RATIO,
        "controls": rows,
        "coverage": coverage(target),
    }


ControlJob = tuple[str, str, str, dict[str, Any], np.ndarray | None, dict[str, Any]]


def _evaluate_control(job: ControlJob) -> dict[str, Any]:
    name, purpose, expected, record, truth, identity = job
    result = bdsc.evaluate(record, identity)
    return {"control": name, "purpose": purpose, "expected": expected, **summary(result, truth)}


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
            "probs_to_sample_count, the conversion DetectorBalancing ends in, reads a zero-count frequency of 0.311 "
            "against the binomial 0.368 at p = 1e-4 and n = 10^4, so converted counts are not Bernoulli trials",
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
        "synthetic_validation": {
            "controls": len(controls["controls"]),
            "all_expected": all(r["disposition"] == r["expected"] for r in controls["controls"]),
            "scope": "the analysis procedure under its assumptions; no hardware certificate",
        },
        "authorization": "no acquisition, upload or cloud submission is authorized by these records",
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
    records = {
        "target.json": target,
        "bank.json": bank,
        "pilot.json": pilot,
        "controls.json": controls,
        "planning.json": planning,
        "qualification.json": qualification,
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
        f"bdsc self-test: exact, unitary, bank, pilot and acceptance checks pass; theorem on {len(items)} effects, "
        f"{nontrivial} with a < gamma, tightest sin^2 theta / (a / gamma) = {tightest:.6f}"
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
