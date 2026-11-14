"""The relation ideals of the Iso and W8 fiber cones on the weight slice equal their quadric ideals: order functions.

The argument is the first half of `e8_relation_ideal_orders.py`. On the weight slice at N- or N+ let O be the local
ring of the source germ, I = (G_1, ..., G_g) the Pfaffian ideal, L the relation ideal of the fiber cone and K the ideal
of the degree-2 relations of `weight_slice_fiber_relations.py`, each of which lies in L
(`weight_slice_relation_membership.py`). A polynomial map phi from an affine space to the slice that sends the
center of a weight vector w to the origin and kills the germ ideal J gives the order v_w(x) = (lowest w-weight of a
term of phi^* x). The weights are nonnegative and every slice coordinate has positive order e, so every element of
m I^d has order at least d nu + e with nu = min_a v_w(G_a), and L lies in the limit ideal Q_w = ker(y_a -> V_a) of the
initial forms V_a (the part of phi^* G_a of weight nu). Q_w equals a minimal prime P of K when the generators of P
vanish on V and the Jacobian matrix of V has rank dim P at one rational point (characteristic 0: Q_w is prime,
contains P, and dim S/Q_w is the generic rank of that matrix).

Both germs are quadric cones: s5^2 + 4 s3 s6 + 4 s1 s9 = 0 for Iso and s5^2 + 4 s3 s6 + 4 s2 s8 + 4 s1 s9 = 0 for W8
at N-, with s4 and s5 exchanged and s7 and s8 exchanged at N+. The map solves the quadric for s6 after s5 = y b,
s9 = y c (and s8 = y d for W8) with y = s3 and x = s1, and it replaces s2 by x b / 2 - t: the combination
t = s1 s5 / (2 s3) - s2 is the coordinate whose order separates the limits, and no weight vector on s2 itself reaches
the dimension of the fiber cone (ledger row A5-458).

- Iso: weights (1, 2, 0, 0, 2) on (x, y, b, c, t) give Q_w = K, the prime of dimension 5 and degree 23. Hence
  L lies in K, and L = K.
- W8: weights (1, 1, 0, 0, 0, 1) and (1, 2, 0, 0, 1, 2) on (x, y, b, c, d, t) give the two minimal primes of
  dimension 6 and degrees 20 and 30. K is their intersection, so L lies in K, and L = K.

Controls: a second weight vector whose initial forms have rank below the dimension, the map of the other basepoint
(generators of J stay nonzero), and for W8 the other prime on each family of initial forms (it stays nonzero).

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/iso_w8_relation_ideal_orders.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from string import Template
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "iso-w8-relation-ideal-orders-result.json"
SCHEMA = "gororoba.a5.iso-w8-relation-ideal-orders/1"
INPUTS = ("iso_w8_relation_ideal_orders.py", "weight_slice_fiber_relations.py")
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
CELLS: tuple[tuple[str, str], ...] = tuple((orbit, source) for orbit in ("N-", "N+") for source in ("iso", "w8"))
GENERATORS = {"iso": 17, "w8": 24}
PARAMETERS = {"iso": ("qx", "qy", "qb", "qc", "qt"), "w8": ("qx", "qy", "qb", "qc", "qd", "qt")}
RANK_POINT = (2, 3, 5, 7, 11, 13)
# The image of s_1, ..., s_9 at N-. At N+ the slots of s_4, s_5 and of s_7, s_8 are exchanged.
PARAMETRIZATION_MINUS: dict[str, tuple[str, ...]] = {
    "iso": ("qx", "qx*qb/2-qt", "qy", "0", "qy*qb", "-(qy*qb^2+4*qx*qc)/4", "0", "0", "qy*qc"),
    "w8": (
        "qx",
        "qx*qb/2-qt",
        "qy",
        "0",
        "qy*qb",
        "-(qy*qb^2+4*qx*qc+4*(qx*qb/2-qt)*qd)/4",
        "0",
        "qy*qd",
        "qy*qc",
    ),
}
EXCHANGE = (0, 1, 2, 4, 3, 5, 7, 6, 8)
# (dimension, degree) of each minimal prime of K, by name.
PRIMES: dict[str, dict[str, tuple[int, int]]] = {
    "iso": {"P23": (5, 23)},
    "w8": {"P20": (6, 20), "P30": (6, 30)},
}
# Weight vector, the minimal prime its limit ideal equals, and for W8 the other prime, which stays nonzero.
ORDER_FUNCTIONS: dict[str, dict[str, tuple[tuple[int, ...], str, str | None]]] = {
    "iso": {"prime23": ((1, 2, 0, 0, 2), "P23", None)},
    "w8": {"prime20": ((1, 1, 0, 0, 0, 1), "P20", "P30"), "prime30": ((1, 2, 0, 0, 1, 2), "P30", "P20")},
}
# A weight vector with positive order on the slice coordinates whose initial forms have rank below the dimension.
DEFICIENT_WEIGHTS = {"iso": (1, 1, 0, 0, 1), "w8": (1, 1, 1, 1, 1, 1)}
EXPECTED_ORDERS: dict[str, dict[str, dict[str, Any]]] = {
    "iso": {"prime23": {"weights": [1, 2, 0, 0, 2], "ideal_order": 4, "maximal_ideal_order": 1, "target": [5, 23]}},
    "w8": {
        "prime20": {"weights": [1, 1, 0, 0, 0, 1], "ideal_order": 2, "maximal_ideal_order": 1, "target": [6, 20]},
        "prime30": {"weights": [1, 2, 0, 0, 1, 2], "ideal_order": 4, "maximal_ideal_order": 1, "target": [6, 30]},
    },
}
EXPECTED: dict[str, dict[str, Any]] = {
    "iso": {"ideal": [5, 23, 68], "minimal_primes": [[5, 23]], "radical": True, "germ_nonzero_on_parametrization": 0},
    "w8": {
        "ideal": [6, 50, 144],
        "minimal_primes": [[6, 20], [6, 30]],
        "radical": True,
        "germ_nonzero_on_parametrization": 0,
    },
}

HEAD = Template("""
matrix SM=matrix(S); int nrel=ncols(SM); int nprod=nrows(SM); ideal mxr=maxideal(1);
intmat IXM[nprod][2]; for(a=1;a<=nprod;a++){ IXM[a,1]=IX[a][1]; IXM[a,2]=IX[a][2]; }
ring Y=(0,i),(y(1..$generators)),dp; minpoly=i^2+1; option(redSB);
matrix SM=fetch(r,SM); ideal K; poly q; int u1; int u2;
for(u1=1;u1<=nrel;u1++){ q=0;
  for(u2=1;u2<=nprod;u2++){ if(SM[u2,u1]!=0){ q=q+SM[u2,u1]*y(IXM[u2,1])*y(IXM[u2,2]); } } K[u1]=q; }
