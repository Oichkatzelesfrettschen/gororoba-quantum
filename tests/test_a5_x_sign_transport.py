"""The check of the sign transport of the same-sign X module maps, on a fixture built from the module's tables.

The retained record replays on demand through the gate core-a5-x-sign-transport of ci/gates.json.
"""

import importlib.util
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "docs/evidence/a5-kernel-attachments/x_sign_transport.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_x_sign_transport", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fixture(mod: ModuleType) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kind, prime, root in mod.tasks():
        if kind == "signs":
            rows.append({"item": kind, "prime": prime, "G_signs": list(mod.G_SIGNS), "J_signs": list(mod.J_SIGNS)})
            continue
        row: dict[str, Any] = {"item": kind, "transported": [0, 0], "one_more_sign": [0] * mod.N}
        if kind == "qi":
            rows.append(row | {"identity": [27, 27], "conjugate": [0, 0], "square": [0]})
            continue
        row |= {"prime": prime, "root": root, "scalar": [1, 1, mod.SCALARS[kind]], "control_indices": [3, 7, 10]}
        row |= {control: [1, 0, 0] for control in mod.cmp.CONTROLS}
        row |= {"from_side": list(mod.SIDES), "to_side": list(mod.SIDES), "linear_parts": [0, 0]}
        for side, tag in (("from", "xm"), ("to", "xp")):
            row[f"{side}_image"] = [list(pair) for pair in mod.expected_images(kind, tag, prime, root)]
            row |= {f"{side}_solutions": [1], f"{side}_det_nonzero": [1], f"{side}_control_solutions": [0]}
        if kind == "weight":
            row["square"] = [0]
        rows.append(row)
    return rows


def test_the_fixture_passes_and_holds_ten_rows() -> None:
    mod = load()
    rows = fixture(mod)
    found = mod.problems(rows, mod.diagonal_text(mod.W_SIGNS))
    if len(rows) != 10 or found:
        raise AssertionError(found)


def test_the_residue_of_the_scalar_is_accepted() -> None:
    mod = load()
    rows = fixture(mod)
    rows[4]["scalar"] = [1, 1, 32008]
    if mod.problems(rows, mod.diagonal_text(mod.W_SIGNS)):
        raise AssertionError(rows[4])


# rows: 0-2 signs, 3 the Q(i) item, 4-6 the header slice, 7-9 the weight slice.
MUTATIONS = {
    "a header sign vector with one sign changed": lambda rows: rows[2]["G_signs"].__setitem__(0, -1),
    "a header generator carried to neither sign": lambda rows: rows[0]["J_signs"].__setitem__(3, 0),
    "an ideal that the weight-slice substitution misses over Q(i)": lambda rows: rows[3].update(transported=[0, 4]),
    "equal X- and X+ ideals": lambda rows: rows[3].update(identity=[0, 0]),
    "a conjugate that is another ideal": lambda rows: rows[3].update(conjugate=[3, 3]),
    "a square that does not commute over Q(i)": lambda rows: rows[3].update(square=[2]),
    "a square that does not commute at a prime": lambda rows: rows[8].update(square=[1]),
    "every added sign accepted": lambda rows: rows[5].update(one_more_sign=[1] * 15),
    "fourteen added signs": lambda rows: rows[7]["one_more_sign"].pop(),
    "the header scalar 1": lambda rows: rows[4].update(scalar=[1, 1, 1]),
    "the weight scalar -1": lambda rows: rows[9].update(scalar=[1, 1, -1]),
    "no scalar": lambda rows: rows[6].update(scalar=[1, 0, 0]),
    "exchanged images accepted": lambda rows: rows[4].update(control_images_exchanged=[1, 1, -1]),
    "a perturbed substitution accepted": lambda rows: rows[8].update(control_map_perturbed=[1, 1, 1]),
    "the X+ header map on the X- side": lambda rows: rows[4]["from_image"][0].__setitem__(1, "-2*y(6)"),
    "the X- weight map on the X+ side": lambda rows: rows[7]["to_image"][1].__setitem__(1, "10754*y(5)"),
    "a two-dimensional solution space": lambda rows: rows[5].update(to_solutions=[2]),
    "a header ideal the signs miss": lambda rows: rows[6].update(transported=[5, 0]),
    "a row removed": lambda rows: rows.pop(),
    "two rows exchanged": lambda rows: rows.insert(4, rows.pop(5)),
    "an extra field": lambda rows: rows[9].update(note="x"),
}

