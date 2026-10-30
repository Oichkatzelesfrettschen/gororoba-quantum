"""Singular headers for the nullity-16 and VB Rees-fiber computations over F_p, regenerated from the Q(i) producer.

A header holds the ring over F_p in the presolved slice variables (dp), `number I` bound to a chosen square root of
-1, the presolved germ ideal J and the Nakayama generator ideal G. The headers come from nullity16_rees_fibers'
phase-one script (`_phase_one_script`, embedding stage off) at the chosen prime and root, so no specialized file is
edited. `check` regenerates the headers at p=32009, I=10754 and compares them with the files the degree-by-degree
computations read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import nakayama_rees_fibers as nakayama  # noqa: E402
import nullity16_basepoints as basepoints  # noqa: E402
import nullity16_rees_fibers as rees  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-fiber-inputs-v1"
CHECK_PRIME = 32009
CHECK_ROOT = 10754
SINGULAR_TIMEOUT_SECONDS = 900
LOCAL_BASE = Path("docs/local/a5-failed-runs")


@dataclass(frozen=True)
class Spec:
    slug: str
    incidence: str
    computed: str  # path relative to the local base
    route: str = "nullity16"  # producer whose phase-one script emits the input


SPECS = (
    Spec("xp-np", "X+->N+", "kaggle-pack-a/xp_np/input.sing"),
    Spec("xm-nm", "X-->N-", "kaggle-pack-a/xm_nm/input.sing"),
    Spec("iso-np", "Iso->N+", "inputs/iso_K2.sing"),
    Spec("iso-nm", "Iso->N-", "inputs/iso_K2.sing"),
    Spec("e8-np", "E8bar->N+", "inputs/e8_np_fiber.sing"),
    Spec("e8-nm", "E8bar->N-", "inputs/e8_nm_fiber.sing"),
    Spec("w8-nm", "W8->N-", "inputs/w8_nm_fiber.sing"),
    Spec("w8-np", "W8->N+", "inputs/w8_np_fiber.sing"),
    Spec("e8-vb", "E8bar->VB", "runs/e8vb_b/input.sing", "nakayama"),
)
SPEC_BY_SLUG = {spec.slug: spec for spec in SPECS}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def primary_checkout() -> Path:
    common = subprocess.run(  # noqa: S603
        ("git", "-C", str(HERE), "rev-parse", "--path-format=absolute", "--git-common-dir"),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return Path(common).parent


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _task(incidence: str) -> rees.RowTask:
    """Build the producer's RowTask; incidences absent from the nullity-16 record come from the census."""
    record = rees._load_json(rees.BASEPOINT_RESULT)
    closures = dict(
        parallel.ordered_map(
            rees._closure_row,
            tuple(sorted({str(r["source_orbit"]) for r in record["incidences"]} | {incidence.split("->")[0]})),
            min_items=1,
        )
    )
    for row in record["incidences"]:
        if row["incidence"] == incidence:
            return rees._task_row(row, closures=closures)
    census = rees._load_json(basepoints.CENSUS_RESULT)
    points = dict(filter(None, (basepoints._point_candidate(p) for p in census["points"])))
    census_row = next(r for r in census["incidences"] if r["incidence"] == incidence)
    base = basepoints._row_task(census_row, points=points, closures=closures)
    row = {
        "incidence": base.incidence,
        "passage": base.passage,
        "source_orbit": base.source_orbit,
        "boundary_orbit": base.boundary_orbit,
        "source_nullity": base.source_nullity,
        "census_point_key": base.point_key,
        "boundary_point": [str(value) for value in base.boundary_point],
        "expected_germ_dimension_multiplicity_embedding_components": list(base.expected_germ),
        "status": "census_only",
    }
    return rees.RowTask(row, base.closure_generators)


