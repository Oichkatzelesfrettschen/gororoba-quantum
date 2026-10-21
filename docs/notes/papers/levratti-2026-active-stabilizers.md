# Levratti: active stabilizers and Cayley-Dickson zero-divisor supports

## Source copy and license

The unchanged [source PDF](https://www.informationalidentityboundary.info/public/paper5.pdf) is retained under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
The [source-specific license evidence](https://zenodo.org/api/records/20431754) identifies the grant.
[SOURCES.json](../../SOURCES.json) binds the source bytes, evidence hash and reading scope.

[P] marks a statement or number in the source. [I] marks a repository
inference or exact check. Author-reported hardware observations remain
independent of the repository's own retained QPU evidence.

## Citation and provenance

- Title: Active Stabilizers in Reed-Muller CSS Codes from Cayley-Dickson
  Zero-Divisors.
- Author: Giovanni Levratti, independent researcher.
- PDF date: 28 May 2026. The hosting page identifies version 1, year 2026.
- Hosting page: https://www.informationalidentityboundary.info/paper5.html
- Direct PDF, linked by that page:
  https://www.informationalidentityboundary.info/public/paper5.pdf
- The page links DOI https://doi.org/10.5281/zenodo.20431754.
  The source-rights audit verifies the linked CC BY 4.0 record and the
  deposited PDF against the retained byte count, SHA-256 and record MD5.
- Retained PDF: [9-page manuscript](../../pdf/levratti-2026-active-stabilizers.pdf),
  390731 bytes, retrieved 12 October 2026 UTC; SHA-256
  `7bd01b5fda24b2de56b10bf9404efaa968e48d467350f1b8f361ef9ed36c3a9b`.
- The earlier page-only assessment identifies HTML SHA-256
  `0676656c1339f869853edc8993a902b8ae07071a6610e7980e445548bee8ac81`.
  That hash identifies an earlier capture, rather than the PDF.
- The [source registry](../../SOURCES.json) records retrieval identities.
- Reading scope: all nine pages as extracted text; page images 3-8 verify
  the support table, Theorems 3.1, 4.2, 5.1, 5.4 and 5.5, the complete
  hardware table, and the bridge-unit argument. The imported proofs from
  references [1]-[4], the author's verification code and raw hardware data
  receive no independent verification here. The separate rights audit
  verifies Zenodo license metadata and deposited-file identity.
- Status: author-hosted manuscript. The retrieved PDF establishes neither
  peer review nor an independently reproduced hardware result. The
  acknowledgements disclose AI assistance and author-run numerical checks.

## Historical page-only assessment

The earlier note reads only the approximately 340-word hosting page. Its
assessment identifies standard Fano/Hamming support incidence and the Pauli
identity, records the 336-row repository corpus's 42 mixed supports as a
finite overlap, and leaves theorem details and hardware metadata unassessed.
The earlier assessment treats every hardware claim as author-reported and
creates no QPU case. Those boundaries remain applicable to that reading.
The PDF retrieval closes the missing-text item and supplies the following
more precise assessment; it does not retroactively expand the earlier scope.

The companion [Fano-CSS note](levratti-2026-fano-css.md) calls this manuscript
reference [4]. Its reference [5] is a different Clifford-representation
manuscript. A shared author and consistent abstract add bibliographic context,
rather than independent confirmation.

## Mathematical claims and checks

- [P] Section 2 defines a flat as four distinct nonzero basis indices with
  XOR zero. It defines a split parity as
  `pi((p,q)|(r,s))=epsilon(p,r)*epsilon(q,r)*epsilon(p,s)*epsilon(q,s)`.
  An active split has parity `+1`. The criterion connecting activity to a
  signed zero-product pair is imported from reference [1]. These are
  support-defined objects; their finite counts do not enumerate arbitrary
  real zero-divisor coefficients.
- [P] Theorem 3.1 identifies the seven lo-flats with the supports of the seven
  nonidentity X stabilizers of the Steane code. Its table uses the dual
  Hamming-code support construction. Theorem 3.2 assigns the common mixed
  sign pattern `(-1,+1,+1)` and imports sign-table facts from reference [1].
- [I] Exact enumeration reproduces the seven weight-four XOR-zero supports
  and their equality with the nonzero binary linear-functional supports.
  The support correspondence is standard coding theory. The imported
  zero-divisor classification requires its own convention and proof audit.
- [P] Theorem 4.2 proves
  `(Z_alpha Z_beta)(X_alpha X_gamma)(X_beta X_gamma)=-Y_alpha Y_beta`
  for a balanced triple with one Z half and two X halves. The proof uses
  `ZX=iY` twice. Remark 4.5 explicitly locates the identity in the full Pauli
  group, rather than a product of code stabilizers.
- [I] The Pauli identity holds independently of the Cayley-Dickson sign
  table. The assignment of Pauli types to splits carries the proposed
  interpretation. A relative-phase experiment needs a reference branch;
  syndrome measurement of an unconditional Pauli error loses its global sign.
- [P] Theorem 5.1 gives 105 lo-flats in `F_2^4`, each contained in a unique
  three-dimensional subspace, and 15 such planes. Their complements are
  the 15 nonidentity X-stabilizer supports of the `[[15,7,3]]` Hamming CSS
  code. Individual lo-flats have four points; stabilizer supports have eight.
- [I] Exact enumeration reproduces the 105 flats, unique containment, and
  equality of the 15 plane complements with the 15 nonzero linear-functional
  supports. These checks concern finite binary incidence, rather than a
  complete dimension-32 rank locus or bundle.
- [P] Theorem 5.4 imports an all-dimensional sign-parity identity and uses
  the universal Pauli identity. Proposition 5.3 also describes fully inactive
  mixed splits at dimension 32.
- [I] A fully inactive flat has no two active splits from which the theorem's
  prescribed two X halves can be selected. In the repository convention,
  `{1,2,28,31}` is an exact witness: all three split parities are `-1`.
  The Pauli identity survives where the required type assignment exists;
  the paper's wording does not supply that assignment for every mixed flat.
- [P] Theorem 5.5 and Section 6 derive full-group syndrome weight `2^(n-2)`
  from the nonzero binary functional `s=alpha XOR beta`. Generator-level
  Hamming weight depends on the pair. Exact enumeration reproduces
  full-group weights 4 and 8 for all pairs at `n=4` and `n=5` [I].
- [I] Section 6, p. 8, states `epsilon(x,8)=+1` for every `x` from 1 through
  15. The statement fails at `x=8` because `e8^2=-1`; the repository also
  gives `epsilon(9,8)=-1` and `epsilon(8,9)=+1`. The claimed universal sign
  rule cannot support the printed Type-B proof without a corrected domain
  and argument. This defect does not itself refute the final Type-B criterion.

The two sign witnesses replay from the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" - <<'PY'
import sys
sys.path.insert(0, "gororoba_quantum")
from cd_core import cd_sign

splits = [((1, 2), (28, 31)), ((1, 28), (2, 31)), ((1, 31), (2, 28))]
parities = [
    cd_sign(32, first, third) * cd_sign(32, second, third)
    * cd_sign(32, first, fourth) * cd_sign(32, second, fourth)
    for (first, second), (third, fourth) in splits
]
print(parities)  # [-1, -1, -1]
print([cd_sign(16, *pair) for pair in [(8, 8), (9, 8), (8, 9)]])
# [-1, -1, 1]
PY
```

## Hardware evidence and experimental meaning

[P] Section 5.5 reports eight circuits on `ibm_kingston`, dated 27 May 2026,
8192 shots per circuit, with 15 data qubits and four ancillas. Experiment A
prepares `|+>^15`, applies a two-qubit Z error, and measures X syndromes.
Experiment B prepares `|0>^15`, applies an X error, and measures Z syndromes.
The table reports the expected syndrome as the plurality outcome in each
circuit, with rounded probabilities 28.7%, 51.4%, 30.6%, 49.9%, 32.7%,
44.5%, 38.2%, and 53.8%. The manuscript calls those probabilities
"fidelity" and reports approximately 150-180 native gates after transpilation.

[I] The PDF supplies preparation descriptions, expected four-bit syndromes,
shot counts, and a result summary. It omits complete count histograms,
shot-ordered data, transpiled circuits, physical layouts, calibration records,
confidence intervals, and a reproducible analysis. The repository has no
independent access to the reported job. Its numbers remain author-reported
and enter neither the repository's quota inventory nor its hardware results.

[I] A plurality outcome alone does not characterize the full distribution or
establish a statistical fidelity threshold. Separate product-state experiments
on the X and Z syndrome components also differ from preparing and protecting
a simultaneous encoded CSS state. Full-group weight eight follows classically
from a nonzero four-bit syndrome; the table does not independently measure
all 15 nonidentity stabilizers.

[I] For every density operator `rho`, `(-Y_alpha Y_beta) rho
(-Y_alpha Y_beta)^dagger` equals `(Y_alpha Y_beta) rho
(Y_alpha Y_beta)^dagger`. The reported syndrome protocol therefore cannot
distinguish the claimed global phase. The useful hardware observable is
syndrome conformance under its preparation/measurement circuits. It supplies
neither annihilator topology nor an observation of the repository's LCU
zero-product fringe.

## Repository use and remaining evidence

The PDF retrieval and requested theorem/hardware-section inspection are
complete. The source-rights audit also verifies the Zenodo file identity
and CC BY 4.0 grant. Imported sign-classification proofs, the corrected
Type-B argument, and lossless experimental data remain separate evidence items. The [Fano-CSS companion note](levratti-2026-fano-css.md) retains its
original narrower audit; claims imported from this source now route here.

The standard support and syndrome identities supply classical conformance
checks. They do not justify another QPU run by themselves. A useful hardware
case first states competing predicted distributions and a compilation decision
that the measured difference changes. A phase claim requires an actual
relative-phase control. The continuous rank-stratum program instead uses
[exact coefficient predicates and kernel charts](../../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md).
