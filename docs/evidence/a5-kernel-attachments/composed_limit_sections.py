"""Limit planes of a nullity-8 source at N+ or N- that lie in a limiting plane of a nullity-12 stratum.

Every row into N+ (and into N-) uses one basepoint z_0, one slice and one frame of the 9-dimensional ker C_(z_0),
so the fibers of all sources live in one space. A nullity-12 stratum M has the rank-two Schur form S with limiting
7-plane Q = ker S_0; a nullity-8 source has the rank-four form T with limiting 5-plane P = ker T_0, recorded by the
126 principal four-Pfaffians pi of T. A limit of 5-planes taken first at points w of M and then along w -> z_0
lies in the limit of ker C_w, so a composed limit through M is a plane P inside some Q. With S_0 = alpha ^ beta and
pi = alpha_1 ^ ... ^ alpha_4 the containment P inside Q reads (iota_v S_0) ^ pi = 0 for every v, which is linear
in the source fiber coordinates y for a fixed point m of the fiber of M. This producer evaluates that linear
section of each source fiber V_+(K2) at fixed points m, modulo 32009 and 32029, and compares the section through
a stratum with a one-point fiber into N (VB, V^a+, V^a-) with the fiber of the source over that stratum.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import nakayama_rees_fibers as nakayama  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-composed-limit-sections-v1"
FIBERS = ROOT / "docs" / "evidence" / "a5-exceptional-fibers"
HILBERT = FIBERS / "k2-hilbert.jsonl"
WITNESSES = FIBERS / "witnesses.jsonl"
NULLITY16_RESULT = HERE / "nullity16-rees-fibers-result.json"
NAKAYAMA_RESULT = HERE / "nakayama-rees-fibers-result.json"
IMPORT_RESULT = HERE / "nullity8-fiber-import-result.json"
CELLS = ((32009, 10754), (32029, 9115))
PRIMES = tuple(prime for prime, _ in CELLS)
KERNEL_DIMENSION = 9
PAIRS = tuple(itertools.combinations(range(KERNEL_DIMENSION), 2))
QUADS = tuple(itertools.combinations(range(KERNEL_DIMENSION), 4))
QUAD_INDEX: dict[tuple[int, ...], int] = {quad: index for index, quad in enumerate(QUADS)}
FIVES = tuple(itertools.combinations(range(KERNEL_DIMENSION), 5))
# Source incidence -> `fiber` label of k2-hilbert.jsonl; None marks the polynomial fiber cone (K2 = 0, A5-001).
SOURCES: dict[str, str | None] = {
    "X+->N-": None,
    "X-->N+": None,
    "X+->N+": "X+",
    "X-->N-": "X-",
    "Iso->N+": "Iso",
    "W8->N-": "W8 -> N-",
    "E8bar->N+": "E8-bar -> N+",
    "E8bar->N-": "E8-bar -> N-",
}
# k2-hilbert.jsonl `fiber` label -> incidence of the import record whose header the relation file is written against.
INCIDENCE_OF_LABEL = {label: row for row, label in SOURCES.items() if label is not None}
# The nullity-12 strata between each source and nullity 16 (incidence census).
MIDDLE = {
    "X+": ("B9", "VB", "Va+"),
    "X-": ("B9", "VB", "Va-"),
    "Iso": ("B9", "VB"),
    "W8": ("B9", "VB"),
    "E8bar": ("B9", "V", "VB", "Va+", "Va-"),
}
# Fixed points of the middle fiber: the plane P^2 of B9, the conic m2^2 = m1 m3 of V, the single point otherwise.
PLANE_POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 2, 3), (1, 5, 7), (2, 3, 11))
CONIC_POINTS = ((1, 0, 0), (0, 0, 1), (1, 1, 1), (1, 2, 4), (1, 3, 9), (4, 6, 9))
SINGLE_POINT = ((1,),)
# Reduced components (projective dimension, degree) of the source fiber over the middle stratum, from the
# nullity-12 records: nakayama-rees-fibers-result.json, and A5-005 with A5-015 and A5-016 for E8bar->VB.
E8BAR_VB_COMPONENTS = ((3, 3), (3, 4))
VA_FIBER = (2, 2, 2)  # two planes
# Sources whose K2 is retained at one prime only: the record carries their chains at that prime and leaves them out of
# the cross-prime comparison. X+ -> N+ has no K2 file at 32009 (the sign map carries X- -> N- there, A5-304).
SINGLE_PRIME_SOURCES = {"X+->N+": 32029}
# Independent linear conditions that the containment equations impose on the source fiber coordinates at the single
# fiber point of a one-point middle stratum, by (source incidence, middle stratum). The counts are the retained values
# of both primes (X+->N+ at 32029 only), a regression guard on the equation system and not a derived quantity.
LINEAR_CONDITIONS = {
    ("X+->N-", "VB"): 0,
    ("X-->N+", "VB"): 0,
    ("X+->N+", "VB"): 9,
    ("X-->N-", "VB"): 9,
    ("Iso->N+", "VB"): 9,
    ("W8->N-", "VB"): 13,
    ("E8bar->N+", "VB"): 11,
    ("E8bar->N-", "VB"): 11,
    ("X+->N+", "Va+"): 9,
    ("X-->N-", "Va-"): 9,
    ("E8bar->N+", "Va+"): 15,
    ("E8bar->N-", "Va-"): 15,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduce_gaussian(pair: list[str], prime: int, root: int) -> int:
    """a + b i in Q(i) reduced modulo the prime with i sent to the root."""
    real, imaginary = (Fraction(value) for value in pair)
    values = [value.numerator * pow(value.denominator, -1, prime) for value in (real, imaginary)]
    return (values[0] + root * values[1]) % prime


def wedge_residual(form: list[list[int]], pfaffians: list[int]) -> int:
    """Number of nonzero coefficients of (iota_k S) ^ pi over all k: zero exactly when ker T lies in ker S."""
    count = 0
    for k in range(KERNEL_DIMENSION):
        for five in FIVES:
            value = 0
            for position, j in enumerate(five):
                if j != k:
                    rest = tuple(index for index in five if index != j)
                    value += (-1 if position % 2 else 1) * form[k][j] * pfaffians[QUAD_INDEX[rest]]
            count += value != 0
    return count


def convention_control(base: int = 2, modulus: int = 11) -> dict[str, Any]:
    """Exact integer forms with known containment: the equations vanish on the contained plane only.

    The six covectors are (i + base)^j mod modulus, centered; the defaults give the retained control.
    """
    covectors = [[(i + base) ** j % modulus - modulus // 2 for j in range(KERNEL_DIMENSION)] for i in range(6)]

    def wedge(a: list[int], b: list[int]) -> list[list[int]]:
        return [[a[i] * b[j] - a[j] * b[i] for j in range(KERNEL_DIMENSION)] for i in range(KERNEL_DIMENSION)]

    first, second = wedge(covectors[0], covectors[1]), wedge(covectors[2], covectors[3])
    rank_four = [[first[i][j] + second[i][j] for j in range(KERNEL_DIMENSION)] for i in range(KERNEL_DIMENSION)]
    pfaffians = [
        rank_four[a][b] * rank_four[c][d] - rank_four[a][c] * rank_four[b][d] + rank_four[a][d] * rank_four[b][c]
        for a, b, c, d in QUADS
    ]
    inside = wedge(
        [covectors[0][j] + 2 * covectors[2][j] for j in range(KERNEL_DIMENSION)],
        [covectors[1][j] - 3 * covectors[3][j] + covectors[0][j] for j in range(KERNEL_DIMENSION)],
    )
    record = {
        "contained_plane_nonzero_coefficients": wedge_residual(inside, pfaffians),
        "plane_sharing_one_covector_nonzero_coefficients": wedge_residual(wedge(covectors[0], covectors[4]), pfaffians),
        "transverse_plane_nonzero_coefficients": wedge_residual(wedge(covectors[4], covectors[5]), pfaffians),
    }
    record["detected"] = (
        record["contained_plane_nonzero_coefficients"] == 0
        and record["plane_sharing_one_covector_nonzero_coefficients"] > 0
        and record["transverse_plane_nonzero_coefficients"] > 0
    )
    return record


def _linear(row: list[int], names: tuple[str, ...]) -> str:
    terms = [f"{coefficient}*{name}" for coefficient, name in zip(row, names, strict=True) if coefficient]
    return "(" + "+".join(terms) + ")" if terms else ""


def flag_equations(form_entries: list[int], embedding: list[list[int]], names: tuple[str, ...]) -> list[str]:
    """The coefficients of (iota_k S_0) ^ pi(y) for a fixed form S_0 (36 upper-triangle entries), linear in y."""
    form = [[0] * KERNEL_DIMENSION for _ in range(KERNEL_DIMENSION)]
    for value, (a, b) in zip(form_entries, PAIRS, strict=True):
        form[a][b], form[b][a] = value, -value
    pfaffians = [_linear(row, names) for row in embedding]
    equations = []
    for k in range(KERNEL_DIMENSION):
        for five in FIVES:
            terms = []
            for position, j in enumerate(five):
                rest = tuple(index for index in five if index != j)
                if j != k and form[k][j] and pfaffians[QUAD_INDEX[rest]]:
                    sign = -form[k][j] if position % 2 else form[k][j]
                    terms.append(f"({sign})*{pfaffians[QUAD_INDEX[rest]]}")
            if terms:
                equations.append("+".join(terms))
    return equations


def section_script(prime: int, names: tuple[str, ...], quadrics: str, equations: list[str]) -> str:
    return "\n".join(
        (
            'LIB "primdec.lib";',
            f"ring r={prime},({','.join(names)}),dp;",
            "option(redSB);",
            f"ideal K={quadrics};",
            f"ideal E={','.join(equations) if equations else '0'};",
            'ideal Lin=interred(E); "RESULT linear_conditions",size(Lin);',
            "ideal L=std(sat(std(K+E),maxideal(1)));",
            '"RESULT section_dimension",dim(L)-1;',
            '"RESULT section_degree",mult(L);',
            '"RESULT reduced_degree",mult(std(radical(L)));',
            'list PD=minAssGTZ(L); "RESULT component_count",size(PD);',
            'for(int q=1;q<=size(PD);q++){"RESULT component_"+string(q)+"_dimension",dim(std(PD[q]))-1;'
            '"RESULT component_"+string(q)+"_degree",mult(std(PD[q]));}',
            "quit;",
        )
    )


def section_task(item: tuple[int, tuple[str, ...], str, list[str]]) -> dict[str, Any]:
    prime, names, quadrics, equations = item
    result = nakayama._run_singular(section_script(prime, names, quadrics, equations))
    count = int(result["component_count"])
    return {
        "linear_conditions": int(result["linear_conditions"]),
        "section_projective_dimension": int(result["section_dimension"]),
        "section_degree": int(result["section_degree"]),
        "reduced_degree": int(result["reduced_degree"]),
        "components_projective_dimension_degree": sorted(
            [int(result[f"component_{q}_dimension"]), int(result[f"component_{q}_degree"])] for q in range(1, count + 1)
        ),
    }


def expected_through(source_row: str, middle: str, nakayama_rows: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Reduced components, degree and linear conditions the section must show where the middle stratum has one point."""
    source = source_row.split("->")[0]
    conditions = LINEAR_CONDITIONS[(source_row, middle)] if (source_row, middle) in LINEAR_CONDITIONS else None
    if middle == "VB":
        if source == "E8bar":
            return {
                "reduced_components": [list(pair) for pair in E8BAR_VB_COMPONENTS],
                "section_degree": None,
                "linear_conditions": conditions,
            }
        fiber = nakayama_rows[f"{source}->VB"]["rational"]
        _require(int(fiber["component_count"]) == 1, f"{source}->VB fiber is reducible")
        return {
            "reduced_components": [[int(fiber["image_projective_dimension"]), int(fiber["image_degree"])]],
            "section_degree": None,
            "linear_conditions": conditions,
        }
    if middle.startswith("Va"):
        # The two planes of the fiber over V^a+ or V^a- have one limit plane, which carries their degree 2.
        return {
            "reduced_components": [[VA_FIBER[0], 1]],
            "section_degree": VA_FIBER[1],
            "linear_conditions": conditions,
        }
    return None


