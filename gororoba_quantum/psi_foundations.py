"""Operational CHSH falsifier: no ontological interpretation is assumed.

Run: python -m unittest discover -s tests -p 'test_psi_foundations.py'
"""

from fractions import Fraction
from itertools import product
from math import sqrt


def classical_chsh_bound():
    """Enumerate all deterministic local response assignments."""
    values = set()
    for a0, a1, b0, b1 in product((-1, 1), repeat=4):
        values.add(a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1)
    return sorted(values)


def singlet_correlation(a, b):
    """Unit planar directions a,b; E(a,b)=-a dot b."""
    return -(a[0] * b[0] + a[1] * b[1])


def quantum_chsh():
    """Singlet with A0=z, A1=x, B0=(z+x)/sqrt(2), B1=(z-x)/sqrt(2)."""
    a0, a1 = (1.0, 0.0), (0.0, 1.0)
    b0 = (1 / sqrt(2), 1 / sqrt(2))
    b1 = (1 / sqrt(2), -1 / sqrt(2))
    return (
        singlet_correlation(a0, b0)
        + singlet_correlation(a0, b1)
        + singlet_correlation(a1, b0)
        - singlet_correlation(a1, b1)
    )


def product_probability(p, q):
    """Independent preparations: P(lambda1,lambda2)=P1*P2."""
    return {(i, j): p[i] * q[j] for i in p for j in q}


def overlap(p, q):
    """Classical epistemic overlap of normalized finite distributions."""
    if set(p) != set(q) or sum(p.values()) != 1 or sum(q.values()) != 1:
        raise ValueError("distributions must share support and normalize to one")
    if any(x < 0 for x in (*p.values(), *q.values())):
        raise ValueError("negative probability")
    return sum((min(p[k], q[k]) for k in p), Fraction(0))


def independent_common_overlap(p, q):
    """Probability both independently prepared ontic samples lie in common part.

    This is omega**2, NOT a PBR theorem proof: measurement exclusion and
    preparation independence beyond this toy model require separate assumptions.
    """
    return overlap(p, q) ** 2
