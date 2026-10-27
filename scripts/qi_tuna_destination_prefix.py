"""Replay descriptive nominal-zero data while preserving the incomplete case's refusal."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from qi_tuna_readout_destination_analysis import (
    ANCILLAS,
    BATCHES,
    PROPOSAL,
    ROOT,
    SHOTS,
    analyze,
    digest,
    ordered_map,
    timestamp,
    validate_approval,
    validate_batch,
)

CAMPAIGN_SHA256 = "53eb49080573b876545b5301b195ee06127625653266fbb64b98a60823e07a76"


def replay(run: Path) -> dict[str, Any]:
    """Validate the acquired prefix and return counts without a statistical acceptance decision."""
    if digest(run / "sequence-plan.json") != CAMPAIGN_SHA256:
        raise ValueError("descriptive replay requires the approved campaign")
    primary = analyze(run)
    if primary != json.loads((run / "analysis.json").read_text()):
        raise ValueError("retained primary refusal differs from frozen replay")
    if primary["outcome"] != "implementation route unavailable":
        raise ValueError("prefix description requires the retained incomplete-case outcome")
    state = json.loads((run / "execution-state.json").read_text())
    if state["phase"] != "stopped" or state["error_type"] != "TimeoutError":
        raise ValueError("prefix description requires the recorded request-deadline stop")
    submitted = [name for name in BATCHES if (run / name / "submission.json").exists()]
    if submitted != list(BATCHES[:3]):
        raise ValueError("description requires exactly the three nominal-zero submissions")
    campaign = json.loads((run / "sequence-plan.json").read_text())
    bindings, approval = validate_approval(run, campaign)
    rows = ordered_map(
        validate_batch,
        [(run, PROPOSAL, batch, campaign, bindings, approval) for batch in campaign["batches"][:3]],
    )
    if len({row["job"] for row in rows}) != 3 or len({row["batch_job"] for row in rows}) != 3:
        raise ValueError("prefix job or batch identities repeat")
    for before, after in zip(rows, rows[1:], strict=False):
        if timestamp(after["created_utc"]) < timestamp(before["finished_utc"]) + dt.timedelta(seconds=30):
            raise ValueError("prefix violates completion plus the frozen pause")
    comparisons = []
    for index, qubit in enumerate(ANCILLAS):
        before, rotated, after = [row["joint_counts"][index] for row in rows]
        comparisons.append(
            {
                "ancilla_qubit": qubit,
                "joint_cell_order": ["00", "01", "10", "11"],
                "joint_counts_before_rotated_after": [before, rotated, after],
                "early_one_counts": [counts[2] + counts[3] for counts in (before, rotated, after)],
                "terminal_one_counts": [counts[1] + counts[3] for counts in (before, rotated, after)],
                "response_numerators": [2 * rotated[cell] - before[cell] - after[cell] for cell in range(4)],
                "response_denominator": 2 * SHOTS,
                "baseline_numerators": [after[cell] - before[cell] for cell in range(4)],
                "baseline_denominator": SHOTS,
            }
        )
    return {
        "schema": "qi-nominal-zero-prefix-description-v1",
        "primary_case_outcome": primary["outcome"],
        "scope": "Posthoc description of the complete nominal-zero prefix; the six-job endpoint remains unavailable.",
        "statistical_acceptance_admitted": False,
        "causal_attribution": "unresolved",
        "shots_total": 3 * SHOTS,
        "execution_seconds_decimal": str(sum((Decimal(row["execution_seconds_decimal"]) for row in rows), Decimal(0))),
        "jobs": rows,
        "comparisons": comparisons,
        "inputs": {
            name: digest(run / name)
            for name in ("analysis.json", "execution-state.json", "read-only-recovery-receipt.json")
        },
        "producer": {"file": Path(__file__).relative_to(ROOT).as_posix(), "sha256": digest(Path(__file__))},
        "frozen_analyzer_sha256": primary["analyzer_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json.dumps(replay(arguments.run), indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained descriptive prefix differs from exact replay")
    else:
        with arguments.out.open("x") as output:
            output.write(content)
    print("descriptive prefix replays; the complete-case refusal remains in force")


if __name__ == "__main__":
    main()
