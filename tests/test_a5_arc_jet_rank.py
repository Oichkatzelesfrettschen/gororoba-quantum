"""Bounded falsifiers of the arc-jet rank producer: functionals by hand, the J and K2 checks, the record check.

A synthetic slice replaces the target's ideals and its arcs, so no test runs Singular or reads a retained record's
matrix. Two tests build one real arc of each header and compare it with the retained record's own entry for it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

JETS = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "arc-jets"
sys.path.insert(0, str(JETS))

import jet_rank as J  # noqa: E402

NAME = "e8nm-p32009"
PRIME = 32009
NGEN = J.A.NGEN
NVAR = J.A.NVAR


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _t(*indices: int) -> J.A.Poly:
    """The polynomial sum of the t variables with 1-based `indices`."""
    out: J.A.Poly = {}
    for index in indices:
        exps = [0] * NVAR
        exps[index - 1] = 1
        out[tuple(exps)] = 1
    return out


def _y(terms: dict[tuple[int, ...], int]) -> J.A.Poly:
    """A polynomial in y(1..21) from {1-based variable indices of a monomial: coefficient}."""
    out: J.A.Poly = {}
    for indices, coefficient in terms.items():
        exps = [0] * NGEN
        for index in indices:
            exps[index - 1] += 1
        out[tuple(exps)] = coefficient % PRIME
    return out


def _monomial(*indices: int) -> tuple[int, ...]:
    exps = [0] * NGEN
    for index in indices:
        exps[index - 1] += 1
    return tuple(exps)


def _mono(coefficient: int, order: int) -> J.Lm.L:
    return J.Lm.L.mono(coefficient, order, J.TOP, PRIME)


def _zero() -> J.Lm.L:
    return J.Lm.L([], 0, J.TOP, PRIME)


class Slice:
    """The synthetic slice: G_1 = t1, G_2 = t2, G_3 = t1 + t2, G_4 .. G_21 = 0 and the arc

    t1 = s^2 + 3 s^3, t2 = 5 s^2, t3 .. t9 = 0 (index-independent), so v = 2, e = 2 and, after division by s^v,
    g_1 = 1 + 3s, g_2 = 5, g_3 = 6 + 3s modulo s^2.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch, ideal_j: list[J.A.Poly], k2: list[J.A.Poly]) -> None:
        ideal_g = [_t(1), _t(2), _t(1, 2)] + [{} for _ in range(NGEN - 3)]
        monkeypatch.setattr(J, "slice_ideals", lambda _name: (ideal_j, ideal_g, k2))
        monkeypatch.setattr(J, "arc", self.arc)

    @staticmethod
    def arc(_target: J.Target, _idx: int) -> list[J.Lm.L]:
        return [_mono(1, 2) + _mono(3, 3), _mono(5, 2)] + [_zero() for _ in range(NVAR - 2)]


KERNEL = _y({(3,): 1, (1,): -1, (2,): -1})  # y3 - y1 - y2 vanishes on g = (g_1, g_2, g_3) identically


