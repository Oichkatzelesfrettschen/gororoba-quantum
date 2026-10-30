"""Exact arithmetic for the unapproved Tuna destination-response working case.

The scoring core accepts already classified job-level inputs. It does not validate
provider identity, assignment concealment, observation time, raw shots or admission.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

SHOTS = 4096
MAX_SLOTS = 24
THRESHOLD = Fraction(400)
NEUTRAL_KINDS = frozenset({"confirmed_failure", "partial", "unavailable"})


def decode_counts(arm: str, shots: object) -> dict[str, int]:
    """Decode the two specified q6 destinations from complete width-20 shots."""
    if arm not in {"baseline", "rotated"}:
        raise ValueError("unknown destination assignment")
    if (
        not isinstance(shots, list)
        or len(shots) != SHOTS
        or any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots)
    ):
        raise ValueError("complete result requires 4096 width-20 binary shots")
    early_offset = 0 if arm == "baseline" else 1
    return {
        "early_ones": sum(shot[early_offset] == "1" for shot in shots),
        "terminal_ones": sum(shot[13] == "1" for shot in shots),
    }


def score_sequence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Score ordered classified slots exactly, refusing observations after a stop."""
    if not isinstance(rows, list) or len(rows) > MAX_SLOTS:
        raise ValueError("score requires at most 24 ordered slots")
    processes: dict[str, dict[str, Any]] = {}
    products: dict[str, tuple[Fraction, Fraction]] = {}
    for response in ("early", "terminal"):
        for direction in ("positive", "negative"):
            name = f"{response}_{direction}"
            processes[name] = {"value": Fraction(1), "maximum": Fraction(1), "first_crossing": None}
            products[name] = (Fraction(1), Fraction(1))
    stop_reason: str | None = None
    for slot, row in enumerate(rows, start=1):
        if stop_reason is not None:
            raise ValueError("observation after stop is inadmissible")
        if not isinstance(row, dict) or type(row.get("slot")) is not int or row["slot"] != slot:
            raise ValueError("slot identity must be contiguous and ordered")
        arm = row.get("arm")
        kind = row.get("kind")
        if (
            not isinstance(arm, str)
            or arm not in {"baseline", "rotated"}
            or not isinstance(kind, str)
            or kind not in NEUTRAL_KINDS | {"complete"}
        ):
            raise ValueError("slot assignment or classification is invalid")
        if kind == "complete":
            if set(row) != {"slot", "arm", "kind", "early_ones", "terminal_ones"}:
                raise ValueError("complete slot must contain exactly two response counts")
            for field in ("early_ones", "terminal_ones"):
                if type(row[field]) is not int or not 0 <= row[field] <= SHOTS:
                    raise ValueError("response count must be an integer between zero and 4096")
            outcomes = {response: Fraction(row[f"{response}_ones"], SHOTS) for response in ("early", "terminal")}
        else:
            if set(row) != {"slot", "arm", "kind"}:
                raise ValueError("neutral slot cannot carry response counts")
            outcomes = {"early": Fraction(1, 2), "terminal": Fraction(1, 2)}
        assignment = 1 if arm == "rotated" else -1
        for response in ("early", "terminal"):
            score = 2 * assignment * (outcomes[response] - Fraction(1, 2))
            for direction, sign in (("positive", 1), ("negative", -1)):
                name = f"{response}_{direction}"
                full, half = products[name]
                full *= 1 + sign * score
                half *= 1 + sign * score / 2
                products[name] = (full, half)
                value = Fraction(9, 10) * full + Fraction(1, 10) * half
                process = processes[name]
                process["value"] = value
                process["maximum"] = max(process["maximum"], value)
                if value >= THRESHOLD and process["first_crossing"] is None:
                    process["first_crossing"] = slot
        if kind != "complete":
            stop_reason = kind
        elif all(
            any(
                processes[f"{response}_{direction}"]["first_crossing"] is not None
                for direction in ("positive", "negative")
            )
            for response in ("early", "terminal")
        ):
            stop_reason = "both_observables_crossed"
        elif slot == MAX_SLOTS:
            stop_reason = "slot_limit"
    return {"processes": processes, "slots_scored": len(rows), "stop_reason": stop_reason}
