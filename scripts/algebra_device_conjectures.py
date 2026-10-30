"""Replay exact operational falsifiers and synthesize a frozen acquisition corpus.

Raw records and their provider analyzers remain authoritative. The offline
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
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from sympy import I, Matrix, Rational, exp, eye, kronecker_product, simplify, sqrt, symbols, zeros

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact, cd_sign, left_mult_matrix_exact  # noqa: E402
from parallel import ordered_map  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
import plan_records  # noqa: E402

DEFAULT_MANIFEST = ROOT / "docs/evidence/algebra-device-conjectures-14/manifest.json"
SCHEMA = "algebra-device-conjectures-v1"
# Files the check imports and runs: research_state's provider adapters re-derive every acquisition's facts and
# parallel.ordered_map keeps item order, so a behavior change in either fails the replay as a fact difference.
# A freeze binds them by behavior, not by bytes, and leaves them out of the sources.
EXECUTED_SOURCES = frozenset({"scripts/research_state.py", "gororoba_quantum/parallel.py"})


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


def _provider_facts(name: str) -> tuple[str, Any]:
    import research_state

    return name, research_state.PROVIDERS[name]().runs()


def source_digest(reference: str) -> str | None:
    """The sha256 a source binds: a file's bytes, or for FILE.json#COLLECTION/FIELD=VALUE the digest of the one
    record it selects (plan_records.evidence_digest), so a record appended to a shared ledger leaves it fresh.
    None when the file is missing or the selector matches no single record."""
    path = local_path(reference.partition("#")[0])
    if not path.is_file():
        return None
    return plan_records.evidence_digest(ROOT, reference) if "#" in reference else digest(path)


def _source_record(path: str) -> dict[str, str]:
    found = source_digest(path)
    if found is None:
        raise ValueError(f"source missing: {path}")
    return {"path": path, "sha256": found}


def _uncommitted() -> list[str]:
    """Every tracked or untracked path whose checkout state differs from HEAD's, ignored files excepted."""
    listed = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode()
    entries = iter(listed.split("\0"))
    paths = []
    for entry in entries:
        if not entry:
            continue
        paths.append(entry[3:])
        # A rename or copy entry is followed by its source path.
        if "R" in entry[:2] or "C" in entry[:2]:
            next(entries, None)
    return paths


def freeze_manifest(manifest: dict[str, Any], census_path: Path, reason: str, predecessor_path: str) -> dict[str, Any]:
    """Explicitly refresh the frozen inventory through the existing offline provider adapters.

    manifest is the predecessor's content, read from predecessor_path. The
    successor names that path, its digest, its base commit and the reason
    for the refresh, and the predecessor bundle keeps its path and bytes. A
    freeze reads the registry, every retained run and this producer, so it
    runs only on a checkout identical to HEAD and base_commit names every
    byte it read.
    """
    import research_state

    require(bool(reason.strip()), "a refresh needs a reason")
    uncommitted = _uncommitted()
    require(not uncommitted, f"freeze needs a checkout identical to HEAD: {', '.join(uncommitted[:5])}")
    predecessor = {
        "path": predecessor_path,
        "manifest_sha256": digest(local_path(predecessor_path)),
        "base_commit": manifest["base_commit"],
        "reason": reason.strip(),
    }

    registry = json.loads((ROOT / "docs/state/research_state.json").read_text())
    selected = set(manifest["selected_claim_ids"])
    claims = [claim for claim in registry["claims"] if claim["id"] in selected]
    require({claim["id"] for claim in claims} == selected, "selected claim is absent")
    acquired = {identity for claim in claims for identity in claim["acquisitions"]}
    providers = {name: adapter() for name, adapter in research_state.PROVIDERS.items()}
    facts = dict(ordered_map(_provider_facts, list(providers), min_items=1))
    acquisitions = []
    additional = [path for path in manifest["additional_sources"] if path not in EXECUTED_SOURCES]
    paths = set(additional)
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
        "supersedes": predecessor,
        "additional_sources": additional,
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "companion_pin": (ROOT / "ci/open_gororoba.pin").read_text().strip(),
        "claims": claims,
        "acquisitions": acquisitions,
        "acquisition_count": len(acquisitions),
        "sources": ordered_map(_source_record, sorted(paths), min_items=1),
    }
    census_path = local_path(census_path.resolve().relative_to(ROOT.resolve()).as_posix())
    census_path.write_text(
        encode(
            {
                "schema": "algebra-device-census-v1",
                "base_commit": manifest["base_commit"],
                "acquisitions": acquisitions,
                "sources": manifest["sources"],
            }
        )
    )
    manifest["census"] = {"path": census_path.relative_to(ROOT).as_posix(), "sha256": digest(census_path)}
    return manifest


