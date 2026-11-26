"""Complex kernel map of A_5 on bounded fixtures."""

from __future__ import annotations

import a5_complex_kernel_map_statevector as record
import pytest
from qiskit.quantum_info import Statevector


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


@pytest.mark.parametrize(
    ("i", "j", "label", "nullity"), [(1, 3, "i", 16), (1, 26, "i", 12), (1, 26, "-i", 12), (1, 26, "1", 4)]
)
def test_reading_equals_the_nullity_over_c(i: int, j: int, label: str, nullity: int) -> None:
    row = record.reading(i, j, record.PHASES[label])
    require(row["half_sum"] == row["selector"] == nullity == record.exact_nullity(i, j, record.PHASES[label]))
    require(row["unit_contrasts"])


def test_plain_phases_do_not_read_the_nullity() -> None:
    require(record.reading(1, 26, 1j, plain=True)["half_sum"] == -2)


def test_builder_reproduces_the_pinned_module() -> None:
    require(record.tie_failures() == {"operands": 8, "laws": 16, "failures": 0})


def test_complex_circuit_is_the_real_circuit_with_two_s_gates() -> None:
    for plus in (False, True):
        direct = Statevector(record.kernel_map(1, 26, 1j, plus))
        require(Statevector(record.s_form(1, 26, 1j, plus)).equiv(direct))