def _candidates(task: rees.RowTask, data: Any, cache: Path) -> list[int]:
    row = task.row
    if row["status"] == "completed":
        return [int(value) for value in row["selected_coordinate_indices_one_based"]]
    cache_file = cache / (str(row["incidence"]).replace(">", "") + ".json")
    if cache_file.exists():
        return [int(v) for v in json.loads(cache_file.read_text(encoding="utf-8"))["survivor_indices_one_based"]]
    outcome = rees._run_singular(
        rees._survivor_script(task, data), "normal_form_survivor_selection", SINGULAR_TIMEOUT_SECONDS
    )
    _require(outcome.status == "completed", f"{row['incidence']} survivor selection {outcome.status}")
    summary = rees._survivor_summary(outcome.results)
    cache.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return list(summary["survivor_indices_one_based"])


def _variables(polynomials: list[str]) -> list[str]:
    names = {name for text in polynomials for name in re.findall(r"\bt\d+\b", text)}
    return sorted(names, key=lambda name: int(name[1:]))


def header_text(prime: int, root: int, variables: list[str], reduced_j: list[str], reduced_g: list[str]) -> str:
    return "\n".join(
        (
            f"ring r={prime},({','.join(variables)}),dp;",
            f"number I={root};",
            f"ideal J={','.join(reduced_j) if reduced_j else '0'};",
            f"ideal G={','.join(reduced_g) if reduced_g else '0'};",
            "",
        )
    )


