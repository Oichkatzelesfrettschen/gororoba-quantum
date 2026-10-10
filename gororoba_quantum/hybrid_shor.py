"""Credential-free host CLI for bounded hybrid Shor experiments.

The CLI plans circuits, runs local Aer simulation, or decodes saved counts.
IBM Runtime service construction and job submission remain exclusively in
live_run.py under the repository's explicit approval gate.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from qiskit_aer import AerSimulator

from factoring import (
    PrecheckResult,
    classical_precheck,
    decode_counts,
    distribution_success,
    ideal_phase_distribution,
    reference_multiplicative_order,
)
from order_finding import factor_order_finding, order_finding_plan


def _precheck_payload(result: PrecheckResult) -> dict[str, Any]:
    return asdict(result)


def _can_run_evidence(result: PrecheckResult) -> bool:
    return (
        result.modulus >= 3
        and result.base not in (0, 1)
        and math.gcd(result.base, result.modulus) == 1
        and result.status != "prime"
    )


def _plan_payload(modulus: int, base: int, phase_bits: int | None, evidence_mode: bool) -> dict[str, Any]:
    precheck = classical_precheck(modulus, base)
    payload: dict[str, Any] = {
        "mode": "evidence" if evidence_mode else "production",
        "precheck": _precheck_payload(precheck),
    }
    if precheck.status != "proceed" and not evidence_mode:
        payload["state"] = "resolved_classically"
        return payload
    if precheck.status != "proceed" and not _can_run_evidence(precheck):
        raise ValueError(f"evidence mode cannot build an order finder: {precheck.reason}")
    plan = order_finding_plan(modulus, precheck.base, phase_bits)
    payload.update({"state": "circuit_planned", "plan": asdict(plan)})
    return payload


def _decoded_payload(counts: Mapping[str | int, int], phase_bits: int, modulus: int, base: int) -> dict[str, Any]:
    decoded = decode_counts(counts, phase_bits, modulus, base)
    shot_count = sum(count for _, count in decoded)
    outcomes = []
    factors: set[int] = set()
    for recovery, count in decoded:
        factors.update(recovery.factors)
        outcomes.append(
            {
                "measurement": recovery.measurement,
                "bitstring": format(recovery.measurement, f"0{phase_bits}b"),
                "count": count,
                "probability": count / shot_count if shot_count else 0.0,
                "orders": list(recovery.orders),
                "factors": list(recovery.factors),
                "convergents": [asdict(candidate) for candidate in recovery.candidates],
            }
        )
    return {
        "state": "factored" if factors else "order_not_recovered",
        "shots": shot_count,
        "verified_factors": sorted(factors),
        "outcomes": outcomes,
    }


def _simulate_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload = _plan_payload(args.modulus, args.base, args.phase_bits, args.evidence)
    if payload["state"] != "circuit_planned":
        return payload
    if args.shots < 1:
        raise ValueError(f"shots must be positive, got {args.shots}")
    plan = payload["plan"]
    phase_bits = int(plan["phase_bits"])
    normalized_base = int(plan["base"])
    circuit = factor_order_finding(args.modulus, normalized_base, phase_bits)
    counts = AerSimulator().run(circuit, shots=args.shots, seed_simulator=args.seed).result().get_counts()
    reference_order = reference_multiplicative_order(normalized_base, args.modulus)
    ideal = ideal_phase_distribution(reference_order, phase_bits)
    payload.update(
        {
            "state": "locally_simulated",
            "simulation": {
                "engine": "AerSimulator",
                "seed": args.seed,
                "counts": dict(sorted(counts.items())),
                "ideal": distribution_success(ideal, phase_bits, args.modulus, normalized_base),
            },
            "decode": _decoded_payload(counts, phase_bits, args.modulus, normalized_base),
        }
    )
    return payload


def _load_counts(path: Path) -> Mapping[str | int, int]:
    document = json.loads(path.read_text())
    raw = document.get("counts", document) if isinstance(document, dict) else document
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object of bitstring counts")
    counts: dict[str | int, int] = {}
    for key, value in raw.items():
        if not isinstance(key, (str, int)) or not isinstance(value, int):
            raise ValueError(f"{path} counts must map bitstrings to integer frequencies")
        counts[key] = value
    return counts


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_problem_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("modulus", type=int)
        command.add_argument("--base", type=int, default=2)
        command.add_argument("--phase-bits", type=int)
        command.add_argument(
            "--evidence",
            action="store_true",
            help="build a coprime order-finding control even when preprocessing already finds a factor",
        )

    plan = subparsers.add_parser("plan", help="emit coefficients and resource counts without a circuit")
    add_problem_arguments(plan)
    simulate = subparsers.add_parser("simulate", help="run one local Aer order-finding experiment")
    add_problem_arguments(simulate)
    simulate.add_argument("--shots", type=int, default=256)
    simulate.add_argument("--seed", type=int, default=7)
    decode = subparsers.add_parser("decode", help="recover orders and verified factors from JSON counts")
    decode.add_argument("modulus", type=int)
    decode.add_argument("counts", type=Path)
    decode.add_argument("--base", type=int, default=2)
    decode.add_argument("--phase-bits", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            payload = _plan_payload(args.modulus, args.base, args.phase_bits, args.evidence)
        elif args.command == "simulate":
            payload = _simulate_payload(args)
        else:
            if args.modulus < 2:
                raise ValueError("modulus must be at least 2")
            counts = _load_counts(args.counts)
            payload = {
                "mode": "decode",
                "modulus": args.modulus,
                "base": args.base % args.modulus,
                "phase_bits": args.phase_bits,
                "decode": _decoded_payload(counts, args.phase_bits, args.modulus, args.base),
            }
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
