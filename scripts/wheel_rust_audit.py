"""Differential audit of the Rust wheel crate 0.1.0 against gororoba_quantum/wheel_algebra.py.

The crate's w64 wraps one IEEE binary64 value and reads it by category:
+-0 is the wheel's 0, +-inf its infinity /0, every NaN its bottom 0/0, and
every other value (subnormals included) a finite element. Its operations
dispatch on the categories by Carlstrom's wheel-of-fractions table and hand
two finite operands to the hardware +, * or 1.0 / x. The harness under
docs/evidence/wheel_rust_audit/harness/ prints every unary and binary w64
operation on a fixed binary64 corpus, and both sides of every law of
wheel_algebra.axioms plus the p. 5 identity x - x = 0x^2 on seeded triples,
as 16-hex-digit bit patterns; it does the same for the exact qw64 type on a
rational corpus and records qw8 integer-overflow probes under both overflow
profiles.

This script reads those bit patterns by integer arithmetic alone and runs
three models of every case:

- exact: wheel_algebra.Wheel over Q on the exactly mapped inputs;
- rules: the crate's category table over exact rationals;
- rounded: the rules model with each finite result rounded to binary64 by
  round_binary64, round to nearest even over integers.

The rounded model must reproduce every crate bit pattern and every law
outcome. An operation case is ``a`` (agree: the crate value equals the exact
element), ``i`` (inexact: the crate value is the binary64 rounding of a
finite exact value), ``o`` (overflow: the exact value is finite and rounds to
+-inf, which the crate reads as infinity), ``u`` (underflow: the exact value
is nonzero and rounds to +-0), ``d`` (composite rounding: x / y is x * /y,
two roundings, and the result differs from the rounding of the exact
quotient within the exact value's wheel class), ``c`` (the same composite
rounding moves the result to another wheel class: finite, infinity or
bottom) or ``s`` (structural: any other difference, or a crate pattern the
rounded model does not reproduce).

A law case is ``a`` when it holds in the crate. A failing case whose rules
model and exact evaluation both hold is ``i`` when every rounding on the way
was finite and inexact and both crate sides keep the exact sides' wheel
classes, ``o`` when an overflow or underflow occurred and the classes are
kept, and ``c`` when a crate side lands in another wheel class; anything
else is ``s``. Law trees come from wheel_algebra.axioms itself, evaluated on
symbolic operands, so the audit tests the module's own expressions.

``--out DIR`` writes DIR/classification.json from DIR's harness outputs.
``--check DIR`` recomputes it from the retained outputs and requires it byte
for byte, with the source digests. ``--self-test`` checks round_binary64
against float(Fraction) and the overflow and subnormal boundaries, and
requires --check's comparison to reject a flipped classification and a
corrupted bit pattern.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import random
import struct
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
import wheel_algebra as wa  # noqa: E402

EVIDENCE = ROOT / "docs/evidence/wheel_rust_audit"
CRATE_ARCHIVE = ROOT / "docs/source_archives/wheel-0.1.0.crate"
CRATE = {
    "name": "wheel",
    "version": "0.1.0",
    "crate_sha256": "2fb7ccae7d01d16dca5a39f58376ae6277467a8e3bea3fe45c20f72b4ee2c58b",
    "license": "Apache-2.0 OR MPL-2.0",
    "source_url": "https://static.crates.io/crates/wheel/wheel-0.1.0.crate",
    "repository": "https://github.com/menhera-org/wheel-rs",
    "vcs_commit": "630d82071e9d0bebd0cffb5b249526c10e6c371c",
}
TOOLCHAIN = "rustc 1.98.1 (48a229cea 2026-09-01), cargo 1.98.1 (797e8a9bc 2026-08-05)"
HARNESS_FILES = ("harness/Cargo.toml", "harness/Cargo.lock", "harness/src/main.rs")
FULL_OUTPUT = "harness-debug.json"
RELEASE_OUTPUT = "harness-release-qw8.json"
RECORD = "classification.json"
SCHEMA = "wheel-rust-audit-v1"

# The harness constants (main.rs FIXED, AXIOM_POOL, QW_CORPUS, SEED,
# RANDOM_DYADICS, RANDOM_TRIPLES); --check requires the outputs to carry them.
FIXED = (
    0x0000000000000000,
    0x8000000000000000,
    0x3FF0000000000000,
    0xBFF0000000000000,
    0x7FF0000000000000,
    0xFFF0000000000000,
    0x7FF8000000000000,
    0x7FF8000000000001,
    0xFFF8000000000000,
    0x7FF0000000000001,
    0x3FE0000000000000,
    0xBFD0000000000000,
    0x4000000000000000,
    0x4008000000000000,
    0xC000000000000000,
    0x3FF8000000000000,
    0x3FD8000000000000,
    0xC01B000000000000,
    0x4090000000000000,
    0x3F50000000000000,
    0x4014000000000000,
    0x401C000000000000,
    0x4024000000000000,
    0x3FB999999999999A,
    0x3FD5555555555555,
    0xBFE5555555555555,
    0x4340000000000000,
    0x4340000000000001,
    0x3FF0000000000001,
    0x7FEFFFFFFFFFFFFF,
    0xFFEFFFFFFFFFFFFF,
    0x7FE0000000000000,
    0x7FE1CCF385EBC8A0,
    0x6570000000000000,
    0x1A70000000000000,
    0x0010000000000000,
    0x0000000000000001,
    0x8000000000000001,
    0x000FFFFFFFFFFFFF,
)
AXIOM_POOL = (0, 1, 2, 3, 4, 5, 6, 9, 13, 10, 24, 23, 29, 35, 36, 33)
QW_CORPUS = (
    (0, 1),
    (1, 1),
    (-1, 1),
    (1, 0),
    (0, 0),
    (3, 2),
    (-2, 5),
    (7, 1),
    (1, 3),
    (-5, 6),
    (2, -4),
    (-3, 0),
    (12, 1),
    (-1, 7),
)
SEED = 20241022
RANDOM_DYADICS = 16
RANDOM_TRIPLES = 1024
P5_LAW = "(p. 5) x - x = 0x^2"
OPS = ("add", "sub", "mul", "div")
# Per qw8 probe: the exact result, and whether its i8 arithmetic overflows
# (an intermediate product, sum, negation or absolute value outside i8).
QW8_PROBES: dict[str, tuple[Fraction | bool, bool]] = {
    "(1/2) + (1/3)": (Fraction(5, 6), False),
    "(1/16) * (1/16)": (Fraction(1, 256), True),
    "100 + 100": (Fraction(200), True),
    "64 * 2": (Fraction(128), True),
    "-(-128)": (Fraction(128), True),
    "/(-128)": (Fraction(-1, 128), True),
    "127/2 == 127/3": (False, True),
    "127/2 == 127/2": (True, True),
}
ROUNDING_EVENTS = {"inexact": "i", "overflow": "o", "underflow": "u"}
OPERATION_CLASSES = dict.fromkeys("a", "agree") | dict.fromkeys("ioud", "rounding") | dict.fromkeys("cs", "structural")
LAW_CLASSES = dict.fromkeys("a", "agree") | dict.fromkeys("iocs", "structural")
# (law, triple) cases per ordered_map item.
CASES_PER_CHUNK = 1024

MASK52 = (1 << 52) - 1
NAN_BITS = 0x7FF8000000000000
INF_BITS = 0x7FF0000000000000
ZERO_BITS = 0
ONE_BITS = 0x3FF0000000000000
NEG_ONE_BITS = 0xBFF0000000000000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- binary64 by integer arithmetic -----------------------------------------


def category(bits: int) -> str:
    """The crate's FpWheelCategory: z (+-0), i (+-inf), b (NaN), n (finite nonzero)."""
    field = (bits >> 52) & 0x7FF
    if field == 0x7FF:
        return "b" if bits & MASK52 else "i"
    if field == 0 and not bits & MASK52:
        return "z"
    return "n"


