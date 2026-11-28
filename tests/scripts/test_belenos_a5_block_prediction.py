"""Fixtures for the offline A_5 coset-block predictions of a linear-optics chip."""

from __future__ import annotations

import belenos_a5_block_prediction as bab


def test_block_nullities_sum_to_the_global_nullity_of_each_operand() -> None:
    rec = bab.record()
    if {name: row["global_nullity"] for name, row in rec.items()} != {"e1+e26": 4, "e1+e10": 8, "e1+e17": 0}:
        raise AssertionError(rec)


def test_basis_input_is_blind_to_nullity_and_prepared_kernel_input_reads_zero() -> None:
    rec = bab.record()
    blocks = [b for row in rec.values() for b in row["first_blocks"]]
    if {b["basis_input_0_in_block"] for b in blocks} != {0.5}:
        raise AssertionError(blocks)
    deficient = [b for b in rec["e1+e26"]["first_blocks"] if b["nullity"] == 2]
    reads = [i["in_block"] for i in deficient[0]["prepared_right_singular_inputs"]]
    if len(deficient) != 1 or sorted(reads) != [0.0, 0.0, 1.0, 1.0]:
        raise AssertionError(deficient)
    if any(i["in_block"] != 0.5 for b in rec["e1+e17"]["first_blocks"] for i in b["prepared_right_singular_inputs"]):
        raise AssertionError(rec["e1+e17"])


def test_a_prepared_input_off_the_singular_vector_changes_the_share() -> None:
    import numpy as np

    rec = bab.record()
    block = rec["e1+e26"]["first_blocks"][1]["block_indices"]
    a = np.array(bab.left_mult_matrix(bab.DIM, [1.0 if i in (1, 26) else 0.0 for i in range(bab.DIM)]))
    b = a[np.ix_(block, block)]
    x = np.eye(4)[0]
    if abs(float(np.sum((b @ x) ** 2)) / bab.ALPHA**2 - 0.5) > 1e-12:
        raise AssertionError("basis input share is not 1/2")
    _, sv, vt = np.linalg.svd(b)
    if abs(float(np.sum((b @ vt[-1]) ** 2))) > 1e-12 or sv[-1] > 1e-12:
        raise AssertionError("the last right singular vector is not in the kernel")
