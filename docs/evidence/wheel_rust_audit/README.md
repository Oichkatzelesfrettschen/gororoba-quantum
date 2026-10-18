# Rust `wheel` crate 0.1.0 against wheel_algebra.py

The `w64` type of the Rust `wheel` crate implements Carlstrom's wheel of
fractions over Q with infinity and bottom by a category table, and runs its
finite arithmetic in IEEE binary64.
- **Structural findings.** 56 divisions land in another wheel class than the
  exact quotient. 2729 law cases hold in wheel_algebra.py and fail in `w64`,
  on (1), (2), (3), (4), (10) and (12).
- **Their cause.** Every one comes from the binary64 carrier: rounding,
  overflow and underflow. The crate's category table, run over exact
  rationals, holds every law on every triple. A model of that table with
  per-step binary64 rounding reproduces every crate bit pattern and law
  outcome, and leaves no case unexplained.
- **The paper sides with the exact module.** Proposition 3.14 makes every
  wheel of fractions satisfy the laws.
- **`qw64`** agrees with `gororoba_quantum/wheel_algebra.py` on every case.
- **Fixed-width overflow.** The fixed-width types break on integer overflow:
  `qw8` panics, or wraps to a wrong element.

wheel_algebra.py needs no change. Labels below are those of
[Carlstrom's report](../../notes/wheels-carlstrom.md).

## Crate identity and source review

| Field | Value |
| --- | --- |
| Name, version | `wheel` 0.1.0, published 2024-10-22T20:04:52Z, crates.io index `yanked: false` |
| Archive | [docs/source_archives/wheel-0.1.0.crate](../../source_archives/wheel-0.1.0.crate), 14092 bytes |
| SHA-256 | `2fb7ccae7d01d16dca5a39f58376ae6277467a8e3bea3fe45c20f72b4ee2c58b`, the index `cksum` |
| License (Cargo.toml) | `Apache-2.0 OR MPL-2.0` |
| Repository, VCS commit | https://github.com/menhera-org/wheel-rs, `630d82071e9d0bebd0cffb5b249526c10e6c371c` |
| Source note | [docs/notes/wheel-rust-crate.md](../../notes/wheel-rust-crate.md) |

The source review, completed before any compilation, found no network or
filesystem side effect:
- `Cargo.toml` sets `build = false`, and `[dependencies]` is empty.
- No member is a build script, a proc-macro, a `rust-toolchain` file or a
  `.cargo/config`.
- No source uses `include!`, `include_bytes!` or `env!`.
- The library is `no_std` outside `#[cfg(test)]`.

The harness compiled it offline as a path dependency and fetched nothing.

## What the crate implements

`w64` wraps one `f64` and reads it by category:

| IEEE value | `w64` category | Wheel element |
| --- | --- | --- |
| +0, -0 | Zero | 0 = [0, 1] |
| +inf, -inf | Infinity | infinity = /0 = [1, 0] |
| any NaN (quiet, signaling, either sign, any payload) | Bottom | bottom = 0/0 = [0, 0] |
| normal or subnormal | Normal | the finite element [x, 1] |

- **Addition and multiplication.** Both dispatch on the categories:
  - bottom absorbs every operand;
  - infinity + infinity = bottom, and 0 * infinity = bottom;
  - infinity absorbs every other operand;
  - x + 0 returns x unchanged, and 0 * x returns +0;
  - two finite nonzero operands go to hardware `+` or `*`, round to
    nearest even.
- **Involution.** `/` maps bottom to bottom, infinity to +0, 0 to +inf, and
  a finite x to `1.0 / x`.
- **Derived operations.** -x is `x * (-1)`, x - y is `x + (-y)`, and x / y
  is `x * /y`, the paper's definition of division.
- **Equality.** It compares categories, then the values within Normal, so
  it is the equality of wheel elements. The crate defines no ordering.
- **Representatives.** The carrier keeps non-canonical ones:
  - `x + 0` returns a -0 operand unchanged;
  - an overflowing negative result is -inf (`fff0000000000000`);
  - a signed underflow gives -0.

  Over the binary tables, 66 results are -0 and 110 are -inf. Every bottom
  result is the constant `f64::NAN` (`7ff8000000000000`), so no input NaN
  payload propagates.

`FractionWheel<T>` (`qw8` to `qw128`) holds the gcd-reduced pair with a
nonnegative denominator, (n, 0) -> (1, 0) and (0, d) -> (0, 1), which is
wheel_algebra.py's canonical pair, and computes Carlstrom's p. 5 formulas in
`T`. A product or sum in `add`, `mul` or the cross-multiplying `eq`, or
`abs` or `-` of `T::MIN`, can overflow; the type has no overflow handling.

The crate's own tests check (2) involution and /(xy) = /y /x, (3), (4), (5),
(6), (7), (8), (10), (12) and x - x = 0x^2 (p. 5). They run on nine small
elements whose `w64` arithmetic is exact. The `w64` tests compare by
`roughly_eq`, an absolute difference below 1e-7. They cannot see a relative
rounding error at large magnitude, and they accept distinct values below
1e-7 as equal. wheel_algebra.py's self-test already checks every one of these
laws.

## Harness and models

`harness/src/main.rs` depends on the crate by path. It prints
`harness-debug.json` under the dev profile with overflow checks, and the qw8
section of `harness-release-qw8.json` under the release profile with
wrapping. Both profiles are pinned in `harness/Cargo.toml`. The run used
rustc 1.98.1 and cargo 1.98.1, and rustfmt and `cargo clippy -D warnings`
are clean.

**The w64 corpus** has 55 binary64 patterns:
- +-0, +-1, +-inf;
- four NaN encodings: the canonical quiet NaN, a payload of 1, a negative
  NaN and a signaling NaN;
- small dyadics: 1/2, -1/4, 2, 3, -2, 3/2, 3/8, -27/4, 1024, 2^-10, 5, 7
  and 10;
- the binary64 roundings of 1/10, 1/3 and -2/3;
- 2^53, 2^53 + 2 and 1 + 2^-52;
- the extremes: +-f64::MAX, 2^1023, the rounding of 1e308, 2^600, 2^-600,
  2^-1022, +-2^-1074 and the largest subnormal;
- 16 random dyadics from a SplitMix64 stream seeded 20241022, each with at
  most 21 significant bits and a binary exponent in [-40, 40].

**The cases.**
- Every unary operation (neg, inv) and binary operation (add, sub, mul, div)
  runs over the whole corpus.
- The 17 laws of `wheel_algebra.axioms` and x - x = 0x^2 (p. 5) run on 5120
  triples: the cube of a 16-element pool of the edge values, plus 1024
  random triples from the same stream.
- Every value prints as its 16-hex-digit bit pattern, and the harness checks
  each pattern against the crate's own Debug rendering before printing it.
- `qw64` runs the same operations and laws over 14 rationals, among them the
  non-canonical inputs (2, -4) and (-3, 0), on all 2744 triples.

**The models.** `scripts/wheel_rust_audit.py` reads the patterns with integer
arithmetic only. It rebuilds the corpus and triples from the same stream, and
it builds the law trees from `wheel_algebra.axioms` itself, evaluated on
symbolic operands. It then runs three models of each case:
- **exact:** `wheel_algebra.Wheel` over Q;
- **rules:** the crate's category table over exact rationals;
- **rounded:** the rules model with each finite result rounded to binary64
  by `round_binary64`, an integer round to nearest even. Its self-test
  checks it against CPython's correctly rounded `float(Fraction)` and at the
  overflow threshold 2^1024 - 2^970.

The rounded model reproduces every crate bit pattern and every law outcome.

## Classification

**Operation cases** take one of seven classes:
- `a`: the crate's element equals the exact one;
- `i`, `o`, `u`: the crate's pattern is the binary64 rounding of the finite
  exact value (`i` inexact; `o` overflow to +-inf, read as infinity; `u`
  underflow of a nonzero value to +-0);
- `d`: x / y = x * /y rounds twice, and the result differs from the rounded
  exact quotient within the exact value's class;
- `c`: the same two roundings move the result to another class among finite,
  infinity and bottom;
- `s`: a structural departure.

| operation | cases | a | i | o | u | d | c | s |
|---|---|---|---|---|---|---|---|---|
| neg | 55 | 55 | 0 | 0 | 0 | 0 | 0 | 0 |
| inv | 55 | 21 | 32 | 2 | 0 | 0 | 0 | 0 |
| add | 3025 | 1713 | 1302 | 10 | 0 | 0 | 0 | 0 |
| sub | 3025 | 1733 | 1286 | 6 | 0 | 0 | 0 | 0 |
| mul | 3025 | 2330 | 437 | 177 | 81 | 0 | 0 | 0 |
| div | 3025 | 1433 | 1054 | 145 | 65 | 272 | 56 | 0 |

**Law cases** take one of five classes:
- `a`: the law holds in the crate;
- `i`: it fails, both the rules model and the exact model hold, and every
  rounding was finite and inexact with each side's class kept;
- `o`: as `i`, but an overflow or underflow occurred on the way;
- `c`: a crate side lands in a different wheel class from the exact side;
- `s`: a structural departure.

Each law has 5120 cases.

| law | a | i | o | c | s |
|---|---|---|---|---|---|
| (1) addition is associative | 5041 | 74 | 0 | 5 | 0 |
| (1) addition is commutative | 5120 | 0 | 0 | 0 | 0 |
| (1) 0 is the additive unit | 5120 | 0 | 0 | 0 | 0 |
| (2) multiplication is associative | 4861 | 76 | 54 | 129 | 0 |
| (2) multiplication is commutative | 5120 | 0 | 0 | 0 | 0 |
| (2) 1 is the multiplicative unit | 5120 | 0 | 0 | 0 | 0 |
| (2) involution: //x = x | 4507 | 35 | 288 | 290 | 0 |
| (2) involution is multiplicative: /(xy) = /x /y | 4660 | 242 | 80 | 138 | 0 |
| (3) distributive: (x + y)z + 0z = xz + yz | 4983 | 58 | 17 | 62 | 0 |
| (4) division: x/y + z + 0y = (x + yz)/y | 4741 | 166 | 27 | 186 | 0 |
| (5) 0 * 0 = 0 | 5120 | 0 | 0 | 0 | 0 |
| (6) (x + 0y)z = xz + 0y | 5120 | 0 | 0 | 0 | 0 |
| (7) /(x + 0y) = /x + 0y | 5120 | 0 | 0 | 0 | 0 |
| (8) x + 0/0 = 0/0 | 5120 | 0 | 0 | 0 | 0 |
| (10) 0x + 0y = 0xy | 4962 | 0 | 0 | 158 | 0 |
| (11) (0/0)x = 0/0 | 5120 | 0 | 0 | 0 | 0 |
| (12) x/x = 1 + 0x/x | 4476 | 356 | 0 | 288 | 0 |
| (p. 5) x - x = 0x^2 | 5120 | 0 | 0 | 0 | 0 |

**Audit classes.** The letters map onto three audit classes:
- **agree:** `a`.
- **rounding:** the crate value is the binary64 rounding of the exact value
  (`i`, `o`, `u`) or of its defining steps (`d`). The proof for `d` is
  per-step rounding, RNE(x * RNE(1/y)), and the value differs from the
  rounding of the exact quotient.
- **structural:** an operation whose wheel class differs from the exact one
  (`c`), or a law that holds in wheel_algebra.py and fails in the crate
  (law `i`, `o` or `c`), whatever its cause.

The letter `s` counts the unexplained cases: those the rounded model fails
to reproduce, or where the category table departs from the wheel.

| type | level | agree | rounding | structural | unexplained (`s`) |
|---|---|---|---|---|---|
| w64 | operations | 7285 | 4869 (4111 `i`, 340 `o`, 146 `u`, 272 `d`) | 56 (`c`) | 0 |
| w64 | laws | 89431 | 0 | 2729 (1007 `i`, 466 `o`, 1256 `c`) | 0 |
| qw64 | operations | 812 | 0 | 0 | 0 |
| qw64 | constructor checks | 14 | 0 | 0 | 0 |
| qw64 | laws | 49392 | 0 | 0 | 0 |

The qw8 probes classified `p` or `s` are structural: their i8 arithmetic overflows into a wrong element or a panic. The two release-profile equality probes overflow in their cross-multiplications yet return the exact booleans, so they classify `a`.
`classification.json` holds every case's letter and these counts
(`task_counts`), and `--check` recomputes them.

## Findings by label

wheel_algebra.py holds every law on every triple, as Proposition 3.14
guarantees for a wheel of fractions. The rules model holds on every triple
where the crate fails, so each failure comes from the binary64 carrier.
Binary64 is closed under neither the exact operations nor the reciprocal,
and the paper sides with the exact module on every row. Patterns below are
rows of `harness-debug.json`.

- **(1) Additive monoid.** Commutativity and the unit 0 hold everywhere,
  because hardware `+` is commutative and x + 0 returns x. Associativity
  fails in two ways:
  - by inexact rounding: (1 + 1) + RNE(1/3) gives `4002aaaaaaaaaaab`, while
    1 + (1 + RNE(1/3)) gives `4002aaaaaaaaaaaa`;
  - by overflow that changes the class: (infinity + MAX) + MAX is infinity,
    while infinity + (MAX + MAX) is infinity + infinity, which is bottom.
- **(2) Multiplicative monoid with involution.**
  - Commutativity and the unit 1 hold.
  - Associativity fails by rounding and, through overflow, by class:
    (0 * 3) * MAX is 0, while 0 * (3 * MAX) is 0 * infinity, which is
    bottom.
  - //x = x fails for x = 2^-1074: /x overflows to infinity and //x is 0.
    It fails for x = MAX too, because /MAX rounds to a subnormal whose
    reciprocal overflows to infinity.
  - /(xy) = /x /y fails the same ways.
  - Underflow feeds the class changes: 1/2 * 2^-1074 rounds to 0, which
    turns a later infinity into bottom.
- **(3), (4) and (10).** They fail where a product overflows or underflows
  on one side only. (10) 0 * 3 + 0 * MAX is 0, while 0 * (3 * MAX) is bottom.
  (4) at (0, 3, MAX) gives MAX against infinity.
- **(12) x/x = 1 + 0x/x.** The left side x * /x rounds twice, so MAX / MAX
  is 1 - 2^-53 (`3fefffffffffffff`) where the paper gives 1. At x = 2^-1074
  the left side is 2^-1074 * infinity, which is infinity, and the right side
  is 1 + 0 * infinity, which is bottom; the exact value of both is 1.
- **(5), (6), (7), (8), (11) and x - x = 0x^2 (p. 5).** They hold on every
  triple. Each side of these laws meets the same finite rounding or none,
  because 0y is 0 or bottom and x - x adds x to its exact negation.
- **Division** is x * /y in the crate, in the paper and in wheel_algebra.py.
  In binary64 it rounds twice:
  - 272 quotients sit one rounding away from the rounded exact quotient
    (`d`): -1/4 / RNE(1e308) gives `8001cc359e067a34` against the correctly
    rounded `8001cc359e067a35`;
  - 56 change class (`c`): 0 / 2^-1074 is 0 * infinity, which is bottom,
    where the exact value is 0; x / +-2^-1074 is infinity for every finite
    nonzero x.

**Fixed-width fractions.** Integer overflow in qw8 departs from the wheel of
fractions of Z (p. 6, example 1):
- With overflow checks, every overflowing probe panics:
  - the equality 127/2 == 127/2 panics, because its cross-multiplication
    127 * 2 overflows;
  - the probes -(-128) and /(-128) panic inside `qw8::new(-128, 1)`, at
    `abs(i8::MIN)` in the gcd, before any negation or inversion. Under
    overflow checks `i8::MIN` cannot be constructed.
- Wrapping gives:
  - (1/16) * (1/16) = (1, 0), infinity in place of 1/256;
  - 100 + 100 = -56;
  - 64 * 2 = -128;
  - -(-128) = -128;
  - /(-128) = (-1, -128), a non-canonical pair whose value +1/128 has the
    wrong sign.
- The gcd normalization and sign rules assume Z, so wrapped `qwN` is not the
  wheel of fractions of Z/2^N either.

`qw64` on its 14-element corpus stays within range and matches the exact
canonical pairs on every operation and law.

## wheel_algebra.py

The audit changes nothing in the module:
- The crate tests no law the module lacks.
- Wherever the two differ, the paper (Definition 1.1, Proposition 3.14,
  Proposition 4.3) sides with the exact module.
- The crate's category table, run over exact rationals, coincides with the
  module's operations on every case.

## Replay

CI has no Rust. The sources-251 gate runs
`"$PYTHON" scripts/wheel_rust_audit.py --check docs/evidence/wheel_rust_audit`.
It requires the digests of the harness
sources and outputs, regenerates the corpus and triples, and recomputes every
class into `classification.json` byte for byte. The sources-252 gate runs
`--self-test`, which checks `round_binary64` and requires the comparison to
reject a flipped class, a corrupted operation pattern and a corrupted law
side.

Regenerating the outputs needs a Rust toolchain:
1. Extract the vendored crate into a scratch directory as
   `src/wheel-0.1.0`.
2. Copy `harness/` beside it.
3. Run `cargo build --offline` and `cargo build --offline --release`.
4. Run `target/debug/wheel-audit-harness > harness-debug.json` and
   `target/release/wheel-audit-harness qw8-overflow > harness-release-qw8.json`.
5. Run `"$PYTHON" scripts/wheel_rust_audit.py --out DIR`, which first requires
   `DIR/src/wheel-0.1.0` to equal the vendored archive file for file.

| File | Content |
| --- | --- |
| `harness/Cargo.toml`, `harness/Cargo.lock`, `harness/src/main.rs` | the harness; the lock pins the path dependency and nothing else |
| `harness-debug.json` | w64 and qw64 cases and qw8 probes, overflow checks on |
| `harness-release-qw8.json` | qw8 probes, wrapping |
| `classification.json` | crate identity, toolchain, source digests, every class and the counts |
