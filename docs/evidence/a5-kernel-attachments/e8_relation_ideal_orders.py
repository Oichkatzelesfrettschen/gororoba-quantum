"""The relation ideal of the E8-bar fiber cone on the weight slice equals its quadric ideal: three order functions.

On the weight slice at N- or N+ (`weight_slice_fiber_relations.py`) let O be the local ring of the E8-bar germ at the
origin, m its maximal ideal, I = (G_1, ..., G_21) the Pfaffian ideal, L the relation ideal of the fiber cone
(a form F of degree d lies in L exactly when F(G) lies in m I^d), and K the ideal that the 148 relations of degree 2
generate (each lies in L by the weight-slice producer, A5-421, the one premise this argument takes from it). K has
the minimal primes P5 (dimension 5, degree 11) and P4 (dimension 4, degree 4), radical R = P5 /\\ P4, and the
embedded prime A = K : R (A5-451, A5-454).

A polynomial map phi from the affine space of (pa, pb, pl, pz, pm) to the slice sends the origin to the origin and
satisfies every generator of the germ ideal J, so it induces a ring map from O to the local ring of that affine
space at its origin. A weight vector w on the five parameters gives the order function v_w(x) = (lowest w-weight of
a term of phi^* x, and +infinity for phi^* x = 0). The weights are nonnegative, so the order is additive on products
and at least the minimum on sums, and phi(0) = 0, so a unit of O keeps its nonzero constant term as its part of
weight 0 and has order zero; v_w therefore extends to fractions with unit denominators. With nu = min_a v_w(G_a)
and e = min_k v_w(s_k), every weight vector here has e >= 1, also the one with a zero entry, so every element of
m I^d has order at least d nu + e. The initial forms
V_a (the part of phi^* G_a of weight nu) define the limit ideal Q_w = ker(y_a -> V_a), a homogeneous prime.

Two consequences hold for every w with e >= 1. A form F of L has v_w(F(G)) > deg(F) nu, so F(V) = 0: L lies in Q_w.
A form c with c * l in L, for a linear form l with v_w(l(G)) < nu + e, has v_w(c(G)) > deg(c) nu, so c lies in Q_w.

The producer regenerates the relations at both basepoints and checks over Q(i) in Singular, for three weight
vectors: Q_w = P5 for (1, 1, 2, 1, 2), Q_w = P4 for (1, 1, 1, 1, 0), and Q_w = A for (2, 2, 1, 2, 1), where nu = 4,
e = 2 and each of the five nilpotent linear forms has order 5. Each equality Q_w = P is read from two facts: the
generators of the prime P vanish on V, and the Jacobian matrix of V has rank dim P at a rational point, so the
closure of the image of V is an irreducible subvariety of V(P) of the same dimension (characteristic 0: the
dimension of the closure of the image of a polynomial map is the generic rank of its Jacobian matrix, and the rank
at one point bounds it from below; P is prime, contained in Q_w, and dim S/Q_w >= dim S/P). Two controls run: equal
weights (1, 1, 1, 1, 1) give e = 1 and no order strictly between nu and nu + e, and the parametrization of the other
basepoint leaves generators of J nonzero.

Deduction recorded in the ledger: L lies in P5 /\\ P4 = R, so L / K is a submodule of the torsion-free module R / K
of rank 1 over S / A (A5-454). The class of y6 in R / K is nonzero, since K is generated in degree 2. A nonzero
class of L / K and the class of y6 are dependent over S / A with both coefficients nonzero, which gives c outside A
with c * y6 in L; L, A and y6 are homogeneous, so some homogeneous component of c is outside A with its product
with y6 in L, and the third order function forces every such form into A. Hence L = K, given K inside L.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_relation_ideal_orders.py [--check]
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

import e8_quadric_nilradical as nilradical  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "e8-relation-ideal-orders-result.json"
SCHEMA = "gororoba.a5.e8-relation-ideal-orders/1"
INPUTS = ("e8_relation_ideal_orders.py", "e8_quadric_nilradical.py", "weight_slice_fiber_relations.py")
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
ORBITS = ("N-", "N+")
GENERATORS = 21
PARAMETERS = ("pa", "pb", "pl", "pz", "pm")
# The image of s_1, ..., s_9 under phi. The germ ideal at N+ is the complex conjugate of the one at N- with s_4, s_5
# exchanged and s_7, s_8 exchanged, and so is the map.
PARAMETRIZATION: dict[str, tuple[str, ...]] = {
    "N-": (
        "pa",
        "pz",
        "pl*pa",
        "pl*pm",
        "pl*(2*pz+(-i)*(pm^2)/8)",
        "pb",
        "(i)*pl^2",
        "pl^2*(-pz+(i)*(pm^2)/8)",
        "-pl*pb",
    ),
    "N+": (
        "pa",
        "pz",
        "pl*pa",
        "pl*(2*pz+(i)*(pm^2)/8)",
        "pl*pm",
        "pb",
        "pl^2*(-pz+(-i)*(pm^2)/8)",
        "(-i)*pl^2",
        "-pl*pb",
    ),
}
# Weight vector on (pa, pb, pl, pz, pm), the associated prime of K that its limit ideal equals, and a second
# associated prime that does not contain the first: its generators stay nonzero on the initial forms, which shows
# that the substitution distinguishes the primes.
ORDER_FUNCTIONS: dict[str, tuple[tuple[int, ...], str, str]] = {
    "prime5": ((1, 1, 2, 1, 2), "P5", "P4"),
    "prime4": ((1, 1, 1, 1, 0), "P4", "A"),
    "embedded": ((2, 2, 1, 2, 1), "A", "P4"),
}
EQUAL_WEIGHTS = (1, 1, 1, 1, 1)
RANK_POINT = (2, 3, 5, 7, 11)
EXPECTED: dict[str, Any] = {
    "ideal": [5, 11, 148],
    "minimal_primes": [[4, 4], [5, 11]],
    "radical_linear_forms": 5,
    "annihilator": [4, 2],
    "annihilator_is_prime": True,
    "germ_nonzero_on_parametrization": 0,
}
EXPECTED_ORDERS: dict[str, dict[str, Any]] = {
    "prime5": {"weights": [1, 1, 2, 1, 2], "ideal_order": 5, "maximal_ideal_order": 1, "target": [5, 11]},
    "prime4": {"weights": [1, 1, 1, 1, 0], "ideal_order": 2, "maximal_ideal_order": 1, "target": [4, 4]},
    "embedded": {"weights": [2, 2, 1, 2, 1], "ideal_order": 4, "maximal_ideal_order": 2, "target": [4, 2]},
}

HEAD = Template("""
matrix SM=matrix(S); int nrel=ncols(SM); int nprod=nrows(SM); ideal mxr=maxideal(1);
intmat IXM[nprod][2]; for(a=1;a<=nprod;a++){ IXM[a,1]=IX[a][1]; IXM[a,2]=IX[a][2]; }
ring Y=(0,i),(y(1..$generators)),dp; minpoly=i^2+1; option(redSB);
matrix SM=fetch(r,SM); ideal K; poly q; int u1; int u2;
for(u1=1;u1<=nrel;u1++){ q=0;
  for(u2=1;u2<=nprod;u2++){ if(SM[u2,u1]!=0){ q=q+SM[u2,u1]*y(IXM[u2,1])*y(IXM[u2,2]); } } K[u1]=q; }
