"""Perceval's two-photon source model: the click visibility of a (M, g2) pair, and the overlap behind a figure.

Perceval's NoiseModel takes `indistinguishability` (the two-photon mean wavepacket overlap M) and `g2` (the
multiphoton emission). For the input |1,1> on a balanced beam splitter the photon-number distribution contains the
two-photon sector, where the coincidence fraction gives V = M exactly, and the multiphoton tails (1,2), (2,1), (2,2),
which add coincidences. The click visibility V = 1 - P(both modes click) / 0.5 therefore falls below M by about g2
(computed with Perceval 1.3.1: M 0.8728 and g2 0.020 give V 0.8537). A forecast that passes a measured visibility
as `indistinguishability` while the same model carries g2 simulates a visibility that is lower than the stated one;
overlap_for_click_visibility returns the M whose simulated click visibility equals the stated figure, for a figure
that is a click-coincidence visibility.

Two normalizations of the coincidence probability P(M) are in use. The "distinguishable" dip depth V = 1 - P(M) /
P(0) at the same g2 is the figure a Hong-Ou-Mandel scan reports (it reads 0 for distinguishable photons and
`scripts/belenos_best_mesh_first_principles.perceval_hom_visibility` computes it); the "half" form V = 1 - P(M) /
0.5 divides by the ideal distinguishable coincidence of a balanced beam splitter and reproduces the four values of
issue 888, but reads below 0 for distinguishable photons at g2 above 0. The two agree at g2 = 0 and differ by about
0.001 to 0.002 at the g2 of the retained platform reads.
"""

from __future__ import annotations

OVERLAP_BOUNDS = (0.0, 1.0)
SOLVER_TOLERANCE = 1e-12
# The simulator drops probabilities below 1e-6, so the forward function has gaps; an inversion that ends in one has a
# residual far above this bound and is refused.
RESIDUAL_TOLERANCE = 1e-9
REFERENCES = ("distinguishable", "half")


def coincidence(overlap: float, g2: float) -> float:
    """P(both modes click) for |1,1> on a balanced beam splitter under Perceval's source model."""
    import perceval as pcvl

    if not 0.0 <= overlap <= 1.0 or not 0.0 <= g2 < 1.0:
        raise ValueError(f"overlap {overlap} must lie in [0, 1] and g2 {g2} in [0, 1)")
    processor = pcvl.Processor("SLOS", pcvl.BS(), noise=pcvl.NoiseModel(indistinguishability=overlap, g2=g2))
    processor.with_input(pcvl.BasicState([1, 1]))
    results = processor.probs()["results"]
    return sum(float(p) for state, p in results.items() if len(state) == 2 and state[0] > 0 and state[1] > 0)


def _visibility(overlap: float, g2: float, denominator: float) -> float:
    return 1.0 - coincidence(overlap, g2) / denominator


def _denominator(g2: float, reference: str) -> float:
    if reference not in REFERENCES:
        raise ValueError(f"reference {reference!r} must be one of {REFERENCES}")
    return coincidence(0.0, g2) if reference == "distinguishable" else 0.5


def click_visibility(overlap: float, g2: float, reference: str = "distinguishable") -> float:
    """The simulated click visibility of |1,1> on a balanced beam splitter: 1 - P(both modes click) / reference, where
    the reference is P at overlap 0 and the same g2 ("distinguishable") or 0.5 ("half"). The model has unit
    transmission and perfect detection: a measured figure of a lossy detector weights the photon-number sectors
    differently, and its inversion needs the matching detection model."""
    return _visibility(overlap, g2, _denominator(g2, reference))


def overlap_for_click_visibility(visibility: float, g2: float, reference: str = "distinguishable") -> float:
    """The overlap M with click_visibility(M, g2, reference) equal to `visibility`, by bisection (the visibility rises
    with M).

    The final overlap bracket is at most SOLVER_TOLERANCE wide. The reference coincidence is computed once and reused
    by every evaluation. A visibility above the ceiling `click_visibility(1.0, g2, reference)` is refused; with
    multiphoton emission that ceiling can lie below 1. Measured with Perceval 1.3.1 (2026-11-15): the simulator drops
    probabilities below 1e-6, so at g2 = 0 the visibility reads exactly 1.0 within about 1e-6 of M = 1 (0.999999 at
    M = 1 - 1e-6). The ceiling therefore returns M = 1, and a visibility inside such a gap, which no overlap
    simulates, raises after the bisection because the residual of the result exceeds RESIDUAL_TOLERANCE. Measured
    2026-11-15 with Perceval 1.3.1 under a 1 GB cap: the first evaluation of a process takes about 2 s (import and
    setup) and a warm one about 1 ms, so a default solve of about 42 evaluations takes about 0.03 s warm.
    """
    denominator = _denominator(g2, reference)
    low, high = OVERLAP_BOUNDS
    floor, ceiling = _visibility(low, g2, denominator), _visibility(high, g2, denominator)
    if not floor <= visibility <= ceiling:
        raise ValueError(f"a click visibility of {visibility} lies outside [{floor}, {ceiling}] at g2 {g2}")
    if visibility == ceiling:
        return high
    while high - low > SOLVER_TOLERANCE:
        middle = (low + high) / 2
        if _visibility(middle, g2, denominator) < visibility:
            low = middle
        else:
            high = middle
    solved = (low + high) / 2
    residual = abs(_visibility(solved, g2, denominator) - visibility)
    if residual > RESIDUAL_TOLERANCE:
        raise ValueError(f"no overlap simulates a click visibility of {visibility} at g2 {g2}: residual {residual}")
    return solved
