"""Exact assessor ET cells in the cd_core convention; ordered cells count twice per edge.

The unnormalized assessor e_low + e_high has Gram eigenvalues 0, 2, 4.
Each occupied paired block contributes one kernel vector. Finite checks of
these blocks establish bounded conformance separately from an all-order proof.
"""

from dataclasses import dataclass
from functools import cached_property

from cd_core import cd_sign


@dataclass(frozen=True)
class ETCell:
    column: int
    valid: bool
    exclusion: str | None
    occupied: bool
    sign: int | None
    emanation_index: int

    @property
    def value(self) -> int:
        return (self.sign or 0) * self.emanation_index


@dataclass(frozen=True)
class ETSpec:
    dimension: int
    strut: int
    row: int

    def __post_init__(self) -> None:
        if type(self.dimension) is not int or self.dimension < 16 or self.dimension & (self.dimension - 1):
            raise ValueError("ET dimension must be an integer power of two, at least 16")
        if type(self.strut) is not int or not 1 <= self.strut < self.generator:
            raise ValueError("ET strut must lie between one and G-1")
        if type(self.row) is not int or not 1 <= self.row < self.generator or self.row == self.strut:
            raise ValueError("ET row must be an assessor low label, excluding the strut")

    @property
    def bits(self) -> int:
        return self.dimension.bit_length() - 1

    @property
    def generator(self) -> int:
        return self.dimension // 2

    @property
    def xor_label(self) -> int:
        return self.generator ^ self.strut

    @property
    def high(self) -> int:
        return self.row ^ self.xor_label

    @property
    def tone_row(self) -> tuple[int, ...]:
        front = tuple(label for label in range(1, self.generator) if label != self.strut and label < label ^ self.strut)
        return front + tuple(label ^ self.strut for label in reversed(front))

    def block_signs(self, column: int) -> tuple[int, int]:
        if type(column) is not int or not 0 <= column < self.generator:
            raise ValueError("column must lie in the padded low-label register")
        partner = column ^ self.xor_label
        return (
            cd_sign(self.dimension, self.high, column) * cd_sign(self.dimension, self.row, partner),
            cd_sign(self.dimension, self.high, partner) * cd_sign(self.dimension, self.row, column),
        )

    def cell(self, column: int) -> ETCell:
        first, second = self.block_signs(column)
        exclusion = next(
            (
                reason
                for label, reason in (
                    (0, "padding"),
                    (self.strut, "strut_label"),
                    (self.row, "diagonal"),
                    (self.row ^ self.strut, "strut_opposite"),
                )
                if column == label
            ),
            None,
        )
        occupied = exclusion is None and first == second
        return ETCell(column, exclusion is None, exclusion, occupied, first if occupied else None, self.row ^ column)

    @cached_property
    def degree(self) -> int:
        return sum(self.cell(column).occupied for column in range(self.generator))

    @property
    def spectrum(self) -> dict[int, int]:
        return {0: self.degree, 2: self.dimension - 2 * self.degree, 4: self.degree}

    def decode(self, data_index: int) -> int:
        if type(data_index) is not int or not 0 <= data_index < self.dimension:
            raise ValueError("data outcome lies outside the algebra register")
        return self.row ^ data_index ^ (self.xor_label if data_index >= self.generator else 0)


def table_census(dimension: int, strut: int) -> dict[str, int]:
    spec = ETSpec(dimension, strut, 1 if strut != 1 else 2)
    labels = spec.tone_row
    return {
        "filled": sum(ETSpec(dimension, strut, row).degree for row in labels),
        "addressable": len(labels) * (len(labels) - 2),
    }


def child_box(parent_dimension: int, strut: int) -> dict:
    parent = ETSpec(parent_dimension, strut, 1 if strut != 1 else 2)
    primary = parent.tone_row
    shifted = tuple(parent.generator ^ column for column in primary)
    boundary = (parent.generator, parent.generator ^ strut)
    labels = shifted + boundary
    interior = sum(
        ETSpec(2 * parent_dimension, strut, row).cell(column).occupied for row in shifted for column in shifted
    )
    total = sum(ETSpec(2 * parent_dimension, strut, row).cell(column).occupied for row in labels for column in labels)
    return {
        "primary": primary,
        "shifted": shifted,
        "boundary": boundary,
        "counts": {"interior": interior, "border": total - interior, "box": total},
    }