def _verify_source(source: dict[str, str]) -> None:
    found = source_digest(source["path"])
    require(found is not None, f"source missing: {source['path']}")
    require(found == source["sha256"], f"source digest differs: {source['path']}")


def prose_paths(manifest: dict[str, Any]) -> set[str]:
    """The Markdown sources a manifest names only as claim documents or additional sources.

    Synthesis opens the comparison records, the Target snapshot and the companion
    pin, and the provider adapters open the run directories; none of them reads
    a Markdown file outside a run directory. A drifted prose source therefore
    leaves every derived byte fixed, so replay lists it and the next freeze
    rebinds it, while every other source fails replay on any byte change.
    """
    named = set(manifest["additional_sources"]) | {path for claim in manifest["claims"] for path in claim["documents"]}
    bound = {item["path"] for claim in manifest["claims"] for item in claim["evidence"]}
    bound |= {comparison["path"] for comparison in manifest["comparisons"]}
    runs = [Path(row["record"]["run"]) for row in manifest["acquisitions"] if row["included"]]
    return {
        path
        for path in named - bound
        if path.endswith(".md") and not any(Path(path).is_relative_to(run) for run in runs)
    }


def _source_drift(source: dict[str, str]) -> bool:
    return source_digest(source["path"]) != source["sha256"]


def drifted_prose(manifest: dict[str, Any]) -> list[str]:
    """The prose sources whose bytes differ from the manifest's binding, or that no longer exist."""
    prose = sorted(prose_paths(manifest))
    rows = [source for source in manifest["sources"] if source["path"] in prose]
    return [row["path"] for row, drift in zip(rows, ordered_map(_source_drift, rows), strict=True) if drift]


def _hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(char in "0123456789abcdef" for char in value)


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
    if "supersedes" in manifest:
        predecessor = manifest["supersedes"]
        require(
            isinstance(predecessor, dict)
            and set(predecessor) == {"path", "manifest_sha256", "base_commit", "reason"}
            and isinstance(predecessor["path"], str)
            and _hex(predecessor["manifest_sha256"], 64)
            and _hex(predecessor["base_commit"], 40)
            and isinstance(predecessor["reason"], str)
            and bool(predecessor["reason"].strip()),
            "predecessor record needs a path, a manifest digest, a base commit and a reason",
        )
        # The predecessor is retained evidence: its manifest keeps its path and bytes.
        _verify_source({"path": predecessor["path"], "sha256": predecessor["manifest_sha256"]})
    prose = prose_paths(manifest)
    ordered_map(_verify_source, [row for row in manifest["sources"] if row["path"] not in prose], min_items=1)
    _verify_source(manifest["census"])
    census = json.loads(local_path(manifest["census"]["path"]).read_text())
    require(
        census["schema"] == "algebra-device-census-v1" and census["base_commit"] == manifest["base_commit"],
        "frozen census identity differs",
    )
    require(census["sources"] == manifest["sources"], "frozen raw/source inventory differs")
    require(census["acquisitions"] == manifest["acquisitions"], "frozen acquisition census or facts differ")
    source_paths = {source["path"] for source in manifest["sources"]}
    pin_path = "ci/open_gororoba.pin"
    require(pin_path in source_paths, "companion pin source is unbound")
    require(manifest["companion_pin"] == local_path(pin_path).read_text().strip(), "companion pin differs")
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
        require(
            comparison["path"] in {item["path"] for item in current_claims[comparison["claim"]]["evidence"]},
            "comparison source is outside the named claim's evidence",
        )
        require(comparison["sampling_unit"] == "acquisition", "cross-job shot pairing is forbidden")
        require(
            comparison["register_semantics"] in {"provider-analyzer", "classical-bit", "qubit-last-measurement"},
            "unknown register semantics",
        )
    require(manifest["acquisition_count"] == len(manifest["acquisitions"]), "frozen acquisition denominator differs")
    # Adapters read retained records only. Re-deriving facts prevents a
    # self-consistent but invented census from becoming a provider observation.
    import research_state

    providers = {name: adapter() for name, adapter in research_state.PROVIDERS.items()}
    facts = dict(ordered_map(_provider_facts, list(providers), min_items=1))
    for acquisition in manifest["acquisitions"]:
        record = acquisition["record"]
        require(
            facts[record["provider"]].get(record["run"]) == acquisition["facts"],
            f"adapter facts differ: {record['id']}",
        )
        require(
            providers[record["provider"]].charge_unit == acquisition["charge_unit"],
            f"adapter charge unit differs: {record['id']}",
        )


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