@functools.lru_cache(maxsize=1 << 16)
def decode(bits: int) -> Fraction:
    """The exact value of a finite binary64 pattern."""
    field = (bits >> 52) & 0x7FF
    require(field != 0x7FF, f"{bits:016x} is not finite")
    mantissa = bits & MASK52 if field == 0 else (1 << 52) | bits & MASK52
    shift = max(field, 1) - 1075
    value = Fraction(mantissa << shift) if shift >= 0 else Fraction(mantissa, 1 << -shift)
    return -value if bits >> 63 else value


def round_binary64(q: Fraction) -> tuple[int, str]:
    """IEEE 754 round-to-nearest-even of q to binary64, as (bits, event).

    The event is "exact", "inexact", "overflow" (|q| rounds past f64::MAX,
    from 2^1024 - 2^970 up) or "underflow" (q != 0 rounds to zero). An exact
    zero gives +0.
    """
    if q == 0:
        return ZERO_BITS, "exact"
    sign = 1 << 63 if q < 0 else 0
    n, d = abs(q.numerator), q.denominator
    e = n.bit_length() - d.bit_length()
    if (n << max(0, -e)) < (d << max(0, e)):
        e -= 1
    quantum = max(e, -1022) - 52
    num, den = (n, d << quantum) if quantum >= 0 else (n << -quantum, d)
    m, r = divmod(num, den)
    if 2 * r > den or (2 * r == den and m & 1):
        m += 1
    if m == 1 << 53:
        m >>= 1
        quantum += 1
    if m == 0:
        return sign, "underflow"
    event = "exact" if r == 0 else "inexact"
    if m < 1 << 52:
        return sign | m, event
    field = quantum + 52 + 1023
    if field >= 0x7FF:
        return sign | INF_BITS, "overflow"
    return sign | (field << 52) | (m - (1 << 52)), event