def test_functionals_of_one_arc_match_a_hand_computation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation caught: a rows[r][col] transposition, a wrong truncation length of truncated_product, or an
    s^v shift off by one (g_j read at v + k + 1) in jet_rows."""
    Slice(monkeypatch, [_t(3)], [KERNEL])
    columns = [_monomial(1), _monomial(2), _monomial(3), _monomial(1, 2), _monomial(3, 3), _monomial(1, 1)]
    out = J.jet_rows((NAME, 0, 1, columns))
    _check((out["e"], out["v"], out["j_nonzero"], out["k2_nonzero"]) == (2, 2, 0, 0))
    # Row 0 holds the coefficient of s^0 and row 1 that of s^1 of each column's product of the g_j:
    # y1: 1 + 3s; y2: 5; y3: 6 + 3s; y1 y2: 5 + 15s; y3^2: 36 + 36s; y1^2: 1 + 6s.
    _check(out["rows"] == [[1, 5, 6, 5, 36, 1], [3, 0, 3, 15, 36, 6]])
    _check(out["family"] == list(J.FAMILIES[0]))
    _check(out["coefficients"]["w"] == J.coefficients(0, 1, PRIME))


def test_rank_is_the_rank_over_the_prime_field() -> None:
    """Mutation caught: rank() reducing modulo a fixed prime instead of its argument (the second matrix has
    determinant 7, so its rank is 3 over Q and modulo 32009 and 2 modulo 7)."""
    _check(J.rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 3, PRIME) == 2)
    _check(J.rank([[1, 1, 0], [1, 8, 0], [0, 0, 1]], 3, 7) == 2)
    _check(J.rank([[1, 1, 0], [1, 8, 0], [0, 0, 1]], 3, PRIME) == 3)
    _check(J.rank([[0, 0], [0, 0]], 2, PRIME) == 0)


def test_the_k2_check_reports_a_quadric_the_arc_violates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation caught: k2_nonzero forced to 0, or the comparison cut to the s^0 coefficient (`[:1]`, which the
    last quadric below separates from the full `[:eo]`: it vanishes at s^0 and not at s^1)."""
    quadrics = [
        KERNEL,  # 0 modulo s^2
        _y({(1,): 1, (2,): -1}),  # g_1 - g_2 = -4 + 3s
        _y({(1, 2): 1, (1, 1): -5}),  # g_1 g_2 - 5 g_1^2 = 0 - 15 s
    ]
    Slice(monkeypatch, [_t(3)], quadrics)
    out = J.jet_rows((NAME, 0, 1, [_monomial(1)]))
    _check(out["k2_nonzero"] == 2)
    Slice(monkeypatch, [_t(3)], quadrics[:1])
    _check(J.jet_rows((NAME, 0, 1, [_monomial(1)]))["k2_nonzero"] == 0)
    Slice(monkeypatch, [_t(3)], quadrics[2:])
    _check(J.jet_rows((NAME, 0, 1, [_monomial(1)]))["k2_nonzero"] == 1)


def test_the_j_check_reports_a_generator_the_arc_violates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation caught: j_nonzero forced to 0, or counted only for the first generator of J."""
    # t3 vanishes on the arc; t1 and t2 - t1 do not.
    Slice(monkeypatch, [_t(3), _t(1), {**_t(2), **{k: PRIME - 1 for k in _t(1)}}], [KERNEL])
    _check(J.jet_rows((NAME, 0, 1, [_monomial(1)]))["j_nonzero"] == 2)
    Slice(monkeypatch, [_t(3)], [KERNEL])
    _check(J.jet_rows((NAME, 0, 1, [_monomial(1)]))["j_nonzero"] == 0)


def test_an_arc_with_a_unit_coordinate_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation caught: dropping the `eo < 2` guard, which would let a jet see the reduced support only."""
    Slice(monkeypatch, [_t(3)], [KERNEL])
    monkeypatch.setattr(J, "arc", lambda _t, _i: [_mono(1, 1)] + [_zero() for _ in range(NVAR - 1)])
    with pytest.raises(RuntimeError, match="valuation 1"):
        J.jet_rows((NAME, 0, 1, [_monomial(1)]))
    monkeypatch.setattr(J, "arc", lambda _t, _i: [_mono(1, 0)] + [_zero() for _ in range(NVAR - 1)])
    with pytest.raises(RuntimeError, match="origin"):
        J.jet_rows((NAME, 0, 1, [_monomial(1)]))


def _record(out: Path, narcs: int = 2) -> dict[str, Any]:
    return J.compute(NAME, 1, narcs, 1, out)


