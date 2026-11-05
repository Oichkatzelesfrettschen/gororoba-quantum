"""Collate the scans, the numeric survey, the certificates and the controls into campaign_summary.json (all counts),
result.json (component P2) and result_P1.json (component P1)."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

import symfam as SF
from arc_targets import Target, k2_hilbert_function
from gen_family import P1_FAMILY, P2_FAMILY

PT = (3, 5, 7, 11, 2)
SCAN_FILES = {"k-rs": "scan_k_rs", "k-pq": "scan_k_pq", "near": "scan_near"}


def classify(r: dict[str, Any]) -> str:
    if "status" in r:
        return "no-order"
    in_p2, in_p1, in_k2 = r["P2NONVAN"] == 0, r["P1NONVAN"] == 0, r["K2NONVAN"] == 0
    if not in_k2:
        return "outside-K2"
    if in_p1 and in_p2:
        return "P1-and-P2"
    return "P2-only" if in_p2 else "P1-only" if in_p1 else "K2-only"


def ngen(text: str) -> int:
    return len([t for t in text.strip().split(",") if t])


def parse_primes_log(log: str) -> dict[str, Any]:
    """Counts printed by k2_primes.sing: the primes, the radical identity and the two Hilbert functions."""
    primes = {
        int(m.group(1)): {
            "projective_dimension": int(m.group(2)),
            "degree": int(m.group(3)),
            "linear_generators": int(m.group(4)),
        }
        for m in re.finditer(r"^prime (\d+) proj dim (-?\d+) deg (\d+) linear gens (\d+)$", log, re.M)
    }
    hf_k2 = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"^HF_K2 (\d+) (\d+)$", log, re.M)}
    hf_sqrt = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"^HF_sqrtK2 (\d+) (\d+)$", log, re.M)}
    ident = re.search(r"^radical == P1 cap P2 : (\d)$", log, re.M)
    k2dim = re.search(r"^K gens (\d+) dim (\d+) deg (\d+)$", log, re.M)
    raddim = re.search(r"^radical dim (\d+) deg (\d+)$", log, re.M)
    if ident is None or k2dim is None or raddim is None or not hf_k2 or not hf_sqrt:
        raise ValueError("k2_primes.log lacks a required line")
    return {
        "primes_by_log_index": primes,
        "radical_equals_P1_cap_P2": ident.group(1) == "1",
        "K2_standard_basis_elements": int(k2dim.group(1)),
        "K2_dim_deg": [int(k2dim.group(2)), int(k2dim.group(3))],
        "radical_dim_deg": [int(raddim.group(1)), int(raddim.group(2))],
        "HF_K2": hf_k2,
        "HF_sqrt_K2": hf_sqrt,
    }


def family_info(target: Target, fam_tag: str, log: str) -> dict[str, Any]:
    def g(key: str) -> int:
        found = re.search(key + r" (\d+)", log)
        if found is None:
            raise ValueError(f"{fam_tag}: no {key} in the log")
        return int(found.group(1))

    fj = SF.load_fj(log, target.prime)
    return {
        "nu": g("NU"),
        "P2_nonvanishing": g("P2NONVAN"),
        "P1_nonvanishing": g("P1NONVAN"),
        "K2_nonvanishing": g("K2NONVAN"),
        "symbolic_jacobian_rank_at_point": g("RANK5"),
        "nonzero_coordinates": sorted(fj),
        "limit_vector_at_point": SF.vector(fj, PT, target.prime),
    }


def survey_summary(rows: list[dict[str, Any]]) -> tuple[Counter[str], dict[tuple[int, ...], int]]:
    cnt: Counter[str] = Counter()
    bases: dict[tuple[int, ...], int] = {}
    for r in rows:
        if r["status"] != "ok":
            cnt["status: " + r["status"][:24]] += 1
            continue
        b = r["base"]
        origin = all(x == 0 for x in b)
        line = b[0] == b[2] and b[1] == 0 and all(x == 0 for x in b[3:])
        where = "origin" if origin else "line t1=t3" if line else "other base point"
        cl = ("P2" if r["P2"] else "") + ("P1" if r["P1"] else "") or "neither"
        cnt[f"{where} | {cl} | {'in K2' if r['K2'] else 'OUTSIDE K2'}"] += 1
        if where == "other base point":
            key = tuple(b)
            bases[key] = bases.get(key, 0) + 1
    return cnt, bases


def collate(
    target: Target, scans: dict[str, list[dict[str, Any]]], survey: list[dict[str, Any]], d: dict[str, Any]
) -> None:
    """Write the three summary files into the target directory; `d` holds the parsed step outputs."""
    out = target.directory
    p = target.prime
    summary: dict[str, Any] = {
        "target": target.name,
        "fiber": target.fiber,
        "prime": p,
        "i": target.root,
        "sign_t9": target.sign9,
        "symbolic_families": {},
    }
    tot: Counter[str] = Counter()
    maxrank: Counter[str] = Counter()
    for kind, rows in scans.items():
        c = Counter(classify(r) for r in rows)
        summary["symbolic_families"][SCAN_FILES[kind]] = {
            "total": len(rows),
            "classes": dict(c),
            "x0_not_origin": sum(1 for r in rows if "status" not in r and not r["x0_zero"]),
        }
        tot.update(c)
        for r in rows:
            if "status" not in r:
                cl = classify(r)
                maxrank[cl] = max(maxrank[cl], r["RANK5"])
    all_rows = [r for rows in scans.values() for r in rows if "status" not in r]
    summary["symbolic_totals"] = dict(tot)
    summary["max_jacobian_rank_by_class"] = dict(maxrank)
    summary["families_with_jacobian_rank_5"] = [r["tag"] for r in all_rows if r["RANK5"] >= 5]
    summary["p1_only_families_with_rank_4"] = [
        r["tag"] for r in all_rows if classify(r) == "P1-only" and r["RANK5"] == 4
    ]
    summary["families_without_order_up_to_7"] = [r["tag"] for rows in scans.values() for r in rows if "status" in r]
    cnt, bases = survey_summary(survey)
    summary["numeric_survey"] = dict(cnt)
    summary["numeric_survey_other_base_points"] = {
        "distinct": len(bases),
        "pattern_of_zero_coordinates": sorted({"".join("0" if x == 0 else "x" for x in b) for b in bases}),
        "t1_eq_t3_t4_eq_t6_t5_eq_t7_and_t2_t8_t9_zero": all(
            b[0] == b[2] and b[3] == b[5] and b[4] == b[6] and b[1] == b[7] == b[8] == 0 for b in bases
        ),
    }
    summary["certificates"] = {"P2": d["numeric_P2"], "P1": d["numeric_P1"]}
    summary["mutation_controls"] = d["mutation"]
    summary["hilbert"] = {"k2": d["primes"]["HF_K2"], "sqrt_k2": d["primes"]["HF_sqrt_K2"]}
    (out / "campaign_summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    sums = lambda prefix: sum(v for k, v in cnt.items() if k.startswith(prefix) and "OUTSIDE" in k)  # noqa: E731
    outside = {
        "total": tot["outside-K2"] + sums("origin") + sums("line") + sums("other"),
        "origin_symbolic_families": tot["outside-K2"],
        "origin_numeric_arcs": sums("origin"),
        "line_t1_eq_t3_numeric_arcs": sums("line"),
        "other_base_points_numeric_arcs": sums("other"),
        "arcs_surveyed_by_base": {k: v for k, v in cnt.items() if not k.startswith("status")},
    }
    n1, n2, nk = ngen(d["P1"]), ngen(d["P2"]), ngen(d["k2"])
    vphi = d["verify_phi_log"]
    vanish = re.search(r"generators vanishing identically: (\d+) of (\d+)", vphi)
    mut1 = re.search(r"\(t9 -> t9\+1\): nonzero residues in (\d+) of (\d+)", vphi)
    mut2 = re.search(r"\(t9 -> -t9\): nonzero residues in (\d+) of (\d+)", vphi)
    if vanish is None or mut1 is None or mut2 is None:
        raise ValueError("verify_phi.log lacks a required line")
    jd = d["j_decomp_log"]
    jdim = re.search(r"J gens \d+ dim (\d+) deg (\d+)", jd)
    jmin = re.search(r"minimal primes of J: (\d+)", jd)
    if jdim is None or jmin is None:
        raise ValueError("j_decomp.log lacks a required line")
    extra: dict[str, Any] = {
        "ideal_J": {
            "minimal_primes_over_F_p": int(jmin.group(1)),
            "dim": int(jdim.group(1)),
            "deg": int(jdim.group(2)),
            "prime_contains_only_polynomials_vanishing_at_origin": "contained in the maximal ideal of the origin: 1"
            in jd,
        }
    }
    if "cross_control" in d:
        extra["cross_control_against_N_minus_ideals"] = d["cross_control"]
        extra["compare_with_N_minus_ideals"] = d["compare_nm_log"].strip().split("\n")
    common = dict(
        extra,
        field=f"F_{p}, i = {target.root}",
        fiber=target.fiber,
        base_point="origin of the slice",
        parametrization={
            "J_generators_vanishing_on_Phi": list(vanish.groups()),
            "mutation_t9_plus_1_nonzero_residues": list(mut1.groups()),
            "mutation_t9_negated_nonzero_residues": list(mut2.groups()),
        },
        phi_jacobian_rank=d["phi_rank"]["rank"],
        phi_jacobian_point=d["phi_rank"]["point"],
        k2_generators=nk,
        prime_generator_counts={"P1": n1, "P2": n2},
        limits_outside_K2=outside,
        scans={k: v["classes"] for k, v in summary["symbolic_families"].items()},
        max_jacobian_rank_by_class=dict(maxrank),
        hilbert_function_sqrt_K2=d["primes"]["HF_sqrt_K2"],
        campaign_summary="campaign_summary.json",
    )
    c2, c1 = d["numeric_P2"], d["numeric_P1"]
    f2 = family_info(target, P2_FAMILY.tag, d["family_P2_log"])
    f1 = family_info(target, P1_FAMILY.tag, d["family_P1_log"])
    grid_names = {"W": [1, 3, 7], "R": [2, 5, 13], "S": [1, 6, 19], "Z": [4, 11]}
    result_p2 = dict(
        component="P2",
        certified=bool(
            f2["P2_nonvanishing"] == 0
            and f2["K2_nonvanishing"] == 0
            and min(c2["jacobian_rank"].values()) == 4
            and sum(c2["failures"].values()) == 0
        ),
        family=dict(
            arc="x(s) = Phi(w = W s, rho = R s, sigma = S s, E, zeta = Z s)",
            parameters=["W", "R", "S", "Z", "E"],
            order=2,
            limit="E^2 F_j = coefficient of s^2 of E^2 G_j(x(s))",
            symbolic_limit_log=f"families/fam_{P2_FAMILY.tag}.log",
        ),
        jacobian_rank=min(c2["jacobian_rank"].values()),
        jacobian_rank_points=c2["jacobian_rank"],
        explicit_point=dict(parameters=dict(zip("WRSZE", PT, strict=True)), **f2),
        grid=dict(points=c2["grid_size"], checked=c2["points_checked"], **grid_names, E=[2, 3, 5, 10, 23]),
        symbolic_vanishing=dict(
            P2_generators_nonvanishing=f"{f2['P2_nonvanishing']} of {n2}",
            P1_generators_nonvanishing=f"{f2['P1_nonvanishing']} of {n1}",
            K2_generators_nonvanishing=f"{f2['K2_nonvanishing']} of {nk}",
        ),
        numeric_grid_failures=c2["failures"],
        negative_controls=d["mutation"],
        **common,
    )
    result_p1 = dict(
        component="P1",
        certified=bool(
            f1["P1_nonvanishing"] == 0
            and f1["K2_nonvanishing"] == 0
            and min(c1["jacobian_rank"].values()) == 5
            and sum(c1["failures"].values()) == 0
        ),
        family=dict(
            arc="x(s) = Phi(w = W s^2, rho = (R s + S s)/2, sigma = (R s - S s)/2, e = -1 + E1 s^2, zeta = Z s)",
            parameters=["W", "R", "S", "Z", "E1"],
            order=5,
            limit="F_j = coefficient of s^5 of G_j(x(s))",
            symbolic_limit_log=f"families/fam_{P1_FAMILY.tag}.log",
        ),
        jacobian_rank=min(c1["jacobian_rank"].values()),
        jacobian_rank_points=c1["jacobian_rank"],
        explicit_point=dict(parameters=dict(zip(["W", "R", "S", "Z", "E1"], PT, strict=True)), **f1),
        grid=dict(points=c1["grid_size"], checked=c1["points_checked"], **grid_names, E1=[2, 3, 5, 10, 23]),
        symbolic_vanishing=dict(
            P1_generators_nonvanishing=f"{f1['P1_nonvanishing']} of {n1}",
            P2_generators_nonvanishing=f"{f1['P2_nonvanishing']} of {n2}",
            K2_generators_nonvanishing=f"{f1['K2_nonvanishing']} of {nk}",
        ),
        numeric_grid_failures=c1["failures"],
        negative_controls=d["mutation"],
        **common,
    )
    (out / "result.json").write_text(json.dumps(result_p2, indent=1) + "\n")
    (out / "result_P1.json").write_text(json.dumps(result_p1, indent=1) + "\n")
    if not (result_p2["certified"] and result_p1["certified"]):
        raise RuntimeError(f"{target.name}: a component is not certified")
    hf = k2_hilbert_function(target)
    if {str(k): v for k, v in d["primes"]["HF_K2"].items()} != hf:
        raise RuntimeError(f"{target.name}: HF(k[y]/K2) differs from k2-hilbert.jsonl")
