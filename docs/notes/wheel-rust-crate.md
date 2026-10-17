# The Rust `wheel` crate 0.1.0: wheel arithmetic on binary64 and fixed-width fractions

## Source copy and license

The crates.io package `wheel` 0.1.0 ("Wheel algebra library for Rust", author
`metastable-void`, repository https://github.com/menhera-org/wheel-rs, VCS
commit `630d82071e9d0bebd0cffb5b249526c10e6c371c`, published
2024-10-22T20:04:52Z) is retained unchanged as
[wheel-0.1.0.crate](../source_archives/wheel-0.1.0.crate), downloaded from
https://static.crates.io/crates/wheel/wheel-0.1.0.crate on 2026-10-17. Its
SHA-256 `2fb7ccae7d01d16dca5a39f58376ae6277467a8e3bea3fe45c20f72b4ee2c58b`
equals the `cksum` of the crates.io index entry, and it holds 14092 bytes.
The manifest declares `Apache-2.0 OR MPL-2.0` and the archive carries both
texts (LICENSE.APACHE, LICENSE.MPL); either grant permits redistribution of
the unchanged archive. [SOURCES.json](../SOURCES.json) binds the archive, the
license member and every inspected member by SHA-256.

The archive has no build script (`build = false`), an empty
`[dependencies]` table, no proc-macro, no `include!`, `include_bytes!` or
`env!`, and no toolchain or cargo configuration file. The library is
`no_std` outside its tests. Every source, manifest and metadata member was
read in full before the audit harness compiled it; the license texts were
read by their headers.

## What the source establishes

[P] `src/lib.rs` defines the trait `Wheel` with constants `ZERO`, `ONE`,
`INFINITY` (unsigned) and `BOTTOM`, operations `add`, `neg`, `mul`, `inv`,
and `sub(x, y) = x + (-y)` and `div(x, y) = x * /y` as provided methods. It
requires `Eq` and gives no ordering.

[P] `src/float.rs` defines `w32` and `w64` as one-field tuple structs over
`f32` and `f64`. A category reads the float: `classify()` Zero (+-0) is the
wheel's 0, Infinite (+-inf) its infinity, Nan (any payload) its bottom, and
Normal or Subnormal a finite nonzero element. `add` and `mul` dispatch on the
two categories: bottom absorbs; infinity + infinity and 0 * infinity give
bottom; infinity absorbs every other operand; `x + 0` returns `x` and
`0 * x` returns `ZERO`; two finite nonzero operands go to the hardware `+` or
`*`. `inv` maps bottom to bottom, infinity to `ZERO`, zero to `INFINITY` and a
finite nonzero `x` to `1.0 / x`. `neg(x)` is `x * (-1)`. `eq` compares
categories and, within the finite nonzero category, values with `==`.
`roughly_eq` accepts an absolute difference below 1e-7 (`w64`) or 1e-4
(`w32`).

[P] `src/fraction.rs` defines `FractionWheel<T>` over `i8` to `i128`
(`qw8` to `qw128`) as a pair (numerator, denominator) normalized by the
gcd, with a nonnegative denominator, `(n, 0)` mapped to `(1, 0)` and
`(0, d)` to `(0, 1)`. Addition, multiplication and the involution are the
wheel-of-fractions formulas of Carlstrom section 1.2 (p. 5), and equality
cross-multiplies. Integer overflow in a product, a sum or the negation or
absolute value of `MIN` panics with overflow checks and wraps without them.

[P] The tests of both modules check Definition 1.1 (2) involution and
`/(xy) = /y /x`, (3), (4), (5), (6), (7), (8), Proposition 4.3 (10) and
(12), and `x - x = 0x^2` (p. 5) on nine elements: 0, 1, infinity, bottom,
-1, 3, -2, and 1/2, -1/4 (`w64`) or 3/2, -2/5 (`qw32`). The `w64` tests
compare with `roughly_eq`.

## Use in this repository

The following are inferences about the code, not statements of the crate.

The crate is a second, independent implementation of the wheel of fractions
of [Carlstrom's report](wheels-carlstrom.md), which
`gororoba_quantum/wheel_algebra.py` implements exactly over Q.

Relevance: (a) none; (b) method -- a second, independent wheel
implementation that cross-checks wheel_algebra.py; (c) none.