@functools.lru_cache(maxsize=1 << 16)
def to_wheel(bits: int) -> wa.Wheel:
    """The wheel element the crate reads from a binary64 pattern."""
    kind = category(bits)
    if kind == "b":
        return wa.BOTTOM
    if kind == "i":
        return wa.INFINITY
    if kind == "z":
        return wa.ZERO
    return wa.Wheel(decode(bits))


# --- the crate's category table ----------------------------------------------


class Value:
    """A w64 value in a model: its category, its exact value if finite nonzero, and its bits when rounded."""

    __slots__ = ("kind", "q", "bits")

    def __init__(self, kind: str, q: Fraction | None, bits: int | None) -> None:
        self.kind, self.q, self.bits = kind, q, bits

    @staticmethod
    @functools.lru_cache(maxsize=1 << 16)
    def of_bits(bits: int) -> Value:
        """The value of a bit pattern; cached instances are never mutated."""
        kind = category(bits)
        return Value(kind, decode(bits) if kind == "n" else None, bits)

    def __eq__(self, other: object) -> bool:
        """Wheel64::eq: equal categories, and equal values within the finite nonzero category."""
        return isinstance(other, Value) and self.kind == other.kind and (self.kind != "n" or self.q == other.q)

    def __hash__(self) -> int:
        return hash((self.kind, self.q))

    def wheel(self) -> wa.Wheel:
        if self.kind == "n":
            return wa.Wheel(cast(Fraction, self.q))
        return {"z": wa.ZERO, "i": wa.INFINITY, "b": wa.BOTTOM}[self.kind]


class CrateModel:
    """Wheel64's add, mul and inv dispatch over exact values, rounding finite results when ``rounded``."""

    def __init__(self, rounded: bool) -> None:
        self.rounded = rounded
        self.events: set[str] = set()
        self.zero = self.constant(ZERO_BITS)
        self.one = self.constant(ONE_BITS)
        self.neg_one = self.constant(NEG_ONE_BITS)
        self.nan = self.constant(NAN_BITS)
        self.inf = self.constant(INF_BITS)

    def constant(self, bits: int) -> Value:
        value = Value.of_bits(bits)
        return value if self.rounded else Value(value.kind, value.q, None)

    def lift(self, bits: int) -> Value:
        return self.constant(bits)

    def finite(self, q: Fraction) -> Value:
        if not self.rounded:
            return Value("n", q, None) if q else self.zero
        bits, event = round_binary64(q)
        self.events.add(event)
        return Value.of_bits(bits)

    def add(self, a: Value, b: Value) -> Value:
        if a.kind == "b" or b.kind == "b" or (a.kind == "i" and b.kind == "i"):
            return self.nan
        if a.kind == "i" or b.kind == "i":
            return self.inf
        if b.kind == "z":
            return a
        if a.kind == "z":
            return b
        return self.finite(cast(Fraction, a.q) + cast(Fraction, b.q))

    def mul(self, a: Value, b: Value) -> Value:
        if a.kind == "b" or b.kind == "b" or {a.kind, b.kind} == {"i", "z"}:
            return self.nan
        if a.kind == "i" or b.kind == "i":
            return self.inf
        if a.kind == "z" or b.kind == "z":
            return self.zero
        return self.finite(cast(Fraction, a.q) * cast(Fraction, b.q))

    def inv(self, a: Value) -> Value:
        if a.kind == "b":
            return self.nan
        if a.kind == "i":
            return self.zero
        if a.kind == "z":
            return self.inf
        return self.finite(1 / cast(Fraction, a.q))

    def neg(self, a: Value) -> Value:
        return self.mul(a, self.neg_one)

    def binary(self, op: str, a: Value, b: Value) -> Value:
        if op == "add":
            return self.add(a, b)
        if op == "sub":
            return self.add(a, self.neg(b))
        if op == "mul":
            return self.mul(a, b)
        return self.mul(a, self.inv(b))


def exact_binary(op: str, a: wa.Wheel, b: wa.Wheel) -> wa.Wheel:
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    if op == "mul":
        return a * b
    return a / b


# --- law trees from wheel_algebra.axioms --------------------------------------

Tree = tuple[Any, ...]


class Symbol:
    """A symbolic operand; == records the two sides of a law instead of comparing."""

    __slots__ = ("tree",)
    sides: list[tuple[Tree, Tree]] = []

    def __init__(self, tree: Tree) -> None:
        self.tree = tree

    def __eq__(self, other: object) -> bool:
        Symbol.sides.append((self.tree, leaf(other)))
        return True

    __hash__ = None  # type: ignore[assignment]


def leaf(value: Any) -> Tree:
    if isinstance(value, Symbol):
        return value.tree
    require(value in (wa.ZERO, wa.ONE), f"unexpected constant {value!r}")
    return ("const", ZERO_BITS if value == wa.ZERO else ONE_BITS)


