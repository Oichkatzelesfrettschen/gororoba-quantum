"""Action of phi(a, b) = (a, -b) on the split coordinates z' and on the closure ideals of the regularity record.

phi negates y_16..y_31, i.e. conjugates z_k = y_k + i y_(16+k); with z_k = i^popcount(k) z'_k and rational z' the image
is z'_k -> (-1)^popcount(k) z'_k. Checks: which split slots flip sign; image of each orbit representative; closure
membership of each image; nullity preserved."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a5-strata-regularity"))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "gororoba_quantum"))
import strata_regularity as sr  # noqa: E402


def main() -> None:
    eq = sr.eq
    flip = [(-1) ** bin(k).count("1") for k in range(1, 16)]
    print("split slots with sign -1 (1-based):", [k for k in range(1, 16) if flip[k - 1] < 0])
    ideals = sr.closure_ideals()
    for name, zp in sr.REPS.items():
        img = [f * x for f, x in zip(flip, zp, strict=True)]
        y = eq.y_from_split([sr.Fraction(x) for x in zp])
        yi = eq.y_from_split([sr.Fraction(x) for x in img])
        phi_y = [v if i < 16 else -v for i, v in enumerate(y)]
        same = phi_y == yi
        inside = [k for k, gens in ideals.items() if sr.member(gens, img)]
        print(f"{name:5s} phi matches flip: {same}  nullity {eq.nullity(y)} -> {eq.nullity(yi)}  image in: {inside}")


if __name__ == "__main__":
    main()