ideal sK=std(K); print("RESULT ideal "+string(dim(sK))+","+string(mult(sK))+","+string(size(K)));
list MP=minAssGTZ(K); ideal R=1; ideal component; $declarations
for(k=1;k<=size(MP);k++){ component=std(MP[k]);
  print("RESULT prime "+string(dim(component))+","+string(mult(component)));
  $assignments
  R=intersect(R,MP[k]); }
print("RESULT radical "+string(size(reduce(R,sK))==0));
$targets
ring P=(0,i),($parameters),dp; minpoly=i^2+1; option(redSB);
proc vmin(poly f, intvec wv){ if(f==0){return(-1);} int dd=0; while(jet(f,dd,wv)==0){dd++;} return(dd); }
map ph=r,$mapping;
ideal JP=ph(J); print("RESULT germ_nonzero_on_parametrization "+string(size(simplify(JP,2))));
map other=r,$other_mapping;
ideal JO=other(J); print("RESULT germ_nonzero_on_other_parametrization "+string(size(simplify(JO,2))));
ideal gp=ph(G); ideal sp=ph(mxr);
intvec wv; int nu; int e; int dd; string orders; ideal V; matrix JN; ideal TV;
""")

ORDER_BLOCK = Template("""
wv=$weights; nu=vmin(gp[1],wv); e=-1; orders="";
for(k=1;k<=$generators;k++){ dd=vmin(gp[k],wv); if(dd<nu){nu=dd;} orders=orders+string(dd)+","; }
for(k=1;k<=9;k++){ if(sp[k]!=0){ dd=vmin(sp[k],wv); if(e<0 or dd<e){e=dd;} } }
print("RESULT $name.generator_orders "+orders);
print("RESULT $name.ideal_order "+string(nu));
print("RESULT $name.maximal_ideal_order "+string(e));
V=0; for(k=1;k<=$generators;k++){ V[k]=jet(gp[k],nu,wv); }
JN=subst(jacob(V),$point); print("RESULT $name.initial_jacobian_rank "+string(rank(JN)));
$target_block
""")

TARGET_BLOCK = Template("""map ev_$name=Y,V; TV=ev_$name($target);
print("RESULT $name.target_nonzero_on_initial_forms "+string(size(simplify(TV,2))));
""")

OTHER_BLOCK = Template("""TV=ev_$name($other);
print("RESULT $name.other_prime_nonzero_on_initial_forms "+string(size(simplify(TV,2))));
""")


def parametrization(orbit: str, source: str) -> tuple[str, ...]:
    minus = PARAMETRIZATION_MINUS[source]
    if orbit == "N-":
        return minus
    if orbit != "N+":
        raise ValueError(f"unknown basepoint {orbit}")
    return tuple(minus[index] for index in EXCHANGE)


def _weights(weights: tuple[int, ...]) -> str:
    return ",".join(str(weight) for weight in weights)


def order_stage(orbit: str, source: str) -> str:
    """The Singular statements appended to the weight-slice script of one cell."""
    other_orbit = "N+" if orbit == "N-" else "N-"
    names = PARAMETERS[source]
    generators = GENERATORS[source]
    point = ",".join(f"{name},{value}" for name, value in zip(names, RANK_POINT, strict=False))
    primes = PRIMES[source]
    stage = HEAD.substitute(
        generators=generators,
        declarations=" ".join(f"ideal {name};" for name in primes),
        assignments=" ".join(
            f"if(dim(component)=={dimension} and mult(component)=={degree}){{ {name}=component; }}"
            for name, (dimension, degree) in primes.items()
        ),
        targets="\n".join(
            f'print("RESULT target.{name} "+string(dim({name}))+","+string(mult({name})));' for name in primes
        ),
        parameters=",".join(names),
        mapping=",".join(parametrization(orbit, source)),
        other_mapping=",".join(parametrization(other_orbit, source)),
    )
    for name, (weights, target, other_prime) in ORDER_FUNCTIONS[source].items():
        block = TARGET_BLOCK.substitute(name=name, target=target)
        if other_prime is not None:
            block += OTHER_BLOCK.substitute(name=name, other=other_prime)
        stage += ORDER_BLOCK.substitute(
            name=name, weights=_weights(weights), generators=generators, point=point, target_block=block
        )
    stage += ORDER_BLOCK.substitute(
        name="deficient",
        weights=_weights(DEFICIENT_WEIGHTS[source]),
        generators=generators,
        point=point,
        target_block="",
    )
    return stage


def _integers(text: str) -> list[int]:
    return [int(part) for part in text.split(",") if part != ""]


def _order_record(values: dict[str, list[str]], name: str) -> dict[str, Any]:
    return {
        "generator_orders": _integers(values[f"{name}.generator_orders"][0]),
        "ideal_order": int(values[f"{name}.ideal_order"][0]),
        "maximal_ideal_order": int(values[f"{name}.maximal_ideal_order"][0]),
        "initial_jacobian_rank": int(values[f"{name}.initial_jacobian_rank"][0]),
    }


def certify(cell: tuple[str, str]) -> dict[str, Any]:
    orbit, source = cell
    marker = 'print("RESULT done 1");'
    script = ws.fiber_script(ws.orbit_task(orbit), source, 0, 0)
    if script.count(marker) != 1:
        raise RuntimeError("the weight-slice script has no single end marker")
    run = ws.run_singular(script.replace(marker, order_stage(orbit, source) + marker))
    values = run["values"]
    functions: dict[str, Any] = {}
    for name, (weights, target, other_prime) in ORDER_FUNCTIONS[source].items():
        function = {"weights": list(weights), **_order_record(values, name)}
        function["target"] = _integers(values[f"target.{target}"][0])
        function["target_nonzero_on_initial_forms"] = int(values[f"{name}.target_nonzero_on_initial_forms"][0])
        if other_prime is not None:
            function["other_prime_nonzero_on_initial_forms"] = int(
                values[f"{name}.other_prime_nonzero_on_initial_forms"][0]
            )
        functions[name] = function
    return {
        "orbit": orbit,
        "source": source,
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "parametrization": list(parametrization(orbit, source)),
        "ideal": _integers(values["ideal"][0]),
        "minimal_primes": sorted(_integers(text) for text in values["prime"]),
        "radical": values["radical"] == ["1"],
        "germ_nonzero_on_parametrization": int(values["germ_nonzero_on_parametrization"][0]),
        "order_functions": functions,
        "controls": {
            "deficient_weights": {"weights": list(DEFICIENT_WEIGHTS[source]), **_order_record(values, "deficient")},
            "other_basepoint_parametrization": {
                "germ_nonzero": int(values["germ_nonzero_on_other_parametrization"][0])
            },
        },
    }


def _function_problems(label: str, source: str, name: str, function: Any) -> list[str]:
    if not isinstance(function, dict):
        return [f"{label}: the order function {name} is missing"]
    expected = EXPECTED_ORDERS[source][name]
    found = [
        f"{label}: {name} {key} differs from {value}" for key, value in expected.items() if function.get(key) != value
    ]
    orders = function.get("generator_orders")
    if not isinstance(orders, list) or len(orders) != GENERATORS[source] or min(orders) != function.get("ideal_order"):
        found.append(f"{label}: {name} generator orders do not have the ideal order as their minimum")
    if function.get("target_nonzero_on_initial_forms") != 0:
        found.append(f"{label}: {name} target prime does not vanish on the initial forms")
    if function.get("initial_jacobian_rank") != expected["target"][0]:
        found.append(f"{label}: {name} initial_jacobian_rank differs from the dimension of the target prime")
    if ORDER_FUNCTIONS[source][name][2] is not None and function.get("other_prime_nonzero_on_initial_forms", 0) <= 0:
        found.append(f"{label}: {name} other prime vanishes on the initial forms")
    return found


def _control_problems(label: str, source: str, cell: dict[str, Any]) -> list[str]:
    controls = cell.get("controls")
    if not isinstance(controls, dict) or set(controls) != {"deficient_weights", "other_basepoint_parametrization"}:
        return [f"{label}: the controls are missing"]
    found: list[str] = []
    deficient = controls["deficient_weights"]
    dimension = EXPECTED[source]["ideal"][0]
    if deficient.get("weights") != list(DEFICIENT_WEIGHTS[source]) or deficient.get("maximal_ideal_order", 0) < 1:
        found.append(f"{label}: the deficient-weights control has other weights or no positive order")
    rank = deficient.get("initial_jacobian_rank")
    if not isinstance(rank, int) or rank >= dimension:
        found.append(f"{label}: the deficient-weights control reaches the dimension")
    if controls["other_basepoint_parametrization"].get("germ_nonzero", 0) <= 0:
        found.append(f"{label}: the parametrization of the other basepoint satisfies the germ ideal")
    return found


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("field") != "Q(i)":
        found.append("the field differs from Q(i)")
    cells = record.get("cells", [])
    if [(cell.get("orbit"), cell.get("source")) for cell in cells] != list(CELLS):
        found.append("the cells are not the four cells in order")
        return found
    for cell in cells:
        orbit, source = cell["orbit"], cell["source"]
        label = f"{source} {orbit}"
        for key, expected in EXPECTED[source].items():
            if cell.get(key) != expected:
                found.append(f"{label}: {key} differs from {expected}")
        if cell.get("parametrization") != list(parametrization(orbit, source)):
            found.append(f"{label}: parametrization differs from the one of the producer")
        functions = cell.get("order_functions")
        if not isinstance(functions, dict) or set(functions) != set(ORDER_FUNCTIONS[source]):
            found.append(f"{label}: the order functions are not those of the producer")
            continue
        for name in ORDER_FUNCTIONS[source]:
            found += _function_problems(label, source, name, functions[name])
        found += _control_problems(label, source, cell)
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice_problems(record: dict[str, Any]) -> list[str]:
    """The relation digests against the Iso and W8 cells over Q(i) of the weight-slice record."""
    retained = {
        (cell["orbit"], cell["source"]): cell["relations_sha256"]
        for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0
    }
    return [
        f"{cell['source']} {cell['orbit']}: the relations differ from those of the weight-slice record"
        for cell in record.get("cells", [])
        if cell.get("relations_sha256") != retained.get((cell["orbit"], cell["source"]))
    ]


def build() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "weight_slice_record_sha256": _digest(WEIGHT_SLICE),
        "cells": parallel.ordered_map(certify, list(CELLS), min_items=2),
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def main() -> None:
    if "--check" in sys.argv[1:]:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = problems(record) + slice_problems(record)
        for name in INPUTS:
            if record["inputs"].get(name) != _digest(HERE / name):
                found.append(f"input digest of {name} differs")
        if record.get("weight_slice_record_sha256") != _digest(WEIGHT_SLICE):
            found.append("digest of the weight-slice record differs")
        if found:
            raise SystemExit("\n".join(found))
        print("iso-w8-relation-ideal-orders-result.json: pass")
        return
    record = build()
    found = problems(record) + slice_problems(record)
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
