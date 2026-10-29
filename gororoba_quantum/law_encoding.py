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
the list it received (for an all-float list, when the float64 bit patterns
agree), and a list otherwise; dense() returns a list
unchanged, so every reader accepts both record forms.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import numpy as np

DENSE_LIMIT = 4096


def _dependent_bits(values: Sequence[float], width: int) -> list[int]:
    """The outcome bits whose flip changes some entry of values.

    Viewing the vector as (2^(width - 1 - b), 2, 2^b) puts outcome x with bit
    b clear at [.., 0, ..] and x | 2^b at [.., 1, ..], so one array comparison
    per bit replaces 2^(width - 1) scalar ones.
    """
    array = np.asarray(values, dtype=float)
    return [
        bit
        for bit in range(width)
        if not np.array_equal(array.reshape(-1, 2, 1 << bit)[:, 0, :], array.reshape(-1, 2, 1 << bit)[:, 1, :])
    ]


def _truthy_indices(values: Sequence[float]) -> list[int]:
    """Indices of the entries a truth test keeps: nonzero and NaN, never 0, 0.0 or -0.0."""
    array = np.asarray(values, dtype=float)
    return np.flatnonzero(array != 0).tolist()


def _gather_array(count: int, bits: Sequence[int], forward: bool) -> np.ndarray:
    """Per k < count, the table or outcome index the bit map sends k to.

    forward maps table index k to the outcome whose bit bits[j] is bit j of k; otherwise outcome k maps to the table
    index whose bit j is bit bits[j] of k.
    """
    k = np.arange(count, dtype=np.int64)
    index = np.zeros(count, dtype=np.int64)
    for j, bit in enumerate(bits):
        if forward:
            index |= ((k >> j) & 1) << bit
        else:
            index |= ((k >> bit) & 1) << j
    return index


def _gather_index(count: int, bits: Sequence[int], forward: bool) -> list[int]:
    """_gather_array as a list; only indices are computed, so a gather through it keeps the entries' objects."""
    return _gather_array(count, bits, forward).tolist()


def encode(values: Sequence[float]) -> list[float] | dict[str, Any]:
    """values as a record stores them: a list up to DENSE_LIMIT entries, else the shorter exact form."""
    if len(values) <= DENSE_LIMIT:
        return list(values)
    length = len(values)
    width = length.bit_length() - 1
    if 1 << width != length:
        raise ValueError(f"an outcome vector of {length} entries spans no whole register")
    indices = _truthy_indices(values)
    bits = _dependent_bits(values, width)
    # A form stands only when it expands to the same JSON text: 0, 0.0 and
    # -0.0 compare equal and serialize apart. For an all-float input the text
    # is a function of the float64 bit patterns, so equal patterns accept the
    # form without serializing; any other input, and a pattern mismatch
    # (distinct NaN payloads share the text "NaN"), takes the text test.
    all_float = set(map(type, values)) == {float}
    bit_view = np.asarray(values, dtype=np.float64).view(np.int64) if all_float else None
    support: dict[str, Any] = {
        "encoding": "support",
        "length": length,
        "support": {str(index): values[index] for index in indices},
    }
    table = [values[index] for index in _gather_index(1 << len(bits), bits, forward=True)]
    junta: dict[str, Any] = {"encoding": "bits", "length": length, "bits": bits, "table": table}
    text: str | None = None
    exact = []
    for form in (support, junta):
        if bit_view is not None:
            expanded_bits = _expansion_bits(bit_view, form, indices, bits)
            if np.array_equal(bit_view, expanded_bits):
                exact.append(form)
                continue
        if text is None:
            text = json.dumps(list(values))
        if json.dumps(dense(form)) == text:
            exact.append(form)
    if not exact:
        return list(values)
    return exact[0] if len(exact) == 1 else min(exact, key=lambda form: len(json.dumps(form)))


def _expansion_bits(bit_view: np.ndarray, form: dict[str, Any], indices: list[int], bits: list[int]) -> np.ndarray:
    """The float64 bit patterns dense(form) holds, from the input's own patterns bit_view.

    A support form holds the input's pattern at each listed index and +0.0 elsewhere; a bit-table form holds the
    input's pattern at the table's source indices, spread over the outcomes that depend on those bits only.
    """
    if form["encoding"] == "support":
        out = np.zeros_like(bit_view)
        out[indices] = bit_view[indices]
        return out
    table_bits = bit_view[_gather_array(1 << len(bits), bits, forward=True)]
    return table_bits[_gather_array(len(bit_view), bits, forward=False)]


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
        return [table[index] for index in _gather_index(length, bits, forward=False)]
    raise ValueError(f"unknown outcome vector encoding {stored.get('encoding')!r}")
