"""Passivity controls for the two-qubit QET protocol: local energy below the vacuum value requires information.

The model and conventions are those of scripts/qet_two_qubit_reference.py
(Hotta's minimal model, ground energy zero, qubit A first, Z|0> = |0>).
Alice measures X_A and reports a bit r; Bob rotates exp(-i phi Y_B / 2) with
phi = -b phi*, phi* = atan2(hk, h^2 + 2k^2). Bob's local energy is
L = <H_B + V>, whose exact ground-state value is L_g = 0.

Floors. Bob's operations leave <H_A> unchanged and the total energy never
falls below the ground energy, so after any local operation on B
L >= -<H_A>. Alice's nonselective X_A measurement commutes with H_B and V,
so an operation that ignores her record acts as if applied to the
unmeasured state: on the ground state every uninformed local channel,
unitary or not, ends at L >= -<H_A>_g = 0 (passivity floor), while an
informed one ends at L >= -E_A (conservation floor) and the optimum reaches
-E_B, with E_B = sqrt(h^2 + 4k^2) - (h^2 + 2k^2)/r < E_A = h^2/r.

Arms and ideal values (drops of L, positive means lowered):

- feedback, b = r: E_m = E_B; reversed, b = -r: E_x < 0;
- fixed b = +1 or -1, and uninformed drives at larger angles: at most zero;
- fixed arms binned by (r, b) in {++, +-, -+, --}: E_m, E_x, E_x, E_m with
  signs +, -, -, +; the contrast D = (E_m - E_x) / 2 equals feedback minus
  reversed over two;
- record flip q at the fixed angle: (1 - q) E_m + q E_x, zero at
  q* = E_m / (E_m - E_x); q = 1/2 is an uninformed mixture;
- product-state mutation (|00> in place of the ground state, same angle and
  Hamiltonian): Alice's record still tells Bob the sign of X_A, so the
  information excess stays positive, but the feedback L no longer falls
  below the passivity floor; the floor margin, not the excess, carries the
  entanglement the protocol needs.

Confounds. A prepared state that is not the ground state need not be
passive. An RY-angle error delta moves energy from B's terms into H_A and
puts L below L_g with no information; a relative phase between |00> and
|11> (idle Z detuning during the feed-forward wait; ZZ is a global phase on
that pair and needs its own model) is a Z rotation Bob undoes locally, an
uninformed drop from the run's own reference; amplitude damping inflates
the drop from the reference and deflates the drop below L_g. Against
record-independent unitaries the sound endpoint is the information excess:
the lowest L those unitaries reach on the same preparation minus the
feedback arm's L. Against every record-independent channel the endpoint is
the margin of the feedback L below the passivity floor -<H_A>, which needs
<Z_A> from a reference circuit without Alice's X measurement. That maximum is a Kabsch problem: L after
an SU(2) rotation R of B's Bloch frame is const - h z.(R s) + 2k x.(R c),
with s B's Bloch vector and c_j = <X_A sigma_j^B>, so three Bob settings of
the reference arm (X, Y, Z, each with Alice's record) certify it exactly.
A q = 1/2 record makes the feedback arm an uninformed mixture, so its
information excess is at most zero for every preparation. A run must read
X_A again at the end of each circuit: substituting Alice's reported bit for
X_A turns a broken readout into an apparent excess.

The values are dimensionless spin-model energies of an encoded Hamiltonian;
the script submits no job.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

from qet_two_qubit_reference import I2, X, Y, Z, hamiltonians  # noqa: E402

from parallel import ordered_map  # noqa: E402

TOLERANCE = 1e-10
DRIVE_ANGLES = (math.pi / 4, math.pi / 2, math.pi)
PAULIS = (X, Y, Z)


def qet_angle(h: float, k: float) -> float:
    return math.atan2(h * k, h * h + 2 * k * k)


def ground_state(h: float, k: float, delta: float = 0.0) -> np.ndarray:
    """cos(t)|00> - sin(t)|11> with tan(2t) = k/h; delta is a coherent error on the preparation angle t."""
    theta = math.atan2(k, h) / 2 + delta
    vector = np.zeros(4, dtype=complex)
    vector[0], vector[3] = math.cos(theta), -math.sin(theta)
    return np.outer(vector, vector.conj())


def amplitude_damp(rho: np.ndarray, gamma: float, qubits: tuple[int, ...] = (0, 1)) -> np.ndarray:
    """Independent amplitude damping of strength gamma toward |0> on the listed qubits."""
    k0 = np.array([[1, 0], [0, math.sqrt(1 - gamma)]], dtype=complex)
    k1 = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    for qubit in qubits:
        out = np.zeros_like(rho)
        for kraus in (k0, k1):
            op = np.kron(kraus, I2) if qubit == 0 else np.kron(I2, kraus)
            out += op @ rho @ op.conj().T
        rho = out
    return rho


def prepare(h: float, k: float, delta: float = 0.0, gamma: float = 0.0, phase: float = 0.0) -> np.ndarray:
    """Ground state with angle error delta, then a Z rotation by phase on B, then amplitude damping gamma."""
    rz = np.kron(I2, np.diag([np.exp(-0.5j * phase), np.exp(0.5j * phase)]))
    return amplitude_damp(rz @ ground_state(h, k, delta) @ rz.conj().T, gamma)


def rotation_b(phi: float) -> np.ndarray:
    return np.kron(I2, math.cos(phi / 2) * I2 - 1j * math.sin(phi / 2) * Y)


def expect(rho: np.ndarray, operator: np.ndarray) -> float:
    return float(np.trace(rho @ operator).real)


def branches(rho: np.ndarray, flip: float) -> list[tuple[float, int, np.ndarray]]:
    """(probability, reported bit, post-measurement state) of Alice's X_A measurement with record flip."""
    out = []
    for mu in (-1, 1):
        projector = np.kron((I2 + mu * X) / 2, I2)
        branch = projector @ rho @ projector
        probability = expect(branch, np.eye(4))
        if probability < 1e-15:
            continue
        for reported, weight in ((mu, 1 - flip), (-mu, flip)):
            if weight > 0:
                out.append((probability * weight, reported, branch / probability))
    return out