def _measurement_row(count: int) -> dict[str, Any]:
    return {
        "steps": count,
        "cosine": "3/5",
        "sine": "4/5",
        **{key: str(value) for key, value in measurement_sequence(Rational(3, 5), Rational(4, 5), count).items()},
    }


def _verify_projector(projector: Any) -> None:
    require(projector * projector == projector and projector.T == projector, "sector projector failed")


def _project_shot(task: tuple[str, int, list[int]]) -> tuple[int, ...]:
    shot, width, indices = task
    require(isinstance(shot, str) and len(shot) == width and set(shot) <= {"0", "1"}, "malformed shot register")
    return tuple(int(shot[-1 - index]) for index in indices)


def project_shots(shots: list[str], width: int, indices: list[int]) -> list[tuple[int, ...]]:
    """Read explicit rightmost-bit indices; caller supplies the provider's register map."""
    require(type(width) is int and width > 0, "register width must be positive")
    require(
        bool(indices)
        and len(set(indices)) == len(indices)
        and all(type(index) is int and 0 <= index < width for index in indices),
        "invalid register indices",
    )
    return ordered_map(_project_shot, [(shot, width, indices) for shot in shots], min_items=1)


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


def _recovery_law(task: tuple[Any, Any, Any, bool]) -> bool:
    encoding, recovery, error, matched = task
    return bool(recovery * error * encoding == (encoding if matched else zeros(8, 2)))


def _recovery_operator(task: tuple[Any, Any]) -> Any:
    projector, error = task
    return projector * error.H


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
    code_projector = encoding * encoding.H
    recoveries = ordered_map(_recovery_operator, [(code_projector, error) for error in errors], min_items=1)
    complete = sum((recovery.H * recovery for recovery in recoveries), zeros(8)) == eye(8)
    recovery_law = all(
        ordered_map(
            _recovery_law,
            [
                (encoding, recovery, error, recovery_index == error_index)
                for recovery_index, recovery in enumerate(recoveries)
                for error_index, error in enumerate(errors)
            ],
        )
    )
    phase = kronecker_product(Matrix.diag(1, -1), eye(2), eye(2))
    logical_plus = encoding * Matrix([[1, 1], [1, 1]]) * encoding.H / 2
    logical_minus = encoding * Matrix([[1, -1], [-1, 1]]) * encoding.H / 2
    phase_collision = (logical_plus + phase * logical_plus * phase.H) / 2 == (
        logical_minus + phase * logical_minus * phase.H
    ) / 2 and logical_plus != logical_minus
    return {
        "reference": "three-qubit repetition encoding; specified error sets only",
        "corrects_single_x": bool(corrects and complete and recovery_law),
        "recovery_complete": bool(complete),
        "single_x_recovery_law": recovery_law,
        "logical_phase_ensembles_collide": bool(phase_collision),
        "corrects_single_z": _kl_scalar((encoding, eye(8), phase)),
        "algebra_specific": False,
    }


def _string_row(row: list[Any]) -> list[str]:
    return [str(simplify(value)) for value in row]


def strings(matrix: Any) -> list[list[str]]:
    return ordered_map(_string_row, matrix.tolist(), min_items=1)


def _bell_basis(task: tuple[Any, str, tuple[Any, Any]]) -> tuple[str, list[str]]:
    effect, basis, projectors = task
    bell = Matrix([1, 0, 0, 1]) / sqrt(2)
    density = bell * bell.H
    remote_sum = zeros(2)
    selector_rates = []
    for projector in projectors:
        instrument = kronecker_product(eye(2), projector)
        branch = instrument * density * instrument.H
        probability = branch.trace()
        require(probability == Rational(1, 2), "Bell outcome probability differs")
        remote = Matrix(
            2, 2, lambda row, column, state=branch: sum(state[2 * row + bit, 2 * column + bit] for bit in (0, 1))
        )
        remote_sum += remote
        selector_rates.append(str((effect * remote).trace() / probability))
    require(remote_sum == eye(2) / 2, "unconditional remote ensemble changed")
    return f"remote_{basis}_selector_success", selector_rates


