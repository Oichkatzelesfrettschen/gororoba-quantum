"""Sheets, special fibers and exact arcs for the E8bar->Va+ and E8bar->Va- slice germs.

The reduced slice germ ideal J of each incidence (Nakayama-reduced, from nakayama_rees_fibers.py) has two prime
components over Q(i), the sheets, each a 4-dimensional complete intersection with a linear part and one quadric. The
Rees ideal of the six Nakayama generators G restricted to one sheet has a special fiber over the slice origin that is
a plane of the projective fiber (three coordinate hyperplanes y_i = 0), computed over Q(i) and modulo 32003 with
global monomial orderings; the sheet-to-plane correspondence matches each plane with a component of the retained
fiber of nakayama-rees-fibers-result.json. The retained arcs reach exactly one component, so the sheet whose plane is
the other component carries the arcs that no retained arc represents. That sheet holds the conic
t_2^2 + t_8^2 + 2 t_2 = 0, whose only line through the origin direction is t_2 = t_8 = 0. Two arcs are recorded on it.
The conic arc t_2 = -2 u^2 / (1 + u^2), t_8 = -2 u / (1 + u^2), t_k = c_k u otherwise, lies in the open E8-bar orbit:
the E8-bar closure generators vanish on it and each closure strictly inside the E8-bar closure (EXPECTED_LOWER of
strata_regularity.py) has a generator that does not. The line arc t = c u inside t_2 = t_8 = 0 lies in the closure of
X+ (at Va+) or X- (at Va-), a lower stratum of nullity 8. Each arc lies in J and in the sheet identically in u, has
rank C_z = 8 at the origin and 10 along the arc, and its 21 Schur coordinates vanish to first order with leading
vector equal to the embedded plane point of the preimage (g_1, ..., g_6) of the Rees map. The algebra of the claim
is exact: Singular substitutes the arc in Q(i)[u, d], clears d = 1 / (1 + u^2) by the unit (1 + u^2)^M, which leaves
the lowest-order coefficient vector in u unchanged, and checks vanishing in Q(i)[u]; the ranks are exact
Gaussian-rational ranks of the original-coordinate matrix C_z of holomorphic_kernel_lemma.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import nakayama_rees_fibers as nakayama  # noqa: E402

import parallel  # noqa: E402

resolved = nakayama.resolved
kernel_lemma = resolved.kernel_lemma
regularity = nakayama.regularity

SCHEMA = "a5-kernel-attachments-sheet-fiber-planes-v1"
NAKAYAMA_RESULT = nakayama.RESULT_PATH
SOURCE_PATHS = (
    HERE / "sheet_fiber_planes.py",
    HERE / "nakayama_rees_fibers.py",
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "holomorphic_kernel_lemma.py",
    nakayama.REGULARITY / "strata_regularity.py",
    nakayama.FIRST_ORDER_RESULT,
    NAKAYAMA_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
INCIDENCES = ("E8bar->Va+", "E8bar->Va-")
MODULAR_PRIME = nakayama.MODULAR_PRIME
SLICE_VARIABLE_COUNT = 8
SCHUR_COORDINATE_COUNT = 21
NAKAYAMA_GENERATOR_COUNT = 6
SHEET_COUNT = 2
# Arcs on the sheet whose special fiber is the plane that no retained arc reaches. The sheet of E8bar->Va+ is
# t_6 = t_7, t_4 = -t_5, t_1 = t_3, t_2^2 + t_8^2 + 2 t_2 = 0; the sheet of E8bar->Va- has t_1 = -t_3 instead. The
# coefficients give t_k(u) = c_k u for k outside {2, 8}. The line arc keeps t_2 = t_8 = 0; the conic arc sets
# t_2 = -2 u^2 d and t_8 = -2 u d with d (1 + u^2) = 1, the rational parametrization of the conic through the origin.
ARCS: dict[str, tuple[int, ...]] = {
    "E8bar->Va+": (1, 0, 1, -2, 2, 3, 3, 0),
    "E8bar->Va-": (1, 0, -1, -2, 2, 3, 3, 0),
}
CONIC_POSITIONS = {1: "-2*u^2*d", 7: "-2*u*d"}
LINE_ARC_STRATUM = {"E8bar->Va+": "Xp", "E8bar->Va-": "Xm"}
SOURCE_KEY = "Ehat"
MUTATED_COEFFICIENT_INDEX = 4
RANK_PARAMETERS = (0, 1, 2, 3)
RANK_AT_ORIGIN = 8
RANK_ALONG_ARC = 10
CHARACTERISTICS = (0, MODULAR_PRIME)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _slice_names() -> list[str]:
    return [f"t{index}" for index in range(1, SLICE_VARIABLE_COUNT + 1)]


def _decomposition_script(characteristic: int, phase_one: dict[str, Any], known_sheets: list[list[str]]) -> str:
    """Prime components of J, whether their intersection is J, and which of the known sheets each one equals."""
    lines = [
        'LIB "primdec.lib";',
        f"ring r={nakayama._field(characteristic)},({','.join(_slice_names())}),dp;",
        "minpoly=I2+1;",
        f"ideal J={','.join(phase_one['reduced_j'])};",
        '"RESULT version",system("version");',
        '"RESULT germ_dimension",dim(std(J));',
        "ideal SJ=std(J); list P=minAssGTZ(J); ideal Meet=P[1];",
        "for(int i=2;i<=size(P);i++){Meet=intersect(Meet,P[i]);}",
        "Meet=std(Meet);",
        '"RESULT sheet_count",size(P);',
        '"RESULT sheets_intersect_to_germ",(size(reduce(Meet,SJ))==0)&&(size(reduce(SJ,Meet))==0);',
        "ideal Q; ideal Gn; int j;",
        "for(i=1;i<=size(P);i++){Q=std(P[i]);Gn=simplify(Q,2);"
        '"RESULT sheet_"+string(i)+"_dimension",dim(Q);'
        '"RESULT sheet_"+string(i)+"_multiplicity",mult(Q);'
        '"RESULT sheet_"+string(i)+"_generator_count",size(Gn);'
        'for(j=1;j<=size(Gn);j++){"RESULT sheet_"+string(i)+"_generator_"+string(j),string(Gn[j]);}}',
    ]
    for known_index, generators in enumerate(known_sheets, start=1):
        lines += [
            f"ideal K{known_index}={','.join(generators)};",
            f"for(i=1;i<=size(P);i++){{Q=std(P[i]);"
            f'"RESULT known_{known_index}_equals_"+string(i),'
            f"(size(reduce(K{known_index},Q))==0)&&(size(reduce(Q,std(K{known_index})))==0);}}",
        ]
    lines.append("quit;")
    return "\n".join(lines)


def _decomposition(characteristic: int, phase_one: dict[str, Any], known_sheets: list[list[str]]) -> dict[str, Any]:
    result = nakayama._run_singular(_decomposition_script(characteristic, phase_one, known_sheets))
    sheets = []
    for index in range(1, int(result["sheet_count"]) + 1):
        count = int(result[f"sheet_{index}_generator_count"])
        sheets.append(
            {
                "dimension": int(result[f"sheet_{index}_dimension"]),
                "multiplicity": int(result[f"sheet_{index}_multiplicity"]),
                "generators": [result[f"sheet_{index}_generator_{position}"] for position in range(1, count + 1)],
            }
        )
    matches = [
        [index for index in range(1, len(sheets) + 1) if result[f"known_{known}_equals_{index}"] == "1"]
        for known in range(1, len(known_sheets) + 1)
    ]
    return {
        "version_code": int(result["version"]),
        "germ_dimension": int(result["germ_dimension"]),
        "sheets_intersect_to_germ": result["sheets_intersect_to_germ"] == "1",
        "sheets": sheets,
        "known_sheet_matches_one_based": matches,
    }


def _fiber_script(characteristic: int, phase_one: dict[str, Any], sheet: list[str]) -> str:
    """The special fiber over the slice origin of the Rees ideal of G restricted to one sheet."""
    names = _slice_names()
    return "\n".join(
        [
            'LIB "primdec.lib";',
            'LIB "elim.lib";',
            f"ring R={nakayama._field(characteristic)},(a,{','.join(names)},y1,y2,y3,y4,y5,y6),dp;",
            "minpoly=I2+1;",
            f"ideal J={','.join(sheet)};",
            f"ideal G={','.join(phase_one['reduced_g'])};",
            '"RESULT sheet_dimension",dim(std(J))-7;',
            "ideal Graph=J; int i;",
            f"for(i=1;i<={NAKAYAMA_GENERATOR_COUNT};i++){{Graph=Graph,(var({SLICE_VARIABLE_COUNT}+1+i)-a*G[i]);}}",
            "ideal Rees=eliminate(std(Graph),a); ideal Fiber=Rees;",
            f"for(i=1;i<={SLICE_VARIABLE_COUNT};i++){{Fiber=subst(Fiber,var(1+i),0);}}",
            "ideal Target=y1,y2,y3,y4,y5,y6;",
            "Fiber=std(sat(Fiber,Target)); ideal Gn=simplify(Fiber,2);",
            '"RESULT fiber_generator_count",size(Gn);',
            'for(i=1;i<=size(Gn);i++){"RESULT fiber_generator_"+string(i),string(Gn[i]);}',
            "list C=minAssGTZ(Fiber); ideal Cn; int j;",
            '"RESULT component_count",size(C);',
            "for(i=1;i<=size(C);i++){Cn=simplify(std(C[i]),2);"
            '"RESULT component_"+string(i)+"_generator_count",size(Cn);'
            'for(j=1;j<=size(Cn);j++){"RESULT component_"+string(i)+"_generator_"+string(j),string(Cn[j]);}}',
            "quit;",
        ]
    )


def _fiber(characteristic: int, phase_one: dict[str, Any], sheet: list[str]) -> dict[str, Any]:
    result = nakayama._run_singular(_fiber_script(characteristic, phase_one, sheet))
    count = int(result["fiber_generator_count"])
    components = []
    for index in range(1, int(result["component_count"]) + 1):
        generator_count = int(result[f"component_{index}_generator_count"])
        components.append(
            sorted(result[f"component_{index}_generator_{position}"] for position in range(1, generator_count + 1))
        )
    return {
        "generators": sorted(result[f"fiber_generator_{position}"] for position in range(1, count + 1)),
        "prime_components": sorted(components),
    }


def _arc_image(coefficients: tuple[int, ...], conic: bool) -> tuple[str, ...]:
    """The images of t_1..t_8 in Q(i)[u, d]: c_k u, with the conic parametrization at t_2 and t_8 when conic."""
    return tuple(
        CONIC_POSITIONS[position] if conic and position in CONIC_POSITIONS else f"({value})*u"
        for position, value in enumerate(coefficients)
    )


def _arc_point(coefficients: tuple[int, ...], conic: bool, parameter: int) -> tuple[Fraction, ...]:
    """The slice point of the arc at a rational parameter, with d = 1 / (1 + u^2)."""
    unit = Fraction(1, 1 + parameter * parameter)
    conic_values = {1: -2 * parameter * parameter * unit, 7: -2 * parameter * unit}
    return tuple(
        conic_values[position] if conic and position in conic_values else Fraction(value * parameter)
        for position, value in enumerate(coefficients)
    )


# cleard multiplies each entry of an ideal of Q(i)[u, d] by (1 + u^2)^M after d -> 1 / (1 + u^2), M the largest
# d-degree in the ideal: the result lies in Q(i)[u], vanishes exactly when the entry vanishes on the arc, and has the
# lowest-order coefficient vector of the arc series because (1 + u^2)^M = 1 + O(u^2) is one common unit.
CLEAR_D_PROCEDURE = (
    "proc cleard(ideal A){int M=0;int i;int j;intvec w=0,1;"
    "for(i=1;i<=ncols(A);i++){if(A[i]!=0){if(deg(A[i],w)>M){M=deg(A[i],w);}}}"
    "ideal B;matrix C;poly Q;"
    "for(i=1;i<=ncols(A);i++){B[i]=0;if(A[i]!=0){C=coeffs(A[i],d);Q=0;"
    "for(j=1;j<=nrows(C);j++){Q=Q+C[j,1]*(1+u^2)^(M-j+1);}B[i]=Q;}}"
    "return(B);}"
)


def _arc_script(
    row: dict[str, Any],
    closures: dict[str, tuple[str, ...]],
    data: Any,
    phase_one: dict[str, Any],
    sheet: list[str],
    image: tuple[str, ...],
) -> str:
    """Substitute the arc; report nonzero generator counts and the u-coefficients of G and the Schur coordinates.

    closures maps the source key and every closure strictly inside the source closure to its generators.
    """
    names = _slice_names()
    schur = ",".join(resolved._singular_expression(value) for value in data.coordinates)
    lower = sorted(key for key in closures if key != SOURCE_KEY)
    lines = [
        f"ring r={nakayama._field(0)},({','.join(regularity.GLOBAL_VARS)}),dp;",
        "minpoly=I2+1;",
        f"ideal Closure={','.join(closures[SOURCE_KEY])};",
        *(f"ideal Lower{key}={','.join(closures[key])};" for key in lower),
        f"ring Slice={nakayama._field(0)},({','.join(names)}),dp;",
        "minpoly=I2+1;",
        f"map sliceMap=r,{','.join(nakayama._germ_substitutions(row))};",
        "ideal CG=sliceMap(Closure);",
        *(f"ideal LG{key}=sliceMap(Lower{key});" for key in lower),
        f"ideal J={','.join(phase_one['reduced_j'])};",
        f"ideal S={','.join(sheet)};",
        f"ideal G={','.join(phase_one['reduced_g'])};",
        f"ideal F={schur};",
        '"RESULT closure_slice_nonzero",size(CG);',
        f"ring Arc={nakayama._field(0)},(u,d),dp;",
        "minpoly=I2+1;",
        CLEAR_D_PROCEDURE,
        f"map arcMap=Slice,{','.join(image)};",
        "ideal CGu=cleard(arcMap(CG)); ideal Ju=cleard(arcMap(J)); ideal Su=cleard(arcMap(S));",
        "ideal Gu=cleard(arcMap(G)); ideal Fu=cleard(arcMap(F));",
        '"RESULT closure_nonzero",size(simplify(CGu,2));',
        '"RESULT germ_nonzero",size(simplify(Ju,2));',
        '"RESULT sheet_nonzero",size(simplify(Su,2));',
        *(f'"RESULT lower_{key}_nonzero",size(simplify(cleard(arcMap(LG{key})),2));' for key in lower),
        "int i; int k; matrix M;",
        f"for(i=1;i<={NAKAYAMA_GENERATOR_COUNT};i++){{M=coeffs(Gu[i],u);"
        '"RESULT g_"+string(i)+"_count",nrows(M);'
        'for(k=1;k<=nrows(M);k++){"RESULT g_"+string(i)+"_"+string(k),string(M[k,1]);}}',
        f"for(i=1;i<={SCHUR_COORDINATE_COUNT};i++){{M=coeffs(Fu[i],u);"
        '"RESULT f_"+string(i)+"_count",nrows(M);'
        'for(k=1;k<=nrows(M);k++){"RESULT f_"+string(i)+"_"+string(k),string(M[k,1]);}}',
        "quit;",
    ]
    return "\n".join(lines)


def _coefficient_lists(result: dict[str, str], prefix: str, count: int) -> list[list[nakayama.Gaussian]]:
    return [
        [
            nakayama._parse_gaussian(result[f"{prefix}_{index}_{position}"])
            for position in range(1, int(result[f"{prefix}_{index}_count"]) + 1)
        ]
        for index in range(1, count + 1)
    ]


def _lowest_order(series: list[list[nakayama.Gaussian]]) -> int:
    """The smallest u-degree with a nonzero coefficient among the series; every series being zero raises."""
    orders = [
        degree for coefficients in series for degree, value in enumerate(coefficients) if value != kernel_lemma.ZERO
    ]
    _require(bool(orders), "every coefficient series is zero")
    return min(orders)


def _coefficient_at(series: list[list[nakayama.Gaussian]], degree: int) -> nakayama.GaussianVector:
    return tuple(coefficients[degree] if degree < len(coefficients) else kernel_lemma.ZERO for coefficients in series)


def _arc_vanishing(
    row: dict[str, Any],
    closures: dict[str, tuple[str, ...]],
    data: Any,
    phase_one: dict[str, Any],
    sheet: list[str],
    image: tuple[str, ...],
) -> dict[str, str]:
    return nakayama._run_singular(_arc_script(row, closures, data, phase_one, sheet, image))


def _rank_along_arc(row: dict[str, Any], coefficients: tuple[int, ...], conic: bool) -> dict[str, int]:
    boundary = [Fraction(value) for value in row["boundary_point"]]
    slice_columns = [int(value) for value in row["slice_columns_zero_based"]]
    ranks: dict[str, int] = {}
    for parameter in RANK_PARAMETERS:
        split = list(boundary)
        for column, value in zip(slice_columns, _arc_point(coefficients, conic, parameter), strict=True):
            split[column] = boundary[column] + value
        z = kernel_lemma._original_z_from_split(tuple(split))
        ranks[str(parameter)] = kernel_lemma._rank(kernel_lemma._c_matrix(z))
    return ranks


def _plane_coordinates(fiber: dict[str, Any]) -> list[str]:
    """The coordinate hyperplanes cutting the fiber out; a generator that is not a single variable raises."""
    _require(
        all(generator in {f"y{index}" for index in range(1, 7)} for generator in fiber["generators"]),
        "a special fiber is not cut out by coordinate hyperplanes",
    )
    return sorted(fiber["generators"])


def _arc_record(
    task: dict[str, Any],
    sheet: list[str],
    plane: list[str],
    coefficients: tuple[int, ...],
    conic: bool,
) -> dict[str, Any]:
    row, closures, data, phase_one = task["row"], task["closures"], task["data"], task["phase_one"]
    result = _arc_vanishing(row, closures, data, phase_one, sheet, _arc_image(coefficients, conic))
    g_series = _coefficient_lists(result, "g", NAKAYAMA_GENERATOR_COUNT)
    f_series = _coefficient_lists(result, "f", SCHUR_COORDINATE_COUNT)
    g_order = _lowest_order(g_series)
    f_order = _lowest_order(f_series)
    g_leading = _coefficient_at(g_series, g_order)
    f_leading = _coefficient_at(f_series, f_order)
    columns = nakayama._rational_columns(phase_one)
    preimage = nakayama._solve_gaussian(columns, f_leading)
    plane_indices = [int(name[1:]) - 1 for name in plane]
    lower = {key: int(result[f"lower_{key}_nonzero"]) for key in sorted(closures) if key != SOURCE_KEY}
    return {
        "coefficients_of_t1_to_t8": list(coefficients),
        "images_of_t1_to_t8": list(_arc_image(coefficients, conic)),
        "closure_generator_count": len(closures[SOURCE_KEY]),
        "closure_generators_nonzero_on_slice": int(result["closure_slice_nonzero"]),
        "closure_generators_nonzero_on_arc": int(result["closure_nonzero"]),
        "lower_closure_generators_nonzero_on_arc": lower,
        "lower_closures_containing_the_arc": sorted(key for key, count in lower.items() if count == 0),
        "germ_generators_nonzero_on_arc": int(result["germ_nonzero"]),
        "sheet_generators_nonzero_on_arc": int(result["sheet_nonzero"]),
        "schur_lowest_order_in_u": f_order,
        "schur_nonzero_leading_entry_count": sum(1 for value in f_leading if value != kernel_lemma.ZERO),
        "rees_map_lowest_order_in_u": g_order,
        "rees_map_leading_vector": [nakayama._gaussian_record(value) for value in g_leading],
        "schur_leading_vector_lies_in_embedding_span": preimage is not None,
        "schur_leading_vector_preimage": (
            None if preimage is None else [nakayama._gaussian_record(value) for value in preimage]
        ),
        "schur_leading_vector_equals_embedded_rees_leading_vector": preimage == g_leading and f_order == g_order,
        "leading_vector_is_nonzero_and_on_plane": all(g_leading[index] == kernel_lemma.ZERO for index in plane_indices)
        and any(value != kernel_lemma.ZERO for value in g_leading),
        "rank_C_z_at_parameter": _rank_along_arc(row, coefficients, conic),
    }


def _arc_passes(arc: dict[str, Any], lower_closures_containing: list[str]) -> bool:
    """The arc lies on the sheet in the source closure, in exactly the named lower closures, with the rank jump."""
    ranks = arc["rank_C_z_at_parameter"]
    return (
        arc["closure_generators_nonzero_on_arc"] == 0
        and arc["germ_generators_nonzero_on_arc"] == 0
        and arc["sheet_generators_nonzero_on_arc"] == 0
        and arc["lower_closures_containing_the_arc"] == sorted(lower_closures_containing)
        and arc["schur_lowest_order_in_u"] == 1
        and bool(arc["schur_leading_vector_equals_embedded_rees_leading_vector"])
        and bool(arc["leading_vector_is_nonzero_and_on_plane"])
        and ranks[str(RANK_PARAMETERS[0])] == RANK_AT_ORIGIN
        and all(ranks[str(parameter)] == RANK_ALONG_ARC for parameter in RANK_PARAMETERS[1:])
    )


def _phase_one(characteristic: int, *, task: Any, data: Any) -> dict[str, Any]:
    summary: dict[str, Any] = nakayama._phase_one_summary(
        nakayama._run_singular(nakayama._phase_one_script(characteristic, task, data))
    )
    return summary


def _fiber_pair(generators: list[str], *, rational: dict[str, Any], modular: dict[str, Any]) -> dict[str, Any]:
    return {"rational": _fiber(0, rational, generators), "modular": _fiber(MODULAR_PRIME, modular, generators)}


def _analyze(name: str) -> dict[str, Any]:
    resolved._cap_worker_memory()
    first_order = nakayama._load_json(nakayama.FIRST_ORDER_RESULT)
    rows = {str(entry["incidence"]): entry for entry in first_order["incidences"]}
    row = rows[name]
    _, closure = nakayama._closure_row(name, rows=rows)
    task = nakayama.RowTask(row, (), closure)
    data = resolved._schur_polynomials(resolved.IncidenceTask(row))
    phase_one = dict(
        zip(
            CHARACTERISTICS,
            parallel.ordered_map(partial(_phase_one, task=task, data=data), CHARACTERISTICS, min_items=1),
            strict=True,
        )
    )
    rational = phase_one[0]
    modular = phase_one[MODULAR_PRIME]
    reductions_agree = rational["reduced_j"] == modular["reduced_j"] and rational["reduced_g"] == modular["reduced_g"]
    rational_decomposition = _decomposition(0, rational, [])
    sheets = sorted(rational_decomposition["sheets"], key=lambda entry: entry["generators"])
    sheet_generators = [list(entry["generators"]) for entry in sheets]
    modular_decomposition = _decomposition(MODULAR_PRIME, modular, sheet_generators)
    fibers = parallel.ordered_map(
        partial(_fiber_pair, rational=rational, modular=modular), sheet_generators, min_items=1
    )

    retained = next(entry for entry in nakayama._load_json(NAKAYAMA_RESULT)["incidences"] if entry["incidence"] == name)
    retained_components = [sorted(component["generators"]) for component in retained["rational"]["components"]]
    reached = sorted({index for arc in retained["rational"]["arcs"] for index in arc["component_indices_one_based"]})
    sheet_rows = []
    for position, (entry, fiber) in enumerate(zip(sheets, fibers, strict=True), start=1):
        plane = _plane_coordinates(fiber["rational"])
        component = [index for index, value in enumerate(retained_components, start=1) if value == plane]
        sheet_rows.append(
            {
                "sheet_index_one_based": position,
                "dimension": entry["dimension"],
                "multiplicity": entry["multiplicity"],
                "generators": entry["generators"],
                "special_fiber_over_q_i": fiber["rational"],
                "special_fiber_modulo_prime": fiber["modular"],
                "plane_vanishing_coordinates": plane,
                "retained_fiber_component_one_based": component[0] if len(component) == 1 else None,
                "reached_by_a_retained_arc": bool(component) and component[0] in reached,
            }
        )
    unreached = [entry for entry in sheet_rows if not entry["reached_by_a_retained_arc"]]
    _require(len(unreached) == 1, f"{name} does not have exactly one sheet without a retained arc")
    sheet_position = int(unreached[0]["sheet_index_one_based"]) - 1
    plane = list(unreached[0]["plane_vanishing_coordinates"])

    coefficients = ARCS[name]
    mutated = tuple(
        value + 1 if index == MUTATED_COEFFICIENT_INDEX else value for index, value in enumerate(coefficients)
    )
    ideals = regularity.closure_ideals()
    closures = {
        key: tuple(str(value) for value in ideals[key]) for key in (SOURCE_KEY, *regularity.EXPECTED_LOWER[SOURCE_KEY])
    }
    _require(closures[SOURCE_KEY] == closure, "the source closure differs from the one of the Nakayama record")
    context = {"row": row, "closures": closures, "data": data, "phase_one": rational}
    sheet = sheet_generators[sheet_position]
    conic_arc, line_arc = parallel.ordered_map(
        partial(_arc_record, context, sheet, plane, coefficients), (True, False), min_items=1
    )
    mutated_result = _arc_vanishing(row, closures, data, rational, sheet, _arc_image(mutated, True))
    mutated_nonzero = {
        "sheet_generators_nonzero_on_arc": int(mutated_result["sheet_nonzero"]),
        "germ_generators_nonzero_on_arc": int(mutated_result["germ_nonzero"]),
    }
    decomposition_agrees = (
        modular_decomposition["sheets_intersect_to_germ"]
        and modular_decomposition["germ_dimension"] == rational_decomposition["germ_dimension"]
        and all(len(match) == 1 for match in modular_decomposition["known_sheet_matches_one_based"])
        and len(modular_decomposition["sheets"]) == len(sheets)
    )
    fibers_agree = all(
        entry["rational"]["generators"] == entry["modular"]["generators"]
        and entry["rational"]["prime_components"] == entry["modular"]["prime_components"]
        for entry in fibers
    )
    passed = (
        reductions_agree
        and len(sheets) == SHEET_COUNT
        and bool(rational_decomposition["sheets_intersect_to_germ"])
        and decomposition_agrees
        and fibers_agree
        and all(len(entry["special_fiber_over_q_i"]["prime_components"]) == 1 for entry in sheet_rows)
        and all(entry["retained_fiber_component_one_based"] is not None for entry in sheet_rows)
        and _arc_passes(conic_arc, [])
        and _arc_passes(line_arc, [LINE_ARC_STRATUM[name]])
        and mutated_nonzero["sheet_generators_nonzero_on_arc"] > 0
    )
    return {
        "incidence": name,
        "singular_version_code": rational_decomposition["version_code"],
        "reduced_slice_variables": rational["remaining_variables"],
        "germ_dimension": rational_decomposition["germ_dimension"],
        "reductions_agree_between_characteristics": reductions_agree,
        "sheets_intersect_to_germ": rational_decomposition["sheets_intersect_to_germ"],
        "sheets_agree_modulo_prime": decomposition_agrees,
        "special_fibers_agree_between_characteristics": fibers_agree,
        "sheets": sheet_rows,
        "retained_arc_components_one_based": reached,
        "unreached_sheet_index_one_based": sheet_position + 1,
        "conic_arc_in_the_open_source_orbit": {
            **conic_arc,
            "parameter": "u, with t_2 = -2 u^2 d, t_8 = -2 u d, d = 1 / (1 + u^2), and t_k = c_k u otherwise",
        },
        "line_arc_in_a_lower_stratum": {
            **line_arc,
            "parameter": "u, with t_k = c_k u",
        },
        "mutated_conic_arc": {
            "coefficients_of_t1_to_t8": list(mutated),
            "changed_coefficient_index_one_based": MUTATED_COEFFICIENT_INDEX + 1,
            **mutated_nonzero,
        },
        "pass": passed,
    }


def build_record() -> dict[str, Any]:
    rows = parallel.ordered_map(_analyze, INCIDENCES, min_items=1)
    inputs = dict(parallel.ordered_map(nakayama._hash_path, SOURCE_PATHS, min_items=1))
    versions = {row["singular_version_code"] for row in rows}
    _require(len(versions) == 1, "the incidences ran under different Singular builds")
    mutation_detected = all(row["mutated_conic_arc"]["sheet_generators_nonzero_on_arc"] > 0 for row in rows)
    return {
        "schema": SCHEMA,
        "inputs": inputs,
        "tools": {"python_flint": flint.__version__, "singular": f"version code {versions.pop()}"},
        "execution_contract": {
            "modular_prime": MODULAR_PRIME,
            "singular_address_space_bytes": int(nakayama.SINGULAR_MEMORY_LIMIT),
            "singular_timeout_seconds": nakayama.SINGULAR_TIMEOUT_SECONDS,
            "orderings": "global dp",
        },
        "scope": {
            "incidences": list(INCIDENCES),
            "claim_boundary": (
                "Each arc is exact on the retained transverse slice germ of its incidence at the retained "
                "basepoint. The record computes two sheets and two planes per incidence and two arcs on the sheet "
                "that no retained arc reaches: a conic arc in the open E8-bar orbit and a line arc in the closure "
                "of X+ or X-. Membership in the open orbit is the vanishing of the E8-bar closure generators with "
                "one nonvanishing generator of every closure strictly inside it. The variation of the fibers "
                "along the boundary orbit and the incidence E8bar->VB lie outside the record."
            ),
        },
        "incidences": rows,
        "summary": {
            "incidence_count": len(rows),
            "sheet_count": sum(len(row["sheets"]) for row in rows),
            "conic_arcs_in_the_open_source_orbit": sum(
                _arc_passes(row["conic_arc_in_the_open_source_orbit"], []) for row in rows
            ),
            "line_arcs_in_a_lower_stratum": sum(
                _arc_passes(row["line_arc_in_a_lower_stratum"], [LINE_ARC_STRATUM[row["incidence"]]]) for row in rows
            ),
        },
        "mutation_control": {
            "name": "one_changed_arc_coefficient",
            "input_change": "add 1 to the coefficient of t5 in each conic arc",
            "detected": mutation_detected,
        },
        "falsifier": (
            "A sheet decomposition, special fiber or plane that differs between Q(i) and the prime 32003; a sheet "
            "generator, germ generator or closure generator that fails to vanish on an arc; a closure strictly "
            "inside the E8-bar closure whose generators all vanish on the conic arc; a line arc outside the closure "
            "of X+ (at Va+) or X- (at Va-); a rank of C_z "
            "other than 8 at the origin and 10 at the parameters 1, 2 and 3; a Schur leading vector that differs "
            "from the embedded Rees leading vector or leaves the plane; or a one-coefficient change of the arc "
            "that the vanishing check still accepts."
        ),
        "pass": all(bool(row["pass"]) for row in rows) and mutation_detected,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the sheet-fiber-plane record failed")
    _require(bool(record["mutation_control"]["detected"]), "the changed arc coefficient survived")


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