def _emit_nakayama(spec: Spec, *, prime: int, root: int) -> dict[str, Any]:
    """Emit a nullity-12 boundary input: nakayama_rees_fibers supplies the Schur coordinates and the row, and the
    nullity-16 phase-one script (coefficient-rank Nakayama selection, no embedding lift) supplies the presolve.

    The nakayama phase-one script selects with a sequential std(NormalForms) loop that exceeds 900 s at
    E8bar->VB; both selections are the greedy column-independence rule over the same ordered coordinates.
    """
    first_order = nakayama._load_json(nakayama.FIRST_ORDER_RESULT)
    row = next(r for r in first_order["incidences"] if r["incidence"] == spec.incidence)
    ideals = nakayama.regularity.closure_ideals()
    source = str(row["source_orbit"])
    closure = tuple(str(v) for v in ideals[nakayama.SOURCE_KEYS.get(source, source)])
    nakayama_data = nakayama.resolved._schur_polynomials(nakayama.resolved.IncidenceTask(row))
    shim_row = {
        "incidence": row["incidence"],
        "passage": "8->12",
        "source_orbit": source,
        "boundary_orbit": row["boundary_orbit"],
        "source_nullity": 8,
        "census_point_key": f"{row['boundary_orbit']}:canonical",
        "boundary_point": [str(v) for v in row["boundary_point"]],
        "expected_germ_dimension_multiplicity_embedding_components": [0, 0, 0, 0],
    }
    data = SimpleNamespace(
        slice_names=tuple(nakayama_data.slice_names),
        slice_columns=tuple(int(v) for v in row["slice_columns_zero_based"]),
        coordinates=tuple(nakayama_data.coordinates),
    )
    task = rees.RowTask(shim_row, closure)
    candidates = tuple(range(1, len(data.coordinates) + 1))
    script = rees._phase_one_script(root, task, data, candidates, prime=prime, embedding=False)  # type: ignore[arg-type]
    outcome = rees._run_singular(script, "fiber_input_phase_one", SINGULAR_TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{spec.incidence} phase one {outcome.status}: {outcome.diagnostic}")
    return _finish(spec, outcome, prime, root, len(candidates))


def _finish(spec: Spec, outcome: Any, prime: int, root: int, candidate_count: int) -> dict[str, Any]:
    results = outcome.results
    reduced_j = [results[f"reduced_j_{i}"] for i in range(1, int(results["reduced_j_count"]) + 1)]
    reduced_g = [results[f"reduced_g_{i}"] for i in range(1, int(results["reduced_g_count"]) + 1)]
    variables = _variables(reduced_j + reduced_g)
    selected = [int(results[f"selected_{i}"]) for i in range(1, int(results["selected_count"]) + 1)]
    eliminated = [results[f"eliminated_{i}"] for i in range(1, int(results["eliminated_count"]) + 1)]
    return {
        "slug": spec.slug,
        "incidence": spec.incidence,
        "route": spec.route,
        "header": header_text(prime, root, variables, reduced_j, reduced_g),
        "variables": variables,
        "candidate_count": candidate_count,
        "selected_indices_one_based": selected,
        "eliminated": eliminated,
        "generator_count": len(reduced_g),
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "peak_rss_kib": outcome.peak_rss_kib,
    }


def _emit_one(slug: str, *, prime: int, root: int, cache: Path) -> dict[str, Any]:
    spec = SPEC_BY_SLUG[slug]
    if spec.route == "nakayama":
        return _emit_nakayama(spec, prime=prime, root=root)
    task = _task(spec.incidence)
    data = basepoints._schur_coordinates(rees._base_task(task))
    candidates = _candidates(task, data, cache)
    script = rees._phase_one_script(root, task, data, tuple(candidates), prime=prime, embedding=False)
    outcome = rees._run_singular(script, "fiber_input_phase_one", SINGULAR_TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{spec.incidence} phase one {outcome.status}: {outcome.diagnostic}")
    return _finish(spec, outcome, prime, root, len(candidates))


def _parse_computed(text: str) -> dict[str, Any]:
    ring = re.search(r"^ring \w+=(\d+),\(([^)]*)\),(\w+);", text, re.M)
    _require(ring is not None, "computed file has no ring line")
    if not (ring is not None):
        raise RuntimeError("missing parsed value: ring is not None")
    j = re.search(r"^ideal J=(.*);$", text, re.M)
    g = re.search(r"^ideal G=(.*);$", text, re.M)
    _require(j is not None and g is not None, "computed file lacks ideal J or G")
    if not (j is not None and g is not None):
        raise RuntimeError("missing parsed value: j is not None and g is not None")
    root = re.search(r"^number I=(\d+);", text, re.M)
    return {
        "prime": int(ring.group(1)),
        "variables": ring.group(2).split(","),
        "order": ring.group(3),
        "root": int(root.group(1)) if root else None,
        "J": j.group(1),
        "G": g.group(1),
    }


def _compare_script(prime: int, root: int, variables: list[str], computed: dict[str, Any], header: str) -> str:
    new_j = re.search(r"^ideal J=(.*);$", header, re.M)
    new_g = re.search(r"^ideal G=(.*);$", header, re.M)
    if not (new_j is not None and new_g is not None):
        raise RuntimeError("missing parsed value: new_j is not None and new_g is not None")
    product = "*".join(variables)
    return "\n".join(
        (
            'LIB "matrix.lib";',
            f"ring r={prime},({','.join(variables)}),dp;",
            f"number I={root};",
            "option(redSB);",
            f"ideal Jc={computed['J']};",
            f"ideal Gc={computed['G']};",
            f"ideal Jn={new_j.group(1)};",
            f"ideal Gn={new_g.group(1)};",
            "ideal sc=std(Jc);ideal sn=std(Jn);",
            '"RESULT j_ideal_equal",(size(reduce(Jc,sn))==0 and size(reduce(Jn,sc))==0);',
            "int jc=(size(sc)==size(sn));int k;if(jc){for(k=1;k<=size(sc);k++){if(sc[k]-sn[k]!=0){jc=0;}}}",
            '"RESULT j_canonical_equal",jc;',
            '"RESULT g_count_computed",ncols(Gc);"RESULT g_count_new",ncols(Gn);',
            "int a;int b;intvec used=0:ncols(Gn);int exact=0;int signed=0;int modj=0;int ordered=0;int hit;",
            "if(ncols(Gc)==ncols(Gn)){for(a=1;a<=ncols(Gc);a++){if(Gc[a]-Gn[a]==0){ordered++;}}}",
            "ideal Nc=reduce(Gc,sc);ideal Nn=reduce(Gn,sc);",
            "used=0:ncols(Gn);for(a=1;a<=ncols(Gc);a++){hit=0;for(b=1;b<=ncols(Gn);b++){"
            "if(hit==0 and used[b]==0 and Gc[a]-Gn[b]==0){hit=b;}}"
            "if(hit>0){used[hit]=1;exact++;}}",
            "used=0:ncols(Gn);for(a=1;a<=ncols(Gc);a++){hit=0;for(b=1;b<=ncols(Gn);b++){"
            "if(hit==0 and used[b]==0 and (Gc[a]-Gn[b]==0 or Gc[a]+Gn[b]==0)){hit=b;}}"
            "if(hit>0){used[hit]=1;signed++;}}",
            "used=0:ncols(Gn);for(a=1;a<=ncols(Gc);a++){hit=0;for(b=1;b<=ncols(Gn);b++){"
            "if(hit==0 and used[b]==0 and (Nc[a]-Nn[b]==0 or Nc[a]+Nn[b]==0)){hit=b;}}"
            "if(hit>0){used[hit]=1;modj++;}}",
            '"RESULT g_same_order",ordered;"RESULT g_matched_exact",exact;'
            '"RESULT g_matched_signed",signed;"RESULT g_matched_signed_mod_j",modj;',
            "ideal Nb=Nc,Nn;",
            f"matrix Mc=coef(Nc,{product});matrix Mn=coef(Nn,{product});matrix Mb=coef(Nb,{product});",
            "intvec rc=2..ncols(Nc)+1;intvec rn=2..ncols(Nn)+1;intvec rb=2..ncols(Nb)+1;",
            "intvec cc=1..ncols(Mc);intvec cn=1..ncols(Mn);intvec cb=1..ncols(Mb);",
            '"RESULT span_rank_computed",rank(submat(Mc,rc,cc));"RESULT span_rank_new",rank(submat(Mn,rn,cn));'
            '"RESULT span_rank_union",rank(submat(Mb,rb,cb));',
            "quit;",
        )
    )


def compare(slug: str, emitted: dict[str, Any], prime: int, root: int, base: Path) -> dict[str, Any]:
    spec = SPEC_BY_SLUG[slug]
    path = base / LOCAL_BASE / spec.computed
    text = path.read_text(encoding="utf-8")
    computed = _parse_computed(text)
    new = _parse_computed(emitted["header"])
    record: dict[str, Any] = {
        "computed_file": str(LOCAL_BASE / spec.computed),
        "computed_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "computed_ring_order": computed["order"],
        "computed_variables": computed["variables"],
        "regenerated_variables": new["variables"],
    }
    record["j_text_identical"] = computed["J"].replace(" ", "") == new["J"].replace(" ", "")
    record["g_text_identical"] = computed["G"].replace(" ", "") == new["G"].replace(" ", "")
    if set(computed["variables"]) != set(new["variables"]):
        record["status"] = "different"
        record["difference"] = "slice variable sets differ"
        return record
    variables = computed["variables"]
    outcome = rees._run_singular(
        _compare_script(prime, root, variables, computed, emitted["header"]), "compare", SINGULAR_TIMEOUT_SECONDS
    )
    _require(outcome.status == "completed", f"{slug} comparison {outcome.status}: {outcome.diagnostic}")
    result = {key: int(value) for key, value in outcome.results.items()}
    record["singular"] = result
    count = result["g_count_computed"]
    same_count = count == result["g_count_new"]
    j_equal = bool(result["j_ideal_equal"])
    if record["j_text_identical"] and record["g_text_identical"]:
        record["status"] = "identical"
    elif j_equal and same_count and result["g_same_order"] == count:
        record["status"] = "identical-polynomials-text-differs"
    elif j_equal and same_count and result["g_matched_signed"] == count:
        record["status"] = "equal-up-to-order-sign"
    elif (
        j_equal and same_count and result["span_rank_computed"] == result["span_rank_new"] == result["span_rank_union"]
    ):
        record["status"] = "equal-span-mod-J" + ("" if result["g_matched_signed_mod_j"] == count else " (not termwise)")
    else:
        record["status"] = "different"
        record["difference"] = (
            f"J ideal equal={j_equal}; G counts {count} vs {result['g_count_new']}; exact matches "
            f"{result['g_matched_exact']}, signed matches {result['g_matched_signed']}, mod-J matches "
            f"{result['g_matched_signed_mod_j']}; span ranks {result['span_rank_computed']}/"
            f"{result['span_rank_new']}/{result['span_rank_union']}"
        )
    return record


def _worker(slug: str, *, prime: int, root: int, cache: Path, base: Path, do_compare: bool) -> dict[str, Any]:
    emitted = _emit_one(slug, prime=prime, root=root, cache=cache)
    if do_compare:
        emitted["comparison"] = compare(slug, emitted, prime, root, base)
    return emitted


def split_prime_root(prime: int, root: int) -> None:
    _require(prime % 4 == 1, f"{prime} is not 1 mod 4")
    _require(root * root % prime == prime - 1, f"{root} is not a square root of -1 modulo {prime}")


def find_split_prime(start: int, step: int = -1) -> tuple[int, int]:
    """Return the first prime p = 1 mod 4 from start in direction step with the smaller square root of -1."""
    p = start
    while True:
        if p % 4 == 1 and all(p % d for d in range(2, int(p**0.5) + 1)):
            g = 2
            while pow(g, (p - 1) // 2, p) != p - 1:
                g += 1
            r = pow(g, (p - 1) // 4, p)
            return p, min(r, p - r)
        p += step


def run(prime: int, root: int, slugs: tuple[str, ...], out_root: Path, *, do_compare: bool) -> dict[str, Any]:
    split_prime_root(prime, root)
    base = primary_checkout()
    directory = out_root / f"p{prime}-r{root}"
    directory.mkdir(parents=True, exist_ok=True)
    work = partial(_worker, prime=prime, root=root, cache=out_root / "survivors", base=base, do_compare=do_compare)
    rows = parallel.ordered_map(work, slugs, min_items=1)
    receipt_rows = []
    for row in rows:
        (directory / f"{row['slug']}.sing").write_text(row["header"], encoding="utf-8")
        receipt = {key: value for key, value in row.items() if key != "header"}
        receipt["header_file"] = f"{row['slug']}.sing"
        receipt["header_sha256"] = _sha256_text(row["header"])
        receipt_rows.append(receipt)
    receipt = {
        "schema": SCHEMA,
        "prime": prime,
        "i_root": root,
        "tools": {"singular": basepoints.schur._singular_version(), "python_flint": basepoints.flint.__version__},
        "producer_sha256": rees._sha256(Path(rees.__file__)),
        "incidences": receipt_rows,
    }
    (directory / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("emit", "check"))
    parser.add_argument("--prime", type=int, default=CHECK_PRIME)
    parser.add_argument("--root", type=int, default=CHECK_ROOT)
    parser.add_argument("--slug", action="append", choices=[spec.slug for spec in SPECS])
    parser.add_argument("--out", type=Path, help="output root (default: build/inputs of the primary checkout)")
    arguments = parser.parse_args()
    slugs = tuple(arguments.slug) if arguments.slug else tuple(spec.slug for spec in SPECS)
    out_root = arguments.out or primary_checkout() / LOCAL_BASE / "build" / "inputs"
    receipt = run(arguments.prime, arguments.root, slugs, out_root, do_compare=arguments.mode == "check")
    for row in receipt["incidences"]:
        status = row.get("comparison", {}).get("status", "emitted")
        print(f"{row['slug']} {status} vars={len(row['variables'])} g={row['generator_count']} {row['wall_seconds']}s")
    different = [row["slug"] for row in receipt["incidences"] if row.get("comparison", {}).get("status") == "different"]
    if different:
        raise SystemExit(f"regenerated fiber inputs differ from the computed headers: {', '.join(different)}")


if __name__ == "__main__":
    main()
