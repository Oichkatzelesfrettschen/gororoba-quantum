"""Exact two-qubit quantum energy teleportation reference (Hotta's minimal model).

H = H_A + H_B + V with H_A = -h Z_A + h^2/r, H_B = -h Z_B + h^2/r and
V = 2k X_A X_B + 2k^2/r, r = sqrt(h^2 + k^2); the constants put the ground
energy at zero. Alice measures X_A with outcome mu = +-1 and Bob applies
exp(-i phi_mu Y_B / 2). Closed forms:

- Alice's measurement injects E_A = h^2 / r on average;
- Bob's local energy H_B + V falls by at most
  E_B = sqrt(h^2 + 4k^2) - (h^2 + 2k^2) / r, reached at
  phi_mu = -mu atan2(hk, h^2 + 2k^2), because
  (h^2 + 2k^2)^2 + h^2 k^2 = (h^2 + k^2)(h^2 + 4k^2);
- the total energy after Bob's operation is E_A - E_B >= 0 (passivity of the
  ground state);
- the same E_B in rationalized form, h^2 k^2 / (r (r sqrt(h^2 + 4k^2) + h^2 + 2k^2)),
  which avoids cancellation at weak coupling;
- if Alice's reported bit is flipped with probability q before Bob uses it,
  Bob's optimum is E_B(q) = sqrt(C^2 + (1 - 2q)^2 A^2) - C with
  C = (h^2 + 2k^2) / r and A = hk / r, at angle
  -mu atan2((1 - 2q) hk, h^2 + 2k^2); E_B(1/2) = 0;
- Bob's unitary commutes with H_A, so the drop in total energy equals the
  drop in Bob's local energy H_B + V.

The check evaluates every quantity from 4 x 4 matrices at machine precision
and confirms that the closed-form angle is a minimum of Bob's energy. The
values are dimensionless spin-model energies. They are not field
stress-energy, and the script submits no hardware job.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)
COUPLINGS = (0.1, 0.25, 0.5, 1.0, 2.0)
TOLERANCE = 1e-12


def hamiltonians(h: float, k: float) -> tuple[np.ndarray, np.ndarray]:
    r = math.hypot(h, k)
    alice = -h * np.kron(Z, I2) + (h * h / r) * np.eye(4)
    bob = -h * np.kron(I2, Z) + (h * h / r) * np.eye(4)
    coupling = 2 * k * np.kron(X, X) + (2 * k * k / r) * np.eye(4)
    return alice + bob + coupling, bob + coupling


def energy(rho: np.ndarray, operator: np.ndarray) -> float:
    return float(np.trace(rho @ operator).real)


def protocol(h: float, k: float, angle_scale: float = 1.0, flip: float = 0.0) -> dict[str, float]:
    """Average energies of the protocol with Bob's angle scaled and Alice's report flipped with probability flip."""
    total, bob_local = hamiltonians(h, k)
    values, vectors = np.linalg.eigh(total)
    if abs(values[0]) > TOLERANCE:
        raise RuntimeError(f"ground energy {values[0]} differs from zero")
    ground = np.outer(vectors[:, 0], vectors[:, 0].conj())
    angle = math.atan2((1 - 2 * flip) * h * k, h * h + 2 * k * k) * angle_scale
    injected = after = local_drop = 0.0
    for mu in (-1, 1):
        projector = np.kron((I2 + mu * X) / 2, I2)
        branch = projector @ ground @ projector
        probability = float(np.trace(branch).real)
        branch = branch / probability
        injected += probability * energy(branch, total)
        for reported, weight in ((mu, 1 - flip), (-mu, flip)):
            phi = -reported * angle
            rotation = np.kron(I2, math.cos(phi / 2) * I2 - 1j * math.sin(phi / 2) * Y)
            rotated = rotation @ branch @ rotation.conj().T
            after += probability * weight * energy(rotated, total)
            local_drop += probability * weight * (energy(branch, bob_local) - energy(rotated, bob_local))
    if abs((injected - after) - local_drop) > TOLERANCE:
        raise RuntimeError("total-energy drop differs from Bob's local-energy drop")
    return {"h": h, "k": k, "injected": injected, "extracted": injected - after, "total_after": after}


def reference() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for k in COUPLINGS:
        h = 1.0
        r = math.hypot(h, k)
        row = protocol(h, k)
        closed_a = h * h / r
        closed_b = math.hypot(h, 2 * k) - (h * h + 2 * k * k) / r
        if abs(row["injected"] - closed_a) > TOLERANCE or abs(row["extracted"] - closed_b) > TOLERANCE:
            raise RuntimeError(f"k = {k}: closed forms differ from the matrix evaluation")
        if row["total_after"] < -TOLERANCE:
            raise RuntimeError(f"k = {k}: total energy fell below the ground energy")
        for scale in (0.98, 1.02):
            if protocol(h, k, scale)["extracted"] >= row["extracted"]:
                raise RuntimeError(f"k = {k}: the closed-form angle is not a local optimum")
        rationalized = h * h * k * k / (r * (r * math.hypot(h, 2 * k) + h * h + 2 * k * k))
        if abs(rationalized - closed_b) > TOLERANCE:
            raise RuntimeError(f"k = {k}: rationalized E_B differs")
        a_coef, c_coef = h * k / r, (h * h + 2 * k * k) / r
        flips = {}
        for q in (0.1, 0.25, 0.5):
            closed_q = math.hypot(c_coef, (1 - 2 * q) * a_coef) - c_coef
            if abs(protocol(h, k, flip=q)["extracted"] - closed_q) > TOLERANCE:
                raise RuntimeError(f"k = {k}, q = {q}: record-flip formula differs")
            flips[str(q)] = closed_q
        rows.append(row | {"closed_form_injected": closed_a, "closed_form_extracted": closed_b, "record_flip": flips})
    weak = 1e-4
    r = math.hypot(1.0, weak)
    stable = weak * weak / (r * (r * math.hypot(1.0, 2 * weak) + 1 + 2 * weak * weak))
    if not 0.99 * weak * weak / 2 < stable < 1.01 * weak * weak / 2:
        raise RuntimeError("rationalized E_B leaves its weak-coupling asymptote k^2/2")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="JSON path; default prints a summary only")
    args = parser.parse_args()
    rows = reference()
    for row in rows:
        print(
            f"k/h = {row['k']:4}: injected {row['injected']:.12f}, extracted {row['extracted']:.12f}, "
            f"total after {row['total_after']:.12f}"
        )
    if args.out:
        args.out.write_text(json.dumps(rows, indent=1) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