def law_trees() -> dict[str, tuple[Tree, Tree]]:
    """(left, right) expression trees of every wheel_algebra.axioms law and the p. 5 identity."""
    ops = (
        lambda a, b: Symbol(("add", leaf(a), leaf(b))),
        lambda a, b: Symbol(("mul", leaf(a), leaf(b))),
        lambda a: Symbol(("inv", leaf(a))),
    )
    laws = wa.axioms(cast(wa.Ops, ops))
    x, y, z = Symbol(("var", 0)), Symbol(("var", 1)), Symbol(("var", 2))
    trees: dict[str, tuple[Tree, Tree]] = {}
    for name, law in laws.items():
        Symbol.sides.clear()
        law(cast(wa.Wheel, x), cast(wa.Wheel, y), cast(wa.Wheel, z))
        require(len(Symbol.sides) == 1, f"{name} compares {len(Symbol.sides)} pairs")
        trees[name] = Symbol.sides[0]
    # p. 5: x - x = 0x^2 with -x = (-1)x; the crate's x - x is x + x * (-1).
    trees[P5_LAW] = (
        ("add", ("var", 0), ("mul", ("var", 0), ("const", NEG_ONE_BITS))),
        ("mul", ("mul", ("const", ZERO_BITS), ("var", 0)), ("var", 0)),
    )
    return trees


def evaluate(
    tree: Tree,
    env: Sequence[Any],
    add: Callable[..., Any],
    mul: Callable[..., Any],
    inv: Callable[..., Any],
    const: Callable[[int], Any],
) -> Any:
    head = tree[0]
    if head == "var":
        return env[tree[1]]
    if head == "const":
        return const(tree[1])
    if head == "inv":
        return inv(evaluate(tree[1], env, add, mul, inv, const))
    left = evaluate(tree[1], env, add, mul, inv, const)
    right = evaluate(tree[2], env, add, mul, inv, const)
    return add(left, right) if head == "add" else mul(left, right)


def exact_constant(bits: int) -> wa.Wheel:
    return to_wheel(bits)


def kind_of(w: wa.Wheel) -> str:
    return {"finite": "n", "infinity": "i", "bottom": "b"}[w.kind()]


def wheel_kind(value: Value) -> str:
    """Wheel class of a model value: n (finite, zero included), i or b."""
    return "n" if value.kind in ("z", "n") else value.kind


# --- classification ----------------------------------------------------------


def classify_op(crate_bits: int, model: Value, rules: Value, exact: wa.Wheel) -> str:
    """One operation case: a, i, o, u, d, c or s (module docstring)."""
    if model.bits != crate_bits:
        return "s"
    crate = Value.of_bits(crate_bits)
    if crate.wheel() == exact:
        return "a"
    if exact.finite:
        bits, event = round_binary64(exact.value())
        if bits == crate_bits and event in ROUNDING_EVENTS:
            return ROUNDING_EVENTS[event]
    if rules.wheel() != exact:
        return "s"
    return "d" if wheel_kind(crate) == kind_of(exact) else "c"


def unary_values(model: CrateModel, op: str, a_bits: int) -> Value:
    a = model.lift(a_bits)
    return model.neg(a) if op == "neg" else model.inv(a)


def classify_unary(corpus: Sequence[int], outputs: Sequence[int], op: str) -> str:
    letters = []
    for a_bits, out in zip(corpus, outputs, strict=True):
        exact = -to_wheel(a_bits) if op == "neg" else to_wheel(a_bits).inv()
        rounded = unary_values(CrateModel(rounded=True), op, a_bits)
        rules = unary_values(CrateModel(rounded=False), op, a_bits)
        letters.append(classify_op(out, rounded, rules, exact))
    return "".join(letters)


class BinaryRow:
    """The classes of one row a (op) b over the corpus."""

    def __init__(self, corpus: Sequence[int]) -> None:
        self.corpus = list(corpus)

    def __call__(self, item: tuple[str, int, list[int]]) -> str:
        op, row, outputs = item
        letters = []
        a_bits = self.corpus[row]
        for b_bits, out in zip(self.corpus, outputs, strict=True):
            rounded, rules = CrateModel(rounded=True), CrateModel(rounded=False)
            value = rounded.binary(op, rounded.lift(a_bits), rounded.lift(b_bits))
            ideal = rules.binary(op, rules.lift(a_bits), rules.lift(b_bits))
            exact = exact_binary(op, to_wheel(a_bits), to_wheel(b_bits))
            letters.append(classify_op(out, value, ideal, exact))
        return "".join(letters)


LawCase = tuple[int, tuple[int, int, int], bool, tuple[int, int] | None]