def section_passes(section: dict[str, Any], expected: dict[str, Any]) -> bool:
    """A section through a one-point stratum: reduced components, degrees and the number of linear conditions."""
    components = section["components_projective_dimension_degree"]
    top = max((dimension for dimension, _ in components), default=-1)
    return (
        components == sorted(expected["reduced_components"])
        and section["reduced_degree"] == sum(degree for dimension, degree in components if dimension == top)
        and (expected["section_degree"] is None or section["section_degree"] == expected["section_degree"])
        and (expected["linear_conditions"] is None or section["linear_conditions"] == expected["linear_conditions"])
    )


def chain_passes(chain: dict[str, Any]) -> bool:
    expected = chain["expected_through_one_point_stratum"]
    sections = [point["section"] for point in chain["points"]]
    if expected is None:
        return all(section["section_projective_dimension"] >= 0 for section in sections)
    return all(section_passes(section, expected) for section in sections)


def compare_primes(chains: list[dict[str, Any]]) -> dict[str, Any]:
    """Cross-prime agreement of the sections of every (source, stratum) pair that both primes carry.

    A pair present at one prime only has no second value to agree with: it is listed with its prime and left out of
    the agreement. The comparison holds only when the one-prime pairs are exactly those of SINGLE_PRIME_SOURCES and at
    least one pair is present at both primes.
    """
    sections: dict[tuple[str, str], dict[int, list[dict[str, Any]]]] = {}
    for chain in chains:
        by_prime = sections.setdefault((chain["source"], chain["through"]), {})
        by_prime.setdefault(int(chain["prime"]), []).extend(point["section"] for point in chain["points"])
    both = sorted(key for key, by_prime in sections.items() if set(by_prime) == set(PRIMES))
    single = sorted(
        (source, through, next(iter(by_prime)))
        for (source, through), by_prime in sections.items()
        if len(by_prime) == 1
    )
    equal = all(sections[key][PRIMES[0]] == sections[key][PRIMES[1]] for key in both)
    declared = sorted((source, through, SINGLE_PRIME_SOURCES.get(source, 0)) for source, through, _ in single)
    return {
        "pairs_at_both_primes": [list(key) for key in both],
        "pairs_at_one_prime_only": [[source, through, prime] for source, through, prime in single],
        "agree": bool(both)
        and equal
        and all(source in SINGLE_PRIME_SOURCES for source, _, _ in single)
        and single == declared,
    }


