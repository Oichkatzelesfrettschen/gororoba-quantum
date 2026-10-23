"""Extended-precision probe of the local dimension of D_(5,12) at the {a, 0} witnesses.

At a nonzd-axis witness x0 = {e_p, 0} (rank_locus_local_dimension.witnesses)
the {a, 0} family has unit dimension 13 and the tangent bound is 15. The second-
and third-order compatibility tests are vacuous there, so a direction tangent to
T(x0) but not to D_(5,12) keeps sigma_21(L_y) of order 4 or higher in the
distance, which no float64 tolerance resolves near x0.

The probe draws seeded starts x0 + eps d, projects each onto the rank-20 cone by
alternating projection (truncate L_y to rank 20, then project orthogonally onto
the span of the left multiplications, which is orthogonal under the Frobenius
product with |L_(e_m)|^2 = 32), and refines the landing point at 110 decimal
digits until sigma_21 / sigma_1 < 1e-40, using mpmath.eigsy on L^T L. It
records the refined point's relative distance from the family cone
{a, 0} = span{(a, -i_4 a)} (famdist) and from x0. A cloud test at scale 1e-2
perturbs each witness, projects back in float64, and reads the span of the
displacements against the 16 of T(x0). The span bounds the local dimension of
the cone at x0 from above only: several lower-dimensional branches through x0
can together span 16 directions.

Falsifier, stated before the run: if D_(5,12) near x0 were the family alone, a
refined landing point would move to the family, so a refined famdist below half
its float64 value at any point, or a cloud span below 16, refutes the excess.

The record is numerical evidence and certifies nothing: famdist and ranks come
from floating and extended-precision arithmetic, and a certificate of the local
dimension needs an exact parameterized piece or equations cutting out D_(5,12).

Usage:
    "$PYTHON" scripts/rank_locus_nullity12_refinement.py --out docs/evidence/rank_locus_nullity12_refinement/result.json
    "$PYTHON" scripts/rank_locus_nullity12_refinement.py \
        --check docs/evidence/rank_locus_nullity12_refinement/result.json
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from rank_locus_local_dimension import witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-nullity12-refinement-v1"
DIM = 32
HALF = 16
RANK = 20
I4 = 8
SEED = 20_261_023
DIGITS = 110
TARGET_LOG10 = -40
FLOAT_TOLERANCE = 1e-14
EPSILONS = (0.03, 0.003)
CLOUD_ETA = 1e-2
CLOUD_SAMPLES = 64
SIGNIFICANT = 3

SIGNS = np.array([[cd_sign(DIM, i, j) for j in range(DIM)] for i in range(DIM)], dtype=np.int64)
ROW = np.arange(DIM)[:, None]
COLUMN = np.arange(DIM)[None, :]


def left(v: np.ndarray) -> np.ndarray:
    return v[ROW ^ COLUMN] * SIGNS[ROW ^ COLUMN, COLUMN]


BASIS = np.array([left(e) for e in np.eye(DIM)])


def onto_left(matrix: np.ndarray) -> np.ndarray:
    return np.einsum("aij,ij->a", BASIS, matrix) / DIM


def family_basis() -> np.ndarray:
    i4 = left(np.eye(DIM)[I4])[:HALF, :HALF]
    columns = []
    for index in range(1, HALF):
        if index == I4:
            continue
        a = np.eye(HALF)[index]
        columns.append(np.concatenate([a, -i4 @ a]))
    q, _ = np.linalg.qr(np.array(columns).T)
    return q


FAMILY = family_basis()


def famdist(y: np.ndarray) -> float:
    return float(np.linalg.norm(y - FAMILY @ (FAMILY.T @ y)) / np.linalg.norm(y))


def project(y: np.ndarray, limit: int = 20000) -> tuple[np.ndarray, int]:
    for step in range(limit):
        u, s, vt = np.linalg.svd(left(y))
        if s[RANK] / s[0] < FLOAT_TOLERANCE:
            return y, step
        y = onto_left((u[:, :RANK] * s[:RANK]) @ vt[:RANK])
    raise RuntimeError("alternating projection did not reach the float tolerance")


def refine(item: tuple[list[float], list[float]]) -> dict[str, Any]:
    """Alternating projection at DIGITS decimal digits until sigma_21 / sigma_1 < 10^TARGET_LOG10."""
    start, witness = item
    mpmath.mp.dps = DIGITS
    signs = SIGNS.tolist()
    y = [mpmath.mpf(value) for value in start]
    iterations = 0
    for _ in range(4000):
        m = mpmath.matrix(DIM, DIM)
        for k in range(DIM):
            for j in range(DIM):
                m[k, j] = y[k ^ j] * signs[k ^ j][j]
        values, vectors = mpmath.eigsy(m.T * m)
        order = sorted(range(DIM), key=lambda i: -values[i])
        ratio = mpmath.sqrt(abs(values[order[RANK]]) / values[order[0]])
        if ratio < mpmath.mpf(10) ** TARGET_LOG10:
            break
        iterations += 1
        top = mpmath.matrix(DIM, RANK)
        for column, index in enumerate(order[:RANK]):
            for row in range(DIM):
                top[row, column] = vectors[row, index]
        truncated = m * top * top.T
        y = [mpmath.fsum(truncated[k, k ^ e] * signs[e][k ^ e] for k in range(DIM)) / DIM for e in range(DIM)]
    else:
        raise RuntimeError("extended-precision projection did not reach the target")
    point = np.array([float(value) for value in y])
    unit = point / np.linalg.norm(point)
    return {
        "iterations": iterations,
        "log10_ratio": float(mpmath.log10(ratio)),
        "famdist": famdist(point),
        "distance_to_witness": float(np.linalg.norm(unit - np.array(witness))),
    }


def project_point(start: list[float]) -> list[float]:
    return project(np.array(start))[0].tolist()


def cloud_starts(witness: list[float], seed: int) -> list[list[float]]:
    y = np.array(witness)
    rng = np.random.default_rng(seed)
    starts = []
    for _ in range(CLOUD_SAMPLES):
        d = rng.normal(size=DIM)
        starts.append((y + CLOUD_ETA * d / np.linalg.norm(d)).tolist())
    return starts


def cloud_spectrum(witness: list[float], landed: list[list[float]]) -> list[float]:
    y = np.array(witness)
    rows = [(np.array(z) - y) / CLOUD_ETA for z in landed]
    s = np.linalg.svd(np.array(rows), compute_uv=False)
    return [float(value) for value in s / s[0]]


def rounded(value: float) -> float:
    return float(f"{value:.{SIGNIFICANT}g}")


def measure() -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    rows = [row for row in witnesses() if row["family"] == "nonzd-axis"]
    raw: list[list[float]] = []
    anchors: list[list[float]] = []
    labels: list[dict[str, Any]] = []
    for row in rows:
        x0 = np.array([float(Fraction(value)) for value in row["x"]])
        x0 /= np.linalg.norm(x0)
        for eps in EPSILONS:
            for kind in ("random", "mixed"):
                d = rng.normal(size=DIM)
                if kind == "mixed":
                    d = rng.normal() * np.eye(DIM)[I4] + rng.normal() * np.eye(DIM)[HALF + I4] + 0.3 * d
                d -= x0 * (x0 @ d)
                d /= np.linalg.norm(d)
                raw.append((x0 + eps * d).tolist())
                anchors.append(x0.tolist())
                labels.append({"witness": row["witness"], "epsilon": eps, "start": kind})
    landed = parallel.ordered_map(project_point, raw, min_items=2)
    for label, y in zip(labels, landed, strict=True):
        label["float64_famdist"] = famdist(np.array(y))
    refined = parallel.ordered_map(refine, list(zip(landed, anchors, strict=True)), min_items=2)
    centers = anchors[:: len(EPSILONS) * 2]
    perturbed = [cloud_starts(center, SEED + row["witness"]) for center, row in zip(centers, rows, strict=True)]
    cloud_landed = parallel.ordered_map(project_point, [z for group in perturbed for z in group], min_items=2)
    clouds = [
        cloud_spectrum(center, cloud_landed[i * CLOUD_SAMPLES : (i + 1) * CLOUD_SAMPLES])
        for i, center in enumerate(centers)
    ]
    points = []
    for label, result in zip(labels, refined, strict=True):
        points.append(
            {
                "witness": label["witness"],
                "epsilon": label["epsilon"],
                "start": label["start"],
                "float64_famdist": rounded(label["float64_famdist"]),
                "refined_famdist": rounded(result["famdist"]),
                "distance_to_witness": rounded(result["distance_to_witness"]),
                "refined_below_target": result["log10_ratio"] < TARGET_LOG10,
                "famdist_kept": result["famdist"] >= 0.5 * label["float64_famdist"],
            }
        )
    cloud_rows = []
    for row, values in zip(rows, clouds, strict=True):
        # The count is the span of the displacements, an upper bound on the local dimension of the cone at x0:
        # several lower-dimensional branches through x0 can together span more directions than any one of them.
        rank = int(sum(value > 10 * CLOUD_ETA for value in values))
        cloud_rows.append(
            {
                "witness": row["witness"],
                "eta": CLOUD_ETA,
                "rank": rank,
                "sigma_at_rank": rounded(values[rank - 1]),
                "sigma_after_rank": rounded(values[rank]),
            }
        )
    for point in points:
        if not (point["refined_below_target"] and point["famdist_kept"]):
            raise SystemExit(f"rank_locus_nullity12_refinement: point {point} collapses toward the family")
    for row in cloud_rows:
        if row["rank"] != 16:
            raise SystemExit(f"rank_locus_nullity12_refinement: cloud rank {row['rank']} at witness {row['witness']}")
    return {
        "schema": SCHEMA,
        "seed": SEED,
        "digits": DIGITS,
        "target_log10_ratio": TARGET_LOG10,
        "float_tolerance": FLOAT_TOLERANCE,
        "significant_digits": SIGNIFICANT,
        "points": points,
        "clouds": cloud_rows,
        "versions": {"numpy": np.__version__, "mpmath": mpmath.__version__},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = sorted(key for key in retained.keys() | data.keys() if retained.get(key) != data.get(key))
        if differing:
            raise SystemExit(f"rank_locus_nullity12_refinement: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    for point in data["points"]:
        print(
            f"witness {point['witness']} eps {point['epsilon']} {point['start']}: famdist "
            f"{point['float64_famdist']} -> {point['refined_famdist']}, |y - x0| {point['distance_to_witness']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