def _bell_kernel_selection(effect: Any) -> dict[str, Any]:
    """Trace the measured half of a Bell pair; the remote basis is dark/bright."""
    plus = Matrix([[1, 1], [1, 1]]) / 2
    minus = Matrix([[1, -1], [-1, 1]]) / 2
    results: dict[str, Any] = dict(
        ordered_map(
            _bell_basis,
            [(effect, "z", (Matrix.diag(1, 0), Matrix.diag(0, 1))), (effect, "x", (plus, minus))],
            min_items=1,
        )
    )
    results["remote_selector_unconditional"] = str((effect * eye(2) / 2).trace())
    results["remote_unconditional"] = strings(eye(2) / 2)
    return results


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
    ordered_map(_verify_projector, projectors, min_items=1)
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
    dark_bright_encoding = Matrix.hstack(Matrix(dark) / sqrt(2), Matrix(bright) / sqrt(2))
    remote_effect = dark_bright_encoding.T * gram * dark_bright_encoding / 4
    require(remote_effect == Matrix.diag(0, 1), "dark/bright selector effect differs")
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
            **_bell_kernel_selection(remote_effect),
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
        "measurement": ordered_map(_measurement_row, [1, 2, 4, 8], min_items=1),
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


def _comparison(item: dict[str, Any]) -> dict[str, Any]:
    record = json.loads(local_path(item["path"]).read_text())
    selected = {}
    for field in item["fields"]:
        value = record
        for key in field.split("::"):
            value = value[key]
        selected[field] = value
    return {**item, "retained_values": selected}


def synthesis(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    comparisons = ordered_map(_comparison, manifest["comparisons"], min_items=1)
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
        "versions": {"python": platform.python_version(), "sympy": version("sympy")},
        "frozen_base": manifest["base_commit"],
        "supersedes": manifest.get("supersedes"),
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


def _comparison_markdown(comparison: dict[str, Any]) -> list[str]:
    return [
        f"### {comparison['claim']}",
        "",
        comparison["boundary"],
        "",
        "```json",
        encode(comparison["retained_values"]).rstrip(),
        "```",
        "",
    ]


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Algebra-to-device conjecture synthesis",
        "",
        "Generated by `scripts/algebra_device_conjectures.py`.",
        "Primary identity checks and reading scopes: "
        "[instrument sources](../../notes/papers/operational-instrument-sources.md).",
        "",
        f"Checkout HEAD at freeze: `{result['frozen_base']}`. Input bytes are bound individually by the manifest.",
        f"Manifest digest: `{result['manifest_sha256']}`.",
        *(
            [
                f"Supersedes `{result['supersedes']['path']}` (manifest digest "
                f"`{result['supersedes']['manifest_sha256']}`, frozen at `{result['supersedes']['base_commit']}`), "
                f"which keeps its path and bytes: {result['supersedes']['reason']}"
            ]
            if result["supersedes"]
            else []
        ),
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
    for section in ordered_map(_comparison_markdown, result["comparisons"], min_items=1):
        lines.extend(section)
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
    parser.add_argument("--reason", help="why --freeze refreshes the manifest, recorded beside its predecessor")
    parser.add_argument(
        "--predecessor", type=Path, help="the manifest --freeze supersedes; the successor goes to a new --manifest"
    )
    args = parser.parse_args()
    if args.freeze:
        if args.reason is None or args.predecessor is None:
            parser.error("--freeze requires --reason and --predecessor")
        census = args.manifest.with_name("census.json")
        # Retained bundles keep their paths and bytes, so a refresh writes a new bundle.
        if args.manifest.exists() or census.exists():
            parser.error(f"--freeze writes a new bundle; {args.manifest.parent} already holds one")
        predecessor = local_path(args.predecessor.resolve().relative_to(ROOT.resolve()).as_posix())
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        frozen = freeze_manifest(
            load_manifest(predecessor), census, args.reason, predecessor.relative_to(ROOT).as_posix()
        )
        args.manifest.write_text(encode(frozen))
        print("successor manifest frozen; generate derived outputs explicitly")
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
    for path in drifted_prose(load_manifest(args.manifest)):
        print(f"prose source drifted since the freeze (the next --freeze rebinds it): {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
