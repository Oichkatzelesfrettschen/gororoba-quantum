"""The nilradical of the E8-bar quadric ideal over Q(i) on the weight slice: five linear forms of square zero.

The quadric ideal K of E8-bar (148 quadrics on 21 generators, `weight_slice_fiber_relations.py`) is not radical
(A5-447). This producer regenerates the quadrics at N- and N+ and computes over Q(i) in Singular: the radical R of K
as the intersection of the minimal primes from minAssGTZ, the linear forms among its minimal generators, whether
R = K + (those linear forms), whether R^2 lies in K, the annihilator A = K : R of the nilradical R / K, whether A is
prime (one minimal prime from minAssGTZ and A equal to its radical), the first Hilbert series numerators of S/K, S/R
and S/A, whether R / K has the Hilbert function of S / A in degrees 1..12, and the primary decomposition of K from
primdecGTZ.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_quadric_nilradical.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "e8-quadric-nilradical-result.json"
SCHEMA = "gororoba.a5.e8-quadric-nilradical/2"
INPUTS = ("e8_quadric_nilradical.py", "weight_slice_fiber_relations.py")
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
ORBITS = ("N-", "N+")
GENERATORS = 21
HILBERT_DEGREES = range(1, 13)
# What every cell holds: the radical, its linear forms, the annihilator of the nilradical and its primality, the
# Hilbert functions of S/K, S/R, S/A in degrees 1..12 (their difference is that of S/A: R/K is torsion free of rank 1
# over the domain S/A), the primary components as (dimension, degree of the prime, degree of the primary ideal,
# whether the component is prime), sorted.
EXPECTED: dict[str, Any] = {
    "ideal": [5, 11],
    "minimal_primes": [[4, 4], [5, 11]],
    "radical": [5, 11],
    "radical_linear_forms": 5,
    "radical_is_ideal_plus_linear_forms": True,
    "radical_square_in_ideal": True,
    "linear_forms_square_in_ideal": True,
    "annihilator": [4, 2],
    "annihilator_generator_degrees": [1] * 16 + [2],
    "annihilator_minimal_primes": 1,
    "annihilator_is_radical": True,
    "annihilator_is_prime": True,
    "hilbert_function": {
        "ideal": [21, 83, 225, 495, 952, 1666, 2718, 4200, 6215, 8877, 12311, 16653],
        "radical": [16, 69, 195, 440, 861, 1526, 2514, 3915, 5830, 8371, 11661, 15834],
        "annihilator": [5, 14, 30, 55, 91, 140, 204, 285, 385, 506, 650, 819],
    },
    "nilradical_module_hilbert_function_is_that_of_annihilator_quotient": True,
    "primary_components": [[4, 2, 4, False], [4, 4, 4, True], [5, 11, 11, True]],
}
SCRIPT = """LIB "primdec.lib"; option(redSB);
ideal sK=std(K); print("RESULT ideal "+string(dim(sK))+","+string(mult(sK)));
list L=minAssGTZ(K); int k; ideal R=1; ideal component;
for(k=1;k<=size(L);k++){ component=std(L[k]); print("RESULT prime "+string(dim(component))+","+string(mult(component)));
  R=intersect(R,L[k]); }
ideal sR=std(R); print("RESULT radical "+string(dim(sR))+","+string(mult(sR)));
ideal N=minbase(R); ideal lin;
for(k=1;k<=size(N);k++){ if(deg(N[k])==1){ lin=lin,N[k]; } } lin=simplify(lin,2);
print("RESULT radical_linear_forms "+string(size(lin)));
for(k=1;k<=size(lin);k++){ print("RESULT linear_form "+string(lin[k])); }
print("RESULT radical_is_ideal_plus_linear_forms "+string(size(reduce(R,std(K+lin)))==0));
print("RESULT radical_square_in_ideal "+string(size(reduce(R*R,sK))==0));
print("RESULT linear_forms_square_in_ideal "+string(size(reduce(lin*lin,sK))==0));
ideal A=std(quotient(K,R)); print("RESULT annihilator "+string(dim(A))+","+string(mult(A)));
ideal mA=minbase(A); intvec da; for(k=1;k<=size(mA);k++){ da[k]=deg(mA[k]); }
print("RESULT annihilator_generator_degrees "+string(da));
list LA=minAssGTZ(A); ideal RA=1; for(k=1;k<=size(LA);k++){ RA=intersect(RA,LA[k]); }
print("RESULT annihilator_minimal_primes "+string(size(LA)));
print("RESULT annihilator_is_radical "+string(size(reduce(RA,A))==0));
print("RESULT hilbert_numerator_ideal "+string(hilb(sK,1)));
print("RESULT hilbert_numerator_radical "+string(hilb(sR,1)));
print("RESULT hilbert_numerator_annihilator "+string(hilb(A,1)));
list PD=primdecGTZ(K); ideal primary;
for(k=1;k<=size(PD);k++){ component=std(PD[k][2]); primary=std(PD[k][1]);
  print("RESULT primary "+string(dim(component))+","+string(mult(component))+","+string(mult(primary))+","
    +string(size(reduce(component,primary))==0)); }