def final_local(rho: np.ndarray, h: float, k: float, rule: str, flip: float = 0.0, angle: float | None = None) -> float:
    """Bob's final local energy averaged over Alice's outcomes when Bob's sign follows rule."""
    _, bob_local = hamiltonians(h, k)
    phi = qet_angle(h, k) if angle is None else angle
    total = 0.0
    for weight, reported, state in branches(rho, flip):
        sign = {"feedback": reported, "reversed": -reported, "plus": 1, "minus": -1, "none": 0}[rule]
        rotation = rotation_b(-sign * phi)
        total += weight * expect(rotation @ state @ rotation.conj().T, bob_local)
    return total


def bloch_and_correlation(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """B's Bloch vector s_j = <sigma_j^B> and the record correlation c_j = <X_A sigma_j^B>."""
    s = np.array([expect(rho, np.kron(I2, p)) for p in PAULIS])
    c = np.array([expect(rho, np.kron(X, p)) for p in PAULIS])
    return s, c


def kabsch_min_local(rho: np.ndarray, h: float, k: float) -> float:
    """Minimum of Bob's local energy over every SU(2) unitary on B, in closed form.

    After rotation R in SO(3), L = const + tr(R M) with M = -h s z^T + 2k c x^T.
    M has rank at most two, so its third singular value is zero and the
    minimum over SO(3) of tr(R M) is -(sigma_1 + sigma_2).
    """
    s, c = bloch_and_correlation(rho)
    _, bob_local = hamiltonians(h, k)
    return kabsch_floor(s, c, expect(rho, bob_local) - (-h * s[2] + 2 * k * c[0]), h, k)


def search_min_local(rho: np.ndarray, h: float, k: float) -> float:
    """Nelder-Mead minimum over ZYZ Euler angles, the cross-check of kabsch_min_local."""
    _, bob_local = hamiltonians(h, k)

    def energy(params: np.ndarray) -> float:
        a, b, c = params
        rz1 = np.diag([np.exp(-0.5j * a), np.exp(0.5j * a)])
        ry = math.cos(b / 2) * I2 - 1j * math.sin(b / 2) * Y
        rz2 = np.diag([np.exp(-0.5j * c), np.exp(0.5j * c)])
        unitary = np.kron(I2, rz1 @ ry @ rz2)
        return expect(unitary @ rho @ unitary.conj().T, bob_local)

    starts = ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, -1.0, 2.0), (2.0, 2.5, -1.0), (0.5, math.pi, 0.5))
    options = {"xatol": 1e-11, "fatol": 1e-14, "maxiter": 4000}
    return min(float(minimize(energy, np.array(s), method="Nelder-Mead", options=options).fun) for s in starts)


