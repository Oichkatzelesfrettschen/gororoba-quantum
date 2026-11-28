"""Validate the machine-readable contract of a written case: one provider-neutral block and one provider block.

A case directory holds case_meta.json beside its CASE.md. The contract is the
JSON form of the approval request, so a reviewer, the pre-flight check
(scripts/preflight_check.py) and the submission scripts read one set of fields.

Layout of case_meta.json (schema "case-contract-v1"):

- "schema", "provider" ("ibm", "quandela", "quantum_inspire" or "iqm") and the
  common fields COMMON name, as top-level keys;
- the provider block, an object under the key that equals "provider", with the
  fields PROVIDER_BLOCKS names for it.

Beyond the type of each field, the checks bind the numbers to each other: the
expected cost stays inside the ceiling of the provider block, the expected
seconds stay inside the run's time ceiling, and each QRNG seed reference has
the spelling qrng_seeds.REF accepts. The approval quote may be null in a case
still awaiting approval; --require-approval demands a quote.

Usage: "$PYTHON" scripts/check_case_contract.py --check CASE_DIR [--require-approval]

Exit 0 when the contract holds, 1 with one line per violation, 2 when
case_meta.json is missing or is not JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qrng_seeds  # noqa: E402

SCHEMA = "case-contract-v1"
CASE_FILE = "case_meta.json"
HEX64 = "0123456789abcdef"

Rule = Callable[[Any], str | None]


def text(value: Any) -> str | None:
    return None if isinstance(value, str) and value.strip() else "must be a non-empty string"


def number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def positive(value: Any) -> str | None:
    return None if number(value) and value > 0 else "must be a positive number"


def non_negative(value: Any) -> str | None:
    return None if number(value) and value >= 0 else "must be a number of at least 0"


def positive_int(value: Any) -> str | None:
    return (
        None if isinstance(value, int) and not isinstance(value, bool) and value > 0 else "must be a positive integer"
    )


def true_flag(value: Any) -> str | None:
    return None if value is True else "must be true"


def flag(value: Any) -> str | None:
    return None if isinstance(value, bool) else "must be true or false"


def non_empty(value: Any) -> str | None:
    return None if isinstance(value, list | dict) and value else "must be a non-empty list or object"


def string_list(value: Any) -> str | None:
    ok = isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)
    return None if ok else "must be a list of non-empty strings"


def int_list(value: Any) -> str | None:
    ok = isinstance(value, list) and all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    return None if ok else "must be a list of integers"


def seed_refs(value: Any) -> str | None:
    if not isinstance(value, list):
        return "must be a list of qrng:<draw path>#<index> references"
    bad = [item for item in value if not (isinstance(item, str) and qrng_seeds.REF.fullmatch(item))]
    return f"holds malformed references {bad}" if bad else None


def quote(value: Any) -> str | None:
    return None if value is None or (isinstance(value, str) and value.strip()) else "must be null or a non-empty string"


def cost(value: Any) -> str | None:
    if not isinstance(value, dict) or set(value) != {"unit", "value"}:
        return 'must be an object with exactly "unit" and "value"'
    if value["unit"] not in ("seconds", "credits"):
        return 'unit must be "seconds" or "credits"'
    return None if number(value["value"]) and value["value"] >= 0 else "value must be a number of at least 0"


def sha256_hex(value: Any) -> str | None:
    ok = isinstance(value, str) and len(value) == 64 and set(value) <= set(HEX64)
    return None if ok else "must be a lowercase 64-digit sha256"


def one_of(*choices: Any) -> Rule:
    def rule(value: Any) -> str | None:
        return None if value in choices else f"must be one of {list(choices)}"

    return rule


def fraction(value: Any) -> str | None:
    return None if number(value) and 0 <= value <= 1 else "must be a number between 0 and 1"


def modes(value: Any) -> str | None:
    return (
        None if positive_int(value) is None or (int_list(value) is None and value) else "must be a mode count or a list"
    )


COMMON: dict[str, Rule] = {
    "case_id": text,
    "hypothesis": text,
    "observable_primary_source": text,
    "falsifier": text,
    "why_cheaper_substrate_fails": text,
    "backend": text,
    "shots": positive_int,
    "expected_seconds": positive,
    "expected_cost": cost,
    "qrng_seed_refs": seed_refs,
    "preregistered_readings": non_empty,
    "void_rules": non_empty,
    "stopping_rule": text,
    "approval_quote": quote,
}

# The ibm, quandela and quantum_inspire blocks follow the red-team template; the iqm block takes the fields
# iqm_records and the submission receipt of an IQM run already bind.
PROVIDER_BLOCKS: dict[str, dict[str, Rule]] = {
    "ibm": {
        "account": text,
        "family": text,
        "rep_delay_s": positive,
        "max_execution_seconds": positive,
        "max_total_execution_seconds": positive,
        "reserve_seconds": non_negative,
        "exclude_qubits": int_list,
        "pin_layout": flag,
        "readout_pair_in_job": true_flag,
        "check_cmd": text,
    },
    "quandela": {
        "platform": text,
        "max_credits": positive,
        "per_job_credits": positive,
        "mitigations": string_list,
        "source_modes": modes,
        "routing_health_floor": fraction,
        "architecture_policy": text,
    },
    "quantum_inspire": {
        "backend_type_id": one_of(1, 7),
        "qx_twin_run": text,
        "queue_policy": one_of("legacy", "wave-v1"),
        "readout_pair_per_batch": true_flag,
        "sanity_script": text,
    },
    "iqm": {
        "qc": text,
        "max_credits": positive,
        "price_per_second": positive,
        "calibration_set_id": text,
        "prediction_sha256": sha256_hex,
    },
}
COST_UNIT = {"ibm": "seconds", "quandela": "credits", "quantum_inspire": "credits", "iqm": "credits"}


def structural(meta: dict[str, Any], provider: str) -> list[str]:
    problems = []
    for name, rule in COMMON.items():
        if name not in meta:
            problems.append(f"{name}: required field is missing")
        elif (message := rule(meta[name])) is not None:
            problems.append(f"{name}: {message}")
    block = meta.get(provider)
    if not isinstance(block, dict):
        return [*problems, f"{provider}: the provider block is missing or is not an object"]
    for name, rule in PROVIDER_BLOCKS[provider].items():
        if name not in block:
            problems.append(f"{provider}.{name}: required field is missing")
        elif (message := rule(block[name])) is not None:
            problems.append(f"{provider}.{name}: {message}")
    unknown = sorted(set(block) - set(PROVIDER_BLOCKS[provider]))
    return [*problems, *(f"{provider}.{name}: field is not part of the contract" for name in unknown)]


def relations(meta: dict[str, Any], provider: str) -> list[str]:
    """Cross-field bounds; each runs only when the fields it reads passed their type rule."""
    block = meta[provider]
    problems = []
    expected = meta["expected_cost"]
    if expected["unit"] != COST_UNIT[provider]:
        problems.append(f"expected_cost.unit: a {provider} case counts {COST_UNIT[provider]}")
    if provider == "ibm":
        total = block["max_total_execution_seconds"]
        if block["max_execution_seconds"] > total:
            problems.append("ibm.max_execution_seconds: exceeds max_total_execution_seconds")
        if meta["expected_seconds"] > total:
            problems.append("expected_seconds: exceeds ibm.max_total_execution_seconds")
        if expected["unit"] == "seconds" and expected["value"] > total:
            problems.append("expected_cost.value: exceeds ibm.max_total_execution_seconds")
    elif provider == "quandela":
        ceiling = block["max_credits"]
        if block["per_job_credits"] > ceiling:
            problems.append("quandela.per_job_credits: exceeds max_credits")
        if expected["value"] > ceiling:
            problems.append("expected_cost.value: exceeds quandela.max_credits")
        if meta["backend"] != block["platform"]:
            problems.append("quandela.platform: differs from backend")
    elif provider == "iqm":
        if expected["value"] > block["max_credits"]:
            problems.append("expected_cost.value: exceeds iqm.max_credits")
        if meta["expected_seconds"] * block["price_per_second"] > block["max_credits"]:
            problems.append("expected_seconds: priced above iqm.max_credits")
    return problems


def validate(meta: Any, *, require_approval: bool = False) -> list[str]:
    """Every violation of the contract in a parsed case_meta.json; an empty list admits the case."""
    if not isinstance(meta, dict):
        return ["case_meta.json: the top level must be an object"]
    problems = []
    if meta.get("schema") != SCHEMA:
        problems.append(f"schema: must be {SCHEMA}")
    provider = meta.get("provider")
    if provider not in PROVIDER_BLOCKS:
        return [*problems, f"provider: must be one of {sorted(PROVIDER_BLOCKS)}"]
    found = structural(meta, provider)
    problems.extend(found)
    if require_approval and not meta.get("approval_quote"):
        problems.append("approval_quote: a quoted approval is required")
    if not found:
        problems.extend(relations(meta, provider))
    return problems


def check_case_dir(case_dir: Path, *, require_approval: bool = False) -> list[str]:
    """Read CASE_DIR/case_meta.json and validate it; raises FileNotFoundError or ValueError when it is unreadable."""
    return validate(json.loads((case_dir / CASE_FILE).read_text(encoding="utf-8")), require_approval=require_approval)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--check", metavar="CASE_DIR", type=Path, required=True)
    parser.add_argument("--require-approval", action="store_true")
    arguments = parser.parse_args()
    try:
        problems = check_case_dir(arguments.check, require_approval=arguments.require_approval)
    except (OSError, ValueError) as error:
        print(f"check_case_contract: {arguments.check}/{CASE_FILE}: {error}", file=sys.stderr)
        return 2
    for problem in problems:
        print(f"{arguments.check}: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
