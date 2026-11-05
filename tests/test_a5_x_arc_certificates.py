"""Arc certificate of the opposite-sign X fibers: header parsing, the P^2 limit map on grid points, controls."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ARCS_X = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "arcs-x"
sys.path.insert(0, str(ARCS_X))

import xarc_certify as C  # noqa: E402
import xarc_common as K  # noqa: E402
import xarc_flip as F  # noqa: E402
import xarc_gen as G  # noqa: E402
import xarc_run as RUN  # noqa: E402
import xarc_series as SR  # noqa: E402

PRIMES = (32009, 32029)
SLUGS = ("xp-nm", "xm-np")
POINTS = [(1, 2, 1, 0), (3, 5, 6, 4), (7, 13, 1, 4)]
CASES = [(p, s) for p in PRIMES for s in SLUGS]


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _headers(prime: int) -> dict[str, K.Header]:
    return K.load_headers(prime)


def _symbolic(prime: int, slug: str) -> dict[int, list]:
    text = (K.prime_dir("logs", prime) / f"{slug}_limit.log").read_text()
    raw = C.parse_limit_text(text)
    return {j: [C.mod_poly(e, prime) for e in raw[j]] for j in raw}


@pytest.mark.parametrize("prime", PRIMES)
def test_headers_give_prime_and_root_of_minus_one(prime: int) -> None:
    for slug, header in _headers(prime).items():
        _check(header.prime == prime)
        _check((header.root**2 + 1) % prime == 0)
        _check(len(header.j) == 12 and len(header.g) == 3)
        _check(header.slug == slug)


def test_header_prime_or_root_mismatch_raises() -> None:
    header = _headers(32009)["xp-nm"]
    with pytest.raises(ValueError):
        K.read_header(header.path, "xp-nm", prime=32029)
    with pytest.raises(ValueError):
        K.read_header(header.path, "xp-nm", root=header.root + 1)


def test_header_directory_is_unique_per_prime() -> None:
    with pytest.raises(ValueError):
        K.find_header_dir(99991)


@pytest.mark.parametrize("prime", PRIMES)
def test_headers_match_the_emission_receipt(prime: int) -> None:
    directory = K.find_header_dir(prime)
    receipt = json.loads((directory / "receipt-x-opposite.json").read_text())
    _check(receipt["prime"] == prime)
    for row in receipt["incidences"]:
        digest = hashlib.sha256((directory / f"{row['slug']}.sing").read_bytes()).hexdigest()
        _check(digest == row["header_sha256"])


@pytest.mark.parametrize("prime", PRIMES)
def test_generated_scripts_equal_the_retained_scripts(prime: int) -> None:
    texts = G.scripts(_headers(prime))
    _check(len(texts) == 11)
    for name, text in texts.items():
        _check((K.prime_dir("sing", prime) / name).read_text() == text)


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_phi_lies_on_the_slice_at_parameter_points(prime: int, slug: str) -> None:
    sl = C.slice_of(_headers(prime)[slug])
    _check(sum(C.PhiResidue(sl)(pt) for pt in C.PHI_POINTS) == 0)


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_limit_map_certificate_on_grid_points(prime: int, slug: str) -> None:
    sl = C.slice_of(_headers(prime)[slug])
    check = C.PointCheck(sl, _symbolic(prime, slug))
    for pt in POINTS:
        res = check(pt)
        _check(res["reasons"] == [])
        _check(res["nu"] == 2)


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_limit_map_has_rank_three_and_the_p2_shape(prime: int, slug: str) -> None:
    sl = C.slice_of(_headers(prime)[slug])
    jac = C.JacobianRows(sl)
    for pt in C.RANK_POINTS[:2]:
        _check(C.rank_mod(jac(pt), prime) == 3)
    # F = (a1 W^2, a2 W (R+S), a3 W (R-S)): the target (1 : a : b) is hit by an arc whose limit has that shape.
    sym = _symbolic(prime, slug)
    a1 = int(sym[1][2].coeff_monomial(C.W_**2)) % prime
    a2 = int(sym[2][2].coeff_monomial(C.W_ * C.R_)) % prime
    a3 = int(sym[3][2].coeff_monomial(C.W_ * C.R_)) % prime
    for target in ((2, 3), (0, 9)):
        _check(C.HitCheck(sl, (a1, a2, a3))(target)["ok"])


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_dphi_has_rank_four(prime: int, slug: str) -> None:
    rank = C.DphiRank(prime, K.SIGN9[slug])
    _check(rank((0, 0, 0, 0)) == 4)
    _check(rank((3, 5, 7, 11)) == 4)


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_reversed_t9_term_leaves_the_slice(prime: int, slug: str) -> None:
    sl = C.slice_of(_headers(prime)[slug])
    res = C.PointCheck(C.with_flipped_t9(sl), _symbolic(prime, slug))(POINTS[1])
    _check("J(x(s)) != 0" in res["reasons"])


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_perturbed_generator_departs_from_the_symbolic_series(prime: int, slug: str) -> None:
    sl = C.slice_of(_headers(prime)[slug])
    res = C.PointCheck(C.with_perturbed_g2(sl), _symbolic(prime, slug))(POINTS[1])
    _check("series != symbolic" in res["reasons"])


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_duplicated_generator_collapses_the_rank(prime: int, slug: str) -> None:
    sl = C.with_duplicated_g(C.slice_of(_headers(prime)[slug]))
    _check(C.rank_mod(C.JacobianRows(sl)(C.RANK_POINTS[0]), prime) < 3)


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_opposite_sign_of_t9_leaves_the_slice(prime: int, slug: str) -> None:
    other = "xm-np" if slug == "xp-nm" else "xp-nm"
    header = _headers(prime)[slug]
    sl = C.Slice(prime, K.SIGN9[other], header.j, header.g)
    res = C.PointCheck(sl, _symbolic(prime, slug))(POINTS[1])
    _check("J(x(s)) != 0" in res["reasons"])


def test_corrupted_symbolic_log_fails_the_certificate() -> None:
    prime, slug = 32009, "xp-nm"
    text = (K.prime_dir("logs", prime) / f"{slug}_limit.log").read_text()
    marker = "  s^ 2 :"
    head, _, tail = text.partition(marker)
    corrupted = head + marker + " 1+" + tail.lstrip()
    raw = C.parse_limit_text(corrupted)
    symbolic = {j: [C.mod_poly(e, prime) for e in raw[j]] for j in raw}
    sl = C.slice_of(_headers(prime)[slug])
    _check("series != symbolic" in C.PointCheck(sl, symbolic)(POINTS[1])["reasons"])


def test_series_arithmetic_keeps_each_modulus() -> None:
    for prime in PRIMES:
        a = SR.Series([1, 2, 3], 4, prime)
        _check((a * a.inv()).coeff(0) == 1)
        _check(all((a * a.inv()).coeff(k) == 0 for k in (1, 2, 3)))
        _check(SR.Dual(5, 1, prime).inv().a == pow(5, -1, prime))


def test_sign_change_of_t9_relates_the_two_incidences() -> None:
    for prime in PRIMES:
        headers = _headers(prime)
        rows = F.matches(headers["xp-nm"], headers["xm-np"])
        t9_only = (0, 0, 0, 0, 0, 0, 1)
        _check(any(flips == t9_only and j_hits == 12 and len(g_hits) == 3 for flips, j_hits, g_hits in rows))


@pytest.mark.parametrize(("prime", "slug"), CASES)
def test_retained_records_certify_the_fiber(prime: int, slug: str) -> None:
    header = _headers(prime)[slug]
    res = json.loads((K.prime_dir("records", prime) / slug / "result.json").read_text())
    _check(res["certified_P2"] is True)
    _check(res["prime"] == prime and res["root_of_minus_one"] == header.root)
    _check(res["jacobian_rank"] == 3 and res["grid_failures"] == 0)
    _check(res["targets_hit"] == res["targets"] == 100)
    _check(res["input_sha256"] == hashlib.sha256(header.path.read_bytes()).hexdigest())
    _check(all(c["failed_as_intended"] for c in res["controls"].values()))
    _check(res["controls"]["rank_collapse"]["ranks"] == [2, 2, 2, 2, 2])
    _check(res["symbolic_J_of_Phi_vanishes"] is True)
    _check(res["limit_map"]["F1"].endswith(" W^2"))


@pytest.mark.parametrize("prime", PRIMES)
def test_retained_ideal_checks_show_a_smooth_curve_germ(prime: int) -> None:
    logs = K.prime_dir("logs", prime)
    for slug in SLUGS:
        quot = (logs / f"{slug}_quot.log").read_text()
        for n in range(1, 9):
            _check(f"n {n} colength of I' + m^n: {n}  (smooth curve germ: n)" in quot)
        explore = (logs / f"{slug}_explore.log").read_text()
        _check("dim V(J) 4 global degree 6" in explore)
        _check("rank of the Jacobian of J at the origin 3" in explore)
        _check("minimal primes of J 1" in explore)


def test_singular_error_lines_are_detected() -> None:
    _check(RUN.singular_errors("n 2 colength 5\n") == [])
    bad = "   ? `bogus` is undefined\n   ? error occurred in or before bad.sing line 2: `bogus`\n"
    _check(len(RUN.singular_errors(bad)) == 2)


@pytest.mark.skipif(shutil.which("Singular") is None, reason="Singular is not installed")
def test_failed_singular_script_raises(tmp_path: Path) -> None:
    good = tmp_path / "good.sing"
    good.write_text('ring r=7,(x),dp;\n"ok", 1+1;\nquit;\n')
    _check("ok" in RUN.run_singular(good, tmp_path, timeout=60))
    bad = tmp_path / "bad.sing"
    bad.write_text("ring r=7,(x),dp;\nbogus syntax here(;\nquit;\n")
    with pytest.raises(RuntimeError):
        RUN.run_singular(bad, tmp_path, timeout=60)
