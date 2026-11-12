"""Exact contracts for Cayley-Dickson block encodings and selected kernel filters.

The natural LCU uses signed basis permutations, not the Pauli expansion of L_a.
Its selector probabilities are rational for rational coefficients; the selected
block is exact even though preparing their square roots on a device is a separate
implementation. A Gram-polynomial certificate concerns real/rational matrices,
not finite-field rank, a compiled QSVT circuit, or a quantum speedup.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

import cd_core
import parallel
from cd_core import ExactMatrix, ExactScalar, ExactVector


@dataclass(frozen=True, init=False)
class NaturalLCU:
    """PREP probabilities and SELECT action for L_a / sum_i |a_i|.

    SELECT preserves its selector and applies sign(a_i) L_ei on the data.
    Padding selector states apply identity and have zero preparation weight.
    The selector size excludes data qubits and any implementation workspace.
    """

    dimension: int
    coefficients: ExactVector

    def __init__(self, dimension: int, coefficients: Sequence[ExactScalar]) -> None:
        cd_core.cd_sign(dimension, 0, 0)  # The specification validates the dimension.
        identity = (1,) + (0,) * (dimension - 1)
        exact = cd_core.cd_multiply_exact(dimension, coefficients, identity)
        if not any(exact):
            raise ValueError("a natural LCU needs a nonzero coefficient vector")
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "coefficients", exact)

    @property
    def terms(self) -> tuple[tuple[int, Fraction], ...]:
        return tuple((index, value) for index, value in enumerate(self.coefficients) if value)

    @property
    def alpha(self) -> Fraction:
        return sum((abs(value) for value in self.coefficients), Fraction(0))

    @property
    def data_qubits(self) -> int:
        return self.dimension.bit_length() - 1

    @property
    def selector_qubits(self) -> int:
        return (len(self.terms) - 1).bit_length()

    @property
    def preparation_probabilities(self) -> ExactVector:
        active = tuple(abs(value) / self.alpha for _, value in self.terms)
        return active + (Fraction(0),) * ((1 << self.selector_qubits) - len(active))

    @property
    def normalization_ratio_upper_squared(self) -> Fraction:
        """Upper bound on (alpha / ||L_a||_2)^2, not an evaluation of that norm.

        L_a e_0 = a gives ||L_a||_2 >= ||a||_2, and Cauchy-Schwarz bounds
        alpha^2 / ||a||_2^2 by the support size. SELECT/PREP gate costs remain.
        """
        squared_norm = sum((value * value for value in self.coefficients), Fraction(0))
        return self.alpha * self.alpha / squared_norm

    def select_action(self, selector: int, basis_index: int) -> tuple[int, int]:
        """Return (output data index, phase) with the selector left unchanged."""
        if type(selector) is not int or not 0 <= selector < 1 << self.selector_qubits:
            raise ValueError("selector lies outside the padded SELECT register")
        if type(basis_index) is not int or not 0 <= basis_index < self.dimension:
            raise ValueError("data basis index lies outside the algebra dimension")
        terms = self.terms
        if selector >= len(terms):
            return basis_index, 1
        left, coefficient = terms[selector]
        phase = (1 if coefficient > 0 else -1) * cd_core.cd_sign(self.dimension, left, basis_index)
        return left ^ basis_index, phase

    def selected_block(self) -> ExactMatrix:
        """Evaluate <PREP| SELECT |PREP> from its selector action exactly."""
        columns = parallel.ordered_map(_lcu_column, [(self, index) for index in range(self.dimension)])
        return _transpose(tuple(columns))


def _lcu_column(task: tuple[NaturalLCU, int]) -> ExactVector:
    encoding, column = task
    out = [Fraction(0)] * encoding.dimension
    for selector, probability in enumerate(encoding.preparation_probabilities):
        if probability:
            row, phase = encoding.select_action(selector, column)
            out[row] += probability * phase
    return tuple(out)


def _matrix(values: Sequence[Sequence[ExactScalar]]) -> ExactMatrix:
    if not values or not values[0]:
        raise ValueError("an exact matrix must have at least one row and column")
    width = len(values[0])
    if any(len(row) != width for row in values):
        raise ValueError("an exact matrix must be rectangular")
    if any(isinstance(value, bool) or not isinstance(value, int | Fraction) for row in values for value in row):
        raise ValueError("matrix entries must be integers or Fractions")
    return tuple(tuple(Fraction(value) for value in row) for row in values)


def _transpose(matrix: ExactMatrix) -> ExactMatrix:
    return tuple(zip(*matrix, strict=True))


def _identity(size: int) -> ExactMatrix:
    return tuple(tuple(Fraction(row == column) for column in range(size)) for row in range(size))


def _product_row(task: tuple[ExactVector, ExactMatrix]) -> ExactVector:
    row, second = task
    out = [Fraction(0)] * len(second[0])
    for index, value in enumerate(row):
        if value:
            for column, right in enumerate(second[index]):
                if right:
                    out[column] += value * right
    return tuple(out)


def _product(first: ExactMatrix, second: ExactMatrix) -> ExactMatrix:
    if len(first[0]) != len(second):
        raise ValueError("matrix product dimensions differ")
    return tuple(parallel.ordered_map(_product_row, [(row, second) for row in first]))


@dataclass(frozen=True)
class KernelProjector:
    """Exact orthogonal projector certified by P^2=P, P^T=P and A P=0.

    P = product_r (I - A^T A / r) also acts as identity on ker(A), so those
    checks establish the complete kernel. Supplied roots may include unused
    positive values; this certificate does not call them the minimal spectrum.
    """

    matrix: ExactMatrix
    nonzero_gram_roots: ExactVector
    projector: ExactMatrix
    nullity: int

    @property
    def rank(self) -> int:
        return len(self.matrix[0]) - self.nullity


def kernel_projector(
    matrix: Sequence[Sequence[ExactScalar]], nonzero_gram_roots: Sequence[ExactScalar]
) -> KernelProjector:
    """Certify a rational polynomial kernel filter, rejecting incomplete roots.

    Every supplied root is a distinct positive rational. Empty roots are
    admitted only for the zero matrix. No floating rank threshold enters.
    """
    exact = _matrix(matrix)
    if any(isinstance(root, bool) or not isinstance(root, int | Fraction) or root <= 0 for root in nonzero_gram_roots):
        raise ValueError("Gram roots must be positive rational numbers")
    roots = tuple(sorted(Fraction(root) for root in nonzero_gram_roots))
    if len(set(roots)) != len(roots):
        raise ValueError("Gram roots must be distinct")
    gram = _product(_transpose(exact), exact)
    size = len(gram)
    identity = _identity(size)
    projector = identity
    for root in roots:
        factor = tuple(
            tuple(identity[row][column] - gram[row][column] / root for column in range(size)) for row in range(size)
        )
        projector = _product(projector, factor)
    if any(value for row in _product(exact, projector) for value in row):
        raise ValueError("the supplied Gram roots do not annihilate the nonzero singular spectrum")
    if _transpose(projector) != projector or _product(projector, projector) != projector:
        raise ValueError("the polynomial did not produce an orthogonal projector")
    trace = sum((projector[index][index] for index in range(size)), Fraction(0))
    if trace.denominator != 1 or not 0 <= trace <= size:
        raise ValueError("the projector trace is not an admissible nullity")
    return KernelProjector(exact, roots, projector, int(trace))


def basis_unit_properties(dimension: int, index: int) -> dict[str, int | bool]:
    """Check a basis left action is a signed permutation and test skew symmetry."""
    cd_core.cd_sign(dimension, index, 0)
    coefficients = tuple(int(position == index) for position in range(dimension))
    matrix = cd_core.left_mult_matrix_exact(dimension, coefficients)
    columns = _transpose(matrix)
    images = [tuple(row for row, value in enumerate(column) if value) for column in columns]
    if any(len(image) != 1 for image in images) or len({image[0] for image in images}) != dimension:
        raise ValueError("a basis left action is not a permutation")
    if any(abs(column[image[0]]) != 1 for column, image in zip(columns, images, strict=True)):
        raise ValueError("a basis left action has a nonunit permutation entry")
    skew = all(matrix[row][column] == -matrix[column][row] for row in range(dimension) for column in range(dimension))
    return {"dimension": dimension, "basis_index": index, "signed_permutation": True, "skew_symmetric": skew}


def isotropy_counterexample(dimension: int, imaginary_index: int, modulus: int) -> dict[str, object]:
    """Certify v^T A v=0 with A v!=0 and invertible A=L_ei at an odd modulus.

    The signed permutation is invertible over every modulus. Exact skew
    symmetry makes the quadratic form zero on every vector when 2 is a unit.
    No primality claim is made: this applies to the program's odd primes and
    also to odd composite moduli. v=e_0 is the explicit nonkernel witness.
    """
    if type(modulus) is not int or modulus < 3 or modulus % 2 == 0:
        raise ValueError("the isotropy certificate requires an odd modulus greater than one")
    if type(imaginary_index) is not int or imaginary_index == 0:
        raise ValueError("the isotropy certificate requires an imaginary basis unit")
    properties = basis_unit_properties(dimension, imaginary_index)
    if not properties["skew_symmetric"]:
        raise ValueError("the selected left action is not skew-symmetric")
    vector = (1,) + (0,) * (dimension - 1)
    coefficients = tuple(int(index == imaginary_index) for index in range(dimension))
    image = cd_core.cd_multiply_exact(dimension, coefficients, vector)
    residues = tuple(int(value) % modulus for value in image)
    quadratic_form = sum(value * output for value, output in zip(vector, residues, strict=True)) % modulus
    if quadratic_form != 0 or not any(residues):
        raise ValueError("the selected vector does not falsify isotropy-implies-kernel")
    return {
        "dimension": dimension,
        "basis_index": imaginary_index,
        "modulus": modulus,
        "vector": list(vector),
        "image": list(residues),
        "quadratic_form": quadratic_form,
        "quadratic_form_zero_on_all_vectors": True,
        "invertible_by_signed_permutation": True,
    }


def modular_rank_counterexample(prime: int) -> dict[str, object]:
    """Exhibit an integer 2x2 matrix of rank two over Q and rank one over F_p.

    A=((1,2),((p+1)/2,1)) has determinant -p and a nonzero entry modulo p.
    These two minors certify both ranks without floating SVD or a rank oracle.
    The explicit vector (p-2,1) lies only in the modular kernel.
    FLINT's exact primality test also handles the program's large prime fields.
    """
    if type(prime) is not int or prime < 3 or prime % 2 == 0:
        raise ValueError("the rank counterexample requires an odd prime")
    from flint import fmpz

    if not fmpz(prime).is_prime():
        raise ValueError("the rank counterexample requires an odd prime")
    matrix = ((1, 2), ((prime + 1) // 2, 1))
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    vector = (prime - 2, 1)
    image = tuple(sum(value * entry for value, entry in zip(row, vector, strict=True)) for row in matrix)
    if determinant != -prime or not any(image) or any(value % prime for value in image):
        raise ValueError("the integer and modular rank witness differs")
    return {
        "prime": prime,
        "matrix": [list(row) for row in matrix],
        "determinant_over_Z": determinant,
        "rank_over_Q": 2,
        "rank_over_Fp": 1,
        "modular_kernel_vector": list(vector),
        "integer_image": list(image),
        "modular_image": [value % prime for value in image],
    }


def verify() -> dict[str, bool]:
    """Run small pure controls for admission without reading retained evidence."""
    coefficients = (Fraction(2, 3), Fraction(-5, 4), Fraction(0), Fraction(7, 6))
    encoding = NaturalLCU(4, coefficients)
    direct = cd_core.left_mult_matrix_exact(4, coefficients)
    if encoding.selected_block() != tuple(tuple(value / encoding.alpha for value in row) for row in direct):
        raise ValueError("the signed rational SELECT block differs from direct multiplication")
    matrix = ((1, 1, 0), (0, 0, 2))
    certificate = kernel_projector(matrix, (2, 4))
    if certificate.nullity != 1 or certificate.projector[0] != (Fraction(1, 2), Fraction(-1, 2), Fraction(0)):
        raise ValueError("the noncoordinate kernel control failed")
    try:
        kernel_projector(matrix, (2, 3))
    except ValueError:
        pass
    else:
        raise ValueError("an incorrect Gram root passed the projector certificate")
    isotropy_counterexample(4, 1, 5)
    modular_rank_counterexample(5)
    return {
        "signed_lcu": True,
        "kernel_projector": True,
        "wrong_gram_root_rejected": True,
        "isotropy": True,
        "modular_rank_mismatch": True,
    }
