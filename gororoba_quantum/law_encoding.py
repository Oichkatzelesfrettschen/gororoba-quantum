"""Lossless record encoding of vectors over a register's classical outcomes.

A record stores a member's ideal law, each replica's noisy law and each
observable term's score values, and collect.json each replica's measured
law, as one number per outcome, index = the outcome's bits little-endian. A
vector of at most DENSE_LIMIT entries stays a JSON list, so every record over
at most 12 classical bits keeps its dense bytes. A longer vector is stored as the shorter of two exact forms:

- support: {"encoding": "support", "length": n, "support": {"index": value}}
  lists every nonzero entry; a law over a few outcomes of a wide register
  takes one entry per outcome it reaches.
- bits: {"encoding": "bits", "length": n, "bits": [b, ...], "table": [...]}
  holds a vector that depends on outcome bits b only, table index
  sum_j bit_(b_j)(x) 2^j; a score that reads one segment bit of a 15-bit
  outcome takes two entries.

encode() keeps a form only when dense() of it serializes to the JSON text of
the list it received, and a list otherwise; dense() returns a list
unchanged, so every reader accepts both record forms.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

DENSE_LIMIT = 4096


def _dependent_bits(values: Sequence[float], width: int) -> list[int]:
    """The outcome bits whose flip changes some entry of values."""
    found = []
    for bit in range(width):
        step = 1 << bit
        if any(values[x] != values[x | step] for x in range(len(values)) if not x & step):
            found.append(bit)
    return found


def encode(values: Sequence[float]) -> list[float] | dict[str, Any]:
    """values as a record stores them: a list up to DENSE_LIMIT entries, else the shorter exact form."""
    if len(values) <= DENSE_LIMIT:
        return list(values)
    length = len(values)
    width = length.bit_length() - 1
    if 1 << width != length:
        raise ValueError(f"an outcome vector of {length} entries spans no whole register")
    support: dict[str, Any] = {
        "encoding": "support",
        "length": length,
        "support": {str(index): value for index, value in enumerate(values) if value},
    }
    bits = _dependent_bits(values, width)
    table = [values[sum(((k >> j) & 1) << bit for j, bit in enumerate(bits))] for k in range(1 << len(bits))]
    junta: dict[str, Any] = {"encoding": "bits", "length": length, "bits": bits, "table": table}
    # A form stands only when it expands to the same JSON text: 0, 0.0 and
    # -0.0 compare equal and serialize apart.
    text = json.dumps(list(values))
    exact = [form for form in (support, junta) if json.dumps(dense(form)) == text]
    return min(exact, key=lambda form: len(json.dumps(form))) if exact else list(values)


def dense(stored: Any) -> list[float]:
    """The per-outcome list a record field stores, from a list, an in-memory tuple or either encoded form."""
    if isinstance(stored, list | tuple):
        return list(stored) if isinstance(stored, tuple) else stored
    if not isinstance(stored, dict) or not isinstance(stored.get("length"), int):
        raise ValueError(f"an outcome vector is neither a list nor an encoded form: {type(stored).__name__}")
    length = stored["length"]
    if stored.get("encoding") == "support":
        out: list[Any] = [0.0] * length
        for index, value in stored["support"].items():
            position = int(index)
            if not 0 <= position < length:
                raise ValueError(f"support index {position} lies outside {length} outcomes")
            out[position] = value
        return out
    if stored.get("encoding") == "bits":
        bits, table = stored["bits"], stored["table"]
        if len(table) != 1 << len(bits) or any(not 0 <= bit < length.bit_length() - 1 for bit in bits):
            raise ValueError("a bit-table form names bits outside its register or a table of the wrong size")
        return [table[sum(((x >> bit) & 1) << j for j, bit in enumerate(bits))] for x in range(length)]
    raise ValueError(f"unknown outcome vector encoding {stored.get('encoding')!r}")
