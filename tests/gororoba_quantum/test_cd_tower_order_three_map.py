"""The order-three sedenion map of proofs/CdTowerOrderThreeMap.v against Gresnigt's psi and the cd_core product.

docs/evidence/cd-tower-ring-base-change/images.txt is the Rocq vm_compute output of images.v: for each basis
element e_m of level 4, the 16 coordinates over Z[sqrt 3] of psi2(e_m) = 2 psi(e_m), as pairs (a, b) for
a + b sqrt 3. The tests compare that table with twice the matrix of Gresnigt (arXiv 2609.10569), Eq. 61, written
out here from the formula psi(e_i) = -e_i/2 - (sqrt 3 / 2) e_(i+8), psi(e_(i+8)) = (sqrt 3 / 2) e_i - e_(i+8)/2
for i = 1..7 with e_0 and e_8 fixed, and recompute psi2(e_i) psi2(e_j) = 2 psi2(e_i e_j) on the 256 basis pairs
with cd_core.cd_sign extended bilinearly to Z[sqrt 3]. The Rocq theorem images_basis_check proves the same 256
identities for the pair-tower product; the identity of that product with cd_sign at integer coefficients is the
chain of proofs named in docs/evidence/cd-tower-ring/README.md ("Binding to cd_core"). The control flips the
sign of one entry of the table and requires the product check to fail.
"""

import re
from pathlib import Path

import cd_core

IMAGES = Path(__file__).resolve().parents[2] / "docs/evidence/cd-tower-ring-base-change/images.txt"
Root3 = tuple[int, int]
ZERO: Root3 = (0, 0)
DIM = 16


def r_add(x: Root3, y: Root3) -> Root3:
    return (x[0] + y[0], x[1] + y[1])


def r_mul(x: Root3, y: Root3) -> Root3:
    """(a + b sqrt 3)(c + d sqrt 3) = (a c + 3 b d) + (a d + b c) sqrt 3."""
    return (x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def r_scale(factor: int, x: Root3) -> Root3:
    return (factor * x[0], factor * x[1])


def cd_mul(a: list[Root3], b: list[Root3]) -> list[Root3]:
    """The bilinear extension of e_p e_q = cd_sign(16, p, q) e_(p xor q) to coordinates in Z[sqrt 3]."""
    out = [ZERO] * DIM
    for p, x in enumerate(a):
        if x == ZERO:
            continue
        for q, y in enumerate(b):
            if y == ZERO:
                continue
            out[p ^ q] = r_add(out[p ^ q], r_scale(cd_core.cd_sign(DIM, p, q), r_mul(x, y)))
    return out


def rocq_images() -> list[list[Root3]]:
    """Row m is the coordinate vector of psi2(e_m) printed by Rocq."""
    text = IMAGES.read_text(encoding="utf-8")
    # Rocq prints a negative integer as (-1)%Z and a nonnegative one as 1%Z.
    number = r"\(?(-?\d+)\)?%Z"
    pairs = [(int(a), int(b)) for a, b in re.findall(rf"\(\s*{number},\s*{number}\s*\)", text)]
    if len(pairs) != DIM * DIM:
        raise AssertionError(f"images.txt holds {len(pairs)} coordinates, expected {DIM * DIM}")
    return [pairs[m * DIM : (m + 1) * DIM] for m in range(DIM)]


def gresnigt_twice_psi() -> list[list[Root3]]:
    """Twice Eq. 61 on the basis: row m is the coordinate vector of 2 psi(e_m)."""
    rows = [[ZERO] * DIM for _ in range(DIM)]
    rows[0][0] = rows[8][8] = (2, 0)
    for i in range(1, 8):
        rows[i][i] = (-1, 0)
        rows[i][i + 8] = (0, -1)
        rows[i + 8][i] = (0, 1)
        rows[i + 8][i + 8] = (-1, 0)
    return rows


def apply(images: list[list[Root3]], vector: list[Root3]) -> list[Root3]:
    out = [ZERO] * DIM
    for m, coefficient in enumerate(vector):
        if coefficient == ZERO:
            continue
        for i, entry in enumerate(images[m]):
            out[i] = r_add(out[i], r_mul(coefficient, entry))
    return out


def product_failures(images: list[list[Root3]]) -> list[tuple[int, int]]:
    """Basis pairs (i, j) where psi2(e_i) psi2(e_j) differs from 2 psi2(e_i e_j)."""
    failures = []
    for i in range(DIM):
        for j in range(DIM):
            product = [ZERO] * DIM
            product[i ^ j] = (cd_core.cd_sign(DIM, i, j), 0)
            expected = [r_scale(2, x) for x in apply(images, product)]
            if cd_mul(images[i], images[j]) != expected:
                failures.append((i, j))
    return failures


def test_rocq_image_table_is_twice_gresnigt_psi() -> None:
    differing = [(m, i) for m in range(DIM) for i in range(DIM) if rocq_images()[m][i] != gresnigt_twice_psi()[m][i]]
    if differing:
        raise AssertionError(f"the Rocq table and twice Eq. 61 differ at (basis element, coordinate) {differing}")


def test_image_table_preserves_cd_core_products_up_to_two() -> None:
    failures = product_failures(rocq_images())
    if failures:
        raise AssertionError(f"psi2(e_i) psi2(e_j) differs from 2 psi2(e_i e_j) at {failures}")


def test_sign_flipped_table_fails_the_product_check() -> None:
    mutant = [row[:] for row in rocq_images()]
    mutant[1][9] = r_scale(-1, mutant[1][9])
    if mutant[1][9] == rocq_images()[1][9]:
        raise AssertionError("the mutated entry must be nonzero")
    if not product_failures(mutant):
        raise AssertionError("a table with one sign flipped must fail the product check")


def test_psi_has_order_three_on_the_table() -> None:
    """psi2 applied three times is 8 times the identity, so psi = psi2 / 2 has order dividing three."""
    table = rocq_images()
    for m in range(DIM):
        unit = [ZERO] * DIM
        unit[m] = (1, 0)
        cubed = apply(table, apply(table, apply(table, unit)))
        if cubed != [r_scale(8, x) for x in unit]:
            raise AssertionError(f"psi2 cubed differs from 8 at e_{m}: {cubed}")