class LawCases:
    """Classes of a chunk of (law, triple, crate holds, crate failing sides) cases over w64."""

    def __init__(self, corpus: Sequence[int], laws: Sequence[str]) -> None:
        self.corpus = list(corpus)
        self.laws = list(laws)

    def __call__(self, chunk: list[LawCase]) -> list[str]:
        trees = law_trees()
        out = []
        for law, (i, j, k), crate_holds, sides in chunk:
            left, right = trees[self.laws[law]]
            triple = (self.corpus[i], self.corpus[j], self.corpus[k])
            rounded = CrateModel(rounded=True)
            env = [rounded.lift(b) for b in triple]
            r_left = evaluate(left, env, rounded.add, rounded.mul, rounded.inv, rounded.constant)
            r_right = evaluate(right, env, rounded.add, rounded.mul, rounded.inv, rounded.constant)
            exact_env = [to_wheel(b) for b in triple]
            e_left = evaluate(left, exact_env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant)
            e_right = evaluate(right, exact_env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant)
            exact_holds = e_left == e_right
            model_holds = r_left == r_right
            if model_holds != crate_holds or (sides is not None and sides != (r_left.bits, r_right.bits)):
                out.append("s")
                continue
            if crate_holds:
                out.append("a" if exact_holds else "s")
                continue
            rules = CrateModel(rounded=False)
            rules_env = [rules.lift(b) for b in triple]
            rules_holds = evaluate(left, rules_env, rules.add, rules.mul, rules.inv, rules.constant) == evaluate(
                right, rules_env, rules.add, rules.mul, rules.inv, rules.constant
            )
            if not (exact_holds and rules_holds):
                out.append("s")
                continue
            if wheel_kind(r_left) != kind_of(e_left) or wheel_kind(r_right) != kind_of(e_right):
                out.append("c")
            else:
                out.append("i" if rounded.events <= {"exact", "inexact"} else "o")
        return out


def parse_bits(text: str) -> int:
    require(len(text) == 16 and all(c in "0123456789abcdef" for c in text), f"bit pattern {text!r}")
    return int(text, 16)


def splitmix64(state: int) -> tuple[int, int]:
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


def harness_corpus() -> tuple[list[int], list[tuple[int, int, int]]]:
    """The harness's w64 corpus and triples, regenerated from its SplitMix64 stream."""
    state = SEED
    corpus = list(FIXED)
    for _ in range(RANDOM_DYADICS):
        state, r = splitmix64(state)
        corpus.append((r >> 63) << 63 | (1023 - 40 + (r >> 32) % 81) << 52 | (r & 0xFFFFF) << 32)
    triples = [(i, j, k) for i in AXIOM_POOL for j in AXIOM_POOL for k in AXIOM_POOL]
    for _ in range(RANDOM_TRIPLES):
        drawn = []
        for _ in range(3):
            state, r = splitmix64(state)
            drawn.append(r % len(corpus))
        triples.append((drawn[0], drawn[1], drawn[2]))
    return corpus, triples


