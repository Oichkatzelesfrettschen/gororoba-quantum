# Carlstrom: wheels, total division by zero

## Source copy and license

The [source PDF](https://www2.math.su.se/reports/2001/11/2001-11.pdf) remains external to the published library.
Its optional personal reading copy is `docs/local_source_cache/carlstrom-wheels-2001-11.pdf`.
The [rights evidence](https://www2.math.su.se/reports/2001/11/) records `NOASSERTION`.
The report archive page states no license. The PDF carries the notice (c) 2001 Jesper Carlstrom and no
redistribution grant.
[SOURCES.json](../SOURCES.json) binds the source bytes, evidence hash and reading scope.

Jesper Carlstrom, *Wheels -- On Division by Zero*, Research Reports in
Mathematics 2001:11, Department of Mathematics, Stockholm University,
published 2001-09-10. The report is the author's licentiate thesis, 48 PDF
pages, ISSN 1401-5617. The version of record is Math. Struct. in Comp.
Science 14(1) (2004) 143-184; this note reads the report, not the journal
version.

The retained copy is the report archive's PDF, fetched from
`https://www2.math.su.se/reports/2001/11/2001-11.pdf` on 2026-10-17. It has
SHA-256 `339fd916659b381dd8e03ca58164e533c15173b7700bb7f3b08d42ad7ed5319b`
and 350294 bytes. Its PDF metadata names `2001-11.dvi`, dvipsk 5.86 and AFPL
Ghostscript 7.0. The archive page itself has SHA-256
`e41b113c4a39e08331bc721fddf9347ae73031b9302538b20d1e4092a45feeef`.

Page references below are the report's printed page numbers; the PDF page
is the printed page plus 2. Inspection covers section 1 (printed pp. 3-6),
Definitions 2.1, 2.2 and 2.6 (pp. 8-10), Proposition 3.14 and Theorem 3.15
(p. 22) and Proposition 4.3 (p. 24), read as pdftotext extraction. The
PDF pages 7 and 26 were rendered and read visually to confirm the wheel of
fractions operations, Definition 1.1 (1)-(8) and Proposition 4.3 (9)-(13)
with their proofs; the page footers fix the printed = PDF - 2 offset. The
scope stops short of an independent verification of the completeness
theorems of section 4.3.

## Statements used

From the paper:

| Locator | Statement |
| --- | --- |
| Section 1.1, p. 3 | The names infinity = 1/0 and bottom = 0/0 for the two elements adjoined to make division total, following Edalat and Potts. |
| Section 1.2, p. 4 | For a commutative ring A and a multiplicative submonoid S, (x, y) ==_S (x', y') iff (s x, s y) = (s' x', s' y') for some s, s' in S. This is the congruence the relation ~_S generates on the monoid A x A. |
| Section 1.2, p. 5 | The wheel of fractions S(.)A is A x A / ==_S with 0 = [0, 1], 1 = [1, 1], [x, y] + [x', y'] = [x y' + x' y, y y'], [x, y][x', y'] = [x x', y y'] and /[x, y] = [y, x]. |
| Section 1.2, p. 5 | 0x = 0 fails in general, x - x = 0x^2 with -1 = [-1, 1], / is an involution (//x = x, /(xy) = /y /x), and x/x = 1 + 0x/x. |
| Definition 1.1, p. 5 | A wheel satisfies (1) <H, 0, +> is a commutative monoid; (2) <H, 1, *, /> is a commutative monoid with involution /; (3) (x + y)z + 0z = xz + yz; (4) x/y + z + 0y = (x + yz)/y; (5) 0 * 0 = 0; (6) (x + 0y)z = xz + 0y; (7) /(x + 0y) = /x + 0y; (8) x + 0/0 = 0/0. |
| Section 1.2, p. 6, example 1 | (Z minus 0)(.)Z = Q together with /0 and 0/0. |
| Definition 2.1, p. 8 | An involution on a monoid M satisfies x** = x and (xy)* = y* x*. |
| Definition 2.6, p. 10 | The involution-monoid construction on M x M with (x, y)* = (y, x), modulo ==_S. |
| Proposition 3.14, p. 22 | Every wheel of fractions is a wheel in the sense of Definition 1.1. |
| Proposition 4.3, p. 24 | Derived rules: (9) /1 = 1; (10) 0x + 0y = 0xy; (11) (0/0)x = 0/0; (12) x/x = 1 + 0x/x; (13) xz = yz implies x + 0z/z = y + 0z/z. |
| Section 4.1, p. 24 | By (8) and (11), a term equals 0/0 if it contains 0/0 as a subterm. |

## Use in this repository

The following are inferences about the code, not statements of the paper.

`gororoba_quantum/wheel_algebra.py` implements the wheel of fractions with
A = Q and S = Q minus 0. That wheel is isomorphic to example 1 on p. 6.
Every class has the canonical pair (q, 1), (1, 0) = /0 or (0, 0) = 0/0.

The module's self-test names each law by its label:
- Definition 1.1 (1)-(8);
- Proposition 4.3 (10)-(12).

It checks every law on a pool of edge and random elements, and checks that a
mutation sending 0/0 to 0 breaks the laws.

`solve` performs Gaussian elimination over wheel elements in natural pivot
order. Its outcome on a positive semidefinite Gram system with a right side
in the column space follows from (8) and (11):
- A zero pivot leaves a zero row below it.
- Each entry of that row becomes 0 * /0 = 0/0.
- 0/0 then absorbs every term it enters.
- So every component is 0/0 exactly when the Gram matrix is singular.

The wheel has no notion of consistency. Bottom and infinity in a general
system carry no information about whether the system is consistent or about
its kernel. docs/evidence/lsq_conditioning applies the solve to the
normal equations of the coherent-family fits.

Relevance: (a) none; (b) method -- exact total arithmetic for algebra checks;
(c) none.
