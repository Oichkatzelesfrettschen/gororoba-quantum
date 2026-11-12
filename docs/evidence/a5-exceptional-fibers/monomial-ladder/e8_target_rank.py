"""Exact truncated ranks of (sqrt(K2)/K2)_d on the E8 exceptional fiber.

The retained arc certificates give K2 <= L <= sqrt(K2), with L the fiber
cone's defining ideal. Consequently h_d = HF(S/sqrt(K2), d) + rank(phi),
where phi sends a class in (sqrt(K2)/K2)_d to its value on G in I^d/m_R I^d.
Truncation gives rank(phi_N) <= rank(phi). This runner retains the FULL
m_R I^d closure and evaluates only the target numerator. A zero truncated
image does not prove exact membership. Matching the K2 upper bound certifies
one degree over the selected finite field, without a characteristic-zero claim.

``prepare`` exports standard monomials and radical normal forms in Singular
with global dp order, then computes their coefficient kernel with python-flint.
``run`` uses the unchanged e8_ladder quadratic algebra and closure propagation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from flint import fmpz, nmod_mat, nmod_mpoly, nmod_mpoly_ctx

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = EVIDENCE.parents[2]
sys.path.insert(0, str(EVIDENCE / "arcs"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import arc_targets as targets  # noqa: E402

import parallel  # noqa: E402

BASIS_SCHEMA = "a5-e8-nilpotent-target-basis-v1"
RANK_SCHEMA = "a5-e8-nilpotent-target-rank-v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_digest(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "payload_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def save_record(path: Path, record: dict[str, Any]) -> None:
    record["payload_sha256"] = payload_digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    temporary.replace(path)


def membership_inputs(target: targets.Target, witnesses: list[dict[str, Any]]) -> list[Path]:
    """Bind exact K2 membership, using the retained sign transport when necessary."""
    relative = (ROOT / target.k2_relations).relative_to(EVIDENCE).as_posix()
    matches = [
        row
        for row in witnesses
        if row.get("kind") == "k2-span"
        and row.get("fiber") == target.fiber
        and row.get("prime") == target.prime
        and row.get("k2_source") == relative
    ]
    if not matches:
        partner = targets.minus_partner(target)
        transports = [
            row
            for row in witnesses
            if row.get("kind") == "sign-isomorphism"
            and row.get("prime") == target.prime
            and row.get("to") == target.fiber
            and row.get("k2_to") == relative
        ]
        if partner is None or len(transports) != 1:
            raise ValueError("no unique exact K2 membership or sign-transport receipt")
        transport = transports[0]
        if (
            transport.get("ok") is not True
            or transport.get("k2_mutual_remainders") != [0, 0]
            or transport.get("from") != partner.fiber
            or transport.get("k2_from") != (ROOT / partner.k2_relations).relative_to(EVIDENCE).as_posix()
            or transport.get("k2_to_sha256") != digest(ROOT / target.k2_relations)
            or transport.get("k2_from_sha256") != digest(ROOT / partner.k2_relations)
        ):
            raise ValueError("invalid K2 sign transport")
        targets.check_generator_order(partner)
        return [
            ROOT / partner.header,
            ROOT / partner.generators,
            ROOT / partner.k2_relations,
            *membership_inputs(partner, witnesses),
        ]
    if len(matches) != 1:
        raise ValueError("no unique exact K2 membership receipt")
    witness = matches[0]
    receipt_path = EVIDENCE / witness["receipt"]
    relations = EVIDENCE / witness["receipt_relations"]
    receipt = json.loads(receipt_path.read_text())
    if (
        witness.get("ok") is not True
        or witness.get("mutual_remainders") != [0, 0]
        or witness.get("k2_source_sha256") != digest(ROOT / target.k2_relations)
        or witness.get("receipt_relations_sha256") != digest(relations)
        or receipt.get("status") != "degree-certified"
        or receipt.get("degree") != 2
        or receipt.get("prime") != target.prime
        or int(receipt.get("root_of_minus_one", -1)) != target.root
        or receipt.get("generator_count") != targets.NGEN
        or receipt.get("generator_order_sha256") != digest(ROOT / target.generators)
        or receipt.get("input_sha256") != digest(ROOT / target.header)
        or receipt.get("relation_sha256") != digest(relations)
        or receipt.get("relation_count") != 148
        or receipt.get("membership_check") != {"checked": 148, "failures": 0}
    ):
        raise ValueError("invalid exact K2 membership receipt")
    return [receipt_path, relations]


def bound_inputs(target: targets.Target) -> dict[str, str]:
    """Bind the ordered G, K2 and retained arc premises; do not replay those proofs."""
    targets.k2_ideal(target)
    targets.check_generator_order(target)
    witnesses = [json.loads(line) for line in (EVIDENCE / "witnesses.jsonl").read_text().splitlines()]
    for name, rank, component in (("result.json", 4, "P2"), ("result_P1.json", 5, "P1")):
        receipt = json.loads((target.directory / name).read_text())
        if (
            receipt.get("certified") is not True
            or receipt.get("jacobian_rank") != rank
            or receipt.get("component") != component
            or receipt.get("fiber") != target.fiber
            or receipt.get("field") != f"F_{target.prime}, i = {target.root}"
        ):
            raise ValueError(f"{target.name}: incompatible retained arc certificate {name}")
    paths = [
        ROOT / target.header,
        ROOT / target.generators,
        ROOT / target.k2_relations,
        EVIDENCE / "k2-hilbert.jsonl",
        EVIDENCE / "witnesses.jsonl",
        EVIDENCE / "arcs" / "arc_targets.py",
        *membership_inputs(target, witnesses),
        *(
            target.directory / name
            for name in ("P1.txt", "P2.txt", "result.json", "result_P1.json", "campaign_summary.json")
        ),
    ]
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}


def parse_polynomial(text: str, context: Any) -> Any:
    return nmod_mpoly(re.sub(r"y\((\d+)\)", r"y\1", text.strip()), context)


def encode_polynomial(polynomial: Any) -> list[list[Any]]:
    return [[[int(e) for e in exponent], int(value)] for exponent, value in sorted(polynomial.to_dict().items())]


def decode_polynomial(terms: list[list[Any]], context: Any, degree: int, nvars: int, prime: int) -> Any:
    coefficients: dict[tuple[int, ...], int] = {}
    for exponent, value in terms:
        if (
            len(exponent) != nvars
            or any(type(item) is not int or item < 0 for item in exponent)
            or sum(exponent) != degree
            or type(value) is not int
            or not 0 < value < prime
            or tuple(exponent) in coefficients
        ):
            raise ValueError("noncanonical or nonhomogeneous polynomial terms")
        coefficients[tuple(exponent)] = value
    return context.from_dict(coefficients)


def coefficient_matrix(polynomials: list[Any], prime: int) -> Any:
    columns = sorted({tuple(exponent) for polynomial in polynomials for exponent in polynomial.to_dict()})
    index = {exponent: j for j, exponent in enumerate(columns)}
    matrix = nmod_mat(len(polynomials), len(columns), prime)
    for i, polynomial in enumerate(polynomials):
        for exponent, value in polynomial.to_dict().items():
            matrix[i, index[tuple(exponent)]] = int(value)
    return matrix


def kernel_rows(normal_forms: list[Any], prime: int) -> list[list[list[int]]]:
    """A joint coefficient kernel, not independent yes/no tests of monomials."""
    matrix = coefficient_matrix(normal_forms, prime)
    kernel, nullity = matrix.transpose().nullspace()
    return [[[i, int(kernel[i, j])] for i in range(len(normal_forms)) if kernel[i, j]] for j in range(nullity)]


def singular_script(target: targets.Target, degree: int) -> str:
    p1, p2, k2 = targets.load_primes(target)
    return f"""// Global-order export for the nilpotent target coefficient kernel.
