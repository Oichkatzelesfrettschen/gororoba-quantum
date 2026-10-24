# McKay -- Hadamard matrices: equivalence-class representatives (combinatorial data page)

## Pages and retrieval

Retrieved 2026-10-23T22:23:57Z (license page 22:53:28Z) with curl. Each SHA-256 identifies
the bytes served at retrieval. The Hadamard subpage carries no license notice of its own;
McKay's parent Combinatorial Data page releases the collection's data files under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), except data another compiler is
credited with, and excludes the HTML pages. The Hadamard page credits other compilers only
for order 32. The 400-byte order-16 list is retained unmodified under that grant as the input
of a replay, credited to Brendan McKay; the HTML pages stay external.

| Source | URL | SHA-256 of retrieved bytes | Cited for |
|---|---|---|---|
| Brendan McKay, Hadamard matrices (Combinatorial Data) | https://users.cecs.anu.edu.au/~bdm/data/hadamard.html | `151e0b0a86b4f70639f1009fe9b67919475ab050c29dd57c09bef29259afdc90` | The file format, the equivalence relation and the class counts below |
| Brendan McKay, Combinatorial Data (collection page, License section) | https://users.cecs.anu.edu.au/~bdm/data/ | `ad346572677e19cb10ffc3e7f7f6cbfcdb6f70bef022175812df4afe7434f3b8` | "Except where it is indicated that the data was compiled by someone else, Brendan McKay releases all the data files (but not the html files) in this collection under the Creative Commons Attribution 4.0 International (CC BY 4.0) license" |
| Order-16 representatives, `had16.txt` | https://users.cecs.anu.edu.au/~bdm/data/hadamard/had16.txt | `67fb6f1a36f6893fca541a85754329812b9b8b454b3438ec9b6fd00005c2f170` | Five representatives, one per line; the retained copy [mckay_had16.txt](../../evidence/cd-star-lattice/external/mckay_had16.txt) has the same digest |

Tag convention: [P] marks a statement of the page; [I] marks repository interpretation.

## Main claims

- [P] A Hadamard matrix of order n is an n x n matrix of +1 and -1 whose rows, and therefore
  columns, are orthogonal.
- [P] Each file holds one matrix per line, written as n hexadecimal numbers, one per row; a
  row's binary digits with every 0 changed to -1 give its entries.
- [P] Two Hadamard matrices are equivalent when one comes from the other by permuting rows,
  permuting columns, and negating rows and columns.
- [P] The class counts are 1, 1, 1, 5, 3, 60 and 487 at orders 4, 8, 12, 16, 20, 24 and 28,
  and 13710027 at order 32, which Kharaghani and Tayfeh-Rezaie determined.
- [P] Only at order 32 does the page add files that treat a matrix and its transpose as
  equivalent (6857010 extended classes) and that list the 3993 classes equivalent to their own
  transposes.
- [I] The order-16 file therefore counts a matrix and its transpose separately; the replay's
  placement of I + W_16 and its transpose on different lines agrees.

## Mapping to this repository

- [I] The page names a class by no label. The [star-lattice tower note](../topics/cd-star-lattice-tower.md)
  therefore names a class by its line in the retained `had16.txt` and that file's SHA-256, and
  the page supplies no crosswalk to the class labels of Hall or of Sloane's tables.
- [I] [hadamard_replay.py](../../evidence/cd-star-lattice/external/hadamard_replay.py) decodes
  the five lines, places I + W_16 in the class of line 4 and its transpose and the sedenion
  sign table in the class of line 5, and counts automorphism pairs (P, Q) with
  P H Q^T = H; those placements and counts are the replay's results, which the page neither
  states nor checks.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: medium (equivalence classes for the boundary Hadamard matrix).
- [I] Factoring resource estimates: none.

## Boundaries

[I] The Hadamard page, the order-16 file and the collection page's License section were read
in full; the order-32 files were not downloaded.
