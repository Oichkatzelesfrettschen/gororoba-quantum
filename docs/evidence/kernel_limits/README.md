# Kernel attachment evidence

The [proof note](../../notes/annihilator_kernel_limits.md) proves limiting
annihilator inclusions along polynomial paths and classifies the entire
three-coefficient affine cone slice. The exact replay reconstructs every
recorded polynomial identity, global frame and overlap map. Its all-stage
operator checks validate ordinary embeddings through dimension 256; the
written induction covers every higher stage.

The attachment image is `S3*(S1 x S3)`, with integral homology in degrees
zero, five, seven and eight. The complete pair incidence over this slice
has a mapping-cylinder model and retracts onto `S11`. These are different
spaces. Their invariants leave the unrestricted pair space open.

Run with the pinned dependencies from the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/kernel_limits/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/kernel_limits/replay.py --check
(cd docs/evidence/kernel_limits && sha256sum -c SHA256SUMS)
```

`result.json` binds exact rank-sized minors, complete
frames, rational projectors and removable limits, persistent charts,
certified punctured radii, endpoint coordinate inclusions, continuous
circle charts, their reciprocal transitions, and mutation controls.
The independent path and cone audits use the repository's order-preserving
spawn pool. Serial and spawned replays retain identical certificate bytes.
Independent recursive multiplication checks the signed action used in
the all-stage replay. Source hashes are checked before and after each
calculation. The replay rejects a changing source snapshot.

The polynomial API accepts rational coefficient polynomials at rational
endpoints. The written projector theorem covers real coefficients. The
cone identities and two-chart coverage prove the named slice's statements
for arbitrary real `A,B,C`; rational evaluator fixtures verify a separate
implementation surface. The topological model rests on the explicit
homeomorphisms and deformation retraction in the proof note. A chain
summary alone does not establish those geometric identifications.

[proof_obligations.json](proof_obligations.json) retains statements,
hypotheses, dependencies and remaining ambient obligations for the later
Rocq port. New formalization stays deferred until approved run results
are collected and adjudicated, or the human changes that workflow order.
The certificate executes exact CPU algebra and submits zero QPU jobs.