def test_a_failed_check_makes_the_record_inconsistent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Mutation caught: dropping `or bad` from the status of compute, so that an arc off V(J) still reads as a
    lower bound; also an arcs_with_failed_check that omits the arc."""
    Slice(monkeypatch, [_t(3)], [KERNEL])
    clean = _record(tmp_path / "clean.json")
    # Two arcs of the synthetic slice span the one-dimensional space of the g's: rank 2 of at most 21.
    _check(clean["status"] == "lower_bound_only" and clean["rank"] == 2 and clean["bound"] == "2 <= h_1 <= 21")
    _check(clean["arcs_with_failed_check"] == [] and len(clean["arcs"]) == 2)
    _check([c["rank"] for c in clean["checkpoints"]] == [2, 2])
    Slice(monkeypatch, [_t(1)], [KERNEL])
    off_j = _record(tmp_path / "off_j.json")
    _check(off_j["status"] == "inconsistent" and off_j["arcs_with_failed_check"] == [0, 1])
    Slice(monkeypatch, [_t(3)], [_y({(1,): 1, (2,): -1})])
    off_k2 = _record(tmp_path / "off_k2.json")
    _check(off_k2["status"] == "inconsistent" and off_k2["arcs_with_failed_check"] == [0, 1])


def test_the_record_stops_at_the_first_step_that_reaches_the_k2_bound(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Mutation caught: a rank at or above `upper` that no longer ends the run, or `current >= upper` weakened to
    `>`, which would leave the status at lower_bound_only."""
    Slice(monkeypatch, [_t(3)], [KERNEL])
    monkeypatch.setattr(J, "k2_hilbert_function", lambda _target: {"1": 2})
    record = _record(tmp_path / "bound.json", narcs=4)
    _check(record["status"] == "equal_to_k2_bound" and record["rank"] == 2 and record["hf_k2"] == 2)
    _check(len(record["checkpoints"]) == 1 and len(record["arcs"]) == 1)


def _run_check(path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> str:
    monkeypatch.setattr(sys, "argv", ["jet_rank.py", "--check", str(path)])
    J.main()
    return capsys.readouterr().out


@pytest.mark.parametrize(
    "alter",
    [
        lambda record: record.__setitem__("rank", record["rank"] + 1),
        lambda record: record.__setitem__("status", "equal_to_k2_bound"),
        lambda record: record["checkpoints"][-1].__setitem__("rank", 1),
        lambda record: record["arcs"][0].__setitem__("k2_nonzero", 1),
        lambda record: record["arcs"][1]["coefficients"]["w"].__setitem__(0, 7),
        lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64),
        lambda record: record.__setitem__("bound", "3 <= h_1 <= 21"),
    ],
    ids=["rank", "status", "checkpoint", "arc-check", "coefficient", "input-digest", "bound"],
)
def test_check_rejects_an_altered_record_and_ignores_the_timing(
    alter: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Mutation caught: strip_times dropping more than `elapsed_ms` (for example `rank` or `arcs`), or --check
    comparing a subset of the fields, or returning before the comparison."""
    Slice(monkeypatch, [_t(3)], [KERNEL])
    path = tmp_path / "record.json"
    record = _record(path)
    record["elapsed_ms"] += 12345
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    out = _run_check(path, monkeypatch, capsys)
    _check(json.loads(out) == {"check": "identical", "target": NAME, "degree": 1, "rank": 2})
    alter(record)
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="the recomputed record differs"):
        _run_check(path, monkeypatch, capsys)


@pytest.mark.parametrize("name", ["e8nm-p32009", "e8np-p32009"])
def test_the_first_real_arc_of_each_header_reproduces_its_retained_entry(name: str) -> None:
    """Mutation caught: a change of the coefficient rule, the family order or the Phi parametrization (an arc
    entry of the retained record differs), a sign of t9 that leaves V(J) of the header (j_nonzero), and a
    K2 relation file other than the target's own (k2_nonzero)."""
    retained = json.loads((JETS / "records" / f"{name}-d1.json").read_text(encoding="utf-8"))
    out = J.jet_rows((name, 0, 1, J.columns(J.TARGETS[name], 1)[0]))
    entry = retained["arcs"][0]
    _check({key: out[key] for key in entry} == entry)
    _check(entry["j_nonzero"] == 0 and entry["k2_nonzero"] == 0 and entry["e"] == 2)
    _check(len(out["rows"]) == 2 and len(out["rows"][0]) == 21 and any(out["rows"][1]))


def test_the_coefficient_rule_is_the_retained_sha256_enumeration() -> None:
    """Mutation caught: any change of the byte count, the field order or the zero replacement of `coefficients`."""
    _check(J.coefficients(0, 1, PRIME) == [30404, 2070, 1920, 2589])
    _check(J.coefficients(0, 5, PRIME) == [8683, 8451, 5597, 15363])
    _check(all(0 < c < PRIME for idx in range(5) for var in range(1, 6) for c in J.coefficients(idx, var, PRIME)))
