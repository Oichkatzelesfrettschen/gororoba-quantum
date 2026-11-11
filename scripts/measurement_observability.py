"""Evaluate declared measurement contracts from JSON without acquiring provider data.

Usage: "$PYTHON" scripts/measurement_observability.py INPUT.json [--output RESULT.json]
The input schema is measurement-observability-input-v1. Every item declares its
id, kind, source and input. Supported kinds are multinomial_scores, six_state,
predictive_residual, nested_herald and tomography_completion. See the design
document for the exact estimands and tests/fixtures/measurement-observability.json
for a complete bounded example. Missing denominators or covariance stay missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
from collections import Counter as FrequencyCounter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from acceptance_statistics import AcceptanceCounts, analyze_six_state  # noqa: E402
from kernel_observability import nested_herald_statistics, tomography_completion  # noqa: E402
from measurement_statistics import multinomial_scores, predictive_residual  # noqa: E402
from provider_counters import Counter, Population, Status  # noqa: E402

INPUT_SCHEMA = "measurement-observability-input-v1"
OUTPUT_SCHEMA = "measurement-observability-result-v1"
DEFAULT_COEFFICIENT_ENTRY_BUDGET = 1_000_000
PRODUCERS = (
    "scripts/measurement_observability.py",
    "gororoba_quantum/acceptance_statistics.py",
    "gororoba_quantum/kernel_observability.py",
    "gororoba_quantum/measurement_statistics.py",
    "gororoba_quantum/provider_counters.py",
    "gororoba_quantum/parallel.py",
)


def _object(value: Any, required: set[str], optional: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{name}: a JSON object is required")
    missing, extra = required - value.keys(), value.keys() - required - optional
    if missing or extra:
        raise ValueError(f"{name}: missing fields {sorted(missing)}, unknown fields {sorted(extra)}")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(char) < 32 for char in value):
        raise ValueError(f"{name}: nonempty single-line text is required")
    return value


def _counter(value: Any) -> Counter:
    fields = _object(
        value,
        {"name", "value", "population", "scope", "status", "source"},
        {"assumptions", "terminated_by"},
        "counter",
    )
    for field in ("name", "scope", "source"):
        _text(fields[field], f"counter {field}")
    assumptions = fields.get("assumptions", [])
    if not isinstance(assumptions, list):
        raise ValueError("counter assumptions must be a list of strings")
    for assumption in assumptions:
        _text(assumption, "counter assumption")
    terminated_by = fields.get("terminated_by")
    if terminated_by is not None:
        _text(terminated_by, "counter terminated_by")
    return Counter(
        fields["name"],
        fields["value"],
        Population(fields["population"]),
        fields["scope"],
        Status(fields["status"]),
        fields["source"],
        tuple(assumptions),
        terminated_by,
    )


def _scores(value: Any) -> dict[str, Any]:
    fields = _object(value, {"counts", "scores", "sampling"}, {"estimator"}, "multinomial scores")
    if fields["sampling"] != "independent_fixed_trials":
        raise ValueError("multinomial scores require declared independent_fixed_trials")
    if not isinstance(fields["counts"], list):
        raise ValueError("counts must be a list")
    return multinomial_scores(fields["counts"], fields["scores"], estimator=fields.get("estimator", "plugin")).record()


def _six_state(value: Any) -> dict[str, Any]:
    fields = _object(value, {"records"}, {"independent_trials", "fixed_attempts", "rate_covariance"}, "six state")
    if not isinstance(fields["records"], list):
        raise ValueError("six-state records must be a list")
    records = []
    for row in fields["records"]:
        row = _object(row, {"state", "selected", "accepted", "denominator", "scope", "source"}, set(), "state")
        records.append(AcceptanceCounts(**{**row, "denominator": _counter(row["denominator"])}))
    return analyze_six_state(
        records,
        independent_trials=fields.get("independent_trials", False),
        fixed_attempts=fields.get("fixed_attempts", False),
        rate_covariance=fields.get("rate_covariance"),
    ).record()


def _prediction(value: Any) -> dict[str, Any]:
    fields = _object(
        value,
        {"observed", "predicted", "observation_covariance", "jacobian", "parameter_covariance", "dependence"},
        {"cross_covariance"},
        "predictive residual",
    )
    return predictive_residual(**fields).record()


def _herald(value: Any) -> dict[str, Any]:
    fields = _object(value, {"attempt_counter", "successes", "sampling"}, {"retention", "estimator"}, "nested herald")
    if not isinstance(fields["successes"], list):
        raise ValueError("successes must be a list")
    result = nested_herald_statistics(**{**fields, "attempt_counter": _counter(fields["attempt_counter"])})
    return {
        "attempt_counter": result.attempt_counter.record(),
        "successes": list(result.successes),
        "probabilities": result.probabilities.tolist(),
        "covariance_of_means": result.covariance_of_means.tolist(),
        "retention": result.retention,
        "recurrence_residuals": result.recurrence_residuals.tolist(),
        "recurrence_covariance": result.recurrence_covariance.tolist(),
        "estimator": result.estimator,
        "sampling_assumption": "fixed independent attempts with nested outcomes from the same attempts",
        "reference_distribution": None,
    }


def _tomography(value: Any) -> dict[str, Any]:
    fields = _object(value, {"half_dimension"}, {"coefficient_entry_budget"}, "tomography completion")
    dimension = fields["half_dimension"]
    budget = fields.get("coefficient_entry_budget", DEFAULT_COEFFICIENT_ENTRY_BUDGET)
    for name, number in (("half_dimension", dimension), ("coefficient_entry_budget", budget)):
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise ValueError(f"{name} must be a positive integer")
    entries = 32 * dimension**4
    if entries > budget:
        raise ValueError(
            f"tomography needs {entries} integer coefficient entries (at least {8 * entries} array bytes), "
            f"above coefficient_entry_budget={budget}; increase the budget only after checking available memory"
        )
    result = tomography_completion(dimension)
    return {
        "dimension": 2 * result.half_dimension,
        "observables": len(result.names),
        "coefficient_entries": entries,
        "coefficient_entry_budget": budget,
        "family_dimensions": dict(FrequencyCounter(result.families)),
        "names": list(result.names),
        "families": list(result.families),
        "real_coefficients": result.real.tolist(),
        "imaginary_coefficients": result.imaginary.tolist(),
        "hilbert_schmidt_norm_squared": result.hs_norm_squared.tolist(),
        "admission": "constructive Hermitian basis; physical implementation and acquired-bank span remain separate",
    }


ANALYZERS = {
    "multinomial_scores": _scores,
    "six_state": _six_state,
    "predictive_residual": _prediction,
    "nested_herald": _herald,
    "tomography_completion": _tomography,
}


def analyze_item(value: Any) -> dict[str, Any]:
    item = _object(value, {"id", "kind", "source", "input"}, set(), "item")
    identifier = _text(item["id"], "item id")
    source = _text(item["source"], "item source")
    kind = _text(item["kind"], "item kind")
    if kind not in ANALYZERS:
        raise ValueError(f"{identifier}: unknown analysis kind {kind}")
    try:
        result = ANALYZERS[kind](item["input"])
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{identifier}: {error}") from error
    return {"id": identifier, "kind": kind, "source": source, "result": result}


def analyze_document(value: Any) -> dict[str, Any]:
    document = _object(value, {"schema", "items"}, set(), "document")
    if document["schema"] != INPUT_SCHEMA:
        raise ValueError(f"schema must be {INPUT_SCHEMA}")
    if not isinstance(document["items"], list) or not document["items"]:
        raise ValueError("items must be a nonempty list")
    items = document["items"]
    identifiers = [_text(_object(item, {"id", "kind", "source", "input"}, set(), "item")["id"], "id") for item in items]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("item ids must be unique")
    return {
        "schema": OUTPUT_SCHEMA,
        "execution": "offline_analysis",
        "items": parallel.ordered_map(analyze_item, items),
        "qualification": "declared sampling/provenance contracts; no automatic physical-origin or significance claim",
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON number: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"nonfinite JSON number: {value}")
    return number


def read_document(content: bytes) -> Any:
    return json.loads(
        content, object_pairs_hook=_unique_object, parse_constant=_invalid_constant, parse_float=_finite_float
    )


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    try:
        if arguments.output is not None and arguments.output.resolve() == arguments.input.resolve():
            raise ValueError("output must not overwrite the input record")
        content = arguments.input.read_bytes()
        result = analyze_document(read_document(content))
        result["provenance"] = {
            "input_sha256": hashlib.sha256(content).hexdigest(),
            "producer_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PRODUCERS},
            "python": platform.python_version(),
            "numpy": np.__version__,
        }
        encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if arguments.output is None:
            print(encoded, end="")
        else:
            _write_atomic(arguments.output, encoded)
    except (OSError, ValueError, TypeError) as error:
        print(f"measurement_observability: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