def _relations(
    label: str | None, prime: int, hilbert: list[dict[str, Any]]
) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    if label is None:
        return "0", None, None
    row = next((row for row in hilbert if row["fiber"] == label and int(row["prime"]) == prime), None)
    if row is None:
        return "", None, None
    path = FIBERS / "working" / str(row["relations"])
    _require(_sha256(path) == row["relations_sha256"], f"{path} differs from the k2-hilbert row")
    text = re.sub(r"y\((\d+)\)", r"y\1", path.read_text(encoding="utf-8"))
    return (
        text.strip().rstrip(",").replace("\n", ""),
        {"relations": f"working/{row['relations']}", "relations_sha256": row["relations_sha256"]},
        row,
    )


def header_generators(text: str) -> list[str]:
    """The G list of a Singular header, in the order the header states it."""
    match = re.search(r"idealG=([^;]*);", "".join(text.split()))
    if match is None:
        raise RuntimeError("the header holds no ideal G")
    return match.group(1).split(",")


def receipt_violation(
    receipt: dict[str, Any],
    *,
    header: dict[str, Any],
    gens: dict[str, Any],
    relations_sha256: str,
    prime: int,
    root: int,
    quadrics: int,
) -> str | None:
    """The first condition by which a degree-2 receipt fails to certify the K2 of a canonical header, else None.

    The receipt binds the header it ran on (`input_sha256`), the G order of that run (`generator_order_sha256`, the
    digest of the `gens.txt` the Singular stage wrote) and the relation file it certified. The G list of `gens.txt`
    must equal the header's G list element by element, so a K2 file certified on this receipt is written in the
    header's generator order.
    """
    checks = (
        ("schema", receipt.get("schema") == "a5-fiber-cone-degree-receipt-v1"),
        ("status", receipt.get("status") == "degree-certified" and receipt.get("degree") == 2),
        ("prime", receipt.get("prime") == prime and str(receipt.get("root_of_minus_one")) == str(root)),
        ("input", Path(str(receipt.get("input"))).name == header["name"]),
        ("input digest", receipt.get("input_sha256") == header["sha256"]),
        ("generator count", receipt.get("generator_count") == len(header["generators"])),
        ("generator order digest", receipt.get("generator_order_sha256") == gens["sha256"]),
        ("generator order", gens["generators"] == header["generators"]),
        ("relation digest", receipt.get("relation_sha256") == relations_sha256),
        ("relation count", receipt.get("relation_count") == quadrics),
        ("membership", receipt.get("membership_check") == {"checked": quadrics, "failures": 0}),
    )
    return next((name for name, holds in checks if not holds), None)


