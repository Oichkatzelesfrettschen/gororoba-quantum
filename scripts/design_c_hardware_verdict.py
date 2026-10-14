"""Design C's falsifier applied to its measured ibm_fez spectra.

Design C (gororoba_quantum/DESIGN_NOTES.md) passes on a device when the
measured Walsh distribution of the associator phase is closer in total
variation distance to the true prediction than to the flip and the omit
control predictions by more than the shot-noise TVD. The measured histograms
are the ripple campaign's members ripple_design_c_{8_1_4,16_1_8,32_1_16} in
results/ripple/measured-ripple.json. Shot noise is the 99th percentile of
the TVD between the measured distribution and 2000 seeded multinomial
resamples of it at the measured shot count.

Usage: "$PYTHON" scripts/design_c_hardware_verdict.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import predict  # noqa: E402

MEASURED = ROOT / "results" / "ripple" / "measured-ripple.json"
PAIRS = ((8, 1, 4), (16, 1, 8), (32, 1, 16))
SEED = 20261013
RESAMPLES = 2000
# Verdicts and distances at the fixed seed; --check requires them.
EXPECTED = {
    8: ("resolved", 0.127, 0.310, 0.936),
    16: ("not resolved", 0.194, 0.218, 0.863),
    32: ("resolved", 0.268, 0.334, 0.842),
}


def _tvd(a: npt.NDArray[np.float64], b: npt.NDArray[np.float64]) -> float:
    return 0.5 * float(np.abs(a - b).sum())


def predictions(dim: int, i: int, j: int) -> dict[str, npt.NDArray[np.float64]]:
    """True, flip and omit Walsh distributions, as designs._check_design_c builds them."""
    phase = predict.associator_phase(dim, i, j)
    flipped = [w * (-1 if (j ^ x) == j else 1) for x, w in enumerate(phase)]
    hadamard = np.ones((1, 1))
    for _ in range(dim.bit_length() - 1):
        hadamard = np.kron(hadamard, np.array([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2))
    plus = np.ones(dim) / np.sqrt(dim)
    omitted = np.abs(hadamard @ predict.left_mult_matrix(dim, i) @ predict.left_mult_matrix(dim, j) @ plus) ** 2
    return {
        "true": np.asarray(predict.walsh_distribution(phase), dtype=float),
        "flip": np.asarray(predict.walsh_distribution(flipped), dtype=float),
        "omit": np.asarray(omitted, dtype=float),
    }


def verdicts() -> dict[int, dict[str, object]]:
    members = json.loads(MEASURED.read_text())["members"]
    rng = np.random.default_rng(SEED)
    out: dict[int, dict[str, object]] = {}
    for dim, i, j in PAIRS:
        counts = np.asarray(members[f"ripple_design_c_{dim}_{i}_{j}"]["counts"], dtype=float)
        shots = int(counts.sum())
        measured = counts / shots
        distances = {name: _tvd(measured, law) for name, law in predictions(dim, i, j).items()}
        noise = float(
            np.percentile([_tvd(rng.multinomial(shots, measured) / shots, measured) for _ in range(RESAMPLES)], 99)
        )
        margin = min(distances["flip"], distances["omit"]) - distances["true"]
        out[dim] = {
            "pair": [i, j],
            "shots": shots,
            "tvd": {name: round(value, 3) for name, value in distances.items()},
            "shot_noise_p99": round(noise, 3),
            "margin": round(margin, 3),
            "verdict": "resolved" if margin > noise else "not resolved",
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="require the recorded verdicts and distances")
    args = parser.parse_args(argv)
    result = verdicts()
    if args.check:
        for dim, (verdict, true, flip, omit) in EXPECTED.items():
            row = result[dim]
            if (row["verdict"], row["tvd"]) != (verdict, {"true": true, "flip": flip, "omit": omit}):
                raise SystemExit(f"D={dim}: {row} differs from the recorded {EXPECTED[dim]}")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
