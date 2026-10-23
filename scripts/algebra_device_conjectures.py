"""Replay exact operational falsifiers and synthesize a frozen acquisition corpus.

Raw records and their provider analyzers remain authoritative. This offline
entry point validates an explicit manifest, computes exact finite controls,
and carries the retained decisions with their evidence classes and limits.
Check and synthesis modes read local files only. Explicit freeze mode uses
the repository provider adapters to validate retained records. No mode executes
commands from a manifest or submits a provider job.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from sympy import I, Matrix, Rational, exp, eye, kronecker_product, simplify, sqrt, symbols, zeros

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact, cd_sign, left_mult_matrix_exact  # noqa: E402
from parallel import ordered_map  # noqa: E402

DEFAULT_MANIFEST = ROOT / "docs/evidence/algebra-device-conjectures/manifest.json"
SCHEMA = "algebra-device-conjectures-v1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def encode(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(value: str) -> Path:
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts, "source must be repository-relative")
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT.resolve()), "source must resolve repository-relative")
    return resolved


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    require(isinstance(value, dict), "manifest must be an object")
    return dict(value)


def freeze_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Explicitly refresh the frozen inventory through the existing offline provider adapters."""
    import research_state

    registry = json.loads((ROOT / "docs/state/research_state.json").read_text())
    selected = set(manifest["selected_claim_ids"])
    claims = [claim for claim in registry["claims"] if claim["id"] in selected]
    require({claim["id"] for claim in claims} == selected, "selected claim is absent")
    acquired = {identity for claim in claims for identity in claim["acquisitions"]}
    providers = {name: adapter() for name, adapter in research_state.PROVIDERS.items()}
    facts = {name: provider.runs() for name, provider in providers.items()}
    acquisitions = []
    paths = set(manifest["additional_sources"])
    for claim in claims:
        paths.update(item["path"] for item in claim["evidence"])
        paths.update(claim["documents"])
    for row in registry["acquisitions"]:
        provider = providers[row["provider"]]
        acquisitions.append(
            {
                "id": row["id"],
                "record": row,
                "included": row["id"] in acquired,
                "reason": "named by selected claim" if row["id"] in acquired else "outside selected claim families",
                "facts": facts[row["provider"]][row["run"]],
                "charge_unit": provider.charge_unit,
            }
        )
        if row["id"] in acquired:
            paths.update(
                path.relative_to(ROOT).as_posix() for path in local_path(row["run"]).rglob("*") if path.is_file()
            )
    manifest = {
        **manifest,
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "companion_pin": (ROOT / "ci/open_gororoba.pin").read_text().strip(),
        "claims": claims,
        "acquisitions": acquisitions,
        "acquisition_count": len(acquisitions),
        "sources": [{"path": path, "sha256": digest(local_path(path))} for path in sorted(paths)],
    }
    return manifest


def _verify_source(source: dict[str, str]) -> None:
    path = local_path(source["path"])
    require(path.is_file(), f"source missing: {source['path']}")
    require(digest(path) == source["sha256"], f"source digest differs: {source['path']}")