def _file_record(path: Path, touched: set[Path]) -> dict[str, str]:
    touched.add(path)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def bind_relations(
    label: str,
    prime: int,
    root: int,
    relations: dict[str, Any],
    *,
    cells: dict[tuple[str, int, int], dict[str, Any]],
    witnesses: list[dict[str, Any]],
    touched: set[Path],
) -> dict[str, Any]:
    """Bind the K2 relation file of one source at one prime to the canonical header it is written against.

    The K2 digest of k2-hilbert.jsonl must be certified by a witness of witnesses.jsonl: either a `k2-span` whose
    receipt passes `receipt_violation` against the regenerated header of the source, or a `sign-isomorphism` whose
    transported file carries such a certificate at the paired incidence. A K2 file without either chain is rejected,
    so a relation file of another incidence or of another generator order cannot enter a section.
    """
    incidence = INCIDENCE_OF_LABEL[label]
    cell = cells[(incidence, prime, root)]
    header = ROOT / str(cell["header"])
    header_sha = _sha256(header)
    _require(cell["identical"] is True, f"{incidence} header at {prime} is not the regenerated header")
    _require(header_sha == cell["header_sha256"] == cell["regenerated_sha256"], f"{header} changed since the import")
    header_record = {
        "name": header.name,
        "sha256": header_sha,
        "generators": header_generators(header.read_text(encoding="utf-8")),
    }
    _require(len(header_record["generators"]) == int(relations["generators"]), f"{incidence} generator count changed")
    relations_sha = str(relations["relations_sha256"])
    quadrics = int(relations["quadrics"])
    binding: dict[str, Any] = {
        "incidence": incidence,
        "prime": prime,
        "i_root": root,
        "header": _file_record(header, touched),
        "generator_count": len(header_record["generators"]),
        "k2_relations": f"working/{relations['relations']}",
        "k2_relations_sha256": relations_sha,
        "quadrics": quadrics,
    }
    for witness in witnesses:
        if witness["kind"] != "k2-span" or witness["k2_source_sha256"] != relations_sha:
            continue
        if witness["ok"] is not True or witness["mutual_remainders"] != [0, 0]:
            continue
        receipt_path = FIBERS / str(witness["receipt"])
        relation_path = FIBERS / str(witness["receipt_relations"])
        gens_path = receipt_path.parent / "gens.txt"
        if not (receipt_path.exists() and relation_path.exists() and gens_path.exists()):
            continue  # the receipt is not retained in the tree
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        gens = {
            "sha256": _sha256(gens_path),
            "generators": "".join(gens_path.read_text(encoding="utf-8").split()).rstrip(";").split(","),
        }
        if (
            _sha256(relation_path) != witness["receipt_relations_sha256"]
            or receipt_violation(
                receipt,
                header=header_record,
                gens=gens,
                relations_sha256=_sha256(relation_path),
                prime=prime,
                root=root,
                quadrics=quadrics,
            )
            is not None
        ):
            continue
        return {
            **binding,
            "route": "k2_span_witness",
            "k2_span_mutual_remainders": witness["mutual_remainders"],
            "receipt": _file_record(receipt_path, touched),
            "receipt_input_sha256": receipt["input_sha256"],
            "receipt_generator_order_sha256": receipt["generator_order_sha256"],
            "generator_order_file": _file_record(gens_path, touched),
            "receipt_relations": _file_record(relation_path, touched),
        }
    for witness in witnesses:
        if (
            witness["kind"] == "sign-isomorphism"
            and witness["prime"] == prime
            and witness["to"] == label
            and witness["k2_to_sha256"] == relations_sha
            and witness["ok"] is True
            and witness["k2_mutual_remainders"] == [0, 0]
            and witness["from"] in INCIDENCE_OF_LABEL
        ):
            source_label = str(witness["from"])
            source_relations = {
                **relations,
                "relations": str(witness["k2_from"]).removeprefix("working/"),
                "relations_sha256": witness["k2_from_sha256"],
            }
            _require(_sha256(FIBERS / str(witness["k2_from"])) == witness["k2_from_sha256"], "k2_from changed")
            return {
                **binding,
                "route": "sign_isomorphism_witness",
                "sign_isomorphism_from": source_label,
                "flip": witness["flip"],
                "generator_signs": witness["G_signs"],
                "k2_mutual_remainders_after_the_y_signs": witness["k2_mutual_remainders"],
                "from_binding": bind_relations(
                    source_label,
                    prime,
                    root,
                    source_relations,
                    cells=cells,
                    witnesses=witnesses,
                    touched=touched,
                ),
            }
    raise RuntimeError(f"no certified generator order binds the K2 of {incidence} at {prime} to its header")