print("RESULT done 1");
quit;
"""


def _module_function(functions: dict[str, list[int]]) -> list[int]:
    """Dimensions of R / K by degree: those of S/K minus those of S/R."""
    return [whole - quotient for whole, quotient in zip(functions["ideal"], functions["radical"], strict=True)]


def _pair(text: str) -> list[int]:
    return [int(part) for part in text.split(",")]


def hilbert_function(numerator: list[int]) -> list[int]:
    """Dimensions in degrees 1..12 of a quotient of the 21-variable polynomial ring from its first Hilbert numerator."""
    return [
        sum(
            coefficient * math.comb(degree - shift + GENERATORS - 1, GENERATORS - 1)
            for shift, coefficient in enumerate(numerator)
            if shift <= degree
        )
        for degree in HILBERT_DEGREES
    ]


def certify(orbit: str) -> dict[str, Any]:
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), "e8", 0, 0))
    polynomials = ",\n".join(
        "+".join(f"({coefficient})*{'*'.join(f'y({index})' for index in key)}" for key, coefficient in relation)
        for relation in (ws.parse_relation(line) for line in run["relations"])
    )
    script = ws._ring(0, 0, f"y(1..{GENERATORS})", "dp") + f"\nideal K={polynomials};\n" + SCRIPT
    values = ws.run_singular(script)["values"]
    # Singular ends the first Hilbert series with a marker entry that is not a coefficient.
    numerators = {
        name: _pair(values[f"hilbert_numerator_{name}"][0])[:-1] for name in ("ideal", "radical", "annihilator")
    }
    functions = {name: hilbert_function(numerator) for name, numerator in numerators.items()}
    return {
        "orbit": orbit,
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "ideal": _pair(values["ideal"][0]),
        "minimal_primes": sorted(_pair(text) for text in values["prime"]),
        "radical": _pair(values["radical"][0]),
        "radical_linear_forms": int(values["radical_linear_forms"][0]),
        "linear_forms": list(values["linear_form"]),
        "radical_is_ideal_plus_linear_forms": values["radical_is_ideal_plus_linear_forms"] == ["1"],
        "radical_square_in_ideal": values["radical_square_in_ideal"] == ["1"],
        "linear_forms_square_in_ideal": values["linear_forms_square_in_ideal"] == ["1"],
        "annihilator": _pair(values["annihilator"][0]),
        "annihilator_generator_degrees": sorted(_pair(values["annihilator_generator_degrees"][0])),
        "annihilator_minimal_primes": int(values["annihilator_minimal_primes"][0]),
        "annihilator_is_radical": values["annihilator_is_radical"] == ["1"],
        "annihilator_is_prime": (
            int(values["annihilator_minimal_primes"][0]) == 1 and values["annihilator_is_radical"] == ["1"]
        ),
        "hilbert_numerator": numerators,
        "hilbert_function": functions,
        "nilradical_module_hilbert_function_is_that_of_annihilator_quotient": _module_function(functions)
        == functions["annihilator"],
        "primary_components": sorted(
            [*parts[:3], bool(parts[3])] for parts in (_pair(text) for text in values["primary"])
        ),
    }


def _hilbert_problems(cell: dict[str, Any]) -> list[str]:
    """The recorded numerators against the recorded Hilbert functions and the claim that R / K shares that of S/A."""
    orbit = cell["orbit"]
    numerators = cell.get("hilbert_numerator")
    functions = cell.get("hilbert_function")
    if not isinstance(numerators, dict) or not isinstance(functions, dict):
        return [f"{orbit}: the Hilbert numerators or functions are missing"]
    found: list[str] = []
    for name in ("ideal", "radical", "annihilator"):
        numerator = numerators.get(name)
        derived = hilbert_function(numerator) if isinstance(numerator, list) else None
        if derived != functions.get(name):
            found.append(f"{orbit}: the Hilbert function of {name} differs from that of its numerator")
    if functions.keys() == EXPECTED["hilbert_function"].keys() and all(
        isinstance(values, list) and len(values) == len(HILBERT_DEGREES) for values in functions.values()
    ):
        shared = _module_function(functions) == functions["annihilator"]
        if cell.get("nilradical_module_hilbert_function_is_that_of_annihilator_quotient") is not shared:
            found.append(f"{orbit}: the module Hilbert flag differs from the recorded Hilbert functions")
    if not found and not module_series_is_that_of_the_irrelevant_ideal(numerators):
        found.append(f"{orbit}: the numerators of S/K and S/R do not differ by that of the irrelevant ideal of S/A")
    return found


def module_series_is_that_of_the_irrelevant_ideal(numerators: dict[str, list[int]]) -> bool:
    """Whether dim (R/K)_d = dim (S/A)_d in every degree d >= 1, read from the three first Hilbert numerators.

    The Hilbert series are N / (1 - t)^21, and the series of R/K is that of S/K minus that of S/R. It equals the
    series of S/A without its constant term exactly when N_K - N_R = N_A - (1 - t)^21.
    """
    length = GENERATORS + 1
    if any(len(numerators[name]) > length for name in ("ideal", "radical", "annihilator")):
        return False
    padded = {name: [*values, *[0] * (length - len(values))] for name, values in numerators.items()}
    unit = [(-1) ** power * math.comb(GENERATORS, power) for power in range(length)]
    return all(
        padded["ideal"][power] - padded["radical"][power] == padded["annihilator"][power] - unit[power]
        for power in range(length)
    )


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
        for key, expected in EXPECTED.items():
            if cell.get(key) != expected:
                found.append(f"{cell['orbit']}: {key} differs from {expected}")
        if len(cell.get("linear_forms", [])) != cell.get("radical_linear_forms"):
            found.append(f"{cell['orbit']}: the linear forms listed differ in number from the count")
        found += _hilbert_problems(cell)
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
        print("e8-quadric-nilradical-result.json: pass")
        return
    record = build()
    found = problems(record) + slice_problems(record)
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