def validate_manifest(manifest: dict[str, Any]) -> None:
    require(manifest.get("schema") == SCHEMA, "manifest schema differs")
    for field, key in (("proposals", "id"), ("sources", "path"), ("claims", "id"), ("acquisitions", "id")):
        rows = manifest[field]
        keys = [row[key] for row in rows]
        require(len(keys) == len(set(keys)), f"duplicate {field} identity")
    require(len(manifest["proposals"]) == 22, "manifest must account for all 22 proposals")
    require(
        set(manifest["selected_claim_ids"]) == {claim["id"] for claim in manifest["claims"]}, "claim selection differs"
    )
    ordered_map(_verify_source, manifest["sources"], min_items=1)
    source_paths = {source["path"] for source in manifest["sources"]}
    registry = json.loads((ROOT / "docs/state/research_state.json").read_text())
    current_claims = {claim["id"]: claim for claim in registry["claims"]}
    current_acquisitions = {row["id"]: row for row in registry["acquisitions"]}
    for claim in manifest["claims"]:
        require(current_claims.get(claim["id"]) == claim, f"selected claim changed: {claim['id']}")
        require(all(item["path"] in source_paths for item in claim["evidence"]), "claim evidence is unbound")
    selected_acquisitions = {item for claim in manifest["claims"] for item in claim["acquisitions"]}
    for acquisition in manifest["acquisitions"]:
        identity = acquisition["id"]
        require(current_acquisitions.get(identity) == acquisition["record"], f"acquisition changed: {identity}")
        require(acquisition["included"] == (identity in selected_acquisitions), "acquisition selection differs")
        require(bool(acquisition["reason"]), "acquisition exclusion/selection needs a reason")
    require(selected_acquisitions <= {row["id"] for row in manifest["acquisitions"]}, "selected acquisition missing")
    runs = [row["record"]["run"] for row in manifest["acquisitions"]]
    require(len(runs) == len(set(runs)), "duplicate acquisition run")
    for proposal in manifest["proposals"]:
        require(proposal["status"] in {"develop", "exactly-refuted", "capability-gated", "deferred"}, "invalid status")
        require(bool(proposal["falsifier"]) and bool(proposal["boundary"]), "proposal lacks falsifier or boundary")
        require(set(proposal["claims"]) <= {claim["id"] for claim in manifest["claims"]}, "unknown proposal claim")
    for comparison in manifest["comparisons"]:
        require(comparison["path"] in source_paths, "comparison source is unbound")
        require(comparison["claim"] in {claim["id"] for claim in manifest["claims"]}, "unknown comparison claim")
        require(comparison["sampling_unit"] == "acquisition", "cross-job shot pairing is forbidden")
        require(
            comparison["register_semantics"] in {"provider-analyzer", "classical-bit", "qubit-last-measurement"},
            "unknown register semantics",
        )
    require(manifest["acquisition_count"] == len(manifest["acquisitions"]), "frozen acquisition denominator differs")


def filter_state(operator: Any, state: Any) -> dict[str, Any]:
    """Complete a contraction by its positive failure operator, keeping zero success undefined."""
    require(
        state.rows == state.cols
        and state.is_hermitian is True
        and state.trace() == 1
        and state.is_positive_semidefinite is True,
        "invalid density matrix",
    )
    require(operator.shape == state.shape, "operator and density dimensions differ")
    complement = eye(operator.cols) - operator.H * operator
    require(complement.is_positive_semidefinite is True, "filter must be a contraction")
    failure_operator = complement ** Rational(1, 2)
    success_state = operator * state * operator.H
    failure_state = failure_operator * state * failure_operator.H
    probability = simplify(success_state.trace())
    return {
        "success": probability,
        "failure": simplify(failure_state.trace()),
        "conditional": success_state / probability if probability != 0 else None,
        "unconditional": simplify(success_state + failure_state),
    }


def require_skew(matrix: Any) -> None:
    require(matrix.T == -matrix, "imaginary left multiplication must be skew")


def _normality(dimension: int) -> dict[str, int]:
    # Each entry is an exact integer signed permutation. Antisymmetry of the
    # basis operators establishes it for every real linear combination here.
    for index in range(1, dimension):
        for column in range(dimension):
            row = index ^ column
            require(cd_sign(dimension, index, column) == -cd_sign(dimension, index, row), "skew sign failure")
    return {"dimension": dimension, "imaginary_basis_operators": dimension - 1}


def measurement_sequence(cosine: Any, sine: Any, count: int) -> dict[str, Any]:
    """Exact rotation/dephasing recurrence; count steps of one specified rotation."""
    require(type(count) is int and count > 0, "measurement count must be positive")
    require(
        cosine.is_real is True and sine.is_real is True and simplify(cosine**2 + sine**2) == 1,
        "rotation must have real unit-norm coefficients",
    )
    rotation = Matrix([[cosine, -sine], [sine, cosine]])
    state = Matrix.diag(1, 0)
    for _ in range(count):
        evolved = rotation * state * rotation.T
        state = Matrix.diag(evolved[0, 0], evolved[1, 1])
    return {
        "all_zero_survival": cosine ** (2 * count),
        "total_probability": state.trace(),
        "unconditional_zero": state[0, 0],
    }


def project_shots(shots: list[str], width: int, indices: list[int]) -> list[tuple[int, ...]]:
    """Read explicit rightmost-bit indices; caller supplies the provider's register map."""
    require(type(width) is int and width > 0, "register width must be positive")
    require(
        bool(indices)
        and len(set(indices)) == len(indices)
        and all(type(index) is int and 0 <= index < width for index in indices),
        "invalid register indices",
    )
    require(
        all(isinstance(shot, str) and len(shot) == width and set(shot) <= {"0", "1"} for shot in shots),
        "malformed shot register",
    )
    return [tuple(int(shot[-1 - index]) for index in indices) for shot in shots]