ring r={target.prime},(y(1..{targets.NGEN})),dp;
short=0; option(redSB);
ideal K={k2};
ideal P1={p1.rstrip(";")};
ideal P2={p2.rstrip(";")};
ideal Kstd=std(K);
ideal Rstd=std(intersect(P1,P2));
print("TARGET_INCLUSION "+string(size(reduce(Kstd,Rstd))));
ideal B=kbase(Kstd,{degree});
print("TARGET_SIZE "+string(size(B)));
for(int j=1;j<=size(B);j++){{
  print("TARGET_B "+string(j)+" "+string(B[j]));
  print("TARGET_N "+string(j)+" "+string(reduce(B[j],Rstd)));
}}
print("TARGET_DONE");
exit;
"""


def read_export(output: str, prime: int, nvars: int) -> tuple[list[list[int]], list[Any]]:
    lines = output.splitlines()
    if any(line.lstrip().startswith("?") for line in lines) or "TARGET_DONE" not in lines:
        raise ValueError("Singular export has errors or no completion marker")
    if [line for line in lines if line.startswith("TARGET_INCLUSION ")] != ["TARGET_INCLUSION 0"]:
        raise ValueError("K2 is not contained in the retained component intersection")
    sizes = [int(line.split()[1]) for line in lines if line.startswith("TARGET_SIZE ")]
    if len(sizes) != 1:
        raise ValueError("Singular export has no unique basis size")
    context = nmod_mpoly_ctx.get(tuple(f"y{i + 1}" for i in range(nvars)), modulus=prime)
    basis: list[Any] = []
    normal: list[Any] = []
    for marker, destination in (("TARGET_B ", basis), ("TARGET_N ", normal)):
        for line in lines:
            if line.startswith(marker):
                _, index, polynomial = line.split(maxsplit=2)
                if int(index) != len(destination) + 1:
                    raise ValueError("Singular export has missing or reordered basis rows")
                destination.append(parse_polynomial(polynomial, context))
        if len(destination) != sizes[0]:
            raise ValueError("Singular export row count differs from its basis size")
    monomials = []
    for polynomial in basis:
        terms = polynomial.to_dict()
        if len(terms) != 1 or list(terms.values()) != [1]:
            raise ValueError("kbase export contains a nonmonomial")
        monomials.append([int(e) for e in next(iter(terms))])
    return monomials, normal


def validate_basis(record: dict[str, Any]) -> None:
    if record.get("schema") != BASIS_SCHEMA or record.get("payload_sha256") != payload_digest(record):
        raise ValueError("target basis schema or payload digest differs")
    prime, degree, nvars = record["prime"], record["degree"], record["nvars"]
    if any(type(value) is not int for value in (prime, degree, nvars)):
        raise ValueError("field, degree and variable count must be integers")
    if prime <= 2 or not fmpz(prime).is_prime() or degree < 1 or nvars < 1:
        raise ValueError("invalid field, degree or variable count")
    monomials = record["monomials"]
    if len({tuple(exponent) for exponent in monomials}) != len(monomials):
        raise ValueError("repeated standard monomial")
    for exponent in monomials:
        if len(exponent) != nvars or any(type(e) is not int or e < 0 for e in exponent) or sum(exponent) != degree:
            raise ValueError("invalid standard monomial")
    context = nmod_mpoly_ctx.get(tuple(f"y{i + 1}" for i in range(nvars)), modulus=prime)
    normal = [decode_polynomial(terms, context, degree, nvars, prime) for terms in record["radical_normal_forms"]]
    if len(normal) != len(monomials):
        raise ValueError("normal form and monomial dimensions differ")
    matrix = coefficient_matrix(normal, prime)
    rows = record["target_rows"]
    coefficients = nmod_mat(len(rows), len(monomials), prime)
    for i, row in enumerate(rows):
        seen = set()
        for j, value in row:
            if type(j) is not int or not 0 <= j < len(monomials) or j in seen:
                raise ValueError("invalid target column")
            if type(value) is not int or not 0 < value < prime:
                raise ValueError("invalid target coefficient")
            seen.add(j)
            coefficients[i, j] = value
    base, upper, size = record["base_dimension"], record["upper_dimension"], record["target_dimension"]
    if any(type(value) is not int for value in (base, upper, size)):
        raise ValueError("dimensions must be integers")
    if (
        upper != len(monomials)
        or base != matrix.rank()
        or size != len(rows)
        or size != upper - base
        or coefficients.rank() != size
        or coefficients * matrix != nmod_mat(size, matrix.ncols(), prime)
    ):
        raise ValueError("target rows do not form the claimed radical-normal-form kernel")


def export_basis(
    target: targets.Target, degree: int, singular: str, timeout: int, output: Path
) -> tuple[list[list[int]], list[Any], dict[str, Any]]:
    if timeout < 1:
        raise ValueError("Singular timeout must be positive")
    output.parent.mkdir(parents=True, exist_ok=True)
    script, log = output.with_suffix(".sing"), output.with_suffix(".singular.log")
    script.write_text(singular_script(target, degree))
    version = subprocess.run(
        [singular, "-q", "--no-rc", "--dump-versiontuple"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=min(timeout, 10),
        check=True,
    ).stdout.strip()
    with log.open("w") as stream:
        subprocess.run(
            [singular, "-q", "--no-rc", "--cpus=1", "--threads=1", "--flint-threads=1", str(script.resolve())],
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=True,
        )
    monomials, normal = read_export(log.read_text(), target.prime, targets.NGEN)
    return (
        monomials,
        normal,
        {
            "export_script_sha256": digest(script),
            "export_log_sha256": digest(log),
            "singular": version,
        },
    )


def verify_export(record: dict[str, Any], singular: str, timeout: int, output: Path) -> dict[str, Any]:
    """Re-establish the map from retained ideals; a payload hash alone cannot do this."""
    case = targets.TARGETS[record["target"]]
    monomials, normal, receipt = export_basis(case, record["degree"], singular, timeout, output)
    if (
        monomials != record["monomials"]
        or [encode_polynomial(poly) for poly in normal] != record["radical_normal_forms"]
    ):
        raise ValueError("target basis differs from the fresh exact standard-monomial and normal-form export")
    return receipt


def prepare(target: targets.Target, degree: int, singular: str, timeout: int, output: Path) -> dict[str, Any]:
    started = time.monotonic()
    sources = bound_inputs(target)
    monomials, normal, receipt = export_basis(target, degree, singular, timeout, output)
    rows = kernel_rows(normal, target.prime)
    upper = targets.k2_hilbert_function(target)[str(degree)]
    base = json.loads((target.directory / "campaign_summary.json").read_text())["hilbert"]["sqrt_k2"][str(degree)]
    if len(monomials) != upper or len(rows) != upper - base:
        raise ValueError("export dimensions differ from retained Hilbert functions")
    record = {
        "schema": BASIS_SCHEMA,
        "target": target.name,
        "prime": target.prime,
        "root": target.root,
        "degree": degree,
        "nvars": targets.NGEN,
        "base_dimension": base,
        "upper_dimension": upper,
        "target_dimension": len(rows),
        "monomials": monomials,
        "radical_normal_forms": [encode_polynomial(p) for p in normal],
        "target_rows": rows,
        "sources": sources,
        "producer_sha256": digest(Path(__file__)),
        **receipt,
        "python_flint": importlib.metadata.version("python-flint"),
        "elapsed_ms": round(1000 * (time.monotonic() - started)),
        "premises": "Retained K2 membership and both dominant arc certificates; their proofs are not replayed.",
    }
    record["payload_sha256"] = payload_digest(record)
    validate_basis(record)
    save_record(output, record)
    return record


def bounds(base: int, upper: int, dimension: int, rank: int) -> dict[str, Any]:
    if (
        any(type(value) is not int for value in (base, upper, dimension, rank))
        or min(base, dimension, rank) < 0
        or upper != base + dimension
        or rank > dimension
    ):
        raise ValueError("inconsistent target dimensions or rank")
    lower = base + rank
    return {
        "lower": lower,
        "upper": upper,
        "status": "certified_degree" if lower == upper else "lower_bound_only",
        "exact_membership_certified": False,
    }


def ring_module() -> Any:
    import e8_ladder

    return e8_ladder


def valuation(element: Any, order: int) -> int:
    p, q = element
    return int(min([sum(e) for e in p.to_dict()] + [sum(e) + 1 for e in q.to_dict()], default=order))


def evaluate_polynomial(
    ring: Any, generators: list[Any], terms: dict[tuple[int, ...], int], order: int, low: int
) -> Any:
    """Evaluate homogeneous terms by common factors and exponent groups.

    A factor of y-degree c has valuation at least low*c after substitution.
    Its coefficient therefore needs precision only order-low*c. Raising the
    cutoff by low at each restored factor preserves the exact final jet.
    Grouping before substitution permits cancellations before expansion.
    """
    zero = (ring.zero, ring.zero)
    if not terms or order <= 0:
        return zero
    nvars = len(generators)
    common = tuple(min(exponent[j] for exponent in terms) for j in range(nvars))

    def restore(value: Any, exponents: tuple[int, ...], current: int) -> Any:
        for j, exponent in enumerate(exponents):
            for _ in range(exponent):
                current += low
                value = ring.mul(value, generators[j], current)
        return value

    if any(common):
        reduced = {
            tuple(e - c for e, c in zip(exponent, common, strict=True)): value for exponent, value in terms.items()
        }
        current = order - low * sum(common)
        return restore(evaluate_polynomial(ring, generators, reduced, current, low), common, current)
    if not any(any(exponent) for exponent in terms):
        return sum(terms.values()) * ring.one, ring.zero
    variable = max(range(nvars), key=lambda j: sum(exponent[j] > 0 for exponent in terms))
    groups: dict[int, dict[tuple[int, ...], int]] = {}
    for exponent, value in terms.items():
        residual = (*exponent[:variable], 0, *exponent[variable + 1 :])
        groups.setdefault(exponent[variable], {})[residual] = value
    total = zero
    for power, group in sorted(groups.items()):
        current = order - low * power
        value = evaluate_polynomial(ring, generators, group, current, low)
        exponents = tuple(power if j == variable else 0 for j in range(nvars))
        total = ring.add(total, restore(value, exponents, current))
    return total


def target_image(job: tuple[Any, ...]) -> Any:
    prime, order, encoded_gens, monomials, row = job
    lad = ring_module()
    ring = lad.shared_ring(prime, order)
    generators = [(ring.ctx.from_dict(p), ring.ctx.from_dict(q)) for p, q in encoded_gens]
    terms = {tuple(monomials[index]): coefficient for index, coefficient in row}
    low = min(valuation(generator, order) for generator in generators)
    total = evaluate_polynomial(ring, generators, terms, order, low)
    return lad.plain(total[0]), lad.plain(total[1])


def matrix_guard(rows: int, order: int, maximum: int) -> int:
    """Conservative budget for input and RREF dense arrays, not an RSS limit."""
    if rows < 0 or order < 1 or maximum < 1:
        raise ValueError("invalid matrix budget inputs")
    columns = math.comb(order + 4, 5) + (math.comb(order + 3, 5) if order > 1 else 0)
    selected = 2 * 8 * rows * columns
    if selected > maximum:
        raise MemoryError(f"selected dense arrays need at most {selected} bytes, above budget {maximum}")
    return selected


def denominator(
    lad: Any, ring: Any, generators: list[Any], degree: int, order: int, maximum: int
) -> tuple[list[Any], list[Any]]:
    """Image of m_R I^d: propagate all original G, never only target images."""
    low = min(valuation(generator, order) for generator in generators)
    start = order - low * degree
    if low < 1 or start < 2:
        raise ValueError(f"order {order} is below {low * degree + 2}, or G has a unit")
    basis = lad.ring_basis(ring, start, maximal=True)
    stages = []
    for d in range(1, degree + 1):
        current = start + low * d
        budget = matrix_guard(len(generators) * len(basis), current, maximum)
        started = time.monotonic()
        rank, basis = lad.rank_and_basis(ring, lad.span(ring, generators, basis, current), current)
        stage = {
            "degree": d,
            "order": current,
            "denominator_rank": rank,
            "selected_array_budget_bytes": budget,
            "elapsed_ms": round(1000 * (time.monotonic() - started)),
        }
        stages.append(stage)
        print(json.dumps(stage), file=sys.stderr, flush=True)
    return basis, stages


def bound_target(record: dict[str, Any]) -> targets.Target:
    validate_basis(record)
    target = targets.TARGETS[record["target"]]
    if record["prime"] != target.prime or record["root"] != target.root or record["nvars"] != targets.NGEN:
        raise ValueError("target field or generator count differs from its registry")
    if record["sources"] != bound_inputs(target):
        raise ValueError("basis source digests differ from current input bytes")
    return target


def run(
    record: dict[str, Any],
    order: int,
    maximum: int,
    *,
    verification_output: Path,
    singular: str = "Singular",
    verification_timeout: int = 300,
) -> dict[str, Any]:
    if order < 1 or maximum < 1:
        raise ValueError("order and matrix budget must be positive")
    target = bound_target(record)
    started = time.monotonic()
    verification = verify_export(record, singular, verification_timeout, verification_output)
    lad = ring_module()
    slug = "e8-nm" if target.sign9 == 1 else "e8-np"
    if lad.limits.PRIMES[target.prime] != target.root or lad.SIGN[slug] != target.sign9:
        raise ValueError("quadratic-algebra embedding differs from the registered target")
    _, ideal_j, ideal_g = lad.limits.header(slug, target.prime)
    normalized = tuple([[re.sub(r"\s", "", polynomial) for polynomial in ideal] for ideal in (ideal_j, ideal_g)])
    if normalized != targets.header_ideals(target):
        raise ValueError("quadratic-algebra J or ordered G differs from the bound header")
    ring = lad.Ring(target.prime, order)
    generators = lad.generators(slug, ring)
    if len(generators) != record["nvars"]:
        raise ValueError("substituted G differs from the registered generator count")
    basis, stages = denominator(lad, ring, generators, record["degree"], order, maximum)
    encoded = [(lad.plain(p), lad.plain(q)) for p, q in generators]
    jobs = [(target.prime, order, encoded, record["monomials"], row) for row in record["target_rows"]]
    images = parallel.ordered_map(target_image, jobs, min_items=2)
    elements = [(ring.ctx.from_dict(p), ring.ctx.from_dict(q)) for p, q in images]
    matrix_guard(len(basis) + len(elements), order, maximum)
    rank, _ = lad.rank_and_basis(ring, basis + elements, order)
    restricted = rank - len(basis)
    return {
        "schema": RANK_SCHEMA,
        "target": target.name,
        "prime": target.prime,
        "root": target.root,
        "degree": record["degree"],
        "order": order,
        "target_dimension": record["target_dimension"],
        "target_rank": restricted,
        "base_dimension": record["base_dimension"],
        **bounds(record["base_dimension"], record["upper_dimension"], record["target_dimension"], restricted),
        "full_generator_count": len(generators),
        "denominator_stages": stages,
        "basis_payload_sha256": record["payload_sha256"],
        "basis_verification": verification,
        "sources": record["sources"],
        "producer_sha256": digest(Path(__file__)),
        "ring_producer_sha256": digest(Path(lad.__file__)),
        "header_parser_sha256": digest(Path(lad.limits.__file__)),
        "parallel_sha256": digest(Path(parallel.__file__)),
        "python_flint": importlib.metadata.version("python-flint"),
        "selected_array_limit_bytes": maximum,
        "elapsed_ms": round(1000 * (time.monotonic() - started)),
        "scope": "Selected finite field only. A truncated zero or plateau supplies no exact membership upper bound.",
    }


def replay(basis: dict[str, Any], retained: dict[str, Any] | None, singular: str, timeout: int) -> dict[str, Any]:
    """Recompute exact target data; compare ranks and source identity, excluding timings."""
    with tempfile.TemporaryDirectory(prefix="a5-e8-target-") as directory:
        output = Path(directory) / "verification.json"
        if retained is None:
            bound_target(basis)
            verify_export(basis, singular, timeout, output)
        else:
            if retained.get("schema") != RANK_SCHEMA or retained.get("payload_sha256") != payload_digest(retained):
                raise ValueError("retained rank schema or payload digest differs")
            if retained.get("producer_sha256") != digest(Path(__file__)):
                raise ValueError("retained rank producer digest differs")
            fresh = run(
                basis,
                retained["order"],
                retained["selected_array_limit_bytes"],
                verification_output=output,
                singular=singular,
                verification_timeout=timeout,
            )

            def result_fields(record: dict[str, Any]) -> dict[str, Any]:
                result = {key: value for key, value in record.items() if key not in {"elapsed_ms", "payload_sha256"}}
                result["denominator_stages"] = [
                    {key: value for key, value in stage.items() if key != "elapsed_ms"}
                    for stage in record["denominator_stages"]
                ]
                return result

            if result_fields(fresh) != result_fields(retained):
                raise ValueError("fresh rank, bounds or provenance differ from the retained record")
    return {
        "target": basis["target"],
        "degree": basis["degree"],
        "target_dimension": basis["target_dimension"],
        "status": "replayed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--target", choices=tuple(targets.TARGETS), required=True)
    prep.add_argument("--degree", type=int, choices=(5, 6), required=True)
    prep.add_argument("--singular", default="Singular")
    prep.add_argument("--timeout", type=int, default=300)
    prep.add_argument("--out", type=Path, required=True)
    compute = commands.add_parser("run")
    compute.add_argument("basis", type=Path)
    compute.add_argument("--order", type=int, required=True)
    compute.add_argument("--max-matrix-mib", type=int, default=512)
    compute.add_argument("--singular", default="Singular")
    compute.add_argument("--verification-timeout", type=int, default=300)
    compute.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("replay")
    check.add_argument("basis", type=Path)
    check.add_argument("rank", type=Path, nargs="?")
    check.add_argument("--singular", default="Singular")
    check.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.command == "prepare":
        record = prepare(targets.TARGETS[args.target], args.degree, args.singular, args.timeout, args.out)
        print(
            json.dumps(
                {
                    key: record[key]
                    for key in (
                        "target",
                        "degree",
                        "base_dimension",
                        "upper_dimension",
                        "target_dimension",
                        "elapsed_ms",
                    )
                }
            )
        )
    elif args.command == "run":
        record = run(
            json.loads(args.basis.read_text()),
            args.order,
            args.max_matrix_mib * 1024**2,
            verification_output=args.out.with_name(args.out.stem + "-verification.json"),
            singular=args.singular,
            verification_timeout=args.verification_timeout,
        )
        save_record(args.out, record)
        print(json.dumps(record))
    else:
        retained = json.loads(args.rank.read_text()) if args.rank else None
        print(json.dumps(replay(json.loads(args.basis.read_text()), retained, args.singular, args.timeout)))


if __name__ == "__main__":
    main()
