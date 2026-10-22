"""Sedenion left operators retain a Clifford subfamily beyond normed division."""

from hypercomplex_clifford_envelope import certificate


def test_eight_generator_envelope_spans_real_endomorphisms() -> None:
    record = certificate()
    if record["anticommutator_failures"] != 0 or record["square_failures"] != 0:
        raise RuntimeError("the eight generators must satisfy Cl(0,8) exactly")
    if record["image_dimension"] != 256 or not record["hilbert_schmidt_orthogonal"]:
        raise RuntimeError("256 orthogonal words must span all real 16 by 16 matrices")
    if record["left_encoding_is_product_homomorphism"]:
        raise RuntimeError("an associative operator envelope does not make sedenions associative")