ideal sK=std(K); print("RESULT ideal "+string(dim(sK))+","+string(mult(sK))+","+string(size(K)));
list MP=minAssGTZ(K); ideal R=1; ideal P5; ideal P4; ideal component;
for(k=1;k<=size(MP);k++){ component=std(MP[k]);
  print("RESULT prime "+string(dim(component))+","+string(mult(component)));
  if(dim(component)==5){ P5=component; } else { P4=component; } R=intersect(R,MP[k]); }
ideal N=minbase(R); ideal lin;
for(k=1;k<=size(N);k++){ if(deg(N[k])==1){ lin=lin,N[k]; } } lin=simplify(lin,2);
print("RESULT radical_linear_forms "+string(size(lin)));
for(k=1;k<=size(lin);k++){ print("RESULT linear_form "+string(lin[k])); }
ideal A=std(quotient(K,R)); print("RESULT annihilator "+string(dim(A))+","+string(mult(A)));
list LA=minAssGTZ(A); ideal RA=1; for(k=1;k<=size(LA);k++){ RA=intersect(RA,LA[k]); }
print("RESULT annihilator_is_prime "+string(size(LA)==1 and size(reduce(RA,A))==0));
print("RESULT target.P5 "+string(dim(P5))+","+string(mult(P5)));
print("RESULT target.P4 "+string(dim(P4))+","+string(mult(P4)));
print("RESULT target.A "+string(dim(A))+","+string(mult(A)));
ring P=(0,i),($parameters),dp; minpoly=i^2+1; option(redSB);
proc vmin(poly f, intvec wv){ if(f==0){return(-1);} int dd=0; while(jet(f,dd,wv)==0){dd++;} return(dd); }
map ph=r,$mapping;
ideal JP=ph(J); print("RESULT germ_nonzero_on_parametrization "+string(size(simplify(JP,2))));
map other=r,$other_mapping;
ideal JO=other(J); print("RESULT germ_nonzero_on_other_parametrization "+string(size(simplify(JO,2))));
ideal gp=ph(G); ideal sp=ph(mxr); map ev=Y,gp; ideal lp=ev(lin);
intvec wv; int nu; int e; int dd; string orders; ideal V; matrix JN; ideal TV;
""")

ORDER_BLOCK = Template("""
wv=$weights; nu=vmin(gp[1],wv); e=vmin(sp[1],wv); orders="";
for(k=1;k<=$generators;k++){ dd=vmin(gp[k],wv); if(dd<nu){nu=dd;} orders=orders+string(dd)+","; }
for(k=1;k<=9;k++){ dd=vmin(sp[k],wv); if(dd<e){e=dd;} }
print("RESULT $name.generator_orders "+orders);
print("RESULT $name.ideal_order "+string(nu));
print("RESULT $name.maximal_ideal_order "+string(e));
orders=""; for(k=1;k<=size(lp);k++){ orders=orders+string(vmin(lp[k],wv))+","; }
print("RESULT $name.nilpotent_orders "+orders);
$target_block
""")

TARGET_BLOCK = Template("""V=0; for(k=1;k<=$generators;k++){ V[k]=jet(gp[k],nu,wv); }
map ev_$name=Y,V; TV=ev_$name($target);
print("RESULT $name.target_nonzero_on_initial_forms "+string(size(simplify(TV,2))));
TV=ev_$name($other);
print("RESULT $name.other_prime_nonzero_on_initial_forms "+string(size(simplify(TV,2))));
JN=subst(jacob(V),$point); print("RESULT $name.initial_jacobian_rank "+string(rank(JN)));
""")


def _weights(weights: tuple[int, ...]) -> str:
    return ",".join(str(weight) for weight in weights)


def order_stage(orbit: str) -> str:
    """The Singular statements appended to the weight-slice script of one basepoint."""
    other = next(name for name in ORBITS if name != orbit)
    point = ",".join(f"{name},{value}" for name, value in zip(PARAMETERS, RANK_POINT, strict=True))
    stage = HEAD.substitute(
        generators=GENERATORS,
        parameters=",".join(PARAMETERS),
        mapping=",".join(PARAMETRIZATION[orbit]),
        other_mapping=",".join(PARAMETRIZATION[other]),
    )
    for name, (weights, target, other_prime) in ORDER_FUNCTIONS.items():
        block = TARGET_BLOCK.substitute(name=name, target=target, other=other_prime, generators=GENERATORS, point=point)
        stage += ORDER_BLOCK.substitute(name=name, weights=_weights(weights), generators=GENERATORS, target_block=block)
    stage += ORDER_BLOCK.substitute(
        name="equal", weights=_weights(EQUAL_WEIGHTS), generators=GENERATORS, target_block=""
    )
    return stage


def _integers(text: str) -> list[int]:
    return [int(part) for part in text.split(",") if part != ""]


def strictly_between(orders: list[int], ideal_order: int, maximal_ideal_order: int) -> bool:
    """Whether every order lies strictly between nu and nu + e; such a form lies outside m I and is not a unit of I."""
    return orders != [] and all(ideal_order < order < ideal_order + maximal_ideal_order for order in orders)


def _order_record(values: dict[str, list[str]], name: str, target: str | None) -> dict[str, Any]:
    found: dict[str, Any] = {
        "generator_orders": _integers(values[f"{name}.generator_orders"][0]),
        "ideal_order": int(values[f"{name}.ideal_order"][0]),
        "maximal_ideal_order": int(values[f"{name}.maximal_ideal_order"][0]),
        "nilpotent_orders": _integers(values[f"{name}.nilpotent_orders"][0]),
    }
    if target is not None:
        found["target"] = _integers(values[f"target.{target}"][0])
        found["target_nonzero_on_initial_forms"] = int(values[f"{name}.target_nonzero_on_initial_forms"][0])
        found["other_prime_nonzero_on_initial_forms"] = int(values[f"{name}.other_prime_nonzero_on_initial_forms"][0])
        found["initial_jacobian_rank"] = int(values[f"{name}.initial_jacobian_rank"][0])
    return found


def certify(orbit: str) -> dict[str, Any]:
    marker = 'print("RESULT done 1");'
    script = ws.fiber_script(ws.orbit_task(orbit), "e8", 0, 0)
    if script.count(marker) != 1:
        raise RuntimeError("the weight-slice script has no single end marker")
    run = ws.run_singular(script.replace(marker, order_stage(orbit) + marker))
    values = run["values"]
    functions = {}
    for name, (weights, target, _) in ORDER_FUNCTIONS.items():
        functions[name] = {"weights": list(weights), **_order_record(values, name, target)}
    return {
        "orbit": orbit,
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "parametrization": list(PARAMETRIZATION[orbit]),
        "ideal": _integers(values["ideal"][0]),
        "minimal_primes": sorted(_integers(text) for text in values["prime"]),
        "radical_linear_forms": int(values["radical_linear_forms"][0]),
        "linear_forms": list(values["linear_form"]),
        "annihilator": _integers(values["annihilator"][0]),
        "annihilator_is_prime": values["annihilator_is_prime"] == ["1"],
        "germ_nonzero_on_parametrization": int(values["germ_nonzero_on_parametrization"][0]),
        "order_functions": functions,
        "controls": {
            "equal_weights": {"weights": list(EQUAL_WEIGHTS), **_order_record(values, "equal", None)},
            "other_basepoint_parametrization": {
                "germ_nonzero": int(values["germ_nonzero_on_other_parametrization"][0])
            },
        },
    }


def _function_problems(orbit: str, name: str, function: Any) -> list[str]:
    if not isinstance(function, dict):
        return [f"{orbit}: the order function {name} is missing"]
    found = [
        f"{orbit}: {name} {key} differs from {expected}"
        for key, expected in EXPECTED_ORDERS[name].items()
        if function.get(key) != expected
    ]
    orders = function.get("generator_orders")
    if not isinstance(orders, list) or len(orders) != GENERATORS or min(orders) != function.get("ideal_order"):
        found.append(f"{orbit}: {name} generator orders do not have the ideal order as their minimum")
    if function.get("target_nonzero_on_initial_forms") != 0:
        found.append(f"{orbit}: {name} target prime does not vanish on the initial forms")
    if function.get("other_prime_nonzero_on_initial_forms", 0) <= 0:
        found.append(f"{orbit}: {name} other prime vanishes on the initial forms")
    if function.get("initial_jacobian_rank") != EXPECTED_ORDERS[name]["target"][0]:
        found.append(f"{orbit}: {name} initial_jacobian_rank differs from the dimension of the target prime")
    return found


def _control_problems(cell: dict[str, Any]) -> list[str]:
    orbit = cell["orbit"]
    controls = cell.get("controls")
    if not isinstance(controls, dict) or set(controls) != {"equal_weights", "other_basepoint_parametrization"}:
        return [f"{orbit}: the controls are missing"]
    found: list[str] = []
    equal = controls["equal_weights"]
    if equal.get("weights") != list(EQUAL_WEIGHTS):
        found.append(f"{orbit}: the equal-weights control has other weights")
    if strictly_between(
        list(equal.get("nilpotent_orders", [])), equal.get("ideal_order", 0), equal.get("maximal_ideal_order", 0)
    ):
        found.append(f"{orbit}: the equal-weights control separates the nilpotent forms")
    if controls["other_basepoint_parametrization"].get("germ_nonzero", 0) <= 0:
        found.append(f"{orbit}: the parametrization of the other basepoint satisfies the germ ideal")
    return found


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("field") != "Q(i)":
        found.append("the field differs from Q(i)")
    cells = record.get("cells", [])
    if [cell.get("orbit") for cell in cells] != list(ORBITS):
        found.append("the cells are not N- and N+ in order")
        return found
    for cell in cells:
        orbit = cell["orbit"]
        for key, expected in EXPECTED.items():
            if cell.get(key) != expected:
                found.append(f"{orbit}: {key} differs from {expected}")
        if cell.get("parametrization") != list(PARAMETRIZATION[orbit]):
            found.append(f"{orbit}: parametrization differs from the one of the producer")
        if len(cell.get("linear_forms", [])) != cell.get("radical_linear_forms"):
            found.append(f"{orbit}: the linear forms listed differ in number from the count")
        if sorted(cell.get("linear_forms", [])) != sorted(nilradical.LINEAR_FORMS[orbit]):
            found.append(f"{orbit}: the linear forms differ from the five nilpotent forms")
        functions = cell.get("order_functions")
        if not isinstance(functions, dict) or set(functions) != set(ORDER_FUNCTIONS):
            found.append(f"{orbit}: the order functions are not the three of the producer")
            continue
        for name in ORDER_FUNCTIONS:
            found += _function_problems(orbit, name, functions[name])
        embedded = functions["embedded"]
        if isinstance(embedded, dict):
            orders = list(embedded.get("nilpotent_orders", []))
            between = strictly_between(orders, embedded.get("ideal_order", 0), embedded.get("maximal_ideal_order", 0))
            if len(orders) != cell.get("radical_linear_forms") or not between:
                found.append(f"{orbit}: embedded nilpotent_orders are not strictly between nu and nu + e")
        found += _control_problems(cell)
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice_problems(record: dict[str, Any]) -> list[str]:
    """The relation digests against the E8-bar cells over Q(i) of the weight-slice record."""
    retained = {
        cell["orbit"]: cell["relations_sha256"]
        for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0 and cell["source"] == "e8"
    }
    return [
        f"{cell['orbit']}: the relations differ from those of the weight-slice record"
        for cell in record.get("cells", [])
        if cell.get("relations_sha256") != retained.get(cell["orbit"])
    ]


def build() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "weight_slice_record_sha256": _digest(WEIGHT_SLICE),
        "cells": parallel.ordered_map(certify, list(ORBITS), min_items=2),
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
        print("e8-relation-ideal-orders-result.json: pass")
        return
    record = build()
    found = problems(record) + slice_problems(record)
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