# The one reason each changed record is reported for: every reported line holds this text.
REASONS = {
    "a header sign vector with one sign changed": "the header sign vectors differ",
    "a header generator carried to neither sign": "the header sign vectors differ",
    "an ideal that the weight-slice substitution misses over Q(i)": "does not carry the X- ideal",
    "equal X- and X+ ideals": "tests nothing",
    "a conjugate that is another ideal": "the conjugate of the X- ideal",
    "a square that does not commute over Q(i)": "G+ S_w differs",
    "a square that does not commute at a prime": "G+ S_w differs",
    "every added sign accepted": "no single added sign",
    "fourteen added signs": "no single added sign",
    "the header scalar 1": "is not -1 times",
    "the weight scalar -1": "is not 1 times",
    "no scalar": "is not -1 times",
    "exchanged images accepted": "control_images_exchanged found a scalar",
    "a perturbed substitution accepted": "control_map_perturbed found a scalar",
    "the X+ header map on the X- side": "a side, a solution count",
    "the X- weight map on the X+ side": "a side, a solution count",
    "a two-dimensional solution space": "a side, a solution count",
    "a header ideal the signs miss": "does not carry the X- ideal",
    "a row removed": "not the ten items",
    "two rows exchanged": "not the ten items",
    "an extra field": "unexpected or missing field",
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_changed_record_is_reported(name: str) -> None:
    mod = load()
    rows = fixture(mod)
    MUTATIONS[name](rows)
    found = mod.problems(rows, mod.diagonal_text(mod.W_SIGNS))
    if not found or any(REASONS[name] not in line for line in found):
        raise AssertionError(f"{name}: reported as {found}")


def test_another_weight_slice_matrix_is_reported() -> None:
    mod = load()
    signs = list(mod.W_SIGNS)
    signs[2] = -1
    found = mod.problems(fixture(mod), mod.diagonal_text(tuple(signs)))
    if len(found) != 1 or "not the diagonal of signs" not in found[0]:
        raise AssertionError(found)


def test_gaussian_text_and_arithmetic() -> None:
    mod = load()
    cases: dict[str, tuple[Fraction | int, Fraction | int]] = {
        "0": (0, 0),
        "-524288": (-524288, 0),
        "(-524288*i)": (0, -524288),
        "(i)": (0, 1),
        "-i": (0, -1),
    }
    cases |= {"(1/2-3*i)": (Fraction(1, 2), -3), "(2+i)": (2, 1)}
    for text, value in cases.items():
        if mod.gaussian(text) != value:
            raise AssertionError(text)
    for bad in ("", "x", "2*y", "()"):
        with pytest.raises(ValueError):
            mod.gaussian(bad)
    one, zero, i = (Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)), (Fraction(0), Fraction(1))
    matrix = [[i, one], [(Fraction(2), Fraction(0)), i]]
    if mod.product(matrix, mod.inverse(matrix)) != [[one, zero], [zero, one]]:
        raise AssertionError("the inverse over Q(i) fails on a 2 x 2 matrix")
    with pytest.raises(ZeroDivisionError):
        mod.inverse([[one, i], [i, (Fraction(-1), Fraction(0))]])
    if mod.text_of((Fraction(1, 2), Fraction(1)), 32009, 10754) != str((16005 + 10754) % 32009):
        raise AssertionError("the reduction of 1/2 + i at 32009")
    if mod.text_of((Fraction(1, 2), Fraction(-1)), 0, 0) != "(1/2+(-1)*i)":
        raise AssertionError("the Q(i) text of 1/2 - i")


def test_the_slice_map_of_diagonal_matrices_is_their_product() -> None:
    mod = load()
    one, zero = (Fraction(1), Fraction(0)), (Fraction(0), Fraction(0))
    i = (Fraction(0), Fraction(1))
    minus = [[i, zero], [zero, one]]
    plus = [[i, zero], [zero, (Fraction(-1), Fraction(0))]]
    found = mod.slice_map(minus, (1, -1), plus)
    if [[mod.shown(x) for x in row] for row in found] != [["1", "0"], ["0", "1"]]:
        raise AssertionError(found)


def test_the_tasks_are_ten_items_at_three_split_primes() -> None:
    mod = load()
    if len(mod.tasks()) != 10 or any(pow(root, 2, prime) != prime - 1 for prime, root in mod.PRIMES):
        raise AssertionError(mod.tasks())
    if len(mod.W_SIGNS) != mod.N or len(mod.G_SIGNS) != mod.N or set(mod.W_SIGNS) | set(mod.G_SIGNS) != {1, -1}:
        raise AssertionError("the sign vectors are not 15 signs")
