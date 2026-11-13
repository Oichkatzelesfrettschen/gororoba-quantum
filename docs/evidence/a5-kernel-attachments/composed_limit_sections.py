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
NULLITY16_RESULT = HERE / "nullity16-rees-fibers-result.json"
NAKAYAMA_RESULT = HERE / "nakayama-rees-fibers-result.json"
CELLS = ((32009, 10754), (32029, 9115))
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


def convention_control() -> dict[str, Any]:
    """Exact integer forms with known containment: the equations vanish on the contained plane only."""
    covectors = [[(i + 2) ** j % 11 - 5 for j in range(KERNEL_DIMENSION)] for i in range(6)]

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


def expected_through(source: str, middle: str, nakayama_rows: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Reduced components and degree the section must show where the middle stratum has a one-point fiber into N."""
    if middle == "VB":
        if source == "E8bar":
            return {"reduced_components": [list(pair) for pair in E8BAR_VB_COMPONENTS], "section_degree": None}
        fiber = nakayama_rows[f"{source}->VB"]["rational"]
        _require(int(fiber["component_count"]) == 1, f"{source}->VB fiber is reducible")
        return {
            "reduced_components": [[int(fiber["image_projective_dimension"]), int(fiber["image_degree"])]],
            "section_degree": None,
        }
    if middle.startswith("Va"):
        # The two planes of the fiber over V^a+ or V^a- have one limit plane, which carries their degree 2.
        return {"reduced_components": [[VA_FIBER[0], 1]], "section_degree": VA_FIBER[1]}
    return None


def chain_passes(chain: dict[str, Any]) -> bool:
    expected = chain["expected_through_one_point_stratum"]
    sections = [point["section"] for point in chain["points"]]
    if expected is None:
        return all(section["section_projective_dimension"] >= 0 for section in sections)
    return all(
        section["components_projective_dimension_degree"] == sorted(expected["reduced_components"])
        and (expected["section_degree"] is None or section["section_degree"] == expected["section_degree"])
        for section in sections
    )


def _relations(label: str | None, prime: int, hilbert: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    if label is None:
        return "0", None
    row = next((row for row in hilbert if row["fiber"] == label and int(row["prime"]) == prime), None)
    if row is None:
        return "", None
    path = FIBERS / "working" / str(row["relations"])
    _require(_sha256(path) == row["relations_sha256"], f"{path} differs from the k2-hilbert row")
    text = re.sub(r"y\((\d+)\)", r"y\1", path.read_text(encoding="utf-8"))
    return text.strip().rstrip(",").replace("\n", ""), {
        "relations": f"working/{row['relations']}",
        "relations_sha256": row["relations_sha256"],
    }


def build_record() -> dict[str, Any]:
    record16 = {str(row["incidence"]): row for row in nakayama._load_json(NULLITY16_RESULT)["incidences"]}
    nakayama_rows = {str(row["incidence"]): row for row in nakayama._load_json(NAKAYAMA_RESULT)["incidences"]}
    hilbert = [json.loads(line) for line in HILBERT.read_text(encoding="utf-8").splitlines() if line.strip()]
    chains: list[dict[str, Any]] = []
    items: list[tuple[int, tuple[str, ...], str, list[str]]] = []
    for prime, root in CELLS:
        for source_row, label in SOURCES.items():
            source, target = source_row.split("->")
            quadrics, provenance = _relations(label, prime, hilbert)
            if not quadrics:
                continue  # no retained K2 of this source at this prime
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
                        "expected_through_one_point_stratum": expected_through(source, middle, nakayama_rows),
                        "points": points,
                    }
                )
    sections = iter(parallel.ordered_map(section_task, items, min_items=1))
    for chain in chains:
        for point in chain["points"]:
            point["section"] = next(sections)
        chain["pass"] = chain_passes(chain)
    by_chain: dict[tuple[str, str], list[list[dict[str, Any]]]] = {}
    for chain in chains:
        by_chain.setdefault((chain["source"], chain["through"]), []).append(
            [point["section"] for point in chain["points"]]
        )
    primes_agree = all(all(entry == entries[0] for entry in entries) for entries in by_chain.values())
    control = convention_control()
    inputs = (Path(__file__), Path(nakayama.__file__), NULLITY16_RESULT, NAKAYAMA_RESULT, HILBERT)
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
                "Exact modulo 32009 and 32029 at the listed points m. The section is a necessary condition on a "
                "composed limit: the record does not compute which planes of a section are limits of the "
                "fibers over the middle stratum, and it samples the plane of B9 and the conic of V at six "
                "points each."
            ),
        },
        "chains": chains,
        "summary": {
            "chain_count": len(chains),
            "section_count": len(items),
            "chains_through_a_one_point_stratum": sum(
                chain["expected_through_one_point_stratum"] is not None for chain in chains
            ),
            "sections_agree_between_the_primes": primes_agree,
        },
        "mutation_control": {"name": "containment_equations_on_exact_forms", **control},
        "falsifier": (
            "A section through VB whose reduced components differ from the fiber of the source over VB; a "
            "section through V^a+ or V^a- other than one plane of section degree 2; a section that differs "
            "between the two primes; or containment equations that vanish on a plane outside the 7-plane."
        ),
        "pass": all(bool(chain["pass"]) for chain in chains) and primes_agree and bool(control["detected"]),
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the composed-limit section record failed")
    _require(bool(record["mutation_control"]["detected"]), "the containment equations accepted a plane outside")


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