def holm(probabilities: list[float], alpha: float = 0.05) -> list[bool]:
    """Reject a declared finite family by Holm step-down; False means unresolved."""
    require(math.isfinite(alpha) and 0 < alpha < 1, "invalid family alpha")
    require(all(math.isfinite(value) and 0 <= value <= 1 for value in probabilities), "invalid p-value")
    result = [False] * len(probabilities)
    for rank, index in enumerate(sorted(range(len(probabilities)), key=probabilities.__getitem__)):
        if probabilities[index] > alpha / (len(probabilities) - rank):
            break
        result[index] = True
    return result


def timing_admission(cycle_ns: float, measurement_ns: float, dt_ns: float) -> dict[str, Any]:
    """Necessary timing bound only; served scheduling and feedback overhead need a fresh case."""
    require(
        all(math.isfinite(value) and value > 0 for value in (cycle_ns, measurement_ns, dt_ns)),
        "timing values must be finite positive nanoseconds",
    )
    ticks = cycle_ns / dt_ns
    aligned = math.isclose(ticks, round(ticks), rel_tol=0, abs_tol=1e-9)
    return {
        "cycle_ns": cycle_ns,
        "measurement_ns": measurement_ns,
        "dt_ns": dt_ns,
        "admitted": aligned and cycle_ns >= measurement_ns,
        "boundary": "Necessary lower bound; gate, reset, feedback and backend alignment constraints remain.",
    }


def _kl_scalar(task: tuple[Any, Any, Any]) -> bool:
    encoding, first, second = task
    compressed = encoding.H * first.H * second * encoding
    return bool(compressed == compressed[0, 0] * eye(encoding.cols))


def _code_control() -> dict[str, Any]:
    encoding = zeros(8, 2)
    encoding[0, 0] = encoding[7, 1] = 1
    flip = Matrix([[0, 1], [1, 0]])
    errors = [
        eye(8),
        kronecker_product(flip, eye(2), eye(2)),
        kronecker_product(eye(2), flip, eye(2)),
        kronecker_product(eye(2), eye(2), flip),
    ]
    corrects = all(ordered_map(_kl_scalar, [(encoding, first, second) for first in errors for second in errors]))
    phase = kronecker_product(Matrix.diag(1, -1), eye(2), eye(2))
    return {
        "reference": "three-qubit repetition encoding; specified error sets only",
        "corrects_single_x": corrects,
        "corrects_single_z": _kl_scalar((encoding, eye(8), phase)),
        "algebra_specific": False,
    }


def strings(matrix: Any) -> list[list[str]]:
    return [[str(simplify(value)) for value in row] for row in matrix.tolist()]


