"""The order-three sedenion map of proofs/CdTowerOrderThreeMap.v against Gresnigt's psi and the cd_core product.

docs/evidence/cd-tower-ring-base-change/images.txt is the Rocq vm_compute output of images.v: for each basis
element e_m of level 4, the 16 coordinates over Z[sqrt 3] of psi2(e_m) = 2 psi(e_m), as pairs (a, b) for
a + b sqrt 3. A table here is indexed table[m][i] = coordinate i of the image of e_m, so it is the transpose of
the matrix whose columns are the images. The tests compare the Rocq table with twice the formula of Gresnigt
(arXiv 2609.10569), Eq. 61, written out here (psi(e_i) = -e_i/2 - (sqrt 3 / 2) e_(i+8),
psi(e_(i+8)) = (sqrt 3 / 2) e_i - e_(i+8)/2 for i = 1..7 with e_0 and e_8 fixed) and with twice the sympy matrix
psi() of test_sedenion_automorphism_group.py, whose columns are the images; they recompute
psi2(e_i) psi2(e_j) = 2 psi2(e_i e_j) on the 256 basis pairs with cd_core.cd_sign extended bilinearly to
Z[sqrt 3]. The Rocq theorem images_basis_check proves the same 256 identities for the pair-tower product; the
identity of that product with cd_sign at integer coefficients is the chain of proofs named in
docs/evidence/cd-tower-ring/README.md ("Binding to cd_core"). The controls: the table with one sign flipped fails
the product check, and the transposed table, which is the inverse map and passes the product check, differs from
Eq. 61, so the product check alone does not identify the map.
"""

import re
import sys
from pathlib import Path

from sympy import Integer, sqrt

import cd_core
import parallel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_sedenion_automorphism_group import psi  # noqa: E402

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


Table = list[list[Root3]]


def pair_fails(item: tuple[Table, int, int]) -> bool:
    """Whether psi2(e_i) psi2(e_j) differs from 2 psi2(e_i e_j) for the table and the basis pair of the item."""
    images, i, j = item
    product = [ZERO] * DIM
    product[i ^ j] = (cd_core.cd_sign(DIM, i, j), 0)
    expected = [r_scale(2, x) for x in apply(images, product)]
    return cd_mul(images[i], images[j]) != expected


def product_failures(images: Table) -> list[tuple[int, int]]:
    """Basis pairs (i, j) where psi2(e_i) psi2(e_j) differs from 2 psi2(e_i e_j), the 256 pairs mapped in order."""
    pairs = [(i, j) for i in range(DIM) for j in range(DIM)]
    flags = parallel.ordered_map(pair_fails, [(images, i, j) for i, j in pairs])
    return [pair for pair, failed in zip(pairs, flags, strict=True) if failed]


def composite_on_unit(item: tuple[tuple[Table, ...], int]) -> list[Root3]:
    """The image of e_m under the tables of the item applied right to left."""
    tables, m = item
    vector = [ZERO] * DIM
    vector[m] = (1, 0)
    for table in reversed(tables):
        vector = apply(table, vector)
    return vector


def composite_defects(tables: tuple[Table, ...], factor: int) -> list[int]:
    """Basis indices m where the composite of the tables differs from factor times e_m."""
    images = parallel.ordered_map(composite_on_unit, [(tables, m) for m in range(DIM)], min_items=1)
    return [m for m, image in enumerate(images) if image != [(factor if i == m else 0, 0) for i in range(DIM)]]


def test_rocq_image_table_is_twice_gresnigt_psi() -> None:
    differing = [(m, i) for m in range(DIM) for i in range(DIM) if rocq_images()[m][i] != gresnigt_twice_psi()[m][i]]
    if differing:
        raise AssertionError(f"the Rocq table and twice Eq. 61 differ at (basis element, coordinate) {differing}")


def test_rocq_image_table_is_twice_the_sympy_psi_matrix() -> None:
    """Column m of psi() is the image of e_m, so the table entry [m][i] is twice the matrix entry [i, m]."""
    matrix = psi()
    table = rocq_images()
    differing = [
        (m, i)
        for m in range(DIM)
        for i in range(DIM)
        if (Integer(table[m][i][0]) + Integer(table[m][i][1]) * sqrt(3) - 2 * matrix[i, m]).expand() != 0
    ]
    if differing:
        raise AssertionError(f"the Rocq table and 2 psi() differ at (basis element, coordinate) {differing}")


def test_transposed_table_is_another_product_preserving_map() -> None:
    """The transpose is twice the inverse of psi: it passes the product check and is not Eq. 61."""
    table = rocq_images()
    transposed = [[table[i][m] for i in range(DIM)] for m in range(DIM)]
    if product_failures(transposed):
        raise AssertionError("the transposed table must also preserve products up to the factor 2")
    if transposed == gresnigt_twice_psi():
        raise AssertionError("the transposed table must differ from twice Eq. 61")
    if defects := composite_defects((transposed, table), 4):
        raise AssertionError(f"the transposed table composed with the table differs from 4 at basis indices {defects}")


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
    if defects := composite_defects((table, table, table), 8):
        raise AssertionError(f"psi2 cubed differs from 8 at basis indices {defects}")
