# Coste: semialgebraic triangulation and triviality

Michel Coste, *An Introduction to Semialgebraic Geometry*, Institut de
Recherche Mathematique de Rennes, October 2002, 78 PDF pages. The author
presents established semialgebraic geometry and its algorithmic foundations;
the notes do not claim original results.

The [third-party teaching mirror](http://nicolas.patrois.free.fr/maths/agr%C3%A9gation/documents/semialgebraic-geometry-Coste.pdf)
hosts a downloadable copy of Coste's exposition. Coste supplies the source
text; Nicolas Patrois's website supplies the retrieved file. The mirror is
distinct from the author's institutional hosting authority. The
[retained copy](../pdf/coste-semialgebraic-geometry-2002.pdf)
has SHA-256
`86dbd8733c84db3b6955a36921bd43599a98a82d76fb5f5c041c5a512b8f8a31`.
[SOURCES.json](../SOURCES.json) carries its retrieval identity. The original
author URL `https://perso.univ-rennes1.fr/michel.coste/polyens/SAG.pdf`
returns HTTP 403 during retrieval; the mirror retains the author's title,
date, and text. The inspected PDF metadata identifies `SAGroot.tex` and
author `coste`. Poppler reports legacy ICC-profile syntax warnings during
text extraction and rendering. The retained bytes preserve the source;
visual inspection confirms the cited statements remain legible.

Inspection covers the title, introduction, Theorem 3.12 and the beginning
of its proof on printed pages 51--52, Section 4.1.1 on pages 61--62, and
Theorem 4.4 with the beginning of its proof on page 63. Rendered PDF pages
52 and 63 confirm the printed statements on pages 51 and 62. This scope
does not assert a full independent verification of every proof in the notes.

## Exact statements and hypotheses

| Locator | Hypotheses | Conclusion used |
| --- | --- | --- |
| Theorem 3.12, printed p. 51 | `S` is a compact semialgebraic subset of `R^n`; `S_1,...,S_p` are finitely many semialgebraic subsets of `S` | A finite simplicial complex `K` and a semialgebraic homeomorphism `h:|K|->S` exist, with every `S_i` the image of a union of open simplices |
| Theorem 4.1, printed p. 62 | `A` is semialgebraic and `p:A->R^k` is continuous and semialgebraic | A finite semialgebraic partition of the target makes `p` semialgebraically trivial over each piece; trivializations can respect any specified finite family of semialgebraic subsets of `A` |
| Theorem 4.4, printed p. 63 | `A` is semialgebraic and `a` is a nonisolated point of `A` | For sufficiently small positive radius, the local intersection with the closed ball is semialgebraically homeomorphic to the cone on its sphere intersection, fixing that link |

Theorem 4.1 is the notes' exposition of Hardt's semialgebraic triviality;
the text refers to Bochnak-Coste-Roy and Benedetti-Risler for its proof.
The notes contain a proof of the compatible triangulation theorem.

## Application to dimension-32 zero products

The normalized pair set
`Z_5={(x,y): ||x||=||y||=1, L_x y=0}` is compact and real algebraic.
The unit base rank loci are semialgebraic because the trace/Newton
predicates use polynomial equalities and strict inequalities. Therefore:

- Theorem 3.12 gives an existence theorem for a finite global topological
  model compatible with the inverse images of all four positive-nullity
  base loci.
- Theorem 4.1 applies to the projection `(x,y)->x` and supplies a finite
  partition over which the incidence fibers have product trivializations.
  Compatibility can respect the inverse images of the rank loci.
- Theorem 4.4 supplies the theoretical form of local links around points of
  the pair set; an actual calculation must identify the link and a valid
  radius or equivalent exact certificate.

These statements establish the availability of an exact framework. They do
not produce a triangulation of `Z_5`, its boundary matrices, cup products,
or the transition and attaching maps. A Hardt piece is semialgebraic; the
theorem does not assert that the original rank locus is already one smooth
stratum. A fiberwise homeomorphism also need not be linear on a kernel.
The repository's rational kernel frames remain necessary for linear bundle
information. Theorems about finite decompositions supply no practical
runtime guarantee for a naive calculation in 60 real incidence variables.

The [research synthesis](koebisu_rank_stratum_research.md) therefore uses
exact local Schur reductions before attempting global decomposition. A
candidate triangulation becomes an admitted topological model only after
its covering, compatibility, and geometric identification certificates
pass; agreement of a few Betti numbers supplies a weaker check.