def kabsch_floor(s: np.ndarray, c: np.ndarray, const: float, h: float, k: float) -> float:
    """Minimum over SO(3) of const - h z.(R s) + 2k x.(R c): rank-two M, so -(sigma_1 + sigma_2)."""
    m = -h * np.outer(s, [0.0, 0.0, 1.0]) + 2 * k * np.outer(c, [1.0, 0.0, 0.0])
    sigma = np.linalg.svd(m, compute_uv=False)
    return const - (sigma[0] + sigma[1])


def hardware_excess(
    rho: np.ndarray, h: float, k: float, record_flip: float, final_flip: float, estimator: str
) -> float:
    """Information excess as a run computes it from counts, for two ways of reading X_A.

    estimator "reported" replaces X_A by Alice's mid-circuit bit r; "remeasured"
    reads X_A again at the end of every circuit, with symmetric assignment
    error final_flip, so the estimate is the expectation of an operator
    O_B + X_A O'_B on the physical state and passivity binds it. The floor
    uses the reference arm's Bloch and correlation vectors read the same way.
    """
    r = math.hypot(h, k)
    const = h * h / r + 2 * k * k / r
    phi = qet_angle(h, k)
    shrink = 1 - 2 * final_flip

    def read(rule: str) -> tuple[np.ndarray, np.ndarray]:
        s = np.zeros(3)
        c = np.zeros(3)
        for weight, reported, state in branches(rho, record_flip):
            sign = {"feedback": reported, "none": 0}[rule]
            rotation = rotation_b(-sign * phi)
            out = rotation @ state @ rotation.conj().T
            s += weight * np.array([expect(out, np.kron(I2, p)) for p in PAULIS])
            if estimator == "reported":
                c += weight * reported * np.array([expect(out, np.kron(I2, p)) for p in PAULIS])
            else:
                c += weight * shrink * np.array([expect(out, np.kron(X, p)) for p in PAULIS])
        return s, c

    s_ref, c_ref = read("none")
    s_fb, c_fb = read("feedback")
    feedback = const - h * s_fb[2] + 2 * k * c_fb[0]
    return kabsch_floor(s_ref, c_ref, const, h, k) - feedback


def averaged(rho: np.ndarray) -> np.ndarray:
    return sum((weight * state for weight, _, state in branches(rho, 0.0)), np.zeros((4, 4), dtype=complex))


def summary(
    h: float, k: float, delta: float = 0.0, gamma: float = 0.0, flip: float = 0.0, phase: float = 0.0
) -> dict[str, float]:
    rho = prepare(h, k, delta, gamma, phase)
    total, _ = hamiltonians(h, k)
    alice = total - hamiltonians(h, k)[1]
    reference = final_local(rho, h, k, "none")
    finals = {
        rule: final_local(rho, h, k, rule, flip if rule in ("feedback", "reversed") else 0.0)
        for rule in ("feedback", "reversed", "plus", "minus")
    }
    best_uninformed = kabsch_min_local(averaged(rho), h, k)
    row = {
        "h": h,
        "k": k,
        "delta": delta,
        "gamma": gamma,
        "phase": phase,
        "flip": flip,
        "reference_local": reference,
        "passivity_floor": -expect(rho, alice),
        "feedback_drop": reference - finals["feedback"],
        "reversed_drop": reference - finals["reversed"],
        "contrast": (finals["reversed"] - finals["feedback"]) / 2,
        "uninformed_drop": reference - best_uninformed,
        "feedback_below_ground": -finals["feedback"],
        "uninformed_below_ground": -best_uninformed,
        "information_excess": best_uninformed - finals["feedback"],
        "channel_floor_margin": -expect(rho, alice) - finals["feedback"],
    }
    for name in ("plus", "minus"):
        row[f"fixed_{name}_below_ground"] = -finals[name]
    for angle in DRIVE_ANGLES:
        worst = min(final_local(rho, h, k, rule, angle=angle) for rule in ("plus", "minus"))
        row[f"drive_{angle:.4f}_below_ground"] = -worst
    return row