def import_cells() -> dict[tuple[str, int, int], dict[str, Any]]:
    """The regenerated headers of the fiber import record, by (incidence, prime, root of -1)."""
    record = nakayama._load_json(IMPORT_RESULT)
    _require(record.get("pass") is True, "the fiber import record does not pass")
    return {
        (str(row["incidence"]), int(cell["prime"]), int(cell["i_root"])): cell
        for row in record["incidences"]
        for cell in row["cells"]
    }


def build_record() -> dict[str, Any]:
    record16 = {str(row["incidence"]): row for row in nakayama._load_json(NULLITY16_RESULT)["incidences"]}
    nakayama_rows = {str(row["incidence"]): row for row in nakayama._load_json(NAKAYAMA_RESULT)["incidences"]}
    hilbert = [json.loads(line) for line in HILBERT.read_text(encoding="utf-8").splitlines() if line.strip()]
    witnesses = [json.loads(line) for line in WITNESSES.read_text(encoding="utf-8").splitlines() if line.strip()]
    cells = import_cells()
    touched: set[Path] = set()
    bindings: list[dict[str, Any]] = []
    chains: list[dict[str, Any]] = []
    items: list[tuple[int, tuple[str, ...], str, list[str]]] = []
    for prime, root in CELLS:
        for source_row, label in SOURCES.items():
            source, target = source_row.split("->")
            quadrics, provenance, relations = _relations(label, prime, hilbert)
            if not quadrics:
                # The only source without a retained K2 at one prime is the declared single-prime source.
                _require(
                    SINGLE_PRIME_SOURCES.get(source_row, prime) != prime,
                    f"{source_row}: no retained K2 at {prime}, and the source is not a declared single-prime source",
                )
                continue
            if label is not None and relations is not None:
                bindings.append(
                    {
                        "source": source_row,
                        **bind_relations(
                            label, prime, root, relations, cells=cells, witnesses=witnesses, touched=touched
                        ),
                    }
                )
            embedding = [
                [reduce_gaussian(cell, prime, root) for cell in row]
                for row in record16[source_row]["embedding_matrix_rows"]
            ]
            names = tuple(f"y{index + 1}" for index in range(len(embedding[0])))
            for middle in MIDDLE[source]:
                middle_row = record16.get(f"{middle}->{target}")
                if middle_row is None or middle_row["status"] != "completed":
                    continue
                middle_embedding = [
                    [reduce_gaussian(cell, prime, root) for cell in row] for row in middle_row["embedding_matrix_rows"]
                ]
                samples = {"B9": PLANE_POINTS, "V": CONIC_POINTS}.get(middle, SINGLE_POINT)
                _require(len(middle_embedding[0]) == len(samples[0]), f"{middle}->{target} generator count changed")
                points = []
                for sample in samples:
                    form = [sum(c * v for c, v in zip(row, sample, strict=True)) % prime for row in middle_embedding]
                    items.append((prime, names, quadrics, flag_equations(form, embedding, names)))
                    points.append({"middle_fiber_point": list(sample)})
                chains.append(
                    {
                        "prime": prime,
                        "i_root": root,
                        "source": source_row,
                        "through": f"{middle}->{target}",
                        "source_generators": len(names),
                        "source_quadrics": provenance,
                        "expected_through_one_point_stratum": expected_through(source_row, middle, nakayama_rows),
                        "points": points,
                    }
                )
    sections = iter(parallel.ordered_map(section_task, items, min_items=1))
    for chain in chains:
        for point in chain["points"]:
            point["section"] = next(sections)
        chain["pass"] = chain_passes(chain)
    prime_check = compare_primes(chains)
    single_prime = {(source, through) for source, through, _ in prime_check["pairs_at_one_prime_only"]}
    for chain in chains:
        chain["prime_coverage"] = (
            "single_prime_excluded_from_agreement"
            if (chain["source"], chain["through"]) in single_prime
            else "both_primes"
        )
    primes_agree = bool(prime_check["agree"])
    control = convention_control()
    inputs = (
        Path(__file__),
        Path(nakayama.__file__),
        NULLITY16_RESULT,
        NAKAYAMA_RESULT,
        IMPORT_RESULT,
        HILBERT,
        WITNESSES,
        *sorted(touched),
    )
    return {
        "schema": SCHEMA,
        "inputs": {path.resolve().relative_to(ROOT).as_posix(): _sha256(path) for path in inputs},
        "scope": {
            "statement": (
                "For a fixed point m of the fiber of a nullity-12 stratum at the shared N+ or N- basepoint, the "
                "limit planes of a nullity-8 source contained in the limiting 7-plane of m form the linear "
                "section of the source fiber V_+(K2) recorded here; a composed limit through that stratum lies "
                "in such a section."
            ),
            "claim_boundary": (
                "Exact modulo 32009 and 32029 at the listed points m. Sections agree between the primes for the "
                "source and stratum pairs that both primes carry; the chains of X+->N+ exist at 32029 only (no K2 "
                "file at 32009) and are marked single-prime and excluded from that agreement. The section is a "
                "necessary condition on a composed limit: the record does not compute which planes of a section "
                "are limits of the fibers over the middle stratum, and it samples the plane of B9 and the conic "
                "of V at six points each. The K2 relation file of each source and prime is bound to its canonical "
                "header by a retained receipt or sign-isomorphism witness (k2_bindings)."
            ),
        },
        "k2_bindings": sorted(bindings, key=lambda entry: (entry["source"], entry["prime"])),
        "chains": chains,
        "summary": {
            "chain_count": len(chains),
            "section_count": len(items),
            "chains_through_a_one_point_stratum": sum(
                chain["expected_through_one_point_stratum"] is not None for chain in chains
            ),
            "sections_agree_between_the_primes": primes_agree,
            "pairs_compared_at_both_primes": len(prime_check["pairs_at_both_primes"]),
            "pairs_at_one_prime_only": prime_check["pairs_at_one_prime_only"],
            "k2_bindings": len(bindings),
        },
        "mutation_control": {"name": "containment_equations_on_exact_forms", **control},
        "falsifier": (
            "A section through VB whose reduced components differ from the fiber of the source over VB, or whose "
            "reduced degree or linear-condition count differs from the retained value; a section through V^a+ or "
            "V^a- other than one plane of section degree 2; a section that differs between the two primes at a pair "
            "both primes carry; a single-prime chain outside the declared sources; a K2 relation file without a "
            "certified generator order in its header; or containment equations that vanish on a plane outside the "
            "7-plane."
        ),
        "pass": all(bool(chain["pass"]) for chain in chains) and primes_agree and bool(control["detected"]),
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _verdict(record: dict[str, Any]) -> bool:
    """The pass flag recomputed from the chains, the prime comparison and the control of the record."""
    chains = record["chains"]
    return (
        all(bool(chain["pass"]) == chain_passes(chain) and chain_passes(chain) for chain in chains)
        and bool(compare_primes(chains)["agree"])
        and bool(record["summary"]["sections_agree_between_the_primes"])
        and bool(record["mutation_control"]["detected"])
    )


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the composed-limit section record failed")
    _require(bool(record["mutation_control"]["detected"]), "the containment equations accepted a plane outside")
    _require(_verdict(record), "the composed-limit section record disagrees with its own chains")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        _require(arguments.check.read_bytes() == rendered, f"{arguments.check} differs from the regenerated record")


if __name__ == "__main__":
    main()