def holds_flags(text: str, count: int) -> list[bool]:
    require(len(text) == -(-count // 4), "hold flag length")
    flags = [bool(int(text[t // 4], 16) >> (t % 4) & 1) for t in range(count)]
    require(int(text[-1], 16) >> (count % 4 or 4) == 0, "hold flag padding")
    return flags


def law_cases(section: dict[str, Any], count: int, laws: Sequence[str], parse: Callable[[Any], Any]) -> list[Any]:
    failures: dict[tuple[int, int], tuple[Any, Any]] = {}
    for law, t, left, right in section["failures"]:
        require((law, t) not in failures, "duplicate failure row")
        failures[(law, t)] = (parse(left), parse(right))
    rows = []
    for law in range(len(laws)):
        flags = holds_flags(section["holds"][law], count)
        for t, holds in enumerate(flags):
            require(holds != ((law, t) in failures), f"law {law} triple {t}: flag and failure rows disagree")
            rows.append((law, t, holds, failures.get((law, t))))
    return rows


def classify_w64(doc: dict[str, Any], laws: Sequence[str]) -> dict[str, Any]:
    corpus, triples = harness_corpus()
    w64 = doc["w64"]
    require([parse_bits(b) for b in w64["corpus"]] == corpus, "w64 corpus differs from the harness definition")
    require([tuple(t) for t in w64["triples"]] == triples, "w64 triples differ from the harness definition")
    classes: dict[str, Any] = {}
    for op in ("neg", "inv"):
        classes[op] = classify_unary(corpus, [parse_bits(b) for b in w64[op]], op)
    items = [(op, row, [parse_bits(b) for b in w64[op][row]]) for op in OPS for row in range(len(corpus))]
    rows = parallel.ordered_map(BinaryRow(corpus), items, min_items=2)
    for index, op in enumerate(OPS):
        classes[op] = rows[index * len(corpus) : (index + 1) * len(corpus)]
    cases = [(law, triples[t], holds, sides) for law, t, holds, sides in law_cases(w64, len(triples), laws, parse_bits)]
    chunks = [cases[start : start + CASES_PER_CHUNK] for start in range(0, len(cases), CASES_PER_CHUNK)]
    letters = [c for chunk in parallel.ordered_map(LawCases(corpus, laws), chunks, min_items=2) for c in chunk]
    classes["laws"] = {
        name: "".join(letters[index * len(triples) : (index + 1) * len(triples)]) for index, name in enumerate(laws)
    }
    return classes


def canonical(w: wa.Wheel) -> list[int]:
    if w.bottom:
        return [0, 0]
    if w.infinite:
        return [1, 0]
    q = w.value()
    return [q.numerator, q.denominator]


def classify_qw64(doc: dict[str, Any], laws: Sequence[str]) -> dict[str, Any]:
    """qw64 cases: a when the crate's pair is the exact canonical pair, s otherwise."""
    qw = doc["qw64"]
    require([tuple(p) for p in qw["inputs"]] == list(QW_CORPUS), "qw64 inputs differ from the harness definition")
    corpus = [wa.Wheel(n, d) for n, d in QW_CORPUS]
    classes: dict[str, Any] = {
        "corpus": "".join("a" if p == canonical(w) else "s" for p, w in zip(qw["corpus"], corpus, strict=True)),
        "neg": "".join("a" if p == canonical(-w) else "s" for p, w in zip(qw["neg"], corpus, strict=True)),
        "inv": "".join("a" if p == canonical(w.inv()) else "s" for p, w in zip(qw["inv"], corpus, strict=True)),
    }
    for op in OPS:
        classes[op] = [
            "".join("a" if p == canonical(exact_binary(op, a, b)) else "s" for p, b in zip(row, corpus, strict=True))
            for row, a in zip(qw[op], corpus, strict=True)
        ]
    size = len(corpus)
    triples = [(i, j, k) for i in range(size) for j in range(size) for k in range(size)]
    cases = [(law, triples[t], holds) for law, t, holds, _sides in law_cases(qw, len(triples), laws, tuple)]
    chunks = [cases[start : start + CASES_PER_CHUNK] for start in range(0, len(cases), CASES_PER_CHUNK)]
    letters = [c for chunk in parallel.ordered_map(QwLawCases(laws), chunks, min_items=2) for c in chunk]
    classes["laws"] = {
        name: "".join(letters[index * len(triples) : (index + 1) * len(triples)]) for index, name in enumerate(laws)
    }
    return classes


class QwLawCases:
    """Classes of a chunk of (law, triple, crate holds) cases over qw64: a when both hold, s otherwise."""

    def __init__(self, laws: Sequence[str]) -> None:
        self.laws = list(laws)

    def __call__(self, chunk: list[tuple[int, tuple[int, int, int], bool]]) -> list[str]:
        trees = law_trees()
        corpus = [wa.Wheel(n, d) for n, d in QW_CORPUS]
        out = []
        for law, triple, holds in chunk:
            left, right = trees[self.laws[law]]
            env = [corpus[i] for i in triple]
            exact = evaluate(left, env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant) == evaluate(
                right, env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant
            )
            out.append("a" if holds and exact else "s")
        return out


def classify_qw8(probes: Sequence[dict[str, Any]], overflow_checks: bool) -> dict[str, str]:
    """Per probe: a (exact result), p (panic on overflow) or s (a wrong value, wrapped)."""
    require([p["probe"] for p in probes] == list(QW8_PROBES), "qw8 probe list differs")
    out = {}
    for probe in probes:
        exact, overflows = QW8_PROBES[probe["probe"]]
        result = probe["result"]
        # Overflow checks panic exactly on the probes whose i8 arithmetic overflows; wrapping never panics.
        require((result == "panic") == (overflow_checks and overflows), f"qw8 {probe['probe']} panic behavior")
        if result == "panic":
            out[probe["probe"]] = "p"
            continue
        if isinstance(exact, bool):
            out[probe["probe"]] = "a" if result is exact else "s"
            continue
        out[probe["probe"]] = "a" if result == canonical(wa.Wheel(exact)) else "s"
    return out


def task_counts(classes: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Cases per audit class: agree, rounding or structural, with the unexplained (s) cases.

    An operation is rounding when the crate value is the binary64 rounding of
    the exact value (i, o, u) or of its defining steps x * /y (d), and
    structural when its wheel class differs from the exact one (c) or the
    rounded model fails to reproduce it (s). A law case that fails in the
    crate is structural whatever its cause, since it holds exactly.
    """
    operations = {"agree": 0, "rounding": 0, "structural": 0, "unexplained": 0}
    laws = dict(operations)
    for name, value in classes.items():
        texts = list(value.values()) if name == "laws" else value if isinstance(value, list) else [value]
        table, mapping = (laws, LAW_CLASSES) if name == "laws" else (operations, OPERATION_CLASSES)
        for text in texts:
            for letter in text:
                table[mapping[letter]] += 1
                table["unexplained"] += letter == "s"
    return {"operations": operations, "laws": laws}


def counts(classes: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Per operation and per law, the number of cases of each class."""
    table: dict[str, dict[str, int]] = {}

    def tally(name: str, text: str) -> None:
        row = table.setdefault(name, {})
        for letter in text:
            row[letter] = row.get(letter, 0) + 1

    for name, value in classes.items():
        if name == "laws":
            for law, text in value.items():
                tally(law, text)
        elif isinstance(value, list):
            tally(name, "".join(value))
        else:
            tally(name, value)
    return {name: dict(sorted(row.items())) for name, row in table.items()}


def build_record(directory: Path) -> dict[str, Any]:
    full_path, release_path = directory / FULL_OUTPUT, directory / RELEASE_OUTPUT
    full = json.loads(full_path.read_text())
    release = json.loads(release_path.read_text())
    trees = law_trees()
    laws = list(trees)
    for doc, section, checks in ((full, "full", True), (release, "qw8-overflow", False)):
        require(doc["schema"] == "wheel-rust-audit-harness-v1" and doc["crate"] == "wheel 0.1.0", "harness identity")
        require(doc["section"] == section and doc["overflow_checks"] is checks, f"{section} profile")
        require(doc["seed"] == SEED and doc["laws"] == laws, "harness seed or law list")
    w64 = classify_w64(full, laws)
    qw64 = classify_qw64(full, laws)
    record = {
        "schema": SCHEMA,
        "crate": CRATE,
        "toolchain": TOOLCHAIN,
        "sources": {name: sha256_file(directory / name) for name in (*HARNESS_FILES, FULL_OUTPUT, RELEASE_OUTPUT)},
        "laws": laws,
        "corpus_size": len(full["w64"]["corpus"]),
        "triples": len(full["w64"]["triples"]),
        "w64": {"task_counts": task_counts(w64), "counts": counts(w64), "classes": w64},
        "qw64": {"task_counts": task_counts(qw64), "counts": counts(qw64), "classes": qw64},
        "qw8_overflow": {
            "overflow_checks": classify_qw8(full["qw8_overflow"], True),
            "wrapping": classify_qw8(release["qw8_overflow"], False),
        },
    }
    return record


def dump(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=False) + "\n"


def mismatches(retained: Any, recomputed: Any, path: str = "") -> list[str]:
    """Paths at which a retained record and a recomputed one differ."""
    if isinstance(retained, dict) and isinstance(recomputed, dict):
        out = [f"{path}/{key}" for key in sorted(set(retained) ^ set(recomputed))]
        for key in retained.keys() & recomputed.keys():
            out += mismatches(retained[key], recomputed[key], f"{path}/{key}")
        return out
    if isinstance(retained, list) and isinstance(recomputed, list) and len(retained) == len(recomputed):
        return [
            m
            for index, pair in enumerate(zip(retained, recomputed, strict=True))
            for m in mismatches(*pair, f"{path}/{index}")
        ]
    return [] if retained == recomputed and type(retained) is type(recomputed) else [path or "/"]


def check(directory: Path) -> int:
    text = (directory / RECORD).read_text()
    retained = json.loads(text)
    recomputed = build_record(directory)
    differences = mismatches(retained, recomputed)
    require(not differences, f"{directory / RECORD} differs from the recomputed audit at {differences[:10]}")
    require(dump(recomputed) == text, f"{directory / RECORD} is not in canonical form")
    if CRATE_ARCHIVE.exists():
        require(sha256_file(CRATE_ARCHIVE) == CRATE["crate_sha256"], "vendored crate digest")
    triples, laws, size = retained["triples"], len(retained["laws"]), retained["corpus_size"]
    print(f"wheel crate audit: {triples} triples x {laws} laws, {size} corpus values")
    for name in ("w64", "qw64"):
        for level, row in retained[name]["task_counts"].items():
            print(f"{name} {level}: {row}")
    print(f"qw8 probes: {retained['qw8_overflow']}")
    print("check passed")
    return 0


def self_test() -> int:
    rng = random.Random(SEED)
    # round_binary64 equals CPython's correctly rounded float(Fraction) in range.
    samples = [Fraction(1, 3), Fraction(-2, 3), Fraction(1, 10), Fraction(2**53 + 1), Fraction(-(2**53) - 3)]
    samples += [Fraction(rng.randint(-(10**30), 10**30), rng.randint(1, 10**30)) for _ in range(3000)]
    samples += [Fraction(rng.randint(1, 2**60), 2 ** rng.randint(1000, 1100)) for _ in range(1000)]
    for q in samples:
        bits, _event = round_binary64(q)
        require(bits == struct.unpack("<Q", struct.pack("<d", float(q)))[0], f"round_binary64({q}) differs")
        require(decode(bits) == Fraction(float(q)), "decode differs from Fraction(float)")
    max_bits = 0x7FEFFFFFFFFFFFFF
    top = decode(max_bits)
    half_ulp = Fraction(2) ** 970
    require(round_binary64(top + half_ulp) == (INF_BITS, "overflow"), "the overflow threshold rounds to infinity")
    require(round_binary64(top + half_ulp - Fraction(1, 2**1074))[0] == max_bits, "below the threshold stays MAX")
    require(round_binary64(-(top + half_ulp)) == (1 << 63 | INF_BITS, "overflow"), "negative overflow")
    tiny = Fraction(1, 2**1074)
    require(round_binary64(tiny / 2) == (0, "underflow"), "half the least subnormal ties to even zero")
    require(round_binary64(-tiny * Fraction(3, 4)) == (1 << 63 | 1, "inexact"), "three quarters rounds up, signed")
    require(round_binary64(Fraction(0)) == (0, "exact"), "exact zero is +0")
    require(round_binary64(Fraction(2**52 - 1, 2**1074) + tiny / 2)[0] == 0x0010000000000000, "subnormal carry")
    for bits in FIXED:
        if category(bits) == "n":
            require(round_binary64(decode(bits)) == (bits, "exact"), f"{bits:016x} round trip")
    print(f"round_binary64 equals float(Fraction) on {len(samples)} values and the boundary cases")

    trees = law_trees()
    require(len(trees) == len(wa.axioms(wa.operations("standard"))) + 1, "law trees cover wheel_algebra.axioms")
    # Every law tree, evaluated exactly, agrees with the module's own predicate.
    pool = wa.pool()
    standard = wa.axioms(wa.operations("standard"))
    for name, (left, right) in trees.items():
        for x in pool:
            env = [x, wa.Wheel(Fraction(5, 3)), wa.INFINITY]
            holds = evaluate(left, env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant) == evaluate(
                right, env, wa.Wheel.__add__, wa.Wheel.__mul__, wa.Wheel.inv, exact_constant
            )
            require(holds, f"{name} fails exactly at {x!r}")
            if name in standard:
                require(standard[name](*env), f"{name} predicate")

    directory = EVIDENCE
    full = json.loads((directory / FULL_OUTPUT).read_text())
    retained = json.loads((directory / RECORD).read_text())
    corpus, triples = harness_corpus()
    row = 3
    original = [parse_bits(b) for b in full["w64"]["add"][row]]
    # The recomputed add row and failing law cases, spliced into the retained
    # record, match it; check() compares records through mismatches().
    honest = copy.deepcopy(retained)
    honest["w64"]["classes"]["add"][row] = BinaryRow(corpus)(("add", row, original))
    require(not mismatches(retained, honest), "the retained add row is reproduced")
    flipped = copy.deepcopy(retained)
    letters = flipped["w64"]["classes"]["add"][row]
    flipped["w64"]["classes"]["add"][row] = ("s" if letters[0] != "s" else "a") + letters[1:]
    require(mismatches(flipped, honest) == [f"/w64/classes/add/{row}"], "a flipped classification is rejected")
    corrupted = list(original)
    column = next(c for c, bits in enumerate(corrupted) if category(bits) == "n")
    corrupted[column] ^= 1
    tampered = copy.deepcopy(retained)
    tampered["w64"]["classes"]["add"][row] = BinaryRow(corpus)(("add", row, corrupted))
    require(mismatches(retained, tampered) == [f"/w64/classes/add/{row}"], "a corrupted operation pattern is rejected")
    laws = list(trees)
    law, t, left, right = full["w64"]["failures"][0]
    case: LawCase = (law, triples[t], False, (parse_bits(left), parse_bits(right)))
    expected = retained["w64"]["classes"]["laws"][laws[law]][t]
    require(
        LawCases(corpus, laws)([case]) == [expected] and expected != "s", "the retained failing law case is reproduced"
    )
    bad: LawCase = (law, triples[t], False, (parse_bits(left) ^ 1, parse_bits(right)))
    require(LawCases(corpus, laws)([bad]) == ["s"], "a corrupted law side is rejected")
    text = (directory / FULL_OUTPUT).read_text()
    first = full["w64"]["add"][row][column]
    tampered_text = text.replace(f'"{first}"', f'"{parse_bits(first) ^ 1:016x}"', 1)
    require(hashlib.sha256(tampered_text.encode()).hexdigest() != retained["sources"][FULL_OUTPUT], "digest binding")
    print("a flipped classification, a corrupted operation pattern and a corrupted law side are rejected")
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path, help="write DIR/classification.json from DIR's harness outputs")
    group.add_argument("--check", type=Path, help="recompute DIR/classification.json and require it")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.out is not None:
        (args.out / RECORD).write_text(dump(build_record(args.out)))
        return check(args.out)
    if args.check is not None:
        return check(args.check)
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