def binned_drops(rho: np.ndarray, h: float, k: float) -> dict[str, float]:
    """Drop of Bob's local energy conditional on (reported bit, fixed sign), from the two fixed arms."""
    _, bob_local = hamiltonians(h, k)
    phi = qet_angle(h, k)
    out = {}
    for _, reported, state in branches(rho, 0.0):
        for sign in (1, -1):
            rotation = rotation_b(-sign * phi)
            key = ("+" if reported > 0 else "-") + ("+" if sign > 0 else "-")
            out[key] = expect(state, bob_local) - expect(rotation @ state @ rotation.conj().T, bob_local)
    return out


def shots_per_setting(h: float, k: float, sigmas: float = 5.0) -> int:
    """Shots per setting and arm for a detection of the ideal information excess at sigmas standard errors.

    The feedback arm's L uses settings Z_B (term -h Z_B) and X_B (term
    2k r X_B, r Alice's record), single-shot variances h^2 (1 - <Z>^2) and
    4k^2 (1 - <r X>^2). At the ideal point the Kabsch optimum is the identity
    rotation, so to first order the uninformed bound is the reference arm's
    L, with the same two variances evaluated on the unrotated state; the Y_B
    setting enters at second order.
    """
    rho = ground_state(h, k)
    variance = 0.0
    phi = qet_angle(h, k)
    for sign in (1, 0):
        z_mean = x_mean = 0.0
        for weight, reported, state in branches(rho, 0.0):
            rotation = rotation_b(-sign * reported * phi)
            out = rotation @ state @ rotation.conj().T
            z_mean += weight * expect(out, np.kron(I2, Z))
            x_mean += weight * reported * expect(out, np.kron(I2, X))
        variance += h * h * (1 - z_mean**2) + 4 * k * k * (1 - x_mean**2)
    e_b = summary(h, k)["information_excess"]
    return math.ceil(variance * (sigmas / e_b) ** 2)


def confound_case(case: tuple[float, float, float, float, float]) -> dict[str, float]:
    """Summary row of one preparation error (h, k, delta, gamma, phase), after its soundness checks.

    The checks: the Kabsch minimum equals the Euler-angle search, and neither
    the model's q = 1/2 feedback nor the remeasured hardware estimator with a
    q = 1/2 record shows an information excess.
    """
    h, k, delta, gamma, phase = case
    rho = prepare(h, k, delta, gamma, phase)
    label = f"delta {delta}, gamma {gamma}, phase {phase}"
    measured = averaged(rho)
    if abs(kabsch_min_local(measured, h, k) - search_min_local(measured, h, k)) > 1e-8:
        raise RuntimeError(f"{label}: Kabsch minimum differs from the Euler-angle search")
    if summary(h, k, delta, gamma, flip=0.5, phase=phase)["information_excess"] > TOLERANCE:
        raise RuntimeError(f"{label}: an uninformed q = 1/2 record shows an information excess")
    if hardware_excess(rho, h, k, 0.5, 0.03, "remeasured") > TOLERANCE:
        raise RuntimeError(f"{label}: the remeasured estimator shows an excess with an uninformed record")
    return summary(h, k, delta, gamma, phase=phase)