def exact_families() -> dict[str, Any]:
    """Finite algebra and rational instrument certificates, without simulator sampling."""
    operand = [0] * 16
    operand[1] = operand[10] = 1
    dark, bright = [0] * 16, [0] * 16
    dark[4], dark[15] = 1, -1
    bright[4] = bright[15] = 1
    left = Matrix(left_mult_matrix_exact(16, operand))
    require_skew(left)
    gram = left.T * left
    identity = eye(16)
    projectors = [
        (gram - 2 * identity) * (gram - 4 * identity) / 8,
        -gram * (gram - 4 * identity) / 4,
        gram * (gram - 2 * identity) / 8,
    ]
    require(sum(projectors, zeros(16)) == identity, "sector resolution failed")
    for projector in projectors:
        require(projector * projector == projector and projector.T == projector, "sector projector failed")
    require(gram * (gram - 2 * identity) * (gram - 4 * identity) == zeros(16), "sector polynomial failed")
    require(left * Matrix(dark) == zeros(16, 1), "kernel witness failed")
    x_gate, z_gate = Matrix([[0, 1], [1, 0]]), Matrix.diag(1, -1)
    reference = Matrix([1, 0])
    overlap = (reference.T * (z_gate * x_gate).H * (x_gate * z_gate) * reference)[0]
    require(overlap == -1, "order reference failed")
    filtered = filter_state(Matrix.diag(1, Rational(1, 2)), eye(2) / 2)
    # Bell-pair Z and X selections both average to the same remote density.
    plus = Matrix([[1, 1], [1, 1]]) / 2
    minus = Matrix([[1, -1], [-1, 1]]) / 2
    require((plus + minus) / 2 == eye(2) / 2, "remote ensemble changed")
    exceptional = x_gate + I * z_gate
    require(exceptional != zeros(2) and exceptional**2 == zeros(2), "exceptional point control failed")
    embeddings = ordered_map(_embedding, [8, 16], min_items=1)
    phase_angle = symbols("phi", real=True)
    phase_state = exp(I * phase_angle) * Matrix([1, 1]) / sqrt(2)
    phased_control = Matrix([1, exp(I * phase_angle)]) / sqrt(2)
    left_one = Matrix(left_mult_matrix_exact(8, [0, 1, 0, 0, 0, 0, 0, 0]))
    left_two = Matrix(left_mult_matrix_exact(8, [0, 0, 1, 0, 0, 0, 0, 0]))
    product = cd_multiply_exact(8, [0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0])
    product_left = Matrix(left_mult_matrix_exact(8, product))
    witness = product_left.T * left_one * left_two
    return {
        "evidence_class": "exact finite certificate",
        "normality": ordered_map(_normality, [2, 4, 8, 16, 32, 64], min_items=1),
        "sectors": {
            "operand": operand,
            "unnormalized_dark": dark,
            "unnormalized_bright": bright,
            "multiplicities": {
                str(value): int(projector.trace()) for value, projector in zip((0, 2, 4), projectors, strict=True)
            },
            "kernel_product": [str(value) for value in left * Matrix(dark)],
            "bright_norm_squared": str((left * Matrix(bright)).norm() ** 2),
            "bright_mutation_changes_zero_product": left * Matrix(bright) != zeros(16, 1),
            "gram_polynomial_zero": True,
        },
        "order": {
            "anticommuting_control_x": str(overlap),
            "commuting_control_x": str((reference.T * (x_gate * x_gate).H * (x_gate * x_gate) * reference)[0]),
            "incoherent_control_x": str((x_gate * eye(2) / 2).trace()),
            "matrix_associativity": (x_gate * z_gate) * x_gate == x_gate * (z_gate * x_gate),
        },
        "phase": {
            "unconditional_invariant": simplify(phase_state * phase_state.H) == Matrix([[1, 1], [1, 1]]) / 2,
            "controlled_relative_x": str(simplify((phased_control.H * x_gate * phased_control)[0])),
        },
        "associator": {
            "basis_inputs": [1, 2, 4],
            "encoded_overlap": str(witness[4, 4]),
            "associative_control_overlap": str(witness[0, 0]),
        },
        "code": _code_control(),
        "conditioning": {
            "success": str(filtered["success"]),
            "failure": str(filtered["failure"]),
            "conditional": strings(filtered["conditional"]),
            "remote_unconditional": strings((plus + minus) / 2),
            "zero_success_conditional": filter_state(Matrix.diag(0, 1), Matrix.diag(1, 0))["conditional"],
        },
        "pt": {
            "generator": strings(exceptional),
            "parity_time_invariant": x_gate * exceptional.conjugate() * x_gate == exceptional,
            "exceptional_square_zero": exceptional**2 == zeros(2),
            "exceptional_rank": exceptional.rank(),
            "algebra_specific": False,
        },
        "dimension": {
            "embedding_checks": embeddings,
            "outside_support_changes_product": all(row["outside_changes"] for row in embeddings),
            "sedenion_logical_qubits": 4,
            "one_9_1_3_block_dimension": 2,
        },
        "measurement": [
            {
                "steps": count,
                "cosine": "3/5",
                "sine": "4/5",
                **{
                    key: str(value)
                    for key, value in measurement_sequence(Rational(3, 5), Rational(4, 5), count).items()
                },
            }
            for count in (1, 2, 4, 8)
        ],
        "measurement_fixed_total": {
            "unmeasured_survival": str(
                (Matrix([[Rational(3, 5), -Rational(4, 5)], [Rational(4, 5), Rational(3, 5)]]) ** 2)[0, 0] ** 2
            ),
            "measured_survival": str(measurement_sequence(Rational(3, 5), Rational(4, 5), 2)["all_zero_survival"]),
            "boundary": (
                "Same two rotations; intermediate ideal projection adds no model elapsed time. "
                "Hardware measurement overhead is separate."
            ),
        },
        "limits": [
            "The measurement rows hold the per-step rotation fixed, not total time.",
            "Finite normality checks cover the listed dimensions; "
            "the source adjoint identity supplies the general statement.",
            "No physical squeezing, topological protection, quantum error-correction benefit "
            "or fundamental-physics anomaly follows.",
        ],
    }