def reference(h: float = 1.0, k: float = 1.0) -> dict[str, object]:
    ideal = summary(h, k)
    r = math.hypot(h, k)
    e_b = math.hypot(h, 2 * k) - (h * h + 2 * k * k) / r
    if abs(ideal["reference_local"]) > TOLERANCE or abs(ideal["passivity_floor"]) > TOLERANCE:
        raise RuntimeError("the ground state's local energy or passivity floor differs from zero")
    if abs(ideal["feedback_below_ground"] - e_b) > TOLERANCE or abs(ideal["information_excess"] - e_b) > TOLERANCE:
        raise RuntimeError("feedback below-ground value differs from the closed-form E_B")
    if abs(ideal["uninformed_below_ground"]) > TOLERANCE:
        raise RuntimeError("an uninformed unitary lowered the measured ground state's local energy")
    for name, value in ideal.items():
        if (name.startswith("drive_") or name.startswith("fixed_")) and value > TOLERANCE:
            raise RuntimeError(f"uninformed arm {name} went below the vacuum value")
    ground = ground_state(h, k)
    _, bob_local = hamiltonians(h, k)
    reset = np.kron(I2, np.array([[1, 0], [0, 0]], dtype=complex))
    flip_to_zero = np.kron(I2, np.array([[0, 1], [0, 0]], dtype=complex))
    reset_state = reset @ ground @ reset.conj().T + flip_to_zero @ ground @ flip_to_zero.conj().T
    for name, state in (("reset", reset_state), ("damping", amplitude_damp(ground, 0.5, (1,)))):
        if expect(state, bob_local) < -TOLERANCE:
            raise RuntimeError(f"uninformed channel {name} on B crossed the passivity floor")
    binned = binned_drops(ground, h, k)
    signs = [math.copysign(1.0, binned[key]) for key in ("++", "+-", "-+", "--")]
    if signs != [1.0, -1.0, -1.0, 1.0] or abs(binned["++"] - binned["--"]) > TOLERANCE:
        raise RuntimeError(f"binned arms {binned} do not read +, -, -, +")
    if abs((binned["++"] - binned["+-"]) / 2 - ideal["contrast"]) > TOLERANCE:
        raise RuntimeError("binned contrast differs from feedback minus reversed")
    e_x = binned["+-"]
    for q in (0.1, 0.25, 0.5):
        row = summary(h, k, flip=q)
        if abs(row["feedback_drop"] - ((1 - q) * e_b + q * e_x)) > TOLERANCE:
            raise RuntimeError(f"record flip {q}: the feedback drop is not linear in q")
    mutation = summary(h, k, delta=-math.atan2(k, h) / 2)
    if mutation["channel_floor_margin"] >= 0 or mutation["information_excess"] <= 0:
        raise RuntimeError("the product-state mutation keeps a floor margin or loses its record excess")
    grid = [
        {"delta": d, "gamma": g, "phase": p} for d in (0.0, 0.05, 0.15) for g in (0.0, 0.05) for p in (0.0, 0.2, 0.5)
    ]
    cases = [(h, k, case["delta"], case["gamma"], case["phase"]) for case in grid]
    # Each case runs five Nelder-Mead searches, so even an 18-case grid fills the pool.
    confounds = ordered_map(confound_case, cases, min_items=1)
    if not any(row["uninformed_below_ground"] > 1e-3 for row in confounds):
        raise RuntimeError("no preparation error put L below L_g without information; the confound model is inert")
    if not any(row["uninformed_drop"] > 1e-3 and row["uninformed_below_ground"] < 1e-9 for row in confounds):
        raise RuntimeError("no phase error opened an uninformed drop from the reference")
    readout = {}
    for record_flip in (0.0, 0.01, 0.03, 0.5):
        row = {name: hardware_excess(ground, h, k, record_flip, 0.02, name) for name in ("reported", "remeasured")}
        readout[str(record_flip)] = row
    if abs(hardware_excess(ground, h, k, 0.0, 0.0, "reported") - e_b) > TOLERANCE:
        raise RuntimeError("the reported-bit estimator differs from E_B with a perfect readout")
    if readout["0.5"]["reported"] < 0.1:
        raise RuntimeError("the reported-bit estimator no longer shows its q = 1/2 false excess")
    return {
        "h": h,
        "k": k,
        "E_A": h * h / r,
        "readout_assignment": readout,
        "E_B": e_b,
        "ideal": ideal,
        "binned": binned,
        "flip_zero_crossing": e_b / (e_b - e_x),
        "mutation_product_state": mutation,
        "confounds": confounds,
        "shots_per_setting_5_sigma": shots_per_setting(h, k),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="JSON path; default prints a summary")
    args = parser.parse_args()
    result = reference()
    ideal = result["ideal"]
    confounds = result["confounds"]
    if not isinstance(ideal, dict) or not isinstance(confounds, list):
        raise RuntimeError("reference rows missing")
    print(
        f"h = k = 1: E_A {result['E_A']:.6f}, E_B {result['E_B']:.6f}, contrast {ideal['contrast']:.6f}, "
        f"flip zero crossing {result['flip_zero_crossing']:.4f}, "
        f"shots per setting at 5 sigma {result['shots_per_setting_5_sigma']}"
    )
    for row in confounds:
        print(
            f"delta {row['delta']:.2f} gamma {row['gamma']:.2f} phase {row['phase']:.2f}: "
            f"feedback drop {row['feedback_drop']:+.4f} below-ground {row['feedback_below_ground']:+.4f} "
            f"uninformed drop {row['uninformed_drop']:+.4f} below-ground {row['uninformed_below_ground']:+.4f} "
            f"excess {row['information_excess']:+.4f}"
        )
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