def _embedding(dimension: int) -> dict[str, Any]:
    require(
        all(
            cd_sign(dimension, left, right) == cd_sign(2 * dimension, left, right)
            for left in range(dimension)
            for right in range(dimension)
        ),
        "embedding changed a basis product",
    )
    left, lower, outside = [0] * (2 * dimension), [0] * (2 * dimension), [0] * (2 * dimension)
    left[1], lower[1], outside[dimension] = 1, 1, 1
    return {
        "from": dimension,
        "to": 2 * dimension,
        "basis_pairs": dimension**2,
        "outside_changes": cd_multiply_exact(2 * dimension, left, lower)
        != cd_multiply_exact(2 * dimension, left, outside),
    }


def synthesis(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    comparisons = []
    for item in manifest["comparisons"]:
        record = json.loads(local_path(item["path"]).read_text())
        selected = {}
        for field in item["fields"]:
            value = record
            for key in field.split("::"):
                value = value[key]
            selected[field] = value
        comparisons.append({**item, "retained_values": selected})
    target_path = "docs/evidence/heron_platform/targets.json"
    require(target_path in {source["path"] for source in manifest["sources"]}, "timing source is unbound")
    snapshot = json.loads(local_path(target_path).read_text())
    timing = []
    for backend, target in sorted(snapshot["backends"].items()):
        lower_ns = min(target["instructions"]["measure_2"]["duration"]) * 1e9
        timing.append(
            {
                "backend": backend,
                "calibration": target["calibration"],
                "snapshot_retrieved": snapshot["retrieved"],
                **timing_admission(50, lower_ns, target["dt"] * 1e9),
            }
        )
    return {
        "schema": SCHEMA,
        "manifest_sha256": hashlib.sha256(encode(manifest).encode()).hexdigest(),
        "producer_sha256": digest(Path(__file__)),
        "frozen_base": manifest["base_commit"],
        "acquisitions": manifest["acquisitions"],
        "proposals": manifest["proposals"],
        "comparisons": comparisons,
        "exact": exact_families(),
        "retained_timing_admission": timing,
        "statistical_policy": (
            "Historical decisions retain their preregistered rules; new comparisons are descriptive. "
            "No new p-values are inferred from summary records."
        ),
        "provider_execution_authorized": False,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Algebra-to-device conjecture synthesis",
        "",
        "Generated by `scripts/algebra_device_conjectures.py`.",
        "",
        f"Frozen base: `{result['frozen_base']}`. Manifest digest: `{result['manifest_sha256']}`.",
        "",
        f"Acquisitions accounted for: {len(result['acquisitions'])}; "
        f"selected: {sum(row['included'] for row in result['acquisitions'])}.",
        "",
        result["statistical_policy"],
        "",
        "## Proposal dispositions",
        "",
        "| Proposal | Disposition | Operational question | Falsifier |",
        "|---|---|---|---|",
    ]
    for row in result["proposals"]:
        lines.append(f"| {row['id']} | {row['status']} | {row['question']} | {row['falsifier']} |")
    lines += ["", "## Retained comparisons", ""]
    for comparison in result["comparisons"]:
        lines += [
            f"### {comparison['claim']}",
            "",
            comparison["boundary"],
            "",
            "```json",
            encode(comparison["retained_values"]).rstrip(),
            "```",
            "",
        ]
    lines += [
        "## Exact finite controls",
        "",
        "```json",
        encode(result["exact"]).rstrip(),
        "```",
        "",
        "The machine-readable result retains all acquisition exclusions. "
        "The design document owns prospective controls and admission rules.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--out", type=Path, help="write derived result.json and README.md in this directory")
    target.add_argument("--check", type=Path, help="compare derived bytes without writing")
    target.add_argument(
        "--freeze", action="store_true", help="explicitly refresh manifest from offline provider adapters"
    )
    args = parser.parse_args()
    if args.freeze:
        args.manifest.write_text(encode(freeze_manifest(load_manifest(args.manifest))))
        print("frozen manifest refreshed; regenerate derived outputs explicitly")
        return 0
    result = synthesis(load_manifest(args.manifest))
    outputs = {"result.json": encode(result), "README.md": render(result)}
    destination = args.out or args.check
    if args.check:
        for name, content in outputs.items():
            require((destination / name).read_text() == content, f"derived replay differs: {name}")
    else:
        destination.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (destination / name).write_text(content)
    print(f"{SCHEMA}: {len(result['proposals'])} proposals; {len(result['acquisitions'])} acquisitions accounted for")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
